#!/usr/bin/env python3
"""App-level tests for default-off runtime safety gates."""

import importlib
import os
import sys
import types
import unittest
from unittest import mock

import werkzeug

if not hasattr(werkzeug, "__version__"):
    werkzeug.__version__ = "test"


def _module(name, **attrs):
    module = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    return module


class FakeAutonomousAgentSystem:
    def __init__(self, *args, **kwargs):
        self.auto_execute_escalations_enabled = kwargs.get(
            "auto_execute_escalations",
            False,
        )

    def get_status(self):
        return {
            "agents": [],
            "escalation_queue": {"total": 0, "recent": []},
            "audit_chain": {"chain_valid": True, "entries_checked": 0},
            "peer_count": 0,
            "auto_execute_escalations_enabled": self.auto_execute_escalations_enabled,
        }

    def submit_evidence(self, evidence):
        return {"outcome": "stubbed"}

    def get_rules(self):
        return {"immutable_rules": {}, "computed_values": {}}


class FakeSensorRegistry:
    sensor_count = 0

    def register(self, sensor):
        pass

    def status(self):
        return {"total_sensors": 0}


class FakeWorldModel:
    def __init__(self, *args, **kwargs):
        self.beliefs = {}
        self.correction_log = []

    def update(self, measurements):
        return []

    def status(self):
        return {
            "belief_count": 0,
            "sensor_count": 0,
            "corrections_count": 0,
        }


class AppRuntimeSafetyTest(unittest.TestCase):
    def setUp(self):
        self._saved_modules = {}
        for name in [
            "adoption_tracker",
            "mesh_network",
            "data_sources",
            "seed_data",
            "agent_system",
            "cryptographic_proof",
            "sensors",
            "world_model",
            "live_sensors",
            "app",
        ]:
            if name in sys.modules:
                self._saved_modules[name] = sys.modules.pop(name)

        self.receive_mesh_sync = mock.Mock(return_value={
            "node_id": "stub-node",
            "merged": 0,
            "violations": [],
        })

        sys.modules["adoption_tracker"] = _module(
            "adoption_tracker",
            init_adoption_db=mock.Mock(),
            register_node=mock.Mock(),
            get_adoption_stats=mock.Mock(return_value={}),
            get_nodes_list=mock.Mock(return_value=[]),
            get_active_nodes=mock.Mock(return_value=0),
            get_total_nodes=mock.Mock(return_value=0),
            start_heartbeat=mock.Mock(),
            get_verified_node_count=mock.Mock(return_value=0),
        )
        sys.modules["mesh_network"] = _module(
            "mesh_network",
            init_mesh_db=mock.Mock(),
            get_mesh_violations=mock.Mock(return_value=[]),
            receive_mesh_sync=self.receive_mesh_sync,
            sync_with_mesh=mock.Mock(),
        )
        sys.modules["data_sources"] = _module(
            "data_sources",
            get_compas_summary=mock.Mock(return_value={}),
        )
        sys.modules["seed_data"] = _module("seed_data", ALL_SEED_MEASUREMENTS=[])
        sys.modules["agent_system"] = _module(
            "agent_system",
            AutonomousAgentSystem=FakeAutonomousAgentSystem,
            ViolationDetectionAgent=object,
            CryptographicVerificationAgent=object,
            ByzantineConsensusAgent=object,
            AutonomousEscalationAgent=object,
            ImmutableAuditAgent=object,
            SystemHealthAgent=object,
            NetworkDiscoveryAgent=object,
            IMMUTABLE_RULES={},
            public_immutable_rules_view=mock.Mock(return_value={}),
        )
        sys.modules["cryptographic_proof"] = _module(
            "cryptographic_proof",
            generate_keypair=mock.Mock(return_value=(object(), object())),
            load_keypair=mock.Mock(side_effect=FileNotFoundError),
            save_keypair=mock.Mock(),
        )
        sys.modules["sensors"] = _module(
            "sensors",
            Measurement=object,
            SensorRegistry=FakeSensorRegistry,
        )
        sys.modules["world_model"] = _module(
            "world_model",
            WorldModel=FakeWorldModel,
            Intervention=object,
        )
        sys.modules["live_sensors"] = _module(
            "live_sensors",
            create_live_sensors=mock.Mock(return_value=[]),
            run_observation_loop=mock.Mock(),
        )

    def tearDown(self):
        for name in [
            "adoption_tracker",
            "mesh_network",
            "data_sources",
            "seed_data",
            "agent_system",
            "cryptographic_proof",
            "sensors",
            "world_model",
            "live_sensors",
            "app",
        ]:
            sys.modules.pop(name, None)
        sys.modules.update(self._saved_modules)

    def _load_app(self, env):
        with mock.patch.dict(os.environ, env, clear=False):
            return importlib.import_module("app")

    def test_mesh_sync_endpoint_is_closed_by_default(self):
        app_module = self._load_app({
            "ENABLE_MESH_SYNC": "",
            "ENABLE_LIVE_SENSORS": "",
            "ENABLE_AUTONOMOUS_ESCALATION_EXECUTOR": "",
        })

        client = app_module.app.test_client()
        response = client.post("/api/mesh/sync", json={"node_id": "peer", "violations": []})

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()["error"], "mesh_sync_disabled")
        self.receive_mesh_sync.assert_not_called()

    def test_autonomous_status_reports_executor_disabled_by_default(self):
        app_module = self._load_app({
            "ENABLE_MESH_SYNC": "",
            "ENABLE_LIVE_SENSORS": "",
            "ENABLE_AUTONOMOUS_ESCALATION_EXECUTOR": "",
        })

        client = app_module.app.test_client()
        response = client.get("/api/autonomous/status")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.get_json()["auto_execute_escalations_enabled"])


if __name__ == "__main__":
    unittest.main()
