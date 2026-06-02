#!/usr/bin/env python3
"""Tests for privacy-bounded generic device telemetry sensors."""

import unittest

from device_telemetry import (
    DeviceTelemetrySensor,
    blocked_device_telemetry_fields,
    sanitize_device_payload,
)


class DeviceTelemetryTest(unittest.TestCase):
    def test_sanitizes_phone_watch_laptop_payloads(self):
        examples = [
            {"device_id": "alex-iphone-001", "device_kind": "phone", "device_label": "Alex iPhone"},
            {"device_id": "alex-watch-001", "device_kind": "watch", "device_label": "Alex Watch"},
            {"device_id": "alex-laptop-001", "device_kind": "laptop", "device_label": "Alex Laptop"},
        ]

        for payload in examples:
            with self.subTest(payload=payload):
                sanitized = sanitize_device_payload({
                    **payload,
                    "battery_level": "82%",
                    "battery_state": "charging",
                    "network_state": "wifi",
                    "manual_mode": "working",
                    "client_version": "device-heartbeat-v0.1",
                })

                self.assertEqual(sanitized["device_id"], payload["device_id"])
                self.assertEqual(sanitized["device_kind"], payload["device_kind"])
                self.assertEqual(sanitized["device_label"], payload["device_label"])
                self.assertEqual(sanitized["battery_level"], 82)
                self.assertEqual(sanitized["battery_state"], "charging")
                self.assertEqual(sanitized["network_state"], "wifi")
                self.assertEqual(sanitized["manual_mode"], "working")

    def test_sanitizes_server_and_game_console_payloads(self):
        examples = [
            {"device_id": "hff-pi-001", "device_kind": "raspberry_pi", "device_label": "Desk Pi"},
            {"device_id": "alex-console-001", "device_kind": "game_console", "device_label": "Console"},
            {"device_id": "render-worker-001", "device_kind": "server", "device_label": "Render Worker"},
        ]

        for payload in examples:
            with self.subTest(payload=payload):
                sanitized = sanitize_device_payload({
                    **payload,
                    "power_state": "plugged_in",
                    "network_state": "ethernet",
                    "manual_mode": "idle",
                })

                self.assertEqual(sanitized["device_kind"], payload["device_kind"])
                self.assertEqual(sanitized["power_state"], "plugged_in")
                self.assertEqual(sanitized["network_state"], "ethernet")
                self.assertEqual(sanitized["manual_mode"], "idle")

    def test_rejects_private_device_fields(self):
        payload = {
            "device_id": "alex-watch-001",
            "device_kind": "watch",
            "gps_location": "private",
            "health_steps": 1200,
            "notification_text": "private",
            "bluetooth_nearby_devices": ["private"],
        }

        blocked = blocked_device_telemetry_fields(payload)

        self.assertEqual(
            blocked,
            [
                "bluetooth_nearby_devices",
                "gps_location",
                "health_steps",
                "notification_text",
            ],
        )
        with self.assertRaises(ValueError) as context:
            sanitize_device_payload(payload)
        self.assertIn("blocked_device_telemetry_fields", str(context.exception))

    def test_rejects_unknown_fields(self):
        with self.assertRaises(ValueError) as context:
            sanitize_device_payload({"device_id": "x", "device_kind": "phone", "mood": "great"})

        self.assertIn("unsupported_device_telemetry_fields", str(context.exception))
        self.assertIn("mood", str(context.exception))

    def test_unknown_enum_values_fall_back_to_unknown(self):
        sanitized = sanitize_device_payload({
            "device_id": "x",
            "device_kind": "sentient_toaster",
            "battery_state": "magical",
            "power_state": "quantum",
            "network_state": "telepathy",
            "manual_mode": "superhuman",
        })

        self.assertEqual(sanitized["device_kind"], "unknown")
        self.assertEqual(sanitized["battery_state"], "unknown")
        self.assertEqual(sanitized["power_state"], "unknown")
        self.assertEqual(sanitized["network_state"], "unknown")
        self.assertEqual(sanitized["manual_mode"], "unknown")

    def test_device_telemetry_sensor_emits_measurement(self):
        sensor = DeviceTelemetrySensor(
            sensor_id="alex-laptop-sensor",
            scope="operator:alex:laptop",
        )
        sensor.update_payload({
            "device_id": "alex-laptop-001",
            "device_kind": "laptop",
            "device_label": "Alex Laptop",
            "battery_level": 91,
            "battery_state": "full",
            "power_state": "plugged_in",
            "network_state": "wifi",
            "manual_mode": "working",
            "client_version": "device-heartbeat-v0.1",
        })

        measurements = sensor.observe()

        self.assertEqual(len(measurements), 1)
        measurement = measurements[0]
        self.assertEqual(measurement.scope, "operator:alex:laptop")
        self.assertEqual(measurement.source, "device_client:laptop")
        self.assertEqual(measurement.methodology, "operator_approved_device_heartbeat")
        self.assertEqual(measurement.value["device_kind"], "laptop")
        self.assertEqual(measurement.value["battery_level"], 91)
        self.assertIn("no_precise_location", measurement.missing)
        self.assertIn("no_raw_network_identifiers", measurement.missing)
        self.assertTrue(measurement.measurement_hash)

    def test_device_sensor_records_error_for_blocked_payload(self):
        sensor = DeviceTelemetrySensor(payload_provider=lambda: {
            "device_id": "alex-phone-001",
            "device_kind": "phone",
            "latitude": 1,
        })

        self.assertEqual(sensor.observe(), [])
        self.assertEqual(sensor._error_count, 1)
        self.assertIn("latitude", sensor._last_error)


if __name__ == "__main__":
    unittest.main()
