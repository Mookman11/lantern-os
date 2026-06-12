#!/usr/bin/env python3
"""
Generate a perfect PDF combining:
  - Convergence I/O Engine (Tesseract)
  - CSF Format Specification v1.0

Outputs: docs/CONVERGENCE-CSF-ENGINE.pdf
"""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "CONVERGENCE-CSF-ENGINE.pdf"

# ── Styles ─────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

TITLE = ParagraphStyle(
    "DocTitle",
    parent=styles["Title"],
    fontSize=28,
    leading=34,
    alignment=TA_CENTER,
    spaceAfter=6,
    textColor=HexColor("#1a1a2e"),
)

SUBTITLE = ParagraphStyle(
    "DocSubtitle",
    parent=styles["Normal"],
    fontSize=14,
    leading=18,
    alignment=TA_CENTER,
    spaceAfter=24,
    textColor=HexColor("#4a4a6a"),
)

META = ParagraphStyle(
    "DocMeta",
    parent=styles["Normal"],
    fontSize=10,
    leading=14,
    alignment=TA_CENTER,
    spaceAfter=6,
    textColor=HexColor("#666666"),
)

H1 = ParagraphStyle(
    "DocH1",
    parent=styles["Heading1"],
    fontSize=20,
    leading=26,
    spaceBefore=20,
    spaceAfter=10,
    textColor=HexColor("#1a1a2e"),
    borderPadding=(0, 0, 4, 0),
    borderWidth=0,
    borderColor=HexColor("#4a4a6a"),
)

H2 = ParagraphStyle(
    "DocH2",
    parent=styles["Heading2"],
    fontSize=16,
    leading=22,
    spaceBefore=16,
    spaceAfter=8,
    textColor=HexColor("#2a2a4a"),
)

H3 = ParagraphStyle(
    "DocH3",
    parent=styles["Heading3"],
    fontSize=13,
    leading=18,
    spaceBefore=12,
    spaceAfter=6,
    textColor=HexColor("#3a3a5a"),
)

BODY = ParagraphStyle(
    "DocBody",
    parent=styles["BodyText"],
    fontSize=10,
    leading=14,
    spaceAfter=6,
    alignment=TA_JUSTIFY,
    textColor=HexColor("#222222"),
)

CODE = ParagraphStyle(
    "DocCode",
    parent=styles["Code"],
    fontSize=8,
    leading=11,
    leftIndent=18,
    rightIndent=12,
    spaceAfter=6,
    textColor=HexColor("#333333"),
    backColor=HexColor("#f4f4f8"),
    borderPadding=(6, 6, 6, 6),
)

BULLET = ParagraphStyle(
    "DocBullet",
    parent=BODY,
    leftIndent=24,
    bulletIndent=12,
    spaceAfter=3,
)

TABLE_HEADER = ParagraphStyle(
    "TableHeader",
    parent=BODY,
    fontSize=9,
    leading=12,
    textColor=white,
    alignment=TA_LEFT,
)

TABLE_CELL = ParagraphStyle(
    "TableCell",
    parent=BODY,
    fontSize=9,
    leading=12,
    alignment=TA_LEFT,
)

# ── Markdown helpers ───────────────────────────────────────────────────

def escape_xml(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt_inline(text: str) -> str:
    # bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # italic
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    # inline code
    text = re.sub(r"`([^`]+)`", r"<font face='Courier' size='8' color='#444444'>\1</font>", text)
    # links -> just text
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    return text


def parse_table(lines: list[str], idx: int) -> tuple[Table | None, int]:
    """Parse a markdown table starting at idx. Return (Table, new_idx)."""
    rows_raw: list[list[str]] = []
    while idx < len(lines):
        line = lines[idx].rstrip("\n")
        stripped = line.strip()
        if not stripped or line.startswith("#"):
            break
        if "|" not in stripped:
            break
        cells = [c.strip() for c in stripped.split("|")]
        # Drop empty leading/trailing cells caused by outer pipes
        cells = [c for c in cells if c != ""]
        # Skip separator lines like --- | ---
        if cells and all(set(c) <= set("-:| ") for c in cells):
            idx += 1
            continue
        if cells:
            rows_raw.append(cells)
        idx += 1

    if not rows_raw:
        return None, idx

    # Normalize column count
    max_cols = max(len(r) for r in rows_raw)
    rows: list[list[str]] = []
    for r in rows_raw:
        while len(r) < max_cols:
            r.append("")
        rows.append(r[:max_cols])

    data = []
    for i, row in enumerate(rows):
        style = TABLE_HEADER if i == 0 else TABLE_CELL
        data.append([Paragraph(fmt_inline(c), style) for c in row])

    col_widths = [None] * max_cols
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#2a2a4a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), HexColor("#fafafc")),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
                ("TOPPADDING", (0, 1), (-1, -1), 6),
            ]
        )
    )
    return t, idx


