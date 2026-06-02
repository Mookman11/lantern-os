"""Tests for the safe public UI baseline.

These checks keep the public dashboard readable and assistive-technology
friendly without adding new runtime capability.
"""

import unittest

import safe_app


class PublicUiBaselineTests(unittest.TestCase):
    def setUp(self):
        self.client = safe_app.app.test_client()

    def test_public_html_declares_current_language_and_direction(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn('<html lang="en" dir="ltr">', text)

    def test_public_html_has_skip_link_and_main_landmark(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn('href="#main-content"', text)
        self.assertIn('id="main-content"', text)
        self.assertIn('<main ', text)
        self.assertIn('</main>', text)

    def test_public_html_preserves_advisory_boundary(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn("Research Software", text)
        self.assertIn(
            "not a human board, regulator, court, enforcement system, or autonomous authority",
            text,
        )
        self.assertNotIn("ALGORITHMIC GOVERNANCE", text)
        self.assertNotIn("irreversible after a 24-hour lock", text)

    def test_public_sensor_copy_separates_live_state_from_definitions(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn('live sensors: <span id="wm-live-sensors-header">checking</span>', text)
        self.assertIn("Public runtime sensor state comes from /healthz", text)
        self.assertIn("Runtime Sensor Sources", text)
        self.assertIn(
            "sensor definitions available. Live observation remains disabled unless explicitly enabled.",
            text,
        )
        self.assertNotIn('id="wm-sensor-count-header"', text)
        self.assertNotIn("sensors registered. Waiting for first observation cycle", text)

    def test_public_dashboard_is_not_cached(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("no-store", response.headers.get("Cache-Control", ""))
        self.assertEqual(response.headers.get("Pragma"), "no-cache")
        self.assertEqual(response.headers.get("Expires"), "0")

    def test_bettersafe_pilot_interaction_panel_is_present(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn('id="bettersafe-pilot-panel"', text)
        self.assertIn("BetterSafe Pilot Interaction Screen", text)
        self.assertIn("CONTROLLED LIMITED PILOT ONLY", text)
        self.assertIn("This screen is a local, deterministic guide.", text)
        self.assertIn("not a chatbot, not an LLM endpoint, not autonomous", text)
        self.assertIn("Build local BetterSafe packet", text)

    def test_bettersafe_panel_lists_best_case_interactions(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        required = [
            "Claim Audit",
            "Source Check",
            "Low-Risk Next Step",
            "Confidence Table",
            "Scientific Convergence",
            "Creative Door Scene",
            "High-impact downgrade / blocked request",
        ]
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_bettersafe_packet_builder_is_local_only(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn("This builder runs in the browser only. It formats the request for operator review and does not submit data.", text)
        self.assertIn("BETTERSAFE CONTROLLED LIMITED PILOT PACKET", text)
        self.assertIn("Boundary: not medical/legal/financial/emergency/surveillance/child-facing/autonomous authority", text)
        self.assertIn("Correction path: CORRECTED | RETRACTED | UNKNOWN | BLOCKED", text)
        self.assertIn("Control path: pause | stop | correct | retract | revoke", text)
        self.assertNotIn("fetch('/bettersafe", text)
        self.assertNotIn('action="/bettersafe', text)
        self.assertNotIn("XMLHttpRequest", text)

    def test_iphone_home_screen_shell_is_advertised_without_native_permissions(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn('rel="manifest" href="/manifest.webmanifest"', text)
        self.assertIn('name="apple-mobile-web-app-capable" content="yes"', text)
        self.assertIn('name="apple-mobile-web-app-title" content="BetterSafe"', text)
        self.assertIn('rel="apple-touch-icon" href="/bettersafe-icon.svg"', text)
        self.assertIn("open this dashboard in Safari, tap <strong>Share</strong>, then <strong>Add to Home Screen</strong>", text)
        self.assertIn("without App Store permissions, background collection, or native telemetry", text)

    def test_pwa_manifest_is_safe_home_screen_shell(self):
        response = self.client.get("/manifest.webmanifest")
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/manifest+json", response.headers.get("Content-Type", ""))
        manifest = response.get_json()
        self.assertEqual(manifest["name"], "BetterSafe Pilot")
        self.assertEqual(manifest["short_name"], "BetterSafe")
        self.assertEqual(manifest["start_url"], "/?surface=bettersafe-pilot")
        self.assertEqual(manifest["display"], "standalone")
        self.assertIn("no chatbot", manifest["description"])
        self.assertIn("no LLM endpoint", manifest["description"])
        self.assertIn("no public writes", manifest["description"])
        self.assertEqual(manifest["icons"][0]["src"], "/bettersafe-icon.svg")

    def test_bettersafe_icon_is_local_svg(self):
        response = self.client.get("/bettersafe-icon.svg")
        self.assertEqual(response.status_code, 200)
        self.assertIn("image/svg+xml", response.headers.get("Content-Type", ""))
        text = response.get_data(as_text=True)
        self.assertIn("<svg", text)
        self.assertIn("BetterSafe Pilot icon", text)


if __name__ == "__main__":
    unittest.main()
