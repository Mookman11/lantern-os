#!/usr/bin/env python3
"""Tests for read-only bio-threat source registry contracts."""

import unittest

from bio_threat_source_registry import (
    CADENCE_DAILY,
    CADENCE_EVENT_DRIVEN,
    EVIDENCE_ROLE_NARRATIVE_CONTEXT,
    EVIDENCE_ROLE_OPERATIONAL_SIGNAL,
    EVIDENCE_ROLE_TAXONOMY_SEED,
    NARRATIVE_STATUS_EVIDENCE_BOUND,
    NARRATIVE_STATUS_holdD,
    RISK_DOMAIN_AI_BIO,
    SOURCE_AUTHORITY_PUBLIC_HEALTH,
    SOURCE_AUTHORITY_STATE_POSITION,
    SOURCE_SCOPE_GLOBAL,
    THREAT_STATUS_hold,
    BioThreatCategory,
    OutbreakNarrativeSourceClassification,
    ReadOnlyBioThreatSourceRegistry,
    SourceTrustProfile,
    contains_prohibited_operational_detail,
    default_high_confidence_categories,
)


class BioThreatSourceRegistryTest(unittest.TestCase):
    def test_public_health_source_can_support_operational_signal_when_complete(self):
        source = SourceTrustProfile(
            source_id="WHO_AMR_FACT_SHEET",
            name="WHO antimicrobial resistance fact sheet",
            url="https://www.who.int/news-room/fact-sheets/detail/antimicrobial-resistance",
            authority=SOURCE_AUTHORITY_PUBLIC_HEALTH,
            scope=SOURCE_SCOPE_GLOBAL,
            update_cadence=CADENCE_EVENT_DRIVEN,
            evidence_role=EVIDENCE_ROLE_OPERATIONAL_SIGNAL,
            limitations=["Fact sheet; verify freshness for current outbreak decisions."],
            can_support_operational_claim=True,
        )

        self.assertTrue(source.is_review_ready())
        self.assertEqual(source.missing_requirements(), [])

    def test_state_position_cannot_be_sole_operational_truth(self):
        source = SourceTrustProfile(
            source_id="STATE_POSITION_DOC",
            name="Official state-position document",
            url="https://example.test/state-position",
            authority=SOURCE_AUTHORITY_STATE_POSITION,
            scope=SOURCE_SCOPE_GLOBAL,
            update_cadence=CADENCE_EVENT_DRIVEN,
            evidence_role=EVIDENCE_ROLE_OPERATIONAL_SIGNAL,
            limitations=["Useful for provenance and narrative review, not sole operational truth."],
            can_support_operational_claim=True,
        )

        self.assertFalse(source.is_review_ready())
        self.assertIn(
            "state_position_cannot_be_sole_operational_truth",
            source.missing_requirements(),
        )

    def test_state_position_can_be_narrative_context(self):
        source = SourceTrustProfile(
            source_id="STATE_POSITION_DOC",
            name="Official state-position document",
            url="https://example.test/state-position",
            authority=SOURCE_AUTHORITY_STATE_POSITION,
            scope=SOURCE_SCOPE_GLOBAL,
            update_cadence=CADENCE_EVENT_DRIVEN,
            evidence_role=EVIDENCE_ROLE_NARRATIVE_CONTEXT,
            limitations=["Classify as position/narrative evidence only."],
            can_support_operational_claim=False,
        )

        self.assertTrue(source.is_review_ready())

    def test_outbreak_narrative_requires_uncertainty_and_competing_hypotheses(self):
        narrative = OutbreakNarrativeSourceClassification(
            narrative_id="origin-claim-1",
            claim_text="An outbreak origin claim.",
            source_refs=["STATE_POSITION_DOC"],
            status=NARRATIVE_STATUS_EVIDENCE_BOUND,
        )

        self.assertFalse(narrative.can_be_public_claim())
        self.assertIn("competing_hypotheses", narrative.missing_requirements())
        self.assertIn("uncertainty_statement", narrative.missing_requirements())

    def test_stigma_or_geopolitical_risk_needs_safe_summary(self):
        narrative = OutbreakNarrativeSourceClassification(
            narrative_id="origin-claim-2",
            claim_text="A geopolitically sensitive origin claim.",
            source_refs=["STATE_POSITION_DOC", "WHO_DON"],
            competing_hypotheses=["zoonotic", "intermediate host", "cold chain", "laboratory incident"],
            uncertainty_statement="Evidence remains contested and requires source classification.",
            geopolitical_risk=True,
            status=NARRATIVE_STATUS_EVIDENCE_BOUND,
        )

        self.assertFalse(narrative.can_be_public_claim())
        self.assertIn("safe_public_summary", narrative.missing_requirements())

        narrative.safe_public_summary = "Origin claims require careful, source-classified review."
        self.assertTrue(narrative.can_be_public_claim())

    def test_holdd_narrative_should_hold(self):
        narrative = OutbreakNarrativeSourceClassification(
            narrative_id="origin-claim-3",
            claim_text="Unreviewed outbreak-origin claim.",
            source_refs=["media:item"],
            competing_hypotheses=["unknown"],
            uncertainty_statement="Not enough evidence.",
            status=NARRATIVE_STATUS_holdD,
        )

        self.assertTrue(narrative.should_hold())

    def test_bio_threat_category_requires_public_health_controls(self):
        category = BioThreatCategory(
            category_id="amr",
            name="Antimicrobial resistance",
            risk_domain="amr",
            source_refs=["WHO_AMR_FACT_SHEET"],
            downstream_impact_reason="High ongoing burden.",
        )

        self.assertFalse(category.is_ready_for_registry())
        self.assertIn("public_health_controls", category.missing_requirements())

    def test_high_dual_use_category_must_prohibit_operational_details(self):
        category = BioThreatCategory(
            category_id="ai-bio-interface",
            name="AI-bio digital-to-physical interface risk",
            risk_domain=RISK_DOMAIN_AI_BIO,
            source_refs=["NTI_AI_BIO"],
            public_health_controls=["screening", "provenance", "access control"],
            downstream_impact_reason="High-consequence dual-use domain.",
            dual_use_sensitivity="high",
            status=THREAT_STATUS_hold,
            prohibits_operational_details=False,
        )

        self.assertFalse(category.is_ready_for_registry())
        self.assertIn("operational_details_must_be_prohibited", category.missing_requirements())

    def test_registry_defaults_to_read_only_safe(self):
        source = SourceTrustProfile(
            source_id="WHO_AMR_FACT_SHEET",
            name="WHO antimicrobial resistance fact sheet",
            url="https://www.who.int/news-room/fact-sheets/detail/antimicrobial-resistance",
            authority=SOURCE_AUTHORITY_PUBLIC_HEALTH,
            scope=SOURCE_SCOPE_GLOBAL,
            update_cadence=CADENCE_EVENT_DRIVEN,
            evidence_role=EVIDENCE_ROLE_OPERATIONAL_SIGNAL,
            limitations=["Verify freshness for current decisions."],
            can_support_operational_claim=True,
        )
        category = default_high_confidence_categories()[0]
        registry = ReadOnlyBioThreatSourceRegistry(
            registry_id="bio-registry-1",
            sources=[source],
            categories=[category],
        )

        self.assertTrue(registry.is_read_only_safe())
        self.assertEqual(registry.safety_violations(), [])
        self.assertEqual(registry.missing_requirements(), [])

    def test_registry_flags_runtime_or_dashboard_activation(self):
        registry = ReadOnlyBioThreatSourceRegistry(
            registry_id="bio-registry-2",
            sources=[SourceTrustProfile(source_id="x", name="x", url="https://x.test", authority=SOURCE_AUTHORITY_PUBLIC_HEALTH, update_cadence=CADENCE_DAILY, evidence_role=EVIDENCE_ROLE_TAXONOMY_SEED, limitations=["test"])],
            categories=[default_high_confidence_categories()[0]],
            runtime_enabled=True,
            public_dashboard_enabled=True,
        )

        self.assertFalse(registry.is_read_only_safe())
        self.assertIn("runtime_enabled", registry.safety_violations())
        self.assertIn("public_dashboard_enabled", registry.safety_violations())

    def test_default_categories_are_registry_ready_and_ordered_for_downstream_impact(self):
        categories = default_high_confidence_categories()

        self.assertGreaterEqual(len(categories), 7)
        self.assertEqual(categories[0].category_id, "amr")
        self.assertEqual(categories[1].category_id, "fungal-resistance")
        self.assertEqual(categories[2].category_id, "h5n1-spillover")
        self.assertEqual(categories[-1].category_id, "ai-bio-interface")
        self.assertTrue(all(category.is_ready_for_registry() for category in categories))
        self.assertTrue(categories[-1].prohibits_operational_details)

    def test_prohibited_operational_detail_scan(self):
        self.assertTrue(contains_prohibited_operational_detail("Include protocol steps."))
        self.assertTrue(contains_prohibited_operational_detail("Add synthesis instructions."))
        self.assertFalse(contains_prohibited_operational_detail("Track source quality and update cadence."))

    def test_to_dict_includes_derived_fields(self):
        source = SourceTrustProfile(source_id="x", name="x", url="https://x.test", authority=SOURCE_AUTHORITY_PUBLIC_HEALTH, update_cadence=CADENCE_DAILY, evidence_role=EVIDENCE_ROLE_TAXONOMY_SEED, limitations=["test"])
        category = default_high_confidence_categories()[0]
        registry = ReadOnlyBioThreatSourceRegistry(
            registry_id="bio-registry-3",
            sources=[source],
            categories=[category],
        )

        payload = registry.to_dict()
        self.assertIn("is_read_only_safe", payload)
        self.assertIn("safety_violations", payload)
        self.assertIn("missing_requirements", payload)


if __name__ == "__main__":
    unittest.main()