def md_to_story(text: str) -> list:
    """Convert markdown text to reportlab flowables."""
    story: list = []
    lines = text.splitlines()
    i = 0
    in_code = False
    code_buffer: list[str] = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Code blocks
        if stripped.startswith("```"):
            if in_code:
                if code_buffer:
                    code_text = "\n".join(code_buffer)
                    story.append(Paragraph(escape_xml(code_text), CODE))
                code_buffer = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue

        if in_code:
            code_buffer.append(line)
            i += 1
            continue

        # Empty line
        if not stripped:
            story.append(Spacer(1, 4))
            i += 1
            continue

        # Horizontal rule
        if stripped == "---" or stripped == "***":
            story.append(Spacer(1, 8))
            story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#dddddd")))
            story.append(Spacer(1, 8))
            i += 1
            continue

        # Headings
        if line.startswith("# "):
            story.append(Paragraph(fmt_inline(line[2:].strip()), H1))
            i += 1
            continue
        if line.startswith("## "):
            story.append(Paragraph(fmt_inline(line[3:].strip()), H2))
            i += 1
            continue
        if line.startswith("### "):
            story.append(Paragraph(fmt_inline(line[4:].strip()), H3))
            i += 1
            continue
        if line.startswith("#### "):
            story.append(Paragraph(fmt_inline(line[5:].strip()), H3))
            i += 1
            continue

        # Blockquote
        if stripped.startswith(">"):
            story.append(
                Paragraph(
                    f"<i>{fmt_inline(stripped[1:].strip())}</i>",
                    ParagraphStyle("Quote", parent=BODY, leftIndent=18, textColor=HexColor("#555555")),
                )
            )
            i += 1
            continue

        # Table
        if "|" in stripped and i + 1 < len(lines) and "|" in lines[i + 1]:
            tbl, i = parse_table(lines, i)
            if tbl:
                story.append(Spacer(1, 6))
                story.append(tbl)
                story.append(Spacer(1, 6))
                continue

        # Bullet list
        if stripped.startswith("- ") or stripped.startswith("* "):
            story.append(Paragraph(f"• {fmt_inline(stripped[2:])}", BULLET))
            i += 1
            continue

        # Numbered list
        m = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if m:
            story.append(Paragraph(f"{m.group(1)}. {fmt_inline(m.group(2))}", BULLET))
            i += 1
            continue

        # Normal paragraph
        story.append(Paragraph(fmt_inline(line), BODY))
        i += 1

    return story


# ── Assemble document ──────────────────────────────────────────────────

def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_cover(story: list) -> None:
    story.append(Spacer(1, 120))
    story.append(Paragraph("Lantern OS", TITLE))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Convergence I/O Engine &amp; CSF Format", SUBTITLE))
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="60%", thickness=2, color=HexColor("#4a4a6a"), hAlign="CENTER"))
    story.append(Spacer(1, 30))
    story.append(Paragraph("Technical Reference Document", META))
    story.append(Paragraph("Version 1.0.0 &nbsp;|&nbsp; June 2026", META))
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Convergence I/O Engine</b> — 4-layer Tesseract hypercube routing", META))
    story.append(Paragraph("<b>CSF</b> — Convergence-Fitted Searchable Binary Archive v1.0", META))
    story.append(PageBreak())


def build_toc(story: list) -> None:
    story.append(Paragraph("Table of Contents", H1))
    story.append(Spacer(1, 12))
    toc_items = [
        ("Part I — Convergence I/O Engine", "1"),
        ("   1. Overview", "2"),
        ("   2. The 4-Layer Tesseract Model", "3"),
        ("   3. Convergence Loop", "4"),
        ("   4. CI/CD + Batch Integration", "5"),
        ("Part II — CSF Format Specification v1.0", "6"),
        ("   5. Executive Summary", "6"),
        ("   6. Design Goals &amp; Architecture", "7"),
        ("   7. Binary Format Specification", "8"),
        ("   8. Performance Projections", "9"),
        ("   9. Windows Prototyping Guide", "10"),
        ("   10. Security Considerations", "11"),
    ]
    for text, page in toc_items:
        story.append(
            Paragraph(
                f"{text}<tab/>{page}",
                ParagraphStyle(
                    "TOC",
                    parent=BODY,
                    fontSize=11,
                    leading=18,
                    leftIndent=12,
                    rightIndent=12,
                    tabStops=[(440, TA_RIGHT)],
                ),
            )
        )
    story.append(PageBreak())


def main() -> None:
    story: list = []

    # Cover
    build_cover(story)

    # TOC
    build_toc(story)

    # ── Part I: Convergence I/O Engine ─────────────────────────────────
    story.append(Paragraph("Part I — Convergence I/O Engine", H1))
    story.append(Spacer(1, 6))

    # Tesseract source intro
    tesseract_src = load_text(REPO_ROOT / "src" / "tesseract_convergence.py")
    # Extract docstring
    docstring_match = re.search(r'"""(.+?)"""', tesseract_src, re.DOTALL)
    if docstring_match:
        story.append(Paragraph("Overview", H2))
        story.extend(md_to_story(docstring_match.group(1)))

    # Convergence loop doc
    story.append(Paragraph("The Convergence Loop", H2))
    story.extend(md_to_story(load_text(REPO_ROOT / "docs" / "CONVERGENCE-LOOP.md")))

    # CI/CD batch loop doc
    story.append(Paragraph("CI/CD + Batch Framework Integration", H2))
    story.extend(md_to_story(load_text(REPO_ROOT / "docs" / "CONVERGENCE-CICD-BATCH-LOOP.md")))

    story.append(PageBreak())

    # ── Part II: CSF Format Specification ────────────────────────────────
    story.append(Paragraph("Part II — CSF Format Specification v1.0", H1))
    story.append(Spacer(1, 6))
    story.extend(md_to_story(load_text(REPO_ROOT / "docs" / "CSF-FORMAT-SPECIFICATION.md")))

    # ── Build PDF ──────────────────────────────────────────────────────
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=60,
        bottomMargin=36,
        title="Lantern OS — Convergence I/O Engine & CSF Format v1.0",
        author="Lantern OS Project",
        subject="Technical Reference",
        keywords="CSF, Convergence, Tesseract, Lantern OS, Archive Format",
    )
    doc.build(story)
    print(f"PDF created: {OUTPUT}")


if __name__ == "__main__":
    main()
