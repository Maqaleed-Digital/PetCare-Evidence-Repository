"""SEC-SECRET-01..06 — the governed secret source, and its refusals.

`MVC-W0F-SECRET-SOURCE-DECISION-001` states three binding properties: no
default, no region at the call site, fail closed at startup. Each is asserted
below against the real resolution path — the tests substitute the leaf provider,
never the resolver, so what production runs is what is under test.

Every control here is a NEGATIVE one, and negative controls are worthless
without a positive one beside them: a resolver that raised unconditionally would
satisfy every refusal in this file. `test_positive_control_a_real_secret_resolves`
is what stops that, and it is deliberately the first test in the file.
"""
import json
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from secret_provider import (  # noqa: E402
    AUTHORITY_SECRETS_MANAGER,
    AwsSecretsManagerProvider,
    DB_SECRET_ID_ENV_VAR,
    EnvironmentSecretProvider,
    GOVERNED_SECRET_AUTHORITIES,
    PLACEHOLDER_SECRET_VALUES,
    SECRET_MODE_AWS,
    SECRET_MODE_ENV_VAR,
    SESSION_SECRET_ID_ENV_VAR,
    SecretUnavailable,
    SsmParameterStoreProvider,
    build_secret_provider,
    current_secret_mode,
    resolve_database_url,
    resolve_secret,
    resolve_session_signing_key,
)


class _FakeSecretsManager:
    """A Secrets Manager provider with no AWS behind it.

    Declares the real authority because the point is to exercise the governed
    path, not to bypass it. Nothing in the application constructs this class;
    `build_secret_provider` never returns it.
    """

    authority = AUTHORITY_SECRETS_MANAGER

    def __init__(self, values: dict):
        self._values = values
        self.calls: list[str] = []

    def get(self, secret_id: str) -> str:
        self.calls.append(secret_id)
        if secret_id not in self._values:
            raise SecretUnavailable(f"no such secret {secret_id!r}")
        return self._values[secret_id]


ENV_MODE = {SECRET_MODE_ENV_VAR: "environment"}


# ---------------------------------------------------------------------------
# Positive control — without it every refusal below could pass vacuously
# ---------------------------------------------------------------------------

def test_positive_control_a_real_secret_resolves():
    provider = _FakeSecretsManager({"petcare/session": "a-real-high-entropy-value"})
    assert resolve_secret("petcare/session", provider=provider) == (
        "a-real-high-entropy-value"
    )
    assert provider.calls == ["petcare/session"]


def test_positive_control_the_signing_key_resolves_through_the_real_path():
    env = dict(ENV_MODE, SECRET_KEY="a-real-high-entropy-value")
    assert resolve_session_signing_key(environ=env) == "a-real-high-entropy-value"


# ---------------------------------------------------------------------------
# SEC-SECRET-01 — a missing session secret fails closed
# ---------------------------------------------------------------------------

def test_sec_secret_01_missing_session_secret_fails_closed():
    """The W0-A property, now through the provider. An absent key must stop the
    process, not produce one."""
    env = dict(ENV_MODE)  # SECRET_KEY deliberately absent
    with pytest.raises(SecretUnavailable):
        resolve_session_signing_key(environ=env)


def test_sec_secret_01b_the_router_refuses_to_start_without_it(monkeypatch):
    """Reached through `_require_secret_key`, which is what actually runs at
    import — the resolver being correct is not enough if the caller has its own
    fallback.

    The message still NAMES the configured identifier and keeps W0-A's wording,
    so T-SEC-01 continues to bind to this function rather than being rewritten
    to match new prose.
    """
    import routers.auth as auth

    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.setenv(SECRET_MODE_ENV_VAR, "environment")
    with pytest.raises(RuntimeError, match="SECRET_KEY is not set"):
        auth._require_secret_key()


# ---------------------------------------------------------------------------
# SEC-SECRET-02 — a missing DB secret means the adapter cannot initialise
# ---------------------------------------------------------------------------

