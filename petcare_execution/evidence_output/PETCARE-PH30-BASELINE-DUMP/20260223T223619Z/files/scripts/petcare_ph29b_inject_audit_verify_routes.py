from __future__ import annotations

import sys
from pathlib import Path


MARKER_START = "    BEGIN_PETCARE_PH29B_AUDIT_VERIFY_ROUTES"
MARKER_END = "    END_PETCARE_PH29B_AUDIT_VERIFY_ROUTES"


INJECT_BLOCK = "\n".join(
    [
        "",
        MARKER_START,
        "    try:",
        "        from FND.CODE_SCAFFOLD.api.routes_audit_verify import register_audit_verify_routes",
        "",
        "        register_audit_verify_routes(app)",
        "    except Exception:",
        "        pass",
        MARKER_END,
        "",
    ]
)


def inject_into_create_app(app_py: Path) -> None:
    raw = app_py.read_text(encoding="utf-8")

    if MARKER_START in raw and MARKER_END in raw:
        return

    needle = "\n    return app"
    idx = raw.find(needle)
    if idx == -1:
        raise RuntimeError("Could not find 'return app' in create_app() to inject PH29-B block safely.")

    updated = raw[:idx] + INJECT_BLOCK + raw[idx:]
    app_py.write_text(updated, encoding="utf-8")


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    app_py = repo / "FND" / "CODE_SCAFFOLD" / "app.py"
    if not app_py.exists():
        raise RuntimeError(f"Missing runtime app.py at: {app_py}")

    inject_into_create_app(app_py)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
