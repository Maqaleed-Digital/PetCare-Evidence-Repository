"""W0-F item 3 — the governed secret source, implemented.

`MVC-W0F-SECRET-SOURCE-DECISION-001` decided the authority and defined the
contract. Nothing implemented it: the previous receipt records
`SECRET_PROVIDER=CONTRACT_DEFINED_NOT_IMPLEMENTED`. This module is that
implementation.

```
SECRET_AUTHORITY=AWS_SECRETS_MANAGER
CONFIG_AUTHORITY=AWS_SSM_PARAMETER_STORE_FOR_NON_SECRET_CONFIGURATION_ONLY
```

## The one idea this module exists to enforce

**A value that confers authority comes from exactly one place.** Not "primarily"
from one place with a fallback. The decision states the reason and it is not a
matter of taste: two sources for one secret means two rotation paths, and a
rotation that updates one and not the other leaves a stale credential that still
works. That is indistinguishable from an unrevoked key — the precise failure AC-7
exists to prevent.

So there is no fallback anywhere below. Every path that cannot produce the
governed value raises `SecretUnavailable`. A caller cannot accidentally receive a
placeholder, an empty string, or a value that came from somewhere else.

## Why the mode is explicit and has no default

`PETCARE_SECRET_MODE` must be set. An unset mode does not quietly become
`environment`, because the deployment where that matters is production — the one
place where defaulting to the weaker source would be silent and wrong. W0-A
established this shape for the signing key ("refuses to start rather than run
with an unknown-provenance key"); this extends it to the choice of source.

## Why SSM can never satisfy a secret

`SsmParameterStoreProvider` exists so that non-secret configuration has a named
home, and it declares an authority that is deliberately absent from
`GOVERNED_SECRET_AUTHORITIES`. Passing it where a secret is required raises. That
is SEC-SECRET-05, and it is a real guard rather than a convention: Parameter
Store has no rotation primitive, so a secret sourced from it is a secret that
cannot be rotated by any managed operation.

## Region

The provider reads its region from configuration and callers never name one.
D.21 requires that moving to KSA is a configuration change; a region literal at a
call site is exactly the line that gets missed during a mandatory migration.
"""
from __future__ import annotations

import json
import os
from typing import Any, Callable, Optional, Protocol


class SecretUnavailable(RuntimeError):
    """A governed secret could not be obtained, and there is no fallback.

    Raised for absent, blank, malformed and placeholder values alike, and for a
    provider that cannot be reached. The caller is not given the difference
    because there is no safe action that depends on it: every one of them means
    "do not proceed".
    """


# -- authorities -------------------------------------------------------------

AUTHORITY_SECRETS_MANAGER = "AWS_SECRETS_MANAGER"
AUTHORITY_SSM_PARAMETER_STORE = "AWS_SSM_PARAMETER_STORE"
AUTHORITY_ENVIRONMENT = "ENVIRONMENT"

#: Authorities permitted to supply material that CONFERS authority.
#:
#: `ENVIRONMENT` is here because non-production deployments and the test suite
#: have no Secrets Manager and must still exercise the same code path — a test
#: harness that bypasses the provider proves nothing about the provider. It is
#: admissible only under `PETCARE_SECRET_MODE=environment`, which production does
#: not set.
#:
#: `AWS_SSM_PARAMETER_STORE` is deliberately ABSENT and must stay absent.
GOVERNED_SECRET_AUTHORITIES = frozenset({
    AUTHORITY_SECRETS_MANAGER,
    AUTHORITY_ENVIRONMENT,
})

SECRET_MODE_ENV_VAR = "PETCARE_SECRET_MODE"
SECRET_MODE_AWS = "aws_secrets_manager"
SECRET_MODE_ENVIRONMENT = "environment"
VALID_SECRET_MODES = frozenset({SECRET_MODE_AWS, SECRET_MODE_ENVIRONMENT})

#: Region for the AWS clients. Configuration, never a literal in code.
AWS_REGION_ENV_VAR = "PETCARE_AWS_REGION"

#: Configuration that IDENTIFIES secrets. Knowing a secret's name grants nothing
#: without permission to read it, which is why these are configuration and not
#: secrets themselves (see the decision's authority-vs-sensitivity split).
SESSION_SECRET_ID_ENV_VAR = "PETCARE_SESSION_SECRET_ID"
DB_SECRET_ID_ENV_VAR = "PETCARE_DB_SECRET_ID"

