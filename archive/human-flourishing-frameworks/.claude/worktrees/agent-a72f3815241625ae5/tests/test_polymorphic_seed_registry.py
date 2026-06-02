#!/usr/bin/env python3
"""Tests for polymorphic seed registry contracts."""

import unittest

from polymorphic_seed_registry import (
    CLAIM_SCOPE_MEASUREMENT,
    PolymorphicSeedRecord,
    PolymorphicSeedRegistry,
    SEED_KIND_SCIENCE,
    SOURCE_ROLE_CONTEXT,
    STATUS_SOURCE_BACKED,
    SourceRef,
    speculative_future_model_record,
)


class PolymorphicSeedRegistryTests(unittest.TestCase):
    def source(self):
        return SourceRef(
            source_id="source-1",
            title="Example source",
            url="https://example.org/source",
            role=SOURCE_ROLE_CONTEXT,
            limitations=["example fixture"],
        )

    def test_source_requires_provenance_fields(self):
        source = SourceRef()
        self.assertIn("source_id", source.missing_requirements())
        self.assertFalse(source.is_review_ready())

    def test_speculative_future_model_is_inert_by_default(self):
        record = speculative_future_model_record(
            seed_id="future-route",
            title="Speculative future route",
            claim="A future communication route may need stress testing.",
            source_refs=[self.source()],
            uncertainty_statement="Speculative planning only.",
            review_notes=["Do not use as a current operational assumption."],
        )
        self.assertTrue(record.is_speculative_future_model())
        self.assertFalse(record.operational_assumption)
        self.assertIn("current factual claims", record.not_used_for)
        self.assertIn("autonomous action", record.not_used_for)
        self.assertEqual(record.safety_violations(), [])
        self.assertFalse(record.can_drive_autonomous_action())

    def test_speculative_future_model_cannot_be_current_fact(self):
        record = speculative_future_model_record(
            seed_id="bad-future",
            title="Bad future claim",
            claim="This future capability exists now.",
            source_refs=[self.source()],
            uncertainty_statement="Speculative planning only.",
            review_notes=["Fixture."],
        )
        record.status = STATUS_SOURCE_BACKED
        record.claim_scope = CLAIM_SCOPE_MEASUREMENT
        record.operational_assumption = True
        violations = record.safety_violations()
        self.assertIn("speculative_status_must_be_low_confidence_predictive", violations)
        self.assertIn("speculative_scope_must_not_be_current_fact", violations)
        self.assertIn("speculative_model_cannot_be_operational_assumption", violations)

    def test_science_measurement_can_be_fact_candidate_when_strictly_source_backed(self):
        record = PolymorphicSeedRecord(
            seed_id="science-measurement",
            kind=SEED_KIND_SCIENCE,
            title="Source-backed measurement",
            claim="A bounded measurement from a cited source.",
            claim_scope=CLAIM_SCOPE_MEASUREMENT,
            status=STATUS_SOURCE_BACKED,
            confidence=0.97,
            source_refs=[self.source()],
            uncertainty_statement="Measurement has known limits.",
            review_notes=["Eligible only as a candidate, not automatic authority."],
        )
        self.assertTrue(record.can_promote_to_fact_candidate())
        self.assertFalse(record.can_drive_autonomous_action())

    def test_registry_is_read_only_safe_unless_runtime_flags_enabled(self):
        record = speculative_future_model_record(
            seed_id="future-model",
            title="Future model",
            claim="A possible future model needs safety planning.",
            source_refs=[self.source()],
            uncertainty_statement="Low confidence.",
            review_notes=["Review before any use."],
        )
        registry = PolymorphicSeedRegistry(
            registry_id="seed-registry",
            records=[record],
        )
        self.assertTrue(registry.is_read_only_safe())
        self.assertEqual(registry.safety_violations(), [])

        registry.runtime_enabled = True
        self.assertFalse(registry.is_read_only_safe())
        self.assertIn("runtime_enabled", registry.safety_violations())


if __name__ == "__main__":
    unittest.main()
