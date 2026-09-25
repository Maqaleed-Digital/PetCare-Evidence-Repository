/**
 * FR-06 (MVC-BUILD-RUNNER-001 U22) — the video-call client. Peer-to-peer WebRTC; the served app relays signalling
 * only. Built behind the REG-02 telemedicine gate: the page never starts a call unless the served app says remote
 * consultation is offered. AC-FR-06-02 (NFR-03): capture asks for 720p and quality is reported every
 * QUALITY_REPORT_MS with the browser's quality-limitation reason (the adaptive-bitrate step-down record).
 */
export const HD_CONSTRAINTS: MediaStreamConstraints = {
  audio: true,
  video: { width: { ideal: 1280, min: 1280 }, height: { ideal: 720, min: 720 }, frameRate: { ideal: 30 } },
}
export const POLL_MS = 1000
export const QUALITY_REPORT_MS = 5000

export type Signal = { seq: number; kind: string; payload: Record<string, unknown>; from: string }

export async function sampleQuality(pc: RTCPeerConnection) {
  const stats = await pc.getStats()
  let frame_width = 0, frame_height = 0, bitrate_kbps = 0, quality_limitation_reason: string | null = null
  stats.forEach((r: any) => {
    if (r.type === 'inbound-rtp' && r.kind === 'video') { frame_width = r.frameWidth ?? 0; frame_height = r.frameHeight ?? 0 }
    if (r.type === 'outbound-rtp' && r.kind === 'video') {
      quality_limitation_reason = r.qualityLimitationReason && r.qualityLimitationReason !== 'none' ? r.qualityLimitationReason : null
      bitrate_kbps = Math.round((r.targetBitrate ?? 0) / 1000)
    }
  })
  return { frame_width, frame_height, bitrate_kbps, quality_limitation_reason }
}
