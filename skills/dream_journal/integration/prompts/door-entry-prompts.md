# Door Entry Prompts for Dream Journal

Status: integrated (no quarantine)
Date: 2026-06-02

---

## How to Use

Each prompt is a template. Fill `{context}` with recent dreams, current life events, or operator state. The prompt then feeds into the Dream Journal's `mirror_prompt()` or directly to an LLM interpreter.

---

## Return Door Prompt

```text
You are at the Return Door. This is the threshold between dream and waking.

Before you step through, name one thing from your dream that wants to come with you.
Not the whole dream. One thing. A color, a feeling, a word, a face.

That one thing is your anchor. It is proof that the dream was not wasted.

Recent dream context: {context}

What is your anchor?
```

## Lantern Door Prompt

```text
You hold a lantern. Its light does not reveal everything. It reveals enough.

Look at your dream again. What is the lantern trying to show you that your waking eyes missed?
Not the obvious meaning. The sideways meaning. The meaning that lives in the corner of the dream.

Recent dream context: {context}

What does the lantern see?
```

## Broken Spine Door Prompt

```text
This door is cracked. It hurts to open. But it is the only door that leads to what you have been avoiding.

Your dream contains something your waking mind does not want to know. Not a threat. A truth.
Name it without judgment. You do not have to act on it. You only have to see it.

Recent dream context: {context}

What truth is this dream protecting you from seeing?
```

## Mirror Door Prompt

```text
You stand before a mirror. The mirror shows you as you are in the dream, not as you are in waking life.

If someone who loves you saw this dream, what would they see that you cannot?
Not what they would say. What they would see.

Recent dream context: {context}

What does the mirror show?
```

## Safe Door Prompt

```text
This door leads to a room with no stakes. No judgment. No interpretation required.

Your dream is yours alone in this room. It does not need to mean anything. It does not need to be analyzed.
What does it want to play with? What color, what shape, what sensation wants to move around freely?

Recent dream context: {context}

What does the dream want to play with?
```

## XP Door Prompt

```text
This door is labeled "DO NOT ENTER" in a language you are not supposed to understand.

Your dream breaks a rule. Whose rule? A waking rule? A personal rule? A cosmic rule?
What truth lives in the breakage? What becomes possible because something was broken?

Recent dream context: {context}

What rule does this dream break, and what truth lives there?
```

## Convergence Door Prompt

```text
This door opens onto a landscape made of all your recent dreams stitched together.

Look across the last {session_count} sessions. One thread wants to be woven. One symbol repeats. One emotion deepens. One question refuses to be answered.

Recent dream context: {context}

What single thread wants to be woven?
```

---

## Usage in Code

```python
from skills.dream_journal.dream_journal import DreamJournal
from skills.dream_journal.integration.prompts import door_entry_prompts

dj = DreamJournal()
recent = dj.get_recent(7)
context = "\n".join([d["content"] for d in recent[-3:]])

prompt = door_entry_prompts.RETURN_DOOR.format(context=context)
# Feed to mirror_prompt() or external interpreter
```
