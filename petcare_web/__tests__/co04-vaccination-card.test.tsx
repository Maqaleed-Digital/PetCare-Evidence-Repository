import { describe, it, expect, beforeEach, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import VaccinationCardPage from '@/app/owner/pets/[petId]/vaccination-card/page'

/**
 * CO-04 vaccination card (MVC-EPC-D-001 D2o, R21.4) — UI. Served behaviour: petcare_api/tests/test_epc_d2o_co04_vaccination_card.py.
 * The page shows exactly what the API recorded — vaccinations given (with the veterinarian) and due — in Arabic by default, and
 * its PDF is the browser's print engine (window.print), with no PDF provider.
 */
function json(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}
const CARD = {
  pet: { pet_id: 'p-1', name: 'لونا', species: 'قطة', breed: null, birth_date: '2023-04-01' },
  identifications: [{ id_type: 'MICROCHIP', id_value: '982000123456789' }],
  issued_on: '2031-03-03',
  given: [{ due_id: 'd-1', title: 'داء الكلب', given_on: '2031-03-03', given_by: 'د. سلمى' }],
  due: [{ due_id: 'd-2', title: 'جرعة معززة', due_on: '2031-04-10' }],
}

beforeEach(() => { vi.restoreAllMocks(); localStorage.clear() })

describe('CO-04 vaccination card', () => {
  it('shows the given and due vaccinations from the API, in Arabic with no untranslated copy', async () => {
    const fetchMock = vi.fn(() => json(CARD))
    vi.stubGlobal('fetch', fetchMock)
    render(<LangProvider><VaccinationCardPage params={{ petId: 'p-1' }} /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('vaccination-card')).toBeTruthy())
    expect(String((fetchMock.mock.calls[0] as unknown[])[0])).toMatch(/\/api\/pets\/p-1\/vaccination-card$/)
    const given = screen.getAllByTestId('vaccination-given')
    expect(given.map(g => g.getAttribute('data-given-on'))).toEqual(['2031-03-03'])
    expect(given[0].textContent).toContain('داء الكلب')
    expect(given[0].textContent).toContain('د. سلمى')
    expect(screen.getAllByTestId('vaccination-due').map(d => d.getAttribute('data-due-on'))).toEqual(['2031-04-10'])
    // Latin appears only inside machine values marked translate="no" (the microchip type/number)
    const main = document.querySelector('main') as HTMLElement
    const copy = main.cloneNode(true) as HTMLElement
    copy.querySelectorAll('[translate="no"], style').forEach(n => n.remove())
    expect(copy.textContent).not.toMatch(/[A-Za-z]/)
  })

  it('states none for an empty card and saves the PDF through the browser print engine', async () => {
    vi.stubGlobal('fetch', vi.fn(() => json({ ...CARD, given: [], due: [] })))
    const print = vi.fn()
    vi.stubGlobal('print', print)
    render(<LangProvider><VaccinationCardPage params={{ petId: 'p-1' }} /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('vaccinations-given-none')).toBeTruthy())
    expect(screen.getByTestId('vaccinations-due-none')).toBeTruthy()
    fireEvent.click(screen.getByTestId('vaccination-card-print'))
    expect(print).toHaveBeenCalledTimes(1)
  })

  it('shows an alert and no card when the pet is not the owner\'s (404)', async () => {
    vi.stubGlobal('fetch', vi.fn(() => json({ detail: 'Pet not found' }, 404)))
    render(<LangProvider><VaccinationCardPage params={{ petId: 'p-x' }} /></LangProvider>)
    await waitFor(() => expect(screen.getByRole('alert')).toBeTruthy())
    expect(screen.queryByTestId('vaccination-card')).toBeNull()
    expect(screen.queryByTestId('vaccination-card-print')).toBeNull()
  })

  it('renders English labels when the owner chose English', async () => {
    localStorage.setItem('vc_lang', 'en')
    vi.stubGlobal('fetch', vi.fn(() => json(CARD)))
    render(<LangProvider><VaccinationCardPage params={{ petId: 'p-1' }} /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('vaccination-card')).toBeTruthy())
    expect(screen.getByRole('heading', { level: 1 }).textContent).toBe('Vaccination card')
    expect(screen.getByTestId('vaccination-card-print').textContent).toBe('Save as PDF or print')
  })
})
