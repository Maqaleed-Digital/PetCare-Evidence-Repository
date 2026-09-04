'use client'

/**
 * MarketplaceSeamPanel — PORT-09's visible half.
 *
 * Mounted on /admin. It shows what the marketplace surface will consume and
 * states plainly that it consumes nothing yet. It renders no partner, no
 * catalogue item, no contract and no settlement row, because there is no
 * transport behind the seam and inventing one would be exactly the failure
 * PORT-08 closed on the vet queue.
 */

import { useLang } from '@/components/LangProvider'
import { CANONICAL_READS, readMarketplace } from '@/lib/marketplace'

export function MarketplaceSeamPanel() {
  const { t } = useLang()
  const state = readMarketplace()

  return (
    <section
      className="card stack"
      data-testid="marketplace-seam-panel"
      data-list-region="admin-marketplace"
      aria-label="Marketplace"
    >
      <div>
        <div className="kicker">{t({ ar: 'سوق الشركاء', en: 'Partner marketplace' })}</div>
        <p className="subtitle" style={{ marginTop: 6 }}>
          {t({
            ar: 'يقرأ هذا السطح من خدمات الشركاء المعتمدة ولا يملك أي منطق خاص به.',
            en: 'This surface reads from the canonical partner services and owns no logic of its own.',
          })}
        </p>
      </div>

      {state.wired ? null : (
        <p
          className="muted"
          data-list-empty=""
          data-testid="marketplace-seam-unwired"
          style={{ fontSize: 13 }}
        >
          {t({
            ar: 'لا يوجد اتصال بخدمات الشركاء في هذه النسخة، ولذلك لا تُعرض أي بيانات. تفعيل السوق يتطلب قرار راعٍ.',
            en: 'No transport to the partner services exists in this build, so nothing is shown. Activating the marketplace requires a Sponsor decision.',
          })}
        </p>
      )}

      <div>
        <div className="muted" style={{ fontSize: 12, marginBottom: 6 }}>
          {t({ ar: 'القراءات المعتمدة التي سيستهلكها هذا السطح', en: 'Canonical reads this surface will consume' })}
        </div>
        <ul
          data-testid="marketplace-seam-citations"
          style={{ margin: 0, paddingInlineStart: 18, display: 'grid', gap: 6, fontSize: 13 }}
        >
          {CANONICAL_READS.map((r) => (
            <li key={`${r.module}.${r.fn}`}>
              <code style={{ fontSize: 12 }}>{r.module}.{r.fn}</code>
              <span className="muted"> — {r.surface}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