def test_sec_secret_02_missing_db_secret_fails_closed():
    env = dict(ENV_MODE)  # PETCARE_DB_URL absent
    with pytest.raises(SecretUnavailable):
        resolve_database_url(environ=env)


def test_sec_secret_02b_persistence_refuses_to_build_without_the_db_secret():
    """The control that matters is not that resolution raises — it is that
    `build_persistence` does not answer with a memory store when it does."""
    from persistence import build_persistence
    from postgres_repositories import PersistenceUnavailable

    env = dict(ENV_MODE, PETCARE_PERSISTENCE_MODE="postgres")
    with pytest.raises(PersistenceUnavailable):
        build_persistence(env)


def test_sec_secret_02c_aws_mode_requires_the_identifier_and_never_guesses_it():
    """A secret identifier is configuration, but guessing one in production
    either fails loudly or finds a DIFFERENT secret."""
    env = {SECRET_MODE_ENV_VAR: SECRET_MODE_AWS}
    with pytest.raises(SecretUnavailable, match=SESSION_SECRET_ID_ENV_VAR):
        resolve_session_signing_key(
            environ=env, provider=_FakeSecretsManager({"x": "y"})
        )
    with pytest.raises(SecretUnavailable, match=DB_SECRET_ID_ENV_VAR):
        resolve_database_url(environ=env, provider=_FakeSecretsManager({"x": "y"}))


# ---------------------------------------------------------------------------
# SEC-SECRET-03 — an empty secret is denied
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value", ["", "   ", "\n", "\t "])
def test_sec_secret_03_empty_secret_is_denied(value):
    """Present-but-empty is the shape a misconfigured deployment actually takes,
    and an emptiness that resolved would sign every session with the empty
    string."""
    provider = _FakeSecretsManager({"petcare/session": value})
    with pytest.raises(SecretUnavailable, match="empty"):
        resolve_secret("petcare/session", provider=provider)


def test_sec_secret_03b_an_empty_secret_stops_the_signing_key():
    env = dict(ENV_MODE, SECRET_KEY="   ")
    with pytest.raises(SecretUnavailable):
        resolve_session_signing_key(environ=env)


# ---------------------------------------------------------------------------
# SEC-SECRET-04 — a placeholder is denied
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value", sorted(PLACEHOLDER_SECRET_VALUES))
def test_sec_secret_04_placeholder_values_are_denied(value):
    """The value somebody typed to make the process start, intending to replace
    it. Syntactically present, semantically absent."""
    provider = _FakeSecretsManager({"petcare/session": value})
    with pytest.raises(SecretUnavailable, match="placeholder"):
        resolve_secret("petcare/session", provider=provider)


@pytest.mark.parametrize("value", ["CHANGEME", "  ChangeMe  ", "PLACEHOLDER"])
def test_sec_secret_04b_placeholders_are_caught_whatever_the_casing(value):
    provider = _FakeSecretsManager({"petcare/session": value})
    with pytest.raises(SecretUnavailable, match="placeholder"):
        resolve_secret("petcare/session", provider=provider)


@pytest.mark.parametrize("value", [
    "changeme-but-actually-a-long-random-suffix-9f2a",
    "test-only-not-a-deployed-secret",
    "default-gateway-token-8812aa",
])
def test_sec_secret_04c_the_placeholder_check_does_not_reject_real_secrets(value):
    """Matched as whole values, never as substrings.

    A substring match would reject legitimate high-entropy secrets that happen
    to contain 'test' or 'default' — and a guard that rejects valid input is a
    guard somebody disables.
    """
    provider = _FakeSecretsManager({"petcare/session": value})
    assert resolve_secret("petcare/session", provider=provider) == value.strip()


# ---------------------------------------------------------------------------
# SEC-SECRET-05 — Parameter Store can never satisfy a secret
# ---------------------------------------------------------------------------

