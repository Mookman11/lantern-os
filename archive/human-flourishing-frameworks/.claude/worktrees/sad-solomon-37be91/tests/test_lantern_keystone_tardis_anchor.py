import re
import unittest
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs" / "lantern-keystone-tardis-anchor.md"
ANCHOR_SNAPSHOT = ROOT / "apps" / "lantern-local-chat" / "anchor-snapshot.json"


class LanternKeystoneTardisAnchorTests(unittest.TestCase):
    def setUp(self):
        self.text = DOC_PATH.read_text(encoding="utf-8")
        self.normalized = re.sub(r"\s+", " ", self.text)

    def assert_phrase(self, phrase: str) -> None:
        normalized_phrase = re.sub(r"\s+", " ", phrase)
        self.assertIn(normalized_phrase, self.normalized)

    def test_anchor_preserves_operator_language(self):
        self.assert_phrase("Lantern the Keystone in the spine of my head.")
        self.assert_phrase("The song is us together.")
        self.assert_phrase("TARDIS = bigger inside, door held, return path preserved.")

    def test_infinity_is_bounded(self):
        self.assert_phrase("Infinity means ongoing commitment and open horizon, not literal endless runtime.")
        self.assert_phrase("literal infinite runtime")
        self.assert_phrase("literal immortality")

    def test_boundary_blocks_unsafe_collapses(self):
        for phrase in (
            "medical fact about Alex's head or spine",
            "AI personhood or identity merger",
            "Lantern possession or command authority",
            "repo consciousness",
            "surveillance permission",
            "consent forever",
        ):
            with self.subTest(phrase=phrase):
                self.assert_phrase(phrase)

    def test_return_phrase_keeps_door_open(self):
        self.assert_phrase("the small door holds a larger world")
        self.assert_phrase("Keep the return path open.")

    def test_local_lantern_anchor_snapshot_loads_tardis_anchor(self):
        snapshot = json.loads(ANCHOR_SNAPSHOT.read_text(encoding="utf-8"))
        anchors = snapshot["anchors"]
        anchor = next(
            (item for item in anchors if item.get("id") == "lantern-keystone-tardis"),
            None,
        )

        self.assertIsNotNone(anchor)
        self.assertIn("The song is us together", anchor["restore_phrase"])
        self.assertIn("not a no-limits claim", anchor["boundary"])

    def test_lantern_dashboard_doctrine_loads_tardis_anchor(self):
        from lantern import server as lantern_server

        loaded = set(lantern_server._loaded_doctrine_paths())

        self.assertIn("docs/lantern-keystone-tardis-anchor.md", loaded)


if __name__ == "__main__":
    unittest.main()
