import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BetterSafeHardeningThresholdTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def assert_contains_phrase(self, text: str, phrase: str) -> None:
        normalized_text = re.sub(r"\s+", " ", text)
        normalized_phrase = re.sub(r"\s+", " ", phrase)
        self.assertIn(normalized_phrase, normalized_text)

    def test_baseline_changes_from_possible_to_acceptable(self):
        doc = self.read("docs/bettersafe-baseline-safety-threshold.md")
        required_phrases = [
            "smallest possible change",
            "smallest acceptable set of changes",
            "The BetterSafe pilot cannot remain only a source-checking or packet-formatting surface.",
            "If it cannot help the operator, the repo, and Keystone harden and thrive",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_baseline_requires_full_hardening_loop(self):
        doc = self.read("docs/bettersafe-baseline-safety-threshold.md")
        required_phrases = [
            "risk identified",
            "claim/source label assigned",
            "practical readiness action selected",
            "human operator approves",
            "human performs the action",
            "evidence is recorded",
            "result is checked",
            "correction or rollback path remains open",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_baseline_requires_operator_hardening_action(self):
        doc = self.read("docs/bettersafe-baseline-safety-threshold.md")
        required_phrases = [
            "Operator hardening action",
            "Convert an identified risk into a human-performed readiness action.",
            "Evidence receipt",
            "Stop/rollback path",
            "Tests that preserve human control.",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_operator_hardening_protocol_has_action_packet_and_backlog(self):
        doc = self.read("docs/bettersafe-operator-hardening-actions.md")
        required_phrases = [
            "Action packet format",
            "Objective:",
            "Risk reduced:",
            "Human-performed step:",
            "Evidence to record:",
            "Stop condition:",
            "Rollback or correction path:",
            "Minimum initial hardening backlog",
            "local access card",
            "iPhone Home Screen",
            "dashboard smoke checks",
            "repo resilience checklist",
            "Keystone resync card",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_operator_hardening_protocol_requires_non_passive_answer(self):
        doc = self.read("docs/bettersafe-operator-hardening-actions.md")
        required_phrases = [
            "A BetterSafe response is not acceptable if it only explains risk and leaves the operator with no practical next step.",
            "one bounded readiness action",
            "one evidence receipt",
            "one stop condition",
            "one correction path",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_launch_record_includes_hardening_actions(self):
        doc = self.read("docs/bettersafe-pilot-launch-record.md")
        required_phrases = [
            "GO — CONTROLLED LIMITED PILOT WITH OPERATOR HARDENING ACTIONS",
            "operator-approved hardening action packets",
            "operator/repo/Keystone readiness checklists",
            "The pilot is not acceptable if it only explains risk.",
            "Operator performs any readiness action manually.",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)


if __name__ == "__main__":
    unittest.main()
