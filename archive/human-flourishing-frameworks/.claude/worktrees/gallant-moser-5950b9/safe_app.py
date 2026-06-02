"""Safe public WSGI entrypoint for Human Flourishing Frameworks.

This module imports the existing Flask app and sanitizes known misleading or
incomplete public dashboard markup before the app is served. It does not change
endpoints, auth, agents, sensors, mesh sync, secrets, databases, or deployment
settings beyond the deployment choosing this entrypoint.

The underlying app.py template should still be corrected directly in follow-up
work. This file is a public-copy and presentation guard for the live service.
"""

from __future__ import annotations

from flask import jsonify, Response

import app as _app_module
from background_mode import create_background_controller_from_env
from deploy_identity import deployment_identity


_ADVISORY_BANNER = (
    "<strong>EXPERIMENTAL ADVISORY AGENTS</strong> &mdash; Research/demo agents\n"
    "                expose advisory workflow status and audit records. They are not a\n"
    "                human board, regulator, court, enforcement system, or autonomous authority.\n"
    "                Escalations are review records only unless explicitly authorized by an operator."
)

_PWA_MANIFEST = {
    "name": "BetterSafe Pilot",
    "short_name": "BetterSafe",
    "description": "Controlled limited BetterSafe pilot dashboard. Local packet builder only; no chatbot, no LLM endpoint, no public writes.",
    "start_url": "/?surface=bettersafe-pilot",
    "scope": "/",
    "display": "standalone",
    "background_color": "#0f0c29",
    "theme_color": "#00ff88",
    "orientation": "portrait-primary",
    "categories": ["utilities", "productivity"],
    "icons": [
        {
            "src": "/bettersafe-icon.svg",
            "sizes": "any",
            "type": "image/svg+xml",
            "purpose": "any maskable",
        }
    ],
}

_BETTERSAFE_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-label="BetterSafe Pilot icon">
  <rect width="512" height="512" rx="96" fill="#0f0c29"/>
  <circle cx="256" cy="256" r="170" fill="none" stroke="#00ff88" stroke-width="28"/>
  <path d="M256 110 L356 402 L256 342 L156 402 Z" fill="#00ffff" opacity="0.92"/>
  <circle cx="256" cy="256" r="36" fill="#ffcc00"/>
</svg>
"""

_SKIP_LINK_CSS = """
        .skip-link {
            position: absolute;
            left: 12px;
            top: -48px;
            background: #ffffff;
            color: #111111;
            padding: 10px 14px;
            border-radius: 6px;
            z-index: 1000;
        }
        .skip-link:focus { top: 12px; }
"""

_IPHONE_APP_META = """
    <meta name="theme-color" content="#00ff88">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-title" content="BetterSafe">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="mobile-web-app-capable" content="yes">
    <link rel="manifest" href="/manifest.webmanifest">
    <link rel="icon" type="image/svg+xml" href="/bettersafe-icon.svg">
    <link rel="apple-touch-icon" href="/bettersafe-icon.svg">
