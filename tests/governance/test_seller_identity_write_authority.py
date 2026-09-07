"""W0-H — seller/taxpayer identity write authority, checked structurally.

Annex K §K.2, `REQ-FIN-S1..S3`:

> **S1** Seller/taxpayer identity is an attribute of the transaction record, set
>        at creation from the clinic's own registration record, and immutable
>        thereafter.
> **S2** No payment, settlement, marketplace, or fee-collection component holds
>        write authority over the seller-identity field. **This is enforced
>        structurally, not by convention or code review.**
> **S3** Payment routing, fund flow, and the identity of whichever party receives
>        funds first must never determine or alter seller/taxpayer identity.

> **ACCEPTANCE.** A build in which any payment-layer component can write the
> seller-identity field FAILS. The test is a **static write-authority check**,
> not a runtime assertion.

That wording is the whole design of this file. A runtime assert only fires on
paths that execute; a component retains write *authority* whether or not any
test happens to exercise it. So the property is checked over the source itself.

The same reasoning covers gross-not-net (`REQ-FIN-G1..G3`): the acceptance
criterion is that **no write path exists** that reduces a stored gross value —
again a statement about the code, not about a run.

`CURRENT_STATE` in CP-2 is ABSENT: the fields do not exist yet. These guards are
therefore armed *ahead* of the schema, so the first component that acquires write
authority fails the build rather than acquiring it quietly.
"""
import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

#: Components that must NEVER hold write authority over seller identity.
#: Payment, settlement, marketplace and fee collection — Annex K §K.2 names all four.
PAYMENT_LAYER = [
    "petcare_runtime/src/petcare/payment_activation",
    "petcare_runtime/src/petcare/financial_execution",
    "petcare_runtime/src/petcare/financial_operations",
    "petcare_runtime/src/petcare/partner_network",
]

#: Every spelling the seller-identity attribute may take.
SELLER_FIELDS = {
    "seller_id",
    "seller_identity",
    "seller_identity_id",
    "seller_taxpayer_id",
    "seller_registration_id",
    "taxpayer_id",
}

#: Gross consideration — an immutable commercial fact (REQ-FIN-G1).
GROSS_FIELDS = {"gross_value", "gross_amount", "gross_consideration"}

_WRITER_CALL = re.compile(r"^(create|update|set|write|save|insert|upsert|put|patch)", re.I)
_SQL_SELLER_WRITE = re.compile(
    r"(UPDATE|INSERT\s+INTO)\b[\s\S]{0,400}?\b(" + "|".join(sorted(SELLER_FIELDS)) + r")\b",
    re.I,
)
_SQL_GROSS_REDUCE = re.compile(
    r"SET\b[\s\S]{0,200}?\b(" + "|".join(sorted(GROSS_FIELDS)) + r")\s*=\s*[^,;]*[-]",
    re.I,
)


def _payment_layer_files() -> list[Path]:
    files: list[Path] = []
    for tree in PAYMENT_LAYER:
        base = ROOT / tree
        if base.exists():
            files.extend(p for p in base.rglob("*.py") if "__pycache__" not in str(p))
    return files


def _target_names(node: ast.AST) -> set[str]:
    """Field names a statement writes to."""
    names: set[str] = set()
    targets = []
    if isinstance(node, ast.Assign):
        targets = node.targets
    elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
        targets = [node.target]
    for t in targets:
        if isinstance(t, ast.Attribute):
            names.add(t.attr)
        elif isinstance(t, ast.Subscript):
            key = t.slice
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                names.add(key.value)
        elif isinstance(t, ast.Name):
            names.add(t.id)
    return names


def test_payment_layer_is_not_empty():
    """Without this, every absence assertion below would pass vacuously — which
    is exactly how a structural check quietly stops checking anything."""
    files = _payment_layer_files()
    assert len(files) > 20, f"payment-layer scan collapsed to {len(files)} files"


def test_t_sell_02_no_payment_layer_component_assigns_seller_identity():
    """T-SELL-02 (ARMED) — REQ-FIN-S2 as a structural property.

    Direct assignment: `order.seller_id = ...` or `row["taxpayer_id"] = ...`
    anywhere in the payment layer is write authority, whether or not it runs.
    """
    offenders = []
    for f in _payment_layer_files():
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                hit = _target_names(node) & SELLER_FIELDS
                if hit:
                    offenders.append(f"{f.relative_to(ROOT)}:{node.lineno} -> {sorted(hit)}")
    assert offenders == [], (
        "payment-layer component holds write authority over seller identity "
        f"(REQ-FIN-S2): {offenders}"
    )


