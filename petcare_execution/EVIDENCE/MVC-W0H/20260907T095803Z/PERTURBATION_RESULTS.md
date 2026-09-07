# W0-H perturbation — five classes, each armed separately

A static check that has never failed is indistinguishable from one that scans
nothing. Each write route was opened in turn, in a real payment-layer module
(`financial_execution/payouts.py`), and had to be caught by its own guard.

| # | Violation | Guard that fired | Restored |
|---|---|---|---|
| P1 | `order.seller_id = "maqaleed"` | `test_t_sell_02` — direct assignment | clean |
| P2 | `repo.update_record(seller_taxpayer_id=…)` | `test_t_sell_03` — writer call | clean |
| P3 | `"UPDATE partner_orders SET seller_id = ? …"` | `test_t_sell_04` — SQL | clean |
| P4 | `rec.gross_value -= rec.platform_fee` | `test_req_fin_g_no_write_path_reduces…` | clean |
| P5 | `ALTER TABLE … ADD COLUMN net_value …` | `test_req_fin_g3_net_settlement_is_never_stored…` | clean |

Each probe failed **exactly one** guard — the one that owns that route. That is
the useful signal: it shows the guards are independent rather than one broad
matcher reported five times.

P2 is the probe that justifies the AST work. Write authority does not require an
assignment statement; passing the field into a `create`/`update`/`save` call
writes it just as effectively, and a check built only on assignment targets would
have passed while the defect was present.

P5 is the schema counterpart. The structural guards watch code paths; a stored
`net_value` column needs no code path to be wrong.

Baseline and restored: 7 passed. Worktree verified clean after every probe.

```
PERTURBATION_GUARDS_PROVEN=5
WORKTREE_RESTORED=YES — no perturbation committed
```
