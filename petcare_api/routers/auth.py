import os
import hashlib
import hmac
import logging
from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from pydantic import BaseModel, StrictBool

from persistence import build_persistence
from licences import VetLicence  # FR-05 (U10)
from repositories import (
    InviteCode,
    PROVENANCE_REGISTRATION,
    PROVENANCE_SEED,
    RepositoryDenied,
    UserIdentity,
)
from secret_provider import (
    SecretUnavailable,
    resolve_session_signing_key,
    session_secret_id,
)

log = logging.getLogger("petcare.api.auth")

router = APIRouter(prefix="/api/auth", tags=["auth"])

#: W0-F. The serving layer's persistence, chosen explicitly by
#: PETCARE_PERSISTENCE_MODE and built at import so that a process configured for
#: a store it cannot reach does not start. See persistence.py: there is no
#: fallback from `postgres` to `memory`, because a fallback would leave
#: revocation silently broken across instances while every health check passed.
PERSISTENCE = build_persistence()

#: W0-F AC-7. The authoritative record of which sessions are still live.
SESSION_STORE = PERSISTENCE.session_store

#: W0-F item 4. Identity and invite codes, behind the same boundary.
IDENTITY_REPO = PERSISTENCE.identities
INVITE_REPO = PERSISTENCE.invites

#: SHA-256 of every session signing key that is permanently forbidden.
#:
#: W0-A2. The guard below used to compare against the retired key as a
#: PLAINTEXT literal. That worked, and it made the retired key impossible to
#: remove from the repository: a content-based history rewrite cannot tell the
#: difference between the secret as a leaked value and the secret as the value
#: a guard refuses. A Gate-5 offline rehearsal proved the consequence — the
#: rewrite replaced the comparand, and the resulting tree ACCEPTED the real
#: retired key, while the whole test suite still passed because the rewrite had
#: edited the assertions in step with the implementation.
#:
#: Storing the fingerprint keeps the behaviour identical and leaves nothing for
#: a rewrite to damage. Entries are permanent: a key that has been published
#: can never become safe again.
RETIRED_KEY_FINGERPRINTS = frozenset({
    # The W0-A literal default, published in this repository's history.
    "1cdd7efa59d45698ceba9652ee1c22aa7472503ee381af56833df8f98d65f4ca",
})


def _require_secret_key() -> str:
    """Session signing key — required, never defaulted.

    W0-A (MVC-EXEC / CP-2 Wave 0). The key was previously read with a literal
    fallback, so wherever the variable was unset every session token was signed
    with a key published in the source tree, and was therefore forgeable by
    anyone who could read this repository.

    This ordering is binding and must not be reversed: the fallback is removed
    BEFORE W0-B binds authorization to the session. Binding authorization to a
    session signed with a publicly-known key would replace a header bypass with
    a forgery bypass - strictly worse, because forged sessions look legitimate.

    The process refuses to start rather than run with an unknown-provenance key.
    The governed secret source (AWS Secrets Manager vs SSM Parameter Store) is
    deferred to the MyVetiCare AWS architecture decision; this function is
    indifferent to which supplies the environment.

    W0-A2: rejection is by SHA-256 fingerprint, so the forbidden value appears
    nowhere in this file. Behaviour is unchanged — unset, blank and retired keys
    are each refused, every other value is accepted.

    W0-F: the key now arrives through the governed provider abstraction rather
    than from `os.getenv` here. MVC-W0F-SECRET-SOURCE-DECISION-001 requires that
    application code never reads a secret at the point of use, so that production
    reads it from Secrets Manager without this function changing. Under
    `PETCARE_SECRET_MODE=environment` the identifier names an environment
    variable and the behaviour is byte-for-byte what it was; under
    `aws_secrets_manager` the same call reaches the governed store. Neither mode
    has a fallback, and the retired-key check below is unchanged and still runs
    last, so a key obtained from ANY source is still refused if it is retired.
    """
    try:
        key = resolve_session_signing_key()
    except SecretUnavailable as exc:
        # The message NAMES the configured identifier and keeps W0-A's wording.
        # T-SEC-01 matches on "<id> is not set", and in environment mode the
        # identifier is SECRET_KEY — so the existing control still binds to this
        # function unchanged rather than being rewritten to match new prose.
        raise RuntimeError(
            f"{session_secret_id()} is not set or could not be obtained from "
            f"governed secret storage ({exc}). Refusing to start: a session "
            "signing key must come from governed secret storage and has no safe "
            "default. See W0-A and MVC-W0F-SECRET-SOURCE-DECISION-001."
        ) from None
    # The same normalisation the equality check used, so the guard rejects
    # exactly the values it rejected before.
    if hashlib.sha256(key.strip().encode()).hexdigest() in RETIRED_KEY_FINGERPRINTS:
        raise RuntimeError(
            "SECRET_KEY is a retired signing key and is permanently prohibited. "
            "Refusing to start: tokens signed with it are forgeable. Rotate "
            "before use. See W0-A / W0-A2."
        )
    return key


SECRET_KEY = _require_secret_key()
COOKIE_NAME_SESSION = "petcare_session"
COOKIE_NAME_ROLE = "petcare_role"
COOKIE_MAX_AGE = 60 * 60 * 8  # 8 hours


