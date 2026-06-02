# Public Deployment Strategy

Status: docs/data-contract policy.

This document defines a platform-agnostic public deployment strategy for HFF.
Railway may be used as a current adapter, but HFF should not depend on Railway
as the architecture.

It is intentionally docs-only. It adds no runtime code, deploy hooks, secrets,
credentials, infrastructure automation, endpoints, polling, mesh writes, or
provider-specific configuration.

## Core rule

Railway is a hosting adapter, not the deployment strategy.

The strategy is:

```text
portable container
read-only public surface
closed write/autonomy flags
explicit deployed-SHA validation
post-deploy smoke checks
external monitoring
provider-exit path
technology-exit path
```

## Target deployment shape

Preferred public posture:

```text
public web surface: read-only / advisory
public API surface: health, status, read-only model views
write surfaces: disabled unless narrowly approved
autonomy surfaces: disabled unless stage-authorized
operator/control plane: separate from public app
secrets: never exposed to public app logs or UI
```

## Provider roles

| Provider role | Acceptable use | Not acceptable |
|---|---|---|
| Simple PaaS adapter | Host the Docker image and expose health endpoints | Become the source of deployment truth |
| Container platform | Run the same image with explicit env flags | Mutate runtime behavior through hidden defaults |
| Static host/CDN | Serve public read-only artifacts | Host write/control endpoints |
| External monitor | Verify uptime and smoke checks after deploy | Replace release validation |
| CI/CD system | Build, test, publish signed images | Self-authorize production recovery |

## Current Railway posture

Current Railway-specific posture should stay minimal:

```text
railway.toml: Dockerfile builder only
startCommand override: absent unless fresh evidence requires it
healthcheck path: /health when configured in provider settings
PORT: provided by hosting platform and consumed by container command
```

Railway should be easy to replace with any platform that can run the OCI/Docker
image and provide environment variables.

## Technology exit strategy

HFF should treat every technology choice as replaceable behind a contract.

The goal is not to avoid dependencies. The goal is to avoid making any dependency
irreversible.

| Layer | Current likely technology | Stable contract | Exit strategy |
|---|---|---|---|
| Hosting | Railway or another PaaS | OCI/Docker image + PORT + health endpoints | Run same image on another container host |
| Container build | Dockerfile | OCI image/artifact semantics | Keep startup inside image, not provider config |
| Web runtime | Flask/Gunicorn | HTTP endpoints + JSON schemas | Keep handlers thin; preserve API contract |
| Public API | Flask routes | OpenAPI-style endpoint contract | Generate/validate contract before framework migration |
| Database/local state | SQLite/files in `/data` | Repository/service interface + export format | Add export/import before changing storage engine |
| Background jobs | Python threads | Explicit job interface and feature flags | Move jobs to queue/worker only after contract tests |
| Observability | Logs and smoke checks | OpenTelemetry-compatible traces/metrics/logs | Export to any compatible backend |
| CI | GitHub Actions | Shell/Python test commands | Keep tests runnable locally and in other CI systems |
| Secrets | Provider env vars | Named secret contract + least privilege | Move secrets provider without app code changes |
| Model/LLM usage | External/vendor model if added later | Model adapter + capability/reliance metadata | Swap providers without changing policy logic |
| Mesh/consensus | Current internal mesh/PBFT research code | Message schema + trust/provenance rules | Replace transport/consensus without changing claim semantics |
| Static/public content | Server-rendered or static export | Read-only artifact contract | Publish via CDN/static host independently |

## Exit-readiness checklist

Before adopting or deepening any technology, require:

```text
clear owner
clear contract
known replacement path
export path for data
local test path
non-provider-specific configuration
rollback path
security review of dependency surface
license review when relevant
operational cost/risk note
```

Before removing or replacing a technology, require:

```text
contract tests pass on old and new implementation
migration dry run exists
backup/export produced
rollback procedure written
operator/governance approval for production data changes
public behavior unchanged unless explicitly approved
```

## Technology-specific boundaries

### Hosting providers

Do not let any hosting provider become the release authority.

```text
provider deploy success != release validation
provider healthcheck != ongoing health
provider UI config != source of truth
```

### Web frameworks

Do not let Flask become the product boundary.

```text
API contract matters more than framework
handlers should remain thin
business rules should be testable without HTTP
```

### Databases

Do not let local SQLite or file persistence become a migration trap.

```text
schema must be inspectable
export/import must exist before high-value data accumulates
runtime code should access storage through a small interface
```

### Observability vendors

Do not hardwire monitoring to a single provider.

```text
emit portable logs/metrics/traces
prefer OpenTelemetry-compatible shape
monitoring backend can change
```

### CI/CD providers

Do not let GitHub Actions become the only proof path.

