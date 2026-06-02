"""Test package marker for reliable unittest discovery.

Also prepends the repo's ``src/`` directory to ``sys.path`` so tests can
import the BetterSafe pilot package (``bettersafe.sensor_policy``,
``bettersafe.release_gate``) without requiring ``pip install -e .`` or
``PYTHONPATH=src`` to be set explicitly in CI.

Keeping this in ``tests/__init__.py`` rather than a top-level
``conftest.py`` means the same import path works for both
``python -m unittest discover -s tests`` and ``python -m pytest``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC_DIR = _REPO_ROOT / "src"

if _SRC_DIR.is_dir():
    _SRC_PATH = str(_SRC_DIR)
    if _SRC_PATH not in sys.path:
        sys.path.insert(0, _SRC_PATH)
