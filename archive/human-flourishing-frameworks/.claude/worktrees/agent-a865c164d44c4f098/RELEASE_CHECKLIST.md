# Release Health Checklist

This checklist tracks release and deployment health gates for HFF safety work.

It is intentionally docs-only. It does not change Railway config, runtime code,
mesh behavior, autonomous execution, live sensors, or public-write behavior.

## Release Blockers

1. Public service health must be verified after deployment.
   - `GET /health` should return 200.
   - `GET /api/status` should return 200.
   - Record the deployed commit SHA before treating a deployment as validated.

2. Runtime safety defaults must remain closed unless explicitly approved.
   - `ENABLE_LIVE_SENSORS` unset/false unless live polling is approved.
   - `ENABLE_MESH_SYNC` unset/false unless peer mesh writes are approved.
   - `ENABLE_AUTONOMOUS_ESCALATION_EXECUTOR` unset/false unless autonomous execution is approved.
   - `HFF_ALLOW_PUBLIC_WRITES` unset/false on public services unless a narrow write grant is approved.

3. Draft or split-source PRs are not release artifacts.
   - Large draft PRs may be used as source piles for smaller reviewed PRs.
   - Do not mark a draft bundle as release-ready just because some split PRs pass.

## Required Local Checks

From the repo root:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -m unittest discover -s tests -t . -p "test_*.py"
```

If discovery is unavailable on the checked-out branch, run focused tests directly
and record the discovery limitation in the PR.

## Endpoint Smoke Checks

After deployment, verify:

```bash
curl -i https://web-production-46794.up.railway.app/health
curl -i https://web-production-46794.up.railway.app/api/status
curl -i https://web-production-46794.up.railway.app/api/autonomous/status
curl -i -X POST https://web-production-46794.up.railway.app/api/mesh/sync \
  -H "Content-Type: application/json" \
  -d "{\"node_id\":\"smoke-test\",\"violations\":[]}"
```

Expected default `/api/mesh/sync` result is 403 unless `ENABLE_MESH_SYNC=true`
was explicitly approved.

## Deployment Config Rule

Do not reintroduce a Railway `startCommand` override unless fresh deployment
evidence proves the Dockerfile-only configuration is insufficient.

Current preferred Railway posture is Dockerfile-led startup.

## Human-Impact Rule

Safety checks are not the final goal. They are the release floor for protecting
human and animal flourishing, consent, dignity, beauty, play, rest, touch, art,
and embodied joy.

No release should turn safety telemetry, bio registries, consensus records, or
person-state signals into hidden surveillance, public scoring, coercion, or
automated punishment.
