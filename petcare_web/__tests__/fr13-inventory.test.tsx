import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, act, fireEvent } from '@testing-library/react'
import { LangProvider } from '@/components/LangProvider'
import InventoryPage from '@/app/pharmacy/inventory/page'
import { INVENTORY_REFRESH_MS } from '@/lib/inventory'

/**
 * AC-FR-13-01 (UI) — stock per location, updating WITHOUT a manual refresh
 * (MVC-BUILD-RUNNER-001 U8). REAL_TIME_BOUND = 5 s; the UI contributes at most one refresh
 * interval. Served-app behaviour and the 100-event p95: petcare_api/tests/test_inventory.py.
 */

const view = (north: number) => ({
  as_of: '2026-09-25T10:00:00Z',
  locations: [
    { location_id: 'loc-n', name: 'الرياض الشمالي', stock: [{ product_id: 'gauze-01', batch: 'B1', quantity: north, supply_class: 'GENERAL' }] },
    { location_id: 'loc-s', name: 'الرياض الجنوبي', stock: [{ product_id: 'amoxi', batch: 'P1', quantity: 4, supply_class: 'POM' }] },
  ],
})

function json(body: unknown, status = 200) {
  return Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) } as Response)
}

beforeEach(() => { vi.useFakeTimers(); localStorage.clear() })
afterEach(() => { vi.useRealTimers(); vi.restoreAllMocks() })

describe('FR-13 inventory — per location, refreshing itself inside the ratified bound', () => {
  it('the refresh interval leaves room inside REAL_TIME_BOUND = 5 s', () => {
    expect(INVENTORY_REFRESH_MS).toBeGreaterThan(0)
    expect(INVENTORY_REFRESH_MS).toBeLessThanOrEqual(2500)
  })

  it('shows every location of the tenant with its own stock, Arabic RTL by default', async () => {
    vi.stubGlobal('fetch', vi.fn(() => json(view(25))))
    const { container } = render(<LangProvider><InventoryPage /></LangProvider>)
    await act(async () => { await vi.advanceTimersByTimeAsync(10) })
    expect(screen.getAllByTestId('inventory-location').length).toBe(2)
    expect(screen.getAllByTestId('stock-quantity').map(e => e.textContent)).toEqual(['25', '4'])
    expect(container.querySelector('main')?.getAttribute('dir')).toBe('rtl')
    expect(screen.getByText('المخزون حسب الموقع')).toBeTruthy()
    expect(screen.getByText(/للطبيب البيطري فقط/)).toBeTruthy()
  })

  it('a stock change at another location appears with no user action', async () => {
    let north = 25
    vi.stubGlobal('fetch', vi.fn(() => json(view(north))))
    render(<LangProvider><InventoryPage /></LangProvider>)
    await act(async () => { await vi.advanceTimersByTimeAsync(10) })
    expect(screen.getAllByTestId('stock-quantity')[0].textContent).toBe('25')
    north = 10
    await act(async () => { await vi.advanceTimersByTimeAsync(INVENTORY_REFRESH_MS) })
    expect(screen.getAllByTestId('stock-quantity')[0].textContent).toBe('10')
  })

  it('a failed refresh keeps the last good view', async () => {
    let fail = false
    vi.stubGlobal('fetch', vi.fn(() => fail ? Promise.reject(new Error('network')) : json(view(25))))
    render(<LangProvider><InventoryPage /></LangProvider>)
    await act(async () => { await vi.advanceTimersByTimeAsync(10) })
    fail = true
    await act(async () => { await vi.advanceTimersByTimeAsync(INVENTORY_REFRESH_MS) })
    expect(screen.getAllByTestId('inventory-location').length).toBe(2)
  })

  it('records a movement sending no actor, tenant or supply class', async () => {
    const fetchMock = vi.fn((_u: string, _i?: RequestInit) => json(view(25)))
    vi.stubGlobal('fetch', fetchMock)
    render(<LangProvider><InventoryPage /></LangProvider>)
    await act(async () => { await vi.advanceTimersByTimeAsync(10) })
    const form = screen.getByRole('form')
    for (const [name, value] of [['product_id', 'gauze-01'], ['batch', 'B1'], ['quantity_delta', '5']]) {
      fireEvent.change(form.querySelector(`[name="${name}"]`)!, { target: { value } })
    }
    await act(async () => { fireEvent.submit(form); await vi.advanceTimersByTimeAsync(10) })
    const post = fetchMock.mock.calls.find(c => c[1]?.method === 'POST')!
    expect(String(post[0]).endsWith('/api/inventory/movements')).toBe(true)
    const sent = JSON.parse(String(post[1]!.body))
    expect(sent).toMatchObject({ location_id: 'loc-n', product_id: 'gauze-01', batch: 'B1', quantity_delta: 5, reason: 'RECEIPT' })
    for (const k of ['actor_id', 'tenant_id', 'supply_class', 'role']) expect(k in sent).toBe(false)
  })
})
