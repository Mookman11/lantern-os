from pathlib import Path


def test_active_assist_matrix_preserves_core_boundaries():
    text = Path("docs/active-assist-capability-matrix.md").read_text(
        encoding="utf-8"
    )

    required = [
        "Lead when asked. Preserve consent. Return control.",
        "LEAD-ASSIST",
        "RUNTIME-ACT",
        "STOP-REPO",
        "survival-first",
        "living operator",
        "no runtime",
        "no deployment",
        "no public writes",
        "no actuator",
    ]

    for item in required:
        assert item in text



def test_world_issues_doc_preserves_experiment_boundaries():
    text = Path("docs/world-issues-guidance-experiments.md").read_text(
        encoding="utf-8"
    )

    required = [
        "Small useful guidance. Human dignity first. Scale only what survives evidence.",
        "Each experiment must include",
        "anti-overclaim",
        "return path",
        "Human safety blocks coercion",
        "does not claim AI guidance can solve world-scale problems alone",
        "no public writes",
        "no runtime autonomy",
        "no physical-world control",
    ]

    for item in required:
        assert item in text
