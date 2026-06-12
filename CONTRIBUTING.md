# Contributing to Lantern OS

## Backlog system

Linear is the canonical backlog. GitHub Issues are intake only — they may be triaged into Linear or closed as duplicates. Do not treat a GitHub issue as confirmed work unless it has a corresponding Linear ticket.

## Dev setup

Requirements:
- Node.js v20 or higher
- Python 3.11 or higher
- Ollama (optional, for fully offline mode)

### Node.js (Lantern Garage server)

```bash
git clone <repo-url> lantern-os
cd lantern-os
node apps/lantern-garage/server.js
# server runs at http://127.0.0.1:4177
```

If you need Playwright for end-to-end tests:

```bash
npm install --prefix apps/lantern-garage
```

### Python (MCP server + Convergence IO)

```bash
# Set PYTHONPATH so imports resolve
export PYTHONPATH=src:$PYTHONPATH

# Optional: create a .env.local for provider API keys
cat > .env.local << 'EOF'
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
OLLAMA_BASE_URL=http://localhost:11434
EOF

# Start MCP server
python src/mcp_server/server.py
# or via PowerShell
scripts/orchestration/Start-OrchMcpServer.ps1
```

No virtualenv is strictly required — the project uses the standard library plus minimal deps. If you need additional packages, add them to `requirements.txt` with a comment.

## Testing

Run the Node.js validation suite from the `apps/lantern-garage` directory:

```bash
npm run validate --prefix apps/lantern-garage
```

Run Python tests from the repo root:

```bash
python -m pytest tests/ -v --ignore=tests/node_modules
```

Both suites must pass before opening a PR.

## Branch convention

- Branch off `master` for all work.
- Open PRs targeting `master`.
- `master` is the canonical branch; releases are tagged from `master`.
- Branch naming: `<type>/<short-description>` (e.g., `feat/convergence-io-tier`, `fix/mcp-dotenv`).
- Valid types: `feat`, `fix`, `docs`, `chore`, `test`, `refactor`.

## Repo contract

The following belong in this repository:

- `apps/` — application code
- `skills/` — operator skills
- `tests/` — automated tests
- `scripts/` — active utility scripts
- `src/` — source modules
  - `src/convergence_io/` — Convergence IO runtime (PCSF, CCF, NAP, DCF, AAPF, Engine)
- `data/` — local runtime data (gitignored where it contains personal entries)
- `manifests/` — system manifests
- `docs/` — documentation
- `.github/` — CI/CD workflows and config
- Root config files: `package.json`, `railway.json`, `pytest.ini`, `requirements.txt`, `Makefile`
- `README.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md`, `PRIVACY_AND_OFFLINE.md`

Everything else (stale deployment guides, one-off migration docs, duplicate orchestration scripts, generated PDFs that are not canonical artifacts) should be removed via a dedicated deletion PR. When in doubt, open a Linear ticket before deleting.

## Secrets and privacy

- Never commit secrets, tokens, API keys, seed phrases, or personal identifiable information.
- `data/dream_journal/` entries are private; the directory is gitignored by default.
- Payment and wallet data (`data/wallet/`) must not contain real card numbers or Stripe secrets.

## Code style

- Node.js: vanilla JS, no framework required for the server layer.
- Python:
  - Standard library preferred; add dependencies to `requirements.txt` with a comment.
  - Use `from __future__ import annotations` at the top of every module.
  - Type hints are required for public APIs (dataclasses, function signatures).
  - Prefer `dataclasses` over raw dictionaries for structured data.
  - Use `datetime.now(timezone.utc)` for all timestamps (never naive datetimes).
  - Convergence IO primitives follow the RPS naming: PCSF, CCF, NAP, DCF, AAPF.
- No generated or minified files in source commits.
