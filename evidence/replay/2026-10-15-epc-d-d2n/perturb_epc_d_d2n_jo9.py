"""MVC-EPC-D-001 D2n perturbations: J-O9 internal tracking (derived from records only; no carrier).
python3 perturb_epc_d_d2n_jo9.py <root>. ARMED = the named test FAILS."""
import subprocess
import sys
R = sys.argv[1].rstrip("/") + "/"
T = "petcare_api/tests/test_epc_d2n_jo9_internal_tracking.py::"
PG = "petcare_api/tests/test_epc_d2n_jo9_tracking_postgres.py"
PY = lambda t: ["python3", "-m", "pytest", t, "-q", "-p", "no:cacheprovider"]
VT = lambda t: ["npx", "vitest", "run", t]
O, PAGE = "petcare_api/orders.py", "petcare_web/app/owner/orders/page.tsx"
P = [
 ("P-D2N-JO9-CARRIER-INVENTED", [(O, '            "carrier": None}', '            "carrier": {"status": "IN_TRANSIT"}}')],
  PY(T + "test_a_new_order_is_tracked_as_placed_only_and_claims_no_carrier")),
 ("P-D2N-JO9-REFUSAL-COUNTS-AS-ROUTE", [(O, "    routed = decision is not None and bool(decision.chosen_location_id)\n", "    routed = decision is not None\n")],
  PY(PG)),
 ("P-D2N-JO9-DELIVERED-TIME-INVENTED", [(O, '"DELIVERED": collection.confirmed_at if collection else None', '"DELIVERED": order.created_at if collection else None')],
  PY(T + "test_the_full_internal_lifecycle_placed_routed_delivered_receipt_in_order")),
 ("P-D2N-JO9-RECEIPT-NOT-FROM-RECORD", [(O, '"RECEIPT_ISSUED": receipt.issued_at if receipt else None', '"RECEIPT_ISSUED": collection.confirmed_at if receipt else None')],
  # run 1 targeted the served-app lifecycle test and was VACUOUS: there the collection and the receipt share one instant, so the
  # swap is invisible. The PostgreSQL test stores distinct times and is the test that can detect it (run1.out.txt keeps run 1).
  PY(PG)),
 ("P-D2N-JO9-DELIVERED-BEFORE-COLLECTION", [(O, '"DELIVERED": collection.confirmed_at if collection else None', '"DELIVERED": order.created_at')],
  PY(T + "test_a_refused_delivery_moves_no_step")),
 ("P-D2N-JO9-ROUTED-WITHOUT-DECISION", [(O, '"ROUTED": decision.decided_at if routed else None', '"ROUTED": order.created_at')],
  PY(T + "test_with_the_served_maps_adapter_routing_fails_closed_and_routed_stays_not_done")),
 ("P-D2N-JO9-UI-NO-CARRIER-NOTICE-DROPPED", [(PAGE, "              <p className=\"muted\" data-testid=\"tracking-no-carrier\">{t('noCarrier')}</p>\n", "")],
  VT("__tests__/jo9-order-tracking.test.tsx")),
 ("P-D2N-JO9-UI-ALL-STEPS-DONE", [(PAGE, "data-done={s.done ? 'true' : 'false'}>", "data-done=\"true\">")],
  VT("__tests__/jo9-order-tracking.test.tsx")),
]
res = []
for pid, edits, cmd in P:
    files = sorted({f for f, _, _ in edits})
    orig = {f: open(R + f, 'rb').read() for f in files}
    try:
        for f, old, new in edits:
            s = open(R + f).read(); assert s.count(old) == 1, (pid, f, s.count(old)); open(R + f, 'w').write(s.replace(old, new))
        rc = subprocess.run(cmd, cwd=R + ("petcare_web" if cmd[0] == "npx" else ""), capture_output=True, text=True, timeout=1800)
        out = [l for l in (rc.stdout + rc.stderr).splitlines() if "passed" in l or "failed" in l][-1:]
    finally:
        for f, b in orig.items(): open(R + f, 'wb').write(b)
    for f, b in orig.items(): assert open(R + f, 'rb').read() == b
    res.append((pid, "ARMED" if rc.returncode != 0 else "VACUOUS")); print(pid, res[-1][1], out, flush=True)
print("ARMED=%d VACUOUS=%d" % (sum(r[1] == "ARMED" for r in res), sum(r[1] == "VACUOUS" for r in res)))
