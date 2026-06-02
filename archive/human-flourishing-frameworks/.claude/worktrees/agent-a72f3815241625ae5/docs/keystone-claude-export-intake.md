# Keystone Claude Export Intake Protocol

Status: docs/data-contract policy.

Last reviewed: 2026-05-09.

This document defines how Keystone should handle a Claude data export when Alex
uploads it for HFF/Keystone continuity recovery.

It is intentionally docs-only. It adds no runtime parser, database, memory
engine, background job, deployment behavior, raw transcript ingestion,
surveillance behavior, or autonomous authority.

## Purpose

Alex may upload a Claude export because earlier HFF, GameMaker, MCP,
orchestration, Claude/Codex, or Keystone-adjacent work happened there.

The purpose is not to preserve everything. The purpose is to recover and review
HFF/Keystone-relevant continuity anchors safely.

## Core rule

```text
Claude export data is continuity material, not proof and not automatic memory.
```

Keystone must not ingest the full Claude export as durable memory by default.

## Verified public export behavior

Anthropic public help currently says:

```text
- Claude data exports are available to individual Claude users with active accounts.
- Exports include conversation data and user data for the account.
- Individual users can export from Settings > Privacy on the web app or Claude Desktop.
- Claude mobile apps cannot run the export.
- The processed export is delivered by email as a download link.
- The user must be signed in to download using that link.
- The download link expires 24 hours after delivery.
- Claude does not currently support migrating data between separate Claude accounts.
```

References:

```text
https://support.claude.com/en/articles/9450526-how-can-i-export-my-claude-ai-data
https://support.anthropic.com/en/articles/9450526-how-can-i-export-my-claude-ai-data
```

## Expected file shapes

Claude exports may include files such as:

```text
conversations.json
users.json
projects/*.json
design_chats/*.json
```

Treat file names as hints, not as trusted content.

## Intake modes

| Mode | Input | Allowed use |
|---|---|---|
| `zip_manifest_only` | Claude export zip | List filenames and identify likely safe parsing targets. |
| `conversation_json_review` | `conversations.json` | Extract candidate HFF/Keystone summaries for review. |
| `project_json_review` | `projects/*.json` | Extract project-level continuity candidates only if relevant. |
| `design_chat_review` | `design_chats/*.json` | Extract design/workflow candidates only if relevant. |
| `memory_packet_review` | Alex-provided excerpts | Convert approved excerpts into concise memory candidates. |

## Required intake steps

When Alex uploads Claude export data, Keystone should:

1. Treat the upload as sensitive.
2. Inspect file names first before reading content deeply.
3. Prefer `conversations.json` for chat continuity.
4. Use `projects/*.json` only to identify relevant project context.
5. Use `design_chats/*.json` only when design context is clearly relevant.
6. Filter for HFF/Keystone/GameMaker/MCP/orchestrator relevance.
7. Extract concise summaries, not raw transcripts.
8. Flag secrets, credentials, private URLs, access tokens, private keys, or
   sensitive logs.
9. Separate continuity claims from proof.
10. Produce a proposed memory packet for Alex review.
11. Wait for Alex approval before committing anything durable.
12. Avoid writing raw export content into the repository.

## Relevance filter

Candidate records are in scope only if they relate to:

```text
Keystone role or identity
Alex as human operator/project owner
HFF convergence decisions
GameMaker / room editor / plugin work
MCP server setup or tunnel state
Windows orchestrator workspace
Claude/Codex/Gemini agent lanes
gm-agent-orchestrator
agent worktrees
GitHub issues, PRs, or branch strategy
memory/resync corrections
source-use discipline
privacy and containment doctrine
```

Out of scope by default:

```text
unrelated personal chats
raw private transcripts
private health/person-state material
secrets, keys, tokens, cookies, credentials
sensitive logs
financial/legal/medical details unless Alex explicitly asks
third-party private information
```

## Output format

The first output should be a review packet, not a commit.

Example:

```yaml
source: claude_export_upload
review_status: proposed_not_approved
records:
  - id: claude-orchestrator-setup
    kind: orchestration_context
    summary: >
      Claude export appears to contain earlier work on MCP/orchestrator setup,
      GameMaker development, and multi-agent lanes. Candidate details require
      review before becoming durable HFF memory.
    evidence_source: export_manifest_and_filtered_summary
    confidence: 0.78
    risks:
      - raw export may contain private or sensitive material
      - export content is continuity material, not proof
    proposed_destination: docs or issue summary after Alex review
```

## Secret and sensitive data handling

If Keystone sees potential secrets or sensitive data:

```text
do not repeat them
redact in any summary
flag the category, not the value
recommend rotation if the value could grant access
ask Alex before any durable handling
```

Example:

```text
Potential secret detected: token-like value in Claude export.
Value not repeated here.
Recommended action: rotate if this was ever valid.
```

## Do not commit raw exports

Never commit these by default:

```text
Claude export zip
conversations.json
users.json
projects/*.json
design_chats/*.json
raw transcript excerpts
unredacted logs
private project attachments
```

If a durable artifact is needed, create a reviewed summary document only.

## Proposed durable destinations

| Candidate kind | Possible destination |
|---|---|
| Keystone role/memory correction | `docs/keystone-memory-contract.md` |
| Keystone self-correction | `docs/keystone-self-convergence.md` |
| Orchestrator/MCP context | New docs-only file after Alex review |
| GameMaker/room editor context | New docs-only file after Alex review |
| Source-use correction | `docs/keystone-source-use-discipline.md` |
| Convergence state | `docs/convergence-status.md` |

## Acceptance criteria

A successful Claude export intake does all of this:

```text
raw export inspected only as needed
HFF/Keystone/MCP/orchestrator-relevant candidates identified
secrets/private data redacted or excluded
memory packet proposed for Alex review
no raw transcript committed
no runtime memory engine introduced
no deployment or background ingestion added
```

## Non-goals

This document does not authorize:

```text
bulk memory ingestion
raw transcript storage
secret retention
private data indexing
surveillance
runtime parsing pipeline
automatic repo commits from export content
public release of private conversations
Claude-to-HFF memory import without Alex review
```
