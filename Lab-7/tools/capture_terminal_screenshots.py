"""Run lab commands in a visible Foot terminal and screenshot its live window."""

import argparse
from datetime import datetime, timezone
import getpass
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time

import pexpect

ROOT = Path(__file__).resolve().parents[1]
ANSI = re.compile(r"\x1b\][^\x07]*(?:\x07|\x1b\\)|\x1b\[[0-?]*[ -/]*[@-~]")


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names_for(phase):
    names = ["application_valid", "application_invalid", "pytest_summary"]
    return names + (["all_tests"] if phase == "after" else [])


def wait_for(path, process=None, timeout=180):
    deadline = time.monotonic() + timeout
    while not path.exists():
        if process is not None and process.poll() is not None:
            raise RuntimeError("The terminal closed before capture completed")
        if time.monotonic() > deadline:
            raise TimeoutError(f"Timed out waiting for {path.name}")
        time.sleep(0.05)


class LiveOutput:
    """Forward the actual shell PTY output to Foot and retain its raw bytes."""

    def __init__(self):
        self.buffer = io.StringIO()

    def write(self, text):
        self.buffer.write(text)
        sys.stdout.write(text)
        sys.stdout.flush()

    def flush(self):
        sys.stdout.flush()


def worker(phase, control):
    """Drive an interactive Bash PTY inside the native terminal window."""
    wait_for(control / "start")
    cwd = ROOT / "baseline" if phase == "before" else ROOT
    environment = dict(os.environ)
    environment.update(
        PATH=str(Path(sys.executable).parent) + os.pathsep + os.environ["PATH"],
        PS1=r"\u@\h:\W\$ ", PROMPT_COMMAND="", HISTFILE=os.devnull,
    )
    size = shutil.get_terminal_size()
    shell = pexpect.spawn(
        "/bin/bash", ["--noprofile", "--norc", "-i"], cwd=str(cwd),
        env=environment, encoding="utf-8", timeout=180,
        dimensions=(size.lines, size.columns), echo=True,
    )
    output = LiveOutput()
    shell.logfile_read = output
    prompt = re.escape(getpass.getuser() + "@" + socket.gethostname().split(".")[0])
    prompt += r":[^\r\n]*[$#] "
    shell.expect(prompt)
    try:
        for index, name in enumerate(names_for(phase)):
            output.buffer = io.StringIO()
            shell.sendline("clear")
            shell.expect(prompt)
            shell.sendline("pwd")
            shell.expect(prompt)
            started = now()
            stdin = None
            if name.startswith("application_"):
                command = "python -u parking_fee.py"
                values = (["09:30-11:45", "car", "ka01ab1234"]
                          if name == "application_valid" else ["", "hovercraft", "x"])
                if phase == "before" and name == "application_invalid":
                    values = [""]
                shell.sendline(command)
                for field, value in zip(
                    ["Enter entry and exit time", "Enter vehicle type", "Enter a number plate"],
                    values,
                ):
                    shell.expect_exact(field)
                    shell.sendline(value)
                stdin = "\n".join(values) + "\n"
            elif phase == "before":
                command = ("python -m pytest --import-mode=importlib fuzz_snapshot.py "
                           "-q --tb=no --color=yes")
                shell.sendline(command)
            elif name == "pytest_summary":
                command = ("python -m pytest test_parking_fee.py -k no_crash "
                           "-q --tb=no --color=yes")
                shell.sendline(command)
            else:
                command = "python -m pytest -q --color=yes"
                shell.sendline(command)
            shell.expect(prompt)
            shell.sendline("printf 'Exit code: %s\\n' \"$?\"")
            shell.expect(prompt)
            exit_code = int(re.search(r"Exit code: (\d+)", shell.before).group(1))
            expected = 1 if phase == "before" and name != "application_valid" else 0
            if exit_code != expected:
                raise RuntimeError(f"{phase}/{name}: exit {exit_code}, expected {expected}")
            raw = output.buffer.getvalue()
            text = ANSI.sub("", raw).replace("\r\n", "\n").replace("\r", "")
            text = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
            report_dir = ROOT / "reports" / phase
            raw_path = report_dir / f"terminal_{name}.ansi"
            text_path = report_dir / f"{name}.txt"
            raw_path.write_bytes(raw.encode("utf-8"))
            text_path.write_text(text, encoding="utf-8", newline="")
            record = {
                "name": name, "started_utc": started, "command": command,
                "cwd_relative_to_lab": str(cwd.relative_to(ROOT)), "stdin": stdin,
                "exit_code": exit_code, "expected_exit_code": expected,
                "output_kind": "live terminal transcript with commands and typed input",
                "output_sha256": digest(text_path),
                "raw_terminal_file": str(raw_path.relative_to(ROOT)),
                "raw_terminal_sha256": digest(raw_path),
            }
            temporary = control / "ready.tmp"
            temporary.write_text(json.dumps(record), encoding="utf-8")
            temporary.rename(control / f"ready-{index}.json")
            wait_for(control / f"captured-{index}")
    finally:
        shell.close(force=True)


