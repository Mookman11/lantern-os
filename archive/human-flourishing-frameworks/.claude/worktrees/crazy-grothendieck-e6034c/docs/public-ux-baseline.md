# Public UX Baseline

Status: public presentation guardrail.

## Purpose

The public dashboard should be understandable, calm, accessible, and honest about limits.

## Baseline

```text
Show the state.
Say the limit.
Make the main path easy.
Keep uncertainty visible.
Keep public surfaces safe by default.
```

## Current public language

The current dashboard is English-only. The safe public entrypoint declares:

```html
<html lang="en" dir="ltr">
```

This is a browser and assistive-technology hint for the current UI. It is not a claim that translation or localization is complete.

## Accessibility baseline

Public pages should provide:

- a document language and text direction;
- a skip link to main content;
- a main landmark;
- readable section headings;
- visible degraded-state copy when safe-read data fails;
- advisory language that does not imply authority, enforcement, or autonomy.

## Translation/localization rule

Do not claim translated support until safety-critical copy has been reviewed in that language. Boundary words such as advisory, uncertainty, consent, disabled, no hidden telemetry, not authority, and return path must preserve their meaning.

## Non-goals

This baseline does not add analytics, personalization, location logic, user profiling, sensors, mesh sync, public writes, SDK/APK behavior, or deployment changes.
