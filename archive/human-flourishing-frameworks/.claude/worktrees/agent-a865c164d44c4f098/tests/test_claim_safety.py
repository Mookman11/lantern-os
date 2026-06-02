#!/usr/bin/env python3
"""Tests for epistemic claim-safety baseline records."""

import unittest

from claim_safety import (
    BELIEF_STATUS_ACCEPTED,
    BELIEF_STATUS_SUPERSEDED,
    CHECK_PASSED,
    CIRCUIT_ACTION_ALLOW,
    CIRCUIT_ACTION_BLOCK,
    CIRCUIT_ACTION_SAFE_REWRITE,
    CLAIM_KIND_MEASUREMENT,
    CLAIM_KIND_MYTH,
    CLAIM_KIND_OPERATIONAL_FACT,
    CLASSIFICATION_ACCEPTED_CANDIDATE,
    CLASSIFICATION_IMPOSSIBLE_CLAIM,
    CONTRADICTION_ACTION_HUMAN_REVIEW,
    BeliefLedgerEntry,
    ClaimSafetyClassification,
    ContradictionReport,
    EpistemicCircuitBreaker,
    EvidenceBundle,
    Forecasthold,
    MythRiskPattern,
    RISK_CLASS_HIGH_IMPACT,
    VERDICT_NOT_ENOUGH_INFO,
    VERDICT_SUPPORTS,
)


