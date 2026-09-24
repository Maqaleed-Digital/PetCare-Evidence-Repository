'use client'

/**
 * FR-02 — pet profiles (MVC-BUILD-RUNNER-001 U2).
 *
 * Ratified criteria AC-FR-02-01 (create and view a profile with the BRD fields)
 * and AC-FR-02-02 (medical history — records, prescriptions, lab results — and
 * owner preferences), in Arabic (default, RTL) and English.
 *
 * Everything shown comes from the served API: GET /api/pets, POST /api/pets,
 * GET /api/pets/{id}, PATCH /api/pets/{id}. Nothing is seeded or mocked; an
 * empty list means the owner has no pets. Tenant and owner come from the
 * session server-side — this page sends no actor, no owner and no tenant.
 */

import { FormEvent, useCallback, useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'

type Pet = {
  pet_id: string
  name: string
  species: string
  breed: string | null
  birth_date: string | null
  weight_kg: number | null
  medical_conditions: string | null
  allergies: string | null
  preferences: string | null
}

type Detail = {
  profile: Pet
  identifications: { identification_id: string; id_type: string; id_value: string; captured_at: string }[]
  medical_history: {
    records: { record_id: string; record_type: string; title: string; detail: string | null }[]
    prescriptions: { prescription_id: string; medication_name: string; dosage: string; status: string }[]
  }
}

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')

async function call(path: string, init?: RequestInit) {
  return fetch(`${apiBase}${path}`, { credentials: 'include', cache: 'no-store', ...init })
}

const L = {
  title: { ar: 'حيواناتي الأليفة', en: 'My pets' },
  empty: { ar: 'لا توجد حيوانات مسجلة بعد.', en: 'No pets registered yet.' },
  add: { ar: 'إضافة حيوان', en: 'Add a pet' },
  name: { ar: 'الاسم', en: 'Name' },
  species: { ar: 'النوع', en: 'Species' },
  breed: { ar: 'السلالة', en: 'Breed' },
  birth: { ar: 'تاريخ الميلاد', en: 'Birth date' },
  weight: { ar: 'الوزن (كغ)', en: 'Weight (kg)' },
  conditions: { ar: 'الحالات الطبية', en: 'Medical conditions' },
  allergies: { ar: 'الحساسية', en: 'Allergies' },
  preferences: { ar: 'التفضيلات', en: 'Preferences' },
  save: { ar: 'حفظ', en: 'Save' },
  history: { ar: 'السجل الطبي', en: 'Medical history' },
  records: { ar: 'نتائج المختبر والسجلات', en: 'Lab results and records' },
  prescriptions: { ar: 'الوصفات الطبية', en: 'Prescriptions' },
  identification: { ar: 'الهوية', en: 'Identification' },
  none: { ar: 'لا يوجد', en: 'None' },
  error: { ar: 'تعذر إكمال الطلب', en: 'The request could not be completed' },
} as const

export default function OwnerPetsPage() {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  const t = (k: keyof typeof L) => L[k][isAr ? 'ar' : 'en']

  const [pets, setPets] = useState<Pet[]>([])
  const [selected, setSelected] = useState<Detail | null>(null)
  const [failed, setFailed] = useState(false)
  const [prefs, setPrefs] = useState('')

  const load = useCallback(async () => {
    const r = await call('/api/pets')
    if (!r.ok) { setFailed(true); return }
    setPets(await r.json())
  }, [])

  useEffect(() => { void load() }, [load])

  async function open(petId: string) {
    const r = await call(`/api/pets/${petId}`)
    if (!r.ok) { setFailed(true); return }
    const d: Detail = await r.json()
    setSelected(d)
    setPrefs(d.profile.preferences ?? '')
  }

  async function create(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const f = new FormData(e.currentTarget)
    const str = (k: string) => { const v = String(f.get(k) ?? '').trim(); return v === '' ? null : v }
    const weight = str('weight_kg')
    const r = await call('/api/pets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: str('name'), species: str('species'), breed: str('breed'),
        birth_date: str('birth_date'), weight_kg: weight === null ? null : Number(weight),
        medical_conditions: str('medical_conditions'), allergies: str('allergies'),
        preferences: str('preferences'),
      }),
    })
    if (!r.ok) { setFailed(true); return }
    setFailed(false)
    await load()
  }

  async function savePrefs() {
    if (!selected) return
    const r = await call(`/api/pets/${selected.profile.pet_id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ preferences: prefs }),
    })
    if (!r.ok) { setFailed(true); return }
    await open(selected.profile.pet_id)
  }

  return (
    <main className="stack" dir={isAr ? 'rtl' : 'ltr'} lang={isAr ? 'ar' : 'en'}>
      <h1 className="title-lg">{t('title')}</h1>
      {failed && <p role="alert">{t('error')}</p>}

      {pets.length === 0 ? (
        <p>{t('empty')}</p>
      ) : (
        <ul aria-label={t('title')}>
          {pets.map(p => (
            <li key={p.pet_id}>
              <button type="button" onClick={() => void open(p.pet_id)}>{p.name} · {p.species}</button>
            </li>
          ))}
        </ul>
      )}

      {selected && (
        <section aria-label={selected.profile.name}>
          <h2>{selected.profile.name}</h2>
          <dl>
            <dt>{t('species')}</dt><dd>{selected.profile.species}</dd>
            <dt>{t('breed')}</dt><dd>{selected.profile.breed ?? t('none')}</dd>
            <dt>{t('birth')}</dt><dd>{selected.profile.birth_date ?? t('none')}</dd>
            <dt>{t('weight')}</dt><dd>{selected.profile.weight_kg ?? t('none')}</dd>
            <dt>{t('conditions')}</dt><dd>{selected.profile.medical_conditions ?? t('none')}</dd>
            <dt>{t('allergies')}</dt><dd>{selected.profile.allergies ?? t('none')}</dd>
          </dl>

          <h3>{t('identification')}</h3>
          {selected.identifications.length === 0 ? <p>{t('none')}</p> : (
            <ul>{selected.identifications.map(i => (
              <li key={i.identification_id}>{i.id_type}: {i.id_value} ({i.captured_at})</li>
            ))}</ul>
          )}

          <h3>{t('history')}</h3>
          <h4>{t('records')}</h4>
          {selected.medical_history.records.length === 0 ? <p>{t('none')}</p> : (
            <ul aria-label={t('records')}>{selected.medical_history.records.map(r => (
              <li key={r.record_id}>{r.title}{r.detail ? ` — ${r.detail}` : ''}</li>
            ))}</ul>
          )}
          <h4>{t('prescriptions')}</h4>
          {selected.medical_history.prescriptions.length === 0 ? <p>{t('none')}</p> : (
            <ul aria-label={t('prescriptions')}>{selected.medical_history.prescriptions.map(rx => (
              <li key={rx.prescription_id}>{rx.medication_name} {rx.dosage} · {rx.status}</li>
            ))}</ul>
          )}

          <label>
            {t('preferences')}
            <textarea value={prefs} onChange={e => setPrefs(e.target.value)} />
          </label>
          <button type="button" onClick={() => void savePrefs()}>{t('save')}</button>
        </section>
      )}

      <form onSubmit={e => void create(e)} aria-label={t('add')}>
        <h2>{t('add')}</h2>
        <label>{t('name')}<input name="name" required /></label>
        <label>{t('species')}<input name="species" required /></label>
        <label>{t('breed')}<input name="breed" /></label>
        <label>{t('birth')}<input name="birth_date" type="date" /></label>
        <label>{t('weight')}<input name="weight_kg" type="number" step="0.001" min="0" /></label>
        <label>{t('conditions')}<input name="medical_conditions" /></label>
        <label>{t('allergies')}<input name="allergies" /></label>
        <label>{t('preferences')}<input name="preferences" /></label>
        <button type="submit">{t('save')}</button>
      </form>
    </main>
  )
}
