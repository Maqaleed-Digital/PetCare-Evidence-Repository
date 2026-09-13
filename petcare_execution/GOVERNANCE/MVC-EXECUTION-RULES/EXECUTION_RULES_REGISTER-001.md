# MVC-EXECUTION-RULES-REGISTER-001 — the canonical standing-rules register

**Established:** 2026-09-13 · **Status:** ACTIVE
**Governing act for Rules 18–24:** `[SPONSOR]` ruling of 13 September 2026,
*MYVETICARE EXECUTION RULES 18–24*, recorded verbatim in §4 below.

This is the **single canonical register** of MyVetiCare standing execution and
evidence rules. Where any receipt, evidence bundle, request or summary disagrees
with this register about what a rule *is*, this register governs.

It does **not** govern what a rule *was*. See §5.

```
REGISTER_STATUS=ACTIVE
RULES_RATIFIED=18,19,20,21,22,23,24
RULES_DEFINED_BUT_NOT_RATIFIED=13,14,15,16,17
P1_AUTHORIZED=NO
GATE_LIVE_APPLY=NOT_AUTHORIZED
GATE_CREDENTIAL_ENTRY=NOT_AUTHORIZED
```

---

## 1 — Status summary

| Rule | Shorthand key | Status |
|---|---|---|
| 13 | `GREEN_CI_NECESSARY_NOT_SUFFICIENT` | `PROPOSED_NOT_GRANTED` |
| 14 | `LIVE_REGISTER_OUTRANKS_NARRATIVE` | `PROPOSED_NOT_GRANTED` · conflict, §3 |
| 15 | `WRITE_AUTHORITY_PRECEDES_INTEGRITY_CHAIN` | `PROPOSED_NOT_GRANTED` |
| 16 | `CONTROL_DELIVERED_ONLY_WHEN_GOVERNED_PATH_REACHES_IT` | `PROPOSED_NOT_GRANTED` |
| 17 | `PERTURBATION_PROVEN_APPLIED_BEFORE_ADJUDICATION` | `PROPOSED_NOT_GRANTED` · conflict, §3 |
| 18 | `LIVE_RESIDUE_REMEASUREMENT` | **RATIFIED** 2026-09-13 |
| 19 | `FALSE_POSITIVE_INTEGRITY_CONTROLS` | **RATIFIED** 2026-09-13 |
| 20 | `SPONSOR_AUTHORITY` | **RATIFIED** 2026-09-13 |
| 21 | `ABSENCE_OVER_VALIDATION` | **RATIFIED** 2026-09-13 |
| 22 | `REPEATED_PROCESS_FAILURE_BECOMES_A_CONTROL` | **RATIFIED** 2026-09-13 |
| 23 | `GENESIS_CASE` | **RATIFIED** 2026-09-13 |
| 24 | `LAYERED_DEFENCE_PERTURBATION` | **RATIFIED** 2026-09-13 |

**Rules 13–17 are not ratified.** They are drafted below from documented usage,
for Sponsor review. Until a Sponsor act grants them, any adjudication citing
them must record that it rests on ungoverned rules — see §6.

---

## 2 — Rules 13–17 · `PROPOSED / NOT GRANTED`

Drafted from observed usage across receipts and evidence bundles. **No Sponsor
act has granted these.** Rule 20 applies to this section: drafted wording is not
a ruling regardless of how decisively it is phrased, and nothing here is signed
on the Sponsor's behalf.

Each carries the evidence of its own use, so the Sponsor is reviewing a rule the
estate already relies on rather than a proposal in the abstract.

### RULE 13 — GREEN CI IS NECESSARY, NOT SUFFICIENT · `PROPOSED`

> Green CI is a precondition for merge and never, by itself, a demonstration of
> correctness. A verification command that reports success must additionally be
> shown to have evaluated the assertions it is relied upon to evaluate.
>
> Where CI cannot execute a class of verification, that gap must be stated in
> the evidence rather than absorbed into a green result.

*Observed use.* `pytest tests` failed while the combined command CI runs passed,
because conftest scope differs per invocation — green CI would have hidden it.
At `e693e66`, CI reported 882 passed / 7 skipped where local reported 889 / 0;
the 7 are the cross-repository join CI cannot compute.

### RULE 14 — LIVE REGISTER OUTRANKS NARRATIVE · `PROPOSED` · **conflict**

> Where a summary, transcript, receipt or recollection disagrees with the live
> register or the live repository, the live source governs and the narrative is
> corrected.

**Two definitions are in live use.** The Sponsor must select one; §3 records the
evidence. This register carries `LIVE_REGISTER_OUTRANKS_NARRATIVE` as the
*drafted* form because it is the later and broader usage, not because the
question is settled.

### RULE 15 — WRITE AUTHORITY PRECEDES INTEGRITY CHAIN · `PROPOSED`