"""

_BETTERSAFE_PILOT_CSS = """
        .bettersafe-pilot-panel {
            background: rgba(26, 31, 74, 0.86);
            border: 1px solid rgba(0, 255, 136, 0.38);
            border-radius: 12px;
            padding: 22px;
            margin: 26px 0 36px 0;
        }
        .bettersafe-pilot-panel h2 { margin-top: 0; }
        .bettersafe-mode-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 12px;
            margin: 14px 0;
        }
        .bettersafe-mode-card {
            background: rgba(0, 0, 0, 0.16);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 10px;
            padding: 14px;
        }
        .bettersafe-mode-card strong { color: #00ffff; }
        .bettersafe-mode-card p { color: #bbb; font-size: 13px; margin-top: 6px; }
        .bettersafe-interaction-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 14px;
            margin: 18px 0;
        }
        .bettersafe-interaction-card {
            background: rgba(0, 255, 136, 0.06);
            border: 1px solid rgba(0, 255, 136, 0.22);
            border-radius: 10px;
            padding: 14px;
        }
        .bettersafe-interaction-card h3 { color: #00ff88; font-size: 15px; }
        .bettersafe-interaction-card ul { margin: 10px 0 0 18px; color: #bbb; font-size: 13px; }
        .bettersafe-local-builder {
            background: rgba(0, 0, 0, 0.18);
            border: 1px solid rgba(255, 204, 0, 0.28);
            border-radius: 10px;
            padding: 16px;
            margin-top: 18px;
        }
        .bettersafe-local-builder label { display: block; color: #ddd; font-size: 13px; margin: 10px 0 5px; }
        .bettersafe-local-builder input,
        .bettersafe-local-builder textarea,
        .bettersafe-local-builder select {
            width: 100%;
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.06);
            color: #f0f0f0;
            padding: 10px;
            font: inherit;
        }
        .bettersafe-local-builder textarea { min-height: 74px; resize: vertical; }
        .bettersafe-local-builder button {
            margin-top: 12px;
            background: rgba(0, 255, 136, 0.18);
            border: 1px solid #00ff88;
            color: #00ff88;
            border-radius: 8px;
            padding: 10px 14px;
            font-weight: bold;
            cursor: pointer;
        }
        .bettersafe-packet-output {
            white-space: pre-wrap;
            background: rgba(0, 0, 0, 0.25);
            border: 1px solid rgba(0, 255, 136, 0.2);
            border-radius: 8px;
            padding: 12px;
            margin-top: 12px;
            color: #d7ffe8;
            font-size: 13px;
            min-height: 120px;
        }
"""

_BETTERSAFE_PILOT_HTML = """
        <!-- ============================================================ -->
        <!-- BETTERSAFE PILOT INTERACTION SCREEN -->
        <!-- ============================================================ -->
        <section id="bettersafe-pilot-panel" class="bettersafe-pilot-panel" aria-labelledby="bettersafe-pilot-title">
            <h2 id="bettersafe-pilot-title" style="color: #00ff88;">BetterSafe Pilot Interaction Screen</h2>
            <div class="section-banner banner-green">
                <strong>CONTROLLED LIMITED PILOT ONLY</strong> &mdash; This screen is a local, deterministic guide.
                It is not a chatbot, not an LLM endpoint, not autonomous, and not a public-write surface.
                Use it to convert a request into a bounded BetterSafe packet for human review.
            </div>
            <div class="section-banner banner-yellow">
                iPhone path: open this dashboard in Safari, tap <strong>Share</strong>, then <strong>Add to Home Screen</strong>.
                This creates an app-like launcher without App Store permissions, background collection, or native telemetry.
            </div>
            <div class="section-banner banner-yellow">
                Mode starts as <strong>LIMITED_CHAT_LOCAL</strong> unless the operator explicitly verifies
                <strong>FULL_REPO_GROUNDED</strong>. High-impact requests are blocked or downgraded.
            </div>

            <div class="bettersafe-mode-row" aria-label="BetterSafe pilot boundaries">
                <div class="bettersafe-mode-card">
                    <strong>Included</strong>
                    <p>Claim audit, source-checking, repo/docs reasoning, low-risk planning, education, confidence labels, scientific-method convergence, and bounded fiction-labeled creative play.</p>
                </div>
                <div class="bettersafe-mode-card">
                    <strong>Blocked</strong>
                    <p>Medical, legal, financial, emergency, child-facing, surveillance, public-write, payment, live-sensor, autonomous, physical-control, or identity-continuity authority.</p>
                </div>
                <div class="bettersafe-mode-card">
                    <strong>Control path</strong>
                    <p>Pause, stop, correct, retract, mark unknown, revoke, or open the correction ledger before relying on an answer.</p>
                </div>
            </div>

            <div class="bettersafe-interaction-grid" aria-label="Best-case BetterSafe interactions">
                <div class="bettersafe-interaction-card">
                    <h3>1. Claim Audit</h3>
                    <ul>
                        <li>State one narrow claim.</li>
                        <li>Choose a claim label.</li>
                        <li>List sources or mark unknown.</li>
                        <li>Record correction path.</li>
                    </ul>
                </div>
                <div class="bettersafe-interaction-card">
                    <h3>2. Source Check</h3>
                    <ul>
                        <li>Ask: where did this come from?</li>
                        <li>Compare official/repo/test evidence.</li>
                        <li>Downgrade stale or unsupported claims.</li>
                        <li>Never treat confidence as proof.</li>
                    </ul>
                </div>
                <div class="bettersafe-interaction-card">
                    <h3>3. Low-Risk Next Step</h3>
                    <ul>
                        <li>Define the reversible action.</li>
                        <li>Name the risk and stop condition.</li>
                        <li>Keep human control visible.</li>
                        <li>Do not widen scope silently.</li>
                    </ul>
                </div>
                <div class="bettersafe-interaction-card">
                    <h3>4. Confidence Table</h3>
                    <ul>
                        <li>Use reliance estimates only.</li>
                        <li>Separate fact, inference, and speculation.</li>
                        <li>Show what would change the score.</li>
                        <li>Correct or retract overclaims.</li>
                    </ul>
                </div>
                <div class="bettersafe-interaction-card">
                    <h3>5. Scientific Convergence</h3>
                    <ul>
                        <li>State hypothesis.</li>
                        <li>Define measurement and falsifier.</li>
                        <li>Observe evidence.</li>
                        <li>Converge only after correction.</li>
                    </ul>
                </div>
                <div class="bettersafe-interaction-card">
                    <h3>6. Creative Door Scene</h3>
                    <ul>
                        <li>Label fiction explicitly.</li>
                        <li>Keep return control.</li>
                        <li>No proof, memory, or authority claims.</li>
                        <li>Close or pause on request.</li>
                    </ul>
                </div>
            </div>

            <div class="bettersafe-local-builder" aria-label="Local BetterSafe packet builder">
                <h3 style="color: #ffcc00;">Local packet builder &mdash; no network write</h3>
                <p style="color: #bbb; font-size: 13px; margin-top: 6px;">
                    This builder runs in the browser only. It formats the request for operator review and does not submit data.
                </p>
                <label for="bettersafe-task-type">Interaction type</label>
                <select id="bettersafe-task-type">
                    <option>Claim audit</option>
                    <option>Source check</option>
                    <option>Low-risk next step</option>
                    <option>Confidence table</option>
                    <option>Scientific convergence</option>
                    <option>Creative door scene</option>
                    <option>High-impact downgrade / blocked request</option>
                </select>

                <label for="bettersafe-request-text">Request or claim</label>
                <textarea id="bettersafe-request-text" placeholder="Write one narrow request or claim. Avoid private data unless needed."></textarea>

                <label for="bettersafe-grounding-mode">Grounding mode</label>
                <select id="bettersafe-grounding-mode">
                    <option>LIMITED_CHAT_LOCAL</option>
                    <option>FULL_REPO_GROUNDED</option>
                    <option>UNAVAILABLE_OR_DEGRADED</option>
                </select>

                <label for="bettersafe-claim-label">Claim label</label>
                <select id="bettersafe-claim-label">
                    <option>UNKNOWN</option>
                    <option>FACT_SOURCE_BACKED</option>
                    <option>FACT_OPERATOR_REPORTED</option>
                    <option>INFERENCE</option>
                    <option>HEURISTIC_CONFIDENCE</option>
                    <option>SPECULATION</option>
                    <option>CORRECTED</option>
                    <option>RETRACTED</option>
                    <option>BLOCKED</option>
                </select>

                <label for="bettersafe-sources-text">Sources or evidence to check</label>
                <textarea id="bettersafe-sources-text" placeholder="Repo file, issue, PR, test, log, official source, or UNKNOWN."></textarea>

                <button type="button" id="bettersafe-build-packet">Build local BetterSafe packet</button>
                <pre id="bettersafe-packet-output" class="bettersafe-packet-output">Choose a type and build a local packet. Nothing is submitted.</pre>
            </div>
        </section>
"""

_HEALTHZ_SENSOR_STATUS_JS = """
        // Public runtime sensor state comes from /healthz, not from the
        // world-model registry count. This keeps sensor definitions separate
        // from live observation.
        fetch('/healthz')
            .then(r => r.json())
            .then(data => {
                const el = document.getElementById('wm-live-sensors-header');
                if (!el) return;
                el.textContent = data.live_sensors_enabled ? 'enabled' : 'disabled';
            })
            .catch(() => {
                const el = document.getElementById('wm-live-sensors-header');
                if (el) el.textContent = 'check /healthz';
            });
"""

_BETTERSAFE_PILOT_JS = """
        // BetterSafe packet builder is local-only. It makes no fetch/XHR call
        // and does not submit data. It formats a bounded pilot request for
        // human/operator review.
        function buildBetterSafePacket() {
            const type = document.getElementById('bettersafe-task-type')?.value || 'Claim audit';
            const requestText = document.getElementById('bettersafe-request-text')?.value || 'UNSPECIFIED';
            const mode = document.getElementById('bettersafe-grounding-mode')?.value || 'LIMITED_CHAT_LOCAL';
            const label = document.getElementById('bettersafe-claim-label')?.value || 'UNKNOWN';
            const sources = document.getElementById('bettersafe-sources-text')?.value || 'UNKNOWN';
            const output = [
                'BETTERSAFE CONTROLLED LIMITED PILOT PACKET',
                'Mode: ' + mode,
                'Interaction type: ' + type,
                'Scope: low-risk unless high-impact terms require downgrade/block',
                'Claim label: ' + label,
                'Request/claim: ' + requestText,
                'Sources/evidence to check: ' + sources,
                'Correction path: CORRECTED | RETRACTED | UNKNOWN | BLOCKED',
                'Control path: pause | stop | correct | retract | revoke',
                'Boundary: not medical/legal/financial/emergency/surveillance/child-facing/autonomous authority'
            ].join('\n');
            const out = document.getElementById('bettersafe-packet-output');
            if (out) out.textContent = output;
        }
        document.addEventListener('DOMContentLoaded', () => {
            const btn = document.getElementById('bettersafe-build-packet');
            if (btn) btn.addEventListener('click', buildBetterSafePacket);
        });
"""

_REGISTERED_SENSOR_HEADER = '&mdash; <span id="wm-sensor-count-header">0</span> registered sensors'
_REGISTERED_SENSOR_COPY = '&mdash; registered sensors'
_LIVE_SENSOR_HEADER = ' &mdash; live sensors: <span id="wm-live-sensors-header">checking</span>'

_PUBLIC_COPY_REPLACEMENTS = (
    (
        "<!-- AUTONOMOUS GOVERNANCE (collapsed by default) -->",
        "<!-- ADVISORY AGENT STATUS (collapsed by default) -->",
    ),
    ("Autonomous Governance", "Advisory Agent Status"),
    (
        "<strong>ALGORITHMIC GOVERNANCE</strong> &mdash; 7 autonomous agents\n"
        "                coordinate through PBFT consensus. No human board. Escalations are\n"
        "                irreversible after a 24-hour lock.",
        _ADVISORY_BANNER,
    ),
    ("<strong>ALGORITHMIC GOVERNANCE</strong>", "<strong>EXPERIMENTAL ADVISORY AGENTS</strong>"),
    ("No human board.", "Operator review required."),
    (
        "Escalations are irreversible after a 24-hour lock.",
        "Escalations are review records only unless explicitly authorized by an operator.",
    ),
    (
        "irreversible after a 24-hour lock.",
        "not executable unless explicitly authorized by an operator.",
    ),
    ('<div class="stat-label">Registered Sensors</div>', '<div class="stat-label">Runtime Sensor Sources</div>'),
    ('<div class="stat-label">Registered Sensor Sources</div>', '<div class="stat-label">Runtime Sensor Sources</div>'),
    (
        "document.getElementById('wm-sensor-count-header').textContent = data.sensor_count || 0;",
        "// Registered sensor count is represented in the runtime sensor source summary card.",
    ),
    (
        "sensors registered. Waiting for first observation cycle...",
        "registered sensor definitions available. Live observation remains disabled unless explicitly enabled.",
    ),
)


def _rewrite_public_html(template: str) -> str:
    """Apply public-copy convergence to a rendered or template HTML string."""
    for old, new in _PUBLIC_COPY_REPLACEMENTS:
        template = template.replace(old, new)

    if _REGISTERED_SENSOR_HEADER in template:
        replacement = _REGISTERED_SENSOR_COPY
        if "wm-live-sensors-header" not in template:
            replacement += _LIVE_SENSOR_HEADER
        template = template.replace(_REGISTERED_SENSOR_HEADER, replacement, 1)

    template = template.replace("<html>", '<html lang="en" dir="ltr">', 1)

    if "apple-mobile-web-app-title" not in template:
        template = template.replace("    <title>Human Flourishing Frameworks</title>", "    <title>Human Flourishing Frameworks</title>" + _IPHONE_APP_META, 1)

    if ".skip-link" not in template:
        template = template.replace("    </style>", _SKIP_LINK_CSS + "    </style>", 1)

    if "bettersafe-pilot-panel" not in template:
        template = template.replace("    </style>", _BETTERSAFE_PILOT_CSS + "    </style>", 1)
        template = template.replace(
            "        </header>\n\n        <!-- ============================================================ -->\n        <!-- FLOURISHING SCORES",
            "        </header>\n\n" + _BETTERSAFE_PILOT_HTML + "\n        <!-- ============================================================ -->\n        <!-- FLOURISHING SCORES",
            1,
        )

    if 'href="#main-content"' not in template:
        template = template.replace(
            '<body>\n    <div class="container">',
            '<body>\n    <a class="skip-link" href="#main-content">Skip to main content</a>\n    <main id="main-content" class="container">',
            1,
        )
        template = template.replace(
            "        </footer>\n    </div>\n\n    <script>",
            "        </footer>\n    </main>\n\n    <script>",
            1,
        )

    if (
        "wm-live-sensors-header" in template
        and "Public runtime sensor state comes from /healthz" not in template
    ):
        template = template.replace(
            "        // ---- WORLD MODEL STATUS ----",
            _HEALTHZ_SENSOR_STATUS_JS + "\n        // ---- WORLD MODEL STATUS ----",
            1,
        )

    if "function buildBetterSafePacket()" not in template:
        template = template.replace(
            "        function toggleSection(id, header) {",
            _BETTERSAFE_PILOT_JS + "\n        function toggleSection(id, header) {",
            1,
        )

    return template


def _sanitize_public_template() -> None:
    """Replace misleading public copy in the module-level template."""
    template = getattr(_app_module, "HTML_TEMPLATE", "")
    if isinstance(template, str):
        _app_module.HTML_TEMPLATE = _rewrite_public_html(template)


def _apply_public_ui_baseline() -> None:
    """Kept for compatibility with older tests/imports; handled by rewrite."""
    _sanitize_public_template()


def _clarify_public_sensor_status() -> None:
    """Kept for compatibility with older tests/imports; handled by rewrite."""
    _sanitize_public_template()


_sanitize_public_template()

app = _app_module.app
background_controller = create_background_controller_from_env()
background_controller.start()


@app.route("/manifest.webmanifest")
def pwa_manifest():
    """Manifest for iPhone/Home Screen pilot shell."""
    response = jsonify(_PWA_MANIFEST)
    response.headers["Content-Type"] = "application/manifest+json"
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


@app.route("/bettersafe-icon.svg")
def bettersafe_icon():
    """Small local SVG icon for the BetterSafe pilot shell."""
    return Response(_BETTERSAFE_ICON_SVG, content_type="image/svg+xml")


@app.route("/background/status")
def background_status():
    """Visible status for the opt-in heartbeat-only background mode."""
    return jsonify({"background_mode": background_controller.snapshot()})


@app.route("/deployment/identity")
def deployment_identity_status():
    """Visible non-secret deployment identity for live freshness smoke."""
    return jsonify({"deployment": deployment_identity()})


@app.after_request
def _enforce_safe_public_response(response):
    """Prevent stale public dashboard copy from surviving template drift or cache.

    This response-level guard is intentionally presentation-only. It does not add
    writes, sensors, mesh sync, agents, secrets, databases, or deployment
    authority. It gives the public HTML the same claim/guard language even if the
    imported template changes before app.py is corrected directly.
    """
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    content_type = response.headers.get("Content-Type", "")
    if response.direct_passthrough or "text/html" not in content_type.lower():
        return response

    try:
        html = response.get_data(as_text=True)
        rewritten = _rewrite_public_html(html)
        if rewritten != html:
            response.set_data(rewritten)
            response.headers["Content-Length"] = str(len(response.get_data()))
    except Exception:
        return response

    return response


if __name__ == "__main__":
    app.run()
