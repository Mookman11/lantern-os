#!/usr/bin/env python3
"""Run an HFF convergence restore drill from a generated release bundle.

The drill builds the release bundle, verifies the bundle-local checksum manifest,
extracts the bundle to an isolated directory, verifies required recovery files,
and runs the guardrail tests from the extracted copy.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

try:  # Supports `python -m tools.run_restore_drill` and test imports.
    from tools.build_release_bundle import build_bundle
except ModuleNotFoundError:  # Supports `python tools/run_restore_drill.py`.
    from build_release_bundle import build_bundle


REPO_ROOT = Path(__file__).resolve().parents[1]
RELEASE_NAME = "hff-convergence-v0.1"

RESTORE_TEST_PATTERNS = [
    "test_theorem_register.py",
    "test_schema_source_lore.py",
    "test_recovery_artifacts.py",
    "test_ci_workflow.py",
    "test_release_bundle.py",
    "test_restore_drill.py",
    "test_wish_anchor.py",
]

REQUIRED_RESTORE_FILES = [
    "RELEASE_MANIFEST.md",
    "RECOVERY_README.md",
    "MIRROR_ARCHIVE_PLAN.md",
    "KEYSTONE_BOOTSTRAP.md",
    "RESTORE_DRILL_CHECKLIST.md",
    "FALSE_TRUTHS_REGISTER.md",
    "WISH_ANCHOR.md",
    "CHECKSUMS.sha256",
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


@dataclass(frozen=True)
class RestoreDrillResult:
    release_zip: Path
    checksum_file: Path
    extract_dir: Path
    report_file: Path
    tests_run: tuple[str, ...]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_checksum_file(root: Path, checksum_file: Path) -> list[str]:
    if not checksum_file.is_file():
        raise FileNotFoundError(f"missing checksum file: {checksum_file}")

    verified: list[str] = []
    for line_number, raw_line in enumerate(checksum_file.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        if "PRE_RELEASE_PLACEHOLDER" in line:
            raise ValueError(f"placeholder checksum found on line {line_number}")
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            raise ValueError(f"malformed checksum line {line_number}: {raw_line!r}")
        expected_hash, relative = parts
        if len(expected_hash) != 64 or any(char not in "0123456789abcdef" for char in expected_hash):
            raise ValueError(f"invalid SHA256 digest on line {line_number}: {expected_hash}")
        target = root / relative
        if not target.is_file():
            raise FileNotFoundError(f"checksum target missing: {relative}")
        actual_hash = sha256_file(target)
        if actual_hash != expected_hash:
            raise ValueError(f"checksum mismatch for {relative}: expected {expected_hash}, got {actual_hash}")
        verified.append(relative)
    if not verified:
        raise ValueError("checksum file verified zero files")
    return verified


def verify_required_restore_files(extract_dir: Path) -> None:
    missing = [relative for relative in REQUIRED_RESTORE_FILES if not (extract_dir / relative).is_file()]
    if missing:
        raise FileNotFoundError("missing required restore files: " + ", ".join(missing))


def extract_release_zip(release_zip: Path, extract_dir: Path) -> None:
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True)
    with zipfile.ZipFile(release_zip, "r") as archive:
        archive.extractall(extract_dir)


def run_restore_tests(extract_dir: Path, patterns: list[str] | None = None) -> tuple[str, ...]:
    patterns = RESTORE_TEST_PATTERNS if patterns is None else patterns
    completed_patterns: list[str] = []
    for pattern in patterns:
        command = [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            pattern,
            "-t",
            ".",
        ]
        subprocess.run(command, cwd=extract_dir, check=True)
        completed_patterns.append(pattern)
    return tuple(completed_patterns)


def write_report(result: RestoreDrillResult, verified_files: list[str]) -> None:
    lines = [
        "# Restore Drill Report",
        "",
        f"release_zip: {result.release_zip}",
        f"checksum_file: {result.checksum_file}",
        f"extract_dir: {result.extract_dir}",
        "",
        "verified_checksum_files:",
        *[f"- {relative}" for relative in verified_files],
        "",
        "tests_run:",
        *[f"- {pattern}" for pattern in result.tests_run],
        "",
        "result: PASS",
        "",
    ]
    result.report_file.write_text("\n".join(lines), encoding="utf-8")


def run_restore_drill(repo_root: Path, output_dir: Path, run_tests: bool = True) -> RestoreDrillResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    release_zip, checksum_file = build_bundle(repo_root, output_dir, RELEASE_NAME)

    staging_root = output_dir / RELEASE_NAME
    verified_files = verify_checksum_file(staging_root, checksum_file)

    extract_dir = output_dir / f"{RELEASE_NAME}-restore"
    extract_release_zip(release_zip, extract_dir)
    verify_required_restore_files(extract_dir)
    verify_checksum_file(extract_dir, extract_dir / "CHECKSUMS.sha256")

    tests_run: tuple[str, ...] = ()
    if run_tests:
        tests_run = run_restore_tests(extract_dir)

    result = RestoreDrillResult(
        release_zip=release_zip,
        checksum_file=checksum_file,
        extract_dir=extract_dir,
        report_file=output_dir / "RESTORE_DRILL_REPORT.md",
        tests_run=tests_run,
    )
    write_report(result, verified_files)
    return result


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run HFF convergence restore drill")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to build from.")
    parser.add_argument("--output-dir", default=str(REPO_ROOT / "dist"), help="Output directory for drill files.")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests from the extracted bundle.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    result = run_restore_drill(
        repo_root=Path(args.repo_root).resolve(),
        output_dir=Path(args.output_dir).resolve(),
        run_tests=not args.skip_tests,
    )
    print(f"release_zip={result.release_zip}")
    print(f"checksum_file={result.checksum_file}")
    print(f"extract_dir={result.extract_dir}")
    print(f"report_file={result.report_file}")
    print("result=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