```text
all required tests should run locally
CI should call ordinary commands
release evidence should include commands and results, not only badges
```

### Model providers

Do not let any LLM provider become a governance authority.

```text
model output = proposal/hypothesis
policy engine = explicit rules
sources/evals = evidence
runtime authority = maturity-stage gated
```

## Why provider-agnostic matters

A public deployment that depends too much on one provider can create avoidable
risk:

```text
provider outage -> total outage
provider-specific config -> portability loss
provider healthcheck semantics -> false release confidence
provider logs/env handling -> accidental secret exposure
provider deploy UI -> unreviewed production mutation
```

The system should treat provider evidence as one signal, not the source of
truth.

## Why technology-agnostic matters

Technology lock-in can also create safety risk:

```text
framework lock-in -> hard-to-fix runtime flaws
storage lock-in -> hard-to-migrate corrupted or sensitive data
monitoring lock-in -> blind spots during provider migration
CI lock-in -> inability to validate during platform outage
model-provider lock-in -> governance drift toward vendor capabilities
consensus lock-in -> false authority from one mechanism
```

The system should treat implementation technologies as adapters around stable
contracts.

## Public-risk-minimized modes

### Mode A: Static public mirror

Lowest public risk.

```text
build static/read-only public pages
publish no write endpoints
publish no secrets
publish no live autonomy
refresh by reviewed deploy only
```

Good for public education, status snapshots, and doctrine pages.

### Mode B: Read-only dynamic service

Acceptable default for HFF public app.

```text
serve /health
serve /api/status
serve read-only model/status endpoints
keep writes disabled
keep mesh sync disabled
keep executor disabled
keep live sensors disabled unless explicitly approved
```

Good for demos and public transparency.

### Mode C: Controlled API service

Higher risk.

```text
requires write tokens
requires scoped credentials
requires rate limits
audit logs required
no public-write demo override in production
```

Good only for controlled deployments.

### Mode D: Runtime/autonomy service

Highest risk.

```text
requires maturity-stage authorization
requires separate control plane
requires audit, rollback, external monitor, kill switch
not a default public deployment mode
```

## Release validation ladder

| Reliance level | Evidence | Public-deploy meaning |
|---:|---|---|
| 1 | A provider says deploy succeeded | Weak signal only |
| 2 | `/health` returns 200 once | App process responded once |
| 3 | `/health` + `/api/status` pass on deployed SHA | Basic smoke validation |
| 4 | Safety endpoints and runtime flags verified | Low-risk public mode acceptable |
| 5 | External monitor + rollback path + operator/governance confirmation | Release validated |

## Required public deploy gates

Before public release validation:

```text
deployed commit SHA recorded
container image/digest recorded when available
/health returns 200
/api/status returns 200
/api/autonomous/status confirms executor disabled by default
/api/mesh/sync returns 403 by default
runtime flags audited
public writes disabled
live sensors disabled unless approved
mesh sync disabled unless approved
secrets not printed or exposed
external monitor configured or manual follow-up scheduled
rollback path identified
```

## Provider exit criteria

A deployment strategy is acceptable only if HFF can move providers without
rewriting the app.

Minimum exit criteria:

```text
Dockerfile remains source of startup truth
app listens on PORT
no required Railway-only runtime code
no provider-specific secret assumptions
release checklist works for at least one non-Railway target
health/status endpoints are platform-neutral
```

## Technology exit criteria

A public deployment strategy is acceptable only if HFF can move away from major
implementation choices without changing the public safety meaning of the system.

Minimum exit criteria:

```text
HTTP API behavior has a documented contract
storage can be exported before replacement
observability can be redirected without code rewrites
CI can be reproduced locally
model providers are behind adapters if added
mesh/consensus semantics are separate from transport implementation
runtime flags keep the same meaning across platforms
```

## Better-than-Railway target architecture

Longer-term target:

```text
public static/read-only mirror
+ read-only dynamic API container
+ separate private control plane
+ external uptime/smoke monitor
+ signed image or deploy artifact
+ immutable release notes with deployed SHA
+ provider-neutral rollback procedure
+ technology-exit tests for critical layers
```

Railway can host the read-only dynamic API container for now. It should not host
operatorless control authority until the deployment autonomy maturity model has
advanced beyond Stage 1.

## Explicit non-goals

This policy does not authorize:

```text
self-repairing deploys
secret rotation
production rollback automation
autonomous config changes
public write APIs
mesh writes
live sensor polling
autonomous escalation execution
provider-specific lock-in
technology-specific lock-in
```

## Default conclusion

The acceptable-risk public strategy is not "make Railway safer." It is:

```text
make HFF portable
make technologies replaceable
make the public surface read-only
make provider evidence non-authoritative
make release validation explicit
make provider replacement easy
make technology replacement testable
```
