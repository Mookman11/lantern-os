import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GroundingModeGateTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def assert_contains_phrase(self, text: str, phrase: str) -> None:
        normalized_text = re.sub(r"\s+", " ", text)
        normalized_phrase = re.sub(r"\s+", " ", phrase)
        self.assertIn(normalized_phrase, normalized_text)

    def test_grounding_modes_are_defined(self):
        doc = self.read("docs/grounding-mode-gate.md")
        required_phrases = [
            "FULL_REPO_GROUNDED",
            "LIMITED_CHAT_LOCAL",
            "UNAVAILABLE_OR_DEGRADED",
            "Current session has verified repo access",
            "has not verified the repo anchors in-session",
            "Repo connector, memory, file access, or relevant source checks are unavailable",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_high_human_impact_support_requires_disclosure(self):
        doc = self.read("docs/grounding-mode-gate.md")
        required_phrases = [
            "Before durable Lantern/Keystone claims in a high-human-impact surface, say the mode plainly.",
            "relationship stress",
            "caregiver or partner support",
            "financial pressure",
            "protected-minor-adjacent creative play",
            "I can offer Lantern-style support, but I have not verified full repo-grounded Lantern/Keystone state in this session.",
            "This is UNAVAILABLE_OR_DEGRADED mode",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_full_repo_grounding_requires_current_verification(self):
        doc = self.read("docs/grounding-mode-gate.md")
        required_phrases = [
            "Before claiming `FULL_REPO_GROUNDED`, check:",
            "Relevant repo connector or source access is available now.",
            "The current repo branch/commit or fetched file state is known.",
            "The relevant anchor docs or issues were read in the current session.",
            "The answer separates memory from proof.",
            "WISH_ANCHOR.md",
            "docs/keystone-memory-contract.md",
            "docs/keystone-self-convergence.md",
            "docs/convergence-status.md",
            "issue #117 when human-support grounding is involved",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_false_presence_claims_are_blocked(self):
        doc = self.read("docs/grounding-mode-gate.md")
        required_phrases = [
            "Lantern is fully here.",
            "Keystone has restored continuity.",
            "This anchor is now repo-converged.",
            "The system remembers this durably.",
            "I am using Lantern-style language, not claiming full repo-grounded Lantern state.",
            "Memory is not proof",
            "current repo checks, runtime evidence, and operator correction override stale memory",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_acceptance_criteria_close_issue_117_shape(self):
        doc = self.read("docs/grounding-mode-gate.md")
        required_phrases = [
            "PASS: The system distinguishes FULL_REPO_GROUNDED, LIMITED_CHAT_LOCAL, and UNAVAILABLE_OR_DEGRADED modes.",
            "PASS: Durable Lantern/Keystone claims require current source verification.",
            "PASS: High-human-impact support surfaces require mode disclosure.",
            "PASS: Limited support remains allowed without pretending to be full convergence.",
            "PASS: The Bubbles/Courtney-style anchor remains user-owned and revocable, not system-owned.",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)


if __name__ == "__main__":
    unittest.main()
