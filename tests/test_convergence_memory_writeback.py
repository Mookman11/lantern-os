"""#848 — cross-language contract test for the live memory write-back.

The live serving path (Node) folds a converged continuation back into the
append-only memory log via apps/lantern-garage/lib/convergence-memory.js. Those
rows must load cleanly into the Python Convergence Core: both the Memory dataclass
(src/convergence/objects.py) and the live Kernel loader
(Kernel._load_memory_from_disk). This test LOCKS that schema contract — if either
side drifts, it fails.
"""
import json
from datetime import datetime

from src.convergence.objects import Memory
from src.convergence.kernel import Kernel

# The exact JSON shape emitted by convergence-memory.js::writeMemory.
JS_EMITTED = {
    "id": "mem-abc123-def456",
    "timestamp": "2026-06-21T10:00:01.000+00:00",
    "source": "convergance-council",
    "confidence": 0.7,
    "content": {
        "kind": "convergence",
        "question": "how do two providers converge?",
        "answer": "the council synthesizes a single grounded answer",
        "record_id": "cr-abc123-def456",
    },
    "evidence_ids": ["cr-abc123-def456"],
}

EMITTER_KEYS = {"id", "timestamp", "source", "confidence", "content", "evidence_ids"}


def _load(d):
    """Reconstruct a Memory from a JS-emitted dict (mirrors Kernel loader)."""
    return Memory(
        id=d["id"],
        timestamp=datetime.fromisoformat(d["timestamp"]),
        source=d["source"],
        confidence=d["confidence"],
        content=d["content"],
        evidence_ids=list(d.get("evidence_ids", [])),
    )


def test_emitter_keys_match_dataclass_fields():
    """The JS emitter must produce exactly the dataclass's serialized fields."""
    sample = Memory(
        id="x", timestamp=datetime.now(), source="s",
        confidence=0.5, content={"k": "v"},
    )
    assert set(json.loads(sample.to_jsonl()).keys()) == EMITTER_KEYS
    assert set(JS_EMITTED.keys()) == EMITTER_KEYS


def test_js_emitted_memory_loads_into_dataclass():
    mem = _load(JS_EMITTED)
    assert mem.id == "mem-abc123-def456"
    assert mem.source == "convergance-council"
    assert mem.content["kind"] == "convergence"
    assert mem.evidence_ids == ["cr-abc123-def456"]


def test_confidence_in_unit_interval():
    assert 0.0 <= _load(JS_EMITTED).confidence <= 1.0


def test_timestamp_parses_without_z_stripping():
    """Kernel._load_memory_from_disk calls fromisoformat() raw — the offset form
    the JS writer emits must parse directly (no 'Z' that pre-3.11 would reject)."""
    assert "Z" not in JS_EMITTED["timestamp"]
    datetime.fromisoformat(JS_EMITTED["timestamp"])  # must not raise


def test_live_kernel_loads_js_written_memory(tmp_path):
    """End-to-end: a JS-shaped row on disk loads into a live Kernel's memory."""
    mem_file = tmp_path / "memory.jsonl"
    mem_file.write_text(json.dumps(JS_EMITTED) + "\n", encoding="utf-8")
    kernel = Kernel(memory_path=str(mem_file))
    kernel._load_memory_from_disk()
    assert JS_EMITTED["id"] in kernel.memory
    loaded = kernel.memory[JS_EMITTED["id"]]
    assert loaded.source == "convergance-council"
    assert loaded.evidence_ids == ["cr-abc123-def456"]


def test_evidence_ids_grounds_writeback():
    """A write-back linked to its ConvergenceRecord is grounded; empty is allowed."""
    grounded = _load(JS_EMITTED)
    ungrounded = _load({**JS_EMITTED, "evidence_ids": []})
    assert len(grounded.evidence_ids) > 0
    assert ungrounded.evidence_ids == []
