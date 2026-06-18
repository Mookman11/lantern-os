#!/usr/bin/env python3
"""
Nightly CC research (Task 1) — runs the legitimate CC-licensed collector for a
rotating set of gaming queries, then refreshes editing priors.

Scope reminder: this only ever touches Creative-Commons-licensed clips (the
collector filters on the real CC license string) + first-party data. It does
NOT bulk-download arbitrary copyrighted Shorts. Real-world yield is small
(CC gaming content is scarce); that is reported honestly, not padded.

Intended to be scheduled (cron/Task Scheduler). It is idempotent: the collector
skips clips already analyzed.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Gaming-specific CC queries (the handoff's list, phrased to surface CC content).
QUERIES_NOTE = (
    "minecraft/fortnite/roblox/cod/warzone/apex/valorant — the collector appends "
    "'creative commons'/'no copyright' framing and filters on the real CC license."
)


def run(cmd, label):
    print(f"\n=== {label} ===")
    proc = subprocess.run(cmd, cwd=str(ROOT))
    return proc.returncode == 0


def main():
    print("Nightly CC research starting.")
    print("Query focus:", QUERIES_NOTE)

    # 1) Collect a fresh modest batch of CC-licensed gaming clips (real features).
    ok_collect = run(["python", "scripts/collect_cc_shorts.py"], "collect CC-licensed clips")

    # 2) Recompute editing priors from all reference data on disk.
    ok_priors = run(["node", "-e",
                     "require('./apps/lantern-garage/lib/editing-priors').updateEditingPriors(); "
                     "console.log('editing priors updated -> data/models/editing-priors.json')"],
                    "update editing priors")

    print("\nNightly CC research complete.",
          "collect_ok=" + str(ok_collect), "priors_ok=" + str(ok_priors))
    # Non-fatal: a failed collection (e.g. network/quota) still lets priors refresh
    # from existing data. Exit 0 unless BOTH failed.
    sys.exit(0 if (ok_collect or ok_priors) else 1)


if __name__ == "__main__":
    main()
