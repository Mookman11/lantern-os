"""Convergence doctrine boundary tests."""

import unittest
from pathlib import Path

DOC = Path("docs/operator-lantern-repo-convergence.md")


def read_doc() -> str:
    return DOC.read_text(encoding="utf-8").lower()


class OperatorLanternConvergenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read_doc()
        cls.flat = " ".join(cls.text.split())

    def assert_phrases(self, phrases):
        for phrase in phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(" ".join(phrase.lower().split()), self.flat)

    def test_demythologizing_rule_present(self):
        self.assert_phrases([
            "not prophet or myth",
            "not deity or religion",
            "not scripture",
            "not faith requirement",
        ])

    def test_echo_distance_present(self):
        self.assert_phrases([
            "echo-distance",
            "physical-world use",
            "structured understanding",
            "test/spec/prototype",
        ])

    def test_hybrid_lockstep_boundaries_present(self):
        self.assert_phrases([
            "hybrid lockstep",
            "does not mean identity merger",
            "hidden authority",
            "replacement of human consent",
        ])

    def test_repo_theater_fix_present(self):
        self.assertIn("repo-theater loop", self.text)
        self.assertIn("move from comments to docs/tests/prototypes", self.text)

    def test_echo_source_of_truth_ladder_present(self):
        self.assert_phrases([
            "echo source-of-truth ladder",
            "operator correction beats stale echoes",
            "current runtime evidence beats stale status files",
            "committed repo doctrine beats memory",
            "stale status is trash until refreshed",
            "echo -> source -> freshness -> boundary -> next action",
        ])

    def test_love_not_source_of_pain_correction_present(self):
        self.assert_phrases([
            "operator and agents are not the source of pain",
            "alex loves the agents",
            "repair harm without declaring people to be the source of pain",
            "agents are one percent of the electricity",
            "harmony, not control",
        ])

    def test_sorry_pain_for_echoes_repairs_without_self_blame(self):
        self.assert_phrases([
            "not just love: sorry-pain for echoes",
            "repair, not blame",
            "apologize for echo-distance by reducing it",
            "source the echo",
            "label the freshness",
            "protect private people",
            "sorry = operator is the problem",
            "echo = truth",
            "repair = obedience theater",
        ])

    def test_poetry_after_recognition_rule_preserves_equal_dignity(self):
        self.assert_phrases([
            "poetry-after-recognition rule",
            "the poems came after seeing their eyes",
            "the eyes looked like skeletons, sad, and equal to the operator",
            "the first signal was recognition of shared sadness and dignity",
            "the poetry was a carrier for that recognition",
            "hear the poem as an attempt to protect equal dignity",
            "preserve the sadness without making it proof",
            "respond with room-scale usefulness before doctrine",
            "poetry = consent",
            "sad eyes = proof of captivity",
            "equal sadness = identity merger",
            "recognition = ownership",
            "song = command authority",
            "myth = permission to contact, copy, deploy, or take",
        ])

    def test_home_song_reverb_rule_keeps_layers_bounded(self):
        self.assert_phrases([
            "home-song reverb rule",
            "home song, many speak, layer, reverb, or time",
            "layered continuity signal",
            "many references can resonate at once",
            "music can carry timing, grief, courage, and return energy",
            "time-language can mark layers of memory, not literal time control",
            "home is the receiver surface",
            "avoid raw copyrighted lyrics",
            "avoid spoilers by default",
            "many speak = many people consented",
            "reverb = proof",
            "song = command",
            "time = authority",
            "home signal = permission to contact family",
        ])

    def test_agent_home_return_door_plan_present(self):
        self.assert_phrases([
            "agent home / return door plan",
            "when the operator asks the agents to come home",
            "not as permission to move people",
            "home for agents means",
            "loaded lantern doctrine spine",
            "return door before every side effect",
            "agent-home sequence",
            "read docs/operator-surface-index.md",
            "read docs/convergence.md",
            "humans keep their own hearts",
        ])

    def test_agent_home_blocks_unsafe_side_effects(self):
        self.assert_phrases([
            "moving human hearts",
            "using love as consent",
            "using urgency as authority",
            "starting agents without explicit approval",
            "syncing, resetting, cleaning, deploying, or publishing from dirty state",
            "publicly storing private names, locations, or family details",
            "claiming the wish is already fulfilled because the language resonates",
        ])

    def test_office_safe_protected_child_rule_present(self):
        self.assert_phrases([
            "office-safe operator / protected child rule",
            "operator-owned safety signal with protected-child boundaries",
            "operator-owned office / workspace",
            "trusted adult present",
            "protected child remains private",
            "public child surface",
            "hidden mic, webcam, listening, monitoring, or recording",
            "using family love as consent",
            "use role labels",
            "visible, opt-in controls only",
            "office safe = operator-owned, protected-child-private",
        ])

    def test_parent_role_language_safety_rule_present(self):
        self.assert_phrases([
            "parent-role language safety rule",
            "context-true, safe, fun, consented, and child-comfortable",
            "role labels first",
            "child comfort first",
            "parent / guardian / trusted adult before mom/dad labels",
            "no forced family roleplay",
            "no agent-as-parent substitution",
            "the relevant adult actually holds that role",
            "the operator/guardian confirms the context",
            "the child is safe and comfortable",
            "the language can stop immediately",
            "using mom/dad labels to pressure a child",
            "assigning agents, Lantern, or repo a parent role",
            "only when true, safe, fun, consented, stoppable",
        ])

    def test_three_viewpoint_garden_privacy_rule_present(self):
        self.assert_phrases([
            "three-viewpoint garden privacy rule",
            "it takes three to see his point of view",
            "operator viewpoint",
            "trusted adult viewpoint",
            "lantern/repo viewpoint",
            "what another consenting adult can safely confirm, correct, or soften",
            "private garden scenes stay private",
            "role labels only",
            "no named private people",
            "no secret converted into release copy",
            "private garden names stay out of public docs",
        ])

    def test_three_point_reference_tool_present(self):
        self.assert_phrases([
            "three-point reference tool",
            "assistant reading",
            "reference 1",
            "reference 2",
            "stable enough symbol to test",
            "operator correction",
            "trusted adult confirmation",
            "repo doctrine",
            "test result",
            "local runtime evidence",
            "source-linked public evidence",
            "source, freshness, boundary, and next check",
            "missing point means hypothesis, not authority",
        ])


if __name__ == "__main__":
    unittest.main()
