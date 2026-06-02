# Operator Device Endpoint V1

Status: focused PR design note.

## Purpose

Add a default-closed endpoint surface for bounded operator-approved device telemetry without expanding runtime autonomy, mesh writes, deployment behavior, live sensors, or surveillance scope.

## Proposed endpoints

```text
POST /api/operator/device/heartbeat
GET  /api/operator/device/latest
```

The implementation lives in:

```text
operator_device_api.py
```

It is exposed as a reusable Flask blueprint:

```python
from operator_device_api import create_device_telemetry_blueprint

app.register_blueprint(create_device_telemetry_blueprint())
```

## Current PR boundary

This PR intentionally adds the blueprint and focused tests first.

It does not perform a large direct edit of `app.py` through the connector because `app.py` is a large file and full-file replacement is risky. The safest integration step is a tiny local patch adding the blueprint registration after review.

## Write gate

Heartbeat writes require one of:

```text
Authorization: Bearer <HFF_DEVICE_TELEMETRY_TOKEN>
X-HFF-Device-Token: <HFF_DEVICE_TELEMETRY_TOKEN>
X-HFF-Write-Token: <HFF_WRITE_TOKEN>
```

No token value may be committed to the repo or pasted into issues/chat.

## Storage policy

V1 is latest-only in process memory:

```text
one latest sanitized heartbeat
server_recorded_at
no history table
no raw payload retention
no token retention
```

This is deliberately minimal. A later persistence layer needs a separate retention/redaction review.

## Allowed telemetry

The endpoint accepts the same bounded device payload used by `device_telemetry.py`:

```text
device_id
device_kind
device_label
battery_level
battery_state
power_state
network_state
manual_mode
client_version
operator_note
recorded_at / client_recorded_at
```

## Rejected private fields

The sanitizer rejects fields containing private/sensitive fragments such as:

```text
location
GPS
latitude / longitude
contacts
messages
call logs
photos
microphone / audio
camera / video
health
biometrics
sleep
calendar
browser history
notifications
SSID / BSSID
Bluetooth / nearby device identifiers
```

## Validation

Focused tests:

```powershell
python -m unittest discover -s tests -p "test_operator_device_api.py"
python -m unittest discover -s tests -p "test_device_telemetry.py"
python -m unittest discover -s tests -p "test_phone_telemetry.py"
```

The endpoint tests cover:

```text
default-closed heartbeat without token
Authorization bearer token
X-HFF-Device-Token
X-HFF-Write-Token fallback
rejection of private fields
rejection of non-object JSON
empty latest response
latest-only replacement behavior
sanitized latest response shape
```

## External safety alignment

This design follows the current convergence posture:

```text
minimize data
reject private fields by default
do not rely on client-side filtering
return only explicit schema fields
require a write token
do not retain history by default
```

## Non-goals

This PR does not authorize:

```text
hidden tracking
precise location collection
health or sleep ingestion
messages, contacts, audio, camera, photos, notifications
raw network identifiers
autonomous behavior
mesh writes
live sensor enablement
deployment changes
secret storage
```
