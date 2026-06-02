#!/usr/bin/env python3
"""Tests for complete sensor profile baseline records."""

import unittest

from perfect_adjacent_review import (
    CHECK_NEEDS_REVIEW,
    CHECK_PASSED,
    RISK_HIGH,
    RISK_LOW,
    SOURCE_KIND_EMPIRICAL,
    SOURCE_QUALITY_AUDITED,
)
from sensor_profile import (
    EVIDENCE_CLASS_MEASUREMENT,
    OBSERVATION_STATUS_PROPOSED,
    OBSERVATION_STATUS_REVIEWED,
    SENSOR_TYPE_API,
    SensorObservation,
    SensorPermission,
    SensorProfile,
    SensorProvenance,
    SensorRiskReview,
)


def complete_provenance() -> SensorProvenance:
    return SensorProvenance(
        source_ref="source:who-gho",
        observed_at="2026-05-08T00:00:00Z",
        ingested_at="2026-05-08T00:01:00Z",
        sensor_version="sensor-v1",
        output_hash="sha256:example",
    )


def low_risk_review() -> SensorRiskReview:
    return SensorRiskReview(
        privacy_risk=RISK_LOW,
        dual_use_risk=RISK_LOW,
        p_doom_relevance=CHECK_PASSED,
        security_relevance=CHECK_PASSED,
        spoofing_risk=RISK_LOW,
        tamper_risk=RISK_LOW,
        calibration_status=CHECK_PASSED,
        evidence_refs=["review:calibration"],
    )


class SensorProfileTest(unittest.TestCase):
    def test_sensor_permission_defaults_do_not_grant_runtime_effects(self):
        permission = SensorPermission()

        self.assertTrue(permission.is_conservative_default())
        self.assertFalse(permission.grants_runtime_effect())
        self.assertFalse(permission.can_update_seed)
        self.assertFalse(permission.can_update_world_model)
        self.assertFalse(permission.can_trigger_public_output)
        self.assertFalse(permission.can_trigger_autonomy)

    def test_sensor_profile_defaults_are_incomplete_and_inert(self):
        profile = SensorProfile()

        self.assertFalse(profile.is_profile_complete())
        self.assertFalse(profile.can_have_runtime_effect())
        self.assertIn("sensor_id", profile.missing_profile_requirements())
        self.assertEqual(profile.risk_review.privacy_risk, RISK_HIGH)
        self.assertEqual(profile.risk_review.calibration_status, CHECK_NEEDS_REVIEW)

    def test_sensor_profile_complete_does_not_imply_runtime_effect(self):
        profile = SensorProfile(
            sensor_id="who-gho",
            sensor_name="WHO Global Health Observatory",
            sensor_type=SENSOR_TYPE_API,
            source_url_or_location="https://www.who.int/data/gho",
            domain="health",
            source_kind=SOURCE_KIND_EMPIRICAL,
            source_quality=SOURCE_QUALITY_AUDITED,
            evidence_class=EVIDENCE_CLASS_MEASUREMENT,
            provenance=complete_provenance(),
            risk_review=low_risk_review(),
        )

        self.assertTrue(profile.is_profile_complete())
        self.assertFalse(profile.can_have_runtime_effect())

    def test_sensor_profile_requires_low_risk_review_for_runtime_effect(self):
        profile = SensorProfile(
            sensor_id="runtime-status",
            sensor_name="Runtime status endpoint",
            sensor_type=SENSOR_TYPE_API,
            source_url_or_location="https://example.invalid/api/status",
            domain="runtime",
            source_kind=SOURCE_KIND_EMPIRICAL,
            source_quality=SOURCE_QUALITY_AUDITED,
            evidence_class=EVIDENCE_CLASS_MEASUREMENT,
            provenance=complete_provenance(),
            permission=SensorPermission(can_update_world_model=True),
        )

        self.assertFalse(profile.can_have_runtime_effect())

        profile.risk_review = low_risk_review()
        self.assertTrue(profile.can_have_runtime_effect())

    def test_sensor_observation_defaults_to_proposed_and_not_accepted(self):
        observation = SensorObservation()

        self.assertEqual(observation.status, OBSERVATION_STATUS_PROPOSED)
        self.assertFalse(observation.can_be_accepted())
        self.assertIn("observation_id", observation.missing_observation_requirements())

    def test_sensor_observation_requires_review_and_provenance_to_accept(self):
        observation = SensorObservation(
            observation_id="obs-1",
            sensor_id="who-gho",
            claim_text="Example bounded health measurement.",
            observed_value="42",
            evidence_class=EVIDENCE_CLASS_MEASUREMENT,
            status=OBSERVATION_STATUS_REVIEWED,
            source_refs=["source:who-gho"],
            provenance=complete_provenance(),
        )

        self.assertEqual(observation.missing_observation_requirements(), [])
        self.assertTrue(observation.can_be_accepted())

    def test_to_dict_includes_derived_sensor_fields(self):
        profile = SensorProfile()
        payload = profile.to_dict()

        self.assertIn("missing_profile_requirements", payload)
        self.assertIn("is_profile_complete", payload)
        self.assertIn("can_have_runtime_effect", payload)
        self.assertFalse(payload["can_have_runtime_effect"])

        observation = SensorObservation()
        payload = observation.to_dict()

        self.assertIn("missing_observation_requirements", payload)
        self.assertIn("can_be_accepted", payload)
        self.assertFalse(payload["can_be_accepted"])


if __name__ == "__main__":
    unittest.main()
