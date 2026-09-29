'use client'

import { useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'
import { STRINGS } from '@/lib/strings'
import { FirstRunModal } from '@/components/FirstRunModal'
import { AdvisoryDisclosureBanner } from '@/components/AdvisoryDisclosureBanner'
import { ModeDisclosureBanner } from '@/components/ModeDisclosureBanner'
import { ConfidenceBand } from '@/components/ConfidenceBand'
import { ExplainabilityPanel } from '@/components/ExplainabilityPanel'
import { AuditTrailLink } from '@/components/AuditTrailLink'
import { ErrorState, LoadingState } from '@/components/ui'

export default function OwnerPage() {
  const { t } = useLang()
  const s = STRINGS.owner
  // CO-01 (MVC-EPC-D-001 D2d): the pets shown are the served ones — loading and error are explicit states, never a
  // blank region and never a claim that the owner has no pets before the server has said so.
  const [pets, setPets] = useState<{ pet_id: string; name: string; species: string }[] | 'loading' | 'error'>('loading')
  useEffect(() => {
    const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
    fetch(`${apiBase}/api/pets`, { credentials: 'include', cache: 'no-store' })
      .then(r => (r.ok ? r.json() : Promise.reject(r.status)))
      .then(b => setPets(Array.isArray(b) ? b : 'error'))
      .catch(() => setPets('error'))
  }, [])

  return (
    <main className="stack" id="pets">
      <FirstRunModal />

      <AdvisoryDisclosureBanner storageKey="vc_advisory_dismissed_owner" />

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <div className="kicker">{t(s.kicker)}</div>
          <div className="title-lg">{t(s.title)}</div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
          <span className="badge badge-green">
            <span className="icon-dot green" />{t(s.auditActive)}
          </span>
          {/* Emergency entry — 1 tap from /owner to /owner/emergency.
              Display-only triage; NOT a vet queue (WI-3 hard boundary). */}
          <a href="/owner/emergency" className="emergency-cta" aria-label={t(s.emergencyCta)}>
            <span aria-hidden="true">🚑</span>
            <span>{t(s.emergencyCta)}</span>
          </a>
        </div>
      </div>

      <p className="muted" style={{ fontSize: 13 }}>{t(s.emergencyHint)}</p>

      <div className="grid cols2">
        <section className="role-card" data-list-region="owner-pets" aria-labelledby="owner-pets-title">
          <div>
            <h2 id="owner-pets-title" className="title" style={{ fontSize: 16 }}>{t(s.petProfileTitle)}</h2>
            <p className="subtitle">{t(s.petProfileSub)}</p>
          </div>
          {pets === 'loading' ? <LoadingState /> : pets === 'error' ? <ErrorState /> : pets.length === 0
            ? <span className="muted" data-list-empty="">{t(s.petProfileEmpty)}</span>
            : (
              <ul className="ds-list" aria-label={t(s.petProfileTitle)}>
                {pets.slice(0, 3).map(p => <li key={p.pet_id} data-list-row="">{p.name} · {p.species}</li>)}
              </ul>
            )}
          <a className="button button-outline button-sm" href="/owner/pets" data-testid="owner-open-pets">
            {Array.isArray(pets) && pets.length === 0 ? t(s.addPet) : t(s.petsOpen)}
          </a>
        </section>

        <section className="role-card" aria-labelledby="owner-notifications-title">
          <div>
            <h2 id="owner-notifications-title" className="title" style={{ fontSize: 16 }}>{t(s.notificationsTitle)}</h2>
            <p className="subtitle">{t(s.notificationsSub)}</p>
          </div>
          <a className="button button-outline button-sm" href="/owner/notifications" data-testid="owner-open-notifications">
            {t(s.notificationsOpen)}
          </a>
        </section>

        <section className="role-card" aria-labelledby="owner-orders-title">
          <div>
            <h2 id="owner-orders-title" className="title" style={{ fontSize: 16 }}>{t(s.ordersTitle)}</h2>
            <p className="subtitle">{t(s.ordersSub)}</p>
          </div>
          <div className="row">
            <a className="button button-outline button-sm" href="/owner/orders">{t(s.ordersOpen)}</a>
            <a className="button button-outline button-sm" href="/owner/deliveries">{t(s.deliveriesOpen)}</a>
          </div>
        </section>

        <section className="role-card" aria-labelledby="owner-account-title">
          <div>
            <h2 id="owner-account-title" className="title" style={{ fontSize: 16 }}>{t(s.accountTitle)}</h2>
            <p className="subtitle">{t(s.accountSub)}</p>
          </div>
          <a className="button button-outline button-sm" href="/account">{t(s.accountOpen)}</a>
        </section>

        {/* Booking (J-O5) is not built yet: disclosed, never a dead link (closes D2-DEAD-LINK). */}
        <section className="role-card" aria-labelledby="owner-appointments-title">
          <div>
            <h2 id="owner-appointments-title" className="title" style={{ fontSize: 16 }}>{t(s.appointmentsTitle)}</h2>
            <p className="subtitle">{t(s.appointmentsSoon)}</p>
          </div>
          <ModeDisclosureBanner variant="badge" />
        </section>
      </div>

      <div className="note">
        <span className="muted">{t(s.governanceNote)}</span>
      </div>

      {/*
        WI-6 / WI-7 / WI-8 DARK SCAFFOLD MOUNT POINT.
        All three components return null while FEATURE_AI is OFF, so this
        aside renders empty in the pilot. When the flag activates and real
        AI/agent outputs land, this is where confidence + explanation +
        audit-trail link surface — wired and ready, no second build cycle.
      */}
      <aside data-testid="ai-surface-area" aria-hidden="true">
        <ConfidenceBand confidence={0.0} />
        <ExplainabilityPanel />
        <AuditTrailLink eventHandle={null} />
      </aside>
    </main>
  )
}
