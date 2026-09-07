# F4 — W0-F pack count correction, appended not edited

The W0-F handoff pack carries relayed counts and says so itself
(`DENOMINATOR_STATUS=RELAYED_NOT_REMEASURED`). Four figures have moved.

| Figure | Recorded | Measured 2026-09-07 | Why |
|---|---|---|---|
| `petcare_api` tests | 46 | **51** | estate growth, chiefly W0-A2 |
| vitest | 85 | **120** | estate growth across PORT-01..10 |
| Playwright | 90 | **90** | unchanged |
| `partner_network` modules | 37 | **36** | original count included `__pycache__` |
| W0-A perturbation failures | 3 | **4** | W0-A2 added an AST ordering check |

**These are not corrections of error.** Three moved because the estate grew after
the pack was written; the W0-A count moved because W0-A2 deliberately added guard
coverage. Only `partner_network` was inaccurate when written, by one, from
counting a directory listing rather than modules. No claim is made that the
earlier measurements were invalid at their time, because no primary evidence
shows that.

The correction is **append-only**. Nothing above the appended section in
`MVC-W0F-ENGINEERING-HANDOFF-001.md` was altered.

```
W0F_COUNT_CORRECTION_APPENDED=YES
```
