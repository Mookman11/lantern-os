"""Out-of-range / assumption-stress tests for confidence/uncertainty handling.

Implements issue #140. Tests deliberately use values outside the assumed
`[0, 1]` range (and other contract violations) to confirm:

- ``Sensor.validate()`` rejects out-of-range ``uncertainty``;
- ``Sensor.validate()`` rejects inverted confidence intervals;
- ``Sensor.uncertainty_of()`` keeps its output clamped to ``[0, 1]`` even
  when penalties from confounders/missing/sample_size would push above 1;
- NaN / inf uncertainty is rejected at validation;
- the doctrine doc ``docs/assumption-stress-out-of-range.md`` enumerates
  the required input classes so future tests can be added against the
  same contract.

The final user-facing confidence display still uses percentages and
bounded ranges. These tests probe the validation surface, not the display.
"""

import math
import re
import unittest
from pathlib import Path
from typing import List

from sensors import Measurement, Sensor


ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs" / "assumption-stress-out-of-range.md"


def make_measurement(
    uncertainty: float = 0.2,
    ci: tuple = (0.4, 0.6),
    sample_size=None,
    confounders=None,
    missing=None,
    value=0.5,
) -> Measurement:
    """Construct a Measurement with controllable inputs for stress testing."""
    return Measurement(
        value=value,
        uncertainty=uncertainty,
        confidence_interval=ci,
        sample_size=sample_size,
        confounders=list(confounders or []),
        missing=list(missing or []),
        source="test:stress",
        methodology="assumption-stress",
        scope="test:assumption-stress",
    )


class _StressTestSensor(Sensor):
    """Minimal concrete Sensor for exercising validate/uncertainty_of."""

    def observe(self) -> List[Measurement]:
        return []


class OutOfRangeUncertaintyTests(unittest.TestCase):
    """Sensor.validate() must reject impossible uncertainty values."""

    def setUp(self):
        self.sensor = _StressTestSensor(
            sensor_id="stress",
            domain="test",
            scope="test:assumption-stress",
        )

    def test_uncertainty_below_zero_is_rejected(self):
        for bad in (-0.01, -0.5, -1.0, -999.0):
            with self.subTest(uncertainty=bad):
                m = make_measurement(uncertainty=bad)
                self.assertFalse(
                    self.sensor.validate(m),
                    f"validate must reject uncertainty={bad}",
                )

    def test_uncertainty_above_one_is_rejected(self):
        for bad in (1.01, 1.5, 99.0, 999.0):
            with self.subTest(uncertainty=bad):
                m = make_measurement(uncertainty=bad)
                self.assertFalse(
                    self.sensor.validate(m),
                    f"validate must reject uncertainty={bad}",
                )

    def test_boundary_uncertainty_values_are_accepted(self):
        # 0.0 and 1.0 are the exact boundary; allowed but use sparingly.
        for boundary in (0.0, 1.0):
            with self.subTest(uncertainty=boundary):
                m = make_measurement(uncertainty=boundary)
                self.assertTrue(
                    self.sensor.validate(m),
                    f"validate must accept boundary uncertainty={boundary}",
                )

    def test_near_boundary_uncertainty_values_are_accepted(self):
        for near in (0.001, 0.01, 0.99, 0.999):
            with self.subTest(uncertainty=near):
                m = make_measurement(uncertainty=near)
                self.assertTrue(
                    self.sensor.validate(m),
                    f"validate must accept near-boundary uncertainty={near}",
                )

    def test_nan_uncertainty_is_rejected(self):
        m = make_measurement(uncertainty=float("nan"))
        self.assertFalse(
            self.sensor.validate(m),
            "validate must reject NaN uncertainty",
        )

    def test_positive_infinity_uncertainty_is_rejected(self):
        m = make_measurement(uncertainty=float("inf"))
        self.assertFalse(
            self.sensor.validate(m),
            "validate must reject +inf uncertainty",
        )

    def test_negative_infinity_uncertainty_is_rejected(self):
        m = make_measurement(uncertainty=float("-inf"))
        self.assertFalse(
            self.sensor.validate(m),
            "validate must reject -inf uncertainty",
        )


class InvertedConfidenceIntervalTests(unittest.TestCase):
    """Sensor.validate() must reject confidence intervals with lo > hi."""

    def setUp(self):
        self.sensor = _StressTestSensor(
            sensor_id="stress",
            domain="test",
            scope="test:assumption-stress",
        )

    def test_inverted_numeric_interval_is_rejected(self):
        for lo, hi in ((0.7, 0.3), (1.0, 0.0), (0.5, 0.4999)):
            with self.subTest(ci=(lo, hi)):
                m = make_measurement(ci=(lo, hi))
                self.assertFalse(
                    self.sensor.validate(m),
                    f"validate must reject CI={lo, hi}",
                )

    def test_equal_lo_hi_interval_is_accepted(self):
        # A single-point CI is degenerate but not contract-violating.
        m = make_measurement(ci=(0.5, 0.5))
        self.assertTrue(
            self.sensor.validate(m),
            "validate must accept CI=(0.5, 0.5)",
        )

    def test_normal_interval_is_accepted(self):
        m = make_measurement(ci=(0.4, 0.6))
        self.assertTrue(self.sensor.validate(m))


