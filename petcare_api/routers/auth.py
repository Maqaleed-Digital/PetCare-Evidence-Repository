import os
import hashlib
import hmac
import logging
from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from pydantic import BaseModel

from session_store import InMemorySessionStore

log = logging.getLogger("petcare.api.auth")

router = APIRouter(prefix="/api/auth", tags=["auth"])

#: W0-F AC-7. The authoritative record of which sessions are still live.
#: In-memory for now; the production implementation is a table in the store named
#: by MVC-W0F-DATA-STORE-DECISION-001, and applying it is GATE_LIVE_APPLY.
SESSION_STORE = InMemorySessionStore()

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
    """
    key = os.getenv("SECRET_KEY")
    if not key or not key.strip():
        raise RuntimeError(
            "SECRET_KEY is not set. Refusing to start: a session signing key "
            "must come from governed secret storage and has no safe default. "
            "See W0-A."
        )
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
# In-memory user + invite-code store (pilot phase — DB wiring deferred)
# ---------------------------------------------------------------------------
_users: dict[str, dict] = {}
_invite_codes: dict[str, dict] = {}


def seed_user(user_id: str, email: str, password: str, role: str,
              full_name: str | None = None, tenant_id: str | None = None):
    """Add a user to the in-memory store. Called at startup.

    W0-C: tenant_id is an attribute of the IDENTITY, established server-side.
    Before this change no tenant existed server-side at all - not on the user,
    not in the session - so there was nothing to authorize a request's tenant
    against, and every route simply trusted `body.tenant_id`. Persisting this
    per-user assignment is completed by W0-F.
    """
    _users[email] = {
        "id": user_id,
        "email": email,
        "password_hash": _hash_password(password),
        "role": role,
        "full_name": full_name or email,
        "tenant_id": tenant_id,
    }


def seed_invite_code(code: str, allowed_role: str,
                     expires_at: datetime | None = None):
    """Seed an invite code in the in-memory store. Called at startup."""
    _invite_codes[code] = {
        "code": code,
        "allowed_role": allowed_role,
        "expires_at": expires_at,
        "used_at": None,
        "assigned_email": None,
    }


def _audit(event_name: str, detail: dict):
    """Lightweight audit log — matches main.py pattern."""
    log.info("AUDIT %s %s", event_name, detail)


# ---------------------------------------------------------------------------
class SignInRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    invite_code: str
    role: str
    name: str
    phone: str | None = None


# ── POST /api/auth/sign-in ────────────────────────────────────────
@router.post("/sign-in")
async def sign_in(body: SignInRequest):
    user = _users.get(body.email)
    if not user:
        _audit("auth.sign_in_failed",
               {"email": body.email, "reason": "user_not_found"})
        raise HTTPException(status_code=401,
                            detail={"error": "INVALID_CREDENTIALS"})

    stored = user["password_hash"]
    password_ok = False

    password_ok, needs_rehash = _verify_password(body.password, stored)

    # W0-J: rehash-on-next-login. A credential stored in a legacy format is
    # upgraded here, at the one moment the plaintext is legitimately available.
    if password_ok and needs_rehash:
        user["password_hash"] = _hash_password(body.password)

    if not password_ok:
        _audit("auth.sign_in_failed",
               {"email": body.email, "reason": "bad_password"})
        raise HTTPException(status_code=401,
                            detail={"error": "INVALID_CREDENTIALS"})

    role = user["role"]
    user_id = user["id"]
    name = user["full_name"]

    # W0-F AC-7: the session becomes a server-side record BEFORE the cookie is
    # minted, and the cookie carries only its id. A cookie whose id is not in the
    # store is not a session, however well signed it is.
    record = SESSION_STORE.create(
        user_id=user_id,
        tenant_id=user.get("tenant_id"),
        role=role,
        ttl_seconds=COOKIE_MAX_AGE,
    )
    token = _serializer().dumps(
        {"user_id": user_id, "email": body.email, "role": role,
         "tenant_id": user.get("tenant_id"), "sid": record.session_id}
    )

    _audit("auth.sign_in_success",
           {"user_id": user_id, "email": body.email, "role": role})

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
    invite = _invite_codes.get(body.invite_code)
    if not invite or invite["used_at"] is not None:
        _audit("auth.register_failed",
               {"reason": "invite_invalid_or_used",
                "invite_code": body.invite_code})
        raise HTTPException(status_code=400,
                            detail={"error": "INVALID_INVITE"})

    now = datetime.now(timezone.utc)
    if invite["expires_at"] is not None and invite["expires_at"] <= now:
        _audit("auth.register_failed",
               {"reason": "invite_expired",
                "invite_code": body.invite_code})
        raise HTTPException(status_code=400,
                            detail={"error": "INVITE_EXPIRED"})

    if invite["allowed_role"] != body.role:
        _audit("auth.register_failed",
               {"reason": "role_mismatch",
                "invite_role": invite["allowed_role"],
                "requested_role": body.role})
        raise HTTPException(status_code=400,
                            detail={"error": "ROLE_MISMATCH"})

    if body.email in _users:
        _audit("auth.register_failed",
               {"reason": "email_exists", "email": body.email})
        raise HTTPException(status_code=409,
                            detail={"error": "EMAIL_EXISTS"})

    user_id = f"u-{uuid4().hex[:12]}"
    _users[body.email] = {
        "id": user_id,
        "email": body.email,
        "password_hash": _hash_password(body.password),
        "role": body.role,
        "full_name": body.name,
    }
    invite["used_at"] = now
    invite["assigned_email"] = body.email

    _audit("auth.user_registered",
           {"user_id": user_id, "email": body.email, "role": body.role,
            "invite_code": body.invite_code})

    token = _serializer().dumps(
        {"user_id": user_id, "email": body.email, "role": body.role}
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

    if SESSION_STORE.get_active(sid, tenant_id=payload.get("tenant_id")) is None:
        # Unknown, revoked, expired and cross-tenant are deliberately one answer.
        raise HTTPException(status_code=401, detail={"error": "SESSION_REVOKED_OR_EXPIRED"})

    return payload


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
@router.get("/me")
async def me(request: Request):
    token = request.cookies.get(COOKIE_NAME_SESSION)
    if not token:
        raise HTTPException(status_code=401,
                            detail={"error": "NOT_AUTHENTICATED"})
    try:
        payload = _serializer().loads(token, max_age=COOKIE_MAX_AGE)
    except SignatureExpired:
        raise HTTPException(status_code=401,
                            detail={"error": "SESSION_EXPIRED"})
    except BadSignature:
        raise HTTPException(status_code=401,
                            detail={"error": "INVALID_SESSION"})

    user = _users.get(payload["email"])
    if not user:
        raise HTTPException(status_code=401,
                            detail={"error": "USER_NOT_FOUND"})

    _audit("auth.me_called",
           {"user_id": payload["user_id"], "role": payload["role"]})

    return {
        "user_id": payload["user_id"],
        "email": payload["email"],
        "full_name": user["full_name"],
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
            pass

    _audit("auth.sign_out", {"user_id": user_id})

    resp = JSONResponse(content={"signed_out": True})
    resp.delete_cookie(COOKIE_NAME_SESSION)
    resp.delete_cookie(COOKIE_NAME_ROLE)
    return resp
