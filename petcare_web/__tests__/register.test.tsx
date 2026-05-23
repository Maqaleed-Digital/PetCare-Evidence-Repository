import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LangProvider } from '@/components/LangProvider'
import RegisterPage from '@/app/register/page'

const replaceMock = vi.fn()

vi.mock('next/navigation', () => ({
  useRouter: () => ({ replace: replaceMock, push: vi.fn() }),
}))

function renderRegister() {
  return render(
    <LangProvider>
      <RegisterPage />
    </LangProvider>
  )
}

async function fillAndSubmit(opts?: { role?: string }) {
  const user = userEvent.setup()
  await user.type(screen.getByLabelText(/الاسم الكامل/), 'Test Owner')
  await user.type(screen.getByLabelText(/البريد الإلكتروني/), 'owner@test.com')
  await user.type(screen.getByLabelText(/رمز الدعوة/), 'OWNER-PILOT-001')
  if (opts?.role === 'veterinarian') {
    await user.selectOptions(screen.getByLabelText(/نوع الحساب/), 'veterinarian')
  }
  await user.type(screen.getByLabelText(/كلمة المرور/), 'Pilot2026!')
  await user.click(screen.getByRole('button', { name: /إنشاء الحساب/ }))
}

beforeEach(() => {
  replaceMock.mockReset()
  vi.restoreAllMocks()
})

describe('RegisterPage — invite-gated pilot registration (WI-1)', () => {
  it('renders Arabic-first form fields and invite-only badge', () => {
    renderRegister()
    expect(screen.getByText(/دعوة فقط/)).toBeInTheDocument()
    expect(screen.getByLabelText(/الاسم الكامل/)).toBeInTheDocument()
    expect(screen.getByLabelText(/رمز الدعوة/)).toBeInTheDocument()
    expect(screen.getByLabelText(/نوع الحساب/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /إنشاء الحساب/ })).toBeInTheDocument()
  })

  it('POSTs to /api/auth/register with the invite code and routes to /owner on 201', async () => {
    const fetchMock = vi.spyOn(global, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({
        user: { user_id: 'u-1', email: 'owner@test.com',
                full_name: 'Test Owner', role: 'owner' }
      }), { status: 201, headers: { 'Content-Type': 'application/json' } })
    )
    renderRegister()
    await fillAndSubmit()

    await waitFor(() => expect(fetchMock).toHaveBeenCalled())
    const [url, init] = fetchMock.mock.calls[0]
    expect(String(url)).toMatch(/\/api\/auth\/register$/)
    expect(init?.method).toBe('POST')
    const body = JSON.parse(String(init?.body))
    expect(body).toMatchObject({
      email: 'owner@test.com',
      invite_code: 'OWNER-PILOT-001',
      role: 'owner',
      name: 'Test Owner',
    })

    await waitFor(() => expect(replaceMock).toHaveBeenCalledWith('/owner'))
    expect(localStorage.getItem('vc_user')).toContain('owner@test.com')
  })

  it('routes vet registration to /vet', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({
        user: { user_id: 'u-2', email: 'vet@test.com',
                full_name: 'Vet', role: 'veterinarian' }
      }), { status: 201, headers: { 'Content-Type': 'application/json' } })
    )
    renderRegister()
    await fillAndSubmit({ role: 'veterinarian' })
    await waitFor(() => expect(replaceMock).toHaveBeenCalledWith('/vet'))
  })

  it('shows Arabic INVALID_INVITE error on 400 invalid', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: { error: 'INVALID_INVITE' } }),
        { status: 400, headers: { 'Content-Type': 'application/json' } })
    )
    renderRegister()
    await fillAndSubmit()
    expect(await screen.findByRole('alert')).toHaveTextContent(/غير صالح أو مستخدم/)
    expect(replaceMock).not.toHaveBeenCalled()
  })

  it('shows Arabic INVITE_EXPIRED error on 400 expired', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: { error: 'INVITE_EXPIRED' } }),
        { status: 400, headers: { 'Content-Type': 'application/json' } })
    )
    renderRegister()
    await fillAndSubmit()
    expect(await screen.findByRole('alert')).toHaveTextContent(/انتهت صلاحية/)
  })

  it('shows Arabic ROLE_MISMATCH error on 400', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: { error: 'ROLE_MISMATCH' } }),
        { status: 400, headers: { 'Content-Type': 'application/json' } })
    )
    renderRegister()
    await fillAndSubmit()
    expect(await screen.findByRole('alert')).toHaveTextContent(/لا يطابق/)
  })

  it('shows Arabic EMAIL_EXISTS error on 409', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: { error: 'EMAIL_EXISTS' } }),
        { status: 409, headers: { 'Content-Type': 'application/json' } })
    )
    renderRegister()
    await fillAndSubmit()
    expect(await screen.findByRole('alert')).toHaveTextContent(/مسجّل بالفعل/)
  })

  it('all interactive controls meet the 48px touch-target minimum', () => {
    renderRegister()
    const inputs = ['الاسم الكامل', 'البريد الإلكتروني', 'رمز الدعوة', 'كلمة المرور']
      .map(label => screen.getByLabelText(new RegExp(label)) as HTMLInputElement)
    const button = screen.getByRole('button', { name: /إنشاء الحساب/ }) as HTMLButtonElement

    for (const el of [...inputs, button]) {
      const min = (el.style.minHeight || '').match(/(\d+)px/)?.[1]
      expect(Number(min ?? 0)).toBeGreaterThanOrEqual(48)
    }
  })
})
