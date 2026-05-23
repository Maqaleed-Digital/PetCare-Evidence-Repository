/**
 * lib/triage.ts — Companion-animal red-flag triage table (display-only).
 *
 * MVC-UX-WO-001 WI-3 emergency-access BASELINE.
 *
 * Source rules: petcare-platform/app/backend/services/escalation_engine.py
 * (companion-animal scope: dog / cat / bird / all). Ported as a pure client-
 * side TypeScript module to keep the FR-11 vet-queue boundary auditable by
 * construction — this module performs NO routing, NO dispatch, NO scheduling,
 * NO POST to a backend. It maps symptom IDs to severity + a localised display
 * message. The licensed veterinarian remains the clinical decision authority.
 *
 * Companion-animal scope ONLY. No livestock rules.
 */

export type Species = 'dog' | 'cat' | 'bird'
export type Severity = 'critical' | 'urgent' | 'routine'

export const RED_FLAG_RULES: Record<Species | 'all', readonly string[]> = {
  dog: [
    'breathing_difficulty',
    'seizure',
    'collapse',
    'severe_bleeding',
    'suspected_poisoning',
    'eye_injury',
    'difficulty_urinating',
  ],
  cat: [
    'open_mouth_breathing',
    'urinary_blockage',
    'prolonged_seizure',
    'suspected_toxin',
    'severe_lethargy',
    'rapid_weight_loss',
  ],
  bird: [
    'laboured_breathing',
    'fluffed_feathers_unresponsive',
    'bleeding',
  ],
  all: [
    'loss_of_consciousness',
    'suspected_trauma',
    'extreme_pain',
  ],
} as const

export const SEVERITY_MAP: Record<string, Severity> = {
  breathing_difficulty:           'critical',
  open_mouth_breathing:           'critical',
  urinary_blockage:               'critical',
  seizure:                        'critical',
  collapse:                       'critical',
  suspected_poisoning:            'critical',
  loss_of_consciousness:          'critical',
  severe_bleeding:                'critical',
  extreme_pain:                   'critical',
  prolonged_seizure:              'urgent',
  suspected_toxin:                'urgent',
  severe_lethargy:                'urgent',
  rapid_weight_loss:              'urgent',
  difficulty_urinating:           'urgent',
  eye_injury:                     'urgent',
  laboured_breathing:             'urgent',
  fluffed_feathers_unresponsive:  'urgent',
  bleeding:                       'urgent',
  suspected_trauma:               'urgent',
}

export const SYMPTOM_LABELS: Record<string, { ar: string; en: string }> = {
  breathing_difficulty:           { ar: 'صعوبة في التنفس',                  en: 'Difficulty breathing' },
  open_mouth_breathing:           { ar: 'التنفس بفم مفتوح',                en: 'Open-mouth breathing' },
  urinary_blockage:               { ar: 'انسداد بولي',                       en: 'Urinary blockage' },
  seizure:                        { ar: 'نوبة صرع',                           en: 'Seizure' },
  collapse:                       { ar: 'انهيار / فقدان توازن',             en: 'Collapse' },
  suspected_poisoning:            { ar: 'اشتباه تسمم',                       en: 'Suspected poisoning' },
  loss_of_consciousness:          { ar: 'فقدان الوعي',                       en: 'Loss of consciousness' },
  severe_bleeding:                { ar: 'نزيف شديد',                          en: 'Severe bleeding' },
  extreme_pain:                   { ar: 'ألم شديد',                            en: 'Extreme pain' },
  prolonged_seizure:              { ar: 'نوبة طويلة',                        en: 'Prolonged seizure' },
  suspected_toxin:                { ar: 'اشتباه تعرّض لمادة سامة',          en: 'Suspected toxin exposure' },
  severe_lethargy:                { ar: 'خمول شديد',                          en: 'Severe lethargy' },
  rapid_weight_loss:              { ar: 'فقدان وزن سريع',                    en: 'Rapid weight loss' },
  difficulty_urinating:           { ar: 'صعوبة في التبول',                  en: 'Difficulty urinating' },
  eye_injury:                     { ar: 'إصابة في العين',                    en: 'Eye injury' },
  laboured_breathing:             { ar: 'تنفس مجهد',                          en: 'Laboured breathing' },
  fluffed_feathers_unresponsive:  { ar: 'ريش منفوش وعدم استجابة',           en: 'Fluffed feathers / unresponsive' },
  bleeding:                       { ar: 'نزيف',                               en: 'Bleeding' },
  suspected_trauma:               { ar: 'اشتباه صدمة',                       en: 'Suspected trauma' },
}

export interface TriageResult {
  severity: Severity
  triggered: readonly string[]
}

/**
 * Pure function — given a species and selected symptoms, return the
 * highest-severity red flag triggered. No I/O, no network, no persistence.
 */
export function evaluateTriage(species: Species, symptoms: readonly string[]): TriageResult {
  const speciesRules = new Set<string>([
    ...RED_FLAG_RULES[species],
    ...RED_FLAG_RULES.all,
  ])
  const triggered = symptoms.filter(s => speciesRules.has(s))

  if (triggered.length === 0) {
    return { severity: 'routine', triggered: [] }
  }

  const hasCritical = triggered.some(s => SEVERITY_MAP[s] === 'critical')
  return {
    severity: hasCritical ? 'critical' : 'urgent',
    triggered,
  }
}

/** Symptom IDs applicable for a given species (species rules + universal rules). */
export function symptomsForSpecies(species: Species): readonly string[] {
  return [...RED_FLAG_RULES[species], ...RED_FLAG_RULES.all]
}
