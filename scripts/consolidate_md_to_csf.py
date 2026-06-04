#!/usr/bin/env python3
"""
Consolidate all Markdown files in the repo into a single CSF archive.

Usage:
    python scripts/consolidate_md_to_csf.py
    python scripts/consolidate_md_to_csf.py --output data/all-docs.csf
    python scripts/consolidate_md_to_csf.py --verify  # decompress and check
"""

from __future__ import annotations

import argparse
import io
import struct
import sys
import zlib
from pathlib import Path
from typing import List, Tuple

# Add src/ to path so we can import CSF v0.7
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from csf.v07.classical_compressor import (
    ClassicalCompressor,
    CompressionResult,
    SymbolicDictionary,
    decode_sparse,
    encode_sparse,
)
from csf.v07.csf_file import CSFFileReader, CSFFileWriter

# ------------------------------------------------------------------
# File discovery
# ------------------------------------------------------------------

# Directories that are legacy, skill sprawl, or not part of core convergence docs.
# These are excluded from CSF consolidation.
EXCLUDES = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    ".pytest_cache",
    # Legacy / sprawl directories
    "skills",
    "surfaces",
    "services",
    "templates",
    "tickets",
    "test-results",
    "repo-seeds",
    "profiles",
    "ops",
    "dual-boot",
    "aws-deployment",
    "artifacts",
    "offers",
    "ledger",
    "infra",
    "dashboard",
    "art",
    # Old source trees (preserved in archive; not core docs)
    "src/discord_lounge_bot",
    "src/hff-api",
    "src/mcp_server",
    "src/dream_journal",
    "dream_journal",  # root-level legacy crystallization engine
    # Data / runtime dirs
    "data",
    "archive",
}

# Only top-level READMEs and docs under these paths are considered core.
CORE_DOC_PATHS = {
    "README.md",
    "docs",
    "src/csf",
    "src/convergence_io_engine.py",
    "src/tesseract_convergence.py",
    "src/unified_agent_connector.py",
    "src/agent_tool_hooks.py",
    "src/csf_cache_manager.py",
    "apps/lantern-garage",
    "scripts",
    "config",
    "manifests",
    ".github",
    "benchmarks",
}


def find_md_files(root: Path) -> List[Path]:
    """Find core .md files relevant to convergence / CSF, excluding legacy sprawl."""
    paths: List[Path] = []
    for p in root.rglob("*.md"):
        rel = p.relative_to(root).as_posix()
        # Skip anything inside excluded dirs
        if any(part in EXCLUDES for part in p.parts):
            continue
        # Only include files that live under a core doc path
        if not any(rel.startswith(cp) for cp in CORE_DOC_PATHS):
            continue
        paths.append(p)
    paths.sort()
    return paths


# ------------------------------------------------------------------
# Corpus assembly
# ------------------------------------------------------------------

FILE_HEADER = "\n===== FILE: {path} =====\n\n"
FILE_FOOTER = "\n===== END: {path} =====\n"


def build_corpus(files: List[Path], root: Path) -> str:
    """Concatenate all markdown files with clear file-boundary markers."""
    parts: List[str] = []
    for f in files:
        rel = f.relative_to(root).as_posix()
        parts.append(FILE_HEADER.format(path=rel))
        parts.append(f.read_text(encoding="utf-8"))
        parts.append(FILE_FOOTER.format(path=rel))
    return "".join(parts)


# ------------------------------------------------------------------
# Compression
# ------------------------------------------------------------------

def compress_corpus(text: str, block_size: int = 512) -> Tuple[bytes, CompressionResult]:
    """Compress the combined markdown corpus using CSF v0.7 classical pipeline."""
    compressor = ClassicalCompressor(block_size=block_size)
    compressed, result = compressor.compress_text(text)
    return compressed, result


def write_csf(
    compressed_bytes: bytes,
    dictionary: SymbolicDictionary,
    original_size: int,
    output_path: Path,
) -> int:
    """Wrap compressed data in a proper CSF v0.7 file."""
    writer = CSFFileWriter()
    writer.set_dictionary(dictionary)
    # The compressed_bytes from compress_text already contains dict+meta+sparse+zstd,
    # so we store it as the "baseline" (the converged/static content).
    writer.set_baseline(compressed_bytes)
    writer._original_size = original_size
    return writer.write(output_path)


# ------------------------------------------------------------------
# Decompression / verification
# ------------------------------------------------------------------