def _serializer():
    return URLSafeTimedSerializer(SECRET_KEY)


#: scrypt work factors. Memory-hard by design: `n` sets the memory cost, which is
#: what makes a GPU or ASIC attack expensive rather than merely slow. These are
#: the parameters stored WITH each hash, so raising them later does not
#: invalidate existing credentials — see _verify_password's rehash path.
_SCRYPT_N = 2 ** 14   # 16384 — ~16 MiB per hash at r=8
_SCRYPT_R = 8
_SCRYPT_P = 1
_SCRYPT_DKLEN = 32
_SCRYPT_PREFIX = "scrypt"


def _hash_password(password: str) -> str:
    """Hash a password with a salted, work-factored, memory-hard KDF.

    W0-J. This was `hashlib.sha256(password.encode()).hexdigest()` — unsalted and
    unstretched. Unsalted means identical passwords produce identical digests, so
    one rainbow table breaks every account at once and equal hashes reveal equal
    passwords across users. Unstretched means a commodity GPU tries billions of
    candidates per second: a fast hash is the wrong primitive for a password, and
    SHA-256 is fast by design.

    scrypt is used rather than PBKDF2 because it is MEMORY-hard, so specialised
    hardware cannot buy the attacker much over general-purpose hardware. It is in
    the standard library, so this introduces no new dependency to audit.

    The parameters are stored in the hash string. That is what makes the work
    factor upgradable: raising `n` later leaves every existing credential
    verifiable, and each one is re-hashed on its owner's next successful login.
    """
    salt = os.urandom(16)
    dk = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P, dklen=_SCRYPT_DKLEN,
    )
    return f"{_SCRYPT_PREFIX}${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${salt.hex()}${dk.hex()}"


#: SQ-1 (v1.2 U26): verified against for an UNKNOWN identity so a failed sign-in costs the same either way.
_DUMMY_PASSWORD_HASH = None


def _dummy_hash() -> str:
    global _DUMMY_PASSWORD_HASH
    if _DUMMY_PASSWORD_HASH is None:
        _DUMMY_PASSWORD_HASH = _hash_password("not-a-real-password-" + uuid4().hex)
    return _DUMMY_PASSWORD_HASH


def _verify_password(password: str, stored: str) -> tuple[bool, bool]:
    """Verify a password. Returns (ok, needs_rehash).

    `needs_rehash` is true when the credential verified against a legacy or
    weaker-than-current format. The caller re-hashes on successful login, which
    is how a credential migration happens without ever seeing the plaintext at
    any other moment — there is no batch to run and no window in which old and
    new formats disagree.
    """
    if stored.startswith(_SCRYPT_PREFIX + "$"):
        try:
            _, n_s, r_s, p_s, salt_hex, dk_hex = stored.split("$")
            n, r, p = int(n_s), int(r_s), int(p_s)
            expected = bytes.fromhex(dk_hex)
            actual = hashlib.scrypt(
                password.encode("utf-8"),
                salt=bytes.fromhex(salt_hex),
                n=n, r=r, p=p, dklen=len(expected),
            )
        except (ValueError, TypeError):
            return False, False
        # Constant-time: a timing-variable comparison leaks the digest a byte at
        # a time, which is enough to forge a match without knowing the password.
        ok = hmac.compare_digest(actual, expected)
        return ok, ok and (n, r, p) != (_SCRYPT_N, _SCRYPT_R, _SCRYPT_P)

    if stored.startswith("$2"):  # legacy bcrypt
        try:
            from passlib.hash import bcrypt
            ok = bcrypt.verify(password, stored)
        except Exception:
            return False, False
        return ok, ok

    # Legacy unsalted SHA-256. Accepted ONLY to let an existing credential
    # migrate itself on next login; it is never produced by _hash_password.
    legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
    ok = hmac.compare_digest(legacy, stored)
    return ok, ok


# ---------------------------------------------------------------------------
# Identity and invite codes — through the repository boundary
# ---------------------------------------------------------------------------
#
# W0-F. These were module-level dicts. A dict read as persistence is a store
# with no constraints: it cannot refuse a role outside the catalogue, cannot
# refuse a blank tenant, and cannot make a duplicate email unrepresentable.
# Migration 0031 enforces all three structurally, and `repositories.py` performs
# the same refusals in memory mode so the suite proves the stronger behaviour
# rather than the weaker one.
#
# No SQL appears in this module and none should: the router depends on the
# protocol, which is what makes the store a configuration choice.


def seed_user(user_id: str, email: str, password: str, role: str,
              full_name: str | None = None, tenant_id: str | None = None):
    """Add a user to the configured identity store. Called at startup.

    W0-C: tenant_id is an attribute of the IDENTITY, established server-side.
    Before this change no tenant existed server-side at all - not on the user,
    not in the session - so there was nothing to authorize a request's tenant
    against, and every route simply trusted `body.tenant_id`. W0-F completes it
    by persisting the assignment.

    Seeding is an upsert keyed on `user_id`, so a restart re-establishes the
    pilot identities without duplicating them and without rebinding an existing
    id to a different address.
    """
    IDENTITY_REPO.upsert(UserIdentity(
        user_id=user_id,
        email=email,
        password_hash=_hash_password(password),
        role=role,
        full_name=full_name or email,
        tenant_id=tenant_id,
        provenance=PROVENANCE_SEED,
    ))


