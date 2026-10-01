/**
 * MVC-EPC-D-001 D2f — J-O6 owner screens: consultations list, CO-09 messages and files, CO-08 video waiting room.
 * The screens show what the server serves and send only the message text and the file — never an owner, tenant or
 * actor. The waiting room offers NO device or call control unless the server says remote consultation is offered
 * (REG-02 counsel) AND the SQ-2 video switch is on.
 */
import { fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { LangProvider } from '@/components/LangProvider'
import ConsultationsPage from '@/app/owner/consultations/page'
import MessagesPage from '@/app/owner/consultations/messages/page'
import VideoRoomPage from '@/app/owner/consultations/video/page'
import OwnerPage from '@/app/owner/page'

vi.mock('next/navigation', () => ({
  useSearchParams: () => new URLSearchParams('consultation=c-1'),
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  usePathname: () => '/owner/consultations',
}))

type Call = [string, RequestInit | undefined]
const calls = () => (fetch as unknown as { mock: { calls: Call[] } }).mock.calls

function serve(routes: Record<string, unknown>, post: unknown = { message_id: 'm-new' }) {
  vi.stubGlobal('fetch', vi.fn((url: string, init?: RequestInit) => {
    const path = new URL(url, 'http://x').pathname
    if (init?.method === 'POST') return Promise.resolve(new Response(JSON.stringify(post), { status: 200 }))
    return Promise.resolve(new Response(JSON.stringify(routes[path] ?? []), { status: 200 }))
  }))
}

beforeEach(() => localStorage.clear())
afterEach(() => vi.unstubAllGlobals())

const CONSULTS = { remote: { offered: false }, consultations: [
  { session_id: 'c-1', pet_id: 'p1', mode: 'IN_PERSON', status: 'REQUESTED', created_at: '2031-03-01T06:00:00+00:00' },
  { session_id: 'c-2', pet_id: 'p1', mode: 'REMOTE_VIDEO', status: 'REQUESTED', created_at: '2031-03-02T06:00:00+00:00' }] }

describe('owner consultations (D2f, J-O6)', () => {
  it('lists the served consultations with their pet and opens messages and the video room', async () => {
    serve({ '/api/consultations': CONSULTS, '/api/pets': [{ pet_id: 'p1', name: 'لونا' }] })
    render(<LangProvider><ConsultationsPage /></LangProvider>)
    expect(await screen.findAllByText('لونا')).toHaveLength(2)
    expect(screen.getByTestId('consultations-remote-off')).toBeInTheDocument()
    const msgs = screen.getAllByTestId('consultation-open-messages')
    expect(msgs[0]).toHaveAttribute('href', '/owner/consultations/messages?consultation=c-1')
    expect(screen.getAllByTestId('consultation-open-video')).toHaveLength(1)                 // only the video one
    expect(screen.getByTestId('consultation-open-video')).toHaveAttribute('href', '/owner/consultations/video?consultation=c-2')
  })

  it('is loading, not empty, until the server answers', () => {
    vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {})))
    render(<LangProvider><ConsultationsPage /></LangProvider>)
    expect(document.querySelector('[data-state="loading"]')).not.toBeNull()
  })

  it('is linked from the owner home', () => {
    vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {})))
    render(<LangProvider><OwnerPage /></LangProvider>)
    expect(screen.getByTestId('owner-open-consultations')).toHaveAttribute('href', '/owner/consultations')
  })
})

