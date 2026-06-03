#!/usr/bin/env python3
"""Agent Self-Monitor — lightweight health check for Lantern OS agents.

Checks provider config, garage server, fleet slots, CSF health,
dream journal entries, and dispatcher status. Outputs JSON + human summary.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

PROVIDERS = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "groq": "GROQ_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "ollama": "OLLAMA_BASE_URL",
}


def check_providers() -> dict:
    return {name: bool(os.environ.get(env)) for name, env in PROVIDERS.items()}


def check_garage_server() -> dict:
    url = "http://127.0.0.1:4177/api/agent/status"
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            return {"running": True, "status_code": resp.status}
    except Exception as e:
        return {"running": False, "error": str(e)}


def check_fleet_slots() -> dict:
    fleet_dir = DATA / "agent-fleet"
    if not fleet_dir.exists():
        return {"exists": False, "files": []}
    files = list(fleet_dir.iterdir())
    return {"exists": True, "file_count": len(files), "files": [f.name for f in files]}


def check_csf_health() -> dict:
    csf_files = list(DATA.rglob("*.csf"))
    results = []
    for f in csf_files:
        content = f.read_bytes()
        results.append({
            "path": str(f.relative_to(ROOT)),
            "size": len(content),
            "sha256": hashlib.sha256(content).hexdigest()[:16],
        })
    return {"count": len(csf_files), "files": results}


def check_dream_journal() -> dict:
    dj_dir = DATA / "dream_journal"
    if not dj_dir.exists():
        return {"exists": False, "entry_count": 0}
    total = 0
    files = []
    for jl in sorted(dj_dir.glob("*.jsonl")):
        lines = [l for l in jl.read_text().splitlines() if l.strip()]
        total += len(lines)
        files.append({"file": jl.name, "entries": len(lines)})
    return {"exists": True, "entry_count": total, "files": files}


def check_dispatcher() -> dict:
    status_file = DATA / "status" / "super-jarvis-fleet.json"
    if not status_file.exists():
        return {"exists": False}
    try:
        data = json.loads(status_file.read_text())
        return {"exists": True, "data": data}
    except json.JSONDecodeError as e:
        return {"exists": True, "parse_error": str(e)}


def main() -> None:
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "providers": check_providers(),
        "garage_server": check_garage_server(),
        "fleet_slots": check_fleet_slots(),
        "csf_health": check_csf_health(),
        "dream_journal": check_dream_journal(),
        "dispatcher": check_dispatcher(),
    }

    # Write JSON report
    out_dir = DATA / "status"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "agent-monitor-latest.json"
    out_path.write_text(json.dumps(report, indent=2))

    # Human-readable summary
    print("=== Lantern OS Agent Self-Monitor ===")
    print(f"Timestamp: {report['timestamp']}")

    print("\nProviders:")
    for name, configured in report["providers"].items():
        status = "configured" if configured else "not set"
        print(f"  {name:<12} {status}")

    gs = report["garage_server"]
    print(f"\nGarage Server: {'RUNNING' if gs['running'] else 'DOWN'}")

    fs = report["fleet_slots"]
    print(f"Fleet Slots: {fs.get('file_count', 0)} files")

    csf = report["csf_health"]
    print(f"CSF Files: {csf['count']} files")
    for f in csf["files"]:
        print(f"  {f['path']} ({f['size']} bytes, sha256:{f['sha256']})")

    dj = report["dream_journal"]
    print(f"Dream Journal: {dj['entry_count']} entries")

    disp = report["dispatcher"]
    print(f"Dispatcher: {'found' if disp['exists'] else 'not found'}")

    print(f"\nReport written to: {out_path}")


if __name__ == "__main__":
    main()
