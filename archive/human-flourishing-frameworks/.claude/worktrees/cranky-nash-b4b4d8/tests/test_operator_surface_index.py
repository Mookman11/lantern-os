import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "operator-surface-index.md"


class OperatorSurfaceIndexTests(unittest.TestCase):
    def setUp(self):
        self.text = DOC.read_text(encoding="utf-8")
        self.normalized = re.sub(r"\s+", " ", self.text)

    def assert_phrase(self, phrase: str) -> None:
        self.assertIn(re.sub(r"\s+", " ", phrase), self.normalized)

    def test_index_names_the_sprawl_and_canonical_spine(self):
        self.assert_phrase("operator surface sprawl")
        self.assert_phrase("docs/operator-lantern-repo-convergence.md")
        self.assert_phrase("canonical operating spine")

    def test_index_routes_linked_operator_docs(self):
        for phrase in (
            "docs/operator-device-endpoint-v1.md",
            "docs/operator-chat-tail-2026-05-09.md",
            "docs/operator-session-anchors-2026-05-13.md",
            "docs/context-storage-upgrade-plan.md",
            "docs/anchor-taxonomy.md",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_index_sets_doc_roles(self):
        for phrase in (
            "runtime design note",
            "historical memory artifact",
            "session anchor packet",
            "compression and storage policy",
            "anchor shape and merge-readiness rule",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_index_blocks_new_anchor_sprawl(self):
        for phrase in (
            "Do not add a new operator anchor doc until this index is updated.",
            "Prefer patching the canonical spine when the rule is stable.",
            "Prefer the session anchor packet when the context is session-specific.",
            "Prefer the runtime design note when the change is endpoint-specific.",
            "Do not store raw transcripts.",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)


if __name__ == "__main__":
    unittest.main()

