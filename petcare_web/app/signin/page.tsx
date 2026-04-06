export default function SignInPage() {
  return (
    <main style={{ maxWidth: 480, margin: '80px auto', padding: '0 24px' }}>
      <div className="card stack" style={{ padding: 40 }}>
        <div>
          <div className="kicker">VetiCare pilot</div>
          <div className="title-lg">Sign in</div>
          <p className="subtitle">
            Access is controlled during the pilot phase. Your role is
            assigned by the platform team after identity verification.
          </p>
        </div>

        <div className="note">
          <p style={{ fontSize: 13, color: 'var(--warn)', fontWeight: 600, marginBottom: 4 }}>
            Pilot access only
          </p>
          <p className="muted">
            Authentication is being wired to the identity provider. If you
            are a licensed vet or clinic admin in the pilot cohort, contact
            your onboarding coordinator to receive access credentials.
          </p>
        </div>

        <div className="divider" />

        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <a className="button" href="mailto:onboarding@myveticare.com">
            Contact onboarding team
          </a>
          <a className="button button-outline" href="/onboarding">
            Clinic onboarding
          </a>
        </div>

        <p className="muted" style={{ textAlign: 'center' }}>
          <a href="/" style={{ color: 'var(--accent)' }}>← Back to home</a>
        </p>
      </div>
    </main>
  )
}
