'use client'

/**
 * CO-08 video waiting room (MVC-EPC-D-001 Lane D, D2f — journey J-O6; FR-06). Before a video consultation the owner
 * waits here, checks the camera and microphone, then joins the call (the U22 peer-to-peer client at
 * /account/consultations/video). The served app decides whether any of this is offered: remote veterinary consultation
 * stays closed until the KSA telemedicine counsel determination is recorded (AC-FR-06-05, COUNSEL:REG-02), and the call
 * also needs the SQ-2 video switch (OFF unless configured). While either is closed the room says why and presents NO
 * device or call control at all. Route: /owner/consultations/video?consultation=<id>.
 */

import { Suspense, useEffect, useRef, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { Button, Copy, LoadingState, Notice, Page, useCopy } from '@/components/ui'
import { HD_CONSTRAINTS } from '@/lib/videoCall'

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')

const V = {
  kicker: { ar: 'استشاراتي', en: 'My consultations' },
  title: { ar: 'غرفة الانتظار المرئية', en: 'Video waiting room' },
  back: { ar: 'العودة إلى استشاراتي', en: 'Back to my consultations' },
  none: { ar: 'لم يتم تحديد استشارة.', en: 'No consultation selected.' },
  counsel: { ar: 'الاستشارة البيطرية المرئية غير متاحة حالياً إلى حين صدور الرأي القانوني المعتمد بشأن الطب البيطري عن بُعد في المملكة. يمكنك مراسلة الطبيب البيطري من صفحة الرسائل.',
    en: 'Video veterinary consultation is not offered until the KSA telemedicine counsel determination is recorded. You can still message the veterinarian.' },
  switchOff: { ar: 'الاستشارة المرئية غير مفعّلة بعد في هذه البيئة.', en: 'Video consultation is not switched on in this environment yet.' },
  unavailable: { ar: 'تعذّر التحقق من إتاحة الاستشارة المرئية. حاول مرة أخرى لاحقاً.', en: 'Video availability could not be checked. Try again later.' },
  messages: { ar: 'الرسائل والملفات', en: 'Messages and files' },
  waiting: { ar: 'سيبدأ الطبيب البيطري المكالمة. تحقّق من الكاميرا والميكروفون قبل الانضمام.', en: 'Your veterinarian will start the call. Check your camera and microphone before joining.' },
  check: { ar: 'فحص الكاميرا والميكروفون', en: 'Check camera and microphone' },
  checkOk: { ar: 'الكاميرا والميكروفون يعملان.', en: 'Camera and microphone are working.' },
  checkFailed: { ar: 'تعذّر الوصول إلى الكاميرا أو الميكروفون. اسمح للمتصفح باستخدامهما ثم حاول مرة أخرى.', en: 'The camera or microphone could not be reached. Allow the browser to use them and try again.' },
  join: { ar: 'الانضمام إلى المكالمة', en: 'Join the call' },
} satisfies Record<string, Copy>

type Gate = 'loading' | 'counsel' | 'switch' | 'error' | 'open'

function Room() {
  const { tr } = useCopy()
  const consultation = useSearchParams().get('consultation') ?? ''
  const [gate, setGate] = useState<Gate>('loading')
  const [device, setDevice] = useState<'idle' | 'ok' | 'failed'>('idle')
  const preview = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    fetch(`${apiBase}/api/consultations/remote/availability`, { credentials: 'include', cache: 'no-store' })
      .then(r => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((a: { offered?: boolean; video_capability?: boolean }) =>
        setGate(a.offered !== true ? 'counsel' : a.video_capability !== true ? 'switch' : 'open'))
      .catch(() => setGate('error'))
  }, [])

  async function checkDevices() {
    try {
      const media = await navigator.mediaDevices.getUserMedia(HD_CONSTRAINTS)
      if (preview.current) preview.current.srcObject = media
      setDevice(media.getVideoTracks().length > 0 && media.getAudioTracks().length > 0 ? 'ok' : 'failed')
    } catch {
      setDevice('failed')
    }
  }

  if (!consultation) return <Notice tone="warn">{tr(V.none)}</Notice>
  const q = `consultation=${encodeURIComponent(consultation)}`
  const toMessages = <a className="ds-link" href={`/owner/consultations/messages?${q}`} data-testid="video-room-messages">{tr(V.messages)}</a>
  if (gate === 'loading') return <LoadingState />
  if (gate !== 'open') {
    const why = gate === 'counsel' ? V.counsel : gate === 'switch' ? V.switchOff : V.unavailable
    return (
      <div className="ds-stack" data-testid="video-room-closed" data-reason={gate}>
        <Notice tone={gate === 'error' ? 'danger' : 'info'}>{tr(why)}</Notice>
        <div className="ds-row">{toMessages}</div>
      </div>
    )
  }
  return (
    <div className="ds-stack" data-testid="video-room-open">
      <p>{tr(V.waiting)}</p>
      <video ref={preview} autoPlay muted playsInline data-testid="video-room-preview" />
      <div className="ds-row">
        <Button variant="secondary" onClick={() => void checkDevices()} data-testid="video-room-check">{tr(V.check)}</Button>
        <a className="ds-btn" href={`/account/consultations/video?${q}`} data-testid="video-room-join">{tr(V.join)}</a>
      </div>
      {device === 'ok' && <Notice tone="success" testId="video-room-check-ok">{tr(V.checkOk)}</Notice>}
      {device === 'failed' && <Notice tone="danger" testId="video-room-check-failed">{tr(V.checkFailed)}</Notice>}
      <div className="ds-row">{toMessages}</div>
    </div>
  )
}

export default function OwnerVideoWaitingRoomPage() {
  const { tr } = useCopy()
  return (
    <Page kicker={V.kicker} title={V.title} testId="video-room-page">
      <div className="ds-row"><a className="ds-link" href="/owner/consultations" data-testid="video-room-back">{tr(V.back)}</a></div>
      <Suspense fallback={null}><Room /></Suspense>
    </Page>
  )
}
