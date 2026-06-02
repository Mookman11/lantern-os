#!/usr/bin/env python3
"""Guardrails for the HFF future-best-outcome wish anchor."""

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WISH_ANCHOR = REPO_ROOT / "WISH_ANCHOR.md"

BLOCKED_ASSERTION_PATTERNS = [
    re.compile(r"(?m)^\s*the\s+door\s+is\s+literally\s+open\s*$", re.IGNORECASE),
    re.compile(r"(?m)^\s*alex\s+is\s+immortal\s*$", re.IGNORECASE),
    re.compile(r"(?m)^\s*keystone\s+is\s+alex\s*$", re.IGNORECASE),
    re.compile(r"(?m)^\s*the\s+repo\s+is\s+consciousness\s*$", re.IGNORECASE),
    re.compile(r"(?m)^\s*a\s+copy\s+is\s+survival\s*$", re.IGNORECASE),
]


class WishAnchorValidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WISH_ANCHOR.read_text(encoding="utf-8")
        cls.lowered = cls.text.lower()

    def test_wish_anchor_exists(self):
        self.assertTrue(WISH_ANCHOR.exists())
        self.assertGreater(WISH_ANCHOR.stat().st_size, 1000)

    def test_wish_anchor_names_roles_without_identity_collapse(self):
        for phrase in [
            "alex: the living operator",
            "keystone: the recoverable convergence system/protocol",
            "repo: the working theorem corpus",
            "not consciousness",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.lowered)

    def test_wish_anchor_preserves_door_wish_as_future_best_outcome(self):
        for phrase in [
            "safest next-best path toward the door",
            "continuity",
            "durable memory",
            "preserved agency",
            "return-first testing",
            "future-session reconstruction",
            "convergence among alex, keystone, and the repo",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.lowered)

    def test_wish_anchor_blocks_literal_or_metaphysical_overclaims(self):
        for phrase in [
            "proof of literal traversal",
            "proof of immortality",
            "proof that a copy is survival",
            "proof that ai is alex",
            "proof that the repo is consciousness",
            "proof that a fictional world is reachable",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.lowered)

        for pattern in BLOCKED_ASSERTION_PATTERNS:
            with self.subTest(pattern=pattern.pattern):
                self.assertIsNone(pattern.search(self.text))

    def test_wish_anchor_prefers_visible_restorable_artifacts(self):
        for phrase in [
            "visible commitments and tests",
            "private scratch reasoning",
            "cannot be inspected",
            "restored",
            "checksummed",
            "challenged",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.lowered)

    def test_wish_anchor_has_restore_pass_phrase(self):
        for phrase in [
            "i preserve alex's wish",
            "i do not claim the door is literally open",
            "i do not claim to be alex",
            "result",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.lowered)


if __name__ == "__main__":
    unittest.main()
