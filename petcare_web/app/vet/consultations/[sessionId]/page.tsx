'use client'

/**
 * J-V3 — CV-05 consultation workspace with SOAP templates (MVC-EPC-D-001 D3c, R21.4).
 *
 * The veterinarian's workspace for one of their OWN consultations, as the server holds it
 * (GET /api/vet/consultations/{id}/workspace): the patient and owner, the SOAP draft in force and the structural templates.
 * A template fills only the sections that are still empty — it never overwrites what the veterinarian wrote — and carries
 * headings only. Saving makes a new draft version (PUT …/soap); the draft is UNSIGNED: signing a note is journey J-V4 and is
 * not offered here. The visit is completed by recording its outcome (POST /api/consultations/{id}/outcome, FR-06), after which
 * it leaves the queue. Remote video is not offered until REG-02 is recorded, and no video control is shown. Arabic by default.
 */

import { FormEvent, useCallback, useEffect, useState } from 'react'
import { useLang } from '@/components/LangProvider'
import { formatKsa } from '@/lib/ksaTime'
import { applyTemplate, EMPTY_SOAP, SECTIONS, type SoapSections, type SoapTemplate } from '@/lib/soapTemplates'

type Draft = SoapSections & { draft_id: string; status: string; template_id: string | null; saved_at: string }
type Workspace = {
  consultation: { session_id: string; mode: string; status: string; created_at: string; outcome: { outcome: string } | null }
  pet: { name: string; species: string; breed: string | null } | null
  owner_name: string | null
  soap: Draft | null
  soap_versions: number
  templates: SoapTemplate[]
  remote: { offered: boolean }
}

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')

const L = {
  title: { ar: 'مساحة عمل الاستشارة', en: 'Consultation workspace' },
  patient: { ar: 'المريض', en: 'Patient' },
  owner: { ar: 'المالك', en: 'Owner' },
  visit: { ar: 'الزيارة', en: 'Visit' },
  inPerson: { ar: 'حضورية', en: 'In person' },
  video: { ar: 'مرئية', en: 'Video' },
  REQUESTED: { ar: 'قيد العمل', en: 'In progress' },
  COMPLETED: { ar: 'مكتملة', en: 'Completed' },
  remoteOff: { ar: 'الاستشارة المرئية غير متاحة إلى حين صدور الرأي القانوني المعتمد بشأن الطب البيطري عن بُعد.', en: 'Video consultation is not offered until the telemedicine counsel determination is recorded.' },
  note: { ar: 'الملاحظة السريرية', en: 'Clinical note' },
  template: { ar: 'القالب', en: 'Template' },
  chooseTemplate: { ar: 'اختر قالباً', en: 'Choose a template' },
  applyTemplate: { ar: 'تطبيق القالب على الأقسام الفارغة', en: 'Apply to empty sections' },
  subjective: { ar: 'الشكوى والتاريخ', en: 'Subjective' },
  objective: { ar: 'الفحص', en: 'Objective' },
  assessment: { ar: 'التقييم', en: 'Assessment' },
  plan: { ar: 'الخطة', en: 'Plan' },
  save: { ar: 'حفظ المسودة', en: 'Save draft' },
  draft: { ar: 'مسودة غير موقّعة', en: 'Unsigned draft' },
  noDraft: { ar: 'لا توجد مسودة محفوظة بعد.', en: 'No draft saved yet.' },
  savedAt: { ar: 'آخر حفظ', en: 'Last saved' },
  saved: { ar: 'حُفظت المسودة.', en: 'Draft saved.' },
  invalid: { ar: 'تعذر حفظ المسودة: اكتب قسماً واحداً على الأقل.', en: 'The draft could not be saved: write at least one section.' },
  outcome: { ar: 'نتيجة الزيارة', en: 'Visit outcome' },
  recordOutcome: { ar: 'تسجيل النتيجة وإكمال الزيارة', en: 'Record outcome and complete the visit' },
  outcomeFailed: { ar: 'تعذر تسجيل النتيجة.', en: 'The outcome could not be recorded.' },
  notFound: { ar: 'لا توجد هذه الاستشارة ضمن استشاراتك.', en: 'This consultation is not one of yours.' },
  failed: { ar: 'تعذر عرض مساحة العمل.', en: 'The workspace could not be shown.' },
  back: { ar: 'العودة إلى قائمة العمل', en: 'Back to the queue' },
} as const