def _invite_ref(code: str) -> str:
    """X6 (MVC-EPC-D-001 D1): an invite code or issued credential is a secret; logs carry a short one-way reference."""
    import hashlib
    return "inv:" + hashlib.sha256(str(code).encode()).hexdigest()[:12]


def seed_invite_code(code: str, allowed_role: str,
                     expires_at: datetime | None = None):
    """Seed an invite code. Called at startup.

    Seeding deliberately does NOT reset consumption. Re-seeding at every process
    start is precisely when a consumed pilot code would be handed back, and the
    restart that did it would look like ordinary lifecycle rather than an
    authorization defect. See PostgresInviteCodeRepository.upsert.
    """
    INVITE_REPO.upsert(InviteCode(
        code=code,
        allowed_role=allowed_role,
        expires_at=expires_at,
    ))


def _log_safe(detail: dict) -> dict:
    """X-23: the auth log's view of an event — personal identifiers replaced by their one-way references."""
    from platform_identity_audit import email_ref
    return {("email_ref" if k == "email" else k): (email_ref(v) if k == "email" else v) for k, v in detail.items()}


def _log_auth_event(event_name: str, detail: dict):
    """A LOG LINE. Not the governed audit chain, and deliberately named so.

    This was called `_audit`, which is also the name of the governed,
    chain-linked, now-persisted audit writer in `main.py`. Two functions with the
    same name, one authoritative and one not, is how a reviewer comes to believe
    authentication events are in the audit log. They are not: nothing written
    here is hashed, linked, persisted, or verifiable.

    ## Why authentication events are NOT routed into the chain

    Not an oversight, and not deferred work — a governed record requires a
    tenant, and `audit_event.tenant_id` is `NOT NULL`. The events written here
    are mostly PRE-authentication: a failed sign-in has no authenticated actor,
    no established tenant, and frequently no existing identity at all.

    Routing them into the chain would therefore require inventing a tenant for
    them, and a default tenant is exactly what W0-C removed and what the audit
    probe's own hardening refuses to reintroduce. `UNATTRIBUTED` exists for the
    UI probe because that surface has a governed decision behind it; extending it
    to authentication would be making the same decision by implementation.

    Recorded as an open gap rather than closed by guessing:
    `AUTH_EVENTS_OUTSIDE_AUDIT_CHAIN` — see the W0-G evidence bundle. Closing it
    needs a governed answer on how a tenantless security event is recorded.
    """
    # X-23 (MVC-EPC-D-001 D2): the LOG LINE never carries a raw email address. It carries the same one-way reference the
    # platform identity chain uses as its subject (platform_identity_audit.email_ref), so a security reviewer can still
    # correlate a log line with a chain event. The chain below still receives the detail it needs to resolve a subject.
    log.info("AUTH_EVENT %s %s", event_name, _log_safe(detail))
    # SQ-1 (Sponsor act MVC-SQ1-PLATFORM-IDENTITY-AUDIT-001; v1.2 U26): pre-tenant identity/security events are ALSO
    # chained — on the PLATFORM IDENTITY chain, never a tenant chain, even when the identity has a tenant.
    if event_name in _PLATFORM_CHAINED:
        _platform_chain(event_name, detail)


#: Registration (success, failure, licence submission) and every failed sign-in — the account actions SQ-1 places on
#: the platform identity chain.
_PLATFORM_CHAINED = frozenset({"auth.user_registered", "auth.register_failed", "auth.vet_licence_submitted",
                               "auth.sign_in_failed"})
#: D2 (Sponsor ruling 1): owner self-registration, email verification and password reset are account actions too. Kept
#: as a separate union so the frozen literal above stays byte-identical for the committed U26 perturbation corpus.
_PLATFORM_CHAINED = _PLATFORM_CHAINED | {"auth.owner_self_registered", "auth.email_verified",
                                         "auth.password_reset_completed"}


def _platform_chain(event_name: str, detail: dict) -> None:
    from platform_identity_audit import SUBJECT_IDENTITY, SUBJECT_UNKNOWN, email_ref
    user_id = detail.get("user_id")
    if not user_id and detail.get("email"):
        known = IDENTITY_REPO.get_by_email(detail["email"])
        user_id = known.user_id if known else None
    PERSISTENCE.platform_audit.append({
        "event_id": str(uuid4()), "event_name": event_name,
        "subject_kind": SUBJECT_IDENTITY if user_id else SUBJECT_UNKNOWN,
        "subject_ref": user_id or email_ref(detail.get("email", "")),
        "outcome": "denied" if event_name.endswith("_failed") else "success",
        "reason_code": detail.get("reason"), "correlation_id": str(uuid4()),
        "occurred_at": datetime.now(timezone.utc).isoformat()})


# ---------------------------------------------------------------------------
class SignInRequest(BaseModel):
    email: str
    password: str


class LicenceDetails(BaseModel):
    """FR-05 AC-FR-05-01: a veterinarian registers WITH licence details (MEWA / the competent
    KSA veterinary licensing authority). Nothing here verifies the licence; verification is a
    separate, named, audited act (/api/admin/practitioners/licences/{id}/verify)."""
    model_config = {"extra": "forbid"}

    licence_number: str
    issuing_authority: str
    expires_on: str  # YYYY-MM-DD


