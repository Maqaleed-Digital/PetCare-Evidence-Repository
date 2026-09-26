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
import tempfile
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

# FR-14. The prescription document store is REQUIRED for the same reason the
# persistence mode is, and fails closed the same way: an unset mode is not
# assumed to be the weaker one. `local` plus a per-run temporary directory is
# the non-production pair — node-local, outside the repository, and removed with
# the rest of the temporary tree. It is NOT an object store and the suite does
# not treat it as one; test_prescription_upload.py asserts that the production
# adapter refuses rather than falling back to this.
os.environ.setdefault("PETCARE_DOCUMENT_STORE_MODE", "local")
# NFR-15 (v1.2 U24): limits are CONFIGURABLE (ratified). Suites that are not about rate limiting legitimately send
# thousands of requests per principal per minute (the real-time visibility tests poll), so the harness configures
# high limits. The NFR-15 tests themselves run the DEFAULT policy (Policy.from_env({})) — 100 / 30.
os.environ.setdefault("PETCARE_RATE_LIMIT_PRINCIPAL_PER_MIN", "1000000")
os.environ.setdefault("PETCARE_RATE_LIMIT_ANONYMOUS_PER_MIN", "1000000")
# NFR-08 (v1.2 U25): the TOTP-secret encryption key, resolved through the environment secret provider (non-prod).
os.environ.setdefault("PETCARE_MFA_ENCRYPTION_KEY", "test-only-mfa-key-not-a-deployed-secret")
os.environ.setdefault(
    "PETCARE_DOCUMENT_ROOT",
    str(Path(tempfile.gettempdir()) / "petcare-test-documents"),
)


def pytest_configure(config):
    """MVC-ACCEPT-CHECK-001. Registered here because this root conftest is the one
    bootstrap every invocation loads (CI's included); there is no root pytest.ini.

    `served_app` is a DECLARATION that a test drives the served application object
    (`main:app`). The acceptance checker collects SERVED_APP_E2E evidence under
    `-m served_app`; marking a test that does not drive `main:app` is a false claim.
    """
    config.addinivalue_line(
        "markers", "served_app: test exercises the served application object (main:app)")
