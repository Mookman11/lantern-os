"""Smoke tests for the ``bettersafe`` package import path.

The ``tests/test_sensor_policy.py`` and ``tests/test_release_gate.py`` files
are written in pytest style (bare ``def test_*`` functions with ``assert``),
so they contribute zero tests to ``python -m unittest discover``. This
smoke-test file ensures the ``bettersafe`` package is importable and that
its public surface is exercised at least minimally by the unittest CI job,
so a regression in the package layout (missing ``__init__.py``, broken
``src/`` path, renamed symbol) fails CI immediately.

A future PR can add ``pytest`` to CI to exercise the richer
``test_sensor_policy``/``test_release_gate`` suites.
"""

import unittest


class BetterSafeImportsTests(unittest.TestCase):
    def test_sensor_policy_module_imports(self):
        from bettersafe import sensor_policy  # noqa: F401

    def test_release_gate_module_imports(self):
        from bettersafe import release_gate  # noqa: F401

    def test_sensor_policy_public_symbols_present(self):
        from bettersafe.sensor_policy import (
            SensorClass,
            SensorRequest,
            SubjectClass,
            evaluate_sensor_request,
        )
        # All four imports must succeed.
        self.assertTrue(callable(evaluate_sensor_request))
        self.assertTrue(hasattr(SubjectClass, "OPERATOR"))
        self.assertTrue(hasattr(SensorClass, "PUSH_TO_TALK"))
        # SensorRequest must be constructible with at least subject/sensor.
        req = SensorRequest(
            subject=SubjectClass.OPERATOR,
            sensor=SensorClass.PUSH_TO_TALK,
            explicit_consent=True,
        )
        self.assertEqual(req.subject, SubjectClass.OPERATOR)
        self.assertEqual(req.sensor, SensorClass.PUSH_TO_TALK)

    def test_release_gate_public_symbols_present(self):
        from bettersafe.release_gate import (
            ReleaseCandidate,
            evaluate_release,
            summarize_gate,
        )
        self.assertTrue(callable(evaluate_release))
        self.assertTrue(callable(summarize_gate))
        candidate = ReleaseCandidate(
            name="smoke-test",
            attractors={"happy", "fun", "safe"},
            risks=set(),
            has_return_path=True,
            has_privacy_review=True,
            has_operator_approval=True,
            has_behavior_change=True,
        )
        result = evaluate_release(candidate)
        # A fully-bound, risk-free candidate should be allowed.
        self.assertTrue(result.allowed)
        self.assertEqual(result.blockers, ())

    def test_release_gate_blocks_known_high_confidence_risks(self):
        from bettersafe.release_gate import (
            BLOCKING_RISKS,
            ReleaseCandidate,
            evaluate_release,
        )
        # Pick the first blocking risk deterministically.
        risk = sorted(BLOCKING_RISKS)[0]
        candidate = ReleaseCandidate(
            name="unsafe-smoke-test",
            attractors={"happy", "fun", "safe"},
            risks={risk},
            has_return_path=True,
            has_privacy_review=True,
            has_operator_approval=True,
            has_behavior_change=True,
        )
        result = evaluate_release(candidate)
        self.assertFalse(result.allowed)
        # The block reason must name the risk so a reviewer can see why.
        self.assertTrue(any(risk in b for b in result.blockers))

    def test_sensor_policy_blocks_raw_credentials(self):
        from bettersafe.sensor_policy import (
            SensorClass,
            SensorRequest,
            SubjectClass,
            evaluate_sensor_request,
        )
        req = SensorRequest(
            subject=SubjectClass.OPERATOR,
            sensor=SensorClass.RAW_CREDENTIAL,
            explicit_consent=True,
        )
        result = evaluate_sensor_request(req)
        # Even with explicit consent, raw credentials must never be allowed.
        self.assertFalse(result.allowed)


if __name__ == "__main__":
    unittest.main()
