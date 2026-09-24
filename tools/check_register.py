#!/usr/bin/env python3
"""
MVC-BUILD-W1 status checker: asserts ENGINEERING status for every FR in the spine.

Inputs (repository root):
  requirements/register.yaml       the generated spine (tools/gen_register.py)
  requirements/bindings.json       evidence-cited bindings, one entry per FR
  requirements/served_routes.json  routes of the SERVED app (tools/list_served_routes.py)

Output: requirements/status.json on stdout, deterministic (no clock, no host facts).

  python3 tools/check_register.py > requirements/status.json

ENGINEERING STATES, derived in this order:
  ABSENT              no implementing symbol bound
  BINDING_BROKEN      a bound symbol fails resolution, or a bound test is not collected
  BUILT_UNWIRED       symbols resolve, but no route is bound or a bound route is not served
  REACHABLE_UNTESTED  every bound route is served, no test is bound
  REACHABLE_TESTED    every bound route is served and every bound test is collected

REACHABLE_TESTED is engineering evidence only. It is NOT requirement completion:
every FR carries acceptance_state CRITERIA_NOT_RATIFIED, and this checker has no
code path that emits anything else. Acceptance criteria are not ratified, and
nothing measured here can stand in for them.

Symbol forms:
  <python.module>:<qualname>        imported; the qualname is resolved attribute by attribute
  <repo/relative/file>#<Name>       a non-Python declaration; the file must declare Name

Exit status: 0 emitted; 2 the inputs are malformed (unknown FR id, missing entry,
bad schema, fitness value outside its enum). Malformed input is never emitted as
a status, because a status computed from a document that failed validation would
look exactly like a measurement.
"""
import hashlib
import importlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "requirements" / "register.yaml"
BINDINGS = ROOT / "requirements" / "bindings.json"
SERVED = ROOT / "requirements" / "served_routes.json"

ABSENT = "ABSENT"
BINDING_BROKEN = "BINDING_BROKEN"
BUILT_UNWIRED = "BUILT_UNWIRED"
REACHABLE_UNTESTED = "REACHABLE_UNTESTED"
REACHABLE_TESTED = "REACHABLE_TESTED"
ENGINEERING_STATES = (ABSENT, BINDING_BROKEN, BUILT_UNWIRED, REACHABLE_UNTESTED, REACHABLE_TESTED)

#: The only acceptance state this checker can emit. There is deliberately no
#: parameter, input field or branch that changes it.
ACCEPTANCE_STATE = "CRITERIA_NOT_RATIFIED"

KNOWN_LIMIT = "REACHABLE_TESTED does not prove bound tests exercise the served app"

FITNESS_ENUMS = {
    "storage": ("PERSISTENT_POSTGRES", "IN_MEMORY", "FILE", "NONE", "UNKNOWN"),
    "tenant_source": ("SESSION", "CLIENT_SUPPLIED", "NONE", "UNKNOWN"),
    "audit_actor_source": ("SESSION", "CLIENT_SUPPLIED", "NONE", "UNKNOWN"),
}
LIST_FIELDS = ("implements", "routes", "tests", "legacy", "basis")
ENTRY_FIELDS = set(LIST_FIELDS) | {"unresolved", "fitness"}
FITNESS_FIELDS = set(FITNESS_ENUMS) | {"ui_surface", "basis"}

FR_ENTRY = re.compile(
    r'^  - id: (FR-\d{2})\n    title: "(.*)"\n    priority: (\w+)\n    phase: (\d)\n', re.M)
ROUTE = re.compile(r"^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS) (/\S*)$")

# TEST/LOCAL configuration only: the values the repository-root conftest.py
# uses. Set unconditionally, so that a shell configured for a deployed store can
# never make a measurement reach it.
_NONPROD_ENV = {
    "SECRET_KEY": "test-only-not-a-deployed-secret",
    "PETCARE_SECRET_MODE": "environment",
    "PETCARE_PERSISTENCE_MODE": "memory",
    "PETCARE_DOCUMENT_STORE_MODE": "local",
    "PETCARE_DOCUMENT_ROOT": str(Path(tempfile.gettempdir()) / "petcare-test-documents"),
}


class InputError(Exception):
    pass