def hypr_json(subject):
    return json.loads(subprocess.check_output(["hyprctl", "-j", subject], text=True))


def dispatch(action, argument):
    selectors = {"focuswindow": "window", "workspace": "workspace"}
    selector = selectors[action]
    expression = f"hl.dsp.focus({{{selector} = {json.dumps(argument)}}})"
    subprocess.run(["hyprctl", "dispatch", expression],
                   check=True, stdout=subprocess.DEVNULL)


def capture(phase):
    for program in ["foot", "grim", "hyprctl", "bash"]:
        if shutil.which(program) is None:
            raise SystemExit(f"Required native capture tool is missing: {program}")
    manifest_path = ROOT / "reports" / phase / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    snapshot = ROOT / "baseline/fuzz_snapshot.py"
    if phase == "before" and snapshot.exists():
        raise SystemExit(f"Refusing to overwrite {snapshot}")
    if phase == "before":
        snapshot.write_bytes((ROOT / "baseline/fuzz_tests.py.txt").read_bytes())
    previous = hypr_json("activewindow").get("address")
    previous_workspace = hypr_json("activeworkspace")["id"]
    occupied = {workspace["id"] for workspace in hypr_json("workspaces")}
    workspace = next(number for number in range(90, 200) if number not in occupied)
    dispatch("workspace", workspace)
    app_id = f"lab7-live-evidence-{os.getpid()}"
    process = None
    captures = []
    try:
        with tempfile.TemporaryDirectory(prefix="lab7-live-", dir=ROOT.parent.parent) as folder:
            control = Path(folder)
            with (control / "foot.log").open("w") as terminal_log:
                process = subprocess.Popen([
                    "foot", "-F", "-f", "JetBrains Mono Nerd Font:size=20",
                    "-a", app_id, "-T", f"Lab 7 | {phase} | live terminal evidence",
                    "-D", str(ROOT), sys.executable, str(Path(__file__).resolve()),
                    "--phase", phase, "--worker", str(control),
                ], stdout=terminal_log, stderr=subprocess.STDOUT)
                deadline = time.monotonic() + 15
                window = None
                while window is None:
                    window = next((w for w in hypr_json("clients") if w["class"] == app_id), None)
                    if process.poll() is not None or time.monotonic() > deadline:
                        raise RuntimeError((control / "foot.log").read_text())
                    time.sleep(0.05)
                address = window["address"]
                dispatch("focuswindow", f"address:{address}")
                time.sleep(0.7)
                (control / "start").touch()
                for index, name in enumerate(names_for(phase)):
                    ready = control / f"ready-{index}.json"
                    wait_for(ready, process)
                    record = json.loads(ready.read_text())
                    dispatch("focuswindow", f"address:{address}")
                    time.sleep(0.4)
                    window = next(w for w in hypr_json("clients") if w["address"] == address)
                    x, y = window["at"]
                    w, h = window["size"]
                    geometry = f"{x},{y} {w}x{h}"
                    target = ROOT / "screenshots" / f"{phase}_{name}.png"
                    subprocess.run(["grim", "-g", geometry, str(target)], check=True)
                    image_width, image_height = struct.unpack(">II", target.read_bytes()[16:24])
                    captures.append({
                        "name": name, "captured_utc": now(), "terminal": "foot",
                        "terminal_pid": window["pid"], "capture_tool": "grim",
                        "capture_kind": "live native fullscreen terminal window",
                        "fullscreen": bool(window["fullscreen"]),
                        "theme": "current user Foot configuration",
                        "window_address": address, "geometry": geometry,
                        "image_dimensions": [image_width, image_height],
                        "file": str(target.relative_to(ROOT)), "sha256": digest(target),
                        "command": record["command"], "exit_code": record["exit_code"],
                        "output_file": f"reports/{phase}/{name}.txt",
                        "output_sha256": record["output_sha256"],
                    })
                    manifest["commands"] = [record if r["name"] == name else r
                                            for r in manifest["commands"]]
                    (control / f"captured-{index}").touch()
                    print(f"Captured live Foot window: {target.name}", flush=True)
                process.wait(timeout=10)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        (ROOT / "reports" / phase / "screenshots.json").write_text(
            json.dumps({"phase": phase, "captures": captures}, indent=2) + "\n",
            encoding="utf-8",
        )
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            process.wait(timeout=10)
        if phase == "before":
            snapshot.unlink(missing_ok=True)
        dispatch("workspace", previous_workspace)
        if previous and any(w["address"] == previous for w in hypr_json("clients")):
            dispatch("focuswindow", f"address:{previous}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", required=True, choices=["before", "after"])
    parser.add_argument("--worker", type=Path, help=argparse.SUPPRESS)
    arguments = parser.parse_args()
    if arguments.worker:
        worker(arguments.phase, arguments.worker)
    else:
        capture(arguments.phase)