def test_sec_secret_05_ssm_is_not_a_governed_secret_authority():
    """The decision's reason, as an assertion: Parameter Store has no rotation
    primitive, so a secret sourced from it is a secret that cannot be rotated by
    any managed operation."""
    assert "AWS_SSM_PARAMETER_STORE" not in GOVERNED_SECRET_AUTHORITIES


def test_sec_secret_05b_an_ssm_provider_is_refused_for_a_secret():
    with pytest.raises(SecretUnavailable, match="not a governed secret authority"):
        resolve_secret("petcare/session", provider=SsmParameterStoreProvider())


def test_sec_secret_05c_an_ssm_provider_cannot_even_return_a_value():
    """Refused at both ends. If `resolve_secret` were ever bypassed, the
    provider itself still declines — one refusal that depends on the caller
    remembering to route through the resolver is one refusal."""
    with pytest.raises(SecretUnavailable, match="cannot supply"):
        SsmParameterStoreProvider().get("petcare/session")


def test_sec_secret_05d_an_unknown_authority_is_refused():
    """A provider this module has never seen must not be trusted by default.
    The authority check happens at USE, not at construction, so a substitution
    made later is still checked."""
    class _Rogue:
        authority = "SOMEWHERE_ELSE"

        def get(self, secret_id):
            return "a-real-high-entropy-value"

    with pytest.raises(SecretUnavailable, match="not a governed secret authority"):
        resolve_secret("petcare/session", provider=_Rogue())


def test_sec_secret_05e_a_provider_with_no_declared_authority_is_refused():
    class _Undeclared:
        def get(self, secret_id):
            return "a-real-high-entropy-value"

    with pytest.raises(SecretUnavailable):
        resolve_secret("petcare/session", provider=_Undeclared())


# ---------------------------------------------------------------------------
# SEC-SECRET-06 — no secret material, and no second source, in the tree
# ---------------------------------------------------------------------------

def test_sec_secret_06_no_module_reads_a_secret_at_the_point_of_use():
    """The contract is that application code depends on the provider.

    `routers/auth.py` must not read the signing key from the environment
    directly any more — if it did, the provider would be decoration and the AWS
    path would never run in production.
    """
    import pathlib

    source = (pathlib.Path(__file__).resolve().parents[1]
              / "routers" / "auth.py").read_text(encoding="utf-8")
    code = "\n".join(
        line for line in source.splitlines() if not line.strip().startswith("#")
    )
    assert 'os.getenv("SECRET_KEY"' not in code
    assert 'os.environ["SECRET_KEY"' not in code
    assert 'os.environ.get("SECRET_KEY"' not in code
    assert "resolve_session_signing_key()" in code


def test_sec_secret_06b_the_provider_has_no_fallback_value_anywhere():
    """`get()` must have no default parameter and no `or "..."` rescue.

    Checked on the source because the behavioural tests can only prove the
    absence of the fallbacks they thought to try.
    """
    import pathlib
    import re

    source = (pathlib.Path(__file__).resolve().parents[1]
              / "secret_provider.py").read_text(encoding="utf-8")
    code = "\n".join(
        line for line in source.splitlines() if not line.strip().startswith("#")
    )
    # A default on the environment read is the classic shape of the W0-A defect.
    assert not re.search(r"environ\.get\(\s*secret_id\s*,", code)
    assert not re.search(r"getenv\(\s*secret_id\s*,", code)


# ---------------------------------------------------------------------------
# Mode selection — unset and unknown both fail closed
# ---------------------------------------------------------------------------

def test_secret_mode_must_be_set():
    with pytest.raises(SecretUnavailable, match=SECRET_MODE_ENV_VAR):
        current_secret_mode({})


@pytest.mark.parametrize("mode", ["aws", "AWS_SECRETS_MANAGER", "env", "prod", " "])
def test_an_unknown_secret_mode_is_refused_rather_than_coerced(mode):
    """A typo must not select a mode silently — afterwards it would look
    deliberate."""
    with pytest.raises(SecretUnavailable):
        current_secret_mode({SECRET_MODE_ENV_VAR: mode})


