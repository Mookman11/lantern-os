#!/usr/bin/env python3
"""Build a deterministic HFF convergence release bundle.

This utility is release tooling only. It copies required release artifacts into a
staging directory, writes a SHA256 checksum manifest for the staged files, and
creates a zip archive. It does not modify source files in the repository.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
RELEASE_NAME = "hff-convergence-v0.1"

REQUIRED_RELEASE_FILES = [
    "RELEASE_MANIFEST.md",
    "RECOVERY_README.md",
    "MIRROR_ARCHIVE_PLAN.md",
    "KEYSTONE_BOOTSTRAP.md",
    "RESTORE_DRILL_CHECKLIST.md",
    "FALSE_TRUTHS_REGISTER.md",
    "WISH_ANCHOR.md",
    "data/theorem-register.v0.1.json",
    "schemas/theorem-register.v0.1.schema.json",
    "tests/__init__.py",
    "tests/test_theorem_register.py",
    "tests/test_schema_source_lore.py",
    "tests/test_recovery_artifacts.py",
    "tests/test_ci_workflow.py",
    "tests/test_release_artifacts.py",
    "tests/test_release_bundle.py",
    "tests/test_restore_drill.py",
    "tests/test_wish_anchor.py",
    ".github/workflows/convergence-validation.yml",
    ".github/workflows/release-bundle.yml",
    ".github/workflows/restore-drill.yml",
    "tools/build_release_bundle.py",
    "tools/run_restore_drill.py",
]

OPTIONAL_CONTEXT_FILES = [
    "README.md",
    "HUMAN_TRANSPORTATION_BOUNDARY.md",
    "docs/three-way-convergence-plan-2026-05-09.md",
    "docs/three-way-durability-threat-model-2026-05-09.md",
    "docs/safety-preserving-data-collection-consent-2026-05-09.md",
    "docs/operator-chat-history-convergence-2026-05-09.md",
    "docs/release-preparation-plan-convergence-v0.1-2026-05-09.md",
    "docs/negative-outcomes-future-possibilities-convergence-2026-05-09.md",
    "docs/imaginative-lore-100-negative-outcomes-convergence-2026-05-09.md",
    "docs/imaginative-lore-100b-convergence-2026-05-09.md",
]

EXCLUDED_PARTS = {".git", "__pycache__"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_required_files(repo_root: Path, required_files: Iterable[str]) -> None:
    missing = [relative for relative in required_files if not (repo_root / relative).is_file()]
    if missing:
        raise FileNotFoundError("Missing required release files: " + ", ".join(missing))


def copy_release_files(repo_root: Path, staging_dir: Path) -> list[str]:
    copied: list[str] = []
    for relative in REQUIRED_RELEASE_FILES + OPTIONAL_CONTEXT_FILES:
        source = repo_root / relative
        if not source.is_file():
            continue
        destination = staging_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied.append(relative)
    return copied


def write_checksums(staging_dir: Path, copied_files: Iterable[str]) -> Path:
    checksum_path = staging_dir / "CHECKSUMS.sha256"
    lines = []
    for relative in sorted(set(copied_files)):
        if Path(relative).name == "CHECKSUMS.sha256":
            continue
        path = staging_dir / relative
        if path.is_file():
            lines.append(f"{sha256_file(path)}  {relative}")
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return checksum_path


def create_zip(staging_dir: Path, zip_path: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(staging_dir.rglob("*")):
            if not path.is_file() or any(part in EXCLUDED_PARTS for part in path.parts):
                continue
            archive.write(path, path.relative_to(staging_dir).as_posix())


def build_bundle(repo_root: Path, output_dir: Path, release_name: str = RELEASE_NAME) -> tuple[Path, Path]:
    ensure_required_files(repo_root, REQUIRED_RELEASE_FILES)
    output_dir.mkdir(parents=True, exist_ok=True)
    staging_dir = output_dir / release_name
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True)

    copied_files = copy_release_files(repo_root, staging_dir)
    checksum_path = write_checksums(staging_dir, copied_files)
    zip_path = output_dir / f"{release_name}.zip"
    create_zip(staging_dir, zip_path)
    return zip_path, checksum_path


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build HFF convergence release bundle")
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="Repository root to package. Defaults to this script's repository.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(REPO_ROOT / "dist"),
        help="Directory where the release staging folder and zip should be written.",
    )
    parser.add_argument(
        "--release-name",
        default=RELEASE_NAME,
        help="Release bundle base name.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    zip_path, checksum_path = build_bundle(
        repo_root=Path(args.repo_root).resolve(),
        output_dir=Path(args.output_dir).resolve(),
        release_name=args.release_name,
    )
    print(f"release_zip={zip_path}")
    print(f"checksums={checksum_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
