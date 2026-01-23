async function jget(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return await r.json();
}

export const api = {
  evidenceIndex: () => jget("/api/evidence/index"),
  evidenceChecksums: () => fetch("/api/evidence/checksums").then(r => r.text()),
  evidenceFile: (path) => fetch(`/api/evidence/file?path=${encodeURIComponent(path)}`),

  securityRls: () => jget("/api/security/rls"),
  securityPolicies: () => jget("/api/security/policies"),
  securityPolicyCount: () => jget("/api/security/policy_count"),
  securityBypass: () => jget("/api/security/bypassrls"),
  securityGrants: () => jget("/api/security/grants"),
};