def _nonprod_env() -> dict:
    env = dict(os.environ)
    env.update(_NONPROD_ENV)
    return env


def parse_register() -> list:
    text = REGISTER.read_text(encoding="utf-8")
    rows = [{"id": m.group(1), "title": m.group(2), "priority": m.group(3), "phase": int(m.group(4))}
            for m in FR_ENTRY.finditer(text)]
    if not rows:
        raise InputError("register.yaml yields no FR entries")
    return rows


def _no_duplicate_keys(pairs):
    keys = [k for k, _ in pairs]
    dupes = sorted({k for k in keys if keys.count(k) > 1})
    if dupes:
        raise InputError(f"duplicate keys in bindings.json: {dupes}")
    return dict(pairs)


def load_bindings(fr_ids: list) -> dict:
    data = json.loads(BINDINGS.read_text(encoding="utf-8"), object_pairs_hook=_no_duplicate_keys)
    unknown = sorted(set(data) - set(fr_ids))
    if unknown:
        raise InputError(f"bindings.json names FR ids absent from the register: {unknown}")
    missing = sorted(set(fr_ids) - set(data))
    if missing:
        raise InputError(f"bindings.json has no entry for: {missing}")
    for fr, entry in data.items():
        if not isinstance(entry, dict) or set(entry) != ENTRY_FIELDS:
            raise InputError(f"{fr}: fields must be exactly {sorted(ENTRY_FIELDS)}")
        for f in LIST_FIELDS:
            if not isinstance(entry[f], list) or not all(isinstance(x, str) and x for x in entry[f]):
                raise InputError(f"{fr}.{f} must be a list of non-empty strings")
        if not isinstance(entry["unresolved"], str):
            raise InputError(f"{fr}.unresolved must be a string")
        if entry["implements"] and not entry["basis"]:
            raise InputError(f"{fr}: a positive binding requires file:line basis")
        for r in entry["routes"]:
            if not ROUTE.match(r):
                raise InputError(f"{fr}: route {r!r} is not '<METHOD> <path>'")
        fit = entry["fitness"]
        if not isinstance(fit, dict) or set(fit) != FITNESS_FIELDS:
            raise InputError(f"{fr}.fitness fields must be exactly {sorted(FITNESS_FIELDS)}")
        for f, allowed in FITNESS_ENUMS.items():
            if fit[f] not in allowed:
                raise InputError(f"{fr}.fitness.{f}={fit[f]!r} is not one of {list(allowed)}")
        for f in ("ui_surface", "basis"):
            if not isinstance(fit[f], list) or not all(isinstance(x, str) and x for x in fit[f]):
                raise InputError(f"{fr}.fitness.{f} must be a list of non-empty strings")
        if not entry["implements"]:
            if (fit["storage"], fit["tenant_source"], fit["audit_actor_source"]) != ("NONE",) * 3 \
                    or fit["ui_surface"]:
                raise InputError(f"{fr}: no implementation bound, so fitness must be NONE with no UI")
    return data


def load_served() -> tuple:
    data = json.loads(SERVED.read_text(encoding="utf-8"))
    served = {f"{m} {r['path']}" for r in data["routes"] for m in r["methods"]}
    return data["app"], served, len(data["routes"])


def _prepare_imports() -> None:
    os.environ.update(_NONPROD_ENV)
    for p in (ROOT, ROOT / "petcare_runtime" / "src", ROOT / "petcare_api"):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))


def resolve(symbol: str):
    """None if the symbol resolves, otherwise the reason it does not."""
    if "#" in symbol:
        rel, name = symbol.split("#", 1)
        path = ROOT / rel
        if not path.is_file():
            return f"{symbol}: file not found"
        decl = re.compile(
            rf"^\s*export\s+(?:default\s+)?(?:async\s+)?(?:function|const|let|class|type|interface)\s+{re.escape(name)}\b",
            re.M)
        return None if decl.search(path.read_text(encoding="utf-8")) else f"{symbol}: no declaration"
    if ":" not in symbol:
        return f"{symbol}: not '<module>:<qualname>' or '<file>#<Name>'"
    mod, qual = symbol.split(":", 1)
    try:
        obj = importlib.import_module(mod)
    except Exception as exc:  # noqa: BLE001 — any import failure is a broken binding
        return f"{symbol}: import failed ({type(exc).__name__})"
    for part in qual.split("."):
        if not hasattr(obj, part):
            return f"{symbol}: attribute {part!r} not found"
        obj = getattr(obj, part)
    return None


