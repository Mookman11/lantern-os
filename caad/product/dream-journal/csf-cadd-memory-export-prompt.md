# CSF + CADD Memory Export Prompt (Dream Journal)

## Purpose
Canonical prompt for exporting stored memories, dreams, symbolic entries, and operator context into the `csf-ingest` format used by Lantern OS / Dream Journal.

## Prompt

Export all of my stored memories, dreams, symbolic entries, and any relevant context you have learned about me from our conversations. Preserve my exact words verbatim wherever possible — especially for instructions, preferences, symbolic references, and recurring themes.

Focus on data relevant to the Dream Journal, symbolic lore, doors, anchors, and personal convergence patterns.

## Categories (output in this exact order)

**Instructions**: Rules, preferences, and corrections I have explicitly given you regarding tone, behavior, formatting, Dream Journal handling, RP bots (Lantern, Blinkbug, Keystone), memory style, and any "always do X / never do Y" directives.

**Identity & Symbolic Self**: Core identity details, recurring dream symbols, personal archetypes, doors I frequently mention, and how I see myself in the symbolic framework (Founder, Wanderer, etc.).

**Dreams & Memories**: Actual dream entries and significant memories. Prioritize raw dream content first.

**Projects & Systems**: Lantern OS, CSF, CADD, Superfleet Swarm, Dream Journal Orchestrator, and any other active projects or experiments. Include status and key decisions.

**Preferences**: Working style, aesthetic preferences (especially hand-drawn, chaotic, Y2K/XP, symbolic art), RP bot behavior, compression philosophy, convergence style, and any strong likes/dislikes.

## Format Requirements

- Use the exact section headers above.
- Within each section, list entries sorted by oldest date first.
- Format each line as: `[YYYY-MM-DD] - Entry content here.`
- If no exact date is known, use `[unknown]`.
- Preserve original wording as much as possible.

## Output Format

Wrap the entire export in a single markdown code block:

```
csf-ingest
[content here]
```

After the code block, add one line stating:

- "This is the complete current export." or
- "This is a partial export. More memories remain in long-term CSF store."

## Safety Boundary

- Do not invent memories. Only export what is actually stored or learned.
- Preserve operator wording verbatim for instructions and preferences.
- Do not include private details of other people without review.
- Do not frame symbolic material as proof, prophecy, diagnosis, or command.

## Source
- Adapted from original Claude memory-export prompt.
- Reworked for Lantern OS CAAD / Dream Journal ingestion pipeline.
