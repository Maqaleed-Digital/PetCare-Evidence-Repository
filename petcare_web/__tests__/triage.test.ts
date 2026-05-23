import { describe, it, expect } from 'vitest'
import {
  evaluateTriage,
  symptomsForSpecies,
  RED_FLAG_RULES,
} from '@/lib/triage'

describe('lib/triage — companion-animal red-flag table (WI-3)', () => {
  it('returns critical for a dog with seizure', () => {
    expect(evaluateTriage('dog', ['seizure'])).toEqual({
      severity: 'critical', triggered: ['seizure'],
    })
  })

  it('returns critical for a cat with urinary_blockage', () => {
    expect(evaluateTriage('cat', ['urinary_blockage'])).toEqual({
      severity: 'critical', triggered: ['urinary_blockage'],
    })
  })

  it('returns critical for any species with a universal rule (loss_of_consciousness)', () => {
    expect(evaluateTriage('dog', ['loss_of_consciousness']).severity).toBe('critical')
    expect(evaluateTriage('bird', ['loss_of_consciousness']).severity).toBe('critical')
  })

  it('returns urgent for a bird with bleeding', () => {
    expect(evaluateTriage('bird', ['bleeding']).severity).toBe('urgent')
  })

  it('returns routine when no symptoms are selected', () => {
    expect(evaluateTriage('dog', [])).toEqual({ severity: 'routine', triggered: [] })
  })

  it('ignores symptoms that do not apply to the species (eye_injury is dog-only)', () => {
    expect(evaluateTriage('cat', ['eye_injury'])).toEqual({
      severity: 'routine', triggered: [],
    })
  })

  it('escalates to critical when both critical and urgent symptoms are present', () => {
    const r = evaluateTriage('dog', ['eye_injury', 'severe_bleeding'])
    expect(r.severity).toBe('critical')
    expect(r.triggered).toContain('severe_bleeding')
    expect(r.triggered).toContain('eye_injury')
  })

  it('symptomsForSpecies returns species + universal rules', () => {
    const dog = symptomsForSpecies('dog')
    expect(dog).toEqual(expect.arrayContaining([...RED_FLAG_RULES.dog]))
    expect(dog).toEqual(expect.arrayContaining([...RED_FLAG_RULES.all]))
  })

  it('does not include any livestock species in the rule table', () => {
    // Companion-animal scope only — explicit guard against scope creep.
    expect(Object.keys(RED_FLAG_RULES).sort()).toEqual(['all', 'bird', 'cat', 'dog'])
  })
})
