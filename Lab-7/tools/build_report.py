"""Build the PDF submission from saved command evidence and screenshots."""

from datetime import datetime
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "PES1UG24CS145_SE_Lab7.pdf"
WIDTH, HEIGHT = A4
BODY_WIDTH = WIDTH - 64
NORMAL = ParagraphStyle("Body", fontName="Times-Roman", fontSize=10,
                        leading=13, spaceAfter=6)
BOLD = ParagraphStyle("Bold", parent=NORMAL, fontName="Times-Bold")
TITLE = ParagraphStyle("Title", parent=BOLD, fontSize=15, leading=19,
                       alignment=TA_CENTER, spaceAfter=5)
SUBTITLE = ParagraphStyle("Subtitle", parent=TITLE, fontSize=14)
SECTION = ParagraphStyle("Section", parent=BOLD, fontSize=12, leading=15)
META = ParagraphStyle("Metadata", parent=BOLD, fontSize=12, leading=14)
LABEL = ParagraphStyle("Label", parent=BOLD, fontSize=11, alignment=TA_CENTER)
CAPTION = ParagraphStyle("Caption", parent=BOLD, alignment=TA_CENTER)


def paragraph(text, style=NORMAL):
    return Paragraph(escape(text), style)


def screenshot(name):
    path = ROOT / "screenshots" / name
    picture = Image(str(path))
    scale = min((BODY_WIDTH - 68) / picture.imageWidth,
                390 / picture.imageHeight)
    picture.drawWidth = picture.imageWidth * scale
    picture.drawHeight = picture.imageHeight * scale
    picture.hAlign = "CENTER"
    return picture


def pdf_date(year, month, day, hour, minute, second):
    """Preserve the system's complete UTC offset, including offset minutes."""
    stamp = datetime(year, month, day, hour, minute, second).astimezone()
    offset = stamp.strftime("%z")
    return f"D:{stamp:%Y%m%d%H%M%S}{offset[:3]}'{offset[3:]}'"


def footer(canvas, doc):
    canvas.setDateFormatter(pdf_date)
    canvas.setCreator("Lab 7 report generator (ReportLab)")
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#aab6c0"))
    canvas.line(32, 29, WIDTH - 32, 29)
    canvas.setFont("Times-Roman", 8)
    canvas.drawString(32, 17, "PES1UG24CS145 | Software Engineering | Lab 7")
    canvas.drawRightString(WIDTH - 32, 17, str(doc.page))
    canvas.restoreState()


