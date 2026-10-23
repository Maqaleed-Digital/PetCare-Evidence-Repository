/**
 * J-V3 (MVC-EPC-D-001 D3c) — SOAP sections and the template rule of the consultation workspace (CV-05).
 * Templates are structural (headings only, served by the API). Applying one fills ONLY the sections still empty: what the
 * veterinarian has written is never replaced.
 */
export type Section = 'subjective' | 'objective' | 'assessment' | 'plan'
export type Lang2 = { ar: string; en: string }
export type SoapTemplate = { template_id: string; name: Lang2; sections: Record<Section, Lang2> }
export type SoapSections = Record<Section, string>

export const SECTIONS: Section[] = ['subjective', 'objective', 'assessment', 'plan']
export const EMPTY_SOAP: SoapSections = { subjective: '', objective: '', assessment: '', plan: '' }

export function applyTemplate(current: SoapSections, tpl: SoapTemplate, lang: 'ar' | 'en'): SoapSections {
  return Object.fromEntries(SECTIONS.map(s => [s, current[s].trim() ? current[s] : tpl.sections[s][lang]])) as SoapSections
}
