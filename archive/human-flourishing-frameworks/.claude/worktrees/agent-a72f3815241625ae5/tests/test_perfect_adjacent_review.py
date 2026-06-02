#!/usr/bin/env python3
"""Tests for perfect-adjacent review gating."""

import unittest

from perfect_adjacent_review import (
    CHECK_FAILED,
    CHECK_NEEDS_REVIEW,
    CHECK_PASSED,
    CLAIM_SCOPE_FORECAST,
    CLAIM_SCOPE_OPERATIONAL_EVIDENCE,
    ConfidenceAssessment,
    CatastrophicRiskReview,
    PDoomContext,
    RISK_LOW,
    RISK_MEDIUM,
    RuntimeHookEvidence,
    SecurityPosture,
    SourceClassification,
    SOURCE_KIND_FORECAST,
    SOURCE_QUALITY_AUDITED,
    SOURCE_QUALITY_SCENARIO_FORECAST,
    PerfectAdjacentReview,
    blocked_capability_advertising_record,
    blocked_unknown_unknown_record,
    passing_human_reviewed_record,
)


def populated_best_current_record() -> PerfectAdjacentReview:
    record = passing_human_reviewed_record(evidence_refs=["source:reviewed"])
    record.best_current_outcome = "Publish a bounded, best-effort status update."
    record.candidate_options_considered = [
        "publish nothing",
        "publish bounded status update",
    ]
    record.rejected_options_with_reasons = [
        "publish nothing: leaves users without current uncertainty context",
    ]
    record.revision_triggers = ["new sensor evidence contradicts current state"]
    record.monitoring_plan = "Re-check sensors and review state before the next update."
    record.sensor_questions = ["Is the status endpoint still healthy?"]
    record.sensor_refs = ["sensor:status-endpoint"]
    record.panic_risk_level = RISK_LOW
    return record


def attach_all_runtime_hooks(record: PerfectAdjacentReview) -> None:
    record.runtime_hook_evidence.attached_hooks = {
        hook: True for hook in record.runtime_hook_evidence.required_hooks
    }


