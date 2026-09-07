# W0-I perturbation — four controls, four separate violations

Each §28 control was defeated in turn by a single change to the implementation,
and had to be caught by its own test.

| # | Violation | Control that fired | Restored |
|---|---|---|---|
| P1 | time-bounding removed from `held_at` (authority becomes "always") | `T-PROF-01` | clean |
| P2 | `actor_id` added to `DeviceSealingAuthority` | `T-PROF-02` | clean |
| P3 | audit record removed from the bootstrap (made silent) | `T-PROF-03` | clean |
| P4 | `professional_class_at` returns a default instead of `None` | `T-PROF-04` | clean |

Each probe failed **exactly one** control — the one that owns that property.

P2 is the one worth dwelling on. It does not add a derivation; it merely adds a
field. The control fails anyway, because §28's separation is enforced by the
*shape* of the type rather than by a rule about its use. Making the conflation
representable is itself the defect, since a field that exists will eventually be
read.

P4 is the quiet one. Defaulting an unknown professional class to `VETERINARIAN`
breaks no positive test — every authorised vet still works — and grants clinical
authority to every identity with no grant at all. Only the negative control
catches it.

## Schema-side verification

The migration's CHECK constraints were exercised directly against SQLite:

| Insert | Expected | Result |
|---|---|---|
| no principal, not marked as bootstrap | REJECT | **rejected** by CHECK |
| no principal, marked as bootstrap | ACCEPT | accepted |
| principal present, ordinary grant | ACCEPT | accepted |
| `revoked_at` before `effective_from` | REJECT | **rejected** by CHECK |

The first row is the silent exception §28 forbids; it cannot be stored.

Baseline and restored: 9 passed.

```
PERTURBATION_GUARDS_PROVEN=4 implementation + 4 schema CHECK cases
WORKTREE_RESTORED=YES — no perturbation committed
```
