'use client'

/**
 * The dispensing queue — Option A.
 *
 * This page was a shell: four hard-coded cards, every one of them permanently
 * empty, including "Cold-chain tracking" and "Safety checks" for capabilities
 * that do not exist (FR-16 and FR-15 are out of Option A's scope). A surface
 * that names a capability it does not have reads as a delivered feature to
 * anyone who opens it, which is why those cards are gone rather than left
 * showing "no items".
 *
 * What is here is backed by real API calls against real state. Nothing is
 * seeded, mocked or faked: an empty queue means the tenant has no verified
 * prescriptions.
 *
 * WHO CAN USE THIS. Veterinarian and partner clinic admin. `pharmacy` is not an
 * authorization principal in this estate (PHARMACY_ROLE=REMOVE) and the
 * middleware already routes /pharmacy to ['vet','admin'] for that reason. An
 * external pharmacy operator has no identity the platform can mint, so they
 * cannot open this page — that is a Sponsor product decision, not something the
 * UI can route around, and the banner below says so rather than leaving the
 * reader to infer it from an empty screen.
 */

import { useCallback, useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'

type Prescription = {
  prescription_id: string
  pet_id: string
  medication_name: string
  dosage: string
  instructions: string
  status: string
  issued_at: string | null
  verified_at: string | null
  verified_by_vet_id: string | null
  issuing_vet_id: string
}

type Doc = {
  document_id: string
  filename: string
  content_type: string
  byte_size: number
}

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')

async function call(path: string, init?: RequestInit) {
  return fetch(`${apiBase}${path}`, {
    credentials: 'include',
    cache: 'no-store',
    ...init,
  })
}

function fmt(iso: string | null, isAr: boolean): string {
  if (!iso) return '—'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return '—'
  return d.toLocaleString(isAr ? 'ar-SA' : 'en-GB', {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

export default function PharmacyPage() {
  const { lang } = useLang()
  const isAr = lang === 'ar'

  const [queue, setQueue] = useState<Prescription[]>([])
  const [selected, setSelected] = useState<Prescription | null>(null)
  const [docs, setDocs] = useState<Doc[]>([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  const loadQueue = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const res = await call('/api/prescriptions/queue/awaiting-dispense')
      if (res.status === 401) {
        setError(isAr ? 'انتهت الجلسة. يرجى تسجيل الدخول مرة أخرى.' : 'Session expired. Please sign in again.')
        setQueue([])
        return
      }
      if (res.status === 403) {
        // The honest message. Not "no items" — the caller is not permitted.
        setError(isAr
          ? 'هذا الحساب غير مخوّل بقراءة قائمة الصرف.'
          : 'This account is not authorized to read the dispensing queue.')
        setQueue([])
        return
      }
      if (!res.ok) {
        setError(`${isAr ? 'تعذّر تحميل القائمة' : 'Could not load the queue'} (${res.status})`)
        setQueue([])
        return
      }
      setQueue(await res.json())
    } catch {
      setError(isAr ? 'تعذّر الوصول إلى الخادم.' : 'Could not reach the server.')
      setQueue([])
    } finally {
      setLoading(false)
    }
  }, [isAr])

  useEffect(() => { void loadQueue() }, [loadQueue])

  async function open(rx: Prescription) {
    setSelected(rx)
    setNotice('')
    setDocs([])
    const res = await call(`/api/prescriptions/${rx.prescription_id}/documents`)
    if (res.ok) setDocs(await res.json())
  }

  async function dispense(rx: Prescription) {
    setBusy(true)
    setError('')
    setNotice('')
    try {
      const res = await call(`/api/prescriptions/${rx.prescription_id}/dispense`, { method: 'POST' })
      if (res.ok) {
        setNotice(isAr ? 'تم الصرف وتسجيله في سجل التدقيق.' : 'Dispensed and recorded in the audit log.')
        setSelected(null)
        await loadQueue()
        return
      }
      // Each failure says what actually happened. A single "failed" message
      // would make "you may not do this" and "this is already dispensed"
      // indistinguishable to the person holding the medicine.
      if (res.status === 403) {
        setError(isAr
          ? 'الصرف مقصور على الطبيب البيطري (REQ-DISP-AUTH-FAILCLOSED).'
          : 'Dispensing is restricted to a veterinarian (REQ-DISP-AUTH-FAILCLOSED).')
      } else if (res.status === 409) {
        // The refresh runs FIRST and the message is set after it.
        //
        // `loadQueue` clears the error banner on entry — it has to, or a stale
        // load failure would outlive the load that succeeded. So setting the
        // message before awaiting it wiped the only explanation the person
        // holding the medicine was going to get, and the screen simply went
        // quiet. Caught by the 409 case in __tests__/pharmacy-queue.test.tsx.
        await loadQueue()
        setError(isAr
          ? 'لا يمكن الصرف: الوصفة ليست في حالة «تم التحقق».'
          : 'Cannot dispense: the prescription is not in the verified state.')
      } else if (res.status === 404) {
        await loadQueue()
        setError(isAr ? 'الوصفة غير موجودة في نطاقك.' : 'Prescription not found in your scope.')
      } else {
        setError(`${isAr ? 'فشل الصرف' : 'Dispense failed'} (${res.status})`)
      }
    } catch {
      setError(isAr ? 'تعذّر الوصول إلى الخادم.' : 'Could not reach the server.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="stack" dir={isAr ? 'rtl' : 'ltr'}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <div className="kicker">{isAr ? 'بوابة الصيدلية' : 'Pharmacy portal'}</div>
          <div className="title-lg">{isAr ? 'قائمة الصرف' : 'Dispensing queue'}</div>
        </div>
        <span className="badge badge-green">
          <span className="icon-dot green" />{isAr ? 'التدقيق نشط' : 'Audit active'}
        </span>
      </div>

      <div className="note">
        <span className="muted">
          {isAr
            ? 'صلاحية الصرف مقصورة حاليًا على الطبيب البيطري. لا يوجد دور صيدلاني معتمد في هذا النظام، وإضافته قرار يعود للجهة الراعية.'
            : 'Dispensing authority is currently the veterinarian’s. No dispensing principal exists for an external operator; admitting one is a Sponsor decision.'}
        </span>
      </div>

      {error && (
        <div className="note" role="alert" data-testid="dispense-error">
          <strong>{error}</strong>
        </div>
      )}
      {notice && (
        <div className="note" role="status" data-testid="dispense-notice">
          <strong>{notice}</strong>
        </div>
      )}

      <div className="grid cols2">
        <div className="role-card" data-list-region="pharmacy-validated-prescriptions">
          <div>
            <div className="title" style={{ fontSize: 16 }}>
              {isAr ? 'الوصفات الموثّقة' : 'Verified prescriptions'}
            </div>
            <p className="subtitle">
              {isAr
                ? 'تظهر فقط الوصفات التي تحقّق منها الطبيب. الوصفات غير المتحقّق منها لا يمكن صرفها.'
                : 'Only vet-verified prescriptions appear here. Unverified prescriptions cannot be dispensed.'}
            </p>
          </div>

          {/*
            * PORT-08. A list region must resolve to rows or to an explicit
            * empty state — never to neither. `loading` and `error` are both
            * "no rows", so the empty marker is rendered in those states too,
            * with text that says which one it is. Gating the marker on
            * `!loading && !error` is exactly how a region goes blank while a
            * request is in flight or has failed, which is the state this guard
            * exists to forbid.
            */}
          {queue.length === 0 && (
            <span className="muted" data-list-empty="">
              {loading
                ? (isAr ? 'جارٍ التحميل…' : 'Loading…')
                : error
                  ? (isAr ? 'تعذّر عرض القائمة' : 'The queue could not be shown')
                  : (isAr ? 'لا توجد وصفات بانتظار الصرف' : 'No prescriptions awaiting dispense')}
            </span>
          )}

          {queue.length > 0 && (
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'grid', gap: 8 }}>
              {queue.map((rx) => (
                <li key={rx.prescription_id} data-list-row="">
                  <button
                    type="button"
                    onClick={() => void open(rx)}
                    data-testid="queue-item"
                    style={{
                      width: '100%', textAlign: isAr ? 'right' : 'left', cursor: 'pointer',
                      padding: 12, borderRadius: 8, border: '1px solid var(--border, #ddd)',
                      background: selected?.prescription_id === rx.prescription_id
                        ? 'var(--surface-2, #f3f4f6)' : 'transparent',
                    }}
                  >
                    <div className="title" style={{ fontSize: 15 }}>
                      {rx.medication_name} · {rx.dosage}
                    </div>
                    <div className="muted" style={{ fontSize: 13 }}>
                      {isAr ? 'تم التحقق' : 'Verified'}: {fmt(rx.verified_at, isAr)}
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="role-card" data-list-region="pharmacy-prescription-detail">
          <div>
            <div className="title" style={{ fontSize: 16 }}>
              {isAr ? 'تفاصيل الوصفة' : 'Prescription detail'}
            </div>
            <p className="subtitle">
              {isAr
                ? 'راجع التعليمات وحالة التحقق والمرفقات قبل الصرف.'
                : 'Review instructions, verification status and attachments before dispensing.'}
            </p>
          </div>

          {!selected && (
            <span className="muted" data-list-empty="">
              {isAr ? 'اختر وصفة من القائمة' : 'Select a prescription from the queue'}
            </span>
          )}

          {selected && (
            <div style={{ display: 'grid', gap: 10 }} data-list-row="">
              <div>
                <div className="title" style={{ fontSize: 15 }}>
                  {selected.medication_name} · {selected.dosage}
                </div>
                <p className="subtitle" style={{ margin: 0 }}>{selected.instructions}</p>
              </div>

              <span className="badge badge-green" data-testid="verification-badge">
                <span className="icon-dot green" />
                {isAr ? 'تم تحقق الطبيب' : 'Vet verified'} · {fmt(selected.verified_at, isAr)}
              </span>

              <dl style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '4px 12px', margin: 0 }}>
                <dt className="muted">{isAr ? 'الطبيب الواصف' : 'Prescribing vet'}</dt>
                <dd style={{ margin: 0 }}>{selected.issuing_vet_id}</dd>
                <dt className="muted">{isAr ? 'المتحقّق' : 'Verified by'}</dt>
                <dd style={{ margin: 0 }}>{selected.verified_by_vet_id ?? '—'}</dd>
                <dt className="muted">{isAr ? 'تاريخ الإصدار' : 'Issued'}</dt>
                <dd style={{ margin: 0 }}>{fmt(selected.issued_at, isAr)}</dd>
              </dl>

              <div>
                <div className="muted" style={{ fontSize: 13, marginBottom: 4 }}>
                  {isAr ? 'المرفقات' : 'Attachments'}
                </div>
                {docs.length === 0 && (
                  <span className="muted" style={{ fontSize: 13 }}>
                    {isAr ? 'لا توجد مرفقات' : 'No attachments'}
                  </span>
                )}
                {docs.map((d) => (
                  <a
                    key={d.document_id}
                    href={`${apiBase}/api/prescriptions/${selected.prescription_id}/documents/${d.document_id}`}
                    data-testid="document-link"
                    style={{ display: 'block', fontSize: 13 }}
                  >
                    {d.filename} ({Math.ceil(d.byte_size / 1024)} KB)
                  </a>
                ))}
              </div>

              <button
                type="button"
                disabled={busy}
                onClick={() => void dispense(selected)}
                data-testid="dispense-button"
                style={{ padding: '10px 16px', borderRadius: 8, cursor: busy ? 'wait' : 'pointer' }}
              >
                {busy
                  ? (isAr ? 'جارٍ الصرف…' : 'Dispensing…')
                  : (isAr ? 'تأكيد الصرف' : 'Confirm dispense')}
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="note">
        <span className="muted">
          {isAr
            ? 'عمليات الصرف غير قابلة للإلغاء بعد التأكيد. كل عملية مسجّلة ومنسوبة في سجل التدقيق.'
            : 'Dispense actions are irreversible once confirmed. Every action is attributed and recorded in the audit log.'}
        </span>
      </div>
    </main>
  )
}