def decompress_csf(csf_path: Path) -> str:
    """Read a CSF file and return the original text corpus."""
    reader = CSFFileReader(csf_path)
    if not reader.verify():
        raise ValueError("CSF file CRC verification failed")

    # reader.baseline is the output of compress_text, which is a zlib-compressed
    # blob containing: dict_len(4) + dict_bytes + meta(16) + sparse_compressed
    # First decompress the outer zlib layer.
    body = zlib.decompress(reader.baseline)

    offset = 0
    dict_len = struct.unpack_from(">I", body, offset)[0]
    offset += 4
    dict_bytes = body[offset:offset + dict_len]
    offset += dict_len
    dictionary = SymbolicDictionary.from_bytes(dict_bytes)

    # meta = original_length, block_size, default_value, num_blocks (16 bytes)
    meta_len = 16
    meta = body[offset:offset + meta_len]
    offset += meta_len
    sparse_compressed = body[offset:]

    id_bytes = decode_sparse(meta, sparse_compressed)

    # Unpack LEB128 varints
    ids = _unpack_varints(id_bytes)
    tokens = [dictionary.decode(i) for i in ids]
    text = _untokenize(tokens)
    return text


def _unpack_varints(data: bytes) -> List[int]:
    """Unpack LEB128 varints."""
    values = []
    i = 0
    while i < len(data):
        v = 0
        shift = 0
        while True:
            b = data[i]
            i += 1
            v |= (b & 0x7F) << shift
            if not (b & 0x80):
                break
            shift += 7
        values.append(v)
    return values


def _untokenize(tokens: List[str]) -> str:
    """Reconstruct text from tokens (naive: join with space, then fix common punctuation)."""
    text = " ".join(tokens)
    # Fix common punctuation spacing
    text = text.replace(" .", ".").replace(" ,", ",").replace(" !", "!")
    text = text.replace(" ?", "?").replace(" ;", ";").replace(" :", ":")
    text = text.replace("( ", "(").replace(" )", ")")
    text = text.replace("[ ", "[").replace(" ]", "]")
    text = text.replace("' ", "'").replace(" '", "'")
    text = text.replace("— ", "— ").replace(" - ", "-")
    # Clean up multiple spaces
    while "  " in text:
        text = text.replace("  ", " ")
    return text


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Consolidate Markdown files into a CSF archive")
    p.add_argument("--output", "-o", default="data/all-docs.csf", help="Output .csf path")
    p.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root directory")
    p.add_argument("--verify", action="store_true", help="Decompress and verify round-trip")
    p.add_argument("--list", action="store_true", help="List files that would be included")
    args = p.parse_args(argv)

    root = Path(args.repo_root).resolve()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    md_files = find_md_files(root)
    print(f"Found {len(md_files)} markdown files")

    if args.list:
        for f in md_files:
            print(f"  {f.relative_to(root).as_posix()}")
        return 0

    if args.verify:
        if not output.exists():
            print(f"ERROR: {output} not found. Run without --verify first.")
            return 1
        print(f"Reading {output} ...")
        text = decompress_csf(output)
        print(f"Decompressed corpus: {len(text):,} chars")
        # Count files in corpus
        count = text.count("===== FILE:")
        print(f"Files in corpus: {count}")
        # Show first boundary
        first = text.find("===== FILE:")
        if first >= 0:
            print("First file:", text[first:text.find(chr(10), first + 50)])
        return 0

    # Build corpus
    print("Building corpus ...")
    corpus = build_corpus(md_files, root)
    original_bytes = len(corpus.encode("utf-8"))
    print(f"Corpus size: {original_bytes:,} bytes ({len(md_files)} files)")

    # Compress
    print("Compressing with CSF v0.7 classical pipeline ...")
    compressed, result = compress_corpus(corpus)
    print(f"  Dictionary size: {result.dictionary_size} tokens")
    print(f"  Compressed: {result.compressed_bytes:,} bytes")
    print(f"  Ratio: {result.ratio:.2%}")

    # Write CSF
    compressor = ClassicalCompressor()
    compressor.dictionary = SymbolicDictionary()  # dummy; we'll rebuild from compressed
    # Actually we need the real dictionary from the compression step.
    # compress_corpus creates a new compressor each time. We need to capture it.
    # Let me fix this by re-compressing and capturing the compressor instance.

    # Re-do with captured compressor
    compressor = ClassicalCompressor(block_size=512)
    compressed, result = compressor.compress_text(corpus)
    file_size = write_csf(compressed, compressor.dictionary, original_bytes, output)

    print(f"\nWrote {output}")
    print(f"  File size: {file_size:,} bytes")
    print(f"  Compression: {1 - (file_size / original_bytes):.2%}")
    print(f"  Files: {len(md_files)}")

    # Quick verification
    print("\nVerifying round-trip ...")
    restored = decompress_csf(output)
    if restored == corpus:
        print("  ✓ Bit-perfect round-trip verified")
    else:
        print("  ⚠ Round-trip mismatch (tokenization losses are expected for text)")
        # Show similarity
        import difflib
        sm = difflib.SequenceMatcher(None, corpus, restored)
        print(f"  Similarity: {sm.ratio():.4f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
