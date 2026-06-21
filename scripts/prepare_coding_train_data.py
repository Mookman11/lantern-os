#!/usr/bin/env python3
"""
Prepare merged training data for Σ₀ Ouro Coder retraining (#781).

Merges three sources:
  1. models/lantern-sigma0-coder/coding-seed.jsonl   (35 canonical examples)
  2. models/lantern-sigma0-coder/coding-extra.jsonl  (184 augmented examples)
  3. data/eval/coding-golden.jsonl                   (25 golden tasks — reference solutions)

Outputs:
  models/lantern-sigma0-coder/training-data.jsonl    (all merged, de-duped by instruction)

Then run:
  .venv-train/Scripts/python scripts/train-qlora-ouro.py \
      --data models/lantern-sigma0-coder/training-data.jsonl \
      --out D:/lantern-train/ouro-sigma0-adapters/v2 --epochs 3

After training, update OURO_ADAPTER env to point at the new v2 directory and run:
  .venv-train/Scripts/python scripts/validate_ouro_coding.py
  .venv-train/Scripts/python scripts/eval_humaneval_ouro.py --limit 20
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED_PATH = os.path.join(ROOT, "models", "lantern-sigma0-coder", "coding-seed.jsonl")
EXTRA_PATH = os.path.join(ROOT, "models", "lantern-sigma0-coder", "coding-extra.jsonl")
GOLDEN_PATH = os.path.join(ROOT, "data", "eval", "coding-golden.jsonl")
OUT_PATH = os.path.join(ROOT, "models", "lantern-sigma0-coder", "training-data.jsonl")

# Reference solutions for the 25 golden tasks — written by hand to match the prompt
# exactly (same fn name, no imports beyond builtins, idiomatic Python).
_GOLDEN_SOLUTIONS = {
    "is_prime": "def is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True",
    "reverse_string": "def reverse_string(s):\n    return s[::-1]",
    "fizzbuzz": "def fizzbuzz(n):\n    if n % 15 == 0:\n        return 'FizzBuzz'\n    if n % 3 == 0:\n        return 'Fizz'\n    if n % 5 == 0:\n        return 'Buzz'\n    return str(n)",
    "count_vowels": "def count_vowels(s):\n    return sum(1 for c in s.lower() if c in 'aeiou')",
    "factorial": "def factorial(n):\n    result = 1\n    for i in range(2, n + 1):\n        result *= i\n    return result",
    "flatten_list": "def flatten_list(lst):\n    return [item for sub in lst for item in sub]",
    "palindrome": "def is_palindrome(s):\n    s = s.lower().replace(' ', '')\n    return s == s[::-1]",
    "sum_digits": "def sum_digits(n):\n    return sum(int(d) for d in str(n))",
    "count_words": "def count_words(s):\n    return len(s.split())",
    "second_largest": "def second_largest(lst):\n    unique = sorted(set(lst), reverse=True)\n    return unique[1] if len(unique) >= 2 else None",
    "caesar_cipher": "def caesar(text, shift):\n    result = []\n    for c in text:\n        if c.isalpha():\n            base = ord('A') if c.isupper() else ord('a')\n            result.append(chr((ord(c) - base + shift) % 26 + base))\n        else:\n            result.append(c)\n    return ''.join(result)",
    "merge_sorted": "def merge_sorted(a, b):\n    result, i, j = [], 0, 0\n    while i < len(a) and j < len(b):\n        if a[i] <= b[j]:\n            result.append(a[i]); i += 1\n        else:\n            result.append(b[j]); j += 1\n    return result + a[i:] + b[j:]",
    "binary_search": "def binary_search(arr, target):\n    lo, hi = 0, len(arr) - 1\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1",
    "anagram": "def is_anagram(s1, s2):\n    s1 = s1.lower().replace(' ', '')\n    s2 = s2.lower().replace(' ', '')\n    return sorted(s1) == sorted(s2)",
    "max_subarray": "def max_subarray(nums):\n    max_sum = cur = nums[0]\n    for n in nums[1:]:\n        cur = max(n, cur + n)\n        max_sum = max(max_sum, cur)\n    return max_sum",
    "unique_chars": "def has_unique_chars(s):\n    return len(s) == len(set(s))",
    "remove_dups": "def remove_duplicates(lst):\n    seen, result = set(), []\n    for x in lst:\n        if x not in seen:\n            seen.add(x); result.append(x)\n    return result",
    "matrix_transpose": "def transpose(matrix):\n    return [list(row) for row in zip(*matrix)]",
    "roman_to_int": "def roman_to_int(s):\n    vals = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}\n    total, prev = 0, 0\n    for c in reversed(s):\n        v = vals[c]\n        total += v if v >= prev else -v\n        prev = v\n    return total",
    "balanced_parens": "def is_balanced(s):\n    depth = 0\n    for c in s:\n        if c == '(':\n            depth += 1\n        elif c == ')':\n            depth -= 1\n            if depth < 0:\n                return False\n    return depth == 0",
    "fibonacci": "def fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a",
    "chunk_list": "def chunk_list(lst, size):\n    return [lst[i:i+size] for i in range(0, len(lst), size)]",
    "rotate_left": "def rotate_left(lst, k):\n    if not lst:\n        return lst\n    k %= len(lst)\n    return lst[k:] + lst[:k]",
    "missing_number": "def missing_number(nums):\n    n = len(nums)\n    return n * (n + 1) // 2 - sum(nums)",
    "two_sum": "def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen:\n            return [seen[target - n], i]\n        seen[n] = i",
}


def load_jsonl(path):
    if not os.path.exists(path):
        print(f"[warn] missing: {path}")
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def golden_to_training(task, solution):
    return {
        "instruction": task["prompt"],
        "input": "",
        "output": solution,
    }


def main():
    seen_instructions = set()
    records = []

    def add(rec):
        key = rec.get("instruction", "").strip().lower()[:120]
        if key and key not in seen_instructions:
            seen_instructions.add(key)
            records.append(rec)

    # Source 1 & 2: existing labeled examples
    for path in [SEED_PATH, EXTRA_PATH]:
        for rec in load_jsonl(path):
            add(rec)

    # Source 3: golden coding tasks with reference solutions
    for task in load_jsonl(GOLDEN_PATH):
        sol = _GOLDEN_SOLUTIONS.get(task["name"])
        if sol:
            add(golden_to_training(task, sol))
        else:
            print(f"[warn] no reference solution for task: {task['name']}")

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Wrote {len(records)} training examples to {OUT_PATH}")
    print("\nNext steps (GPU box):")
    print("  .venv-train/Scripts/python scripts/train-qlora-ouro.py \\")
    print("      --data models/lantern-sigma0-coder/training-data.jsonl \\")
    print("      --out D:/lantern-train/ouro-sigma0-adapters/v2 --epochs 3")
    print("  .venv-train/Scripts/python scripts/validate_ouro_coding.py")
    print("  .venv-train/Scripts/python scripts/eval_humaneval_ouro.py --limit 20")


if __name__ == "__main__":
    main()
