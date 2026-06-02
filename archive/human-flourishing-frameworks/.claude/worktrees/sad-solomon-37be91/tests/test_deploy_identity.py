"""Tests for non-secret deployment identity smoke endpoint."""

import unittest

from deploy_identity import deployment_identity
import safe_app


class DeploymentIdentityTests(unittest.TestCase):
    def test_identity_helper_exposes_non_secret_expected_fields(self):
        identity = deployment_identity()
        self.assertEqual(identity["service"], "human-flourishing-frameworks")
        self.assertEqual(identity["app_version"], "deploy-identity-v1")
        self.assertEqual(identity["expected_entrypoint"], "safe_app:app")
        self.assertEqual(identity["background_status_route"], "/background/status")
        self.assertEqual(identity["health_route"], "/healthz")
        self.assertNotIn("token", str(identity).lower())
        self.assertNotIn("secret", str(identity).lower())

    def test_deployment_identity_route_is_visible(self):
        client = safe_app.app.test_client()
        response = client.get("/deployment/identity")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("deployment", data)
        self.assertEqual(data["deployment"]["app_version"], "deploy-identity-v1")
        self.assertEqual(data["deployment"]["expected_entrypoint"], "safe_app:app")


if __name__ == "__main__":
    unittest.main()
