# A2 / A10 — the governed secret provider, implemented

```
SECRET_PROVIDER_IMPLEMENTED=YES
SECRET_AUTHORITY=AWS_SECRETS_MANAGER
CONFIG_AUTHORITY=AWS_SSM_PARAMETER_STORE_FOR_NON_SECRET_CONFIGURATION_ONLY
SECRET_FAIL_CLOSED=YES
LIVE_SECRET_CREATED=NO
LIVE_AWS_CALL_MADE=NO
BOTO3_REQUIRED_BY_TESTS=NO
```

`MVC-W0F-SECRET-SOURCE-DECISION-001` defined the contract and nothing implemented
it; the previous receipt records `SECRET_PROVIDER=CONTRACT_DEFINED_NOT_IMPLEMENTED`.
`petcare_api/secret_provider.py` is that implementation.

## Controls

| ID | Control | Result |
|---|---|---|
| SEC-SECRET-01 | missing session secret → fails closed, and the router refuses to start | PASS |
| SEC-SECRET-02 | missing DB secret → the adapter cannot initialise, and `build_persistence` raises rather than returning memory | PASS |
| SEC-SECRET-03 | empty / whitespace-only secret → denied | PASS |
| SEC-SECRET-04 | placeholder secret → denied, in any casing | PASS |
| SEC-SECRET-04c | a real high-entropy secret containing the substring `test` or `default` is **accepted** | PASS |
| SEC-SECRET-05 | Parameter Store is absent from `GOVERNED_SECRET_AUTHORITIES` and is refused at both the resolver and the provider | PASS |
| SEC-SECRET-05d/e | an unknown or undeclared authority is refused; the check happens at USE, not at construction | PASS |
| SEC-SECRET-06 | `routers/auth.py` no longer reads `SECRET_KEY` from the environment at the point of use; `secret_provider.py` has no defaulting environment read | PASS |

Plus: unset and unknown `PETCARE_SECRET_MODE` both fail closed; the AWS provider
constructs without the SDK or a credential; an unset `PETCARE_AWS_REGION` fails
closed; a managed-credential object missing any required field is refused rather
than completed from defaults; a URI-reserved character in a password is
percent-encoded.

```
TESTS=petcare_api/tests/test_secret_provider.py   64 passed
```

## W0-A behaviour preserved exactly

The signing key now arrives through the provider, and the retired-key
fingerprint check still runs **last** — so a key obtained from any source is
still refused if it is retired. The `RuntimeError` still names the configured
identifier and keeps W0-A's wording, so `T-SEC-01`
(`test_secret_key_required.py`) binds to the function unchanged rather than
being rewritten to match new prose.

```
ASSERTIONS_WEAKENED=0
```

## Percent-encoding

Recorded because it has bitten this portfolio before: a connection-string
credential containing `/`, `@` or `:` silently truncates or redirects the URL,
and the resulting failure looks like a wrong credential rather than a parsing
bug. `resolve_database_url` percent-encodes the username, password and database
name.

## Not done, and gated

```
No secret was created, read, written or rotated.
No AWS account, role, policy, KMS key or region was named or provisioned.
Secret CREATION and ENTRY remain GATE_CREDENTIAL_ENTRY.
```