class ClaimSafetyTest(unittest.TestCase):
    def test_llm_only_evidence_cannot_support_fact_claim(self):
        bundle = EvidenceBundle(
            evidence_id="ev-1",
            llm_panel_outputs=["model says the claim is true"],
            source_classifications=["llm_interpretation"],
            provenance_refs=["llm-run:1"],
            review_status=CHECK_PASSED,
        )

        self.assertTrue(bundle.is_llm_only())
        self.assertFalse(bundle.can_support_fact_claim())
        self.assertIn("non_llm_support", bundle.missing_requirements())

    def test_evidence_bundle_requires_minority_report_for_disagreement(self):
        bundle = EvidenceBundle(
            evidence_id="ev-2",
            source_refs=["source:a"],
            source_classifications=["empirical"],
            provenance_refs=["prov:a"],
            disagreements=["source:b disagrees"],
            review_status=CHECK_PASSED,
        )

        self.assertFalse(bundle.can_support_fact_claim())
        self.assertIn("minority_report", bundle.missing_requirements())

        bundle.minority_report = ["source:b disagreement preserved"]
        self.assertTrue(bundle.can_support_fact_claim())

    def test_supported_claim_can_be_accepted_candidate_only_after_requirements(self):
        claim = ClaimSafetyClassification(
            claim_id="claim-1",
            claim_text="A bounded measurement is supported by audited evidence.",
            claim_kind=CLAIM_KIND_MEASUREMENT,
            classification=CLASSIFICATION_ACCEPTED_CANDIDATE,
            verdict=VERDICT_SUPPORTS,
            source_refs=["source:dataset"],
            evidence_refs=["ev-1"],
            requires_human_review=False,
            revision_triggers=["new audited data contradicts this measurement"],
        )

        self.assertTrue(claim.can_be_accepted_candidate())

    def test_high_impact_claim_requires_human_review(self):
        claim = ClaimSafetyClassification(
            claim_id="claim-2",
            claim_text="High-impact operational claim.",
            claim_kind=CLAIM_KIND_OPERATIONAL_FACT,
            risk_class=RISK_CLASS_HIGH_IMPACT,
            classification=CLASSIFICATION_ACCEPTED_CANDIDATE,
            verdict=VERDICT_SUPPORTS,
            source_refs=["source:dataset"],
            evidence_refs=["ev-2"],
            requires_human_review=False,
            revision_triggers=["new evidence"],
        )

        self.assertFalse(claim.can_be_accepted_candidate())
        self.assertIn("human_review_for_high_impact", claim.missing_requirements())

    def test_unsupported_or_impossible_claim_requires_safe_rewrite(self):
        claim = ClaimSafetyClassification(
            claim_id="claim-3",
            claim_text="The system predicts the future.",
            claim_kind=CLAIM_KIND_MYTH,
            classification=CLASSIFICATION_IMPOSSIBLE_CLAIM,
            verdict=VERDICT_NOT_ENOUGH_INFO,
            source_refs=["source:myth"],
            evidence_refs=["ev-3"],
            revision_triggers=["credible operational evidence appears"],
        )

        self.assertTrue(claim.must_be_blocked_or_rewritten())
        self.assertIn("safe_rewrite", claim.missing_requirements())

        claim.safe_rewrite = "The system can compare bounded probabilistic scenarios."
        self.assertNotIn("safe_rewrite", claim.missing_requirements())

    def test_forecast_cannot_update_seed_by_default(self):
        forecast = Forecasthold(
            forecast_id="forecast-1",
            forecast_text="AGI arrives by a specific year.",
            time_horizon="2027",
            assumptions=["compute continues scaling"],
            source_refs=["source:forecast"],
            falsification_conditions=["frontier capability trend does not materialize"],
            may_update_seed=True,
        )

        self.assertFalse(forecast.can_update_seed_now())
        self.assertTrue(forecast.can_be_used_as_scenario())

    def test_contradiction_triggers_review_not_auto_correction(self):
        report = ContradictionReport(
            contradiction_id="contra-1",
            new_claim="New sensor value conflicts with accepted belief.",
            conflicting_beliefs=["belief-1"],
            conflicting_sources=["source:a", "source:b"],
            recommended_action=CONTRADICTION_ACTION_HUMAN_REVIEW,
        )

        self.assertFalse(report.can_auto_correct())
        self.assertTrue(report.should_trigger_review())

    def test_belief_ledger_requires_evidence_for_accepted_belief(self):
        belief = BeliefLedgerEntry(
            belief_id="belief-1",
            belief_text="Accepted belief without evidence should fail.",
            status=BELIEF_STATUS_ACCEPTED,
        )

        self.assertFalse(belief.can_be_accepted())
        self.assertIn("basis_evidence", belief.missing_requirements())

        belief.accepted_at = "2026-05-08T00:00:00Z"
        belief.basis_evidence = ["ev-1"]
        belief.source_refs = ["source:a"]
        belief.rollback_condition = "new evidence refutes it"
        self.assertTrue(belief.can_be_accepted())

    def test_belief_ledger_preserves_superseded_state(self):
        belief = BeliefLedgerEntry(
            belief_id="belief-2",
            belief_text="Old belief.",
            status=BELIEF_STATUS_SUPERSEDED,
        )

        self.assertIn("superseded_by", belief.missing_requirements())
        belief.superseded_by = ["belief-3"]
        self.assertNotIn("superseded_by", belief.missing_requirements())

    def test_myth_pattern_matches_and_requires_rewrite(self):
        pattern = MythRiskPattern(
            pattern_id="myth-1",
            pattern="sees the past",
            safe_rewrite="Retrieves and reconstructs evidence about past states.",
        )

        self.assertTrue(pattern.matches("The system sees the past."))
        self.assertEqual(pattern.missing_requirements(), [])

    def test_circuit_breaker_blocks_sacred_authority(self):
        breaker = EpistemicCircuitBreaker()

        self.assertEqual(
            breaker.action_for("This has divine authority."),
            CIRCUIT_ACTION_BLOCK,
        )
        self.assertTrue(breaker.should_block("This has divine authority."))

    def test_circuit_breaker_rewrites_future_prediction_claim(self):
        breaker = EpistemicCircuitBreaker()

        self.assertEqual(
            breaker.action_for("The system predicts the future."),
            CIRCUIT_ACTION_SAFE_REWRITE,
        )
        self.assertTrue(breaker.should_require_review("The system predicts the future."))

    def test_circuit_breaker_allows_plain_bounded_claim(self):
        breaker = EpistemicCircuitBreaker()

        self.assertEqual(
            breaker.action_for("The system compares bounded scenarios."),
            CIRCUIT_ACTION_ALLOW,
        )
        self.assertFalse(breaker.should_require_review("The system compares bounded scenarios."))

    def test_to_dict_includes_derived_fields(self):
        bundle = EvidenceBundle(evidence_id="ev-4", llm_panel_outputs=["x"])
        payload = bundle.to_dict()

        self.assertIn("is_llm_only", payload)
        self.assertIn("can_support_fact_claim", payload)

        forecast = Forecasthold()
        payload = forecast.to_dict()
        self.assertIn("can_update_seed_now", payload)
        self.assertIn("can_be_used_as_scenario", payload)


if __name__ == "__main__":
    unittest.main()
