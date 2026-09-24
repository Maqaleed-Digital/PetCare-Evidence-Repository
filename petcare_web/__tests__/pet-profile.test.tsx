import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LangProvider } from '@/components/LangProvider'
import OwnerPetsPage from '@/app/owner/pets/page'

/**
 * FR-02 pet profile page (MVC-BUILD-RUNNER-001 U2) — ratified criteria
 * AC-FR-02-01 (UI: create and view the BRD fields) and AC-FR-02-02
 * (UI + ARABIC_RTL: medical history and preferences; Arabic default, RTL).
 *
 * `fetch` is stubbed: this is a component test. The URLs are the served app's
 * real routes, exercised end to end in petcare_api/tests/test_pet_profile.py.
 */

const PET = {
  pet_id: 'pet-1', name: 'Luna', species: 'cat', breed: 'Siamese', birth_date: '2021-04-02',
  weight_kg: 4.2, medical_conditions: 'asthma', allergies: 'penicillin', preferences: 'SMS',
}
const DETAIL = {
  profile: PET,
  identifications: [{ identification_id: 'i-1', id_type: 'MICROCHIP', id_value: '982000123456789', captured_at: '2024-02-01' }],
  medical_history: {
    records: [{ record_id: 'r-1', record_type: 'LAB_RESULT', title: 'CBC', detail: 'within range' }],
    prescriptions: [{ prescription_id: 'rx-1', medication_name: 'Amoxicillin', dosage: '50mg', status: 'ISSUED' }],
  },
}

function json(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}

function mount() {
  return render(<LangProvider><OwnerPetsPage /></LangProvider>)
}

beforeEach(() => {
  vi.restoreAllMocks()
  localStorage.clear()
})

describe('Owner pet profiles — real backend routes', () => {
  it('renders Arabic by default, right-to-left', async () => {
    vi.stubGlobal('fetch', vi.fn(() => json([])))
    const { container } = mount()
    await waitFor(() => expect(screen.getByText('لا توجد حيوانات مسجلة بعد.')).toBeInTheDocument())
    expect(container.querySelector('main')?.getAttribute('dir')).toBe('rtl')
    expect(screen.getByRole('heading', { level: 1 }).textContent).toBe('حيواناتي الأليفة')
  })

  it('shows every BRD profile field, identification and medical history from the API', async () => {
    const fetchMock = vi.fn((url: string) => String(url).endsWith('/api/pets') ? json([PET]) : json(DETAIL))
    vi.stubGlobal('fetch', fetchMock)
    mount()
    const user = userEvent.setup()
    await user.click(await screen.findByRole('button', { name: /Luna/ }))
    const section = await screen.findByRole('region', { name: 'Luna' })
    for (const v of ['cat', 'Siamese', '2021-04-02', '4.2', 'asthma', 'penicillin']) {
      expect(within(section).getByText(v)).toBeInTheDocument()
    }
    expect(within(section).getByText(/982000123456789/)).toBeInTheDocument()
    expect(within(section).getByText(/CBC — within range/)).toBeInTheDocument()
    expect(within(section).getByText(/Amoxicillin 50mg/)).toBeInTheDocument()
    expect(fetchMock.mock.calls.some(([u]) => String(u).endsWith('/api/pets/pet-1'))).toBe(true)
  })

  it('stores preferences through PATCH /api/pets/{id}', async () => {
    const calls: { url: string; init?: RequestInit }[] = []
    vi.stubGlobal('fetch', vi.fn((url: string, init?: RequestInit) => {
      calls.push({ url: String(url), init })
      return String(url).endsWith('/api/pets') ? json([PET]) : json(DETAIL)
    }))
    mount()
    const user = userEvent.setup()
    await user.click(await screen.findByRole('button', { name: /Luna/ }))
    const section = await screen.findByRole('region', { name: 'Luna' })
    const box = within(section).getByRole('textbox', { name: /التفضيلات/ })
    await user.clear(box)
    await user.type(box, 'email only')
    await user.click(within(section).getByRole('button', { name: 'حفظ' }))
    await waitFor(() => expect(calls.some(c => c.init?.method === 'PATCH')).toBe(true))
    const patch = calls.find(c => c.init?.method === 'PATCH')!
    expect(patch.url.endsWith('/api/pets/pet-1')).toBe(true)
    expect(JSON.parse(String(patch.init!.body))).toEqual({ preferences: 'email only' })
  })

  it('creates with the BRD fields and sends no actor, owner or tenant', async () => {
    const calls: { url: string; init?: RequestInit }[] = []
    vi.stubGlobal('fetch', vi.fn((url: string, init?: RequestInit) => {
      calls.push({ url: String(url), init })
      return json(init?.method === 'POST' ? PET : [])
    }))
    mount()
    const user = userEvent.setup()
    const form = await screen.findByRole('form', { name: 'إضافة حيوان' })
    await user.type(within(form).getByLabelText('الاسم'), 'Luna')
    await user.type(within(form).getByLabelText('النوع'), 'cat')
    await user.type(within(form).getByLabelText('الحساسية'), 'penicillin')
    await user.click(within(form).getByRole('button', { name: 'حفظ' }))
    await waitFor(() => expect(calls.some(c => c.init?.method === 'POST')).toBe(true))
    const body = JSON.parse(String(calls.find(c => c.init?.method === 'POST')!.init!.body))
    expect(body).toMatchObject({ name: 'Luna', species: 'cat', allergies: 'penicillin' })
    for (const k of ['tenant_id', 'owner_id', 'actor_id']) expect(k in body).toBe(false)
    const headers = (calls.find(c => c.init?.method === 'POST')!.init!.headers ?? {}) as Record<string, string>
    expect(Object.keys(headers).map(h => h.toLowerCase())).not.toContain('x-actor-id')
  })
})
