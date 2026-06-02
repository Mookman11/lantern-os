import unittest
from unittest.mock import patch

from health_probe import (
    DEFAULT_HEALTH_PATHS,
    probe_health,
    probe_endpoint,
)


class _FakeResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


@patch("health_probe.urlopen", return_value=_FakeResponse())
def test_probe_endpoint_success(mock_urlopen):
    result = probe_endpoint(
        "https://example.com",
        "/health",
    )

    assert result.ok is True
    assert result.status_code == 200
    assert result.path == "/health"


@patch("health_probe.urlopen", side_effect=OSError("offline"))
def test_probe_endpoint_handles_network_error(mock_urlopen):
    result = probe_endpoint(
        "https://example.com",
        "/health",
    )

    assert result.ok is False
    assert result.error == "OSError"


def test_probe_requires_allowlisted_path():
    with unittest.TestCase().assertRaises(ValueError):
        probe_endpoint(
            "https://example.com",
            "/admin/reset-all",
        )


@patch("health_probe.urlopen", return_value=_FakeResponse())
def test_probe_health_reports_read_only_limits(mock_urlopen):
    result = probe_health(
        "https://example.com",
        paths=("/health", "/healthz"),
    )

    assert result["ok"] is True
    assert result["ok_count"] == 2

    limits = result["limits"]

    assert limits["read_only"] is True
    assert limits["writes"] is False
    assert limits["tokens"] is False
    assert limits["mesh_sync"] is False
    assert limits["live_sensors"] is False
    assert limits["background_worker"] is False


def test_default_paths_are_read_only_health_paths():
    assert "/api/better-next/status" in DEFAULT_HEALTH_PATHS
    assert "/api/adoption/stats" in DEFAULT_HEALTH_PATHS
