'use client'

/**
 * /vet — consultation queue.
 *
 * PORT-08. This surface previously rendered three table rows — "Waiting",
 * "Draft", "Pending" against an em-dash patient, each with an Open /
 * Review & sign / Authorize action. There is no case source in the pilot, so
 * every one of them was fabricated. On a clinical surface that is not a
 * cosmetic defect: "Prescription - Pending - Authorize" reads as a
 * prescription waiting on a veterinarian, and the action does nothing.
 *
 * The queue now states that it is empty, and separately states that it is
 * scaffolded rather than merely quiet — those are different claims and the
 * pilot is the second one. The three capabilities are still described, as
 * capabilities, where they cannot be mistaken for cases.
 */

import { useLang } from '@/components/LangProvider'
import { ModeDisclosureBanner } from '@/components/ModeDisclosureBanner'

export default function VetPage() {
  const { lang } = useLang()
  const isAr = lang === 'ar'

  const capabilities = [
    {
      title: isAr ? 'قائمة الاستشارات' : 'Consultation queue',
      detail: isAr
        ? 'الحالات الواردة مرتبة حسب الأولوية السريرية.'
        : 'Incoming cases ordered by clinical priority.',
    },
    {
      title: isAr ? 'الملاحظة السريرية (SOAP)' : 'Clinical note (SOAP)',
      detail: isAr
        ? 'التوثيق السريري، ويصبح غير قابل للتعديل بعد التوقيع.'
        : 'Clinical documentation, immutable once signed.',
    },
    {
      title: isAr ? 'تفويض الوصفات' : 'Prescription authorization',
      detail: isAr
        ? 'التفويض من قبل الطبيب البيطري فقط؛ الصرف يغلق عند الفشل.'
        : 'Veterinarian-only authorization; dispensing fails closed.',
    },
  ]

  return (
    <main className="stack">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <div className="kicker">{isAr ? 'بوابة الطبيب البيطري' : 'Vet portal'}</div>
          <div className="title-lg">{isAr ? 'قائمة الاستشارات' : 'Consultation queue'}</div>
        </div>
        <span className="badge badge-green"><span className="icon-dot green" />{isAr ? 'التدقيق نشط' : 'Audit active'}</span>
      </div>

      <div className="card stack" data-list-region="vet-consultation-queue">
        <span
          className="muted"
          data-list-empty=""
          data-testid="vet-queue-empty"
        >
          {isAr ? 'لا توجد استشارات في القائمة' : 'No consultations in the queue'}
        </span>
        <ModeDisclosureBanner variant="inline" />
      </div>

      <div className="card stack">
        <div className="kicker">{isAr ? 'ما ستحمله هذه القائمة' : 'What this queue will carry'}</div>
        <ul style={{ margin: 0, paddingInlineStart: 18, display: 'grid', gap: 10 }}>
          {capabilities.map((c) => (
            <li key={c.title}>
              <span style={{ fontWeight: 700 }}>{c.title}</span>
              <span className="muted"> — {c.detail}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="note">
        <span className="muted">{isAr ? 'التوقيع السريري يتم من قبل الطبيب فقط وغير قابل للتعديل بعد الاكتمال. جميع تفويضات الوصفات متتبعة.' : 'Clinical sign-off is human-only and immutable once completed. All prescription authorizations are audit-traced.'}</span>
      </div>
    </main>
  )
}