def build():
    after = json.loads((ROOT / "reports/after/manifest.json").read_text())
    test_output = (ROOT / "reports/after/all_tests.txt").read_text()
    result_summary = re.findall(r"\b\d+ passed[^\r\n]*", test_output)[-1]
    # The complete submission uses one four-column master table. Body text
    # and evidence remain in its section cells, following the assignment guide.
    body = [
        paragraph("Department of Computer Science & Engineering", TITLE),
        Spacer(1, 8), paragraph("Software Engineering", TITLE),
        paragraph("UE24CS341A", TITLE), Spacer(1, 8),
        paragraph("Lab 7: Fuzz Testing Submission", SUBTITLE), Spacer(1, 10),
    ]
    rows = [[paragraph("Name: Devansh Gupta", META), "",
             paragraph("SRN: PES1UG24CS145", META), paragraph("Section: C", META)]]

    sections = [
        ("Objective and setup", [
            "Task: Use Hypothesis to discover input validation bugs in the assigned parking application, fix them, and verify the fixes.",
            "Assigned repository: https://github.com/SETAPESU26/L6_L7_19_parking_fee (Lab 7/). Source commit: fef20d42191cdd992b14c5717db612b929c2cfd0.",
            "The repository filenames parking_fee.py and test_parking_fee.py correspond to processor.py and test_processor.py in the handout.",
            f"Environment used: {after['python'].splitlines()[0]}. Dependencies: pytest 9.2.0 and Hypothesis 6.170.15.",
            "Commands: python -m pip install -r requirements.txt; python parking_fee.py; python -m pytest test_parking_fee.py.",
            "Method: Record the original application output, complete the three starter properties, retain their failures, fix each helper, then rerun both those properties and the expanded suite.",
            "The final suite has 79 helper test instances (14 Hypothesis property instances and 65 explicit regression cases), plus nine CLI cases: 88 passing tests in total. A property instance may execute hundreds of generated examples; the pytest test count is not the generated-input count.",
            "Arbitrary Unicode is useful for finding crashes, but rarely resembles a valid time range or plate. Structured strategies also generate valid values and check their exact outputs against independent expectations. Hypothesis shrinking reduces a failure to a small example for diagnosis.",
        ], []),
        ("Step 2: Run the original application", [
            "Input: 09:30-11:45, car, ka01ab1234. The original program prints 135 minutes, rate 30, and KA 01 AB 1234.",
            "An empty time input causes ValueError and stops the program before the remaining prompts. The baseline application is preserved unchanged in baseline/parking_fee.py.",
        ], [("Screenshot 1: Original application, valid input", "before_application_valid.png"),
            ("Screenshot 2: Original application, invalid input", "before_application_invalid.png")]),
        ("Steps 3 and 4: Fuzz tests expose failures", [
            "Each starter property uses @given(st.text() | st.none()) with max_examples=500 and deterministic generation. It checks that the function does not throw and that any returned value has a valid basic shape.",
            "All three tests fail against the original code. Hypothesis reports seven distinct failing outcomes across those three tests: time None and empty text; rate None and empty text; plate None, empty text, and '00'.",
            "The full tracebacks and minimized inputs are preserved in reports/before/pytest.txt. The screenshot shows a separate run with traceback display disabled for readability; no failures are hidden from the test result.",
        ], [("Screenshot 3: Three failing Hypothesis properties", "before_pytest_summary.png")]),
        ("Bug analysis and input policy", [
            "minutes_parked: None raises AttributeError; empty text raises ValueError. Directed checks also show that 25:00-26:00 returns 60, 09:60-10:00 returns 0, and 11:00-10:00 returns -60.",
            "hourly_rate: None raises AttributeError and unknown or empty text raises KeyError.",
            "format_plate: None raises AttributeError, empty text raises IndexError, and '00' produces two digits followed by three spaces. A long plate such as KA01AB123456 is silently truncated.",
            "Contract: Invalid inputs return None. Time fields must use ASCII HH:MM-HH:MM, valid clock ranges, and same-day forward order. Equal times return 0; overnight stays need a date and are rejected here.",
            "Rates retain bike=10, car=30, truck=60, with surrounding whitespace and case normalization. Plates accept the lab's AA99AA9999 syntax in compact or single-space grouped form and produce uppercase AA 99 AA 9999.",
        ], []),
        ("Step 5: Fix and rerun the application", [
            "The helpers validate types, complete formats, clock ranges, and same-day order. The CLI explains invalid entries and continues; EOF and Ctrl+C exit cleanly. A valid zero is preserved, and the original sample outputs remain correct.",
        ], [("Screenshot 4: Fixed application, valid input", "after_application_valid.png"),
            ("Screenshot 5: Fixed application, invalid input", "after_application_invalid.png")]),
        ("Step 6: Rerun the tests", [
            "The same three starter properties now pass. The expanded suite also checks exact valid results, time boundaries and ordering, case/whitespace normalization, plate idempotence, malformed formats, unsupported Python types, and command-line behavior.",
            "Generated valid examples use independent expected values, including datetime arithmetic for durations and explicit known rate values. Returning None for every input would fail these properties.",
            f"Final pytest result: {result_summary}. Raw results are saved in reports/after/. The screenshot below shows the complete test suite, including CLI regression tests.",
        ], [("Screenshot 6: Final complete test suite", "after_all_tests.png")]),
        ("Deliverables and evidence", [
            "PDF: PES1UG24CS145_SE_Lab7.pdf. Fixed application: parking_fee.py. Completed Hypothesis suite: test_parking_fee.py. Additional CLI tests: test_cli.py.",
            "Supporting files: INPUT_CONTRACT.md, BUG_ANALYSIS.md, unchanged baseline, raw reports, screenshot PNGs, and tools to reproduce the evidence and this PDF.",
            "Screenshots are direct Grim captures of a live fullscreen Foot terminal using the current user theme. Commands, typed inputs, working directories, results, and exit codes are visible in the terminal. Capture manifests record UTC timestamps, window geometry, PNG hashes, and matching terminal transcript hashes.",
            "Fuzzing identified crashes and malformed output with small examples. Boundary checks added silent validation failures. The revised suite checks both rejection and correct handling of valid inputs; passing it does not prove correctness for all possible inputs.",
        ], []),
    ]
    for number, (title, texts, pictures) in enumerate(sections, start=1):
        content = [paragraph(f"Section {number} - {title}", SECTION)]
        content.extend(paragraph(text) for text in texts)
        for label, filename in pictures:
            content.extend([Spacer(1, 5), paragraph(label, CAPTION), screenshot(filename)])
        rows.append([Paragraph(f"Section<br/>{number}", LABEL), content, "", ""])
    master = Table(rows, colWidths=[56, 197, 180, BODY_WIDTH - 433],
                   repeatRows=1, hAlign="LEFT", splitByRow=1, splitInRow=0)
    style = [
        ("SPAN", (0, 0), (1, 0)),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#8899aa")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8edf2")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]
    for row in range(1, len(rows)):
        style.append(("SPAN", (1, row), (3, row)))
    master.setStyle(TableStyle(style))
    body.append(master)
    document = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=32,
                                 leftMargin=32, topMargin=32, bottomMargin=40,
                                 title="Lab 7 Fuzz Testing - Parking Fee",
                                 author="Devansh Gupta - PES1UG24CS145")
    document.build(body, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    build()
