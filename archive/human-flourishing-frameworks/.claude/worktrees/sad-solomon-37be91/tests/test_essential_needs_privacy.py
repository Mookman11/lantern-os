"""Privacy and redaction boundary tests for BetterSafe Essential Needs artifacts."""

from pathlib import Path

DOC = Path("docs/bettersafe-essential-needs-navigator.md")


def read_doc() -> str:
    return DOC.read_text(encoding="utf-8").lower()


def test_redaction_rules_present():
    text = read_doc()
    assert "redaction rules" in text
    assert "private-citizen names" in text
    assert "contact information" in text
    assert "bank credentials" in text


def test_private_role_labels_present():
    text = read_doc()
    required_roles = [
        "private participant",
        "household partner",
        "trusted adult",
        "protected minor",
        "third party",
        "pilot user",
    ]

    for role in required_roles:
        assert role in text


def test_manual_only_boundaries_present():
    text = read_doc()

    required_boundaries = [
        "manual-only",
        "local/private first",
        "no raw bank credentials",
        "no live money movement",
        "no hidden telemetry",
    ]

    for boundary in required_boundaries:
        assert boundary in text
