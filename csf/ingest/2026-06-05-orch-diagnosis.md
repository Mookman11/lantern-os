# Orchestration Diagnosis — 2026-06-05

Status: diagnosis
Authored by: Claude Code audit pass

---

## Summary

The dispatcher/work delegation system has **four critical bugs** that prevent tasks from being routed to available healthy agents as defined in `agent-slots.json`. The hardcoded single-agent setup, missing health-check-aware routing, missing fallback chains, and a queue data-loss bug all need to be fixed together. This is not safely fixable in under 50 lines.

---

## Bug 1 — `get_pending_jobs` silently drops jobs when filtered (data loss)

**File:** `services/dispatcher/work_queue.py`, lines 39–51

`get_pending_jobs(agent_type=...)` pops jobs from the Redis `queue:pending` list with `lpop`. If a job's `agent_type` does not match the filter, it is appended to neither `jobs` nor the queue — it is **permanently discarded**.

The dispatcher currently calls this with no filter, so the bug is dormant today. But any caller that passes `agent_type` will silently eat work items belonging to other agents.

**Fix required:** Collect non-matching jobs during the scan and `rpush` them back to `queue:pending` before returning, or (better) use a per-agent-type queue key (`queue:pending:{agent_type}`) so `lpop` never needs a filter at all.

---

## Bug 2 — Dispatcher ignores `agent-slots.json` entirely (hardcoded single agent)

**File:** `services/dispatcher/dispatcher.py`, lines 27–33

`WorkDispatcher.__init__` hardcodes exactly one agent:

```python
self.agents = {
    "dream_journal": AgentController(
        agent_name="dream_journal",
        agent_type="dream_journal",
        container_name="lantern-dream-journal"
    )
}
```

`.claude/agent-slots.json` defines four slots (`claude-slot-1`, `codex-slot-1`, `gemini-slot-1`, `devin-slot-1`) with load-balancing weights, affinity rules, quota tracking, and fallback chains. None of this is loaded, parsed, or consulted at runtime. Every job whose `agent_type` is not `dream_journal` hits the `agent type not configured` warning at line 75 and is marked failed.

**Fix required:** On startup, read and parse `agent-slots.json`. Construct one `AgentController` per slot (keyed by `agent_type` / `id`). Apply affinity rules when selecting which slot to wake for a given job type.

---

## Bug 3 — No health check before assigning work; no fallback on wake failure

**File:** `services/dispatcher/dispatcher.py`, lines 81–85

When `agent.wake()` fails, jobs are immediately marked failed:

```python
if not agent.wake():
    logger.error(f"[ERROR] Failed to wake agent {agent_type}")
    for job in jobs:
        self.queue.mark_failed(job.job_id, "Agent wake failed")
    continue
```

`agent-slots.json` defines `quotaTracking.fallbackAgent` for every slot (e.g. `claude-slot-1` → `codex-slot-1` → `gemini-slot-1` → `claude-slot-1`). These fallback chains are never followed; a single failed wake permanently fails the batch.

Additionally, `agent.wake()` always tries to `docker start` even if the agent is already `AWAKE`. A pre-wake health check (or a guard on `agent.state`) should skip the wake attempt when the agent is already ready.

**Fix required:**
1. In `AgentController.wake()`, return `True` immediately (with no Docker call) when `self.state == AgentState.AWAKE`.
2. In `WorkDispatcher.dispatch_work()`, when a wake fails, look up the slot's `fallbackAgent` from the loaded slot config and retry on that agent before marking jobs failed.

---

## Bug 4 — `AgentController` state is in-process only; not PCSF-persistent

**File:** `services/dispatcher/agent_controller.py`

Agent state (`SLEEPING`, `WAKING`, `AWAKE`, `PROCESSING`) is held in-memory on the `AgentController` instance. If the dispatcher process restarts, all agents reset to `SLEEPING` and the state log is lost. There is no PCSF write-back of agent health or last-known state.

This is lower priority than bugs 1–3 but means health signals from `monitoring.alerts` in `agent-slots.json` (`slotUnhealthy → remove_from_pool`) can never be persisted or acted on across restarts.

**Fix required:** Write agent state transitions to a PCSF-compatible store (e.g. a JSON file under `csf/` or a Redis key) on each `log_state()` call. On `WorkDispatcher.__init__`, reload last-known state from that store before the first dispatch cycle.

---

## What a complete fix requires

| File | Change |
|---|---|
| `work_queue.py` | Fix `get_pending_jobs` filter to re-queue non-matching jobs, or move to per-type queues |
| `dispatcher.py` | Load `agent-slots.json` on init; build agent pool from slots; implement fallback chain on wake failure; respect affinity rules |
| `agent_controller.py` | Skip wake if already AWAKE; persist state to PCSF on each transition |
| New: `slot_loader.py` | Parse `agent-slots.json`, expose slot → fallback chain and affinity map |

Estimated diff: ~120–180 lines of net-new/changed code across four files. Not reducible below 50 lines without leaving one of the critical routing gaps open.

---

## Routing rules as they should work (from `agent-slots.json`)

1. Incoming job carries `agent_type` (maps to slot responsibilities).
2. Check affinity: `strategic_decisions → claude-slot-1`, `implementation_work → codex-slot-1`, `analysis_tasks → gemini-slot-1`, `engineering_work → devin-slot-1`.
3. If primary slot is healthy (`status == "ready"`, health-check passes), wake and assign.
4. If primary slot fails wake or is at quota (`quotaUtilization >= 0.80`), follow `fallbackAgent` chain until a healthy slot is found.
5. If all fallbacks exhausted, re-queue the job (do not mark failed) with a backoff timestamp.
6. After processing, persist updated token-usage and health state to PCSF.
