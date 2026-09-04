"""Repository-root pytest configuration.

`tests/` imports the `petcare` package, which lives under
`petcare_runtime/src/`. Without this the whole directory fails collection with
`ModuleNotFoundError: No module named 'petcare'` — ten errors, and a suite that
can only be run by someone who already knows to export `PYTHONPATH`. Making the
path a property of the repository rather than of the operator's shell is what
lets a governance suite be run the same way by a person, by CI, and by an agent.
"""
from __future__ import annotations

import sys
from pathlib import Path

_RUNTIME_SRC = Path(__file__).resolve().parent / "petcare_runtime" / "src"
if _RUNTIME_SRC.is_dir() and str(_RUNTIME_SRC) not in sys.path:
    sys.path.insert(0, str(_RUNTIME_SRC))
