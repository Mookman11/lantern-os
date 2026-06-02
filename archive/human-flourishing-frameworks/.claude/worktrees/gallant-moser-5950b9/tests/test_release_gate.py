from bettersafe.release_gate import (
    ReleaseCandidate,
    evaluate_release,
    summarize_gate,
)


def test_valid_release_candidate_allowed():
    candidate = ReleaseCandidate(
        name="navigator-v0",
        attractors={"happy", "fun", "safe"},
        risks=set(),
        has_return_path=True,
        has_privacy_review=True,
        has_operator_approval=True,
        has_behavior_change=True,
    )

    result = evaluate_release(candidate)

    assert result.allowed is True
    assert result.blockers == ()
    assert summarize_gate(result) == "allowed"



def test_private_data_risk_blocks_release():
    candidate = ReleaseCandidate(
        name="unsafe-release",
        attractors={"happy", "fun", "safe"},
        risks={"private_citizen_exposure"},
        has_return_path=True,
        has_privacy_review=True,
        has_operator_approval=True,
        has_behavior_change=True,
    )

    result = evaluate_release(candidate)

    assert result.allowed is False
    assert any("blocking_risks" in item for item in result.blockers)



def test_missing_attractor_blocks_release():
    candidate = ReleaseCandidate(
        name="joyless-release",
        attractors={"safe"},
        risks=set(),
        has_return_path=True,
        has_privacy_review=True,
        has_operator_approval=True,
        has_behavior_change=True,
    )

    result = evaluate_release(candidate)

    assert result.allowed is False
    assert any("missing_attractors" in item for item in result.blockers)



def test_docs_only_release_warns():
    candidate = ReleaseCandidate(
        name="docs-only",
        attractors={"happy", "fun", "safe"},
        risks=set(),
        has_return_path=True,
        has_privacy_review=True,
        has_operator_approval=True,
        has_behavior_change=False,
    )

    result = evaluate_release(candidate)

    assert result.allowed is True
    assert "docs_only_or_no_behavior_change" in result.warnings
