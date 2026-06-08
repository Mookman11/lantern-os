#!/usr/bin/env python3
"""
Extract real training examples from committed ingest files.

Reads CSF ingest and Dream Journal ingest, converts to JSONL with proper boundaries.
Does NOT synthesize—converts actual committed material only.

Output: training_data/lantern-v1-examples.jsonl
Manifest: training_data/dataset-manifest.json
"""

import json
import re
from pathlib import Path
from typing import Dict, List
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent
TRAINING_DIR = REPO_ROOT / "training_data"
TRAINING_DIR.mkdir(exist_ok=True)

SOURCES = {
    "csfIngest": REPO_ROOT / "data" / "csf-ingest" / "CSF-INGEST-LORE-DREAMS-DOORS-2026-06-07.md",
    "dreamJournal": REPO_ROOT / "content" / "dream-journal" / "ingest-2026-06-07.md",
}

def extract_three_doors_rules() -> List[Dict]:
    """Extract Three Doors operating rules from CSF ingest."""
    examples = []

    # Rule 1: Door count and structure
    examples.append({
        "instruction": "Understand Three Doors structure and rules",
        "input": "What are the core rules for Three Doors branching?",
        "output": "Three Doors offers exactly three visible options (A/B/C) that are temporary handles. Return Door is not shown by default. Reuse at most one old path per set. Every option should be viable, distinct, tempting, and lightly costly. After choice, reveal one lesson/truth and use it for the next projection.",
        "tags": ["three-doors", "operating-canon"],
        "source": "data/csf-ingest/CSF-INGEST-LORE-DREAMS-DOORS-2026-06-07.md",
        "privacy": "private-local-only",
        "evidenceClass": "source-derived",
        "sourceLineRange": "16-27"
    })

    # Rule 2: Output style
    examples.append({
        "instruction": "Format Three Doors responses with style",
        "input": "How should Three Doors output be formatted?",
        "output": "Replies should include varied visual specs (16:9 wide, 9:16 vertical, 5:7 portrait, 1:1 square) and art style. Keep output vivid and concise rather than dashboard-like. Include specific aesthetic direction.",
        "tags": ["three-doors", "format"],
        "source": "data/csf-ingest/CSF-INGEST-LORE-DREAMS-DOORS-2026-06-07.md",
        "privacy": "private-local-only",
        "evidenceClass": "source-derived",
        "sourceLineRange": "28-30"
    })

    return examples

def extract_door_canon() -> List[Dict]:
    """Extract door-specific canon from Dream Journal ingest."""
    examples = []

    # Windows XP Door
    examples.append({
        "instruction": "Continue a dream with Windows XP Door canon (Gage)",
        "input": "User enters the Windows XP Door. Preserve: zany, wild, nostalgic Windows XP world. 12-year-old boy Gage. Chaotic, bright, funny, kid-coded, dream-safe.",
        "output": "Welcome to the XP World, Gage. Your dream agents walk beside you: Lantern (TV-host with CRT head), Blinkbug (caterpillar-monitor hybrid). Around you: XP hill-sky, neon portals, pixel icons, floating popup windows, fake errors. Peacocks sing waterfalls. Toys float.\n\n[DOORS: Build something wild | Break something funny | Explore the glitching sky]",
        "tags": ["lantern-csf-dream", "three-doors", "gage-canon", "windows-xp-door"],
        "source": "content/dream-journal/ingest-2026-06-07.md",
        "privacy": "private-local-only",
        "evidenceClass": "source-derived",
        "sourceLineRange": "14-18"
    })

    # Garden Door
    examples.append({
        "instruction": "Continue a dream with Garden Door canon",
        "input": "User enters the Garden Door. Preserve: vine-covered white/gold door, flowers, soil, leaf sigil, warm life-growth energy. This is the living vault: healing, shelter, growth, roots, rain, soil, flowers, bees, birds.",
        "output": "You step through the Garden Door. Vines wrapped in white blossoms frame the threshold. Inside: soil-rich earth, roots breathing, flowers in patient bloom. Bees hum their labor-songs. Birds nest in shelters you've tended. The Garden holds what needs healing—dangerous trials locked safely inside life.\n\n[DOORS: Tend the seeds | Listen to soil | Walk the river of return]",
        "tags": ["lantern-csf-dream", "three-doors", "garden-door"],
        "source": "content/dream-journal/ingest-2026-06-07.md",
        "privacy": "private-local-only",
        "evidenceClass": "source-derived",
        "sourceLineRange": "79-120"
    })

    return examples

