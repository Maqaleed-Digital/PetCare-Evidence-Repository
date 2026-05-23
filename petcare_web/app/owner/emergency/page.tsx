'use client'

/**
 * /owner/emergency — Emergency-access BASELINE (WI-3, display-only).
 *
 * HARD BOUNDARIES (per MVC-UX-WO-001 WI-3):
 *  - Display-only triage guidance + urgent-contact path.
 *  - NOT FR-11: no vet queue, no live routing, no autonomous decisioning,
 *    no diagnosis. The licensed veterinarian remains the clinical authority.
 *  - All evaluation runs client-side via lib/triage.ts. There is NO POST to
 *    a backend and NO server-side dispatch from this page.
 */

import { useMemo, useState } from 'react'
import { useLang } from '@/components/LangProvider'
import { STRINGS } from '@/lib/strings'
import {
  evaluateTriage,
  symptomsForSpecies,
  SYMPTOM_LABELS,
  SEVERITY_MAP,
  type Species,
  type Severity,
} from '@/lib/triage'

const SEVERITY_STYLE: Record<Severity, { background: string; color: string; border: string }> = {
  critical: { background: '#fee4e2', color: '#7a271a', border: '#fda29b' },
  urgent:   { background: '#fef0c7', color: '#7a2e0e', border: '#fec84b' },
  routine:  { background: '#ecfdf3', color: '#054f31', border: '#abefc6' },
}

export default function EmergencyPage() {
  const { t } = useLang()
  const s = STRINGS.emergency

  const [species, setSpecies] = useState<Species>('dog')
  const [picked, setPicked] = useState<Set<string>>(new Set())
  const [result, setResult] = useState<{ severity: Severity; triggered: readonly string[] } | null>(null)

  const symptoms = useMemo(() => symptomsForSpecies(species), [species])

  function toggleSymptom(id: string) {
    setPicked(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  function handleEvaluate() {
    setResult(evaluateTriage(species, [...picked]))
  }

  function severityBanner(severity: Severity) {
    if (severity === 'critical') return t(s.severityCriticalBanner)
    if (severity === 'urgent')   return t(s.severityUrgentBanner)
    return t(s.severityRoutineBanner)
  }

  return (
    <main className="stack" style={{ maxWidth: 720 }}>
      <div>
        <div className="title-lg">{t(s.title)}</div>
        <p className="subtitle" style={{ marginTop: 6 }}>{t(s.sub)}</p>
      </div>

      {/* Urgent-contact card — visible immediately so guidance is reachable
          without filling the symptom form. */}
      <div className="card" style={{ borderColor: '#fda29b', background: '#fef3f2' }}>
        <div className="kicker" style={{ color: '#7a271a' }}>{t(s.urgentContactLabel)}</div>
        <p style={{ marginTop: 6, lineHeight: 1.6 }}>{t(s.urgentContactBody)}</p>
      </div>

      {/* Species picker */}
      <div className="card stack">
        <div>
          <div className="kicker">{t(s.speciesLabel)}</div>
          <div role="radiogroup" aria-label={t(s.speciesLabel)} style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 8 }}>
            {(['dog', 'cat', 'bird'] as const).map(sp => (
              <label key={sp} style={{
                display: 'inline-flex', alignItems: 'center', gap: 8,
                padding: '12px 16px', minHeight: 48,
                border: `1.5px solid ${species === sp ? 'var(--accent)' : 'var(--line)'}`,
                borderRadius: 8, cursor: 'pointer',
                background: species === sp ? 'var(--accent-light)' : '#fff',
                fontWeight: 600, fontSize: 14,
              }}>
                <input
                  type="radio" name="species" value={sp}
                  checked={species === sp}
                  onChange={() => { setSpecies(sp); setPicked(new Set()); setResult(null) }}
                  style={{ width: 18, height: 18 }}
                />
                <span>{sp === 'dog' ? t(s.speciesDog) : sp === 'cat' ? t(s.speciesCat) : t(s.speciesBird)}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Symptom checklist (species + universal rules) */}
        <div>
          <div className="kicker">{t(s.symptomsLabel)}</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 8, marginTop: 8 }}>
            {symptoms.map(id => {
              const label = SYMPTOM_LABELS[id]
              const sev = SEVERITY_MAP[id]
              return (
                <label key={id} style={{
                  display: 'flex', alignItems: 'center', gap: 10,
                  padding: '12px 14px', minHeight: 48,
                  border: '1px solid var(--line)', borderRadius: 8,
                  background: '#fff', cursor: 'pointer',
                }}>
                  <input
                    type="checkbox"
                    checked={picked.has(id)}
                    onChange={() => toggleSymptom(id)}
                    aria-label={t(label)}
                    style={{ width: 18, height: 18 }}
                  />
                  <span style={{ fontSize: 14 }}>{t(label)}</span>
                  <span className={`badge ${sev === 'critical' ? 'badge-amber' : 'badge-gray'}`} style={{ marginInlineStart: 'auto' }}>
                    {sev}
                  </span>
                </label>
              )
            })}
          </div>
        </div>

        <button onClick={handleEvaluate} className="button" style={{ alignSelf: 'flex-start', minHeight: 48 }}>
          {t(s.evaluateCta)}
        </button>
      </div>

      {/* Triage result panel — display-only */}
      {result && (
        <div role="status" aria-live="polite" className="card" style={{
          background: SEVERITY_STYLE[result.severity].background,
          borderColor: SEVERITY_STYLE[result.severity].border,
          color:       SEVERITY_STYLE[result.severity].color,
        }}>
          <div style={{ fontWeight: 800, fontSize: 16, marginBottom: 8 }}>
            {severityBanner(result.severity)}
          </div>
          {result.triggered.length > 0 && (
            <div>
              <div className="kicker" style={{ color: 'inherit' }}>{t(s.triggeredLabel)}</div>
              <ul style={{ marginTop: 6, paddingInlineStart: 18 }}>
                {result.triggered.map(id => (
                  <li key={id}>{t(SYMPTOM_LABELS[id])}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <p className="muted" style={{ fontSize: 12, lineHeight: 1.6 }}>{t(s.noQueueNote)}</p>

      <p>
        <a href="/owner" style={{ color: 'var(--accent)', fontSize: 14 }}>{t(s.backToOwner)}</a>
      </p>
    </main>
  )
}
