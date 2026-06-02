"""Regression tests for the public projection of autonomous-system rules.

The HTML dashboard cleanup removed unsafe authority claims from the page copy;
this test guards the JSON analog. The public ``/api/autonomous/status`` and
``/api/autonomous/rules`` payloads must not carry flag-style fields whose names
imply governance authority the software does not possess.
"""

import json
import unittest

from agent_system import (
    IMMUTABLE_RULES,
    PUBLIC_RULES_DISCLAIMER,
    _INTERNAL_ONLY_RULE_KEYS,
    public_immutable_rules_view,
)


FORBIDDEN_KEYS = ("no_human_override", "escalation_is_irreversible")
FORBIDDEN_PHRASES = (
    "no_human_override",
    "escalation_is_irreversible",
    "ALGORITHMIC GOVERNANCE",
    "No human board",
    "irreversible after a 24-hour lock",
)


class PublicImmutableRulesProjectionTest(unittest.TestCase):
    def test_internal_rule_keys_match_forbidden_keys(self):
        self.assertEqual(
            set(_INTERNAL_ONLY_RULE_KEYS),
            set(FORBIDDEN_KEYS),
            "Internal-only key list and forbidden-key list must stay aligned.",
        )

    def test_public_view_omits_forbidden_keys(self):
        view = public_immutable_rules_view()
        for key in FORBIDDEN_KEYS:
            with self.subTest(key=key):
                self.assertNotIn(key, view)

    def test_public_view_serialized_json_has_no_forbidden_phrases(self):
        body = json.dumps(public_immutable_rules_view())
        for phrase in FORBIDDEN_PHRASES:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, body)

    def test_public_view_keeps_behavioral_fields(self):
        view = public_immutable_rules_view()
        for key in (
            "accuracy_gap_threshold",
            "escalation_lock_hours",
            "consensus_threshold_formula",
            "agent_count",
            "append_only_audit",
        ):
            with self.subTest(key=key):
                self.assertIn(key, view)

    def test_public_view_includes_research_mode_disclaimer(self):
        view = public_immutable_rules_view()
        self.assertEqual(view.get("mode"), "research")
        self.assertEqual(view.get("disclaimer"), PUBLIC_RULES_DISCLAIMER)
        self.assertIn("research", PUBLIC_RULES_DISCLAIMER.lower())
        self.assertIn("operator", PUBLIC_RULES_DISCLAIMER.lower())

    def test_internal_rules_constant_unchanged(self):
        for key in FORBIDDEN_KEYS:
            with self.subTest(key=key):
                self.assertIn(
                    key,
                    IMMUTABLE_RULES,
                    "IMMUTABLE_RULES must keep internal flags so startup "
                    "assertions in AgentBase._validate_rules continue to pass.",
                )


if __name__ == "__main__":
    unittest.main()
