'use client'

/**
 * ExplainabilityPanel — WI-7 DARK SCAFFOLD (Register C-03 ExplainabilityBundle).
 *
 * Layered-disclosure shell for AI-output explanations: summary up front,
 * details (inputs + sources) behind a disclosure. Built, wired, gated
 * behind FEATURE_AI. Returns null while the flag is OFF — we do not
 * surface explanations for a non-running engine.
 */

import { useState } from 'react'
import { FEATURE_AI } from '@/lib/featureFlags'
import { useLang } from '@/components/LangProvider'
import { STRINGS } from '@/lib/strings'

interface Props {
  summary?: string
  inputs?: readonly string[]
  sources?: readonly string[]
}

export function ExplainabilityPanel({ summary, inputs, sources }: Props) {
  if (!FEATURE_AI) return null

  const { t } = useLang()
  const s = STRINGS.explainability
  const [open, setOpen] = useState(false)

  return (
    <div
      data-testid="explainability-panel"
      style={{
        padding: 12,
        background: '#f7f8fb',
        border: '1px solid var(--line)',
        borderRadius: 10,
      }}
    >
      <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 6 }}>
        {t(s.summaryLabel)}
      </div>
      <p style={{ fontSize: 13, lineHeight: 1.6, margin: 0 }}>
        {summary ?? t(s.notAvailable)}
      </p>

      {(inputs?.length || sources?.length) ? (
        <>
          <button
            type="button"
            onClick={() => setOpen(o => !o)}
            aria-expanded={open}
            className="button button-outline button-sm"
            style={{ marginTop: 10, minHeight: 36 }}
          >
            {open ? '−' : '+'}
          </button>

          {open && (
            <div style={{ marginTop: 10, fontSize: 12, lineHeight: 1.6 }}>
              {inputs?.length ? (
                <>
                  <div className="kicker">{t(s.inputsLabel)}</div>
                  <ul style={{ marginTop: 4, paddingInlineStart: 18 }}>
                    {inputs.map((i, idx) => <li key={idx}>{i}</li>)}
                  </ul>
                </>
              ) : null}
              {sources?.length ? (
                <>
                  <div className="kicker" style={{ marginTop: 8 }}>{t(s.sourcesLabel)}</div>
                  <ul style={{ marginTop: 4, paddingInlineStart: 18 }}>
                    {sources.map((src, idx) => <li key={idx}>{src}</li>)}
                  </ul>
                </>
              ) : null}
            </div>
          )}
        </>
      ) : null}
    </div>
  )
}
