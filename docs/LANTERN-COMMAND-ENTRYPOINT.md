# Lantern Command Entrypoint

Status: local-first command contract.

All chat commands use one entrypoint:

```text
POST /api/command
```

| Command | Local behavior | Cloud behavior |
|---|---|---|
| `!one` | Runs `scripts/Get-OneIdeStatus.ps1` as a read-only preflight. | Held; points back to local Lantern Garage. |
| `!converge` | Runs `scripts/Invoke-LanternConvergenceLoop.ps1`. | Held; convergence requires local repo/MCP evidence. |
| `!superjarvis` | Runs `scripts/Invoke-SuperJarvisPerfectLoop.ps1 -Passes 1`. | Held; diagnostics require local PowerShell/MCP. |

## Token Discipline

The command table is the stable prefix. Dynamic state comes from tool output and
receipts. That keeps chat short, avoids repeating scattered instructions, and
matches OpenAI guidance for cheaper GPT-5.5 operation: use lower reasoning
effort when enough, control verbosity, compact long-running state, defer large
tool catalogs, and keep stable prompt content before dynamic user context so
prompt caching can reduce latency and input-token cost.

Source: https://developers.openai.com/api/docs/guides/latest-model#using-reasoning-models

## Revenue Demo Rule

`!converge` should keep the one-hour revenue demo honest: direct invoice service
pilot first, no fake cleared cash, no hidden payment tokens, and no public cloud
claim until the AWS service URL passes `/`, `/api/health`, and
`/api/cloud-mirrors`.
