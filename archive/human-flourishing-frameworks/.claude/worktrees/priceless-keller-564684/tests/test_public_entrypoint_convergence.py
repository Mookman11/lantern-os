"""Convergence guard for public HFF entrypoints.

The public dashboard copy fix must be treated as one coherent release surface,
not as independent legs. These tests prevent Docker, WSGI, and Python startup
paths from drifting apart after the emergency safe_app entrypoint was added.
"""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PublicEntrypointConvergenceTest(unittest.TestCase):
    def test_dockerfile_serves_safe_app(self):
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("gunicorn safe_app:app", dockerfile)
        self.assertNotIn("gunicorn app:app", dockerfile)

    def test_wsgi_imports_safe_app(self):
        wsgi = (ROOT / "wsgi.py").read_text(encoding="utf-8")
        self.assertIn("from safe_app import app", wsgi)
        self.assertNotIn("from app import app", wsgi)

    def test_render_yaml_serves_safe_app(self):
        render_yaml = (ROOT / "render.yaml").read_text(encoding="utf-8")
        self.assertIn("gunicorn safe_app:app", render_yaml)
        self.assertNotIn("gunicorn app:app", render_yaml)

    def test_procfile_serves_safe_app(self):
        procfile = (ROOT / "Procfile").read_text(encoding="utf-8")
        self.assertIn("gunicorn safe_app:app", procfile)
        self.assertNotIn("gunicorn app:app", procfile)

    def test_no_sitecustomize_monkeypatch_path(self):
        self.assertFalse(
            (ROOT / "sitecustomize.py").exists(),
            "Do not use global Python startup monkeypatches for dashboard copy safety.",
        )

    def test_safe_app_contains_public_copy_guard(self):
        safe_app = (ROOT / "safe_app.py").read_text(encoding="utf-8")
        self.assertIn("EXPERIMENTAL ADVISORY AGENTS", safe_app)
        self.assertIn("Escalations are review records only", safe_app)
        self.assertIn("_sanitize_public_template()", safe_app)


if __name__ == "__main__":
    unittest.main()
