"""Regression tests for repo-owned deployment strategy."""

from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_START_JSON = "gunicorn safe_app:app --bind 0.0.0.0:$PORT --log-file -"
CANONICAL_START_TOML = "gunicorn safe_app:app --bind 0.0.0.0:${PORT:-5000} --log-file -"


class DeploymentStrategyTests(unittest.TestCase):
    def test_railway_json_uses_safe_app_gunicorn_and_healthz(self):
        data = json.loads((ROOT / "railway.json").read_text(encoding="utf-8"))
        self.assertEqual(data["build"]["builder"], "NIXPACKS")
        self.assertEqual(data["deploy"]["startCommand"], CANONICAL_START_JSON)
        self.assertEqual(data["deploy"]["healthcheckPath"], "/healthz")
        self.assertEqual(data["deploy"]["restartPolicyType"], "ON_FAILURE")
        self.assertNotIn("dashboard_app.py", json.dumps(data))

    def test_railway_toml_uses_safe_app_gunicorn_and_healthz(self):
        text = (ROOT / "railway.toml").read_text(encoding="utf-8")
        self.assertIn('builder = "dockerfile"', text)
        self.assertIn(f'startCommand = "{CANONICAL_START_TOML}"', text)
        self.assertIn('healthcheckPath = "/healthz"', text)
        self.assertIn('restartPolicyType = "ON_FAILURE"', text)
        self.assertNotIn("dashboard_app.py", text)
        self.assertNotIn("python app.py", text)

    def test_dockerfile_defaults_to_safe_app_gunicorn(self):
        text = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn(f"CMD {CANONICAL_START_TOML}", text)
        self.assertNotIn("dashboard_app.py", text)

    def test_render_config_matches_canonical_start(self):
        text = (ROOT / "render.yaml").read_text(encoding="utf-8")
        self.assertIn(f"startCommand: {CANONICAL_START_JSON}", text)
        self.assertNotIn("dashboard_app.py", text)

    def test_deployment_strategy_doc_blocks_stale_commands(self):
        text = (ROOT / "docs" / "deployment-strategy.md").read_text(encoding="utf-8")
        self.assertIn(CANONICAL_START_JSON, text)
        self.assertIn("/healthz", text)
        self.assertIn("python /app/dashboard_app.py", text)
        self.assertIn("not the canonical production target", text)
        self.assertIn("Platform deployment references the expected Git commit", text)


if __name__ == "__main__":
    unittest.main()
