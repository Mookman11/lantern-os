from pathlib import Path


def test_shield_brave_matrix_preserves_core_boundaries():
    text = Path("docs/shield-brave-matrix.md").read_text(encoding="utf-8")

    required = [
        "Shield Protocol protects the return path.",
        "Brave Reprotocol allows the door to still be opened.",
        "uncertainty from becoming a cage",
        "serious nonconsensual harm",
        "Defensive resilience only.",
        "weapons",
        "dead-man switches",
        "unsafe driving",
        "financial authority",
        "physical-world control",
    ]

    for item in required:
        assert item in text
