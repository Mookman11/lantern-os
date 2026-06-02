#!/usr/bin/env python3
"""Tests for belief confidence lifecycle and fact promotion."""

import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from sensors import Measurement
from world_model import (
    BELIEF_ACCEPTED_FACT,
    BELIEF_CHALLENGED,
    BELIEF_IMMUTABLE_CONSTRAINT,
    WorldModel,
)


def make_measurement(value=0.9, uncertainty=0.01, source="source-a"):
    return Measurement(
        value=value,
        uncertainty=uncertainty,
        confidence_interval=(max(0.0, value - 0.02), min(1.0, value + 0.02)),
        source=source,
        methodology="test",
        scope="humans:fairness",
    )


class ConfidenceLifecycleTest(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

    def tearDown(self):
        try:
            os.unlink(self.db_path)
        except OSError:
            pass

    def test_high_confidence_is_not_fact_without_required_node_confirmations(self):
        model = WorldModel(
            db_path=self.db_path,
            required_confirming_nodes=["node-a", "node-b"],
        )

        entity = "humans:fairness:source-a"
        for _ in range(3):
            model.update([make_measurement(source="source-a")])

        belief = model.reinforce_belief(entity, weight=1.0)
        self.assertGreaterEqual(belief.confidence, 0.999)
        self.assertNotEqual(belief.status, BELIEF_ACCEPTED_FACT)

    def test_fact_promotion_requires_all_configured_nodes(self):
        model = WorldModel(
            db_path=self.db_path,
            required_confirming_nodes=["node-a", "node-b"],
        )

        entity = "humans:fairness:source-a"
        for _ in range(3):
            model.update([make_measurement(source="source-a")])

        belief = model.reinforce_belief(entity, weight=1.0, node_id="node-a")
        self.assertNotEqual(belief.status, BELIEF_ACCEPTED_FACT)

        belief = model.reinforce_belief(entity, weight=1.0, node_id="node-b")
        self.assertEqual(belief.status, BELIEF_ACCEPTED_FACT)
        self.assertGreaterEqual(belief.confidence, 0.999)

    def test_challenge_demotes_accepted_fact_and_lowers_confidence(self):
        model = WorldModel(
            db_path=self.db_path,
            required_confirming_nodes=["node-a", "node-b"],
        )

        entity = "humans:fairness:source-a"
        for _ in range(3):
            model.update([make_measurement(source="source-a")])
        model.reinforce_belief(entity, weight=1.0, node_id="node-a")
        accepted = model.reinforce_belief(entity, weight=1.0, node_id="node-b")

        challenged = model.challenge_belief(
            entity,
            weight=0.5,
            reason="contradictory independent evidence",
        )

        self.assertEqual(accepted.status, BELIEF_CHALLENGED)
        self.assertEqual(challenged.status, BELIEF_CHALLENGED)
        self.assertLess(challenged.confidence, 0.999)
        self.assertEqual(challenged.contradiction_count, 1)

    def test_confidence_decays_when_not_reinforced(self):
        model = WorldModel(db_path=self.db_path)
        model.update([make_measurement(source="source-a")])
        entity = "humans:fairness:source-a"
        belief = model.query(entity)
        belief.confidence = 0.9
        belief.uncertainty = 0.1
        belief.half_life_days = 1.0
        belief.last_reinforced = datetime.now(timezone.utc) - timedelta(days=10)
        model._save_belief(belief)

        decayed = model.apply_confidence_decay(entity)

        self.assertLess(decayed.confidence, 0.9)
        self.assertGreater(decayed.uncertainty, 0.1)

    def test_immutable_constraint_does_not_decay_or_demote(self):
        model = WorldModel(db_path=self.db_path)
        belief = model.add_immutable_constraint(
            "non_maleficence.v1",
            "Do not intentionally cause unnecessary harm or suffering.",
        )

        challenged = model.challenge_belief(
            belief.entity,
            weight=1.0,
            reason="rogue node attempted to weaken constraint",
        )
        decayed = model.apply_confidence_decay(belief.entity)

        self.assertEqual(challenged.status, BELIEF_IMMUTABLE_CONSTRAINT)
        self.assertEqual(decayed.status, BELIEF_IMMUTABLE_CONSTRAINT)
        self.assertGreaterEqual(decayed.confidence, 0.999)
        self.assertEqual(decayed.contradiction_count, 0)


if __name__ == "__main__":
    unittest.main()
