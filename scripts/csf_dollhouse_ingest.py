#!/usr/bin/env python3
"""Ingest dollhouse .md files into CSF format.

Reads each .md in data/dollhouse/ recursively, compresses via CSF v0.7
symbolic compressor, writes individual .csf files and a merged archive.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from csf.v07.csf_symbolic_compressor import SymbolicCompressor, CompressionResult
from csf import CsfArchive

DOLLHOUSE_DIR = Path(__file__).resolve().parents[1] / "data" / "dollhouse"
CSF_OUT = DOLLHOUSE_DIR / "csf"

# Anchors we look for across documents
SYMBOLIC_ANCHORS = [
    "Convergence", "Fleet", "RAG", "Dollhouse", "MCP", "Agent",
    "Self-Correcting", "Handoff", "Context", "Learning", "Memory",
    "Skill", "Knowledge", "Book", "Model", "Chat",
]


def find_anchors(text: str) -> list[str]:
    return [a for a in SYMBOLIC_ANCHORS if a.lower() in text.lower()]


def main() -> None:
    CSF_OUT.mkdir(parents=True, exist_ok=True)

    md_files = sorted(DOLLHOUSE_DIR.rglob("*.md"))
    if not md_files:
        print("No .md files found in", DOLLHOUSE_DIR)
        sys.exit(1)

    compressor = SymbolicCompressor()
    archive = CsfArchive()
    rows: list[tuple[str, int, int, float, list[str]]] = []

    for md in md_files:
        # Skip files inside the csf output dir
        if CSF_OUT in md.parents:
            continue

        text = md.read_text(encoding="utf-8")
        compressed_bytes, result = compressor.compress_text(text)

        # Write individual .csf
        out_name = md.relative_to(DOLLHOUSE_DIR).with_suffix(".csf")
        out_path = CSF_OUT / out_name
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(compressed_bytes)

        # Add to merged archive
        archive.add_bytes(compressed_bytes)

        anchors = find_anchors(text)
        rows.append((
            str(md.relative_to(DOLLHOUSE_DIR)),
            result.original_bytes,
            result.compressed_bytes,
            result.ratio,
            anchors,
        ))

    # Write merged archive
    merged_path = CSF_OUT / "dollhouse-merged.csf"
    with open(merged_path, "w+b") as f:
        archive._write_to(f)

    # Print summary table
    print(f"\n{'File':<45} {'Orig':>7} {'CSF':>7} {'Ratio':>7}  Anchors")
    print("-" * 100)
    for name, orig, comp, ratio, anchors in rows:
        anchor_str = ", ".join(anchors) if anchors else "-"
        print(f"{name:<45} {orig:>7} {comp:>7} {ratio:>6.1%}  {anchor_str}")

    total_orig = sum(r[1] for r in rows)
    total_comp = sum(r[2] for r in rows)
    total_ratio = 1.0 - (total_comp / total_orig) if total_orig else 0.0
    print("-" * 100)
    print(f"{'TOTAL':<45} {total_orig:>7} {total_comp:>7} {total_ratio:>6.1%}")
    print(f"\nMerged archive: {merged_path}")
    print(f"Merged archive size: {merged_path.stat().st_size} bytes")
    print(f"Individual .csf files: {len(rows)}")


if __name__ == "__main__":
    main()
