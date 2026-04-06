export default function UnauthorizedPage({
  searchParams,
}: {
  searchParams: { from?: string; required?: string }
}) {
  const from = searchParams.from ?? ''
  const required = searchParams.required?.split(',') ?? []

  const roleLabels: Record<string, string> = {
    owner: 'Pet Owner',
    vet: 'Licensed Veterinarian',
    pharmacy: 'Pharmacy Operator',
    admin: 'Platform Admin',
  }

  return (
    <main style={{ maxWidth: 520, margin: '80px auto', padding: '0 24px' }}>
      <div className="card stack" style={{ textAlign: 'center', padding: 40 }}>
        <div style={{ fontSize: 48 }}>🔒</div>
        <div>
          <div className="title-lg">Access restricted</div>
          <p className="subtitle">
            {from
              ? `The page ${from} requires a specific role to access.`
              : 'You do not have permission to view this page.'}
          </p>
        </div>

        {required.length > 0 && (
          <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap' }}>
            <span className="muted" style={{ alignSelf: 'center' }}>Required role:</span>
            {required.map(r => (
              <span key={r} className="badge badge-blue">
                {roleLabels[r] ?? r}
              </span>
            ))}
          </div>
        )}

        <div className="divider" />

        <p className="muted">
          If you have an account, sign in and your role will be assigned automatically.
          Clinic and vet onboarding is available if you are joining the pilot.
        </p>

        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          <a className="button" href="/signin">Sign in</a>
          <a className="button button-outline" href="/">Back to home</a>
        </div>
      </div>
    </main>
  )
}
