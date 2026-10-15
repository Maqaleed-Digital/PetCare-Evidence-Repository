'use client'

/**
 * CO-04 — vaccination card (PDF) (MVC-EPC-D-001 D2o, R21.4).
 *
 * Everything shown comes from GET /api/pets/{pet_id}/vaccination-card: the pet's identity, the vaccinations GIVEN (the
 * completion a veterinarian recorded, with their name and the Asia/Riyadh date) and the vaccinations DUE. Nothing is inferred:
 * an overdue vaccination is still due. The PDF is the browser's own print engine ("Save as PDF") over this page; print styles
 * drop the site chrome and the action buttons. No PDF service or provider is involved. Arabic by default, right-to-left.
 */

import { useCallback, useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'
import { formatKsa } from '@/lib/ksaTime'

type Given = { due_id: string; title: string; given_on: string; given_by: string | null }
type Due = { due_id: string; title: string; due_on: string }
type Card = {
  pet: { pet_id: string; name: string; species: string; breed: string | null; birth_date: string | null }
  identifications: { id_type: string; id_value: string }[]
  issued_on: string
  given: Given[]
  due: Due[]
}

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')

const L = {
  title: { ar: 'بطاقة التطعيمات', en: 'Vaccination card' },
  species: { ar: 'النوع', en: 'Species' },
  breed: { ar: 'السلالة', en: 'Breed' },
  birth: { ar: 'تاريخ الميلاد', en: 'Birth date' },
  identification: { ar: 'الهوية', en: 'Identification' },
  given: { ar: 'التطعيمات المُعطاة', en: 'Vaccinations given' },
  due: { ar: 'التطعيمات المستحقة', en: 'Vaccinations due' },
  vaccine: { ar: 'التطعيم', en: 'Vaccine' },
  givenOn: { ar: 'تاريخ الإعطاء', en: 'Given on' },
  givenBy: { ar: 'الطبيب البيطري', en: 'Veterinarian' },
  dueOn: { ar: 'تاريخ الاستحقاق', en: 'Due on' },
  issued: { ar: 'تاريخ إصدار البطاقة', en: 'Card issued on' },
  none: { ar: 'لا يوجد', en: 'None' },
  print: { ar: 'حفظ البطاقة كملف أو طباعتها', en: 'Save as PDF or print' },
  back: { ar: 'العودة إلى حيواناتي', en: 'Back to my pets' },
  notFound: { ar: 'تعذر عرض بطاقة التطعيمات', en: 'The vaccination card could not be shown' },
} as const

export default function VaccinationCardPage({ params }: { params: { petId: string } }) {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  const t = (k: keyof typeof L) => L[k][isAr ? 'ar' : 'en']
  // A recorded KSA calendar date, shown on the Riyadh clock at that day's noon (never shifted by the viewer's zone).
  const day = (d: string) => formatKsa(`${d}T12:00:00+03:00`, lang, { dateStyle: 'medium' })

  const [card, setCard] = useState<Card | null>(null)
  const [failed, setFailed] = useState(false)

  const load = useCallback(async () => {
    const r = await fetch(`${apiBase}/api/pets/${encodeURIComponent(params.petId)}/vaccination-card`,
      { credentials: 'include', cache: 'no-store' })
    if (!r.ok) { setFailed(true); return }
    setCard(await r.json())
  }, [params.petId])

  useEffect(() => { void load() }, [load])

  return (
    <main className="stack vaccination-card" dir={isAr ? 'rtl' : 'ltr'} lang={isAr ? 'ar' : 'en'}>
      <style>{`@media print {
        body > *:not(main), header, nav, footer, .no-print { display: none !important; }
        .vaccination-card { margin: 0; }
        .vaccination-card table { width: 100%; border-collapse: collapse; }
        .vaccination-card th, .vaccination-card td { border: 1px solid #000; padding: 4px; }
      }`}</style>
      <h1 className="title-lg">{t('title')}</h1>
      {failed && <p role="alert">{t('notFound')}</p>}

      {card && (
        <article data-testid="vaccination-card" aria-label={t('title')}>
          <h2 translate="no">{card.pet.name}</h2>
          <dl>
            <dt>{t('species')}</dt><dd translate="no">{card.pet.species}</dd>
            <dt>{t('breed')}</dt><dd translate="no">{card.pet.breed ?? t('none')}</dd>
            <dt>{t('birth')}</dt><dd>{card.pet.birth_date ? day(card.pet.birth_date) : t('none')}</dd>
            <dt>{t('identification')}</dt>
            <dd translate="no">{card.identifications.length === 0 ? t('none')
              : card.identifications.map(i => `${i.id_type}: ${i.id_value}`).join(' · ')}</dd>
          </dl>

          <h3>{t('given')}</h3>
          {card.given.length === 0 ? <p data-testid="vaccinations-given-none">{t('none')}</p> : (
            <table data-testid="vaccinations-given">
              <thead><tr><th>{t('vaccine')}</th><th>{t('givenOn')}</th><th>{t('givenBy')}</th></tr></thead>
              <tbody>{card.given.map(g => (
                <tr key={g.due_id} data-testid="vaccination-given" data-given-on={g.given_on}>
                  <td translate="no">{g.title}</td><td>{day(g.given_on)}</td><td translate="no">{g.given_by ?? t('none')}</td>
                </tr>
              ))}</tbody>
            </table>
          )}

          <h3>{t('due')}</h3>
          {card.due.length === 0 ? <p data-testid="vaccinations-due-none">{t('none')}</p> : (
            <table data-testid="vaccinations-due">
              <thead><tr><th>{t('vaccine')}</th><th>{t('dueOn')}</th></tr></thead>
              <tbody>{card.due.map(d => (
                <tr key={d.due_id} data-testid="vaccination-due" data-due-on={d.due_on}>
                  <td translate="no">{d.title}</td><td>{day(d.due_on)}</td>
                </tr>
              ))}</tbody>
            </table>
          )}

          <p><small>{t('issued')}: {day(card.issued_on)}</small></p>
        </article>
      )}

      <div className="no-print cluster">
        {card && (
          <button type="button" className="button" data-testid="vaccination-card-print" onClick={() => window.print()}>
            {t('print')}
          </button>
        )}
        <a className="button button-outline" href="/owner/pets">{t('back')}</a>
      </div>
    </main>
  )
}
