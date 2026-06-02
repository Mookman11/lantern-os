"""Safe public WSGI entrypoint for Human Flourishing Frameworks.

This module imports the existing Flask app and sanitizes a known misleading
public dashboard banner before the app is served. It does not change endpoints,
auth, agents, sensors, mesh sync, secrets, databases, or deployment settings
beyond the Dockerfile choosing this entrypoint.

The underlying app.py template should still be corrected directly in a follow-up
PR. This file is an emergency public-copy guard for the live service.
"""

from __future__ import annotations

import app as _app_module


def _sanitize_public_template() -> None:
    template = getattr(_app_module, "HTML_TEMPLATE", "")
    if not isinstance(template, str):
        return

    advisory_banner = (
        "<strong>EXPERIMENTAL ADVISORY AGENTS</strong> &mdash; Research/demo agents\n"
        "                expose advisory workflow status and audit records. They are not a\n"
        "                human board, regulator, court, enforcement system, or autonomous authority.\n"
        "                Escalations are review records only unless explicitly authorized by an operator."
    )

    replacements = (
        (
            "<!-- AUTONOMOUS GOVERNANCE (collapsed by default) -->",
            "<!-- ADVISORY AGENT STATUS (collapsed by default) -->",
        ),
        (
            "Autonomous Governance",
            "Advisory Agent Status",
        ),
        (
            "<strong>ALGORITHMIC GOVERNANCE</strong> &mdash; 7 autonomous agents\n"
            "                coordinate through PBFT consensus. No human board. Escalations are\n"
            "                irreversible after a 24-hour lock.",
            advisory_banner,
        ),
        (
            "<strong>ALGORITHMIC GOVERNANCE</strong>",
            "<strong>EXPERIMENTAL ADVISORY AGENTS</strong>",
        ),
        (
            "No human board.",
            "Operator review required.",
        ),
        (
            "Escalations are irreversible after a 24-hour lock.",
            "Escalations are review records only unless explicitly authorized by an operator.",
        ),
        (
            "irreversible after a 24-hour lock.",
            "not executable unless explicitly authorized by an operator.",
        ),
    )

    for old, new in replacements:
        template = template.replace(old, new)

    _app_module.HTML_TEMPLATE = template


_sanitize_public_template()

app = _app_module.app

if __name__ == "__main__":
    app.run()
