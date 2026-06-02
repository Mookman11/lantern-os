# Device Telemetry Validation - 2026-05-09

Status: focused validation evidence.

## Context

Device telemetry was generalized from an iPhone-only adapter into a bounded device telemetry model.

Relevant files:

```text
device_telemetry.py
phone_telemetry.py
tests/test_device_telemetry.py
tests/test_phone_telemetry.py
```

## Bug found during validation

Initial focused test execution after pulling current `master` produced one real failure:

```text
python -m unittest discover -s tests -p "test_device_telemetry.py"
.F.....
FAIL: test_device_telemetry_sensor_emits_measurement
AssertionError: 0 != 1
```

The iPhone wrapper tests passed at that point:

```text
python -m unittest discover -s tests -p "test_phone_telemetry.py"
.......
Ran 7 tests in 0.001s
OK
```

Root cause:

```text
DeviceTelemetrySensor.update_payload() stored a sanitized payload.
DeviceTelemetrySensor.observe() sanitized that already-sanitized payload again.
The sanitized payload contained client_recorded_at.
client_recorded_at was not accepted as an allowed input key.
observe() caught the ValueError and returned [].
```

Fix commit:

```text
aa8bcb2499c202ea6fc0e1d805d5a2135ec96b9a
fix: allow sanitized device telemetry replay
```

Fix summary:

```text
ALLOWED_DEVICE_TELEMETRY_FIELDS now includes client_recorded_at.
sanitize_device_payload now accepts either recorded_at or client_recorded_at.
```

## Passing focused validation

After pulling fix commit `aa8bcb2`, Alex ran:

```powershell
git pull
python -m unittest discover -s tests -p "test_device_telemetry.py"
python -m unittest discover -s tests -p "test_phone_telemetry.py"
```

Observed results:

```text
python -m unittest discover -s tests -p "test_device_telemetry.py"
.......
----------------------------------------------------------------------
Ran 7 tests in 0.001s

OK

python -m unittest discover -s tests -p "test_phone_telemetry.py"
.......
----------------------------------------------------------------------
Ran 7 tests in 0.001s

OK
```

## Evidence class

```text
operator_reported_local_windows_validation
```

## Current interpretation

The focused adapter-level validation gap is closed:

```text
device telemetry focused tests: passing
phone telemetry focused tests: passing
```

This does not yet validate any future runtime endpoint, token handling, storage, retention, deployment, or public API behavior.

## Next best action

If device telemetry moves beyond adapters, create a small focused PR for a default-closed endpoint such as:

```text
POST /api/operator/device/heartbeat
GET /api/operator/device/latest
```

Required before endpoint merge:

```text
auth required
blocked private fields rejected
sanitized fields stored separately from adoption metadata
latest-only or retention policy documented
no secrets committed
no GPS/location, health, contacts, messages, audio, camera, photos, notification contents, or raw nearby-network/device identifiers
focused endpoint tests passing
```
