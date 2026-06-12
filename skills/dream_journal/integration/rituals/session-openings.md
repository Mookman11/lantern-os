# Dream Journal Session Rituals

Status: integrated (no quarantine)
Date: 2026-06-02

---

## What Is a Session Ritual?

A ritual is a structured sequence that opens and closes a Dream Journal session. It is not magic. It is a pattern that signals to the operator (and the system) that a session has begun, what mode it is in, and how it will close.

Rituals live in `integration/rituals/`. They are referenced by the Dream Journal core but are not hard-coded into it.

---

## Opening Rituals

### 1. The Three-Breath Opening

```text
1. Operator states intention: "I am here to log / explore / integrate."
2. System suggests a door based on recent patterns (optional).
3. Operator breathes three times.
4. Session begins.
```

Use case: Standard entry. Works for logging, exploration, or synthesis.

### 2. The Door-Knock Opening

```text
1. Operator names a door: "I enter through the Lantern Door."
2. System loads the corresponding prompt archetype.
3. Operator knocks (metaphorically or literally — a physical tap on the desk).
4. Session begins with that door's tone.
```

Use case: When the operator knows what mode they need.

### 3. The Emergency Opening

```text
1. Operator states: "Emergency entry. No ritual."
2. System bypasses all prompts and opens a raw log.
3. Operator logs the dream immediately.
4. System tags it as "emergency" for later review.
```

Use case: Vivid dream that will fade. Speed over structure.

---

## Closing Rituals

### 1. The Return Door Close

```text
1. System asks: "What one thing wants to come with you?"
2. Operator names an anchor.
3. System records the anchor as a tag on the session.
4. System says: "You can always come home safe."
5. Session ends.
```

Use case: Standard close. Ensures memory anchoring.

### 2. The Lantern Close

```text
1. System generates a mirror prompt using the session's content.
2. Operator reads it (does not have to respond).
3. System asks: "Does this feel true?"
4. Operator answers yes/no/maybe.
5. Session ends.
```

Use case: When the operator wants interpretation before closing.

### 3. The Broken Spine Close

```text
1. System asks: "What truth from this session feels hard to carry?"
2. Operator names it (or says "nothing").
3. System records it as a shadow tag.
4. System says: "You do not have to carry it alone."
5. Session ends.
```

Use case: Difficult dreams, high-emotion sessions.

---

## Ritual Selection Logic

```python
def suggest_ritual(recent_dreams, operator_state=None):
    """Suggest opening and closing ritual based on context."""
    if operator_state and operator_state.get("urgent"):
        return "emergency_open", "return_close"

    avg_lucidity = sum(d.get("lucidity", 0) for d in recent_dreams) / max(len(recent_dreams), 1)
    shadow_tags = sum(1 for d in recent_dreams if "shadow" in d.get("tags", []))

    if avg_lucidity > 0.8:
        return "door_knock_open", "lantern_close"
    elif shadow_tags >= 2:
        return "door_knock_open", "broken_spine_close"
    else:
        return "three_breath_open", "return_close"
```

---

## Integration Note

Rituals are optional. The Dream Journal works without them. But when used, they create a predictable container that makes the symbolic work feel safe and intentional.