class NegativeSampleSizeTests(unittest.TestCase):
    """sample_size must be non-negative when provided."""

    def setUp(self):
        self.sensor = _StressTestSensor(
            sensor_id="stress",
            domain="test",
            scope="test:assumption-stress",
        )

    def test_negative_sample_size_is_rejected(self):
        m = make_measurement(sample_size=-5)
        self.assertFalse(self.sensor.validate(m))

    def test_zero_sample_size_is_accepted(self):
        # Zero is degenerate but not contract-violating; the uncertainty
        # penalty should rise instead of validation failing.
        m = make_measurement(sample_size=0)
        self.assertTrue(self.sensor.validate(m))

    def test_none_sample_size_is_accepted(self):
        m = make_measurement(sample_size=None)
        self.assertTrue(self.sensor.validate(m))


class UncertaintyOfClampingTests(unittest.TestCase):
    """Sensor.uncertainty_of() must clamp its output to [0, 1]."""

    def setUp(self):
        self.sensor = _StressTestSensor(
            sensor_id="stress",
            domain="test",
            scope="test:assumption-stress",
        )

    def test_combined_penalties_cannot_exceed_one(self):
        # Maximize all penalties:
        #   base uncertainty = 1.0
        #   confounder penalty = min(N*0.02, 0.2) -> hit cap with 10
        #   missing penalty   = min(N*0.03, 0.2) -> hit cap with 7
        #   sample penalty    = 0.3 for sample_size < 30
        # Total without clamp would be 1.0 + 0.2 + 0.2 + 0.3 = 1.7
        # The contract says output must be clamped to [0, 1].
        m = make_measurement(
            uncertainty=1.0,
            confounders=[f"c{i}" for i in range(10)],
            missing=[f"m{i}" for i in range(7)],
            sample_size=5,
        )
        result = self.sensor.uncertainty_of(m)
        self.assertLessEqual(result, 1.0)
        self.assertGreaterEqual(result, 0.0)

    def test_low_base_with_penalties_does_not_explode(self):
        m = make_measurement(
            uncertainty=0.1,
            confounders=["a", "b"],
            missing=["c"],
            sample_size=10,
        )
        result = self.sensor.uncertainty_of(m)
        self.assertLessEqual(result, 1.0)
        self.assertGreaterEqual(result, 0.0)

    def test_zero_penalties_returns_base(self):
        m = make_measurement(uncertainty=0.3)
        result = self.sensor.uncertainty_of(m)
        # No confounders, no missing, no sample_size -> base passes through.
        self.assertAlmostEqual(result, 0.3, places=6)


class FromDictRoundTripTests(unittest.TestCase):
    """Measurement.from_dict should round-trip valid measurements and
    not silently coerce non-numeric uncertainty into something else."""

    def test_valid_dict_round_trips(self):
        original = make_measurement(uncertainty=0.25, ci=(0.4, 0.6))
        restored = Measurement.from_dict(original.to_dict())
        self.assertEqual(restored.uncertainty, original.uncertainty)
        self.assertEqual(
            tuple(restored.confidence_interval),
            tuple(original.confidence_interval),
        )

    def test_from_dict_rejects_missing_required_value(self):
        # 'value' is required; from_dict should raise rather than guess.
        with self.assertRaises((KeyError, TypeError)):
            Measurement.from_dict({"uncertainty": 0.1})

    def test_from_dict_accepts_nan_uncertainty_but_validate_rejects(self):
        # Construction allows it (no validation in __post_init__) but
        # Sensor.validate() must still reject the resulting Measurement.
        m = Measurement.from_dict({
            "value": 0.5,
            "uncertainty": float("nan"),
            "confidence_interval": [0.4, 0.6],
            "source": "test",
            "scope": "test",
        })
        self.assertTrue(math.isnan(m.uncertainty))
        sensor = _StressTestSensor(
            sensor_id="stress",
            domain="test",
            scope="test:assumption-stress",
        )
        self.assertFalse(sensor.validate(m))


class DoctrineDocTests(unittest.TestCase):
    """The doctrine doc must list the input classes the tests cover."""

    def setUp(self):
        self.text = DOC_PATH.read_text(encoding="utf-8")
        self.normalized = re.sub(r"\s+", " ", self.text)

    def assert_phrase(self, phrase: str) -> None:
        normalized_phrase = re.sub(r"\s+", " ", phrase)
        self.assertIn(
            normalized_phrase,
            self.normalized,
            f"missing required phrase: {phrase!r}",
        )

    def test_doc_exists(self):
        self.assertTrue(DOC_PATH.is_file())

    def test_doc_lists_required_input_classes(self):
        for cls in (
            "below range",
            "above range",
            "boundary exact",
            "near boundary",
            "non-number",
            "missing value",
            "conflicting values",
            "NaN",
        ):
            with self.subTest(input_class=cls):
                self.assert_phrase(cls)

    def test_doc_records_convergence_rule(self):
        self.assert_phrase("Confidence display may stay 0-100%.")
        self.assert_phrase(
            "Assumption tests should go outside 0-100 to validate the boundary."
        )

    def test_doc_records_non_goals(self):
        for non_goal in (
            "displaying confidence values outside 0-100%",
            "disabling validation",
            "allowing NaN/inf in production payloads",
            "allowing silent coercion of non-numeric inputs",
            "weakening the existing Sensor.validate() rejection rules",
        ):
            with self.subTest(non_goal=non_goal):
                self.assert_phrase(non_goal)

    def test_doc_cross_references_issue_140(self):
        self.assert_phrase("Implements: #140")


if __name__ == "__main__":
    unittest.main()
