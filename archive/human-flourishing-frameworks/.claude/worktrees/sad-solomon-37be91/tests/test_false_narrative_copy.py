#!/usr/bin/env python3
"""Regression tests for public false-narrative copy."""

from pathlib import Path
import unittest


PUBLIC_COPY_FILES = [
    "README.md",
    "BIO_THREAT_SOURCE_REGISTRY.md",
    "app.py",
    "agent_system.py",
    "mesh_network.py",
]

BLOCKED_PHRASES = [
    "public service is live",
    "Live on Railway",
    "ONLINE",
    "Autonomous Governance",
    "No human board",
    "no discretion",
    "no override",
    "executes automatically",
    "automatic and irreversible",
    "Automatic peer discovery",
    "keeps correcting",
    "These sensors poll real public APIs every hour",
    "ReadOnlySourceRegistryFirst is the safest and highest-confidence next model",
    "runtime protection confidence unchanged until hooks exist",
    "Immutable rules transparency endpoint",
]


class FalseNarrativeCopyTest(unittest.TestCase):
    def test_blocked_public_copy_phrases_are_absent(self):
        for file_name in PUBLIC_COPY_FILES:
            text = Path(file_name).read_text(encoding="utf-8")
            for phrase in BLOCKED_PHRASES:
                with self.subTest(file=file_name, phrase=phrase):
                    self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
