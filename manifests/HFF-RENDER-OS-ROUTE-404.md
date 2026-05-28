# HFF Render `/os` Route 404 Blocker

Generated: 2026-05-27.

## Symptom

Operator reported:

```text
https://human-flourishing-frameworks.onrender.com/os
Not Found
The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.
```

## Current Evidence

Render deploy config in `human-flourishing-frameworks/human-flourishing-frameworks` starts the app with:

```text
gunicorn safe_app:app --bind 0.0.0.0:$PORT --log-file -
```

The repo `Procfile` also points at:

```text
web: gunicorn safe_app:app --bind 0.0.0.0:${PORT:-5000} --log-file -
```

The safe public entrypoint file is `safe_app.py`. A recent repository fetch showed it was modified on `2026-05-28T02:55:58Z` and contains site navigation linking to `/os`, `/art`, `/api/status`, and the source repository.

The observed production response means the live Flask app does not currently serve `/os`, or Render is serving an older revision without the route.

## Classification

| Field | Value |
|---|---|
| State | `live_route_missing` |
| Surface | HFF Render public app |
| Dependency | `human-flourishing-frameworks/human-flourishing-frameworks` |
| Lantern OS role | dependency surface, not control-plane source |
| Risk | public route broken |
| Destructive action needed | no |
| Secret/env action needed | no |
| Safe fix type | local patch + redeploy |

## Minimal Safe Fix

Patch the HFF source repo, not Lantern OS:

1. Inspect local HFF repo status.
2. Add an explicit `/os` route to `safe_app.py`.
3. Add a smoke test that verifies `/os` returns HTTP 200.
4. Commit in HFF only after the test passes.
5. Push HFF and let Render redeploy.
6. Recheck `https://human-flourishing-frameworks.onrender.com/os`.

Use Lantern OS only as the control-plane record and fallback tracker.

## Route Fallback Behavior

The route should prefer the real Lantern desktop/dashboard artifact if present, then fall back to a bounded HTML status page.

Recommended route behavior:

```text
/os -> serve lantern desktop/dashboard HTML if present
/os -> otherwise render a fallback Lantern OS status page with links to /, /art, /api/status, and source
```

## Hold Conditions

Do not claim the public `/os` surface is fixed until a live HTTP check returns 200.

Do not claim the desktop app launched from Render. Render can serve the public web dashboard; the local desktop app still launches from the Windows/local Lantern OS repo.

Do not mutate unrelated HFF routes, auth, agents, sensors, mesh sync, secrets, databases, or deployment settings while fixing this route.

## Validation Commands

From the HFF repo on Windows:

```powershell
cd C:\tmp\human-flourishing-frameworks-scan
git status --short --branch
python -m pytest tests/test_hff_os_route.py
```

After push/redeploy:

```powershell
Invoke-WebRequest -UseBasicParsing https://human-flourishing-frameworks.onrender.com/os | Select-Object StatusCode, Content
```

## Lantern Fallback

Until the public Render route is fixed, use the local Lantern OS surfaces:

```powershell
cd C:\tmp\lantern-os
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Open-TonyGarage.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Start-LanternGarageApp.ps1
```