def collected_tests(test_ids: list) -> set:
    """The bound test ids pytest actually collects."""
    present = sorted({t for t in test_ids if (ROOT / t.split("::", 1)[0]).exists()})
    if not present:
        return set()
    out = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider",
         "--continue-on-collection-errors", *present],
        cwd=ROOT, env=_nonprod_env(), capture_output=True, text=True).stdout
    nodes = {ln.strip() for ln in out.splitlines() if "::" in ln}
    return {t for t in present if any(n == t or n.startswith(t + "::") for n in nodes)}


def derive(entry: dict, served: set, collected: set) -> tuple:
    if not entry["implements"]:
        return ABSENT, ["no implementing symbol bound"]
    reasons = [r for r in (resolve(s) for s in entry["implements"]) if r]
    reasons += [f"{t}: bound test not collected" for t in entry["tests"] if t not in collected]
    if reasons:
        return BINDING_BROKEN, reasons
    if not entry["routes"]:
        return BUILT_UNWIRED, ["no served route bound"]
    unserved = [r for r in entry["routes"] if r not in served]
    if unserved:
        return BUILT_UNWIRED, [f"{r}: not served" for r in unserved]
    if not entry["tests"]:
        return REACHABLE_UNTESTED, ["all bound routes served; no test bound"]
    return REACHABLE_TESTED, ["all bound routes served; all bound tests collected"]


def _summary(rows: list) -> dict:
    counts = {s: 0 for s in ENGINEERING_STATES}
    for r in rows:
        counts[r["status"]] += 1
    return {"total": len(rows), "counts": counts,
            "ids": {s: [r["id"] for r in rows if r["status"] == s] for s in ENGINEERING_STATES}}


def main() -> int:
    try:
        spine = parse_register()
        bindings = load_bindings([r["id"] for r in spine])
        app, served, route_count = load_served()
    except (InputError, OSError, ValueError, KeyError) as exc:
        print(f"check_register: {exc}", file=sys.stderr)
        return 2
    _prepare_imports()
    collected = collected_tests([t for e in bindings.values() for t in e["tests"]])

    rows = []
    for fr in spine:
        entry = bindings[fr["id"]]
        status, reasons = derive(entry, served, collected)
        assert status in ENGINEERING_STATES, status
        rows.append({
            "id": fr["id"],
            "title": fr["title"],
            "priority": fr["priority"],
            "phase": fr["phase"],
            "status": status,
            "reasons": reasons,
            "acceptance_state": ACCEPTANCE_STATE,
            "unresolved": entry["unresolved"],
            "counts": {"implements": len(entry["implements"]), "routes": len(entry["routes"]),
                       "tests": len(entry["tests"]), "legacy": len(entry["legacy"]),
                       "basis": len(entry["basis"]), "ui_surface": len(entry["fitness"]["ui_surface"])},
            "fitness": {k: entry["fitness"][k] for k in ("storage", "tenant_source", "audit_actor_source",
                                                         "ui_surface")},
        })

    high = set(re.search(r"^  phase1_high_ids: \[(.*)\]$", REGISTER.read_text(encoding="utf-8"),
                         re.M).group(1).replace(" ", "").split(","))
    doc = {
        "lane": "MVC-BUILD-W1",
        "known_limit": KNOWN_LIMIT,
        "acceptance_note": ("Engineering status only. acceptance_state is CRITERIA_NOT_RATIFIED for every "
                            "requirement; no requirement is ACCEPTED or CLIENT_ACCEPTED."),
        "inputs": {
            "register_sha256": hashlib.sha256(REGISTER.read_bytes()).hexdigest(),
            "served_app": app,
            "served_route_count": route_count,
        },
        "requirements": rows,
        "summary": {
            "all": _summary(rows),
            "phase1": _summary([r for r in rows if r["phase"] == 1]),
            "phase1_high": _summary([r for r in rows if r["id"] in high]),
            "phase2": _summary([r for r in rows if r["phase"] == 2]),
            "phase3": _summary([r for r in rows if r["phase"] == 3]),
        },
    }
    print(json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
