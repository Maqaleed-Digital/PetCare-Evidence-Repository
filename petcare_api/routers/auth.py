import os
import hashlib
import logging
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
# In-memory user store (pilot phase — DB wiring deferred)
# ---------------------------------------------------------------------------
_users: dict[str, dict] = {}


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


def _audit(event_name: str, detail: dict):
    """Lightweight audit log — matches main.py pattern."""
    log.info("AUDIT %s %s", event_name, detail)


# ---------------------------------------------------------------------------
class SignInRequest(BaseModel):
    email: str
    password: str


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
