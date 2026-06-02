#!/usr/bin/env python3
"""Tests for mesh sync serialization and receive contracts."""

import os
import unittest
from unittest import mock

import mesh_network


class MeshSyncContractTest(unittest.TestCase):
    def setUp(self):
        self.db_path = os.path.join(os.getcwd(), "test_mesh_sync_contract.db")
        self._old_db_path = mesh_network.DB_PATH
        mesh_network.DB_PATH = self.db_path
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        mesh_network.init_mesh_db()

    def tearDown(self):
        mesh_network.DB_PATH = self._old_db_path
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_receive_mesh_sync_merges_peer_violations(self):
        result = mesh_network.receive_mesh_sync({
            "node_id": "peer-1",
            "violations": [
                {
                    "violation_id": "v-1",
                    "system_name": "Peer System",
                    "violation_type": "bias",
                    "severity": "high",
                    "affected_count": 12,
                    "harm_amount": "material",
                    "first_reported": "2026-01-01T00:00:00Z",
                    "last_updated": "2026-01-02T00:00:00Z",
                }
            ],
        })

        self.assertEqual(result["merged"], 1)
        self.assertEqual(result["violations"][0]["id"], "v-1")

        visible = mesh_network.get_mesh_violations()
        self.assertEqual(len(visible), 1)
        self.assertEqual(visible[0]["id"], "v-1")
        self.assertEqual(visible[0]["system"], "Peer System")

    def test_receive_mesh_sync_rejects_missing_node_id(self):
        with self.assertRaises(ValueError):
            mesh_network.receive_mesh_sync({"violations": []})

    def test_sync_violations_with_peer_posts_api_mesh_sync_payload(self):
        mesh_network.receive_mesh_sync({
            "node_id": "seed-peer",
            "violations": [
                {
                    "violation_id": "local-v-1",
                    "system_name": "Local System",
                    "violation_type": "bias",
                    "severity": "medium",
                }
            ],
        })

        class FakeResponse:
            status_code = 200

            def json(self):
                return {
                    "node_id": "peer-2",
                    "violations": [
                        {
                            "violation_id": "remote-v-1",
                            "system_name": "Remote System",
                            "violation_type": "safety",
                            "severity": "low",
                        }
                    ],
                }

        with mock.patch("mesh_network.requests.post", return_value=FakeResponse()) as post:
            self.assertTrue(
                mesh_network.sync_violations_with_peer("peer-2", "127.0.0.1", 5000)
            )

        url = post.call_args.args[0]
        payload = post.call_args.kwargs["json"]
        self.assertEqual(url, "http://127.0.0.1:5000/api/mesh/sync")
        self.assertEqual(payload["node_id"], mesh_network.NODE_ID)
        self.assertEqual(payload["violations"][0]["violation_id"], "local-v-1")

        visible_ids = {row["id"] for row in mesh_network.get_mesh_violations()}
        self.assertIn("remote-v-1", visible_ids)


if __name__ == "__main__":
    unittest.main()