describe('CO-09 messages and files (D2f, J-O6)', () => {
  const MSGS = [{ message_id: 'm-1', sender_id: 'u-vet', sender_role: 'veterinarian', body: 'نتيجة التحليل مرفقة',
    created_at: '2031-03-01T06:00:00+00:00', attachments: [{ attachment_id: 'a-1', filename: 'cbc.png', byte_size: 72 }] }]

  it('shows the thread from the server with the attachment download, Arabic and right-to-left by default', async () => {
    serve({ '/api/consultations/c-1/messages': MSGS })
    render(<LangProvider><MessagesPage /></LangProvider>)
    expect(await screen.findByText('نتيجة التحليل مرفقة')).toBeInTheDocument()
    expect(screen.getByTestId('message-attachment').getAttribute('href')).toMatch(/\/api\/consultations\/c-1\/messages\/m-1\/attachments\/a-1$/)
    expect(screen.getByTestId('messages-page').closest('[dir]')?.getAttribute('dir')).toBe('rtl')
  })

  it('posts only the message text, then the file to that message', async () => {
    serve({ '/api/consultations/c-1/messages': [] })
    render(<LangProvider><MessagesPage /></LangProvider>)
    await screen.findByTestId('message-form')
    fireEvent.change(document.querySelector('textarea[name="body"]') as HTMLTextAreaElement, { target: { value: 'لونا تسعل' } })
    const file = new File([new Uint8Array([137, 80, 78, 71])], 'photo.png', { type: 'image/png' })
    fireEvent.change(screen.getByTestId('message-file'), { target: { files: [file] } })
    fireEvent.submit(screen.getByTestId('message-form'))
    await vi.waitFor(() => expect(calls().filter(([, i]) => i?.method === 'POST')).toHaveLength(2))
    const [msgUrl, msgInit] = calls().filter(([, i]) => i?.method === 'POST')[0]
    expect(msgUrl).toMatch(/\/api\/consultations\/c-1\/messages$/)
    expect(JSON.parse(String(msgInit?.body))).toEqual({ body: 'لونا تسعل' })               // no owner, tenant or actor
    const [upUrl, upInit] = calls().filter(([, i]) => i?.method === 'POST')[1]
    expect(upUrl).toMatch(/\/api\/consultations\/c-1\/messages\/m-new\/attachments$/)
    expect(upInit?.body).toBeInstanceOf(FormData)
    expect(upInit?.credentials).toBe('include')
  })
})

describe('CO-08 video waiting room (D2f, J-O6)', () => {
  it('presents no device or call control while remote consultation is not offered (REG-02)', async () => {
    serve({ '/api/consultations/remote/availability': { offered: false, video_capability: true } })
    render(<LangProvider><VideoRoomPage /></LangProvider>)
    expect(await screen.findByTestId('video-room-closed')).toHaveAttribute('data-reason', 'counsel')
    expect(screen.queryByTestId('video-room-check')).toBeNull()
    expect(screen.queryByTestId('video-room-join')).toBeNull()
    expect(screen.getByTestId('video-room-messages')).toHaveAttribute('href', '/owner/consultations/messages?consultation=c-1')
  })

  it('stays closed while the SQ-2 video switch is off even when counsel has been recorded', async () => {
    serve({ '/api/consultations/remote/availability': { offered: true, video_capability: false } })
    render(<LangProvider><VideoRoomPage /></LangProvider>)
    expect(await screen.findByTestId('video-room-closed')).toHaveAttribute('data-reason', 'switch')
    expect(screen.queryByTestId('video-room-join')).toBeNull()
  })

  it('offers the device check and the call only when both are open', async () => {
    serve({ '/api/consultations/remote/availability': { offered: true, video_capability: true } })
    const track = { stop: vi.fn() }
    vi.stubGlobal('navigator', { ...navigator, mediaDevices: { getUserMedia: vi.fn(() =>
      Promise.resolve({ getVideoTracks: () => [track], getAudioTracks: () => [track] })) } })
    render(<LangProvider><VideoRoomPage /></LangProvider>)
    fireEvent.click(await screen.findByTestId('video-room-check'))
    expect(await screen.findByTestId('video-room-check-ok')).toBeInTheDocument()
    expect(screen.getByTestId('video-room-join')).toHaveAttribute('href', '/account/consultations/video?consultation=c-1')
  })

  it('fails closed when availability cannot be read', async () => {
    vi.stubGlobal('fetch', vi.fn(() => Promise.resolve(new Response('', { status: 500 }))))
    render(<LangProvider><VideoRoomPage /></LangProvider>)
    expect(await screen.findByTestId('video-room-closed')).toHaveAttribute('data-reason', 'error')
    expect(screen.queryByTestId('video-room-join')).toBeNull()
  })
})
