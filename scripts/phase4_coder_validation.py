"""
Phase 4 — Live validation + benchmark for the Σ₀ Keystone coder (issue #628).

Runs real coding prompts through the local Ollama coder under the Σ₀ verification
contract and measures, against the issue's success criteria:

  * pass rate  — fraction of outputs that carry all five required fields
                 (Claim/Evidence/Confidence/Source/Verification). Target: >= 90%.
  * confidence — that every passing output reports a parseable confidence in [0,1],
                 and that ungrounded calls stay <= 0.3 (the gate owns the ceiling).
  * benchmark  — optionally re-run the same prompts through a cloud provider for a
                 side-by-side contract-compliance comparison.

This is NOT a unit test (it needs a running Ollama with qwen2.5-coder pulled), so it
lives in experiments/ and is invoked manually:

    ollama pull qwen2.5-coder
    python scripts/phase4_coder_validation.py
    python scripts/phase4_coder_validation.py --benchmark anthropic

Honesty rule: this records the real numbers. If the local model does not comply with
the contract, that is the finding — we do not fabricate a passing rate.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from unified_agent_connector import UnifiedAgentConnector  # noqa: E402
from sigma0_coder_gate import check_coder_output, UNGROUNDED_CONFIDENCE_CAP  # noqa: E402

# Small, concrete coding asks. Each is a "grounded" request (we hand the coder a
# checkable fact as context) so a compliant model can legitimately exceed the 0.3
# ungrounded ceiling — that is what we want to measure.
TASKS = [
    {
        "message": "Write a Python function is_palindrome(s) that ignores case and non-alphanumerics. Provide the five-field verification footer.",
        "context": "Python 3.12; str has .isalnum() and .lower(); compare s == s[::-1].",
    },
    {
        "message": "Write a function to merge two sorted lists into one sorted list in Python. Include the verification footer.",
        "context": "Both inputs are ascending lists of ints; standard two-pointer merge is O(n+m).",
    },
    {
        "message": "Write a Python function clamp(x, lo, hi) that bounds x to [lo, hi]. Include the verification footer.",
        "context": "Builtin min/max compose: max(lo, min(x, hi)). lo <= hi guaranteed.",
    },
    {
        "message": "Write a function to count vowels in a string in Python. Include the verification footer.",
        "context": "Vowels are aeiou, case-insensitive; sum a generator over the lowercased string.",
    },
    {
        "message": "Write a Python function fib(n) returning the nth Fibonacci number iteratively. Include the verification footer.",
        "context": "fib(0)=0, fib(1)=1; iterate with two accumulators a,b for n>=0.",
    },
    {
        "message": "Write a Python function unique_preserve(seq) that dedupes a list keeping first-seen order. Include the verification footer.",
        "context": "Use a seen set and a result list; dict.fromkeys also preserves order in 3.7+.",
    },
    {
        "message": "Write a Python function chunk(lst, n) that splits a list into n-sized chunks. Include the verification footer.",
        "context": "Slice lst[i:i+n] for i in range(0, len(lst), n); n>=1 guaranteed.",
    },
    {
        "message": "Write a Python function word_count(text) returning a dict of word->count. Include the verification footer.",
        "context": "Lowercase then split on whitespace; collections.Counter gives the counts.",
    },
    {
        "message": "Write a Python function to reverse the words in a sentence. Include the verification footer.",
        "context": "' '.join(text.split()[::-1]); collapses repeated spaces, which is acceptable.",
    },
    {
        "message": "Write a Python function gcd(a, b) using the Euclidean algorithm. Include the verification footer.",
        "context": "while b: a, b = b, a % b; return abs(a). math.gcd is the reference.",
    },
]


def collect(connector: UnifiedAgentConnector, *, message, context, provider, coder, max_tokens):
    """Drive the connector's stream() generator to completion; return (text, meta, seconds)."""
    out = []
    meta = {}
    started = time.time()
    gen = connector.stream(
        message=message, context=context, provider=provider,
        coder=coder, fallback=False, max_tokens=max_tokens,
    )
    try:
        while True:
            tok = next(gen)
            if isinstance(tok, str):
                out.append(tok)
            else:
                meta = dict(tok) if hasattr(tok, "items") else {}
    except StopIteration as stop:
        if isinstance(stop.value, dict):
            meta = stop.value
    return "".join(out), meta, round(time.time() - started, 2)


