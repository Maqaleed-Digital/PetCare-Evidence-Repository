'use client'

/**
 * FR-06 — video consultation with screen sharing (MVC-BUILD-RUNNER-001 U22), behind the REG-02 gate.
 * Route: /account/consultations/video?consultation=<id>. While the served app says remote consultation is not
 * offered (AC-FR-06-05), the page shows why and presents no call control. Arabic default, RTL.
 */

import { Suspense, useCallback, useEffect, useRef, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { useLang } from '@/components/LangProvider'
import { HD_CONSTRAINTS, POLL_MS, QUALITY_REPORT_MS, Signal, sampleQuality } from '@/lib/videoCall'

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
const call = (path: string, init?: RequestInit) =>
  fetch(`${apiBase}${path}`, { credentials: 'include', cache: 'no-store', ...init })

const L = {
  title: { ar: 'استشارة مرئية', en: 'Video consultation' },
  notOffered: { ar: 'الاستشارة البيطرية عن بُعد غير متاحة حالياً إلى حين صدور الرأي القانوني المعتمد.',
    en: 'Remote veterinary consultation is not offered until the counsel determination is recorded.' },
  start: { ar: 'بدء المكالمة', en: 'Start call' },
  share: { ar: 'مشاركة الشاشة', en: 'Share screen' },
  error: { ar: 'تعذر بدء المكالمة', en: 'The call could not start' },
} as const

function Call() {
  const { lang } = useLang()
  const isAr = lang === 'ar'
  const t = (k: keyof typeof L) => L[k][isAr ? 'ar' : 'en']
  const consultation = useSearchParams().get('consultation') ?? ''
  const [offered, setOffered] = useState<boolean | null>(null)
  const [error, setError] = useState('')
  const pcRef = useRef<RTCPeerConnection | null>(null)
  const localRef = useRef<HTMLVideoElement>(null)
  const remoteRef = useRef<HTMLVideoElement>(null)
  const seqRef = useRef(0)
  const base = `/api/consultations/${consultation}/video`

  useEffect(() => {
    void (async () => {
      const r = await call('/api/consultations/remote/availability')
      setOffered(r.ok ? Boolean((await r.json()).offered) : false)
    })()
  }, [])

  const send = useCallback((kind: string, payload: Record<string, unknown>) =>
    call(`${base}/signal`, { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ kind, payload }) }), [base])

  const handle = useCallback(async (pc: RTCPeerConnection, s: Signal) => {
    if (s.kind === 'OFFER' || s.kind === 'SCREEN_OFFER') {
      await pc.setRemoteDescription(s.payload as unknown as RTCSessionDescriptionInit)
      const answer = await pc.createAnswer()
      await pc.setLocalDescription(answer)
      await send(s.kind === 'OFFER' ? 'ANSWER' : 'SCREEN_ANSWER', { type: answer.type, sdp: answer.sdp })
    } else if (s.kind === 'ANSWER' || s.kind === 'SCREEN_ANSWER') {
      await pc.setRemoteDescription(s.payload as unknown as RTCSessionDescriptionInit)
    } else if (s.kind === 'ICE') {
      await pc.addIceCandidate(s.payload as RTCIceCandidateInit)
    }
  }, [send])

  async function start() {
    try {
      const media = await navigator.mediaDevices.getUserMedia(HD_CONSTRAINTS)
      if (localRef.current) localRef.current.srcObject = media
      const pc = new RTCPeerConnection()
      pcRef.current = pc
      media.getTracks().forEach(track => pc.addTrack(track, media))
      pc.onicecandidate = e => { if (e.candidate) void send('ICE', e.candidate.toJSON() as Record<string, unknown>) }
      pc.ontrack = e => { if (remoteRef.current) remoteRef.current.srcObject = e.streams[0] }
      const offer = await pc.createOffer()
      await pc.setLocalDescription(offer)
      await send('OFFER', { type: offer.type, sdp: offer.sdp })
      setInterval(async () => {
        const r = await call(`${base}/signal?after=${seqRef.current}`)
        if (!r.ok) return
        for (const s of (await r.json()) as Signal[]) { seqRef.current = Math.max(seqRef.current, s.seq); await handle(pc, s) }
      }, POLL_MS)
      setInterval(async () => {
        const q = await sampleQuality(pc)
        if (q.frame_height > 0) await call(`${base}/quality`, { method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(q) })
      }, QUALITY_REPORT_MS)
    } catch { setError(t('error')) }
  }

  async function shareScreen() {
    const pc = pcRef.current
    if (!pc) return
    const screen = await navigator.mediaDevices.getDisplayMedia({ video: true })
    const sender = pc.getSenders().find(x => x.track?.kind === 'video')
    await sender?.replaceTrack(screen.getVideoTracks()[0])
  }

  return (
    <main className="stack" dir={isAr ? 'rtl' : 'ltr'}>
      <h1 className="title-lg">{t('title')}</h1>
      {offered === false && <p role="status" data-testid="video-not-offered">{t('notOffered')}</p>}
      {offered && (
        <div className="stack" data-testid="video-call">
          <video ref={localRef} autoPlay muted playsInline />
          <video ref={remoteRef} autoPlay playsInline data-testid="remote-video" />
          <button type="button" className="btn" onClick={() => void start()}>{t('start')}</button>
          <button type="button" className="btn" onClick={() => void shareScreen()}>{t('share')}</button>
        </div>
      )}
      {error && <p role="alert">{error}</p>}
    </main>
  )
}

export default function VideoConsultationPage() {
  return <Suspense><Call /></Suspense>
}
