#!/usr/bin/env python3
"""Tests for live sensor observation-loop telemetry wiring."""

import threading
import unittest

from live_observation_telemetry import (
    STATUS_FAILED,
    STATUS_RAN_NO_MEASUREMENTS,
    STATUS_RAN_WITH_UPDATES,
    LiveObservationTelemetry,
)
from live_sensors import run_observation_loop
from sensors import Measurement


class DummyRegistry:
    def __init__(self, stop_event, measurements=None, error=None):
        self.sensor_count = 1
        self._stop_event = stop_event
        self._measurements = list(measurements or [])
        self._error = error

    def observe_all(self):
        self._stop_event.set()
        if self._error:
            raise self._error
        return self._measurements


class DummyWorldModel:
    def __init__(self, updates=None):
        self.correction_log = []
        self.live_updated_entities = set()
        self._updates = list(updates or [])

    def update(self, measurements):
        return self._updates


class LiveSensorTelemetryWiringTest(unittest.TestCase):
    def test_observation_loop_records_measurement_and_update_counts(self):
        stop_event = threading.Event()
        measurement = Measurement(
            value=0.7,
            uncertainty=0.2,
            confidence_interval=(0.6, 0.8),
            source="test-live-source",
            methodology="test",
            scope="humans:health",
        )
        update = {
            "entity": "humans:health:test-live-source",
            "posterior": 0.66,
            "uncertainty": 0.18,
        }
        registry = DummyRegistry(stop_event, measurements=[measurement])
        world_model = DummyWorldModel(updates=[update])
        telemetry = LiveObservationTelemetry()

        run_observation_loop(
            registry,
            world_model,
            interval_seconds=0,
            stop_event=stop_event,
            telemetry=telemetry,
        )

        payload = telemetry.to_dict()
        self.assertEqual(payload["status_reason"], STATUS_RAN_WITH_UPDATES)
        self.assertEqual(payload["sensor_count"], 1)
        self.assertEqual(payload["observation_count"], 1)
        self.assertEqual(payload["last_measurement_count"], 1)
        self.assertEqual(payload["last_update_count"], 1)
        self.assertEqual(payload["last_correction_count"], 0)
        self.assertEqual(payload["last_error_count"], 0)
        self.assertIn(update["entity"], world_model.live_updated_entities)
        self.assertIs(world_model.live_observation_telemetry, telemetry)

    def test_observation_loop_records_no_measurements(self):
        stop_event = threading.Event()
        registry = DummyRegistry(stop_event, measurements=[])
        world_model = DummyWorldModel()
        telemetry = LiveObservationTelemetry()

        run_observation_loop(
            registry,
            world_model,
            interval_seconds=0,
            stop_event=stop_event,
            telemetry=telemetry,
        )

        payload = telemetry.to_dict()
        self.assertEqual(payload["status_reason"], STATUS_RAN_NO_MEASUREMENTS)
        self.assertEqual(payload["observation_count"], 1)
        self.assertEqual(payload["last_measurement_count"], 0)
        self.assertEqual(payload["last_update_count"], 0)
        self.assertEqual(payload["last_error_count"], 0)

    def test_observation_loop_records_failures(self):
        stop_event = threading.Event()
        registry = DummyRegistry(stop_event, error=RuntimeError("sensor timeout"))
        world_model = DummyWorldModel()
        telemetry = LiveObservationTelemetry()

        run_observation_loop(
            registry,
            world_model,
            interval_seconds=0,
            stop_event=stop_event,
            telemetry=telemetry,
        )

        payload = telemetry.to_dict()
        self.assertEqual(payload["status_reason"], STATUS_FAILED)
        self.assertEqual(payload["observation_count"], 1)
        self.assertEqual(payload["last_error_count"], 1)
        self.assertEqual(payload["last_errors"], ["sensor timeout"])
        self.assertEqual(payload["last_measurement_count"], 0)
        self.assertEqual(payload["last_update_count"], 0)


if __name__ == "__main__":
    unittest.main()