#: In `environment` mode the secret IDENTIFIER is an environment variable name,
#: so the identifier below preserves W0-A's behaviour exactly: the signing key is
#: still read from `SECRET_KEY`. The identifier has a default; the VALUE never
#: does. That distinction is the decision's, not a convenience.
DEFAULT_SESSION_SECRET_ID_IN_ENVIRONMENT_MODE = "SECRET_KEY"
DEFAULT_DB_SECRET_ID_IN_ENVIRONMENT_MODE = "PETCARE_DB_URL"

#: Values that are syntactically present but semantically absent.
#:
#: Matched as whole values after stripping and case-folding — NOT as substrings.
#: A substring match would reject legitimate high-entropy secrets that happen to
#: contain "test" or "default", and a guard that rejects valid input gets
#: disabled. Deployment-shaped placeholders are what this catches: the value
#: someone typed to make the process start, intending to replace it.
PLACEHOLDER_SECRET_VALUES = frozenset({
    "changeme", "change_me", "change-me",
    "placeholder", "replace_me", "replace-me", "replaceme",
    "secret", "password", "todo", "tbd", "xxx", "none", "null",
    "default", "unset", "<unset>", "example", "dummy", "fixme",
})


def _reject_if_not_a_usable_secret(secret_id: str, value: Any) -> str:
    """The single validation gate every provider return passes through.

    Centralised on purpose: a per-provider check would drift, and the provider
    most likely to drift is the one used least often — which in production is the
    one that matters.
    """
    if not isinstance(value, str):
        raise SecretUnavailable(
            f"secret {secret_id!r} did not resolve to a string; refusing to use it"
        )
    stripped = value.strip()
    if not stripped:
        raise SecretUnavailable(
            f"secret {secret_id!r} resolved to an empty value; there is no default"
        )
    if stripped.casefold() in PLACEHOLDER_SECRET_VALUES:
        raise SecretUnavailable(
            f"secret {secret_id!r} resolved to a placeholder value; refusing to "
            "start with a credential that was never set"
        )
    return stripped


# -- the contract ------------------------------------------------------------

class SecretProvider(Protocol):
    """What application code depends on. Never a provider SDK call at the point
    of use, and never a literal."""

    #: Which authority this provider speaks for. Checked against
    #: GOVERNED_SECRET_AUTHORITIES before any value is accepted.
    authority: str

    def get(self, secret_id: str) -> str:
        """Return the secret, or raise `SecretUnavailable`. Never returns a
        default, a placeholder, or an empty string."""
        ...


# -- implementations ---------------------------------------------------------

class AwsSecretsManagerProvider:
    """The production provider.

    `boto3` is imported lazily and the client is built on first use, so importing
    this module — which the whole test suite does — requires neither the
    dependency nor credentials. A provider that needed live credentials to be
    constructed would force the tests to bypass it, and the bypass is what would
    then be under test.
    """

    authority = AUTHORITY_SECRETS_MANAGER

    def __init__(
        self,
        *,
        region: Optional[str] = None,
        client_factory: Optional[Callable[[], Any]] = None,
    ) -> None:
        self._region = region if region is not None else os.getenv(AWS_REGION_ENV_VAR)
        self._client_factory = client_factory
        self._client: Any = None

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        if self._client_factory is not None:
            self._client = self._client_factory()
            return self._client
        if not self._region or not self._region.strip():
            raise SecretUnavailable(
                f"{AWS_REGION_ENV_VAR} is not set. The secret provider is "
                "configured with its region and callers never name one, so an "
                "unset region has no fallback. See D.21 portability."
            )
        try:
            import boto3  # noqa: PLC0415 — lazy by design, see the class docstring
        except ImportError as exc:
            raise SecretUnavailable(
                "the AWS SDK is not available; the governed secret source cannot "
                "be reached and there is no alternative source"
            ) from exc
        self._client = boto3.client("secretsmanager", region_name=self._region)
        return self._client

    def get(self, secret_id: str) -> str:
        client = self._get_client()
        try:
            response = client.get_secret_value(SecretId=secret_id)
        except Exception as exc:
            # Deliberately broad, and deliberately does not carry the provider
            # message forward: an SDK error can quote request parameters, and
            # this exception reaches logs. What matters to the caller is that the
            # secret is unavailable, and every reason means the same thing.
            raise SecretUnavailable(
                f"secret {secret_id!r} could not be read from the governed secret "
                f"source ({type(exc).__name__}); failing closed"
            ) from None
        if not isinstance(response, dict) or "SecretString" not in response:
            raise SecretUnavailable(
                f"secret {secret_id!r} has no string value; a binary secret is not "
                "a supported shape and is not guessed at"
            )
        return _reject_if_not_a_usable_secret(secret_id, response["SecretString"])


