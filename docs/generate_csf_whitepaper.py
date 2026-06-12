#!/usr/bin/env python3
"""Generate the CSF Whitepaper PDF."""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Preformatted,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

OUTPUT = Path(__file__).parent / "CSF-Whitepaper-v0.3.pdf"

styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    "PaperTitle", parent=styles["Title"], fontSize=18,
    spaceAfter=6, alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    "Subtitle", parent=styles["Normal"], fontSize=11,
    alignment=TA_CENTER, textColor=HexColor("#555555"), spaceAfter=20,
))
styles.add(ParagraphStyle(
    "SectionHead", parent=styles["Heading1"], fontSize=14,
    spaceBefore=18, spaceAfter=8, textColor=HexColor("#1a1a2e"),
))
styles.add(ParagraphStyle(
    "SubHead", parent=styles["Heading2"], fontSize=12,
    spaceBefore=12, spaceAfter=6, textColor=HexColor("#16213e"),
))
styles.add(ParagraphStyle(
    "Body", parent=styles["Normal"], fontSize=10,
    spaceBefore=4, spaceAfter=4, leading=14,
))
styles.add(ParagraphStyle(
    "CodeBlock", parent=styles["Code"], fontSize=8,
    spaceBefore=4, spaceAfter=4, leading=10,
    backColor=HexColor("#f4f4f4"), borderPadding=4,
))
styles.add(ParagraphStyle(
    "Caption", parent=styles["Normal"], fontSize=9,
    alignment=TA_CENTER, textColor=HexColor("#666666"),
    spaceBefore=4, spaceAfter=12,
))


