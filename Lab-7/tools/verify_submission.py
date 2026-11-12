"""Verify submission artifacts, provenance, and saved evidence without rerunning tests."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def verify(write_report=False):
    source = json.loads((ROOT / "baseline/source.json").read_text())
    require(sha256(ROOT / "baseline/parking_fee.py") == source["files"]["parking_fee.py"],
            "Baseline application differs from the recorded upstream source")
    require(sha256(ROOT / "baseline/test_parking_fee.py.txt") == source["files"]["test_parking_fee.py"],
            "Original test starter differs from the recorded upstream source")
    checked_commands = 0
    native_captures = 0
    native_artifacts = []
    for phase in ["before", "after"]:
        report_dir = ROOT / "reports" / phase
        manifest = json.loads((report_dir / "manifest.json").read_text())
        app = ROOT / "baseline/parking_fee.py" if phase == "before" else ROOT / "parking_fee.py"
        tests = ROOT / "baseline/fuzz_tests.py.txt" if phase == "before" else ROOT / "test_parking_fee.py"
        require(sha256(app) == manifest["application_sha256"],
                f"{phase}: application hash mismatch")
        require(sha256(tests) == manifest["tests_sha256"],
                f"{phase}: test hash mismatch")
        if phase == "after":
            require(sha256(ROOT / "test_cli.py") == manifest["cli_tests_sha256"],
                    "CLI tests differ from the final evidence")
        for record in manifest["commands"]:
            path = report_dir / f"{record['name']}.txt"
            require(sha256(path) == record["output_sha256"],
                    f"Changed command output: {path}")
            require(record["exit_code"] == record["expected_exit_code"],
                    f"Unexpected command exit: {path}")
            if "raw_terminal_file" in record:
                raw = ROOT / record["raw_terminal_file"]
                require(sha256(raw) == record["raw_terminal_sha256"],
                        f"Changed raw terminal transcript: {raw}")
                native_artifacts.append(raw)
            checked_commands += 1
        capture_path = report_dir / "screenshots.json"
        capture_manifest = json.loads(capture_path.read_text())
        expected_count = 3 if phase == "before" else 4
        require(len(capture_manifest["captures"]) == expected_count,
                f"Incomplete native captures: {phase}")
        for capture in capture_manifest["captures"]:
            require(capture["terminal"] == "foot"
                    and capture["capture_tool"] == "grim"
                    and capture["fullscreen"],
                    "A screenshot is missing native fullscreen capture metadata")
            require(sha256(ROOT / capture["file"]) == capture["sha256"],
                    f"Changed native screenshot: {capture['file']}")
            require(sha256(ROOT / capture["output_file"]) == capture["output_sha256"],
                    f"Changed live transcript: {capture['output_file']}")
            native_captures += 1
        native_artifacts.append(capture_path)
    baseline_log = (ROOT / "reports/before/pytest_summary.txt").read_text()
    require("3 failed" in baseline_log, "Missing original three failing properties")
    passing_log = (ROOT / "reports/after/all_tests.txt").read_text()
    match = re.search(r"\b(\d+) passed\b", passing_log)
    require(match is not None and " failed" not in passing_log,
            "Final test suite did not pass")
    passing_tests = int(match.group(1))
    screenshots = [
        "before_application_valid.png", "before_application_invalid.png",
        "before_pytest_summary.png", "after_application_valid.png",
        "after_application_invalid.png", "after_pytest_summary.png",
        "after_all_tests.png",
    ]
    for name in screenshots:
        path = ROOT / "screenshots" / name
        require(path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"),
                f"Missing or invalid screenshot: {path}")
    pdf = ROOT / "PES1UG24CS145_SE_Lab7.pdf"
    require(pdf.read_bytes().startswith(b"%PDF-") and pdf.stat().st_size > 10000,
            "Missing or invalid PDF report")
    for target in re.findall(r"\]\(([^)]+)\)", (ROOT / "README.md").read_text()):
        if not target.startswith(("http://", "https://")):
            require((ROOT / target).is_file(), f"Broken README link: {target}")
    artifact_paths = [
        ROOT / "parking_fee.py", ROOT / "test_parking_fee.py", ROOT / "test_cli.py",
        ROOT / "README.md", ROOT / "INPUT_CONTRACT.md", ROOT / "BUG_ANALYSIS.md", pdf,
        ROOT / "requirements.txt", ROOT / "requirements-report.txt",
        ROOT / ".gitattributes", ROOT / ".gitignore",
        *[ROOT / "screenshots" / name for name in screenshots],
        *sorted((ROOT / "tools").glob("*.py")),
        *native_artifacts,
    ]
    result = {
        "verified_utc": datetime.now(timezone.utc).isoformat(),
        "upstream_commit": source["commit"],
        "saved_commands_verified": checked_commands,
        "baseline_failing_tests": 3,
        "final_passing_tests": passing_tests,
        "screenshots": len(screenshots),
        "native_fullscreen_captures": native_captures,
        "artifact_sha256": {
            str(path.relative_to(ROOT)): sha256(path) for path in artifact_paths
        },
    }
    verification_path = ROOT / "reports/after/verification.json"
    if write_report:
        verification_path.write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="",
        )
    elif verification_path.exists():
        saved = json.loads(verification_path.read_text())
        require(saved["artifact_sha256"] == result["artifact_sha256"],
                "An artifact changed after the saved verification; rebuild and verify again")
    print(f"Verified {checked_commands} saved commands, 3 baseline failures, "
          f"{passing_tests} final passes, {native_captures} live fullscreen PNGs, "
          "raw terminal transcripts, PDF, and README links.")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    verify(parser.parse_args().write_report)
