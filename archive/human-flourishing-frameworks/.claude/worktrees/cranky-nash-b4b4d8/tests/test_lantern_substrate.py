"""Lantern substrate wiring tests."""

import json
import os
import unittest
from unittest import mock

import requests


class FakeAnthropicResponse:
    def __init__(self, payload, status_code=200, reason="OK"):
        self._payload = payload
        self.status_code = status_code
        self.reason = reason

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}", response=self)

    def json(self):
        return self._payload


class LanternSubstrateTests(unittest.TestCase):
    def setUp(self):
        from lantern import server as lantern_server

        self.lantern_server = lantern_server
        lantern_server.app.config["TESTING"] = True
        lantern_server.app.config["ALLOW_SUBSTRATE_IN_TESTS"] = False
        self.client = lantern_server.app.test_client()

    def tearDown(self):
        self.lantern_server.app.config["ALLOW_SUBSTRATE_IN_TESTS"] = False

    def test_test_mode_blocks_real_substrate_even_with_key(self):
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "unit-test-token"}, clear=False):
            response = self.client.post(
                "/api/lantern/chat",
                data=json.dumps({"message": "hello"}),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "degraded")
        self.assertIn("server substrate is not available", data.get("reply", ""))
        self.assertIn("no local LLM is being claimed", data.get("reply", ""))

    def test_mocked_substrate_call_returns_reply_when_explicitly_enabled(self):
        self.lantern_server.app.config["ALLOW_SUBSTRATE_IN_TESTS"] = True
        fake_payload = {
            "content": [
                {"type": "text", "text": "State observed: test substrate replied."}
            ]
        }

        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "unit-test-token"}, clear=False), \
             mock.patch("lantern.server.requests.post") as post:
            post.return_value = FakeAnthropicResponse(fake_payload)
            response = self.client.post(
                "/api/lantern/chat",
                data=json.dumps({"message": "hello substrate"}),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "ok")
        self.assertEqual(data.get("role"), "Lantern Keystone Wish")
        self.assertIn("test substrate replied", data.get("reply", ""))
        self.assertEqual(data.get("user_message_received"), "hello substrate")

        post.assert_called_once()
        _, kwargs = post.call_args
        self.assertIn("headers", kwargs)
        self.assertIn("json", kwargs)
        self.assertEqual(kwargs["json"]["messages"][0]["content"], "hello substrate")
        self.assertIn("system", kwargs["json"])
        self.assertIn("Show the state", kwargs["json"]["system"])

        self.assertEqual(kwargs["headers"].get("x-api-key"), "unit-test-token")
        self.assertNotIn("unit-test-token", json.dumps(kwargs["json"]))
        self.assertNotIn("unit-test-token", json.dumps(data))

    def test_substrate_error_returns_safe_diagnostic_payload(self):
        self.lantern_server.app.config["ALLOW_SUBSTRATE_IN_TESTS"] = True

        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "unit-test-token"}, clear=False), \
             mock.patch(
                 "lantern.server.requests.post",
                 return_value=FakeAnthropicResponse({"error": "redacted"}, status_code=401, reason="Unauthorized"),
             ):
            response = self.client.post(
                "/api/lantern/chat",
                data=json.dumps({"message": "hello substrate"}),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 502)
        data = response.get_json()
        self.assertEqual(data.get("status"), "substrate_error")
        self.assertIn("configured anthropic substrate failed at HTTP 401", data.get("reply", ""))
        self.assertIn("no secret inspection", data.get("reply", ""))
        self.assertIn("no provider switch", data.get("reply", ""))

        detail = data.get("substrate_error") or {}
        self.assertEqual(detail.get("provider"), "anthropic")
        self.assertEqual(detail.get("http_status_code"), 401)
        self.assertEqual(detail.get("http_status_family"), "4xx")
        self.assertEqual(detail.get("http_reason"), "Unauthorized")
        self.assertTrue(detail.get("secret_safe"))
        self.assertFalse(detail.get("hidden_retry"))
        self.assertFalse(detail.get("action_taken"))
        self.assertFalse(detail.get("body_included"))
        self.assertNotIn("unit-test-token", json.dumps(data))

    def test_substrate_timeout_returns_safe_classification_without_status(self):
        self.lantern_server.app.config["ALLOW_SUBSTRATE_IN_TESTS"] = True

        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "unit-test-token"}, clear=False), \
             mock.patch("lantern.server.requests.post", side_effect=TimeoutError("timeout")):
            response = self.client.post(
                "/api/lantern/chat",
                data=json.dumps({"message": "hello substrate"}),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 502)
        data = response.get_json()
        detail = data.get("substrate_error") or {}
        self.assertEqual(detail.get("error_class"), "TimeoutError")
        self.assertIsNone(detail.get("http_status_code"))
        self.assertEqual(detail.get("http_status_family"), "unknown")
        self.assertIn("no hidden retry", data.get("reply", ""))

    def test_empty_chat_message_is_rejected_without_substrate_call(self):
        self.lantern_server.app.config["ALLOW_SUBSTRATE_IN_TESTS"] = True
        with mock.patch("lantern.server.requests.post") as post:
            response = self.client.post(
                "/api/lantern/chat",
                data=json.dumps({"message": "   "}),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json().get("status"), "empty")
        post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
