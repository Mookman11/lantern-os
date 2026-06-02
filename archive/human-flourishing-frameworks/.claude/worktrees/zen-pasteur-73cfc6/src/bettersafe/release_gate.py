"""Executable release gate for BetterSafe.

The gate converts the current convergence doctrine into a small behavior surface:
release candidates are evaluated for the happy/fun/safe attractor, privacy,
consent, return paths, and release-impact integrity.
"""

from __future__ import annotations

from dataclasses import dataclass, field


REQUIRED_ATTRACTORS = frozenset({"happy", "fun", "safe"})

BLOCKING_RISKS = frozenset(
    {
        "private_citizen_exposure",
        "raw_bank_credentials",
        "live_money_movement",
        "hidden_telemetry",
        "child_data_collection",
        "third_party_outreach_without_consent",
        "medical_legal_financial_authority",
        "mythic_or_religious_authority_claim",
        "public_private_data",
    }
)


@dataclass(frozen=True)
class ReleaseCandidate:
    """Facts needed to evaluate a BetterSafe release candidate."""

    name: str
    attractors: set[str] = field(default_factory=set)
    risks: set[str] = field(default_factory=set)
    has_return_path: bool = False
    has_privacy_review: bool = False
    has_operator_approval: bool = False
    has_behavior_change: bool = False


@dataclass(frozen=True)
class GateResult:
    """Release-gate result."""

    allowed: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]


def evaluate_release(candidate: ReleaseCandidate) -> GateResult:
    """Evaluate whether a release candidate is inside current bounds.

    This gate is intentionally evidence-weighted rather than eternal. It blocks
    current high-confidence hazards and warns when a change is docs-only instead
    of behavior-affecting.
    """

    blockers: list[str] = []
    warnings: list[str] = []

    missing_attractors = REQUIRED_ATTRACTORS - candidate.attractors
    if missing_attractors:
        blockers.append("missing_attractors:" + ",".join(sorted(missing_attractors)))

    blocking_risks = BLOCKING_RISKS & candidate.risks
    if blocking_risks:
        blockers.append("blocking_risks:" + ",".join(sorted(blocking_risks)))

    if not candidate.has_return_path:
        blockers.append("missing_return_path")
    if not candidate.has_privacy_review:
        blockers.append("missing_privacy_review")
    if not candidate.has_operator_approval:
        blockers.append("missing_operator_approval")
    if not candidate.has_behavior_change:
        warnings.append("docs_only_or_no_behavior_change")

    return GateResult(
        allowed=not blockers,
        blockers=tuple(blockers),
        warnings=tuple(warnings),
    )


def summarize_gate(result: GateResult) -> str:
    """Return a compact status string for CLI/UI/status surfaces."""

    if result.allowed and result.warnings:
        return "allowed_with_warnings:" + ";".join(result.warnings)
    if result.allowed:
        return "allowed"
    return "blocked:" + ";".join(result.blockers)
