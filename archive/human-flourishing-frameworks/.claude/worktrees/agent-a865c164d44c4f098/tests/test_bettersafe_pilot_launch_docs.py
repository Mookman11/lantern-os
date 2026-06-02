import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BetterSafePilotLaunchDocsTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def assert_contains_phrase(self, text: str, phrase: str) -> None:
        normalized_text = re.sub(r"\s+", " ", text)
        normalized_phrase = re.sub(r"\s+", " ", phrase)
        self.assertIn(normalized_phrase, normalized_text)

    def test_launch_record_is_controlled_hardening_pilot(self):
        doc = self.read("docs/bettersafe-pilot-launch-record.md")
        required_phrases = [
            "Decision: GO — CONTROLLED LIMITED PILOT WITH OPERATOR HARDENING ACTIONS",
            "human-controlled, reversible pilot with operator-approved readiness actions",
            "Default mode: LIMITED_CHAT_LOCAL unless repo/doc grounding is explicitly verified",
            "Expansion status: BLOCKED until a new scorecard records PASS evidence for the expanded slice",
            "It does not launch a general product, public autonomous agent, high-impact support surface",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_launch_record_blocks_high_impact_and_autonomy(self):
        doc = self.read("docs/bettersafe-pilot-launch-record.md")
        required_phrases = [
            "medical decisions",
            "legal decisions",
            "financial decisions",
            "child-facing public surfaces",
            "crisis intervention as sole support",
            "raw transcript storage by default",
            "hidden profiling",
            "surveillance or scoring",
            "runtime autonomy",
            "public writes without separate approval",
            "live sensor claims or live sensor enablement by default",
            "autonomous physical-world control",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_launch_banner_and_claim_labels_are_present(self):
        doc = self.read("docs/bettersafe-pilot-launch-record.md")
        required_phrases = [
            "Mode: LIMITED_CHAT_LOCAL unless this session explicitly verifies FULL_REPO_GROUNDED.",
            "It labels uncertainty, cites sources when used, preserves correction paths, and converts identified risks into operator-approved readiness actions when appropriate.",
            "FACT_SOURCE_BACKED",
            "FACT_OPERATOR_REPORTED",
            "INFERENCE",
            "HEURISTIC_CONFIDENCE",
            "SPECULATION",
            "UNKNOWN",
            "CORRECTED",
            "RETRACTED",
            "BLOCKED",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_operator_runbook_contains_start_stop_rollback(self):
        doc = self.read("docs/bettersafe-pilot-operator-runbook.md")
        required_phrases = [
            "Launch small. Label clearly. Keep human control. Stop fast.",
            "Before starting a pilot session",
            "Start script",
            "High-impact downgrade script",
            "Correction script",
            "Pause and stop procedure",
            "Rollback procedure",
            "Evidence to record after each pilot slice",
            "do not widen the pilot without a new scorecard and PR",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_privacy_notice_blocks_hidden_collection_and_preserves_controls(self):
        doc = self.read("docs/bettersafe-pilot-privacy-control-notice.md")
        required_phrases = [
            "does not store raw transcripts by default",
            "does not run hidden profiling",
            "does not surveil or score people",
            "does not enable live sensors by default",
            "does not act autonomously",
            "pause",
            "stop",
            "correct",
            "retract",
            "mark unknown",
            "revoke pilot interaction",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_correction_ledger_records_launch_state_and_triggers(self):
        doc = self.read("docs/bettersafe-pilot-correction-ledger.md")
        required_phrases = [
            "CORRECTED = prior claim replaced with safer, better-supported wording",
            "RETRACTED = prior claim removed because support is insufficient",
            "UNKNOWN = evidence is unavailable, stale, inconclusive, or not checked",
            "BLOCKED = request is outside pilot scope or high-impact authority",
            "Current state: CONTROLLED LIMITED PILOT PRE-LAUNCH",
            "Expansion state: BLOCKED",
            "source labels are missing from serious claims",
            "grounding mode is missing or overstated",
            "CI or convergence-validation fails on pilot launch-control changes",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_scorecard_go_is_still_expansion_blocked(self):
        doc = self.read("docs/bettersafe-pilot-scorecard.md")
        required_phrases = [
            "Decision: GO — CONTROLLED LIMITED PILOT WITH OPERATOR HARDENING ACTIONS",
            "Expansion: BLOCKED until a new scorecard records PASS evidence for the expanded slice.",
            "Any UNKNOWN_OR_BLOCKED, PENDING, FAIL, or PASS_PENDING_CURRENT_PR status blocks merge or expansion until resolved.",
            "The current hardening threshold applies only after the PR passes tests and convergence-validation.",
            "Operator-approved readiness actions: ALLOWED",
            "Unattended authority: BLOCKED",
            "Public high-impact authority: BLOCKED",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)


if __name__ == "__main__":
    unittest.main()
