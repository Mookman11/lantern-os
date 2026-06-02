#!/usr/bin/env python3
"""Tests for privacy-bounded iPhone Shortcut telemetry sensor."""

import unittest

from phone_telemetry import (
    PhoneShortcutSensor,
    blocked_phone_telemetry_fields,
    sanitize_phone_payload,
)


class PhoneTelemetryTest(unittest.TestCase):
    def test_sanitizes_allowed_coarse_payload(self):
        payload = {
            "device_id": "alex-iphone-001",
            "battery_level": "83%",
            "battery_state": "charging",
            "manual_mode": "working",
            "shortcut_version": "phone-heartbeat-v0.2",
            "operator_note": "manual check-in",
        }

        sanitized = sanitize_phone_payload(payload)

        self.assertEqual(sanitized["device_id"], "alex-iphone-001")
        self.assertEqual(sanitized["battery_level"], 83)
        self.assertEqual(sanitized["battery_state"], "charging")
        self.assertEqual(sanitized["manual_mode"], "working")
        self.assertEqual(sanitized["shortcut_version"], "phone-heartbeat-v0.2")
        self.assertEqual(sanitized["operator_note"], "manual check-in")

    def test_rejects_precise_location_like_fields(self):
        payload = {
            "device_id": "alex-iphone-001",
            "battery_level": 83,
            "latitude": 40.0,
            "longitude": -73.0,
        }

        with self.assertRaises(ValueError) as context:
            sanitize_phone_payload(payload)

        self.assertIn("blocked_device_telemetry_fields", str(context.exception))
        self.assertIn("latitude", str(context.exception))
        self.assertIn("longitude", str(context.exception))

    def test_rejects_health_message_audio_camera_fields(self):
        payload = {
            "device_id": "alex-iphone-001",
            "health_steps": 1000,
            "message_preview": "private",
            "microphone_level": 0.5,
            "camera_frame": "private",
        }

        blocked = blocked_phone_telemetry_fields(payload)

        self.assertEqual(
            blocked,
            ["camera_frame", "health_steps", "message_preview", "microphone_level"],
        )
        with self.assertRaises(ValueError):
            sanitize_phone_payload(payload)

    def test_rejects_unknown_fields_even_when_not_private(self):
        with self.assertRaises(ValueError) as context:
            sanitize_phone_payload({"device_id": "alex-iphone-001", "mood": "great"})

        self.assertIn("unsupported_device_telemetry_fields", str(context.exception))
        self.assertIn("mood", str(context.exception))

    def test_battery_level_out_of_range_becomes_unknown(self):
        sanitized = sanitize_phone_payload({
            "device_id": "alex-iphone-001",
            "battery_level": 120,
            "battery_state": "plugged_into_magic",
            "manual_mode": "hyperdrive",
        })

        self.assertIsNone(sanitized["battery_level"])
        self.assertEqual(sanitized["battery_state"], "unknown")
        self.assertEqual(sanitized["manual_mode"], "unknown")

    def test_phone_shortcut_sensor_emits_generic_device_measurement(self):
        sensor = PhoneShortcutSensor()
        sensor.update_payload({
            "device_id": "alex-iphone-001",
            "battery_level": 77,
            "battery_state": "unplugged",
            "manual_mode": "awake",
            "shortcut_version": "phone-heartbeat-v0.2",
        })

        measurements = sensor.observe()

        self.assertEqual(len(measurements), 1)
        measurement = measurements[0]
        self.assertEqual(measurement.source, "device_client:phone")
        self.assertEqual(measurement.methodology, "operator_approved_device_heartbeat")
        self.assertEqual(measurement.scope, "operator:alex:iphone")
        self.assertEqual(measurement.value["device_kind"], "phone")
        self.assertEqual(measurement.value["device_label"], "Alex iPhone")
        self.assertEqual(measurement.value["battery_level"], 77)
        self.assertEqual(measurement.value["battery_state"], "unplugged")
        self.assertEqual(measurement.value["manual_mode"], "awake")
        self.assertEqual(measurement.value["client_version"], "phone-heartbeat-v0.2")
        self.assertIn("no_precise_location", measurement.missing)
        self.assertIn("manual_mode_self_reported", measurement.confounders)
        self.assertTrue(measurement.measurement_hash)

    def test_phone_shortcut_sensor_reports_error_for_blocked_payload(self):
        sensor = PhoneShortcutSensor(payload_provider=lambda: {
            "device_id": "alex-iphone-001",
            "gps_location": "private",
        })

        self.assertEqual(sensor.observe(), [])
        self.assertEqual(sensor._error_count, 1)
        self.assertIn("gps_location", sensor._last_error)


if __name__ == "__main__":
    unittest.main()
