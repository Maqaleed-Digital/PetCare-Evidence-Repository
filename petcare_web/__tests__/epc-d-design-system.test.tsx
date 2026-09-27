import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import { DataView, Field, Page } from '@/components/ui'

/** MVC-EPC-D-001 D0 — design-system primitives (G1) and the four data states every screen renders (G4/X4). */
const wrap = (ui: React.ReactNode) => render(<LangProvider>{ui}</LangProvider>)

describe('design system (G1/G4)', () => {
  it('Page is Arabic and right-to-left by default and titles the screen', () => {
    wrap(<Page title={{ ar: 'العنوان', en: 'Title' }}><p>x</p></Page>)
    expect(screen.getByRole('main')).toHaveAttribute('dir', 'rtl')
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('العنوان')
  })

  it('DataView renders exactly one of loading / error / empty / content', () => {
    const { rerender } = wrap(<DataView status="loading" data={null}>{() => <p>content</p>}</DataView>)
    expect(document.querySelector('[data-state="loading"]')).not.toBeNull()
    rerender(<LangProvider><DataView status="error" data={null} onRetry={() => {}}>{() => <p>content</p>}</DataView></LangProvider>)
    expect(screen.getByRole('alert')).toHaveTextContent('تعذر تحميل البيانات')
    expect(screen.getByRole('button', { name: 'إعادة المحاولة' })).toBeInTheDocument()
    rerender(<LangProvider><DataView status="ready" data={[]}>{() => <p>content</p>}</DataView></LangProvider>)
    expect(document.querySelector('[data-state="empty"]')).not.toBeNull()
    expect(screen.queryByText('content')).toBeNull()
    rerender(<LangProvider><DataView status="ready" data={[1]}>{() => <p>content</p>}</DataView></LangProvider>)
    expect(screen.getByText('content')).toBeInTheDocument()
    expect(document.querySelector('[data-state]')).toBeNull()
  })

  it('Field is labelled, carries its hint and announces its error', () => {
    wrap(<Field label={{ ar: 'الاسم', en: 'Name' }} hint={{ ar: 'كما في الهوية', en: 'As on ID' }} error="مطلوب" />)
    const input = screen.getByLabelText('الاسم')
    expect(input).toHaveAttribute('aria-invalid', 'true')
    expect(input.getAttribute('aria-describedby')?.split(' ')).toHaveLength(2)
    expect(screen.getByRole('alert')).toHaveTextContent('مطلوب')
  })
})
