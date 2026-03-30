import os
import sys
from typing import Optional

MARK_START = "# PH8_API_HARDENING_START"
MARK_END = "# PH8_API_HARDENING_END"

INJECT_BLOCK = f"""{MARK_START}
try:
    from fnd.security.auth_stub import evaluate_request_auth, extract_headers_from_flask_request
except Exception:
    evaluate_request_auth = None
    extract_headers_from_flask_request = None

if 'app' in globals():
    try:
        from flask import request
        @app.before_request
        def _ph8_before_request_auth_stub():
            if evaluate_request_auth is None or extract_headers_from_flask_request is None:
                return None
            headers = extract_headers_from_flask_request(request)
            decision = evaluate_request_auth(
                headers=headers,
                require_auth_token=False,
                expected_token=None,
            )
            if not decision.ok:
                return ({{"ok": False, "reason": decision.reason}}, decision.status_code)
            return None
    except Exception:
        pass
{MARK_END}
"""

def find_app_py(root: str) -> Optional[str]:
    candidates = [
        os.path.join(root, "app.py"),
        os.path.join(root, "src", "app.py"),
        os.path.join(root, "app", "app.py"),
    ]
    for p in candidates:
        if os.path.exists(p) and os.path.isfile(p):
            return p
    return None

def is_flask_app(text: str) -> bool:
    t = text.lower()
    return ("from flask import" in t or "import flask" in t) and "flask(" in t

def already_injected(text: str) -> bool:
    return MARK_START in text and MARK_END in text

def inject_into_file(path: str) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    if already_injected(text):
        print(f"OK: already injected: {path}")
        return True

    if not is_flask_app(text):
        print(f"SKIP: not detected as Flask app: {path}")
        return False

    new_text = text.rstrip() + "\n\n" + INJECT_BLOCK + "\n"
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(new_text)
    os.replace(tmp, path)
    print(f"INJECTED: {path}")
    return True

def main() -> int:
    root = os.getcwd()
    app_py = find_app_py(root)
    if not app_py:
        print("SKIP: app.py not found in known locations")
        return 0
    inject_into_file(app_py)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
