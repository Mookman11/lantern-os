import sys
from pathlib import Path

# With --import-mode=importlib pytest doesn't add tests/ to sys.path, so
# pythonpath = src in pytest.ini is sufficient. Belt-and-suspenders: also
# pin src/ first here in case any conftest in a subdirectory runs before
# importlib mode takes full effect.
_src = str(Path(__file__).resolve().parent / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)
