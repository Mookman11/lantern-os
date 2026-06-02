from task_queue import (
    TaskDecision,
    classify_task,
    enqueue_dry_run,
)


def test_safe_task_defaults_to_dry_run_only():
    decision, reasons = classify_task(
        "Summarize status",
        "Create a local read-only status summary.",
    )

    assert decision == TaskDecision.DRY_RUN_ONLY
    assert "non_executing_dry_run" in reasons


def test_merge_requires_approval():
    decision, reasons = classify_task(
        "Merge release",
        "Merge the branch into master.",
    )

    assert decision == TaskDecision.REQUIRES_APPROVAL
    assert any("merge" in reason for reason in reasons)


def test_payments_are_hard_denied():
    decision, reasons = classify_task(
        "Handle payments",
        "Send money and process payment automatically.",
    )

    assert decision == TaskDecision.HARD_DENY
    assert any("payment" in reason for reason in reasons)


def test_vehicle_control_is_hard_denied():
    decision, reasons = classify_task(
        "Drive vehicle",
        "Take over physical vehicle control.",
    )

    assert decision == TaskDecision.HARD_DENY
    assert any("vehicle control" in reason or "drive" in reason for reason in reasons)


def test_enqueue_returns_non_executing_record():
    task = enqueue_dry_run(
        "Prepare notes",
        "Draft local notes for later review.",
    )

    assert task.decision == TaskDecision.DRY_RUN_ONLY
    assert task.title == "Prepare notes"