class RegisterRequest(BaseModel):
    email: str
    password: str
    invite_code: str
    role: str
    name: str
    phone: str | None = None
    licence: LicenceDetails | None = None


# ── POST /api/auth/sign-in ────────────────────────────────────────
@router.post("/sign-in")
async def sign_in(body: SignInRequest):
    user = IDENTITY_REPO.get_by_email(body.email)
    if not user:
        # SQ-1 (v1.2 U26): the response for an unknown identity is indistinguishable from a wrong password — same
        # status and body, and a password verification is still performed so timing does not reveal existence.
        _verify_password(body.password, _dummy_hash())
        _log_auth_event("auth.sign_in_failed",
               {"email": body.email, "reason": "user_not_found"})
        raise HTTPException(status_code=401,
                            detail={"error": "INVALID_CREDENTIALS"})

    password_ok, needs_rehash = _verify_password(body.password, user.password_hash)

    # W0-J: rehash-on-next-login. A credential stored in a legacy format is
    # upgraded here, at the one moment the plaintext is legitimately available.
    # W0-F: written THROUGH the repository, so the upgrade survives the process.
    # While identity lived in a dict the rehash was lost at the next restart and
    # the legacy hash came back, so the migration never actually completed for
    # anyone — it only appeared to, for the lifetime of one process.
    if password_ok and needs_rehash:
        IDENTITY_REPO.set_password_hash(user.user_id, _hash_password(body.password))

    if not password_ok:
        _log_auth_event("auth.sign_in_failed",
               {"email": body.email, "reason": "bad_password"})
        raise HTTPException(status_code=401,
                            detail={"error": "INVALID_CREDENTIALS"})

    # A disabled identity holds no session. Checked AFTER the password so the
    # response cannot be used to enumerate which addresses are disabled.
    if not user.is_active:
        _log_auth_event("auth.sign_in_failed",
               {"email": body.email, "reason": "identity_disabled"})
        raise HTTPException(status_code=401,
                            detail={"error": "INVALID_CREDENTIALS"})

    # MVC-EPC-D-001 D2 (owner self-registration): an identity that must verify its address holds no session until it
    # has. Checked after the password, like the disabled check, so the answer cannot enumerate unverified accounts.
    if PERSISTENCE.account_tokens.verification_pending(user.user_id):
        _log_auth_event("auth.sign_in_failed", {"email": body.email, "reason": "email_not_verified"})
        raise HTTPException(status_code=403, detail={"error": "EMAIL_NOT_VERIFIED"})

    role = user.role
    user_id = user.user_id
    name = user.full_name

    # W0-F AC-7: the session becomes a server-side record BEFORE the cookie is
    # minted, and the cookie carries only its id. A cookie whose id is not in the
    # store is not a session, however well signed it is.
    record = SESSION_STORE.create(
        user_id=user_id,
        tenant_id=user.tenant_id,
        role=role,
        ttl_seconds=COOKIE_MAX_AGE,
    )
    token = _serializer().dumps(
        {"user_id": user_id, "email": body.email, "role": role,
         "tenant_id": user.tenant_id, "sid": record.session_id}
    )

    _log_auth_event("auth.sign_in_success",
           {"user_id": user_id, "email": body.email, "role": role})
    _chain_account_event("account.signed_in", user_id=user_id, role=role, tenant_id=user.tenant_id,
                         session_id=record.session_id)

    resp = JSONResponse(content={
        "user": {
            "user_id": user_id,
            "email": body.email,
            "full_name": name,
            "role": role,
        }
    })
    # httponly session token — not readable by JS
    resp.set_cookie(COOKIE_NAME_SESSION, token,
                    max_age=COOKIE_MAX_AGE, httponly=True,
                    secure=True, samesite="lax")
    # role cookie — readable by Next.js middleware
    resp.set_cookie(COOKIE_NAME_ROLE, role,
                    max_age=COOKIE_MAX_AGE, httponly=False,
                    secure=True, samesite="lax")
    return resp


