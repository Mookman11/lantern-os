#!/usr/bin/env python3
"""Lightweight repo-wide Seven audit.

Seven pattern:
1. Say the claim.
2. Set the guard.
3. Add tiny checks.
4. Try safely.
5. Look at reality.
6. Fix mismatch.
7. Repeat later.

This script is intentionally read-only. It does not contact networks, start
services, enable sensors, inspect secrets, mutate files, or infer anything about
people. It verifies that high-risk repo surfaces have local text anchors for the
claims and boundaries they make.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class SevenCheck:
    name: str
    claim: str
    guard: str
    file_path: str
    required_phrases: tuple[str, ...]

    def run(self, root: Path = ROOT) -> list[str]:
        path = root / self.file_path
        if not path.exists():
            return [f"{self.name}: missing {self.file_path}"]
        text = path.read_text(encoding="utf-8")
        return [
            f"{self.name}: missing phrase {phrase!r} in {self.file_path}"
            for phrase in self.required_phrases
            if phrase not in text
        ]


CHECKS: tuple[SevenCheck, ...] = (
    SevenCheck(
        name="public_surface",
        claim="Public dashboard/API surfaces are bounded and read-safe by default.",
        guard="Public does not mean uncontrolled; token-gated does not mean safe.",
        file_path="docs/public-surface-policy.md",
        required_phrases=(
            "Public does not mean uncontrolled.",
            "Live sensors | Disabled by default",
            "Mesh sync | Disabled by default",
            "HFF_ALLOW_PUBLIC_WRITES=false",
            "advisory status = governance legitimacy",
        ),
    ),
    SevenCheck(
        name="sensor_taxonomy",
        claim="Sensor definitions are not live observation or personal monitoring.",
        guard="A signal is not a person, proof, actuator permission, or consent.",
        file_path="docs/sensor-convergence.md",
        required_phrases=(
            "sensor definition != live observation",
            "live observation != personal monitoring",
            "aggregate public-data polling != device enrollment",
            "signal != person",
            "signal != proof of inner state",
        ),
    ),
    SevenCheck(
        name="public_ux",
        claim="The public dashboard should be understandable, accessible, and honest about limits.",
        guard="Do not claim translation/localization support before reviewed copy exists.",
        file_path="docs/public-ux-baseline.md",
        required_phrases=(
            "Show the state.",
            "Say the limit.",
            "Make the main path easy.",
            "Keep uncertainty visible.",
            "Do not claim translated support",
        ),
    ),
    SevenCheck(
        name="safe_entrypoint",
        claim="The safe public entrypoint patches misleading public copy before serving.",
        guard="It must not add routes, writes, sensors, mesh, agents, or deployment authority.",
        file_path="safe_app.py",
        required_phrases=(
            "It does not change\nendpoints, auth, agents, sensors, mesh sync, secrets, databases, or deployment",
            "EXPERIMENTAL ADVISORY AGENTS",
            "Skip to main content",
            "Public runtime sensor state comes from /healthz",
        ),
    ),
)


def run_all_checks() -> list[str]:
    failures: list[str] = []
    for check in CHECKS:
        failures.extend(check.run())
    return failures


def main() -> int:
    failures = run_all_checks()
    if failures:
        print("Seven surface audit failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Seven surface audit passed:")
    for check in CHECKS:
        print(f"- {check.name}: {check.claim}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