def test_environment_mode_builds_the_environment_provider():
    provider = build_secret_provider(dict(ENV_MODE))
    assert isinstance(provider, EnvironmentSecretProvider)


def test_aws_mode_builds_the_aws_provider_without_touching_aws():
    """Constructing the production provider must require neither the SDK nor a
    credential. A provider that did would force the suite to bypass it — and the
    bypass would then be the thing under test."""
    provider = build_secret_provider({
        SECRET_MODE_ENV_VAR: SECRET_MODE_AWS,
        "PETCARE_AWS_REGION": "a-configured-region-value",
    })
    assert isinstance(provider, AwsSecretsManagerProvider)


def test_the_aws_provider_fails_closed_without_a_configured_region():
    """D.21: the provider is configured with its region and callers never name
    one — so an unset region has no fallback."""
    provider = AwsSecretsManagerProvider(region=None)
    with pytest.raises(SecretUnavailable, match="PETCARE_AWS_REGION"):
        provider.get("petcare/session")


# ---------------------------------------------------------------------------
# Database credential shapes
# ---------------------------------------------------------------------------

def test_a_connection_url_secret_resolves():
    env = dict(ENV_MODE, PETCARE_DB_URL="postgresql://u:p@h:5432/d")
    assert resolve_database_url(environ=env) == "postgresql://u:p@h:5432/d"


def test_a_managed_credential_object_is_assembled():
    secret = json.dumps({
        "username": "app", "password": "pw", "host": "h", "port": 5432,
        "dbname": "petcare",
    })
    env = dict(ENV_MODE, PETCARE_DB_SECRET_ID="db")
    url = resolve_database_url(
        environ=env, provider=_FakeSecretsManager({"db": secret})
    )
    assert url == "postgresql://app:pw@h:5432/petcare"


def test_a_credential_with_uri_reserved_characters_is_percent_encoded():
    """A password containing '/' or '@' silently truncates or redirects the URL
    otherwise, and the resulting failure looks like a wrong credential rather
    than a parsing bug."""
    secret = json.dumps({
        "username": "app", "password": "p/a@ss:word", "host": "h",
        "port": 5432, "dbname": "petcare",
    })
    env = dict(ENV_MODE, PETCARE_DB_SECRET_ID="db")
    url = resolve_database_url(
        environ=env, provider=_FakeSecretsManager({"db": secret})
    )
    assert "p%2Fa%40ss%3Aword" in url
    assert "p/a@ss:word" not in url


@pytest.mark.parametrize("missing", ["username", "password", "host", "port", "dbname"])
def test_a_partial_credential_is_never_completed_from_defaults(missing):
    fields = {"username": "app", "password": "pw", "host": "h", "port": 5432,
              "dbname": "petcare"}
    fields.pop(missing)
    env = dict(ENV_MODE, PETCARE_DB_SECRET_ID="db")
    with pytest.raises(SecretUnavailable, match="missing required fields"):
        resolve_database_url(
            environ=env, provider=_FakeSecretsManager({"db": json.dumps(fields)})
        )


def test_malformed_json_fails_closed_rather_than_falling_back():
    env = dict(ENV_MODE, PETCARE_DB_SECRET_ID="db")
    with pytest.raises(SecretUnavailable, match="does not parse"):
        resolve_database_url(
            environ=env, provider=_FakeSecretsManager({"db": '{"username": '})
        )


def test_a_value_that_is_neither_url_nor_object_is_refused():
    env = dict(ENV_MODE, PETCARE_DB_SECRET_ID="db")
    with pytest.raises(SecretUnavailable, match="refusing to assemble"):
        resolve_database_url(
            environ=env, provider=_FakeSecretsManager({"db": "just-some-text"})
        )
