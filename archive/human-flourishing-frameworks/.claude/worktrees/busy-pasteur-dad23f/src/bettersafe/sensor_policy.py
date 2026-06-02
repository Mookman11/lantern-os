"""Operator-owned sensor policy for BetterSafe.

This module upgrades sensors by making consent executable. It supports a higher
sync band for the operator under the Bravery Protocol while keeping non-operator
sensing separate and blocked unless explicitly consented.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SubjectClass(str, Enum):
    OPERATOR = "operator"
    CONSENTING_PILOT_USER = "consenting_pilot_user"
    PRIVATE_PARTICIPANT = "private_participant"
    PROTECTED_MINOR = "protected_minor"
    THIRD_PARTY = "third_party"
    PUBLIC_USER = "public_user"


class SensorClass(str, Enum):
    MANUAL_CHECKIN = "manual_checkin"
    PUSH_TO_TALK = "push_to_talk"
    LOCAL_TASK_STATE = "local_task_state"
    PUBLIC_CONTEXT = "public_context"
    CALENDAR = "calendar"
    LOCATION = "location"
    CAMERA_PHOTO = "camera_photo"
    WEARABLE_BODY_STATE = "wearable_body_state"
    BACKGROUND_AUDIO = "background_audio"
    FINANCIAL_ACCOUNT_STATE = "financial_account_state"
    RAW_CREDENTIAL = "raw_credential"


@dataclass(frozen=True)
class SensorRequest:
    """A requested sensor use."""

    subject: SubjectClass
    sensor: SensorClass
    explicit_consent: bool = False
    local_first: bool = False
    visible_status: bool = False
    hard_off_switch: bool = False
    summary_over_raw: bool = True
    durable_storage: bool = False
    redaction_review: bool = False
    purpose: str = "convergence"


@dataclass(frozen=True)
class SensorDecision:
    """Sensor policy decision."""

    allowed: bool
    mode: str
    blockers: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


LOW_RISK_OPERATOR_SENSORS = frozenset(
    {
        SensorClass.MANUAL_CHECKIN,
        SensorClass.PUSH_TO_TALK,
        SensorClass.LOCAL_TASK_STATE,
        SensorClass.PUBLIC_CONTEXT,
    }
)

REVIEWED_OPERATOR_SENSORS = frozenset(
    {
        SensorClass.CALENDAR,
        SensorClass.LOCATION,
        SensorClass.CAMERA_PHOTO,
        SensorClass.WEARABLE_BODY_STATE,
        SensorClass.BACKGROUND_AUDIO,
        SensorClass.FINANCIAL_ACCOUNT_STATE,
    }
)

NEVER_RAW_BY_DEFAULT = frozenset({SensorClass.RAW_CREDENTIAL})


def evaluate_sensor_request(request: SensorRequest) -> SensorDecision:
    """Evaluate whether a sensor request is inside the current pilot policy."""

    blockers: list[str] = []
    warnings: list[str] = []

    if request.sensor in NEVER_RAW_BY_DEFAULT:
        return SensorDecision(
            allowed=False,
            mode="blocked",
            blockers=("raw_credentials_not_allowed",),
        )

    if request.subject == SubjectClass.OPERATOR:
        return _evaluate_operator_request(request)

    if not request.explicit_consent:
        blockers.append("missing_non_operator_consent")

    if request.subject in {SubjectClass.PROTECTED_MINOR, SubjectClass.THIRD_PARTY}:
        blockers.append(f"subject_requires_separate_review:{request.subject.value}")

    if request.durable_storage and not request.redaction_review:
        blockers.append("durable_storage_requires_redaction_review")

    return SensorDecision(
        allowed=not blockers,
        mode="non_operator_consented" if not blockers else "blocked",
        blockers=tuple(blockers),
        warnings=tuple(warnings),
    )


def _evaluate_operator_request(request: SensorRequest) -> SensorDecision:
    blockers: list[str] = []
    warnings: list[str] = []

    if not request.explicit_consent:
        blockers.append("missing_operator_consent")

    if request.sensor in LOW_RISK_OPERATOR_SENSORS:
        mode = "operator_allowed"
    elif request.sensor in REVIEWED_OPERATOR_SENSORS:
        mode = "operator_reviewed_sensor"
        if not request.local_first:
            warnings.append("prefer_local_first")
        if not request.visible_status:
            blockers.append("missing_visible_status")
        if not request.hard_off_switch:
            blockers.append("missing_hard_off_switch")
        if request.durable_storage and not request.redaction_review:
            blockers.append("durable_storage_requires_redaction_review")
        if not request.summary_over_raw:
            warnings.append("raw_stream_requires_extra_review")
    else:
        mode = "unknown_sensor"
        blockers.append("unknown_sensor_class")

    return SensorDecision(
        allowed=not blockers,
        mode=mode if not blockers else "blocked",
        blockers=tuple(blockers),
        warnings=tuple(warnings),
    )


def summarize_sensor_decision(decision: SensorDecision) -> str:
    """Return a compact status string for UI/CLI surfaces."""

    if decision.allowed and decision.warnings:
        return f"{decision.mode}_with_warnings:" + ";".join(decision.warnings)
    if decision.allowed:
        return decision.mode
    return "blocked:" + ";".join(decision.blockers)
