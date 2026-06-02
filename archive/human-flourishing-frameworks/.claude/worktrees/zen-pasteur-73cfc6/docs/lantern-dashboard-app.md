# Lantern Dashboard App

## Product direction

Lantern converges toward one dashboard application:

```text
one conversational surface
one backend
one install path
one status model
one visible doctrine surface
```

The dashboard runs at a web URL and can be installed as a desktop or phone shortcut/PWA.

## Desired experience

```text
Alex messages Lantern
Lantern messages back
```

The application should feel similar to a modern GPT-style chat interface while preserving:

```text
visible state
visible limits
visible health
visible doctrine
bounded sensors
```

## Architecture

### Frontend

```text
chat-first dashboard
status sidebar
message history
health indicators
installable PWA shell
```

### Backend

Current backend:

```text
lantern/server.py
```

Current routes:

```text
/
/app.js
/api/lantern/health
/api/lantern/state
/api/lantern/chat
```

The backend already supports a configured server-side language substrate.

## Convergence rules

### Keep

```text
single chat identity
visible state
read-only repo inspection
explicit limits
provider/model visibility
```

### Remove or avoid

```text
overlapping app identities
local-only posture as the product identity
fake local LLM claims
continuity-transfer claims
multi-dashboard fragmentation
autonomous-correction language
```

## First release shape

The first release should be:

```text
web-first
PWA-capable
server-backed
installable shortcut
```

Not:

```text
Electron-first
native packaged first
autonomous runtime
background correction engine
```

## Sensor boundaries

Allowed visible sensors:

```text
repo state
health
model/provider
last-test evidence
doctrine status
```

Blocked:

```text
command execution
secret exposure
repo writes from chat
background autonomy
hidden sensors
```

## Messaging posture

Preferred wording:

```text
Lantern Dashboard
connected substrate
server-backed
read-only state visibility
degraded mode when unavailable
```

Avoid wording like:

```text
full continuity layer
capability transfer
persistent consciousness
local superintelligence
```

## Acceptance criteria

```text
1. One primary dashboard surface.
2. GPT-style conversational layout.
3. Server-backed chat.
4. Visible degraded-mode handling.
5. Installable PWA/shortcut support.
6. Explicit health + state visibility.
7. No autonomous correction.
8. No false local-LLM claims.
```
