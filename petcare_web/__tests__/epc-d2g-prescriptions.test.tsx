/**
 * MVC-EPC-D-001 D2g — CO-11 prescriptions + upload (J-O7). Shows what the server serves (issued prescriptions for the
 * owner's pets, their own uploads awaiting verification) and posts only the pet selector, the file and a note — never an
 * owner, tenant or actor. Linked from the owner home.
 */
import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { LangProvider } from '@/components/LangProvider'
import PrescriptionsPage from '@/app/owner/prescriptions/page'
import OwnerPage from '@/app/owner/page'

type Call = [string, RequestInit | undefined]
const calls = () => (fetch as unknown as { mock: { calls: Call[] } }).mock.calls
const BODY = {
  prescriptions: [{ prescription_id: 'rx1', pet_id: 'p1', medication_name: 'Amoxicillin', dosage: '50mg', instructions: 'مرتين يومياً',
    status: 'ISSUED', issued_at: '2031-03-09T22:30:00Z' }],
  uploads: [{ upload_id: 'u1', pet_id: 'p1', filename: 'rx.png', note: '', status: 'AWAITING_VERIFICATION', uploaded_at: '2031-03-09T22:30:00Z' }],
}

function serve() {
  vi.stubGlobal('fetch', vi.fn((url: string, init?: RequestInit) => {
    const path = new URL(url, 'http://x').pathname
    if (init?.method === 'POST') return Promise.resolve(new Response(JSON.stringify({ upload_id: 'u2' }), { status: 201 }))
    const r = path === '/api/owner/prescriptions' ? BODY : [{ pet_id: 'p1', name: 'لونا' }]
    return Promise.resolve(new Response(JSON.stringify(r), { status: 200 }))
  }))
}
afterEach(() => vi.unstubAllGlobals())

describe('CO-11 prescriptions + upload (D2g, J-O7)', () => {
  it('shows the served prescriptions and uploads with their status', async () => {
    serve()
    render(<LangProvider><PrescriptionsPage /></LangProvider>)
    expect(await screen.findByText(/Amoxicillin/)).toHaveTextContent('Amoxicillin · 50mg')
    expect(screen.getByTestId('owner-prescription')).toHaveAttribute('data-status', 'ISSUED')
    expect(screen.getByTestId('owner-upload')).toHaveAttribute('data-status', 'AWAITING_VERIFICATION')
    expect(screen.getByText('بانتظار تحقق الطبيب البيطري')).toBeInTheDocument()
    expect(screen.getByTestId('owner-upload-download').getAttribute('href')).toMatch(/\/api\/owner\/prescriptions\/uploads\/u1\/document$/)
    expect(screen.getByTestId('prescription-timeline')).toHaveAttribute('href', '/owner/pets')
  })

  it('posts only the pet selector, the file and the note', async () => {
    serve()
    render(<LangProvider><PrescriptionsPage /></LangProvider>)
    await screen.findByText(/Amoxicillin/)
    await userEvent.upload(screen.getByTestId('upload-file'), new File(['%PNG-test'], 'rx2.png', { type: 'image/png' }))
    fireEvent.submit(screen.getByTestId('upload-form'))
    await vi.waitFor(() => expect(calls().some(([, i]) => i?.method === 'POST')).toBe(true))
    const [url, init] = calls().find(([, i]) => i?.method === 'POST') as Call
    expect(url).toMatch(/\/api\/owner\/prescriptions\/uploads$/)
    const form = init?.body as FormData
    expect([...form.keys()].sort()).toEqual(['file', 'note', 'pet_id'])
    expect(form.get('pet_id')).toBe('p1')
    expect(init?.credentials).toBe('include')
  })

  it('is linked from the owner home', () => {
    vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {})))
    render(<LangProvider><OwnerPage /></LangProvider>)
    expect(screen.getByTestId('owner-open-prescriptions')).toHaveAttribute('href', '/owner/prescriptions')
  })
})