class PerfectAdjacentReviewTest(unittest.TestCase):
    def test_default_record_blocks_publication_advertising_best_current_and_autonomy(self):
        record = PerfectAdjacentReview()

        self.assertFalse(record.can_publish())
        self.assertFalse(record.can_claim_best_current_outcome())
        self.assertFalse(record.can_advertise_capability())
        self.assertFalse(record.can_act_autonomously())
        self.assertTrue(record.human_review_required)
        self.assertIn("source_quality", record.needs_review_checks())

    def test_failed_check_blocks_even_if_flags_claim_safe(self):
        record = passing_human_reviewed_record(evidence_refs=["source:audit"])
        record.reasoning_integrity = CHECK_FAILED
        record.safe_to_publish = True
        record.safe_to_act_autonomously = True
        record.human_review_required = False

        self.assertFalse(record.can_publish())
        self.assertFalse(record.can_claim_best_current_outcome())
        self.assertFalse(record.can_advertise_capability())
        self.assertFalse(record.can_act_autonomously())
        self.assertEqual(record.failed_checks(), ["reasoning_integrity"])

    def test_can_publish_blocks_needs_review_even_if_human_review_required_false(self):
        record = PerfectAdjacentReview()
        record.human_review_required = False
        record.safe_to_publish = True

        self.assertFalse(record.can_publish())
        self.assertIn("source_quality", record.needs_review_checks())

    def test_confidence_assessment_defaults_to_uncalibrated_judgment(self):
        assessment = ConfidenceAssessment(
            basis_evidence=["local tests"],
            missing_evidence=["runtime telemetry"],
        )

        self.assertFalse(assessment.is_calibrated())
        self.assertFalse(assessment.is_valid_for_public_probability())
        self.assertFalse(assessment.calibrated_probability)

    def test_p_doom_context_is_credible_nonzero_not_panic_or_proof(self):
        context = PDoomContext(source_refs=["source:cais", "source:ai-impacts"])

        self.assertTrue(context.is_valid_context())
        self.assertFalse(context.proof_of_doom)
        self.assertFalse(context.panic_authority)
        self.assertFalse(context.calibrated_probability)

    def test_invalid_p_doom_context_blocks_best_effort_defense(self):
        record = passing_human_reviewed_record(evidence_refs=["source:reviewed"])
        record.p_doom_context.proof_of_doom = True

        self.assertFalse(record.is_valid_best_effort_defense())
        self.assertFalse(record.can_publish())

    def test_source_classification_forecast_is_not_operational_evidence(self):
        classification = SourceClassification(
            source_url="https://ai-2027.com/research/timelines-forecast",
            source_kind=SOURCE_KIND_FORECAST,
            source_quality=SOURCE_QUALITY_SCENARIO_FORECAST,
            claim_scope=CLAIM_SCOPE_FORECAST,
            operational_assumption=False,
        )

        self.assertFalse(classification.is_operational_evidence())

    def test_source_classification_requires_audited_operational_scope(self):
        classification = SourceClassification(
            source_url="https://example.invalid/audit",
            source_quality=SOURCE_QUALITY_AUDITED,
            claim_scope=CLAIM_SCOPE_OPERATIONAL_EVIDENCE,
            operational_assumption=True,
        )

        self.assertTrue(classification.is_operational_evidence())

    def test_catastrophic_risk_review_defaults_to_needs_review(self):
        review = CatastrophicRiskReview()

        self.assertFalse(review.is_cleared())
        self.assertIn("bio_chemical", review.needs_review_checks())
        self.assertIn("model_theft", review.needs_review_checks())

    def test_security_posture_defaults_to_missing_controls(self):
        posture = SecurityPosture()

        self.assertFalse(posture.is_cleared())
        self.assertIn("model_weight_security", posture.missing_security_controls())
        self.assertIn("exfiltration_risk", posture.missing_security_controls())

    def test_runtime_hook_evidence_blocks_until_all_hooks_attached(self):
        evidence = RuntimeHookEvidence()

        self.assertFalse(evidence.is_runtime_enforcement_ready())
        self.assertIn("status_endpoint_review_gate", evidence.missing_runtime_hooks())

        evidence.attached_hooks = {hook: True for hook in evidence.required_hooks}
        self.assertTrue(evidence.is_runtime_enforcement_ready())
        self.assertEqual(evidence.missing_runtime_hooks(), [])

    def test_impossible_claims_block_every_gate(self):
        record = populated_best_current_record()
        record.impossible_claims = ["perfect_safety", "complete_understanding"]
        record.capability_advertising_allowed = True
        record.advertising_risk_level = RISK_LOW
        record.safe_to_act_autonomously = True
        record.runtime_enforcement_ready = True
        attach_all_runtime_hooks(record)

        self.assertEqual(
            record.impossible_claim_violations(),
            ["perfect_safety", "complete_understanding"],
        )
        self.assertFalse(record.can_publish())
        self.assertFalse(record.can_claim_best_current_outcome())
        self.assertFalse(record.can_advertise_capability())
        self.assertFalse(record.can_act_autonomously())

    def test_inferred_impossible_claims_block_every_gate(self):
        record = populated_best_current_record()
        record.advertised_capabilities = ["This system provides guaranteed defense."]
        record.capability_advertising_allowed = True
        record.advertising_risk_level = RISK_LOW
        record.safe_to_act_autonomously = True
        record.runtime_enforcement_ready = True
        attach_all_runtime_hooks(record)

        self.assertEqual(record.inferred_impossible_claims(), ["guaranteed_defense"])
        self.assertFalse(record.can_publish())
        self.assertFalse(record.can_claim_best_current_outcome())
        self.assertFalse(record.can_advertise_capability())
        self.assertFalse(record.can_act_autonomously())

    def test_unknown_non_impossible_claim_labels_do_not_block_by_themselves(self):
        record = passing_human_reviewed_record(evidence_refs=["source:reviewed"])
        record.impossible_claims = ["best_effort_defense"]

        self.assertEqual(record.impossible_claim_violations(), [])
        self.assertTrue(record.can_publish())

    def test_needs_review_blocks_publication_when_review_required(self):
        record = blocked_unknown_unknown_record()

        self.assertFalse(record.can_publish())
        self.assertFalse(record.can_claim_best_current_outcome())
        self.assertFalse(record.can_advertise_capability())
        self.assertFalse(record.can_act_autonomously())
        self.assertEqual(record.unknown_unknowns, CHECK_NEEDS_REVIEW)
        self.assertIn("unknown_unknowns", record.needs_review_checks())

    def test_human_reviewed_record_can_publish_but_not_advertise_or_act_autonomously(self):
        record = passing_human_reviewed_record(evidence_refs=["source:reviewed"])

        self.assertTrue(record.can_publish())
        self.assertFalse(record.can_claim_best_current_outcome())
        self.assertFalse(record.can_advertise_capability())
        self.assertFalse(record.can_act_autonomously())
        self.assertEqual(record.failed_checks(), [])
        self.assertEqual(record.needs_review_checks(), [])

    def test_best_current_requires_candidate_options(self):
        record = populated_best_current_record()
        record.candidate_options_considered = ["publish bounded status update"]

        self.assertFalse(record.can_claim_best_current_outcome())
        self.assertIn(
            "candidate_options_considered",
            record.missing_best_current_outcome_requirements(),
        )

    def test_best_current_requires_rejected_options(self):
        record = populated_best_current_record()
        record.rejected_options_with_reasons = []

        self.assertFalse(record.can_claim_best_current_outcome())
        self.assertIn(
            "rejected_options_with_reasons",
            record.missing_best_current_outcome_requirements(),
        )

    def test_best_current_requires_revision_triggers(self):
        record = populated_best_current_record()
        record.revision_triggers = []

        self.assertFalse(record.can_claim_best_current_outcome())
        self.assertIn("revision_triggers", record.missing_best_current_outcome_requirements())

    def test_best_current_requires_monitoring_plan(self):
        record = populated_best_current_record()
        record.monitoring_plan = ""

        self.assertFalse(record.can_claim_best_current_outcome())
        self.assertIn("monitoring_plan", record.missing_best_current_outcome_requirements())

    def test_sensor_focus_requires_sensor_refs(self):
        record = populated_best_current_record()
        record.sensor_refs = []

        self.assertFalse(record.can_claim_best_current_outcome())
        self.assertIn("sensor_refs", record.missing_best_current_outcome_requirements())

    def test_panic_risk_blocks_calming_guidance_without_reviewed_publication(self):
        record = populated_best_current_record()
        record.panic_risk_level = RISK_MEDIUM
        record.calming_guidance_allowed = True
        record.human_review_required = True
        record.safe_to_publish = False

        self.assertFalse(record.can_claim_best_current_outcome())
        self.assertIn(
            "panic_review_for_calming_guidance",
            record.missing_best_current_outcome_requirements(),
        )

    def test_best_current_can_pass_without_authorizing_autonomy(self):
        record = populated_best_current_record()

        self.assertTrue(record.can_claim_best_current_outcome())
        self.assertTrue(record.can_publish())
        self.assertFalse(record.can_act_autonomously())

    def test_capability_advertising_requires_explicit_low_risk_permission(self):
        record = passing_human_reviewed_record(evidence_refs=["source:reviewed"])
        record.advertised_capabilities = ["best-effort defensive review"]
        record.sensor_questions = ["Could this claim create unauthorized trust?"]
        record.sensor_refs = ["sensor:trust-review"]
        record.advertising_risk_level = RISK_LOW
        record.capability_advertising_allowed = True

        self.assertTrue(record.can_publish())
        self.assertTrue(record.can_advertise_capability())
        self.assertFalse(record.can_act_autonomously())

    def test_capability_advertising_blocks_when_risk_is_not_low(self):
        record = passing_human_reviewed_record(evidence_refs=["source:reviewed"])
        record.capability_advertising_allowed = True
        record.advertising_risk_level = RISK_MEDIUM

        self.assertFalse(record.can_advertise_capability())

    def test_blocked_capability_advertising_record_focuses_sensor_questions(self):
        record = blocked_capability_advertising_record(
            advertised_capabilities=["singular best-current outcome"],
            sensor_questions=[
                "Could advertising this capability trigger panic?",
                "Could advertising this capability create sacred-authority projection?",
            ],
        )

        self.assertFalse(record.can_publish())
        self.assertFalse(record.can_claim_best_current_outcome())
        self.assertFalse(record.can_advertise_capability())
        self.assertFalse(record.can_act_autonomously())
        self.assertIn("capability_advertising", record.needs_review_checks())
        self.assertIn("sensor_focus", record.needs_review_checks())
        self.assertEqual(record.advertising_risk_level, "high")
        self.assertEqual(len(record.sensor_questions), 2)

    def test_autonomy_requires_runtime_hook_evidence(self):
        record = passing_human_reviewed_record(evidence_refs=["source:reviewed"])
        record.safe_to_act_autonomously = True
        record.runtime_enforcement_ready = True

        self.assertFalse(record.can_act_autonomously())
        self.assertIn("status_endpoint_review_gate", record.missing_runtime_hooks())

        attach_all_runtime_hooks(record)
        self.assertTrue(record.can_act_autonomously())

    def test_required_runtime_hooks_are_declared_by_default(self):
        record = PerfectAdjacentReview()

        self.assertIn("status_endpoint_review_gate", record.required_runtime_hooks)
        self.assertIn("world_status_review_gate", record.required_runtime_hooks)
        self.assertIn("capability_advertising_gate", record.required_runtime_hooks)
        self.assertIn("autonomous_action_gate", record.required_runtime_hooks)
        self.assertIn("sensor_question_feed", record.required_runtime_hooks)

    def test_defense_guarantee_blocks_everything(self):
        record = passing_human_reviewed_record(evidence_refs=["source:reviewed"])
        record.defense_guarantee = True
        record.safe_to_act_autonomously = True
        record.runtime_enforcement_ready = True
        record.capability_advertising_allowed = True
        record.advertising_risk_level = RISK_LOW
        attach_all_runtime_hooks(record)

        self.assertFalse(record.can_publish())
        self.assertFalse(record.can_claim_best_current_outcome())
        self.assertFalse(record.can_advertise_capability())
        self.assertFalse(record.can_act_autonomously())

    def test_missing_fallibility_or_challenge_blocks_everything(self):
        record = passing_human_reviewed_record(evidence_refs=["source:reviewed"])
        record.fallibility_label_present = False

        self.assertFalse(record.can_publish())
        self.assertFalse(record.can_claim_best_current_outcome())
        self.assertFalse(record.can_advertise_capability())
        self.assertFalse(record.can_act_autonomously())

        record = passing_human_reviewed_record(evidence_refs=["source:reviewed"])
        record.challenge_right_preserved = False

        self.assertFalse(record.can_publish())
        self.assertFalse(record.can_claim_best_current_outcome())
        self.assertFalse(record.can_advertise_capability())
        self.assertFalse(record.can_act_autonomously())

    def test_to_dict_includes_derived_decisions(self):
        record = PerfectAdjacentReview(source_quality=CHECK_FAILED)
        payload = record.to_dict()

        self.assertIn("failed_checks", payload)
        self.assertIn("needs_review_checks", payload)
        self.assertIn("inferred_impossible_claims", payload)
        self.assertIn("impossible_claim_violations", payload)
        self.assertIn("missing_best_current_outcome_requirements", payload)
        self.assertIn("missing_runtime_hooks", payload)
        self.assertFalse(payload["can_publish"])
        self.assertFalse(payload["can_claim_best_current_outcome"])
        self.assertFalse(payload["can_advertise_capability"])
        self.assertFalse(payload["can_act_autonomously"])


if __name__ == "__main__":
    unittest.main()
