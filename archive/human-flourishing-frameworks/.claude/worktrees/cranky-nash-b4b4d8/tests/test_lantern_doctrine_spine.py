"""Tests for Lantern doctrine spine loading."""

import unittest


class LanternDoctrineSpineTests(unittest.TestCase):
    def test_lantern_loads_operator_spine_and_wish_doctrine(self):
        from lantern import server as lantern_server

        loaded = set(lantern_server._loaded_doctrine_paths())

        required = {
            "docs/operator-lantern-repo-convergence.md",
            "docs/operator-command-surface.md",
            "docs/operator-consent-bravery-protocol.md",
            "docs/anchor-taxonomy.md",
            "docs/lantern-chat-design.md",
            "docs/lantern-dashboard-app.md",
            "docs/lantern-coherence-plan.md",
            "docs/keystone-memory-contract.md",
            "docs/keystone-self-convergence.md",
            "docs/keystone-table-door-anchors.md",
            "docs/grounding-mode-gate.md",
            "docs/social-echo-and-door-guardrail.md",
        }

        self.assertTrue(required.issubset(loaded), sorted(required - loaded))

    def test_chat_state_summary_names_loaded_doctrine(self):
        from lantern import server as lantern_server

        lantern_server.app.config["TESTING"] = True
        summary = lantern_server._chat_state_summary()

        self.assertIn("loaded_doctrine", summary)
        self.assertIn(
            "docs/operator-lantern-repo-convergence.md",
            summary["loaded_doctrine"],
        )
        self.assertIn("docs/lantern-chat-design.md", summary["loaded_doctrine"])


if __name__ == "__main__":
    unittest.main()