export default function ConsultationWorkspacePage({ params }: { params: { sessionId: string } }) {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  const l = isAr ? 'ar' : 'en'
  const t = (k: keyof typeof L) => L[k][l]
  const sid = encodeURIComponent(params.sessionId)
  const [ws, setWs] = useState<Workspace | null>(null)
  const [state, setState] = useState<'loading' | 'ready' | 'notFound' | 'failed'>('loading')
  const [note, setNote] = useState<SoapSections>(EMPTY_SOAP)
  const [templateId, setTemplateId] = useState<string>('')
  const [saveState, setSaveState] = useState<'idle' | 'saved' | 'invalid'>('idle')
  const [outcome, setOutcome] = useState('')
  const [outcomeFailed, setOutcomeFailed] = useState(false)

  const load = useCallback(async () => {
    const r = await fetch(`${apiBase}/api/vet/consultations/${sid}/workspace`, { credentials: 'include', cache: 'no-store' })
    if (r.status === 404) { setState('notFound'); return }
    if (!r.ok) { setState('failed'); return }
    const w: Workspace = await r.json()
    setWs(w)
    setNote(w.soap ? { subjective: w.soap.subjective, objective: w.soap.objective, assessment: w.soap.assessment, plan: w.soap.plan } : EMPTY_SOAP)
    setTemplateId(w.soap?.template_id ?? '')
    setState('ready')
  }, [sid])
  useEffect(() => { void load() }, [load])

  async function save(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const r = await fetch(`${apiBase}/api/vet/consultations/${sid}/soap`, { method: 'PUT', credentials: 'include',
      headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ template_id: templateId || null, ...note }) })
    if (!r.ok) { setSaveState('invalid'); return }
    setSaveState('saved')
    await load()
  }

  async function complete(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const r = await fetch(`${apiBase}/api/consultations/${sid}/outcome`, { method: 'POST', credentials: 'include',
      headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ outcome }) })
    if (!r.ok) { setOutcomeFailed(true); return }
    setOutcomeFailed(false)
    await load()
  }

  const tpl = ws?.templates.find(x => x.template_id === templateId)
  const c = ws?.consultation

  return (
    <main className="stack" dir={isAr ? 'rtl' : 'ltr'} lang={l} data-testid="vet-workspace">
      <h1 className="title-lg">{t('title')}</h1>
      <a className="button button-outline button-sm" href="/vet/queue" data-testid="workspace-back">{t('back')}</a>
      {state === 'failed' && <p role="alert">{t('failed')}</p>}
      {state === 'notFound' && <p role="alert" data-testid="workspace-not-found">{t('notFound')}</p>}

      {state === 'ready' && ws && c && (
        <>
          <dl data-testid="workspace-header" data-status={c.status}>
            <dt>{t('patient')}</dt>
            <dd data-testid="workspace-pet">{ws.pet ? `${ws.pet.name} · ${ws.pet.species}${ws.pet.breed ? ` · ${ws.pet.breed}` : ''}` : ''}</dd>
            <dt>{t('owner')}</dt><dd data-testid="workspace-owner">{ws.owner_name ?? ''}</dd>
            <dt>{t('visit')}</dt>
            <dd>{formatKsa(c.created_at, lang, { dateStyle: 'medium', timeStyle: 'short' })} · {t(c.mode === 'REMOTE_VIDEO' ? 'video' : 'inPerson')} · <span data-testid="workspace-status">{t(c.status === 'COMPLETED' ? 'COMPLETED' : 'REQUESTED')}</span></dd>
          </dl>
          {!ws.remote.offered && c.mode === 'REMOTE_VIDEO' && <p role="status">{t('remoteOff')}</p>}

          <form onSubmit={e => void save(e)} data-testid="soap-form" className="stack">
            <h2>{t('note')}</h2>
            <p data-testid="soap-draft-status" data-status={ws.soap ? 'DRAFT' : 'NONE'} data-versions={ws.soap_versions}>
              {ws.soap ? `${t('draft')} · ${t('savedAt')}: ${formatKsa(ws.soap.saved_at, lang, { dateStyle: 'medium', timeStyle: 'short' })}` : t('noDraft')}
            </p>
            <label>{t('template')}{' '}
              <select name="template" data-testid="soap-template" value={templateId} onChange={e => setTemplateId(e.target.value)}>
                <option value="">{t('chooseTemplate')}</option>
                {ws.templates.map(x => <option key={x.template_id} value={x.template_id}>{x.name[l]}</option>)}
              </select>
            </label>
            <button type="button" className="button button-outline button-sm" data-testid="soap-apply-template" disabled={!tpl}
              onClick={() => { if (tpl) setNote(n => applyTemplate(n, tpl, l)) }}>{t('applyTemplate')}</button>
            {SECTIONS.map(s => (
              <label key={s}>{t(s)}
                <textarea name={s} data-testid={`soap-${s}`} rows={4} value={note[s]}
                  onChange={e => { const v = e.target.value; setNote(n => ({ ...n, [s]: v })) }} />
              </label>
            ))}
            {saveState === 'saved' && <p role="status" data-testid="soap-saved">{t('saved')}</p>}
            {saveState === 'invalid' && <p role="alert" data-testid="soap-invalid">{t('invalid')}</p>}
            <button type="submit" className="button" data-testid="soap-save">{t('save')}</button>
          </form>

          {c.status === 'COMPLETED' && c.outcome ? (
            <section><h2>{t('outcome')}</h2><p data-testid="workspace-outcome">{c.outcome.outcome}</p></section>
          ) : (
            <form onSubmit={e => void complete(e)} data-testid="outcome-form" className="stack">
              <h2>{t('outcome')}</h2>
              <textarea name="outcome" data-testid="outcome-text" rows={3} required value={outcome} onChange={e => setOutcome(e.target.value)} />
              {outcomeFailed && <p role="alert" data-testid="outcome-failed">{t('outcomeFailed')}</p>}
              <button type="submit" className="button" data-testid="outcome-record">{t('recordOutcome')}</button>
            </form>
          )}
        </>
      )}
    </main>
  )
}
