/**
 * MVC-EPC-D-001 D2d — CO-01 owner home. The pets shown are the SERVED ones: before the server answers the region is
 * loading, when it cannot answer the region is an error — never the claim "you have no pets" the owner could act on.
 */
import { render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { LangProvider } from '@/components/LangProvider'
import OwnerPage from '@/app/owner/page'
import { STRINGS } from '@/lib/strings'

const region = () => document.querySelector('[data-list-region="owner-pets"]') as HTMLElement

afterEach(() => vi.unstubAllGlobals())

describe('CO-01 owner home — served pets (D2d)', () => {
  it('is loading, not empty, until the server answers', () => {
    vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {})))
    render(<LangProvider><OwnerPage /></LangProvider>)
    expect(region().querySelector('[data-state="loading"]')).not.toBeNull()
    expect(screen.queryByText(STRINGS.owner.petProfileEmpty.ar)).toBeNull()
  })

  it('is an error, not empty, when the server refuses', async () => {
    vi.stubGlobal('fetch', vi.fn(() => Promise.resolve(new Response('{}', { status: 500 }))))
    render(<LangProvider><OwnerPage /></LangProvider>)
    await vi.waitFor(() => expect(region().querySelector('[data-state="error"]')).not.toBeNull())
    expect(screen.queryByText(STRINGS.owner.petProfileEmpty.ar)).toBeNull()
  })

  it('lists the served pets as rows and links to the pets screen', async () => {
    vi.stubGlobal('fetch', vi.fn(() => Promise.resolve(new Response(JSON.stringify([
      { pet_id: 'p1', name: 'Luna', species: 'cat' }]), { status: 200 }))))
    render(<LangProvider><OwnerPage /></LangProvider>)
    expect(await screen.findByText('Luna · cat')).toHaveAttribute('data-list-row')
    expect(screen.getByTestId('owner-open-pets')).toHaveAttribute('href', '/owner/pets')
    const [url, init] = (fetch as unknown as { mock: { calls: [string, RequestInit][] } }).mock.calls[0]
    expect(url).toMatch(/\/api\/pets$/)
    expect(init.credentials).toBe('include')
  })
})
