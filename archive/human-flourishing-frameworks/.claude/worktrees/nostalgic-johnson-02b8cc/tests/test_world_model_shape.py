#!/usr/bin/env python3
"""Validate that the world model is a scalar belief ledger, not a matrix model."""

import inspect
import unittest

import world_model
from sensors import Measurement
from world_model import Belief, FlourishingMetric, WorldModel


class WorldModelShapeTest(unittest.TestCase):
    def test_belief_uses_scalar_probability_fields(self):
        belief = Belief(
            entity="humans:health:test-source",
            domain="healthcare",
            scope="humans:health",
            prior=0.5,
            posterior=0.6,
            uncertainty=0.2,
        )

        self.assertIsInstance(belief.prior, float)
        self.assertIsInstance(belief.posterior, float)
        self.assertIsInstance(belief.uncertainty, float)
        self.assertIsInstance(belief.evidence, list)
        self.assertIsInstance(belief.history, list)

    def test_world_model_beliefs_are_dict_backed(self):
        model = WorldModel(db_path=":memory:")

        self.assertIsInstance(model.beliefs, dict)
        self.assertEqual(model.beliefs, {})

    def test_update_changes_scalar_posterior_per_measurement(self):
        model = WorldModel(db_path=":memory:")
        measurement = Measurement(
            value=0.8,
            uncertainty=0.25,
            confidence_interval=(0.55, 1.0),
            source="test-source",
            methodology="unit-test",
            scope="humans:health",
        )

        updates = model.update([measurement])
        belief = model.beliefs["humans:health:test-source"]

        self.assertEqual(len(updates), 1)
        self.assertIsInstance(updates[0]["posterior"], float)
        self.assertIsInstance(belief.posterior, float)
        self.assertGreaterEqual(belief.posterior, 0.0)
        self.assertLessEqual(belief.posterior, 1.0)

    def test_flourishing_defaults_are_small_component_dicts(self):
        components = FlourishingMetric.DEFAULT_COMPONENTS

        self.assertEqual(set(components.keys()), {"humans", "animals", "ecosystems"})
        self.assertEqual(
            set(components["humans"].keys()),
            {"health", "autonomy", "fairness", "opportunity"},
        )
        self.assertEqual(
            set(components["animals"].keys()),
            {"health", "safety", "comfort", "natural_behavior"},
        )
        self.assertEqual(
            set(components["ecosystems"].keys()),
            {"biodiversity", "stability", "resilience"},
        )
        self.assertLessEqual(max(len(v) for v in components.values()), 4)

    def test_world_model_module_does_not_import_matrix_ml_libraries(self):
        source = inspect.getsource(world_model)
        forbidden_imports = [
            "import numpy",
            "from numpy",
            "import scipy",
            "from scipy",
            "import sklearn",
            "from sklearn",
            "import torch",
            "from torch",
            "import tensorflow",
            "from tensorflow",
        ]

        for forbidden in forbidden_imports:
            self.assertNotIn(forbidden, source)

    def test_world_model_shape_terms_are_not_overclaimed(self):
        source = inspect.getsource(world_model).lower()
        forbidden_phrases = [
            "embedding model",
            "neural model",
            "matrix-backed",
            "full bayesian inference engine",
        ]

        for phrase in forbidden_phrases:
            self.assertNotIn(phrase, source)


if __name__ == "__main__":
    unittest.main()