> Authority to perform a write must be established before any integrity or audit
> record of that write is created.
>
> An integrity record produced before its authority is checked describes an act
> that may not have been permitted, and cannot afterwards be distinguished from
> one that was.

*Observed use.* The genesis procedure takes its lock, proves the authority
unconsumed, and proves no `platform_admin` exists — **then** appends the audit
event.

### RULE 16 — CONTROL DELIVERED ONLY WHEN THE GOVERNED PATH REACHES IT · `PROPOSED`

> A control counts as delivered only when it is exercised through the real
> governed path. A control proven against a double, a fixture, or a substitute
> engine is evidence about the substitute.

*Observed use.* The persistence adapter's controls were re-proven on PostgreSQL
through the real serving path after a prior receipt recorded them as
`IN_MEMORY_ONLY`.

### RULE 17 — PERTURBATION PROVEN APPLIED BEFORE ADJUDICATION · `PROPOSED` · **conflict**

> A perturbation must be proven to have actually changed the artefact before its
> result is adjudicated. An unapplied perturbation produces a passing control and
> no information.

**Two wordings are in live use** (`PERTURBATION_MUST_BE_PROVEN_APPLIED_…` and
`PERTURBATION_PROVEN_APPLIED_…`). The difference is cosmetic in substance but
not to a register keyed on the string. See §3.

**Boundary with ratified Rule 24.** They are complementary, not duplicates:
Rule 17 asks *did the perturbation actually land?*; Rule 24 asks *which layer
actually held the property?* A perturbation can satisfy 17 and still fail 24 —
which is exactly what happened at `P-07a`/`P-08a`.

---

## 3 — Duplicate and conflicting definitions found

Cross-check performed 2026-09-13 across all `.md` and `.py` in the repository.

### Rule 14 — substantive conflict, **Sponsor decision required**

| wording | occurrences | dates |
|---|---|---|
| `LIVE_REGISTER_OUTRANKS_NARRATIVE` | 7 | 2026-09-12 |
| `LIVE_REGISTER_OUTRANKS_TRUNCATED_TRANSCRIPT` | 4 | 2026-09-07 |

Not a paraphrase. *Truncated transcript* is the narrow case — a conversation
record that lost content. *Narrative* covers any summary, including a complete
and confident one, which is the harder and more common failure. The later usage
is the broader form.

`RECOMMENDED=LIVE_REGISTER_OUTRANKS_NARRATIVE`, with the 2026-09-07 form
recorded as a superseded historical variant rather than deleted.
**Not selected here — Rule 20.**

### Rule 17 — wording variance, **Sponsor decision required**

| wording | bundles | latest |
|---|---|---|
| `PERTURBATION_PROVEN_APPLIED_BEFORE_ADJUDICATION` | 3 | `20260912T140000Z` |
| `PERTURBATION_MUST_BE_PROVEN_APPLIED_BEFORE_ADJUDICATION` | 2 | `20260912T100000Z` |

The short form is the later usage.
`RECOMMENDED=PERTURBATION_PROVEN_APPLIED_BEFORE_ADJUDICATION`.
**Not selected here — Rule 20.**

### Rules 18 and 19 — reconciled, no conflict

Receipt shorthand `RULE_18=RESIDUE_REMEASURED_FROM_LIVE_SOURCE` and
`RULE_19=NO_FALSE_TAMPER_FINDING_UNDER_CORRECT_OPERATION` are consistent in
substance with the ratified text. The register carries the ruling's own keys
(`LIVE_RESIDUE_REMEASUREMENT`, `FALSE_POSITIVE_INTEGRITY_CONTROLS`); the receipt
shorthands are recorded here as aliases, and the receipts are not edited.

### Rules 20–24 — no prior definition

Cited by label in earlier receipts with no definition anywhere in the
repository. The ruling in §4 is their first and only definition.

### Rules 1–12

No definition of any rule numbered 1–12 exists in this repository, and none is
cited by any current artefact. Recorded so their absence is a known fact rather
than an unexamined gap.

---

## 4 — The ruling, verbatim

