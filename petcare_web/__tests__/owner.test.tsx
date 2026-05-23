import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import OwnerPage from '@/app/owner/page'

describe('OwnerPage — pilot RTL/AR coverage (WI-2)', () => {
  it('renders Arabic-first portal headings and four governance cards by default', () => {
    render(<LangProvider><OwnerPage /></LangProvider>)
    expect(screen.getByText('بوابة المالك')).toBeInTheDocument()
    expect(screen.getByText('حيواناتي الأليفة')).toBeInTheDocument()
    expect(screen.getByText('التدقيق نشط')).toBeInTheDocument()
    expect(screen.getByText('ملف الحيوان الأليف')).toBeInTheDocument()
    expect(screen.getByText('الجدول الصحي')).toBeInTheDocument()
    expect(screen.getByText('المواعيد')).toBeInTheDocument()
    expect(screen.getByText('الموافقة')).toBeInTheDocument()
  })

  it('renders English content when LangProvider hydrates with vc_lang=en', () => {
    localStorage.setItem('vc_lang', 'en')
    render(<LangProvider><OwnerPage /></LangProvider>)
    expect(screen.getByText('Owner portal')).toBeInTheDocument()
    expect(screen.getByText('My pets')).toBeInTheDocument()
    expect(screen.getByText('Pet profile')).toBeInTheDocument()
    expect(screen.getByText('Health timeline')).toBeInTheDocument()
    expect(document.documentElement.dir).toBe('ltr')
    expect(document.documentElement.lang).toBe('en')
  })

  it('uses STRINGS — no inline isAr ternary fallbacks survive on the page', () => {
    render(<LangProvider><OwnerPage /></LangProvider>)
    // Sentinel: previous implementation inlined the literal "Owner portal"
    // alongside the Arabic via `isAr ? 'ar' : 'en'`. After migration only the
    // selected language's strings should render.
    expect(screen.queryByText('Owner portal')).not.toBeInTheDocument()
  })
})