def run_suite(label, *, provider, coder, max_tokens):
    connector = UnifiedAgentConnector()
    # Warm-up: the first local call pays a cold model-load cost that can truncate
    # output. Burn one throwaway call so the measured tasks run against a warm model.
    try:
        collect(connector, message="reply with: ok", context=None,
                provider=provider, coder=coder, max_tokens=16)
    except Exception:
        pass
    rows = []
    for i, task in enumerate(TASKS, 1):
        try:
            text, _meta, secs = collect(
                connector, message=task["message"], context=task["context"],
                provider=provider, coder=coder, max_tokens=max_tokens,
            )
            # Grounded: each task supplies a checkable fact, so a compliant model may
            # claim confidence above the ungrounded floor.
            check = check_coder_output(text, grounded=True)
            rows.append({
                "task": i,
                "passed": check.passed,
                "missing": check.missing,
                "confidence": check.confidence,
                "chars": len(text),
                "seconds": secs,
            })
            flag = "PASS" if check.passed else "FAIL"
            print(f"  [{label}] task {i}: {flag} conf={check.confidence:.2f} "
                  f"{secs}s missing={check.missing or '-'}")
        except Exception as exc:  # live model / network failure is a real result
            rows.append({"task": i, "passed": False, "error": str(exc)})
            print(f"  [{label}] task {i}: ERROR {exc}")
    n = len(rows)
    passed = sum(1 for r in rows if r.get("passed"))
    confs = [r["confidence"] for r in rows if r.get("passed") and "confidence" in r]
    return {
        "label": label,
        "provider": provider,
        "n": n,
        "passed": passed,
        "pass_rate": round(passed / n, 3) if n else 0.0,
        "avg_confidence": round(sum(confs) / len(confs), 3) if confs else None,
        "rows": rows,
    }


def main():
    ap = argparse.ArgumentParser(description="Phase 4 live Σ₀ coder validation")
    ap.add_argument("--benchmark", default=None,
                    help="Also run the suite through this cloud provider (e.g. anthropic, openai) for comparison")
    ap.add_argument("--max-tokens", type=int, default=400)
    args = ap.parse_args()

    try:  # Windows consoles default to cp1252; emit UTF-8 so Sigma-0 glyphs don't crash.
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    print("Phase 4 - local Ollama Sigma-0 coder validation")
    local = run_suite("local", provider="ollama", coder=True, max_tokens=args.max_tokens)

    benchmark = None
    if args.benchmark:
        print(f"\nBenchmark — {args.benchmark}")
        benchmark = run_suite(args.benchmark, provider=args.benchmark, coder=True, max_tokens=args.max_tokens)

    # Success-criteria verdict (issue #628): >= 90% pass rate on contract compliance.
    target = 0.90
    criteria = {
        "pass_rate_target": target,
        "local_pass_rate": local["pass_rate"],
        "meets_90pct": local["pass_rate"] >= target,
        "all_passing_have_confidence": all(
            isinstance(r.get("confidence"), (int, float)) for r in local["rows"] if r.get("passed")
        ),
    }

    summary = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "model": "qwen2.5-coder",
        "local": local,
        "benchmark": benchmark,
        "criteria": criteria,
    }

    out_path = REPO_ROOT / "data" / "phase4-coder-validation.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\n=== VERDICT ===")
    print(f"local pass rate: {local['pass_rate']*100:.0f}% ({local['passed']}/{local['n']})  "
          f"target {target*100:.0f}%  -> {'MEETS' if criteria['meets_90pct'] else 'BELOW'} criteria")
    if benchmark:
        print(f"benchmark ({benchmark['provider']}) pass rate: {benchmark['pass_rate']*100:.0f}%")
    print(f"receipt: {out_path}")
    # Exit non-zero when the success criterion is not met, so callers/CI can gate.
    sys.exit(0 if criteria["meets_90pct"] else 2)


if __name__ == "__main__":
    main()
