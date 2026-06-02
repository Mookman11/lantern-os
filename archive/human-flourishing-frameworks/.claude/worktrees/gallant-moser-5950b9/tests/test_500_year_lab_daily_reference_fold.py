#!/usr/bin/env python3
"""Guardrails for the compact 500-year lab daily reference fold."""

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "500-year-lab-daily-reference-fold.md"


class FiveHundredYearLabDailyReferenceFoldTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = DOC.read_text(encoding="utf-8")
        cls.lower = cls.text.lower()
        cls.flat = " ".join(cls.lower.split())

    def assert_phrase(self, phrase: str) -> None:
        self.assertIn(" ".join(phrase.lower().split()), self.flat)

    def test_fold_exists_and_links_source_stack(self):
        self.assertTrue(DOC.exists())
        for phrase in [
            "docs/time-convergence-spine.md",
            "docs/500-year-lab-treatments.md",
            "docs/500-year-lab-dna-code-future-tech.md",
            "docs/imaginative-lore-100-negative-outcomes-convergence-2026-05-09.md",
            "docs/imaginative-lore-100b-convergence-2026-05-09.md",
            "docs/context-storage-upgrade-plan.md",
            "docs/anchor-taxonomy.md",
        ]:
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_daily_reference_packet_shape_is_present(self):
        for phrase in [
            "daily reference packet",
            "today's floor:",
            "500-year horizon:",
            "current medicine lane:",
            "dna-code / future-tech lane:",
            "lore / novel signal:",
            "source class:",
            "one safe action:",
            "falsifier:",
            "return phrase:",
        ]:
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_compression_keeps_current_care_future_tech_and_lore_separate(self):
        for phrase in [
            "use the strongest current evidence first",
            "keep dna-code and future-tech items in clinician, trial, ethics, and law lanes",
            "treat novels, films, games, and myths as archetype generators and negative tests",
            "not operational proof",
            "preserve no spoilers by default",
            "store the smallest useful packet",
            "do not store raw transcripts or private family details",
        ]:
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_source_classes_block_lore_and_future_tech_overclaim(self):
        for phrase in [
            "current clinical guideline / approved care",
            "regulated trial / peer-reviewed early science",
            "roadmap / vendor / institutional future claim",
            "operator wish / design hypothesis",
            "lore / novel / cultural archetype",
            "must not do",
            "become self-experiment protocol",
            "prove real-world doors, survival, timelines, or authority",
        ]:
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_restore_phrase_and_non_goals_are_bounded(self):
        for phrase in [
            "500-year daily fold",
            "start with today's floor",
            "preserve no spoilers by default",
            "choose one safe action before adding more doctrine",
            "does not authorize medical advice",
            "self-experimentation",
            "diy biology",
            "protected-person data collection",
            "treating fiction as evidence",
        ]:
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)


if __name__ == "__main__":
    unittest.main()
