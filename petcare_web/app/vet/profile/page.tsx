'use client'

/**
 * J-V1 internal portion — the veterinarian's profile and licence status (CV-12) (MVC-EPC-D-001 D3a, R21.4; R18.4, R19.3).
 *
 * Everything shown comes from the served API: the licences the veterinarian registered with (GET /api/practitioners/me/licence)
 * and whether a practitioner authority is in force now (GET /api/practitioners/me/authority). A licence is SUBMITTED until a
 * named staff member verifies it; that verification is an ATTESTATION recorded by the platform — it is NOT verification against
 * the issuing authority's registry, which is the open external dependency X-33 (R19.3). The page says so and never presents an
 * attestation as a registry check. No clinical act is possible until an authority is in force. Arabic by default, right-to-left.
 */

import { useCallback, useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'
import { formatKsa } from '@/lib/ksaTime'

type Licence = { licence_id: string; licence_number: string; issuing_authority: string; expires_on: string; submitted_at: string;
  status: 'SUBMITTED' | 'VERIFIED'; verification: null | { method: 'MANUAL_STAFF' | 'AUTHORITY_LOOKUP'; verified_at: string } }
type Authority = { in_force: boolean; reason: string | null; grants: { expires_at: string | null }[] }

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
const get = (path: string) => fetch(`${apiBase}${path}`, { credentials: 'include', cache: 'no-store' })

const L = {
  title: { ar: 'الملف المهني وحالة الترخيص', en: 'Profile and licence status' },
  licences: { ar: 'تراخيص مزاولة المهنة', en: 'Practice licences' },
  none: { ar: 'لا توجد تراخيص مسجلة.', en: 'No licence is registered.' },
  number: { ar: 'رقم الترخيص', en: 'Licence number' },
  authority: { ar: 'جهة الإصدار', en: 'Issuing authority' },
  expires: { ar: 'تاريخ الانتهاء', en: 'Expires on' },
  SUBMITTED: { ar: 'مُقدَّم — بانتظار التحقق من فريق المنصة', en: 'Submitted — awaiting verification by platform staff' },
  VERIFIED_MANUAL: { ar: 'تحقّق منه موظف مختص (إقرار موثّق)', en: 'Verified by a named staff member (recorded attestation)' },
  VERIFIED_LOOKUP: { ar: 'تحقّق منه عبر استعلام جهة الإصدار', en: 'Verified by an issuing-authority lookup' },
  registry: { ar: 'التحقق من السجل الرسمي لجهة الإصدار غير متاح حالياً؛ إقرار الموظف لا يُعدّ تحققاً من السجل.',
    en: "Verification against the issuing authority's registry is not available yet; a staff attestation is not a registry check." },
  inForce: { ar: 'صلاحية الممارسة سارية', en: 'Practice authority in force' },
  until: { ar: 'حتى', en: 'until' },
  notInForce: { ar: 'لا توجد صلاحية ممارسة سارية؛ الأعمال السريرية غير متاحة حتى التحقق من الترخيص.',
    en: 'No practice authority is in force; clinical acts are unavailable until a licence is verified.' },
  failed: { ar: 'تعذر عرض حالة الترخيص.', en: 'The licence status could not be shown.' },
} as const

export default function VetProfilePage() {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  const t = (k: keyof typeof L) => L[k][isAr ? 'ar' : 'en']
  const [licences, setLicences] = useState<Licence[] | null>(null)
  const [authority, setAuthority] = useState<Authority | null>(null)
  const [failed, setFailed] = useState(false)

  const load = useCallback(async () => {
    const l = await get('/api/practitioners/me/licence')
    if (!l.ok) { setFailed(true); return }
    setLicences(await l.json())
    // A veterinarian not yet assigned to a clinic has no tenant: no authority can be in force (fail closed).
    const a = await get('/api/practitioners/me/authority')
    setAuthority(a.ok ? await a.json() : { in_force: false, reason: null, grants: [] })
  }, [])

  useEffect(() => { void load() }, [load])

  const day = (d: string) => formatKsa(`${d}T12:00:00+03:00`, lang, { dateStyle: 'medium' })
  const expiry = authority?.grants.map(g => g.expires_at).filter((x): x is string => !!x).sort().at(-1)

  return (
    <main className="stack" dir={isAr ? 'rtl' : 'ltr'} lang={isAr ? 'ar' : 'en'} data-testid="vet-profile">
      <h1 className="title-lg">{t('title')}</h1>
      {failed && <p role="alert">{t('failed')}</p>}

      {authority && (authority.in_force
        ? <p data-testid="vet-authority" data-in-force="true">{t('inForce')}{expiry ? ` ${t('until')} ${formatKsa(expiry, lang, { dateStyle: 'medium' })}` : ''}</p>
        : <p role="status" data-testid="vet-authority" data-in-force="false">{t('notInForce')}</p>)}

      <h2>{t('licences')}</h2>
      {licences && licences.length === 0 && <p>{t('none')}</p>}
      {licences && licences.length > 0 && (
        <ul>{licences.map(l => (
          <li key={l.licence_id} data-testid="vet-licence" data-status={l.status} data-method={l.verification?.method ?? ''}>
            <dl>
              <dt>{t('number')}</dt><dd translate="no">{l.licence_number}</dd>
              <dt>{t('authority')}</dt><dd translate="no">{l.issuing_authority}</dd>
              <dt>{t('expires')}</dt><dd>{day(l.expires_on)}</dd>
            </dl>
            <p data-testid="vet-licence-status">{l.status === 'SUBMITTED' ? t('SUBMITTED')
              : t(l.verification?.method === 'AUTHORITY_LOOKUP' ? 'VERIFIED_LOOKUP' : 'VERIFIED_MANUAL')}</p>
          </li>
        ))}</ul>
      )}
      <p className="muted" data-testid="vet-registry-notice">{t('registry')}</p>
    </main>
  )
}
