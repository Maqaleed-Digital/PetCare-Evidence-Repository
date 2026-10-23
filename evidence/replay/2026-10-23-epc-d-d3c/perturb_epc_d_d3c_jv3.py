"""MVC-EPC-D-001 D3c perturbations: J-V3 consultation workspace (only the consultation's own veterinarian; drafts are versions and
the latest is in force; drafts are validated; writing needs a live practitioner authority; the note's text stays out of the audit;
a template fills only empty sections; the queue links the workspace). python3 perturb_epc_d_d3c_jv3.py <root>.
ARMED = the named test FAILS."""
import subprocess
import sys
R = sys.argv[1].rstrip("/") + "/"
T = "petcare_api/tests/test_epc_d3c_jv3_workspace.py::"
PG = "petcare_api/tests/test_epc_d3c_jv3_soap_draft_postgres.py"
PY = lambda t: ["python3", "-m", "pytest", t, "-q", "-p", "no:cacheprovider"]
VT = lambda t: ["npx", "vitest", "run", t]
M, SN, PGR = "petcare_api/main.py", "petcare_api/soap_notes.py", "petcare_api/postgres_repositories.py"
LIB, QP = "petcare_web/lib/soapTemplates.ts", "petcare_web/app/vet/queue/page.tsx"
UT = "__tests__/jv3-workspace.test.tsx"
P = [
 ("P-D3C-JV3-OTHER-VET-SEES-WORKSPACE", [(M, "    if c is None or c.veterinarian_id != actor_id:\n        raise HTTPException(404, {\"error\": \"CONSULTATION_NOT_FOUND\"})",
   "    if c is None:\n        raise HTTPException(404, {\"error\": \"CONSULTATION_NOT_FOUND\"})")],
  PY(T + "test_only_the_consultations_own_veterinarian_has_its_workspace")),
 ("P-D3C-JV3-OWNER-HAS-WORKSPACE", [(M, "    actor_id, actor_role, tenant_id = _vet_session(request, role)\n    c = CONSULTATION_REPO.get(session_id, tenant_id=tenant_id)\n    if c is None or c.veterinarian_id != actor_id:",
   "    actor_id, actor_role = _actor(request); tenant_id = require_tenant(request)\n    c = CONSULTATION_REPO.get(session_id, tenant_id=tenant_id)\n    if c is None or actor_id not in (c.veterinarian_id, c.owner_id):")],
  PY(T + "test_only_the_consultations_own_veterinarian_has_its_workspace")),
 ("P-D3C-JV3-NO-AUTHORITY-CHECK", [(M, "    c, actor_id, actor_role, tenant_id = _own_consultation(request, role, session_id)\n    _require_practitioner_authority(actor_id, tenant_id)\n    d = soap.SoapDraft(",
   "    c, actor_id, actor_role, tenant_id = _own_consultation(request, role, session_id)\n    d = soap.SoapDraft(")],
  PY(T + "test_writing_a_draft_needs_a_practitioner_authority_in_force")),
 ("P-D3C-JV3-FIRST-DRAFT-WINS", [(SN, "        return max(mine, key=lambda d: (d.saved_at, d.draft_id)) if mine else None",
   "        return min(mine, key=lambda d: (d.saved_at, d.draft_id)) if mine else None")],
  PY(T + "test_drafts_are_versions_the_latest_is_in_force_and_unsigned")),
 ("P-D3C-JV3-BLANK-DRAFT-ACCEPTED", [(SN, "    if not any(t.strip() for t in texts):", "    if not any(texts):")],
  PY(T + "test_an_invalid_draft_is_refused_and_changes_nothing")),
 ("P-D3C-JV3-UNKNOWN-TEMPLATE-ACCEPTED", [(SN, "    if d.template_id is not None and d.template_id not in TEMPLATES:", "    if False:")],
  PY(T + "test_an_invalid_draft_is_refused_and_changes_nothing")),
 ("P-D3C-JV3-OVERLONG-SECTION-ACCEPTED", [(SN, "    if any(len(t) > MAX_SECTION for t in texts):", "    if False:")],
  PY(T + "test_an_invalid_draft_is_refused_and_changes_nothing")),
 ("P-D3C-JV3-NOTE-TEXT-IN-AUDIT", [(M, "           correlation_id=x_correlation_id, reason_code=f\"template:{d.template_id or 'none'}\")",
   "           correlation_id=x_correlation_id, reason_code=f\"template:{d.template_id or 'none'}:{d.subjective[:40]}\")")],
  PY(T + "test_drafts_are_versions_the_latest_is_in_force_and_unsigned")),
 ("P-D3C-JV3-TEMPLATE-WITH-CLINICAL-VALUE", [(SN, '"plan": {"ar": "العلاج:\\nالرعاية المنزلية:\\nالمتابعة:", "en": "Treatment:\\nHome care:\\nFollow-up:"},',
   '"plan": {"ar": "العلاج:\\nالرعاية المنزلية:\\nالمتابعة:", "en": "Treatment: rest\\nHome care:\\nFollow-up:"},')],
  PY(T + "test_templates_are_headings_only_in_both_languages")),
 ("P-D3C-JV3-PG-LATEST-IS-OLDEST", [(PGR, '"ORDER BY saved_at DESC, draft_id DESC LIMIT 1", (session_id, tenant_id)).fetchone()',
   '"ORDER BY saved_at ASC, draft_id ASC LIMIT 1", (session_id, tenant_id)).fetchone()')], PY(PG)),
 ("P-D3C-JV3-PG-TENANT-UNSCOPED", [(PGR, '"SELECT count(*) FROM consultation_soap_draft WHERE session_id = %s AND tenant_id = %s",\n                                (session_id, tenant_id)',
   '"SELECT count(*) FROM consultation_soap_draft WHERE session_id = %s OR tenant_id = %s",\n                                (session_id, tenant_id)')], PY(PG)),
 ("P-D3C-JV3-UI-TEMPLATE-OVERWRITES", [(LIB, "current[s].trim() ? current[s] : tpl.sections[s][lang]", "tpl.sections[s][lang]")], VT(UT)),
 ("P-D3C-JV3-UI-TEMPLATE-NOT-SENT", [(f"petcare_web/app/vet/consultations/[sessionId]/page.tsx", "body: JSON.stringify({ template_id: templateId || null, ...note })",
   "body: JSON.stringify({ template_id: null, ...note })")], VT(UT)),
 ("P-D3C-JV3-UI-QUEUE-NO-WORKSPACE-LINK", [(QP, "<div><a href={`/vet/consultations/${encodeURIComponent(c.session_id)}`} data-testid=\"queue-open-workspace\">{t('workspace')}</a></div>", "")],
  VT(UT)),
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
