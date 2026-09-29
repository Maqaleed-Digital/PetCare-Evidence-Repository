'use client'

/**
 * CO-14 notification centre (MVC-EPC-D-001 Lane D, D2d — journey J-O10). One chronological list of what the served
 * app has sent this owner: FR-23 care reminders (/api/me/reminders) and FR-19 recall notices (/api/me/recall-notices).
 * Nothing is generated or stored in the browser; each item links to the screen that owns it.
 */

import { useCallback, useEffect, useState } from 'react'
import { Copy, DataView, Page, useCopy } from '@/components/ui'

const apiBase = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '')
const get = (path: string) => fetch(`${apiBase}${path}`, { credentials: 'include', cache: 'no-store' })
  .then(r => (r.ok ? r.json() : Promise.reject(r.status)))

const N = {
  kicker: { ar: 'بوابة المالك', en: 'Owner portal' },
  title: { ar: 'الإشعارات', en: 'Notifications' },
  empty: { ar: 'لا توجد إشعارات بعد.', en: 'No notifications yet.' },
  reminder: { ar: 'تذكير رعاية', en: 'Care reminder' },
  recall: { ar: 'سحب منتج', en: 'Product recall' },
  openReminders: { ar: 'كل التذكيرات', en: 'All reminders' },
  openRecalls: { ar: 'تفاصيل السحب', en: 'Recall details' },
} satisfies Record<string, Copy>

type Item = { id: string; kind: 'reminder' | 'recall'; body: string; lang?: string; at: string }

export default function NotificationsPage() {
  const { tr, lang } = useCopy()
  const [status, setStatus] = useState<'loading' | 'error' | 'ready'>('loading')
  const [items, setItems] = useState<Item[] | null>(null)

  const load = useCallback(() => {
    setStatus('loading')
    Promise.all([get('/api/me/reminders'), get('/api/me/recall-notices')])
      .then(([reminders, recalls]: [{ reminder_id: string; body: string; language: string; sent_at: string }[],
        { notification_id: string; body: string; created_at: string }[]]) => {
        const all: Item[] = [
          ...reminders.map(r => ({ id: r.reminder_id, kind: 'reminder' as const, body: r.body, lang: r.language, at: r.sent_at })),
          ...recalls.map(n => ({ id: n.notification_id, kind: 'recall' as const, body: n.body, at: n.created_at })),
        ].sort((a, b) => b.at.localeCompare(a.at))
        setItems(all); setStatus('ready')
      })
      .catch(() => setStatus('error'))
  }, [])
  useEffect(load, [load])

  const when = (iso: string) => new Date(iso).toLocaleString(lang === 'ar' ? 'ar-SA' : 'en-GB',
    { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })

  return (
    <Page kicker={N.kicker} title={N.title} testId="notifications-page">
      <DataView status={status} data={items} onRetry={load} empty={N.empty}>
        {list => (
          <ol className="ds-list" aria-label={tr(N.title)}>
            {list.map(i => (
              <li key={`${i.kind}-${i.id}`} data-testid="notification" data-kind={i.kind}>
                <div className="ds-row ds-row--between">
                  <span className={`ds-badge${i.kind === 'recall' ? '' : ' ds-badge--success'}`}>{tr(N[i.kind])}</span>
                  <time dateTime={i.at} className="ds-hint">{when(i.at)}</time>
                </div>
                <p lang={i.lang}>{i.body}</p>
                <a className="ds-link" href={i.kind === 'recall' ? '/owner/recalls' : '/owner/reminders'}>
                  {tr(i.kind === 'recall' ? N.openRecalls : N.openReminders)}
                </a>
              </li>
            ))}
          </ol>
        )}
      </DataView>
    </Page>
  )
}
