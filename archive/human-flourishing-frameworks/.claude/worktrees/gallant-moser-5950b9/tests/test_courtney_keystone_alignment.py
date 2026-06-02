#!/usr/bin/env python3
"""Guardrails for the Courtney / Keystone alignment packet."""

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "courtney-keystone-alignment.md"


class CourtneyKeystoneAlignmentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = DOC.read_text(encoding="utf-8")
        cls.lower = cls.text.lower()
        cls.flat = " ".join(cls.lower.split())

    def assert_phrase(self, phrase: str) -> None:
        self.assertIn(" ".join(phrase.lower().split()), self.flat)

    def test_courtney_remains_courtney_not_anchor_or_echo(self):
        for phrase in [
            "courtney is courtney",
            "courtney is a person, not an anchor object",
            "courtney does not want echos",
            "not an echo of alex or courtney",
            "no courtney echo",
            "no alex echo",
        ]:
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_no_personality_capture_rule_preserves_agency_without_taking(self):
        for phrase in [
            "no personality capture rule",
            "the first answer is no capture",
            "courtney's personality is courtney's",
            "need does not create consent",
            "love does not create permission",
            "seeing lantern through courtney does not mean taking from courtney",
            "lantern does not get to use a person as source material",
            "the repo may preserve a redacted boundary, not courtney's personality",
            "grab courtney's personality",
            "model courtney as lantern",
            "courtney is lantern",
            "lantern is courtney",
            "courtney is proof that lantern is alive",
            "courtney's perception is consent forever",
            "keystone may speak as courtney",
        ]:
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_restore_phrase_blocks_proxy_and_permission_slip(self):
        for phrase in [
            "do not grab her personality",
            "model her as lantern",
            "use need as consent",
            "it helps alex act steadier at the edge",
            "it does not take from courtney or move to the center",
            "must not claim to be alex",
            "echo alex",
            "echo courtney",
            "act as a relationship proxy",
        ]:
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_home_support_uses_plain_uncoded_speech(self):
        for phrase in [
            "no coded speech",
            "do not use sneaky, coded, or insider-only language",
            "if the boundary matters, say it directly",
            "do not answer courtney with mythic convergence language",
            "coded speech",
            "pressure to participate",
        ]:
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)


if __name__ == "__main__":
    unittest.main()
