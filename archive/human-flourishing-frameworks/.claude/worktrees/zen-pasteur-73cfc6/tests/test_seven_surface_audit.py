"""Regression test for the lightweight Seven surface audit."""

import unittest

from scripts import seven_surface_audit


class SevenSurfaceAuditTests(unittest.TestCase):
    def test_repo_surfaces_have_required_claim_and_guard_anchors(self):
        self.assertEqual(seven_surface_audit.run_all_checks(), [])

    def test_audit_includes_high_risk_surfaces_from_recent_convergence(self):
        names = {check.name for check in seven_surface_audit.CHECKS}
        self.assertEqual(
            names,
            {
                "public_surface",
                "sensor_taxonomy",
                "public_ux",
                "safe_entrypoint",
            },
        )


if __name__ == "__main__":
    unittest.main()
