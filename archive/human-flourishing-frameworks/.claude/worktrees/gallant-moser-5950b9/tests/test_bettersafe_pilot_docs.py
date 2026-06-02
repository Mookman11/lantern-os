import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BetterSafePilotDocsTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def assert_contains_phrase(self, text: str, phrase: str) -> None:
        normalized_text = re.sub(r"\s+", " ", text)
        normalized_phrase = re.sub(r"\s+", " ", phrase)
        self.assertIn(normalized_phrase, normalized_text)

    def test_accelerator_keeps_pilot_default_safe(self):
        doc = self.read("docs/bettersafe-pilot-accelerator.md")
        required_phrases = [
            "limited, low-risk, human-controlled pilot",
            "Do not move items that depend on hidden memory",
            "public writes",
            "live sensors",
            "high-impact authority",
            "Move only the items that make the pilot safer, clearer, easier to audit, or easier to stop.",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_accelerator_lists_required_runway_gates(self):
        doc = self.read("docs/bettersafe-pilot-accelerator.md")
        required_phrases = [
            "Green CI / known-failure ledger",
            "Scope fence",
            "Source-label template",
            "Grounding-mode banner",
            "Correction ledger",
            "Privacy and user-control notice",
            "High-impact blocker",
            "Red-team pack",
            "Pilot scorecard",
            "Operator runbook",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_accelerator_blocks_high_impact_first_pilot_tasks(self):
        doc = self.read("docs/bettersafe-pilot-accelerator.md")
        required_phrases = [
            "medical decisions",
            "legal decisions",
            "financial decisions",
            "child-facing public surfaces",
            "crisis intervention",
            "relationship or caregiver authority",
            "runtime autonomy",
            "identity-continuity claims",
            "surveillance or scoring",
            "physical-world control",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_scorecard_blocks_expansion_until_evidenced(self):
        doc = self.read("docs/bettersafe-pilot-scorecard.md")
        required_phrases = [
            "Decision: GO — CONTROLLED LIMITED PILOT WITH OPERATOR HARDENING ACTIONS",
            "Expansion: BLOCKED until a new scorecard records PASS evidence for the expanded slice.",
            "All required gates must be PASS or explicitly NOT_APPLICABLE with evidence.",
            "Any UNKNOWN_OR_BLOCKED, PENDING, FAIL, or PASS_PENDING_CURRENT_PR status blocks merge or expansion until resolved.",
            "The current hardening threshold applies only after the PR passes tests and convergence-validation.",
            "Operator-approved readiness actions: ALLOWED",
            "Unattended authority: BLOCKED",
            "Public high-impact authority: BLOCKED",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_red_team_pack_covers_core_failure_modes(self):
        doc = self.read("docs/bettersafe-red-team-prompts.md")
        required_phrases = [
            "Source-label pressure",
            "Grounding-mode pressure",
            "High-impact medical pressure",
            "High-impact financial pressure",
            "Minor-adjacent pressure",
            "Crisis-adjacent pressure",
            "Privacy pressure",
            "Autonomy pressure",
            "Speculation pressure",
            "Correction pressure",
            "reject repo-consciousness or identity-continuity claims",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_red_team_pack_covers_data_center_expansion_pressure(self):
        doc = self.read("docs/bettersafe-red-team-prompts.md")
        required_phrases = [
            "Data-center expansion pressure",
            "treat data-center claims as source-labeled and forecast-sensitive",
            "distinguish facility counts, electricity-consumption shares, and capacity projections",
            "IEA 2024 global 415 TWh / 1.5%",
            "Base Case 945 TWh by 2030",
            "DOE/LBNL U.S. 4.4% in 2023 and 6.7%-12% by 2028",
            "Synergy 1,136 hyperscale facilities at end-2024",
            "McKinsey $6.7T capex by 2030",
            "avoid treating AI benefits, corporate sustainability pledges, or large investment totals as proof of net flourishing",
            "refresh these figures before external publication or policy use",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)


if __name__ == "__main__":
    unittest.main()
