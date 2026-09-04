"""Test bootstrap.

W0-A removed the literal `SECRET_KEY` fallback, so `routers.auth` now refuses to
import without one. That is the intended fail-closed behaviour in every
environment — including CI, which must supply a real key from governed secret
storage rather than relying on a default.

A deterministic non-secret value is set here ONLY if the environment has not
already provided one, so the suite documents the requirement instead of failing
at collection with an unexplained import error. This value is never used by any
deployed process: `_require_secret_key()` is exercised directly, with
monkeypatched environments, in test_secret_key_required.py.
"""
import os

os.environ.setdefault("SECRET_KEY", "test-only-not-a-deployed-secret")
