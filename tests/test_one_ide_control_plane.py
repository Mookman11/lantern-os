from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_one_ide_doc_names_canonical_surfaces_and_hff_anchors() -> None:
    text = read("docs/LANTERN-ONE-IDE-WORKSTREAM-CONTROL.md")
    required = [
        "Lantern One IDE",
        "C:\\tmp\\lantern-os",
        "C:\\Users\\alexp\\Documents\\gm-agent-orchestrator",
        "C:\\Users\\alexp\\Documents\\agent-worktrees",
        "POST /api/command",
        "BETTER product lane",
        "Show the state. Say the limit. Self-correct before acting.",
        "A door is a protocol boundary",
        "observe -> record -> compare -> propose -> human approve -> apply -> verify -> repeat",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []


def test_one_ide_status_probe_is_read_only_and_checks_drift_surfaces() -> None:
    text = read("scripts/Get-OneIdeStatus.ps1")
    required = [
        "read_only_preflight",
        "git -C $Path status --short --branch",
        "config\\local-services.json",
        "manifests\\cloud-mirrors.json",
        "manifests\\validation\\MCP-CONNECTOR-LATEST.json",
        "do_not_reset_clean_sync_or_dispatch_dirty_worktrees",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []

    blocked = ["git reset", "git clean", "start_agent", "sync_repository", "Move-Item"]
    present = [phrase for phrase in blocked if phrase in text]
    assert present == []