# ── POST /api/auth/register ───────────────────────────────────────
@router.post("/register", status_code=201)
async def register(body: RegisterRequest):
    """
    Pilot-gated registration. Requires a valid, unused, non-expired
    invite code whose allowed_role matches the requested role.
    On success the user is authenticated (session + role cookies set)
    so the frontend can route directly to the role portal.
    """
    # SQ-3 #14 (MVC-EPC-D-001 D1): a credential issued by an admin is stored one-way ("sha256:<hex>"); a seeded pilot
    # code is stored as itself. Look the raw value up first, then its one-way form; consume whichever matched.
    invite_key = body.invite_code
    invite = INVITE_REPO.get(invite_key)
    if invite is None:
        from sq3_ops import credential_key
        invite_key = credential_key(body.invite_code)
        invite = INVITE_REPO.get(invite_key)
    if invite is None or invite.is_consumed():
        _log_auth_event("auth.register_failed",
               {"reason": "invite_invalid_or_used",
                "invite_ref": _invite_ref(body.invite_code), "email": body.email})
        raise HTTPException(status_code=400,
                            detail={"error": "INVALID_INVITE"})

    now = datetime.now(timezone.utc)
    if invite.is_expired_at(now):
        _log_auth_event("auth.register_failed",
               {"reason": "invite_expired",
                "invite_ref": _invite_ref(body.invite_code), "email": body.email})
        raise HTTPException(status_code=400,
                            detail={"error": "INVITE_EXPIRED"})

    if invite.allowed_role != body.role:
        _log_auth_event("auth.register_failed",
               {"reason": "role_mismatch",
                "invite_role": invite.allowed_role,
                "requested_role": body.role, "email": body.email})
        raise HTTPException(status_code=400,
                            detail={"error": "ROLE_MISMATCH"})

    # FR-05 (U10). Checked before the invite is spent: a veterinarian registration without
    # licence details, or with a licence already expired, never completes.
    licence_expiry = None
    if body.role == "veterinarian":
        lic = body.licence
        try:
            licence_expiry = datetime.strptime(lic.expires_on, "%Y-%m-%d").date() if lic else None
        except ValueError:
            licence_expiry = None
        if (lic is None or licence_expiry is None or not lic.licence_number.strip()
                or not lic.issuing_authority.strip()):
            _log_auth_event("auth.register_failed", {"reason": "licence_details_required", "email": body.email})
            raise HTTPException(status_code=400, detail={"error": "LICENCE_DETAILS_REQUIRED"})
        if licence_expiry < now.date():
            _log_auth_event("auth.register_failed", {"reason": "licence_expired", "email": body.email})
            raise HTTPException(status_code=400, detail={"error": "LICENCE_EXPIRED"})

    # Checked before the code is spent, so a registration that was never going
    # to succeed does not burn somebody else's invite.
    if IDENTITY_REPO.get_by_email(body.email) is not None:
        _log_auth_event("auth.register_failed",
               {"reason": "email_exists", "email": body.email})
        raise HTTPException(status_code=409,
                            detail={"error": "EMAIL_EXISTS"})

    # W0-F. Consumption happens HERE, as one conditional write, and BEFORE the
    # identity is created. The ordering is deliberate and it is the fail-closed
    # one: two simultaneous registrations against the same code both pass the
    # read above, and only one of them can win this write. Creating the identity
    # first and marking the code afterwards would admit both.
    #
    # The residual cost is that a code can be spent by a registration that then
    # fails on the UNIQUE email constraint. That direction denies rather than
    # permits, which is the direction to fail in.
    if not INVITE_REPO.consume(invite_key, email=body.email, at=now):
        _log_auth_event("auth.register_failed",
               {"reason": "invite_invalid_or_used",
                "invite_ref": _invite_ref(body.invite_code), "email": body.email})
        raise HTTPException(status_code=400,
                            detail={"error": "INVALID_INVITE"})

    user_id = f"u-{uuid4().hex[:12]}"
    try:
        IDENTITY_REPO.create(UserIdentity(
            user_id=user_id,
            email=body.email,
            password_hash=_hash_password(body.password),
            role=body.role,
            full_name=body.name,
            # No tenant. Registration establishes an identity, never its tenant
            # authority: W0-C makes tenant a server-side assignment, and a value
            # taken from a registration form would be caller-supplied authority.
            # The identity fails closed at require_tenant() until assigned.
            tenant_id=None,
            provenance=PROVENANCE_REGISTRATION,
        ))
    except RepositoryDenied:
        _log_auth_event("auth.register_failed",
               {"reason": "email_exists", "email": body.email})
        raise HTTPException(status_code=409,
                            detail={"error": "EMAIL_EXISTS"})

    _log_auth_event("auth.user_registered",
           {"user_id": user_id, "email": body.email, "role": body.role,
            "invite_ref": _invite_ref(body.invite_code)})

    if licence_expiry is not None:
        submitted = PERSISTENCE.licences.submit(VetLicence(
            licence_id=str(uuid4()), actor_id=user_id, licence_number=body.licence.licence_number.strip(),
            issuing_authority=body.licence.issuing_authority.strip(), expires_on=licence_expiry,
            submitted_at=now))
        # Pre-session and tenantless: recorded in the auth event log (SQ-1 covers whether such
        # events belong in the tenant audit chain). The verification itself is chain-audited.
        _log_auth_event("auth.vet_licence_submitted",
                        {"user_id": user_id, "licence_id": submitted.licence_id})

    # W0-F AC-7. Registration mints a cookie, so registration must create the
    # session record too.
    #
    # It did not, and the consequence was live: the cookie carried no `sid`, and
    # `read_session` refuses a session id it cannot find with
    # SESSION_NOT_ESTABLISHED. Every protected route therefore returned 401 to a
    # user who had just registered successfully and been handed cookies — while
    # /api/auth/me, which parses the cookie itself rather than going through
    # read_session, answered 200. A registered user appeared signed in and could
    # do nothing.
    record = SESSION_STORE.create(
        user_id=user_id,
        tenant_id=None,
        role=body.role,
        ttl_seconds=COOKIE_MAX_AGE,
    )
    token = _serializer().dumps(
        {"user_id": user_id, "email": body.email, "role": body.role,
         "tenant_id": None, "sid": record.session_id}
    )

    resp = JSONResponse(status_code=201, content={
        "user": {
            "user_id": user_id,
            "email": body.email,
            "full_name": body.name,
            "role": body.role,
        }
    })
    resp.set_cookie(COOKIE_NAME_SESSION, token,
                    max_age=COOKIE_MAX_AGE, httponly=True,
                    secure=True, samesite="lax")
    resp.set_cookie(COOKIE_NAME_ROLE, body.role,
                    max_age=COOKIE_MAX_AGE, httponly=False,
                    secure=True, samesite="lax")
    return resp


