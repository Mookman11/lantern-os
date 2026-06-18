# CSF Format Specification (canonical, consolidated)

**CSF** = Convergence-Fitted Searchable Format — Lantern OS's binary container
family for memory, symbolic data, and (as of v0.8) **arbitrary files**.

This is the single canonical spec. It consolidates the previously-scattered CSF
documentation (whitepaper, backend notes, CADD, code docstrings) and supersedes
the dead `CSF-FORMAT-SPECIFICATION.md` reference that `header.py` and the
Knowledge Center pointed at.

---

## 1. Version lineage

| Version | Magic | Purpose | Reference code |
|---|---|---|---|
| **v0.3** | `CSF\0` | Symbolic memory: world-model anchors + delta stream + dictionary | [`src/csf/csf_file.py`](../src/csf/csf_file.py) |
| **v0.7** | — | Symbolic compression engine (quantum-dust, base-3, qutrit delta) | [`src/csf/v07/`](../src/csf/v07/) |
| **v1 (segmented)** | `CSFv1\0\0\0` | Segment-table container (index, converged, encrypted, streaming flags) | [`src/csf/header.py`](../src/csf/header.py) |
| **v0.8 — CSF-Pack** | `CSF\0` | **General-purpose archive: pack/unpack arbitrary files** | [`src/csf/csf_pack.py`](../src/csf/csf_pack.py) |

> The symbolic formats (v0.3 / v0.7) encode Lantern's memory model. **CSF-Pack
> (v0.8) is the new Σ₀ release for wrapping *any* bytes** — code, data, models,
> exports — with hashing, optional compression, and an integrity footer.

---

## 2. CSF-Pack (v0.8) — arbitrary-file container

### 2.1 Binary layout

```
[Magic        4 bytes : b"CSF\x00"]
[Version      2 bytes : major, minor = 0, 8]
[Flags        2 bytes : bit0 = blobs zlib-compressed]
[ManifestLen  4 bytes : uint32 BE]
[Manifest     N bytes : UTF-8 JSON]
[Blob region  M bytes : concatenated (optionally compressed) file bytes]
[Footer      40 bytes : sha256(all preceding bytes) (32) + total size uint64 BE (8)]
```

### 2.2 Manifest JSON

```json
{
  "format": "csf-pack", "version": "0.8", "created_at": 1750000000.0,
  "compressed": true, "file_count": 3,
  "files": [
    {"path": "src/a.txt", "size": 1050, "csize": 60,
     "sha256": "…", "offset": 0, "compressed": true}
  ]
}
```
- `path` — POSIX-relative arc path (directory structure preserved on unpack).
- `size`/`csize` — original / stored byte length; `offset` is relative to the blob region.
- `sha256` — digest of the **original** bytes; verified on unpack.

### 2.3 Integrity & safety
- **Footer digest** (sha256 of everything before the footer) is verified *before*
  the manifest is parsed — any tampering fails with a clean integrity error.
- **Per-file sha256** is verified on extraction.
- **Path traversal** (`..`, absolute paths) is rejected on unpack (`_safe_join`).

### 2.4 API

```python
from csf import csf_pack
csf_pack.pack(["mydir", "file.bin"], "out.csf", compress=True)   # -> manifest
csf_pack.list_archive("out.csf")                                  # -> manifest (no extract)
csf_pack.unpack("out.csf", "dest_dir")                            # -> [written paths]
```

### 2.5 CLI

```bash
python -m csf.csf_pack pack <paths...> -o out.csf [--no-compress]
python -m csf.csf_pack unpack out.csf -d <dest_dir>
python -m csf.csf_pack list out.csf
```

Tests: [`tests/test_csf_pack.py`](../tests/test_csf_pack.py) (round-trip ×2,
list, tamper-detection, traversal).

---

## 3. Legacy / symbolic formats (brief)

### 3.1 v0.3 symbolic (`csf_file.py`)
`[Magic CSF\0][Version 2][Flags 2][Baseline][Dictionary][Delta stream][Footer]`.
Encodes world-model anchors (Garden, Lantern, Convergence…) via a
`SymbolicDictionary` + `DeltaStream`. Used for memory exports.

### 3.2 v1 segmented (`header.py`)
72-byte header (`CSFv1\0\0\0`, version, flags, segment_count, sizes, checksum) +
segment table + `ENDCSF`+CRC-32C footer. Flags: `HAS_INDEX`, `CONVERGED`,
`ENCRYPTED`, `STREAMING`.

### 3.3 v0.7 engine (`v07/`)
Symbolic compression research: `quantum_dust`, `base3_positions`,
`qutrit_delta`, `csf_symbolic_compressor`, `convergence_engine`.

---

## 4. Code map

| Path | Role |
|---|---|
| `src/csf/csf_pack.py` | **v0.8 arbitrary-file pack/unpack (new)** |
| `src/csf/csf_file.py` | v0.3 symbolic writer/reader |
| `src/csf/header.py` | v1 segmented header/segment table |
| `src/csf/v07/` | v0.7 symbolic compression engine |
| `src/csf/status_cube.py` | StatusCube (player ImagniVerse) |
| `src/csf/memory_engine.py` | memory archive over CSF |
| `caad/README.md` | CADD (Context Archive for Dream Data) — built on CSF |

---

## 5. Consolidation pointers (previously scattered)
- `docs/CSF-Whitepaper-v0.3.pdf` — original whitepaper
- `docs/PHASE-1-CSF-BACKEND.md` — backend phase notes
- `caad/README.md`, `caad/dollhouse-csf-upgrade.md` — CADD layer
- `CSF-IMAGE-TRAINING.md` — image-LoRA training over CSF
- `csf/ingest/` — CSF *ingest* docs are the memory/task queue, **not** format specs

This spec is the authoritative format reference; the above remain for history.
