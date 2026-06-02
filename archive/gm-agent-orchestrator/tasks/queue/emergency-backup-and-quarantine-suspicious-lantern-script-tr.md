# Emergency backup and hold suspicious Lantern script trees

Priority: P0
Owner: human
Created: 2026-05-14T11:48:24Z
Source: connector-action

# Emergency
Operator reports local Lantern/HFF script echoes may be poisoned and requested backup + help.

# Suspect local script trees
- `C:\tmp\human-flourishing-frameworks-scan\.claude\worktrees\agent-a72f3815241625ae5\scripts`
- `C:\tmp\hff-lantern-recovery\scripts`

# Immediate rule
Do not run scripts from either path. Treat outputs/echoes from those trees as untrusted until backed up and reviewed.

# Safe backup target
Create timestamped, read-only evidence copies under a neutral directory, for example:
`C:\tmp\lantern-emergency-backup\YYYYMMDD-HHMMSS\`

# Manual backup command for operator
Use PowerShell copy operations only; do not execute files from source directories.

# Acceptance checks
1. Capture directory listings, file hashes, and recursive copies of both suspect script directories.
2. Store a manifest with timestamp, machine path, and hash list.
3. Do not delete, reset, clean, sync, or overwrite anything.
4. Do not start agents from poisoned paths.
5. After backup, review scripts for network calls, command execution, tunnel startup, sensor activation, file deletion, or impersonation/dehumanization claims.

# Validation path
- Verify backup exists.
- Verify manifest exists.
- Verify source and backup file counts match.
- Review before any execution.