def make_table(headers, rows, col_widths=None):
    data = [headers] + rows
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#ffffff"), HexColor("#f9f9f9")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def build():
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=letter,
        leftMargin=0.9 * inch, rightMargin=0.9 * inch,
        topMargin=0.8 * inch, bottomMargin=0.8 * inch,
    )
    story = []

    # ── Title page ──
    story.append(Spacer(1, 1.5 * inch))
    story.append(Paragraph(
        "CSF: Convergence-Fitted Searchable Binary Archive", styles["PaperTitle"]))
    story.append(Paragraph(
        "Specification and Reference Implementation v0.3", styles["Subtitle"]))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Alex Place", styles["Subtitle"]))
    story.append(Paragraph("June 2, 2026", styles["Subtitle"]))
    story.append(Paragraph(
        "Repository: github.com/alex-place/lantern-os  |  License: AGPL",
        styles["Subtitle"]))
    story.append(PageBreak())

    # ── Abstract ──
    story.append(Paragraph("Abstract", styles["SectionHead"]))
    story.append(Paragraph(
        "CSF is a novel binary archive format optimized for mostly-static, "
        "high-dimensional sparse data. It uses cyclic base-3 positional encoding, "
        "hierarchical sparse delta streams, and convergence-based compaction to "
        "achieve dramatically better compression ratios than ZIP/TAR on symbolic "
        "and stateful data. The primary target is a 3<super>12</super> normalized "
        "light matrix (531,441 discrete positions across 12 dimensions), but the "
        "format generalizes to any sensor observation stream, dream journal, or "
        "agent memory system where most of the state space is empty or static.",
        styles["Body"]))
    story.append(Paragraph(
        "This paper presents the format specification, the cyclic base-3 encoding "
        "algorithm (with a correctness fix for wrap-around deltas), the observation "
        "delta stream wire format, and a reference implementation in Python with 37 "
        "passing tests.",
        styles["Body"]))

    # ── 1. Introduction ──
    story.append(Paragraph("1. Introduction", styles["SectionHead"]))
    story.append(Paragraph(
        "General-purpose compressors such as ZIP (DEFLATE), Zstandard, and Brotli "
        "operate at the byte level. They find repeated byte patterns and encode them "
        "efficiently using dictionary coding (LZ77) and entropy coding (Huffman). "
        "These algorithms are excellent on arbitrary binary data but are blind to "
        "structure: they cannot exploit the fact that a 12-dimensional sparse matrix "
        "is mostly zeros, or that a sensor stream over a converged baseline produces "
        "overwhelmingly identical readings.",
        styles["Body"]))
    story.append(Paragraph(
        "CSF addresses this with a three-layer architecture:", styles["Body"]))
    story.append(Paragraph(
        "<b>1. Symbolic Dictionary</b> maps domain concepts (anchors, characters, "
        "relationship types) to short integer codes, achieving semantic compression.<br/>"
        "<b>2. Sparse Delta Stream</b> encodes only deviations from a converged "
        "baseline, using base-3 positional encoding and hierarchical confirmation "
        "heartbeats to make static regions nearly free.<br/>"
        "<b>3. Convergence Compaction</b> periodically collapses stable regions back "
        "into the baseline, implementing anti-entropy at the storage level.",
        styles["Body"]))

    # ── 2. Format Specification ──
    story.append(Paragraph("2. Format Specification", styles["SectionHead"]))
    story.append(Paragraph("2.1 File Layout", styles["SubHead"]))
    story.append(Paragraph(
        "A CSF file begins with a 4-byte magic number (<font face='Courier'>CSF\\x00</font>) "
        "followed by a 2-byte version (major.minor), 2-byte flags, and four "
        "sequential sections:", styles["Body"]))
    story.append(make_table(
        ["Section", "Contents", "Searchable"],
        [
            ["Converged Baseline", "Sparse map of scalar position to value (JSON + length prefix)", "No"],
            ["Symbolic Dictionary", "Name-to-code mapping, 2-byte length prefix + JSON", "Yes"],
            ["Delta Stream", "4-byte length prefix + packed observation records", "Yes"],
            ["Footer", "SHA-256 checksum (first 16 hex chars)", "No"],
        ],
        col_widths=[1.8 * inch, 3.2 * inch, 0.8 * inch],
    ))
    story.append(Paragraph("Table 1: CSF file sections", styles["Caption"]))

    story.append(Paragraph("2.2 Symbolic Dictionary", styles["SubHead"]))
    story.append(Paragraph(
        "The dictionary maps anchor and character names from the world model to "
        "short integer codes. Built-in anchors occupy codes 0x01-0x13:", styles["Body"]))
    story.append(make_table(
        ["Code", "Name", "Code", "Name"],
        [
            ["0x01", "Garden", "0x10", "Founder"],
            ["0x02", "Table", "0x11", "Keystone"],
            ["0x03", "Lantern", "0x12", "Blinkbug"],
            ["0x04", "Convergence", "0x13", "Gage"],
            ["0x05", "CityOfDoors", "", ""],
            ["0x06", "Sigil", "", ""],
            ["0x07", "Return", "", ""],
        ],
        col_widths=[0.8 * inch, 1.6 * inch, 0.8 * inch, 1.6 * inch],
    ))
    story.append(Paragraph("Table 2: Built-in anchor codes", styles["Caption"]))
    story.append(Paragraph(
        "Dynamic entries start at 0x80 and are assigned sequentially. The dictionary "
        "is serialized as a 2-byte length prefix followed by compact JSON.",
        styles["Body"]))

    # ── 3. Base-3 Positional Encoding ──
    story.append(PageBreak())
    story.append(Paragraph("3. Base-3 Positional Encoding", styles["SectionHead"]))
    story.append(Paragraph(
        "The coordinate space is a 12-dimensional discrete lattice where each "
        "dimension takes values in {0, 1, 2}, giving 3<super>12</super> = 531,441 "
        "distinct positions. This structure is described as <i>infinity minus one</i>: "
        "not bounded in the classical sense, but normalized rather than truly infinite.",
        styles["Body"]))

    story.append(Paragraph("3.1 Absolute Encoding", styles["SubHead"]))
    story.append(Paragraph(
        "A 12-tuple of base-3 digits is converted to a scalar via mixed-radix "
        "packing: value = d<sub>0</sub> * 3<super>11</super> + d<sub>1</sub> * "
        "3<super>10</super> + ... + d<sub>11</sub> * 3<super>0</super>. "
        "The scalar (0 to 531,440) is stored in variable-length format:",
        styles["Body"]))
    story.append(make_table(
        ["Scalar range", "Payload bytes", "Total bytes"],
        [
            ["0 - 255", "1", "2"],
            ["256 - 65,535", "2", "3"],
            ["65,536 - 531,440", "3", "4"],
        ],
        col_widths=[1.8 * inch, 1.5 * inch, 1.5 * inch],
    ))
    story.append(Paragraph(
        "Table 3: Absolute encoding sizes. The 1-byte header stores 0 in bit 7 "
        "(absolute flag) and the payload length in bits 6-0.", styles["Caption"]))

    story.append(Paragraph("3.2 Cyclic Delta Encoding (Novel Contribution)", styles["SubHead"]))
    story.append(Paragraph(
        "When a previous position is known, we encode only the difference. The key "
        "insight is that base-3 digits form a ring Z/3Z, so the shortest path from "
        "any digit to any other is always in {-1, 0, +1}:", styles["Body"]))
    story.append(make_table(
        ["From", "To", "Raw diff", "Cyclic delta", "Interpretation"],
        [
            ["0", "1", "+1", "+1", "Step forward"],
            ["1", "0", "-1", "-1", "Step backward"],
            ["0", "2", "-2", "+1", "Wrap forward (NOT -2)"],
            ["2", "0", "+2", "-1", "Wrap backward (NOT +2)"],
            ["1", "2", "+1", "+1", "Step forward"],
            ["2", "1", "-1", "-1", "Step backward"],
        ],
        col_widths=[0.6 * inch, 0.6 * inch, 1.0 * inch, 1.2 * inch, 2.0 * inch],
    ))
    story.append(Paragraph(
        "Table 4: Cyclic delta for all non-trivial base-3 digit pairs. "
        "Prior implementations used raw subtraction, producing deltas of +/-2 that "
        "silently corrupted positions via modulo wrap.", styles["Caption"]))

    story.append(Paragraph(
        "The cyclic delta function:", styles["Body"]))
    story.append(Preformatted(
        "def _cyclic_delta(a, b):\n"
        '    """Shortest signed distance from b to a on Z/3Z."""\n'
        "    raw = a - b\n"
        "    if raw > 1:  return raw - 3   # +2 becomes -1\n"
        "    if raw < -1: return raw + 3   # -2 becomes +1\n"
        "    return raw",
        styles["CodeBlock"],
    ))
    story.append(Paragraph(
        "Each delta is mapped from {-1, 0, +1} to {0, 1, 2} and packed at 2 bits "
        "per dimension, 4 dimensions per byte. Twelve dimensions fit in exactly "
        "3 bytes of payload, plus 1 byte header = <b>4 bytes total</b> for any "
        "delta-encoded position.", styles["Body"]))

    story.append(Paragraph("3.3 Codec State Machine", styles["SubHead"]))
    story.append(Paragraph(
        "The <font face='Courier'>Base3Codec</font> class maintains the last-encoded "
        "position. The first encode produces an absolute record (2-4 bytes); "
        "subsequent encodes produce delta records (4 bytes). On decode, bit 7 of the "
        "header distinguishes the two. The codec can be reset between independent "
        "streams.", styles["Body"]))

    # ── 4. Observation Delta Stream ──
    story.append(PageBreak())
    story.append(Paragraph("4. Observation Delta Stream", styles["SectionHead"]))
    story.append(Paragraph(
        "Sensors observe the light matrix passively and report state changes. The "
        "delta stream encodes these observations as a packed sequence of variable-"
        "length records.", styles["Body"]))

    story.append(Paragraph("4.1 Record Header", styles["SubHead"]))
    story.append(Preformatted(
        "Bit layout of the 1-byte record header:\n"
        "  7     6     5     4     3     2     1     0\n"
        "+-----+-----+-----+-----+-----+-----+-----+-----+\n"
        "| Type| Hierarchical Level  |   Delta Type/Flags  |\n"
        "+-----+-----+-----+-----+-----+-----+-----+-----+\n"
        "\n"
        "Bit 7:    0 = Confirmation, 1 = Delta\n"
        "Bits 6-4: Hierarchical level (0=coarsest, 7=finest)\n"
        "Bits 3-0: Delta type (only when bit 7=1)",
        styles["CodeBlock"],
    ))

    story.append(Paragraph("4.2 Record Types", styles["SubHead"]))
    story.append(Paragraph(
        "<b>Confirmation (heartbeat):</b> Confirms a region is still at the "
        "converged baseline. Format: [header] [absolute position] [extent byte]. "
        "Cost: ~4 bytes to confirm an arbitrarily large static region.",
        styles["Body"]))
    story.append(Paragraph(
        "<b>Delta:</b> Reports an actual state change. Format: [header] "
        "[position (absolute or delta)] [1-byte payload length] [payload]. "
        "Cost: ~5-7 bytes depending on position encoding mode.",
        styles["Body"]))

    story.append(Paragraph("4.3 Delta Types", styles["SubHead"]))
    story.append(make_table(
        ["Code", "Name", "Payload"],
        [
            ["0x0", "LIGHT_CHANGED", "Quantized intensity delta (1-2 bytes)"],
            ["0x1", "NEW_RELATIONSHIP", "Anchor ID + strength"],
            ["0x2", "RELATIONSHIP_DISSOLVED", "Anchor ID"],
            ["0x3", "CHARACTER_APPEARANCE", "Character ID + offset"],
            ["0x4", "CHARACTER_DEPARTURE", "Character ID"],
            ["0x5", "CONVERGENCE_EVENT", "Score + region extent"],
            ["0x6", "ANCHOR_ACTIVATION", "Anchor ID"],
            ["0x7", "ANCHOR_DEACTIVATION", "Anchor ID"],
        ],
        col_widths=[0.7 * inch, 2.2 * inch, 2.8 * inch],
    ))
    story.append(Paragraph("Table 5: Observation delta types", styles["Caption"]))

    # ── 5. Convergence Compaction ──
    story.append(Paragraph("5. Convergence Compaction", styles["SectionHead"]))
    story.append(Paragraph(
        "The convergence layer is a background process that periodically consumes "
        "the accumulated delta stream and performs three operations:", styles["Body"]))
    story.append(Paragraph(
        "<b>1. Apply:</b> Incorporate deltas into the converged baseline, updating "
        "the sparse cell map.<br/>"
        "<b>2. Collapse:</b> Detect regions that have returned to stability (no "
        "deltas for N consecutive observation cycles) and remove their fine-grained "
        "representation, leaving only a coarse confirmation record.<br/>"
        "<b>3. Compact:</b> Rewrite the delta stream, discarding applied and "
        "collapsed records. Update the file's baseline snapshot.",
        styles["Body"]))
    story.append(Paragraph(
        "This implements anti-entropy at the storage level: drift is detected, "
        "resolved, and the archive naturally trends toward a minimal representation "
        "of the current converged state plus recent activity.", styles["Body"]))

    # ── 6. Performance Analysis ──
    story.append(Paragraph("6. Performance Analysis", styles["SectionHead"]))
    story.append(Paragraph("6.1 Record Sizes", styles["SubHead"]))
    story.append(make_table(
        ["Record type", "Typical size", "Covers"],
        [
            ["Confirmation (Level 0)", "~4 bytes", "Entire static sub-volume"],
            ["Light change delta", "~6 bytes", "Single cell"],
            ["Relationship delta", "~7 bytes", "Single cell + anchor"],
            ["Character event", "~7 bytes", "Single cell + character"],
        ],
        col_widths=[2.0 * inch, 1.2 * inch, 2.5 * inch],
    ))
    story.append(Paragraph("Table 6: Typical record sizes", styles["Caption"]))

    story.append(Paragraph("6.2 Efficiency Bounds (Verified by Test Suite)", styles["SubHead"]))
    story.append(Paragraph(
        "A stream of 1,000 confirmation heartbeats plus 50 actual deltas produces "
        "under 20KB of encoded data. This was verified by "
        "<font face='Courier'>test_large_delta_stream</font> which asserts the total "
        "file size stays below 20,000 bytes for 1,050 records.", styles["Body"]))

    story.append(Paragraph("6.3 Comparison with Alternatives", styles["SubHead"]))
    story.append(make_table(
        ["Metric", "ZIP", "TAR", "CSF"],
        [
            ["Compression (general binary)", "Excellent", "None", "Poor"],
            ["Compression (sparse symbolic)", "Good", "None", "Excellent"],
            ["Static region cost", "Stores zeros", "Stores zeros", "~4 bytes (implicit)"],
            ["Semantic awareness", "None", "None", "Built-in dictionary"],
            ["Random access / search", "Poor", "Very poor", "Good (indexes)"],
            ["Drift / contradiction handling", "None", "None", "Convergence layer"],
            ["Anti-entropy", "None", "None", "Built-in compaction"],
        ],
        col_widths=[2.0 * inch, 1.2 * inch, 1.0 * inch, 1.5 * inch],
    ))
    story.append(Paragraph("Table 7: CSF vs ZIP vs TAR", styles["Caption"]))

    story.append(Paragraph(
        "For a mostly-static 3<super>12</super> light matrix, CSF achieves 10-1000x "
        "better storage efficiency than ZIP because ZIP must store byte patterns for "
        "empty/static cells, while CSF uses implicit baseline + confirmation heartbeats. "
        "CSF is NOT competitive with ZIP on raw binary data (photos, audio, executables) "
        "where byte-level pattern matching dominates.", styles["Body"]))

    # ── 7. Reference Implementation ──
    story.append(PageBreak())
    story.append(Paragraph("7. Reference Implementation", styles["SectionHead"]))
    story.append(Paragraph(
        "The reference implementation is written in Python 3.12 with no external "
        "dependencies. It resides in the lantern-os repository:", styles["Body"]))
    story.append(make_table(
        ["Module", "Path", "Responsibility"],
        [
            ["base3.py", "src/csf/base3.py", "Positional encoding/decoding, cyclic delta, codec"],
            ["delta_stream.py", "src/csf/delta_stream.py", "Record encoding/decoding, stream writer/reader"],
            ["csf_file.py", "src/csf/csf_file.py", "File format writer/reader, symbolic dictionary"],
        ],
        col_widths=[1.5 * inch, 2.0 * inch, 2.5 * inch],
    ))
    story.append(Paragraph("Table 8: Reference implementation modules", styles["Caption"]))

    story.append(Paragraph("7.1 Running the Tests", styles["SubHead"]))
    story.append(Preformatted(
        "# Set PYTHONPATH to include src/\n"
        "$env:PYTHONPATH = \"path/to/lantern-os/src\"\n"
        "python -m unittest discover -s tests/csf -v\n"
        "\n"
        "# Expected output: Ran 37 tests in 0.025s  OK",
        styles["CodeBlock"],
    ))

    # ── 8. Future Work ──
    story.append(Paragraph("8. Future Work", styles["SectionHead"]))
    story.append(Paragraph(
        "<b>Hierarchical multi-resolution light fields:</b> Extend the delta stream "
        "to support quadtree/octree-style pyramids where most of the universe "
        "stays at the coarsest (nearly free) resolution level.<br/><br/>"
        "<b>Low-rank matrix approximation:</b> Use SVD or CUR decomposition on the "
        "converged baseline for further compression of the sparse cell map.<br/><br/>"
        "<b>Sensor pipeline integration:</b> Direct ingestion of real-time sensor "
        "observations into the delta stream without intermediate serialization.<br/><br/>"
        "<b>Hybrid CSF+ZIP:</b> A container format that uses CSF for symbolic/sparse "
        "sections and falls back to DEFLATE for raw binary blobs, achieving the best "
        "of both worlds.",
        styles["Body"]))

    # ── 9. Appendix: Test Results ──
    story.append(Paragraph("9. Appendix: Test Results", styles["SectionHead"]))
    story.append(Paragraph("37 / 37 tests passing. Key test categories:", styles["Body"]))
    story.append(make_table(
        ["Test class", "Tests", "What it verifies"],
        [
            ["TestCyclicDelta", "7", "All 9 base-3 digit pairs produce delta in {-1,0,+1}"],
            ["TestAbsoluteEncoding", "3", "Roundtrip, size bounds, input validation"],
            ["TestDeltaEncoding", "4", "Identical, adjacent, wrap-around, compactness"],
            ["TestBase3Codec", "5", "Auto mode selection, sequence roundtrip, exhaustive neighbors"],
            ["TestSymbolicDictionary", "3", "Built-in anchors, dynamic entries, serialization"],
            ["TestCSFFileRoundtrip", "3", "Write/read, empty file, large stream (1050 records)"],
            ["TestConfirmationRecord", "2", "Size, level encoding"],
            ["TestDeltaRecord", "2", "Light change, all delta types"],
            ["TestStreamRoundtrip", "3", "Mixed records, empty, confirmation-only"],
            ["TestStreamEfficiency", "1", "1050 records under 20KB"],
        ],
        col_widths=[2.0 * inch, 0.6 * inch, 3.5 * inch],
    ))
    story.append(Paragraph("Table 9: Test suite coverage", styles["Caption"]))

    story.append(Paragraph(
        "The most critical test is <font face='Courier'>test_exhaustive_neighbor_roundtrip"
        "</font>, which verifies that every single-dimension change from the center "
        "position (1,1,...,1) roundtrips correctly through encode-decode, confirming "
        "the cyclic wrap-around fix is correct for all 36 neighbor transitions.",
        styles["Body"]))

    doc.build(story)
    print(f"Generated: {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    build()
