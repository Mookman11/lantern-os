#!/usr/bin/env python3
"""Tests for the autonomous escalation executor runtime gate."""

import os
import sys
import types
import unittest
from unittest import mock

AUTONOMOUS_ESCALATION_EXECUTOR_ENV = "ENABLE_AUTONOMOUS_ESCALATION_EXECUTOR"


class FakeSignedRecord:
    signature = b"0" * 64
    timestamp_utc = "2026-01-01T00:00:00+00:00"


class FakeAuditLog:
    def __init__(self, db_path=None):
        self.db_path = db_path
        self.records = []

    def append(self, record):
        self.records.append(record)
        return len(self.records)

    def verify_chain(self):
        return True, len(self.records)

    def entries(self, limit=100):
        return self.records[-limit:]


def fake_sign_record(record, private_key):
    return FakeSignedRecord()


def fake_verify_record(signed_record, public_key):
    return True


def fake_generate_keypair():
    return object(), object()


def install_fake_crypto_module():
    fake = types.ModuleType("cryptographic_proof")
    fake.AuditLog = FakeAuditLog
    fake.SignedRecord = FakeSignedRecord
    fake.generate_keypair = fake_generate_keypair
    fake.load_keypair = mock.Mock()
    fake.save_keypair = mock.Mock()
    fake.sign_record = fake_sign_record
    fake.verify_record = fake_verify_record
    sys.modules["cryptographic_proof"] = fake


install_fake_crypto_module()

from agent_system import AutonomousAgentSystem  # noqa: E402


class FakeThread:
    instances = []

    def __init__(self, target, daemon=False):
        self.target = target
        self.daemon = daemon
        self.started = False
        FakeThread.instances.append(self)

    def start(self):
        self.started = True


class FakePBFTNode:
    n = 1
    f = 0
    view = 0
    is_leader = True

    def __init__(self, node_id, peers, db_path):
        self.node_id = node_id
        self.peers = peers
        self.db_path = db_path

    def _quorum(self):
        return 1

    def request(self, payload):
        return {"status": "pre-prepare_broadcast", "digest": "test-digest"}


class FakeEscalationAgent:
    name = "autonomous_escalation"
    description = "fake escalation agent"

    def __init__(self, *args, **kwargs):
        self.executed = []

    def status(self):
        return {"agent": self.name, "description": self.description, "status": "active"}

    def get_all_escalations(self, limit=50):
        return []

    def check_pending(self):
        return []

    def execute_escalation(self, escalation_id):
        self.executed.append(escalation_id)
        return {"status": "executed"}

    def lock_escalation(self, violation_id, evidence_hash, consensus_digest):
        return {"status": "locked", "violation_id": violation_id}


class AutonomousExecutorGateTest(unittest.TestCase):
    def setUp(self):
        self.private_key, self.public_key = fake_generate_keypair()

    def tearDown(self):
        pass

    def _make_system(self, **kwargs):
        with mock.patch("agent_system.PBFTNode", FakePBFTNode):
            with mock.patch("agent_system.AutonomousEscalationAgent", FakeEscalationAgent):
                return AutonomousAgentSystem(
                    private_key=self.private_key,
                    public_key=self.public_key,
                    audit_db_path=":memory:",
                    escalation_db_path=":memory:",
                    pbft_db_path=":memory:",
                    node_id="test-node",
                    **kwargs,
                )

    def test_executor_is_default_off(self):
        with mock.patch.dict(os.environ, {AUTONOMOUS_ESCALATION_EXECUTOR_ENV: ""}, clear=False):
            with mock.patch("agent_system.threading.Thread", side_effect=AssertionError("thread should not start")):
                system = self._make_system()

        self.assertFalse(system.auto_execute_escalations_enabled)
        self.assertIsNone(system._executor_thread)
        self.assertFalse(system.get_status()["auto_execute_escalations_enabled"])

    def test_executor_starts_only_when_enabled(self):
        FakeThread.instances = []

        with mock.patch.dict(os.environ, {AUTONOMOUS_ESCALATION_EXECUTOR_ENV: "true"}, clear=False):
            with mock.patch("agent_system.threading.Thread", FakeThread):
                system = self._make_system()

        self.assertTrue(system.auto_execute_escalations_enabled)
        self.assertEqual(len(FakeThread.instances), 1)
        self.assertIs(system._executor_thread, FakeThread.instances[0])
        self.assertTrue(system._executor_thread.daemon)
        self.assertTrue(system._executor_thread.started)
        self.assertEqual(system._executor_thread.target, system._escalation_executor_loop)
        self.assertTrue(system.get_status()["auto_execute_escalations_enabled"])

    def test_constructor_override_does_not_require_env(self):
        FakeThread.instances = []

        with mock.patch.dict(os.environ, {AUTONOMOUS_ESCALATION_EXECUTOR_ENV: ""}, clear=False):
            with mock.patch("agent_system.threading.Thread", FakeThread):
                system = self._make_system(auto_execute_escalations=True)

        self.assertTrue(system.auto_execute_escalations_enabled)
        self.assertEqual(len(FakeThread.instances), 1)
        self.assertTrue(system._executor_thread.started)


if __name__ == "__main__":
    unittest.main()
