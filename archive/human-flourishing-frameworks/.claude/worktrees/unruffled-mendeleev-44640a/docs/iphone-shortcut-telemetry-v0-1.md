# iPhone Shortcut Telemetry V0.1

Status: transitional Shortcut recipe; superseded architecturally by `phone_telemetry.py`.

Last reviewed: 2026-05-09.

## Purpose

Add a small amount of useful iPhone telemetry without collecting private phone data.

V0.1 builds on the already-working iPhone adoption heartbeat:

```text
POST /api/adoption/register
platform: iphone_shortcuts
node_name: Alex iPhone
```

## Architecture correction

HFF already has a sensor/measurement model in `sensors.py`. Phone telemetry should be represented as real `Measurement` objects, not only as adoption-node metadata.

The repo now includes:

```text
phone_telemetry.py
PhoneShortcutSensor
sanitize_phone_payload
tests/test_phone_telemetry.py
```

The existing adoption heartbeat remains useful for node visibility. It should not be treated as the final telemetry model.

Correct layering:

```text
iPhone Shortcut heartbeat -> visible adoption node
sanitized iPhone payload -> PhoneShortcutSensor -> Measurement
future endpoint/table -> stores bounded phone telemetry separately
```

## Telemetry allowed in V0.1

Allowed coarse telemetry:

```text
battery_level_percent
battery_state: charging | unplugged | full | unknown
manual_mode: awake | working | sleep_soon | traveling | unknown
shortcut_version
operator_note: optional short bounded note
```

Do not collect or transmit by default:

```text
precise GPS location
contacts
messages
call logs
photos
microphone/audio
camera/video
health data
biometrics
sleep data
calendar contents
browser history
raw notification content
```

## Current Shortcut bridge

Until HFF adds a dedicated phone telemetry endpoint/table, the iPhone Shortcut can still encode coarse telemetry into existing adoption metadata fields for visibility.

This is a bridge only.

## Recommended Shortcut actions

In the existing `HFF Heartbeat` Shortcut, add these actions before `Get Contents of URL`:

```text
Get Battery Level
Set Variable: BatteryLevel

Get Battery State
Set Variable: BatteryState

Text: awake
Set Variable: ManualMode
```

For manual mode, Alex can duplicate the shortcut or edit the `Text` value before running:

```text
awake
working
sleep_soon
traveling
unknown
```

## Transitional JSON body

Use the same URL and token as the working heartbeat.

Update the JSON body to:

```json
{
  "node_id": "alex-iphone-001",
  "node_name": "Alex iPhone",
  "platform": "iphone_shortcuts",
  "version": "phone-heartbeat-v0.1 battery=${BatteryLevel}",
  "region": "coarse_only",
  "operator_type": "owner_operator mode=${ManualMode}",
  "deployment_type": "personal_phone_sensor battery_state=${BatteryState}",
  "node_public_key": ""
}
```

In Shortcuts, insert the variables using the variable picker rather than typing `${BatteryLevel}` literally.

## Measurement model target

The proper model is:

```python
Measurement(
    value={
        "device_id": "alex-iphone-001",
        "battery_level": 83,
        "battery_state": "charging",
        "manual_mode": "working",
        "shortcut_version": "phone-heartbeat-v0.2",
    },
    uncertainty=0.35,
    confidence_interval=(0.0, 1.0),
    sample_size=1,
    source="iphone_shortcuts",
    methodology="operator_initiated_phone_heartbeat",
    temporal_range=("instant", "instant"),
    scope="operator:alex:iphone",
    confounders=[
        "operator_controlled_shortcut",
        "manual_mode_self_reported",
        "phone_shortcut_may_fail_or_be_stale",
    ],
    missing=[
        "no_precise_location",
        "no_health_data",
        "no_contacts",
        "no_messages",
        "no_audio",
        "no_camera",
        "no_notification_content",
    ],
)
```

## Expected visible result

After running the shortcut, check:

```text
GET /api/adoption/nodes
```

Expected node entry should still show:

```text
name: Alex iPhone
platform: iphone_shortcuts
```

and may expose coarse bridge metadata inside visible adoption fields, for example:

```text
version: phone-heartbeat-v0.1 battery=83
operator_type: owner_operator mode=working
deployment_type: personal_phone_sensor battery_state=charging
region: coarse_only
```

## Limits

This is not a real phone telemetry table yet. It is a low-friction bridge plus a now-available sensor adapter.

A later V1 should add:

```text
POST /api/operator/phone/heartbeat
GET /api/operator/phone/latest
phone-specific token
bounded schema validation using phone_telemetry.py
separate retention policy
explicit privacy review
```

## Safety boundary

Do not use this telemetry to infer private health, sleep, location, or emotional state as fact.

Treat it as:

```text
operator-controlled coarse phone heartbeat metadata
```

not as:

```text
surveillance
medical data
verified sleep data
precise location
private personal-state proof
```

## Validation checklist

```text
1. Run HFF Heartbeat from iPhone.
2. Confirm Shortcut returns success.
3. Open /api/adoption/nodes.
4. Confirm Alex iPhone appears.
5. Confirm coarse bridge metadata is visible if using the transitional JSON body.
6. Confirm no token, location, health, contact, message, audio, camera, or notification data appears.
7. Run tests/test_phone_telemetry.py when local or CI execution is available.
```