# ── Session identity (W0-B) ───────────────────────────────────────
def read_session(request: Request) -> dict:
    """Return the validated session payload, or raise 401.

    W0-B. This is the ONLY source of authority for authorization decisions.
    The payload is signed with the key W0-A now requires from governed secret
    storage, so its `role` was written server-side at sign-in from the user
    record - it cannot be supplied or altered by the caller.

    The non-httponly `petcare_role` cookie is a display convenience for the
    browser and carries NO authority; it is deliberately not read here.
    """
    token = request.cookies.get(COOKIE_NAME_SESSION)
    if not token:
        raise HTTPException(status_code=401, detail={"error": "NOT_AUTHENTICATED"})
    try:
        payload = _serializer().loads(token, max_age=COOKIE_MAX_AGE)
    except SignatureExpired:
        raise HTTPException(status_code=401, detail={"error": "SESSION_EXPIRED"})
    except BadSignature:
        raise HTTPException(status_code=401, detail={"error": "INVALID_SESSION"})
    if not isinstance(payload, dict) or not payload.get("role"):
        raise HTTPException(status_code=401, detail={"error": "INVALID_SESSION"})

    # W0-F AC-7. Signature verification above proves the payload was written by
    # this service and not altered. It CANNOT prove the session is still valid —
    # that the user has not signed out, been disabled, or had the session
    # revoked. Integrity is a statement about the past; validity is a statement
    # about now, and only the store can answer it.
    #
    # ORDER IS LOAD-BEARING. The signature check runs FIRST and is never skipped:
    # accepting a session on a store hit alone would mean a forged or stale
    # cookie bearing a real session id is honoured, and it would silently undo
    # the emergency property that rotating the signing key revokes everything.
    sid = payload.get("sid")
    if not sid:
        # No fallback for cookies minted before the store existed. A legacy
        # acceptance path is a second, ungoverned way in.
        raise HTTPException(status_code=401, detail={"error": "SESSION_NOT_ESTABLISHED"})

    record = SESSION_STORE.get_active(sid, tenant_id=payload.get("tenant_id"))
    if record is None:
        # Unknown, revoked, expired and cross-tenant are deliberately one answer.
        raise HTTPException(status_code=401, detail={"error": "SESSION_REVOKED_OR_EXPIRED"})

    # FR-01 AC-FR-01-03 (U20): authority comes from SERVER-HELD state, never from the token. The tenant and role are
    # the session record's, and the identity's CURRENT membership must still match it: a membership that has ended
    # or moved makes every older session fail closed at the next request.
    ident = IDENTITY_REPO.get_by_user_id(record.user_id)
    if (ident is None or getattr(ident, "disabled_at", None) is not None or ident.tenant_id != record.tenant_id
            or ident.user_id != payload.get("user_id")):
        raise HTTPException(status_code=401, detail={"error": "SESSION_TENANT_STALE"})
    return {**payload, "user_id": record.user_id, "tenant_id": record.tenant_id, "role": record.role}


def _chain_account_event(event_name: str, *, user_id: str, role: str, tenant_id, session_id: str) -> None:
    """FR-01 AC-FR-01-03 (U20): a session-bearing account action is written to the governed audit chain with the
    session actor. Tenantless (pre-session) events stay in the auth log — SPONSOR_QUEUE SQ-1 decides them."""
    if not tenant_id:
        return
    import main as _main  # the served app module; loaded before any request reaches this router
    _main._audit(event_name=event_name, actor_id=user_id, actor_role=role, tenant_id=tenant_id,
                 resource_type="account_session", resource_id=session_id, action_result="success",
                 correlation_id=str(uuid4()))


def require_tenant(request: Request, requested: str | None = None) -> str:
    """The caller's authorized tenant. Server-derived, never client-supplied.

    W0-C. A client-supplied tenant identifier may act as a RESOURCE SELECTOR
    only after it is authorized against this value - it is never authority.
    There is deliberately NO default: the previous
    `x_tenant_id: Header(default="platform")` meant an omitted header silently
    granted the "platform" scope.
    """
    payload = read_session(request)
    authorized = payload.get("tenant_id")
    if not authorized:
        raise HTTPException(
            status_code=403,
            detail={"error": "NO_TENANT_AUTHORITY",
                    "reason": "identity carries no server-side tenant assignment"},
        )
    if requested is not None and requested != authorized:
        raise HTTPException(
            status_code=403,
            detail={"error": "TENANT_SCOPE_DENIED",
                    "reason": "requested tenant is not authorized for this identity"},
        )
    return authorized


