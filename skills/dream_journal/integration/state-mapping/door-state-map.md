# Door → Technical State Mapping

Status: integrated (no quarantine)
Date: 2026-06-02

---

## Core Principle

Symbolic doors are not just metaphors. They are functional labels that the Dream Journal core module uses to adjust behavior. This file documents the mapping between symbolic door names and technical state changes.

---

## Door → State Mapping Table

| Door | Symbolic Meaning | Technical State Change | Affects |
|------|-----------------|----------------------|---------|
| **Return Door** | Safe return, memory anchor | `session.close_anchor = True` | Adds anchor tag to session; triggers memory consolidation prompt |
| **Lantern Door** | Guidance, interpretation | `session.mode = "interpretive"` | Enables mirror prompt generation; loads Bayesian trend analysis |
| **Broken Spine Door** | Shadow confrontation | `session.mode = "shadow"` | Sets `emotion_weight = 2.0`; flags for later review; disables public sharing |
| **Mirror Door** | External reflection | `session.mode = "reflective"` | Enables external interpreter feed; anonymizes content before export |
| **Safe Door** | Protected play | `session.mode = "sandbox"` | Disables all external feeds; private-only storage; no analysis prompts |
| **XP Door** | Creative disruption | `session.mode = "disruptive"` | Enables unexpected tag suggestions; triggers pattern-breaker analysis |
| **Convergence Door** | Pattern synthesis | `session.mode = "synthetic"` | Enables multi-dream trend analysis; SFI vector update; goal linkage |

---

## State Machine

```
[SESSION START]
    |
    v
[Operator chooses door OR system suggests door]
    |
    v
[Door sets session.mode and session.flags]
    |
    v
[Core module adjusts behavior based on mode]
    |
    +-- interpretive -> mirror_prompt() enabled
    +-- shadow -> emotion_weight up, review flag set
    +-- reflective -> external feed enabled
    +-- sandbox -> all feeds disabled
    +-- disruptive -> pattern-breaker tags enabled
    +-- synthetic -> trend analysis enabled
    |
    v
[Dream logging happens]
    |
    v
[Closing ritual reads session.mode and behaves accordingly]
    |
    v
[SESSION END]
```

---

## JSON Schema for Session State

```json
{
  "session_id": "sess_20260602_143022",
  "door": "lantern",
  "mode": "interpretive",
  "flags": {
    "close_anchor": false,
    "shadow_review": false,
    "private_only": false,
    "external_feed": true,
    "pattern_breaker": false,
    "trend_analysis": false
  },
  "emotion_weight": 1.0,
  "suggested_prompts": ["lantern-door-prompt-v1"]
}
```

---

## Code Integration

```python
# In core/dream_journal.py or future session manager

DOOR_STATE_MAP = {
    "return": {"mode": "anchor", "close_anchor": True, "emotion_weight": 1.0},
    "lantern": {"mode": "interpretive", "external_feed": True, "emotion_weight": 1.0},
    "broken_spine": {"mode": "shadow", "shadow_review": True, "emotion_weight": 2.0, "private_only": True},
    "mirror": {"mode": "reflective", "external_feed": True, "emotion_weight": 1.0},
    "safe": {"mode": "sandbox", "private_only": True, "external_feed": False, "emotion_weight": 1.0},
    "xp": {"mode": "disruptive", "pattern_breaker": True, "emotion_weight": 1.2},
    "convergence": {"mode": "synthetic", "trend_analysis": True, "emotion_weight": 1.0},
}

def open_session(door_name: str) -> dict:
    return DOOR_STATE_MAP.get(door_name, DOOR_STATE_MAP["return"])
```

---

## Why This Matters

Without this mapping, the symbolic doors would be just pretty words. With it, they become functional labels that the system can act on. The symbolic layer and the technical layer are not separate. They are the same thing, viewed from different angles.
