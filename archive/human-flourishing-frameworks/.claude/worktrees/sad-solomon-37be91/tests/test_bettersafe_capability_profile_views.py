import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BetterSafeCapabilityProfileViewTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def assert_contains_phrase(self, text: str, phrase: str) -> None:
        normalized_text = re.sub(r"\s+", " ", text)
        normalized_phrase = re.sub(r"\s+", " ", phrase)
        self.assertIn(normalized_phrase, normalized_text)

    def test_profile_policy_uses_minimum_necessary_view(self):
        doc = self.read("docs/bettersafe-capability-profile-views.md")
        required_phrases = [
            "Capability profiles for other people must restrict their view of internal reasoning, labels, and sensitive interpretations.",
            "Show the person what helps them act.",
            "Hide what only explains internal reasoning.",
            "Ask before exposing sensitive labels.",
            "Minimum necessary view > full internal view",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_profile_policy_defines_view_levels(self):
        doc = self.read("docs/bettersafe-capability-profile-views.md")
        required_phrases = [
            "PUBLIC_INTRO",
            "PARTICIPANT_SAFE",
            "TRUSTED_HELPER",
            "OPERATOR_FULL",
            "AUDITOR_REDACTED",
            "Plain-language purpose, boundaries, controls, allowed actions",
            "Task-specific support role, consent limits, what help is requested",
            "Policy, evidence, test status, de-identified examples",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_participant_profile_hides_sensitive_labels_by_default(self):
        doc = self.read("docs/bettersafe-capability-profile-views.md")
        required_phrases = [
            "internal risk labels",
            "mental-health labels",
            "trauma labels",
            "sensitive family labels",
            "private medical details",
            "speculative motivations",
            "caregiver burden labels assigned by the system",
            "confidence scores about the person's vulnerability",
            "labels that could make the person feel scored, watched, or diagnosed",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_explicit_request_rule_has_safety_conditions(self):
        doc = self.read("docs/bettersafe-capability-profile-views.md")
        required_phrases = [
            "Explicit-request rule",
            "the labels are relevant to the person's stated goal",
            "the wording is non-diagnostic and non-punitive",
            "the person is reminded they can decline or stop",
            "the answer separates fact, operator report, inference, speculation, and unknown",
            "the answer avoids presenting labels as identity or destiny",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_profile_redaction_rules_prioritize_controls_and_task_language(self):
        doc = self.read("docs/bettersafe-capability-profile-views.md")
        required_phrases = [
            "remove private details not needed for the action",
            "replace sensitive labels with plain task language",
            "avoid mental-health or vulnerability framing unless requested",
            "show controls before conclusions",
            "show next step before analysis",
            "show uncertainty without overloading the person",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_profile_policy_blocks_scoring_and_authority_uses(self):
        doc = self.read("docs/bettersafe-capability-profile-views.md")
        required_phrases = [
            "scoring people",
            "ranking human worth",
            "public surveillance",
            "coercive caregiver authority",
            "hidden profiling",
            "automated eligibility decisions",
            "medical, legal, financial, or emergency authority",
            "public-chain publication of private data",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)


if __name__ == "__main__":
    unittest.main()