# ── GET /api/auth/me ──────────────────────────────────────────────
# ---------------------------------------------------------------------------------------------------------------------
# Owner self-registration, email verification, password reset (MVC-EPC-D-001 Lane D, D2).
# Sponsor ruling 1 (2026-09-28): BUILD_FULLY_BEHIND_FEATURE_SWITCH — production default OFF. When OFF the invite-only
# pilot is authoritative and /self-register refuses (no API bypass). When ON: the owner's tenant comes from SERVER
# configuration (PETCARE_SELF_REGISTRATION_TENANT), never from the request; the address must be verified through the
# governed email adapter before the first sign-in. A missing email provider or tenant makes the feature fail closed.
# ---------------------------------------------------------------------------------------------------------------------
SELF_REGISTRATION_SWITCH = "PETCARE_OWNER_SELF_REGISTRATION"
SELF_REGISTRATION_TENANT = "PETCARE_SELF_REGISTRATION_TENANT"
PUBLIC_WEB_ORIGIN = "PETCARE_PUBLIC_WEB_ORIGIN"
MIN_PASSWORD_LENGTH = 10
EMAIL_ADAPTER = None                                   # built on first use; tests may substitute a FakeEmailAdapter


def self_registration_enabled(env=None) -> bool:
    env = os.environ if env is None else env
    return (env.get(SELF_REGISTRATION_SWITCH) or "").strip().lower() in ("on", "true", "1")


def _email():
    global EMAIL_ADAPTER
    from adapters.email import EmailUnavailable, build_email_adapter
    if EMAIL_ADAPTER is None:
        try:
            EMAIL_ADAPTER = build_email_adapter()
        except EmailUnavailable:
            raise HTTPException(503, {"error": "EMAIL_PROVIDER_UNAVAILABLE"}) from None
    return EMAIL_ADAPTER


def _send(to: str, template: str, locale: str, link_path: str, token: str) -> None:
    from adapters.email import EmailMessage, EmailUnavailable
    origin = (os.environ.get(PUBLIC_WEB_ORIGIN) or "").rstrip("/")
    try:
        _email().send(EmailMessage(to=to, template=template, locale=locale if locale in ("ar", "en") else "ar",
                                   params={"link": f"{origin}{link_path}?token={token}"}))
    except EmailUnavailable:
        raise HTTPException(503, {"error": "EMAIL_PROVIDER_UNAVAILABLE"}) from None


def _email_ready() -> None:
    """Fail closed BEFORE creating anything if no email provider is configured."""
    from adapters.email import UnconfiguredEmailAdapter
    if isinstance(_email(), UnconfiguredEmailAdapter):
        raise HTTPException(503, {"error": "EMAIL_PROVIDER_UNAVAILABLE"})


class RegistrationOptions(BaseModel):
    owner_self_registration: bool


@router.get("/registration-options")
async def registration_options() -> RegistrationOptions:
    return RegistrationOptions(owner_self_registration=self_registration_enabled())


class SelfRegisterRequest(BaseModel):
    model_config = {"extra": "forbid"}

    email: str
    password: str
    name: str
    locale: str = "ar"
    #: J-O2: the PDPL privacy notice must be accepted, and the acceptance is recorded server-side (owner_consent).
    privacy_notice_accepted: bool = False
    #: D2d (R13.3): an OPTIONAL, separate choice — care reminders are consented to only by an explicit true, never implied
    #: by the privacy notice. Absent or false records nothing (the owner can grant it later on /account).
    care_reminders: StrictBool = False     # strict: "yes" / 1 are refused (422), never read as consent