def test_t_sell_03_no_payment_layer_component_passes_seller_identity_to_a_writer():
    """T-SELL-03 (ARMED) — the indirect route.

    Assignment is not the only way to hold write authority. Passing the field
    into a create/update/save call writes it just as effectively, and would slip
    past a check that only looked at assignment statements.
    """
    offenders = []
    for f in _payment_layer_files():
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
            if not name or not _WRITER_CALL.match(name):
                continue
            for kw in node.keywords:
                if kw.arg in SELLER_FIELDS:
                    offenders.append(f"{f.relative_to(ROOT)}:{node.lineno} -> {name}({kw.arg}=…)")
    assert offenders == [], (
        f"payment-layer component writes seller identity via a writer call: {offenders}"
    )


def test_t_sell_04_no_payment_layer_sql_writes_seller_identity():
    """T-SELL-04 — the SQL route. An UPDATE or INSERT naming the field is write
    authority regardless of what the Python around it looks like."""
    offenders = []
    for f in _payment_layer_files():
        text = f.read_text(encoding="utf-8")
        m = _SQL_SELLER_WRITE.search(text)
        if m:
            offenders.append(f"{f.relative_to(ROOT)} -> {m.group(0)[:60]!r}")
    assert offenders == [], f"payment-layer SQL writes seller identity: {offenders}"


def test_req_fin_g_no_write_path_reduces_a_stored_gross_value():
    """REQ-FIN-G1..G3 — gross is an immutable commercial fact.

    Deductions are SEPARATE movements referencing the gross sale; net settlement
    is DERIVED and never stored as authoritative. So a path that subtracts from a
    stored gross value is the defect, in Python or in SQL.
    """
    offenders = []
    for f in _payment_layer_files():
        text = f.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            tree = None
        if tree is not None:
            for node in ast.walk(tree):
                if isinstance(node, ast.AugAssign) and isinstance(node.op, ast.Sub):
                    if _target_names(node) & GROSS_FIELDS:
                        offenders.append(f"{f.relative_to(ROOT)}:{node.lineno} -> gross -= …")
        m = _SQL_GROSS_REDUCE.search(text)
        if m:
            offenders.append(f"{f.relative_to(ROOT)} -> {m.group(0)[:60]!r}")
    assert offenders == [], f"a write path reduces a stored gross value: {offenders}"


# ---------------------------------------------------------------------------
# Schema-side invariants — REQ-FIN-G3 and REQ-FIN-S1
# ---------------------------------------------------------------------------
MIGRATIONS = sorted((ROOT / "petcare_runtime/migrations").glob("*.sql"))

#: A stored, authoritative net value. `net_settlement_amount`, `net_value`,
#: `amount_net` — any of these is the same defect under a different name.
_STORED_NET = re.compile(
    r"^\s*(?!--)[\s\S]*?\b(net_value|net_amount|net_settlement_value|"
    r"net_settlement_amount|amount_net|value_net)\b\s+(TEXT|NUMERIC|DECIMAL|INTEGER|REAL)",
    re.I | re.M,
)


def test_migrations_are_scannable():
    assert len(MIGRATIONS) > 25, f"migration scan collapsed to {len(MIGRATIONS)}"


def test_req_fin_g3_net_settlement_is_never_stored_as_a_column():
    """REQ-FIN-G3 — net settlement is DERIVED, never stored as authoritative.

    Gross less referenced deductions is a computation. The moment it becomes a
    column, it becomes a second source of truth that can disagree with the
    movements it was derived from — and the disagreement is invisible, because
    both look like facts.
    """
    offenders = []
    for m in MIGRATIONS:
        hit = _STORED_NET.search(m.read_text(encoding="utf-8"))
        if hit:
            offenders.append(f"{m.name} -> {hit.group(1)}")
    assert offenders == [], (
        f"net settlement stored as an authoritative column (REQ-FIN-G3): {offenders}"
    )