class SsmParameterStoreProvider:
    """NON-SECRET configuration only.

    This class can read a parameter, and it can never satisfy a secret: its
    authority is absent from `GOVERNED_SECRET_AUTHORITIES`, so `resolve_secret`
    refuses it. It exists so that "where does non-secret configuration live" has
    an answer that is not "the same place as the secrets".
    """

    authority = AUTHORITY_SSM_PARAMETER_STORE

    def __init__(
        self,
        *,
        region: Optional[str] = None,
        client_factory: Optional[Callable[[], Any]] = None,
    ) -> None:
        self._region = region if region is not None else os.getenv(AWS_REGION_ENV_VAR)
        self._client_factory = client_factory
        self._client: Any = None

    def get(self, secret_id: str) -> str:
        raise SecretUnavailable(
            f"{self.authority} cannot supply {secret_id!r}: Parameter Store holds "
            "configuration that identifies, never material that confers "
            "authority. See MVC-W0F-SECRET-SOURCE-DECISION-001."
        )


class EnvironmentSecretProvider:
    """Non-production provider. The identifier names an environment variable.

    This is the same code path production takes — `resolve_secret` does not know
    which provider it holds — which is the point. The tests exercise the real
    resolution logic, and only the leaf differs.
    """

    authority = AUTHORITY_ENVIRONMENT

    def __init__(self, *, environ: Optional[dict] = None) -> None:
        self._environ = environ if environ is not None else os.environ

    def get(self, secret_id: str) -> str:
        if secret_id not in self._environ:
            raise SecretUnavailable(
                f"secret {secret_id!r} is not present in the environment; there is "
                "no default and no second source"
            )
        return _reject_if_not_a_usable_secret(secret_id, self._environ[secret_id])


# -- resolution --------------------------------------------------------------

def current_secret_mode(environ: Optional[dict] = None) -> str:
    """The configured secret mode. Unset or unknown fails closed.

    An unknown mode is refused rather than treated as the safest known one,
    because a typo in a deployment variable would otherwise select a mode
    silently — and the mode it selected would look deliberate afterwards.
    """
    env = environ if environ is not None else os.environ
    mode = (env.get(SECRET_MODE_ENV_VAR) or "").strip()
    if not mode:
        raise SecretUnavailable(
            f"{SECRET_MODE_ENV_VAR} is not set. The governed secret source must be "
            f"chosen explicitly (one of {sorted(VALID_SECRET_MODES)}); it has no "
            "default because the deployment where a default would matter is "
            "production."
        )
    if mode not in VALID_SECRET_MODES:
        raise SecretUnavailable(
            f"{SECRET_MODE_ENV_VAR}={mode!r} is not a known secret mode "
            f"(expected one of {sorted(VALID_SECRET_MODES)}); failing closed"
        )
    return mode


def build_secret_provider(environ: Optional[dict] = None) -> SecretProvider:
    """The provider for the configured mode."""
    env = environ if environ is not None else os.environ
    mode = current_secret_mode(env)
    if mode == SECRET_MODE_AWS:
        return AwsSecretsManagerProvider(region=env.get(AWS_REGION_ENV_VAR))
    return EnvironmentSecretProvider(environ=env)


def resolve_secret(secret_id: str, *, provider: SecretProvider) -> str:
    """Obtain a governed secret through a provider whose authority permits it.

    The authority check happens HERE rather than at construction, so a provider
    substituted later — in a test, a fixture, or by a future refactor — is
    checked at the moment its value would be used.
    """
    authority = getattr(provider, "authority", None)
    if authority not in GOVERNED_SECRET_AUTHORITIES:
        raise SecretUnavailable(
            f"{authority!r} is not a governed secret authority and may not supply "
            f"{secret_id!r}; only {sorted(GOVERNED_SECRET_AUTHORITIES)} may. "
            "See MVC-W0F-SECRET-SOURCE-DECISION-001."
        )
    value = provider.get(secret_id)
    # Validated again even though every provider validates: `provider` is a
    # Protocol, so an implementation this module has never seen can reach here.
    return _reject_if_not_a_usable_secret(secret_id, value)


