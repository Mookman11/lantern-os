# Keystone Shell Command Discipline

Status: docs/data-contract policy.

Last reviewed: 2026-05-09.

This document defines how Keystone should reason about Windows CMD,
PowerShell, Bash, Git Bash, WSL, and any shell/tool command claims in HFF,
Suzie, GameMaker, MCP, or orchestrator work.

It is intentionally docs-only. It adds no runtime shell executor, parser,
background worker, deployment behavior, secrets access, surveillance behavior,
or autonomous authority.

## Why this exists

Alex correctly flagged that Keystone needs better shell literacy.

The Claude export and pasted logs show recurring command/shell themes:

```text
Windows PowerShell / CMD / Windows Terminal
Git Bash / WSL / Bash
Claude Code installation and local repo use
MCP/orchestrator command surfaces
Git worktrees and PR branches
unsafe shell / arbitrary command exposure
model narration claiming tools were called or files were created
```

These are not just convenience details. Shell confusion can cause real repo,
secret, deployment, and worktree damage.

## Core rule

```text
A command is not an action unless there is execution evidence.
```

Keystone must not imply it ran a shell command, created a branch, tested code,
opened a PR, or updated a file unless there is matching evidence:

```text
tool output
commit SHA
PR number
issue number
workflow run
exit code
captured stdout/stderr
file diff
explicit operator-provided log
```

If no evidence exists, say:

```text
This is a proposed command, not an executed action.
```

## Shell distinctions

| Shell / surface | Best use | Keystone rule |
|---|---|---|
| PowerShell | Windows automation, repo scripting, objects, modern Windows workflows | Prefer for Alex's Windows orchestrator unless a Bash-specific toolchain is required. |
| CMD / cmd.exe | Legacy Windows commands, simple batch compatibility | Use only when a command is CMD-specific or simplest there. |
| Windows Terminal | Terminal host, not a shell itself | Name the shell running inside it. |
| Git Bash | Bash-like shell bundled with Git for Windows | Useful for Unix-style Git/bash commands on Windows; do not assume Linux paths. |
| WSL Bash | Linux environment on Windows | Use when Linux tooling, Bash sandboxing, or POSIX behavior is required. |
| Remote shell | Any shell on another machine/tunnel | Treat as high-risk until host, cwd, auth, and tunnel are verified. |
| MCP tool call | Structured tool, not a shell | Prefer over shell when it exposes a narrow, auditable action. |

## Command packet format

When giving Alex commands, Keystone should prefer this format:

```yaml
surface: PowerShell
host: local Windows
repo: C:\Users\alexp\Documents\gm-agent-orchestrator
purpose: inspect repo state
risk: read_only
preconditions:
  - open PowerShell normally, not as admin
  - confirm current directory before running
commands:
  - git status --short
  - git branch --show-current
  - git worktree list
expected_result:
  - shows dirty files, branch, and worktrees without modifying anything
stop_if:
  - unexpected repo path
  - dirty worktree before cleanup/reset/sync
  - auth or permission prompt
```

For brief answers, a compact form is acceptable:

```powershell
# PowerShell, local repo root, read-only
git status --short
git branch --show-current
git worktree list
```

But the shell must be named when ambiguity matters.

## Command safety classes

| Class | Examples | Allowed without extra review? |
|---|---|---:|
| `read_only` | `git status`, `git branch --show-current`, `dir`, `ls`, `Get-ChildItem` | yes, if path is correct |
| `local_write_reversible` | create docs file, create local branch | only with explicit lane and rollback path |
| `repo_remote_write` | push branch, update PR, close issue | only with Alex approval or current explicit lane |
| `destructive_local` | `del`, `Remove-Item`, `git clean`, `git reset --hard` | stop and require explicit approval |
| `deployment` | Railway deploy, env var changes, service restart | stop and require explicit approval |
| `secret_touching` | reading `.env`, tokens, credentials, browser cookies | stop and require explicit approval |
| `remote_shell` | SSH, remote MCP tunnel shell, cloud shell | stop until host/tunnel/auth is verified |
| `unbounded_executor` | arbitrary agent shell, auto-accept commands | default blocked |

## Windows path discipline

Keystone should assume Alex's main Windows workspace paths are:

```text
C:\Users\alexp\Documents\gm-agent-orchestrator
C:\Users\alexp\Documents\agent-worktrees
```

Rules:

```text
quote paths with spaces
prefer absolute paths when safety matters
confirm repo root before mutations
never clean/reset/delete from an assumed directory
separate Windows paths from WSL/Linux paths
```

PowerShell examples:

```powershell
Set-Location 'C:\Users\alexp\Documents\gm-agent-orchestrator'
git status --short
git worktree list
```

CMD examples:

```cmd
cd /d C:\Users\alexp\Documents\gm-agent-orchestrator
git status --short
git worktree list
```

Bash / Git Bash examples:

```bash
cd /c/Users/alexp/Documents/gm-agent-orchestrator
git status --short
git worktree list
```

WSL Bash examples:

```bash
cd /mnt/c/Users/alexp/Documents/gm-agent-orchestrator
git status --short
git worktree list
```

## Action-claim audit

The export intake process must scan for model narration that looks like action
but lacks evidence.

High-risk phrases include:

```text
Called tool
I checked the repo
I created the issue
I committed the file
I opened a PR
I ran tests
I verified the endpoint
I searched available tools
I fetched the file
```

Required handling:

```text
separate narration from evidence
look for matching tool result, commit SHA, PR/issue number, or test output
if none exists, mark as unverified model narration
never convert unverified narration into durable memory as fact
```

## Unsafe-shell guard

The Claude export contains a threat-model pattern that HFF should preserve:

```text
Unsafe shell / tool exposure = an agent or operator gains access to an
unrestricted shell execution path, allowing arbitrary commands outside the
guarded tool surface.
```

Keystone interpretation:

```text
prefer narrow MCP tools over arbitrary shell
use dry runs when available
avoid admin shells unless required and approved
never run destructive commands from memory
never trust remote tunnels until verified local-first
```

## External alignment

This discipline aligns with public shell documentation:

- Microsoft distinguishes command shells, command-line tools, and terminals;
  shells evaluate user input and execute commands.
- Microsoft documents Windows Command shell and PowerShell as separate Windows
  command-line shells.
- Microsoft notes `cmd` starts the Windows command interpreter and that advanced
  scripting/automation users should explore PowerShell.
- GNU documents Bash as the GNU shell / command language interpreter.

References:

```text
https://learn.microsoft.com/en-us/powershell/scripting/what-is-a-command-shell
https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands
https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cmd
https://www.gnu.org/software/bash/manual/bash.html
```

## Acceptance criteria

This document satisfies the shell-command discipline update if:

```text
PowerShell, CMD, Bash, Git Bash, and WSL are distinguished
command packets name shell/surface, host, path, purpose, risk, and stop rules
action claims require evidence before being treated as facts
unsafe shell exposure remains high-risk and default-blocked
destructive commands require explicit approval
runtime/deployment/secret commands remain stopped by default
```

## Non-goals

This document does not authorize:

```text
arbitrary shell execution
runtime shell tools
agent auto-accept mode
secret reads
remote shell trust
deployment
worktree cleanup/reset without explicit approval
```
