import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import VideoConsultationPage from '@/app/account/consultations/video/page'
import { QUALITY_REPORT_MS } from '@/lib/videoCall'

/**
 * FR-06 video call client (MVC-BUILD-RUNNER-001 U22) with the browser media APIs stubbed. Served signalling:
 * petcare_api/tests/test_fr06_video.py. Not registered as AC-FR-06-01/02 evidence (SPONSOR_QUEUE SQ-2).
 */

vi.mock('next/navigation', () => ({
  useSearchParams: () => new URLSearchParams('consultation=c-9'),
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  usePathname: () => '/account/consultations/video',
}))

function json(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}

const replaceTrack = vi.fn(async () => {})
class FakePC {
  onicecandidate: unknown = null; ontrack: unknown = null
  addTrack = vi.fn()
  createOffer = vi.fn(async () => ({ type: 'offer', sdp: 'v=0' }))
  setLocalDescription = vi.fn(async () => {})
  getSenders = () => [{ track: { kind: 'video' }, replaceTrack }]
  getStats = async () => new Map<string, unknown>([
    ['in', { type: 'inbound-rtp', kind: 'video', frameWidth: 1280, frameHeight: 720 }],
    ['out', { type: 'outbound-rtp', kind: 'video', qualityLimitationReason: 'none', targetBitrate: 2500000 }]])
}

beforeEach(() => {
  vi.restoreAllMocks(); localStorage.clear(); replaceTrack.mockClear()
  vi.stubGlobal('RTCPeerConnection', FakePC)
  const track = { kind: 'video' }
  Object.defineProperty(navigator, 'mediaDevices', { configurable: true, value: {
    getUserMedia: vi.fn(async () => ({ getTracks: () => [track], getVideoTracks: () => [track] })),
    getDisplayMedia: vi.fn(async () => ({ getVideoTracks: () => [{ kind: 'video', label: 'screen' }] })),
  } })
})
afterEach(() => { vi.useRealTimers() })

describe('FR-06 video call page', () => {
  it('offers no call control while remote consultation is not offered (Arabic RTL)', async () => {
    vi.stubGlobal('fetch', vi.fn(() => json({ offered: false })))
    const { container } = render(<LangProvider><VideoConsultationPage /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('video-not-offered')).toBeTruthy())
    expect(container.querySelector('main')?.getAttribute('dir')).toBe('rtl')
    expect(screen.queryByTestId('video-call')).toBeNull()
    expect(container.querySelectorAll('button').length).toBe(0)
  })

  it('captures at 720p, sends the offer through the served app, shares the screen and reports quality', async () => {
    const fetchMock = vi.fn((url: string, _i?: RequestInit) =>
      String(url).endsWith('/remote/availability') ? json({ offered: true }) : json([]))
    vi.stubGlobal('fetch', fetchMock)
    render(<LangProvider><VideoConsultationPage /></LangProvider>)
    await waitFor(() => expect(screen.getByTestId('video-call')).toBeTruthy())
    vi.useFakeTimers()
    await act(async () => { fireEvent.click(screen.getByText('بدء المكالمة')); await vi.advanceTimersByTimeAsync(10) })
    const gum = (navigator.mediaDevices.getUserMedia as ReturnType<typeof vi.fn>).mock.calls[0][0]
    expect(gum.video.height.min).toBe(720)
    expect(gum.video.width.min).toBe(1280)
    const offer = fetchMock.mock.calls.find(c => String(c[0]).endsWith('/api/consultations/c-9/video/signal') && c[1]?.method === 'POST')!
    expect(JSON.parse(String(offer[1]!.body)).kind).toBe('OFFER')
    await act(async () => { fireEvent.click(screen.getByText('مشاركة الشاشة')); await vi.advanceTimersByTimeAsync(10) })
    expect(navigator.mediaDevices.getDisplayMedia).toHaveBeenCalled()
    expect(replaceTrack).toHaveBeenCalledWith({ kind: 'video', label: 'screen' })
    await act(async () => { await vi.advanceTimersByTimeAsync(QUALITY_REPORT_MS) })
    const quality = fetchMock.mock.calls.find(c => String(c[0]).endsWith('/video/quality'))!
    expect(JSON.parse(String(quality[1]!.body))).toEqual({ frame_width: 1280, frame_height: 720, bitrate_kbps: 2500,
      quality_limitation_reason: null })
  })
})
