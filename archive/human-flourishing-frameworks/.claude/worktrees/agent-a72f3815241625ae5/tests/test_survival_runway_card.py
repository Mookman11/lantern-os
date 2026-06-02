from pathlib import Path


def test_survival_runway_card_preserves_human_first_rules():
    text = Path("docs/survival-runway-card.md").read_text(
        encoding="utf-8"
    )

    required = [
        "Stabilize the person. Protect the home base. Then build doors.",
        "Body:",
        "Home:",
        "Money:",
        "People:",
        "Next safe action:",
        "No shame.",
        "No hidden telemetry.",
        "No financial transactions",
        "No medical diagnosis.",
        "No unsafe driving",
        "Stop repo work",
        "Human safety blocks coercion",
    ]

    for item in required:
        assert item in text
