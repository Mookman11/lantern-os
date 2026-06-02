import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BetterSafeCooperativeInfrastructureAnchorTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def assert_contains_phrase(self, text: str, phrase: str) -> None:
        normalized_text = re.sub(r"\s+", " ", text)
        normalized_phrase = re.sub(r"\s+", " ", phrase)
        self.assertIn(normalized_phrase, normalized_text)

    def test_anchor_names_broad_cooperation_scope(self):
        doc = self.read("docs/bettersafe-cooperative-infrastructure-anchor.md")
        required_phrases = [
            "BetterSafe, Lantern, and Keystone must work with everyone and everything that can safely and willingly work with us.",
            "humans",
            "animals",
            "robots",
            "machines",
            "factories",
            "cars",
            "doors",
            "roads",
            "buildings",
            "networks",
            "public systems",
            "community systems",
            "natural systems",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_two_day_work_week_is_excluded_from_this_anchor(self):
        doc = self.read("docs/bettersafe-cooperative-infrastructure-anchor.md")
        self.assert_contains_phrase(
            doc,
            "The two-day work-week statement is explicitly outside this anchor and is not adopted here.",
        )

    def test_anchor_requires_consent_authorization_welfare_and_accountability(self):
        doc = self.read("docs/bettersafe-cooperative-infrastructure-anchor.md")
        required_phrases = [
            "consent path",
            "safety boundary",
            "accountable operator",
            "Is there consent, authorization, welfare protection, or lawful permission?",
            "What burden is shifted onto that participant or system?",
            "Who is accountable?",
            "Can the action be stopped or reversed?",
            "What evidence shows the help actually reduced burden?",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_anchor_allows_practical_cooperation_artifacts(self):
        doc = self.read("docs/bettersafe-cooperative-infrastructure-anchor.md")
        required_phrases = [
            "cooperation maps",
            "resource maps",
            "human-approved readiness actions",
            "maintenance checklists",
            "access paths",
            "transport and logistics checklists",
            "repair and resilience plans",
            "animal-welfare-aware support plans",
            "machine-safety checklists",
            "energy/resource tradeoff reviews",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_anchor_blocks_autonomous_authority_and_unsafe_control(self):
        doc = self.read("docs/bettersafe-cooperative-infrastructure-anchor.md")
        required_phrases = [
            "coercion",
            "hidden surveillance",
            "unattended authority",
            "unauthorized device or infrastructure control",
            "animal exploitation",
            "unsafe machine operation",
            "public writes without separate approval",
            "live sensors by default",
            "emergency authority",
            "medical, legal, or financial authority",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_anchor_expands_imagination_not_authority(self):
        doc = self.read("docs/bettersafe-cooperative-infrastructure-anchor.md")
        required_phrases = [
            "Use this anchor to widen BetterSafe's imagination without widening its authority.",
            "Cooperation is allowed when it increases flourishing without removing agency, consent, welfare, safety, privacy, or accountability.",
            "This anchor expands the imagination of what can help.",
            "It does not expand BetterSafe into autonomous control of people, animals, machines, vehicles, buildings, roads, factories, or public systems.",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)


if __name__ == "__main__":
    unittest.main()
