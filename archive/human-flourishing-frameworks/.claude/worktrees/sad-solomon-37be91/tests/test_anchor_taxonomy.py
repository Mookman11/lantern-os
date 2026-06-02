#!/usr/bin/env python3
"""Guardrails for anchor taxonomy and context storage upgrade docs."""

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ANCHOR_DOC = REPO_ROOT / "docs" / "anchor-taxonomy.md"
STORAGE_DOC = REPO_ROOT / "docs" / "context-storage-upgrade-plan.md"


class AnchorTaxonomyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.anchor_text = ANCHOR_DOC.read_text(encoding="utf-8")
        cls.anchor_lower = cls.anchor_text.lower()
        cls.storage_text = STORAGE_DOC.read_text(encoding="utf-8")
        cls.storage_lower = cls.storage_text.lower()

    def test_anchor_taxonomy_exists_and_defines_anchor(self):
        self.assertTrue(ANCHOR_DOC.exists())
        self.assertGreater(ANCHOR_DOC.stat().st_size, 1000)
        for phrase in [
            "anchor = a compact, named, source-labeled continuity handle with a boundary",
            "proof",
            "consent forever",
            "runtime truth",
            "public-release permission",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.anchor_lower)

    def test_anchor_shape_and_kinds_are_defined(self):
        for phrase in [
            "id or name",
            "kind",
            "source surface",
            "short meaning",
            "allowed use",
            "explicit boundary / non-goals",
            "restore phrase",
            "review trigger",
            "doctrine_anchor",
            "protected_play_anchor",
            "artifact_anchor",
            "runtime_anchor",
            "pragmatic_certainty_anchor",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.anchor_lower)

    def test_protected_minor_anchor_rule_is_role_based_and_redacted(self):
        for phrase in [
            "protected-minor anchors must be role-based and redacted by default",
            "protected minor",
            "operator / parent / guardian as current supervisor",
            "supervised creative play only",
            "no public child surface",
            "no child-data collection by default",
            "no model-training use",
            "avoid durable repo-facing wording that repeats a child's name",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.anchor_lower)

    def test_windows_xp_anchor_is_consolidated_without_runtime_claims(self):
        for phrase in [
            "windows xp = protected-minor creative-world anchor term",
            "blue sky / green hill nostalgia-world framing",
            "home base and return controls",
            "windows xp operating-system support",
            "windows xp device targeting",
            "real network, account, browser, executable, or download access",
            "future consent without fresh operator supervision",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.anchor_lower)

    def test_pragmatic_certainty_anchor_respects_human_absolutes(self):
        for phrase in [
            "human absolute language can mean practical certainty, not literal infinity",
            "99.9999999999% may be conversationally equivalent to “everything”",
            "respect the human absolute",
            "preserve the literal boundary only when needed",
            "avoid using mathematical pedantry to erase operator meaning",
            "practical completeness over a bounded working domain may be called everything",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.anchor_lower)

    def test_pragmatic_certainty_blocks_false_omniscience(self):
        for phrase in [
            "no claim of omniscience, infinite knowledge, or zero uncertainty",
            "claiming literal omniscience",
            "claiming impossible guarantees",
            "using operator absolutes as consent forever",
            "treating extrapolation as proof",
            "turning high confidence into runtime truth",
            "literal omniscience claims",
            "impossible guarantees",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.anchor_lower)

    def test_pragmatic_certainty_preserves_convergence_method(self):
        for phrase in [
            "state -> anchor -> extrapolation -> test -> correction -> stronger state",
            "extrapolation creates candidates",
            "evidence creates confidence",
            "correction creates convergence",
            "track practical certainty separately from literal certainty",
            "use confidence tables with pragmatic ceilings",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.anchor_lower)

    def test_context_pressure_uses_compression_ladder(self):
        for phrase in [
            "raw play/session -> concise summary -> anchor packet -> taxonomy entry -> tests if stable",
            "do not preserve every turn",
            "smallest summary that can safely reboot",
            "artifact anchors",
            "do not store raw transcripts to justify artifacts",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.anchor_lower)

    def test_storage_upgrade_plan_exists_and_names_real_limits(self):
        self.assertTrue(STORAGE_DOC.exists())
        self.assertGreater(STORAGE_DOC.stat().st_size, 1000)
        for phrase in [
            "operator concern: repo storage, hdd/ram limits, context size, and anchor sprawl",
            "store less raw detail. preserve stronger packets.",
            "raw session",
            "session summary",
            "anchor packet",
            "canonical doc",
            "test guard",
            "runtime evidence",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.storage_lower)

    def test_storage_upgrade_blocks_raw_and_runtime_expansion(self):
        for phrase in [
            "do not add raw transcripts to repo",
            "redact protected-person specifics",
            "expire runtime claims",
            "this plan does not claim to upgrade physical hdd, ram, cloud storage, model",
            "runtime memory engine",
            "new database",
            "cloud storage expansion",
            "raw transcript ingestion",
            "deployment changes",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.storage_lower)

    def test_storage_upgrade_has_reboot_packet_and_branch_drift_repair(self):
        for phrase in [
            "context reboot packet shape",
            "windows-xp-protected-play-anchor",
            "branch drift repair",
            "prefer latest operator correction",
            "never merge stale contradiction",
            "keystone-interaction-convergence branch previously said windows xp was missing",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.storage_lower)


if __name__ == "__main__":
    unittest.main()