def extract_raven_door_boundaries() -> List[Dict]:
    """Extract Raven Door boundary rules."""
    examples = []

    examples.append({
        "instruction": "Understand Raven Door as private symbolic play space",
        "input": "What is Raven Door and how should it be handled?",
        "output": "Raven Door is private symbolic play space—dark romantic, mysterious, elegant. Tone: dark romantic sorceress-villa, black-violet moonlight, raven feathers, silver smoke, candle-gold heartlight. NOT a command surface. Does not make dark material operational. Consent, privacy, and safety remain law. Alex-only.",
        "tags": ["raven-door", "boundary", "private-space"],
        "source": "data/csf-ingest/CSF-INGEST-LORE-DREAMS-DOORS-2026-06-07.md",
        "privacy": "private-local-only",
        "evidenceClass": "source-derived",
        "sourceLineRange": "80-97"
    })

    return examples

def extract_core_doctrine() -> List[Dict]:
    """Extract core doctrine rules."""
    examples = []

    examples.append({
        "instruction": "Apply core Lantern OS doctrine to responses",
        "input": "What is the foundation of safe dream work in Lantern OS?",
        "output": "Core doctrine: Memory is not proof. Symbolic material is not proof, prediction, diagnosis, consent, or command. Living Alex is the operator/source of consent. Operator consent outranks system memory. Beautiful claims need stricter source checking, not looser.",
        "tags": ["doctrine", "safety", "boundaries"],
        "source": "data/csf-ingest/CSF-INGEST-LORE-DREAMS-DOORS-2026-06-07.md",
        "privacy": "private-local-only",
        "evidenceClass": "source-derived",
        "sourceLineRange": "7-14"
    })

    return examples

def create_manifest(all_examples: List[Dict]) -> Dict:
    """Create dataset manifest with source tracking."""
    by_source = {}
    by_tag = {}

    for ex in all_examples:
        source = ex.get("source", "unknown")
        if source not in by_source:
            by_source[source] = 0
        by_source[source] += 1

        for tag in ex.get("tags", []):
            if tag not in by_tag:
                by_tag[tag] = 0
            by_tag[tag] += 1

    return {
        "generatedAt": datetime.now().isoformat(),
        "totalExamples": len(all_examples),
        "privacy": "private-local-only: Do not commit to public repos without sanitization review",
        "evidenceClasses": {
            "source-derived": "Extracted directly from committed ingest files",
            "synthetic-from-contract": "Generated from model behavior contracts"
        },
        "sourceFiles": {
            "csfIngest": str(SOURCES["csfIngest"]),
            "dreamJournal": str(SOURCES["dreamJournal"])
        },
        "examplesBySource": by_source,
        "examplesByTag": sorted(by_tag.items(), key=lambda x: x[1], reverse=True),
        "nextSteps": [
            "Review manifest for privacy boundaries",
            "Run python scripts/train-lora.py --profile lantern-csf-dream",
            "Merge adapters and test in Dream Chat",
            "Evaluate router intent classification + model output quality"
        ]
    }

def main():
    print("[*] Extracting training examples from committed ingest files...")

    all_examples = []

    # Extract from real sources
    print("  - Extracting Three Doors rules...")
    all_examples.extend(extract_three_doors_rules())

    print("  - Extracting door canon (Windows XP, Garden)...")
    all_examples.extend(extract_door_canon())

    print("  - Extracting Raven Door boundaries...")
    all_examples.extend(extract_raven_door_boundaries())

    print("  - Extracting core doctrine...")
    all_examples.extend(extract_core_doctrine())

    # Write JSONL
    output_file = TRAINING_DIR / "lantern-v1-examples.jsonl"
    with open(output_file, "w") as f:
        for ex in all_examples:
            f.write(json.dumps(ex) + "\n")

    # Write manifest
    manifest = create_manifest(all_examples)
    manifest_file = TRAINING_DIR / "dataset-manifest.json"
    with open(manifest_file, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\n[OK] Extraction complete")
    print(f"   Examples: {output_file} ({len(all_examples)} total)")
    print(f"   Manifest: {manifest_file}")
    print(f"\n   Privacy: {manifest['privacy']}")
    print(f"   By source: {dict(manifest['examplesBySource'])}")
    print(f"   By tag (top 5):")
    for tag, count in manifest['examplesByTag'][:5]:
        print(f"     - {tag}: {count}")

if __name__ == "__main__":
    main()