> ```
> [SPONSOR RULING — MYVETICARE EXECUTION RULES 18–24]
>
> I ratify the following as standing execution and evidence rules for MyVetiCare.
>
> RULE 18 — LIVE RESIDUE REMEASUREMENT
> Residue classification must be re-measured from live source at the start of
> every lane. A classification recorded by a prior receipt is evidence of the
> prior state, not proof of the current state.
>
> RULE 19 — FALSE-POSITIVE INTEGRITY CONTROLS
> An integrity mechanism that produces false positives under ordinary operation
> is defective. Integrity controls must distinguish legitimate operation from
> tamper conditions reliably enough that ordinary operation does not train
> operators to disregard genuine alerts.
>
> RULE 20 — SPONSOR AUTHORITY
> Analysis, recommendation, drafted wording, agent output, or implementation does
> not constitute a Sponsor ruling regardless of how decisively it is phrased.
>
> A Sponsor decision becomes authority only through an explicit Sponsor act.
>
> No agent may ratify, approve, authorize, or sign a Sponsor decision on the
> Sponsor's behalf.
>
> RULE 21 — ABSENCE OVER VALIDATION
> Where an input, parameter, capability, or authority is unnecessary, prefer
> removing it from the governed interface rather than accepting and validating
> it.
>
> An absent capability cannot be defaulted, passed incorrectly, relaxed by a
> later validation change, or used as an unintended escalation path.
>
> This rule does not prohibit post-condition or defence-in-depth controls where
> they protect the resulting invariant.
>
> RULE 22 — REPEATED PROCESS FAILURE BECOMES A CONTROL
> When the same material process omission or coverage failure occurs three times,
> it must no longer depend on operator memory or procedural discipline alone.
>
> A durable control must be introduced.
>
> The corrective control must not make the gate self-assembling in a way that
> removes an explicit human decision about what belongs in scope.
>
> RULE 23 — GENESIS CASE
> Every governance model that depends on an already-authorized actor must be
> examined for its genesis case.
>
> Correct steady-state controls must not be assumed to provide authority for the
> first actor.
>
> Where genesis authority is required, it must be explicitly governed before the
> system depends on it.
>
> RULE 24 — LAYERED-DEFENCE PERTURBATION
> A control that remains green after removal of the precondition or defence it is
> claimed to test is unresolved, not automatically proven.
>
> Layered defences must be perturbed independently until the control responsible
> for holding the property is identified.
>
> Perturbation evidence must record the mechanism that actually held the
> property, including ineffective first probes, rather than attributing success
> to a layer that was not load-bearing.
>
> GOVERNANCE
>
> These rules take effect as standing MyVetiCare execution rules from this
> Sponsor ruling.
>
> Prior receipts that cited Rules 18–24 before this ruling remain historical
> records of the execution reasoning used at the time. This ruling does not
> retroactively represent those citations as having possessed Sponsor authority
> when they did not.
>
> No historical receipt, sealed evidence bundle, or provenance record is to be
> silently rewritten to imply otherwise.
>
> This ruling does not itself authorize any production mutation, credential
> entry, production genesis execution, production tenant creation, production
> identity creation, serving binding, or cutover.
>
> P1_AUTHORIZED=NO
> GATE_LIVE_APPLY=NOT_AUTHORIZED
> GATE_CREDENTIAL_ENTRY=NOT_AUTHORIZED
>
> Date: 13 September 2026
> [SPONSOR]
> ```

---

## 5 — Provenance · prospective effect, no retroactive laundering

```
RULES_18_24_EFFECTIVE_FROM=2026-09-13
RETROACTIVE_AUTHORITY=NONE
HISTORICAL_RECEIPTS_REWRITTEN=0
SEALED_BUNDLES_MODIFIED=0
```

Every receipt and evidence bundle that cited Rules 18–24 before 2026-09-13 did
so **without Sponsor authority**, because none existed. Those citations record
the execution reasoning genuinely used at the time, and they remain exactly as
written.

No receipt was edited, no sealed bundle was re-hashed, and no digest was
recomputed to imply those rules were governed when they were not. Establishing
this register creates authority **forward**; it does not reach backwards, and
the earlier documents continue to tell the truth about their own provenance.

The same applies to Rules 13–17, which are cited by current and historical
artefacts and remain ungoverned until a Sponsor act grants them.

---

## 6 — Effect on `REQUEST-002`

`P1_AUTHORIZATION_REQUEST-002.md` adjudicates Rules 13–19 and reports 20–22 as
`UNDERIVED`. After this register:

* Rules **18–24** are governed. The `UNDERIVED` finding for 20–22 is superseded
  and the request's adjudication block is corrected to say so.
* Rules **13–17** remain `PROPOSED / NOT GRANTED`. The request's adjudication of
  them stands as engineering fact but **rests on ungoverned rules**, and the
  request now records that dependency explicitly rather than leaving it implicit.

`EVIDENCE_BASE_SHA` and `PLAN_SHA256` are unchanged by this register — it adds
no code, no migration and no test — so `REQUEST-002` is **amended in place, not
reissued**. A reissue would be required only if the evidence base or the plan
digest moved.

---

## 7 — Open, for a future Sponsor act

```
RULES_13_17_RATIFICATION=PENDING
RULE_14_CANONICAL_WORDING=UNDECIDED   (recommendation in §3)
RULE_17_CANONICAL_WORDING=UNDECIDED   (recommendation in §3)
RULES_1_12=NO_DEFINITION_EXISTS
GITHUB_SUPPORT_REFS_PULL_1_6=NOT_SENT — proposed as a hard cutover condition;
                                        NOT covered by the 13 Sep ruling
```

The cutover condition for `GITHUB_SUPPORT_REFS_PULL_1_6` was discussed alongside
this ruling but does not appear in the ruling text, so it is **not** governed by
it and is recorded here as an open item rather than as a rule.
