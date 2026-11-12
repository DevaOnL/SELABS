"""Screenshot saved, unedited command output with Chromium via Playwright."""

import argparse
import html
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def render(phase):
    """Render logs verbatim; metadata is visually separate from command output."""
    report_dir = ROOT / "reports" / phase
    manifest = json.loads((report_dir / "manifest.json").read_text())
    names = ["application_valid", "application_invalid", "pytest_summary"]
    if phase == "after":
        names.append("all_tests")
    target_dir = ROOT / "screenshots"
    target_dir.mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1000, "height": 200},
                                device_scale_factor=1.5)
        for record in manifest["commands"]:
            name = record["name"]
            if name not in names:
                continue
            output = (report_dir / f"{name}.txt").read_text()
            stdin = record["stdin"]
            metadata = (f"$ {record['command']}\n"
                        f"Working directory: Lab-7/{record['cwd_relative_to_lab']}\n"
                        f"Exit code: {record['exit_code']}")
            if stdin is not None:
                metadata += f"\nInput supplied (JSON escaped): {json.dumps(stdin)}"
            page.set_content(f"""<!doctype html><html><head><meta charset="utf-8">
                <style>
                * {{ box-sizing: border-box; }}
                body {{ margin: 0; padding: 24px; background: #edf1f5;
                        color: #182735; font-family: Arial, sans-serif; }}
                h1 {{ margin: 0 0 8px; font-size: 22px; }}
                .note {{ font-size: 14px; margin: 0 0 16px; }}
                .metadata {{ padding: 14px; background: #dfe7ef;
                             white-space: pre-wrap; overflow-wrap: anywhere;
                             font: 16px/1.55 monospace; }}
                pre {{ margin: 0; padding: 18px; background: #101c2a;
                       color: #eef4fa; white-space: pre-wrap;
                       overflow-wrap: anywhere; font: 18px/1.5 monospace; }}
                </style></head><body>
                <h1>Lab 7 · {html.escape(phase.title())} · {html.escape(name)}</h1>
                <p class="note">Browser screenshot of saved command output.
                Output below is reproduced verbatim.</p>
                <div class="metadata">{html.escape(metadata)}</div>
                <pre>{html.escape(output)}</pre>
                </body></html>""")
            page.screenshot(path=str(target_dir / f"{phase}_{name}.png"),
                            full_page=True)
            print(target_dir / f"{phase}_{name}.png")
        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", required=True, choices=["before", "after"])
    render(parser.parse_args().phase)
