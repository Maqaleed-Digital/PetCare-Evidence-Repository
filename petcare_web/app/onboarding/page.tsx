export default function OnboardingPage() {
  return (
    <main className="stack">
      <div className="card">
        <div className="kicker">Pilot programme</div>
        <div className="title-lg">Clinic onboarding</div>
        <p className="subtitle" style={{ maxWidth: 600 }}>
          VetiCare is in a controlled pilot phase. Clinics are onboarded
          individually with full governance verification before any system
          access is granted.
        </p>
      </div>

      <div className="grid cols2">
        <div className="card stack card-sm">
          <div className="badge badge-blue" style={{ alignSelf: 'flex-start' }}>Step 1</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>Eligibility check</div>
            <p className="subtitle">
              Valid commercial registration, licensed vets on staff, and
              a verified clinic location are required before onboarding begins.
            </p>
          </div>
        </div>

        <div className="card stack card-sm">
          <div className="badge badge-blue" style={{ alignSelf: 'flex-start' }}>Step 2</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>Identity verification</div>
            <p className="subtitle">
              Each vet is verified against the national licensing registry.
              No system access is granted until verification is complete.
            </p>
          </div>
        </div>

        <div className="card stack card-sm">
          <div className="badge badge-blue" style={{ alignSelf: 'flex-start' }}>Step 3</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>Account provisioning</div>
            <p className="subtitle">
              Roles are assigned via the admin portal. All provisioning
              events are audit-logged and tied to a correlation ID.
            </p>
          </div>
        </div>

        <div className="card stack card-sm">
          <div className="badge badge-green" style={{ alignSelf: 'flex-start' }}>Step 4</div>
          <div>
            <div className="title" style={{ fontSize: 16 }}>Pilot activation</div>
            <p className="subtitle">
              Once active, the clinic dashboard, consultation queue, and
              prescription workflow are accessible under governed operation.
            </p>
          </div>
        </div>
      </div>

      <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 24, flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 240 }}>
          <div className="title" style={{ fontSize: 16 }}>Ready to join the pilot?</div>
          <p className="subtitle">Reach out to the onboarding team with your clinic registration details.</p>
        </div>
        <a className="button" href="mailto:onboarding@myveticare.com">Apply for pilot access</a>
      </div>
    </main>
  )
}
