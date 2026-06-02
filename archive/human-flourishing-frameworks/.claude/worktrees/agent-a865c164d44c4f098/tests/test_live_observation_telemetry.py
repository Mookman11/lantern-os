#!/usr/bin/env python3
"""Tests for the live observation telemetry contract."""

import unittest

from live_observation_telemetry import (
    LiveObservationTelemetry,
    classify_belief_data_mode,
    summarize_belief_activity,
    STATUS_FAILED,
    STATUS_NOT_ENABLED,
    STATUS_RAN_NO_MEASUREMENTS,
    STATUS_RAN_WITH_MEASUREMENTS_NO_UPDATES,
    STATUS_RAN_WITH_UPDATES,
    STATUS_REGISTERED_NOT_RUN,
    STATUS_RUNNING,
)


class LiveObservationTelemetryTest(unittest.TestCase):
    def test_disabled_state_is_explicit(self):
        telemetry = LiveObservationTelemetry()

        self.assertEqual(telemetry.status_reason(), STATUS_NOT_ENABLED)
        payload = telemetry.to_dict()
        self.assertFalse(payload["enabled"])
        self.assertTrue(payload["best_effort"])
        self.assertEqual(payload["data_mode"], "best_effort")

    def test_enabled_but_not_run_is_distinct_from_no_corrections(self):
        telemetry = LiveObservationTelemetry()
        telemetry.mark_enabled(sensor_count=9)

        self.assertEqual(telemetry.status_reason(), STATUS_REGISTERED_NOT_RUN)
        payload = telemetry.to_dict()
        self.assertTrue(payload["enabled"])
        self.assertEqual(payload["sensor_count"], 9)
        self.assertEqual(payload["observation_count"], 0)
        self.assertEqual(payload["last_correction_count"], 0)

    def test_started_first_observation_reports_running(self):
        telemetry = LiveObservationTelemetry()
        telemetry.mark_enabled(sensor_count=9)
        telemetry.start_observation()

        self.assertEqual(telemetry.status_reason(), STATUS_RUNNING)
        payload = telemetry.to_dict()
        self.assertEqual(payload["status_reason"], STATUS_RUNNING)
        self.assertEqual(payload["observation_count"], 0)
        self.assertIsNotNone(payload["last_observation_started_at"])
        self.assertIsNone(payload["last_observation_finished_at"])

    def test_run_with_zero_measurements_is_explicit(self):
        telemetry = LiveObservationTelemetry(enabled=True, sensor_count=9)
        telemetry.start_observation()
        telemetry.finish_observation(
            measurement_count=0,
            update_count=0,
            correction_count=0,
        )

        self.assertEqual(telemetry.status_reason(), STATUS_RAN_NO_MEASUREMENTS)
        payload = telemetry.to_dict()
        self.assertEqual(payload["observation_count"], 1)
        self.assertEqual(payload["last_measurement_count"], 0)
        self.assertEqual(payload["last_update_count"], 0)
        self.assertEqual(payload["last_correction_count"], 0)
        self.assertIsNotNone(payload["last_observation_finished_at"])

    def test_run_with_measurements_but_no_updates_is_explicit(self):
        telemetry = LiveObservationTelemetry(enabled=True, sensor_count=9)
        telemetry.start_observation()
        telemetry.finish_observation(
            measurement_count=9,
            update_count=0,
            correction_count=0,
        )

        self.assertEqual(
            telemetry.status_reason(),
            STATUS_RAN_WITH_MEASUREMENTS_NO_UPDATES,
        )
        payload = telemetry.to_dict()
        self.assertEqual(payload["last_measurement_count"], 9)
        self.assertEqual(payload["last_update_count"], 0)
        self.assertEqual(payload["last_correction_count"], 0)

    def test_run_with_updates_and_zero_corrections_is_not_ambiguous(self):
        telemetry = LiveObservationTelemetry(enabled=True, sensor_count=9)
        telemetry.start_observation()
        telemetry.finish_observation(
            measurement_count=9,
            update_count=9,
            correction_count=0,
        )

        self.assertEqual(telemetry.status_reason(), STATUS_RAN_WITH_UPDATES)
        payload = telemetry.to_dict()
        self.assertEqual(payload["last_measurement_count"], 9)
        self.assertEqual(payload["last_update_count"], 9)
        self.assertEqual(payload["last_correction_count"], 0)
        self.assertEqual(payload["last_error_count"], 0)

    def test_failure_is_not_silent(self):
        telemetry = LiveObservationTelemetry(enabled=True, sensor_count=9)
        telemetry.start_observation()
        telemetry.record_failure("world bank timeout")

        self.assertEqual(telemetry.status_reason(), STATUS_FAILED)
        payload = telemetry.to_dict()
        self.assertEqual(payload["last_error_count"], 1)
        self.assertEqual(payload["last_errors"], ["world bank timeout"])
        self.assertEqual(payload["last_measurement_count"], 0)
        self.assertEqual(payload["last_update_count"], 0)

    def test_belief_activity_counts_seeded_and_live_updated(self):
        beliefs = {
            "humans:health:seeded": object(),
            "humans:health:live": object(),
            "ecosystems:stability:seeded": object(),
        }

        summary = summarize_belief_activity(
            beliefs,
            live_updated_entities={"humans:health:live", "missing:key"},
        )

        self.assertEqual(summary["belief_count"], 3)
        self.assertEqual(summary["live_updated_belief_count"], 1)
        self.assertEqual(summary["seeded_only_belief_count"], 2)

    def test_belief_data_mode_never_claims_verified(self):
        seeded = classify_belief_data_mode("humans:health:seeded")
        live = classify_belief_data_mode(
            "humans:health:live",
            live_updated_entities={"humans:health:live"},
        )

        self.assertEqual(seeded["data_mode"], "seeded_baseline")
        self.assertTrue(seeded["best_effort"])
        self.assertEqual(live["data_mode"], "live_best_effort")
        self.assertTrue(live["best_effort"])
        self.assertNotEqual(live["data_mode"], "live_verified")


if __name__ == "__main__":
    unittest.main()