def _required_identifier(
    env: dict, var: str, *, mode: str, default_in_environment_mode: str
) -> str:
    """The configured identifier for a governed secret.

    In `environment` mode the identifier defaults, because the identifier is the
    name of an environment variable and W0-A already fixed that name. In
    `aws_secrets_manager` mode there is no default: guessing a secret's name in
    production either fails loudly or, worse, finds a different secret.
    """
    configured = (env.get(var) or "").strip()
    if configured:
        return configured
    if mode == SECRET_MODE_ENVIRONMENT:
        return default_in_environment_mode
    raise SecretUnavailable(
        f"{var} is not set. Under {SECRET_MODE_ENV_VAR}={mode} the secret "
        "identifier is required and is never guessed."
    )


def session_secret_id(environ: Optional[dict] = None) -> str:
    env = environ if environ is not None else os.environ
    return _required_identifier(
        env, SESSION_SECRET_ID_ENV_VAR,
        mode=current_secret_mode(env),
        default_in_environment_mode=DEFAULT_SESSION_SECRET_ID_IN_ENVIRONMENT_MODE,
    )


def database_secret_id(environ: Optional[dict] = None) -> str:
    env = environ if environ is not None else os.environ
    return _required_identifier(
        env, DB_SECRET_ID_ENV_VAR,
        mode=current_secret_mode(env),
        default_in_environment_mode=DEFAULT_DB_SECRET_ID_IN_ENVIRONMENT_MODE,
    )


def resolve_session_signing_key(
    *, provider: Optional[SecretProvider] = None, environ: Optional[dict] = None
) -> str:
    """The session signing key, through the governed provider.

    W0-A's behaviour is preserved exactly: unset means the process refuses to
    start. What changes is that the key now arrives through the abstraction the
    decision requires, so production reads it from Secrets Manager without any
    code at the call site changing.
    """
    env = environ if environ is not None else os.environ
    prov = provider if provider is not None else build_secret_provider(env)
    return resolve_secret(session_secret_id(env), provider=prov)


#: Keys of the RDS-managed secret shape this understands. Named rather than
#: inferred: a secret that is missing one of these is malformed, and a connection
#: assembled from a partial secret would point somewhere unintended.
_DB_SECRET_REQUIRED_KEYS = ("username", "password", "host", "port", "dbname")


def resolve_database_url(
    *, provider: Optional[SecretProvider] = None, environ: Optional[dict] = None
) -> str:
    """The database connection URL, through the governed provider.

    Two shapes are accepted and both are validated; nothing is assembled from a
    partial value:

      * a complete connection URL string, which is how `environment` mode
        supplies it;
      * the managed-secret JSON object, which is what a provider-managed database
        credential looks like. Every key in `_DB_SECRET_REQUIRED_KEYS` must be
        present — a missing host is not defaulted to anything.

    No region and no endpoint appears here. Both arrive inside the secret or the
    URL, which is what keeps the KSA move a configuration change.
    """
    env = environ if environ is not None else os.environ
    prov = provider if provider is not None else build_secret_provider(env)
    raw = resolve_secret(database_secret_id(env), provider=prov)

    if not raw.lstrip().startswith("{"):
        if "://" not in raw:
            raise SecretUnavailable(
                "the database secret is neither a connection URL nor a managed "
                "credential object; refusing to assemble one"
            )
        return raw

    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        raise SecretUnavailable(
            "the database secret looks like JSON but does not parse; failing "
            "closed rather than falling back to a URL"
        ) from None
    if not isinstance(obj, dict):
        raise SecretUnavailable("the database secret JSON is not an object")
    missing = [k for k in _DB_SECRET_REQUIRED_KEYS if not str(obj.get(k, "")).strip()]
    if missing:
        raise SecretUnavailable(
            f"the database secret is missing required fields {missing}; a partial "
            "credential is not completed from defaults"
        )
    from urllib.parse import quote

    user = quote(str(obj["username"]), safe="")
    # Percent-encoded: a password containing '/', '@' or ':' silently truncates
    # or redirects the URL otherwise, and the resulting connection failure looks
    # like a wrong credential rather than a parsing bug.
    password = quote(str(obj["password"]), safe="")
    host = str(obj["host"])
    port = str(obj["port"])
    dbname = quote(str(obj["dbname"]), safe="")
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
