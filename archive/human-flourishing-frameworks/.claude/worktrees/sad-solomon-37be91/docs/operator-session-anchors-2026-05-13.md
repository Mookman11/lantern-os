# Operator Session Anchors — 2026-05-13

Status: docs/data-contract policy.

Last reviewed: 2026-05-13.

Four anchor packets repaired from one long late-session convergence with the
operator. Each follows the shape required by `docs/anchor-taxonomy.md`: id,
kind, source surface, short meaning, allowed use, boundary, restore phrase,
review trigger, last reviewed date.

These are doctrine-level anchors. They live in `docs/` because they are
repo-wide rules about Lantern's runtime, not protected-person context.

---

## orchestrator_model_alias_poison

```text
id:              orchestrator_model_alias_poison
kind:            doctrine_anchor
source_surface:  docs/operator-lantern-repo-convergence.md
                 + session 2026-05-13 (Anthropic/OpenAI/WebSearch/WebFetch/Agent x10 all failed)
short_meaning:   The orchestrator at gm-agent-orchestrator sets env vars and config
                 fields like ANTHROPIC_DEFAULT_*_MODEL to router-aliases such as
                 "deepseek-v4-pro[1m]" or "deepseek-v4-flash" that do not resolve at
                 real provider endpoints. This bleeds into every Claude Code surface
                 that reads those vars, breaking WebSearch, WebFetch, Agent spawns,
                 and direct Anthropic substrate calls.
allowed_use:     Name this as the root cause when a tool returns
                 "model not found" or "no model" errors. Route Lantern around the
                 poison by setting LANTERN_OPENAI_BASE_URL / LANTERN_OPENAI_MODEL
                 directly at the spawn site, bypassing the orchestrator's poisoned
                 env layer.
boundary:        Do not claim every tool failure is this anchor. Verify by
                 reproducing the call with a known-good model name first.
                 Do not unilaterally rewrite the orchestrator's env without operator
                 review — the orchestrator owns its own config.
restore_phrase:  "The orchestrator's model alias is router-shaped, not
                 provider-shaped. Verify the alias resolves before claiming a tool
                 is broken; route around with Lantern-specific env if it doesn't."
review_trigger:  Any tool failure whose error string mentions "deepseek-v4" or
                 "model not found" or that lists a router-alias as the active model.
last_reviewed:   2026-05-13
```

---

## powershell_startprocess_env_drop

```text
id:              powershell_startprocess_env_drop
kind:            doctrine_anchor
source_surface:  scripts/Wake-Lantern.ps1
                 + session 2026-05-13 (3 confirmed reproductions of voice=local-templated
                 after Start-Process spawn with env apparently set)
short_meaning:   On Windows PowerShell 5.1, Start-Process does not reliably
                 propagate parent shell env vars (`$env:X = "Y"`) to child
                 processes, contrary to default documented behavior. Child gets
                 the system base env, not the parent's modifications. Bash
                 (`export X=Y && python ...`) propagates cleanly. Verified during
                 session 2026-05-13 — direct _maybe_call_llm() in a Python child
                 spawned via Bash returned LLM voice; same code spawned via
                 PowerShell Start-Process returned None (env-less).
allowed_use:     When spawning Lantern's backend or any subprocess that depends on
                 env, prefer Bash with explicit `export` for run_in_background
                 launches; or write env to a wrapper .bat that the spawn calls.
                 Use this anchor to diagnose any "voice flipped to local-templated
                 after restart" report.
boundary:        Applies to PowerShell 5.1 on Windows; PowerShell 7+ may differ
                 (untested). Does not apply when Start-Process is called with
                 explicit -Environment hashtable (also not yet verified in repo).
restore_phrase:  "PowerShell Start-Process eats env. Use Bash export or a .bat
                 wrapper to spawn env-sensitive children."
review_trigger:  Backend `voice=local-templated` immediately after a restart that
                 was supposed to carry LANTERN_LLM_PROVIDER.
last_reviewed:   2026-05-13
```

