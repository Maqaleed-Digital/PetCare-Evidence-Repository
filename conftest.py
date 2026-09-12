"""Repository-root pytest configuration.

`tests/` imports the `petcare` package, which lives under
`petcare_runtime/src/`. Without this the whole directory fails collection with
`ModuleNotFoundError: No module named 'petcare'` — ten errors, and a suite that
can only be run by someone who already knows to export `PYTHONPATH`. Making the
path a property of the repository rather than of the operator's shell is what
lets a governance suite be run the same way by a person, by CI, and by an agent.

The same argument now applies to the serving layer's REQUIRED configuration, and
it is here rather than in `petcare_api/tests/conftest.py` because of a defect
this file's absence produced: `tests/governance/test_retired_key_absence.py`
imports `routers.auth` to read the fingerprint set, and W0-F made that import
require `PETCARE_SECRET_MODE` and `PETCARE_PERSISTENCE_MODE`. With the bootstrap
in the API conftest only, `pytest tests` FAILED while
`pytest tests petcare_runtime/tests petcare_api/tests` — the command CI runs —
passed, because the API conftest was loaded in one and not the other.

Green CI would have hidden it, which is the whole of Rule 13 in one line.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_RUNTIME_SRC = Path(__file__).resolve().parent / "petcare_runtime" / "src"
if _RUNTIME_SRC.is_dir() and str(_RUNTIME_SRC) not in sys.path:
    sys.path.insert(0, str(_RUNTIME_SRC))

# W0-A / W0-F. Each of these is REQUIRED by the application and has no default:
# an unset signing key, secret mode or persistence mode makes the process refuse
# to start, because the deployment where a default would matter is production.
#
# `setdefault` documents the requirement for the suite instead of failing at
# collection with an unexplained import error, and never overrides a value the
# environment supplied. The fail-closed behaviour itself is exercised with
# monkeypatched environments in test_secret_key_required.py,
# test_secret_provider.py and test_persistence_mode.py — so setting these here
# does not weaken the controls that assert their absence.
#
# `environment` + `memory` is the non-production pair. Neither points at a
# deployed store, and no value here is a credential.
os.environ.setdefault("SECRET_KEY", "test-only-not-a-deployed-secret")
os.environ.setdefault("PETCARE_SECRET_MODE", "environment")
os.environ.setdefault("PETCARE_PERSISTENCE_MODE", "memory")
