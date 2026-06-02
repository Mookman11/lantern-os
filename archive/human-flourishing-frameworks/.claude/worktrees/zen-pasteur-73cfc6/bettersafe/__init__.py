"""Import shim for the ``src/bettersafe`` package.

The repository is not packaged with a ``pyproject.toml`` yet, so plain
``python -m unittest discover -s tests`` does not automatically place ``src``
on ``sys.path``. Keep the implementation in ``src/bettersafe`` while making
``import bettersafe`` work from a fresh checkout.
"""

from __future__ import annotations

from pathlib import Path

_SRC_PACKAGE = Path(__file__).resolve().parents[1] / "src" / "bettersafe"

if _SRC_PACKAGE.is_dir():
    __path__ = [str(_SRC_PACKAGE), *__path__]