@router.post("/self-register", status_code=201)
async def self_register(body: SelfRegisterRequest):
    if not self_registration_enabled():
        raise HTTPException(404, {"error": "SELF_REGISTRATION_DISABLED"})
    from tenants import require_assignable
    tenant_id = (os.environ.get(SELF_REGISTRATION_TENANT) or "").strip()
    try:
        require_assignable(PERSISTENCE.tenants, tenant_id or None)
    except Exception:
        raise HTTPException(503, {"error": "SELF_REGISTRATION_TENANT_UNAVAILABLE"}) from None
    email = body.email.strip().lower()
    if "@" not in email or not body.name.strip():
        raise HTTPException(400, {"error": "REGISTRATION_INVALID"})
    if len(body.password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(400, {"error": "PASSWORD_TOO_SHORT", "minimum": MIN_PASSWORD_LENGTH})
    if body.privacy_notice_accepted is not True:
        raise HTTPException(400, {"error": "PRIVACY_NOTICE_REQUIRED"})
    _email_ready()
    if IDENTITY_REPO.get_by_email(email) is not None:
        raise HTTPException(409, {"error": "EMAIL_EXISTS"})
    now = datetime.now(timezone.utc)
    user_id = f"u-{uuid4().hex[:12]}"
    try:
        IDENTITY_REPO.create(UserIdentity(user_id=user_id, email=email, password_hash=_hash_password(body.password),
                                          role="owner", full_name=body.name.strip(), tenant_id=tenant_id,
                                          provenance=PROVENANCE_REGISTRATION))
    except RepositoryDenied:
        raise HTTPException(409, {"error": "EMAIL_EXISTS"}) from None
    import owner_consent
    PERSISTENCE.owner_consent.append(owner_consent.ConsentEvent(
        event_id=str(uuid4()), tenant_id=tenant_id, user_id=user_id, purpose=owner_consent.PRIVACY_NOTICE,
        action=owner_consent.GRANT, origin="self_registration", policy_version=owner_consent.POLICY_VERSION, at=now))
    if body.care_reminders is True:
        PERSISTENCE.owner_consent.append(owner_consent.ConsentEvent(
            event_id=str(uuid4()), tenant_id=tenant_id, user_id=user_id, purpose=owner_consent.CARE_REMINDERS,
            action=owner_consent.GRANT, origin="self_registration", policy_version=owner_consent.POLICY_VERSION, at=now))
    PERSISTENCE.account_tokens.require_verification(user_id, now=now)
    token = PERSISTENCE.account_tokens.issue(user_id, "EMAIL_VERIFICATION", now=now)
    _send(email, "EMAIL_VERIFICATION", body.locale, "/verify-email", token)
    _log_auth_event("auth.owner_self_registered", {"user_id": user_id, "email": email})
    return {"user_id": user_id, "verification_required": True}


class TokenRequest(BaseModel):
    model_config = {"extra": "forbid"}

    token: str


@router.post("/verify-email")
async def verify_email(body: TokenRequest):
    now = datetime.now(timezone.utc)
    user_id = PERSISTENCE.account_tokens.consume(body.token, "EMAIL_VERIFICATION", now=now)
    if user_id is None:
        raise HTTPException(400, {"error": "TOKEN_INVALID_OR_EXPIRED"})
    PERSISTENCE.account_tokens.mark_verified(user_id, now=now)
    _log_auth_event("auth.email_verified", {"user_id": user_id})
    return {"verified": True}


class ResetRequest(BaseModel):
    model_config = {"extra": "forbid"}

    email: str
    locale: str = "ar"


@router.post("/password-reset/request", status_code=202)
async def password_reset_request(body: ResetRequest):
    """Always 202 for any address (no enumeration). A reset link is sent only to an existing, active identity."""
    _email_ready()
    user = IDENTITY_REPO.get_by_email(body.email.strip().lower()) or IDENTITY_REPO.get_by_email(body.email)
    if user is not None and user.is_active:
        token = PERSISTENCE.account_tokens.issue(user.user_id, "PASSWORD_RESET", now=datetime.now(timezone.utc))
        _send(user.email, "PASSWORD_RESET", body.locale, "/reset-password", token)
    _log_auth_event("auth.password_reset_requested", {"email": body.email})
    return {"accepted": True}


class ResetConfirm(BaseModel):
    model_config = {"extra": "forbid"}

    token: str
    password: str


@router.post("/password-reset/confirm")
async def password_reset_confirm(body: ResetConfirm):
    if len(body.password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(400, {"error": "PASSWORD_TOO_SHORT", "minimum": MIN_PASSWORD_LENGTH})
    now = datetime.now(timezone.utc)
    user_id = PERSISTENCE.account_tokens.consume(body.token, "PASSWORD_RESET", now=now)
    if user_id is None:
        raise HTTPException(400, {"error": "TOKEN_INVALID_OR_EXPIRED"})
    user = IDENTITY_REPO.get_by_user_id(user_id)
    IDENTITY_REPO.set_password_hash(user_id, _hash_password(body.password))
    revoked = SESSION_STORE.revoke_all_for_user(user_id, tenant_id=user.tenant_id) if user and user.tenant_id else 0
    _log_auth_event("auth.password_reset_completed", {"user_id": user_id, "sessions_revoked": revoked})
    return {"reset": True, "sessions_revoked": revoked}


@router.get("/me")
async def me(request: Request):
    # NFR-08 / SQ-3 (v1.3 U28): /me validated only the cookie signature, so a REVOKED session (sign-out, or an
    # assisted MFA reset revoking every session of its subject) still read as signed in here. It now takes the same
    # path as every protected route: signature, server-held session record, revocation and tenant staleness.
    payload = read_session(request)

    user = IDENTITY_REPO.get_by_email(payload["email"])
    if not user:
        raise HTTPException(status_code=401,
                            detail={"error": "USER_NOT_FOUND"})

    _log_auth_event("auth.me_called",
           {"user_id": payload["user_id"], "role": payload["role"]})

    return {
        "user_id": payload["user_id"],
        "email": payload["email"],
        "full_name": user.full_name,
        "role": payload["role"],
    }


# ── POST /api/auth/sign-out ──────────────────────────────────────
@router.post("/sign-out")
async def sign_out(request: Request):
    user_id = "anonymous"
    token = request.cookies.get(COOKIE_NAME_SESSION)
    if token:
        try:
            payload = _serializer().loads(token, max_age=COOKIE_MAX_AGE)
            user_id = payload.get("user_id", "anonymous")
        except Exception:
            payload = None
        # FR-01 (U20): sign-out ENDS the server session — deleting the cookie alone left the session live for
        # anyone holding a copy of it. The act is chained with the session actor.
        record = SESSION_STORE.get_active(payload.get("sid"), tenant_id=payload.get("tenant_id")) \
            if isinstance(payload, dict) and payload.get("sid") else None
        if record is not None:
            if record.tenant_id:
                SESSION_STORE.revoke(record.session_id, tenant_id=record.tenant_id)
            _chain_account_event("account.signed_out", user_id=record.user_id, role=record.role,
                                 tenant_id=record.tenant_id, session_id=record.session_id)

    _log_auth_event("auth.sign_out", {"user_id": user_id})

    resp = JSONResponse(content={"signed_out": True})
    resp.delete_cookie(COOKIE_NAME_SESSION)
    resp.delete_cookie(COOKIE_NAME_ROLE)
    return resp
