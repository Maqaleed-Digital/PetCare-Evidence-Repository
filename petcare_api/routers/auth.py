import os
import hashlib
import logging
from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from pydantic import BaseModel

log = logging.getLogger("petcare.api.auth")

router = APIRouter(prefix="/api/auth", tags=["auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-prod")
COOKIE_NAME_SESSION = "petcare_session"
COOKIE_NAME_ROLE = "petcare_role"
COOKIE_MAX_AGE = 60 * 60 * 8  # 8 hours


def _serializer():
    return URLSafeTimedSerializer(SECRET_KEY)


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ---------------------------------------------------------------------------
# In-memory user + invite-code store (pilot phase — DB wiring deferred)
# ---------------------------------------------------------------------------
_users: dict[str, dict] = {}
_invite_codes: dict[str, dict] = {}


def seed_user(user_id: str, email: str, password: str, role: str,
              full_name: str | None = None):
    """Add a user to the in-memory store. Called at startup."""
    _users[email] = {
        "id": user_id,
        "email": email,
        "password_hash": _hash_password(password),
        "role": role,
        "full_name": full_name or email,
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

    if stored.startswith("$2"):  # bcrypt hash
        try:
            from passlib.hash import bcrypt
            password_ok = bcrypt.verify(body.password, stored)
        except Exception:
            password_ok = False
    else:  # sha256 fallback
        password_ok = (_hash_password(body.password) == stored)

    if not password_ok:
        _audit("auth.sign_in_failed",
               {"email": body.email, "reason": "bad_password"})
        raise HTTPException(status_code=401,
                            detail={"error": "INVALID_CREDENTIALS"})

    role = user["role"]
    user_id = user["id"]
    name = user["full_name"]

    token = _serializer().dumps(
        {"user_id": user_id, "email": body.email, "role": role}
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
