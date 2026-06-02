# Current Public Deployment Validation State

Status: durable Keystone deployment memory.

Last reviewed: 2026-05-09.

This note records the current public-copy hotfix and validation state after the
misleading dashboard banner was found on the public Render page and in `app.py`.

## Incident summary

The public dashboard contained false or unsafe authority copy:

```text
ALGORITHMIC GOVERNANCE
No human board
Escalations are irreversible after a 24-hour lock
```

This contradicts current HFF/Keystone doctrine:

```text
Capability is not authority.
Keystone may reason about catastrophe; Keystone may not control catastrophe.
Agents are advisory/demo/research workflows unless explicitly and lawfully authorized.
Escalations are review records unless an operator authorizes action.
```

## Current hotfix stack on master

| Commit | Purpose |
|---|---|
| `3dbd535d1665022b85094089b3ac4de8a775020d` | Add `safe_app.py` sanitized public entrypoint |
| `1ed512ac17d848fcf8a1bc586a8f3b04a2dfc52f` | Point Dockerfile to `safe_app:app` |
| `db00e60b8806e261dd85d369eb4890ffe78633f9` | Add regression test for unsafe dashboard copy |
| `7578f2700fa3afbed64e57a32969d0740a675647` | Point WSGI entrypoint to `safe_app` |
| `400347ab10d8ce8db8d662253b8dff01caefd8ab` | Add public entrypoint convergence guard |
| `c988440923e980f59787e88b103a06e96ba2f195` | Add public-site smoke workflow for Render URL |

## Current deployment evidence

GitHub status for latest checked commit `c988440923e980f59787e88b103a06e96ba2f195`:

```text
context: content-reverence - web
state: success
target: Railway deployment context
```

This means the connected deploy/status integration reported a successful cloud
deploy context for the latest master commit.

Important limitation:

```text
This chat environment could not resolve the public Render or Railway hostnames,
so it has not independently fetched the live HTML.
Deployment status success is evidence of deployment, not proof of rendered page content.
```

## Current source/runtime guard state

| Surface | Current state |
|---|---|
| Dockerfile | `gunicorn safe_app:app --bind 0.0.0.0:${PORT:-5000}` |
| WSGI | `from safe_app import app` |
| `safe_app.py` | Replaces unsafe public dashboard copy before exposing Flask app |
| `sitecustomize.py` | Not present and explicitly blocked by test |
| Regression tests | Guard bad phrases and required advisory phrases |
| Public smoke workflow | Fetches Render page, `/health`, and `/api/status` from GitHub Actions runner |

## Remaining validation gap

The following must still be proven before saying the website is fully validated:

```text
A network path outside this chat environment fetches the public page.
The fetched page does not contain the forbidden phrases.
The fetched page does contain advisory/operator-reviewed replacement copy.
/health returns successfully.
/api/status returns valid JSON.
```

## Next safest action

Add and run a container-level smoke test in CI:

```text
build the Docker image
run it locally inside GitHub Actions
curl /
curl /health
curl /api/status
fail if forbidden public-copy phrases appear
require advisory replacement copy
```

This validates the container artifact before relying on cloud-host DNS or Render/Railway routing.

## Future cleanup

The emergency `safe_app.py` entrypoint should remain until the source template in
`app.py` is corrected from a complete checkout. After direct `app.py` cleanup,
remove `safe_app.py` only after tests prove:

```text
app.py source no longer contains unsafe phrases
Docker and WSGI can route directly to app safely
public page still passes smoke checks
```

Do not replace large truncated `app.py` content through a connector output. Use a
complete local checkout or a targeted patch mechanism that cannot truncate the file.
