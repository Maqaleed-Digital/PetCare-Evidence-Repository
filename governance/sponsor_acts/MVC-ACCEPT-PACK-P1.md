[SPONSOR]
DECISION=MVC-ACCEPT-PACK-P1
DATE=2026-09-24
PACK_VERSION=1.1
PACK_PR=43
PACK_HEAD=2c7f48ee00d9f56fa11fa602f44430714187543d

RESULT=RATIFY_ALL_WITH_INTERPRETATIONS
LOCK=YES

DENOMINATOR=16_PHASE1_HIGH_FRS
CRITERIA=68
PHASE1_RELEVANT_NFR=13

INTERPRETATIONS:

I-01 AC-FR-01-04=ACCEPT
"Pharmacist" in BRD FR-01 is satisfied through class-scoped pharmacy
authority under MVC-PHARM-001. No general-purpose pharmacy role is created.

I-02 AC-FR-02-04=ACCEPT
Current failure on POST /api/pets is implementation debt and MUST be
remediated against this criterion. It does not weaken the criterion.

I-03 AC-FR-04-01=ACCEPT_WITH_CLARIFICATION
Purchaser identity/KYC verification and veterinarian prescribing authority
are separate controls. KYC binds the purchaser where legally required;
practitioner authority is independently verified.

I-04 AC-FR-04-04=ACCEPT
KYC provider selection remains an external implementation dependency.

I-05 AC-FR-05-01=ACCEPT_WITH_CLARIFICATION
Veterinarian licensing verification targets MEWA/the competent KSA
veterinary licensing authority. Exact live verification mechanism remains
an external integration dependency.

I-06 AC-FR-06-05=ACCEPT
Remote veterinary consultation remains fail-closed pending the recorded
KSA regulatory/counsel determination.

I-07 AC-FR-07-02=ACCEPT_WITH_LIMIT
REQ-MVC-8.67 is authoritative only for notification-delivery evidence
within this criterion; it does not define the chat capability itself.

I-08 AC-FR-13-01=ACCEPT_WITH_THRESHOLD
REAL_TIME_BOUND=5_SECONDS
A committed stock change becomes visible to another authorised session of
the same tenant with p95 <= 5 seconds, measured over at least 100 events
in the acceptance environment.

I-09 AC-FR-14-06=ACCEPT
SFDA integration remains adapter/contract-testable before live API access.
Absence of external API access does not permit fabricated integration proof.

I-10 AC-FR-15-01=ACCEPT_WITH_CLARIFICATION
OPTIMAL_ROUTING_RULE:
  1. pharmacy is eligible/licensed for the applicable supply class;
  2. pharmacy can fulfil the complete basket;
  3. choose lowest route ETA;
  4. tie-break by route distance;
  5. final deterministic tie-break by stable pharmacy identifier.
Until establishment licence requirements are defined (MVC-PHARM-001 §6c),
step 1 is evidenced with test fixtures; no pharmacy is live-eligible.
External maps availability remains separately evidenced.

I-11 AC-FR-16-03=ACCEPT
FR-16 remains Phase-1 scope under BRD v1.0. V3.0's proposed rejection
has no force under AA-2.

I-12 AC-FR-20-02=ACCEPT_WITH_CLARIFICATION
"Digital receipt" does not by itself redefine FR-20 as ZATCA e-invoicing.
ZATCA requirements apply where legally required for the actual
seller/taxpayer transaction and are governed separately.

I-13 AC-FR-23-01=ACCEPT_WITH_THRESHOLD
REMINDER_DEFAULT=7_DAYS_BEFORE_DUE
SECOND_REMINDER=24_HOURS_BEFORE_DUE_IF_OUTSTANDING
Tenant/user configuration may add reminders but may not suppress these defaults.

I-14 AC-FR-27-01=ACCEPT_WITH_THRESHOLD
REAL_TIME_BOUND=5_SECONDS
A qualifying pharmacy-operation event becomes visible on another authorised
dashboard session with p95 <= 5 seconds, measured over at least 100 events
in the acceptance environment.

I-15 AC-FR-30-01=ACCEPT_WITH_SCOPE
Phase-1 automated compliance reporting covers the BRD controlled-substance
audit trail plus applicable antimicrobial and notifiable-disease records
represented by the ratified criteria. Live regulator submission remains
subject to confirmed regulator obligation/interface.

I-16 AC-FR-30-03=ACCEPT
The drafted fails-if becomes the ratified criterion despite the source REQ
having no source-authored fails-if.

NFR_INTERPRETATIONS:

NFR-07=ACCEPT
KSA residency is the governing target. Historical Bahrain-region language
does not override the subsequently governed residency decision.

NFR-09=ACCEPT_WITH_THRESHOLD
STANDARD=Saudi_PDPL + Implementing_Regulations + applicable_SDAIA_instruments
PASS=100_PERCENT_APPLICABLE_CONTROLS_EVIDENCED
UNRESOLVED_CRITICAL_FINDINGS=0
UNRESOLVED_HIGH_FINDINGS=0
EVIDENCE_BASIS=PDPL compliance matrix, to be produced and Sponsor-approved
DEPENDENCY=COUNSEL:PDPL_COMPLIANCE_MATRIX
This interprets the BRD "HIPAA equivalent" target; it is not a BRD
amendment. PDPL is the mandatory KSA floor.

NFR-15=ACCEPT_WITH_THRESHOLD
AUTHENTICATED_DEFAULT=100_REQUESTS_PER_MINUTE_PER_PRINCIPAL
ANONYMOUS_DEFAULT=30_REQUESTS_PER_MINUTE_PER_CLIENT_IP
EXCESS_RESPONSE=HTTP_429
ENDPOINT_SPECIFIC_STRICTER_LIMITS=PERMITTED
LIMITS_MUST_BE_CONFIGURABLE_AND_AUDITABLE

NFR-13_PHASE1_RELEVANT=NO
NFR-14_PHASE1_RELEVANT=NO

KNOWN_FAILING_CRITERIA=[AC-FR-02-04]
DISPOSITION=BUILD_REMEDIATION_NOT_REQUIREMENT_REOPEN

EXCEPTIONS=[]

NEXT:
1. freeze ratified acceptance pack;
2. make ACCEPTED mechanically reachable only from complete criterion evidence;
3. close Phase-1 requirements-definition track;
4. issue implementation/closure work against ratified criteria;
5. do not reopen denominator, BRD authority or general acceptance discovery.