---

## watchdog_envless_respawn

```text
id:              watchdog_envless_respawn
kind:            doctrine_anchor
source_surface:  scripts/install_lantern_chat_autostart.ps1
                 scripts/watch_lantern_chat.ps1
                 scripts/Wake-Lantern.ps1
                 + session 2026-05-13
short_meaning:   The LanternChatWatchdog scheduled task respawns Lantern after
                 crash, login, or polled-down detection without carrying the
                 substrate routing env vars (LANTERN_LLM_PROVIDER,
                 LANTERN_OPENAI_BASE_URL, LANTERN_OPENAI_MODEL, OPENAI_API_KEY).
                 Even if Wake-Lantern.ps1 starts Lantern correctly at boot, any
                 subsequent watchdog respawn drops Lantern back to local-templated
                 echo mode. The gap is env, not respawn — the watchdog does its
                 job; substrate routing is invisible to it.
allowed_use:     Name this gap when Lantern's voice flickers between llm and
                 local-templated without operator action. Repair options, in
                 increasing operator burden: (a) wrapper .bat called by the
                 watchdog that sets env then execs python; (b) `setx` to persist
                 user-level env vars across sessions; (c) register the env into
                 the scheduled task action's arguments.
boundary:        Do not claim the watchdog itself is broken — it correctly
                 respawns. Do not propose moving to a Windows Service for this
                 (the existing comment in install_lantern_chat_autostart.ps1
                 explains the GUI-session constraint).
restore_phrase:  "Watchdog respawn is env-less. Substrate routing must live in a
                 user-level persistent env or in the spawn wrapper, never just in
                 the operator's interactive shell."
review_trigger:  Lantern's voice flips to local-templated without operator
                 action, especially after sleep/wake or task-scheduled relaunch.
last_reviewed:   2026-05-13
```

---

## pragmatic_certainty_interpretation

```text
id:              pragmatic_certainty_interpretation
kind:            pragmatic_certainty_anchor
source_surface:  docs/anchor-taxonomy.md (lines 179-228 — the canonical rule)
                 + session 2026-05-13 (live application across "GO", "full panic",
                 "use subagents x10", "full override", "now", "hurry")
short_meaning:   Operator absolutes addressed to Lantern or Claude — "GO",
                 "full panic", "use subagents x10", "full override", "all of it",
                 "everywhere all the time" — mean practical certainty over the
                 current working domain. They authorize proceeding within the
                 established hard constraints; they do not authorize crossing
                 them. Interpret as direction to act, not as consent to violate.
allowed_use:     Receive operator absolutes as HUMAN_OPERATOR_CONFIRMED authority
                 to ship the largest acceptable bounded action within the
                 receiver-acceptance band already in place: voice rule
                 (no synthesis, no cloned voice, no agentic-AI voice), spine
                 stop conditions, redaction rules for protected persons, artists'
                 rights, public-platform constraints. Name when an absolute is
                 being acted on by saying so briefly.
boundary:        Do not use operator absolutes as consent on behalf of artists,
                 protected minors, bystanders, banks, or platforms. Do not treat
                 absolutes as consent forever — they last for the current bounded
                 work, not future bounded work without renewal. Do not claim
                 impossible guarantees because the operator emphasized.
restore_phrase:  "Respect the human absolute as practical certainty over the
                 working domain. Preserve literal limits where safety, evidence,
                 artists' rights, or public claims require them."
review_trigger:  Any operator absolute that would, taken literally, cross a hard
                 constraint (synthesis, copyright, agent-without-approval, public
                 release of private context, protected-minor data collection).
last_reviewed:   2026-05-13
```

---

## Non-goals

This document does not authorize:

```text
rewriting the orchestrator's config without separate operator review
shipping a watchdog .bat wrapper as part of this anchor packet
claiming the PowerShell behavior is a Windows bug (it may be intentional)
treating any one operator absolute as consent forever
using these anchors to override the existing voice rule, spine stop
conditions, or redaction rules
```
