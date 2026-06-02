# Deployment Strategy

Status: repo-owned deployment intent.

## Purpose

The public service should deploy from repo configuration, not stale platform memory.

## Canonical web service command

```text
gunicorn safe_app:app --bind 0.0.0.0:$PORT --log-file -
```

## Canonical healthcheck

```text
/healthz
```

## Railway

`railway.json` is the source-of-truth repo config for the Railway web service.

Required behavior:

```text
builder: NIXPACKS
startCommand: gunicorn safe_app:app --bind 0.0.0.0:$PORT --log-file -
healthcheckPath: /healthz
restartPolicyType: ON_FAILURE
```

The service must not use stale commands such as:

```text
python /app/dashboard_app.py
python dashboard_app.py
python app.py
```

`dashboard_app.py` may remain as a compatibility shim, but it is not the canonical production target.

## Render

`render.yaml` should remain aligned with Railway and use the same canonical command.

## Deploy verification

A public deployment is current only if all are true:

```text
1. Platform deployment references the expected Git commit.
2. Deploy logs show the canonical safe_app Gunicorn command or equivalent repo-owned config.
3. /healthz returns HTTP 200.
4. /healthz reports live_sensors_enabled=false.
5. /healthz reports mesh_sync_enabled=false.
6. /healthz reports public_writes_enabled=false.
7. Public dashboard copy matches current repo convergence.
```

## Cache/stale-deploy diagnosis

If the public URL shows old copy after `master` changes:

```text
1. Add a query string such as ?v=<short-sha>.
2. If old copy remains, suspect stale deployment, wrong service, wrong branch, or old image.
3. Check platform deployment commit and branch.
4. Redeploy latest commit.
5. If still stale, inspect service source/repo linkage and start command.
```

## Non-goals

This strategy does not enable live sensors, mesh sync, public writes, analytics, personalization, location logic, user profiling, device enrollment, protected-minor data collection, SDK/APK behavior, actuator behavior, runtime autonomy, route expansion, or secret exposure.
