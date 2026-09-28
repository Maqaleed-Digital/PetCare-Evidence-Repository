/**
 * FULL-STACK journey suite (MVC-EPC-D-001 Lane D, D0): real browser -> this web app -> FastAPI main:app -> PostgreSQL.
 * The backend is `tools/e2e_stack.py` (fresh database, every migration from empty, synthetic seed). Only external
 * providers are faked, through the D6 adapters. Four projects: Arabic (default, no stored preference — proves the
 * new-visitor default) and English, each at 1280 px and 390 px. The mocked-backend smoke suite stays in ./e2e.
 */
import { defineConfig } from '@playwright/test'
import os from 'node:os'
import path from 'node:path'

const API = process.env.PETCARE_E2E_API ?? 'http://localhost:8090'
const WEB = process.env.PETCARE_E2E_WEB ?? 'http://localhost:3100'
// The FAKE email adapter's outbox (tools/e2e_stack.py writes it; journeys read verification/reset links from it).
const OUTBOX = process.env.PETCARE_E2E_OUTBOX ?? path.join(os.tmpdir(), 'petcare-e2e-outbox.jsonl')
process.env.PETCARE_E2E_OUTBOX = OUTBOX
const desktop = { viewport: { width: 1280, height: 900 } }
const mobile = { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true }

export default defineConfig<{ lang: 'ar' | 'en' }>({
  testDir: './e2e-full',
  fullyParallel: false,
  workers: 1,
  timeout: 90_000,
  // Full stack: `next dev` compiles each route on first visit, so a first navigation can take several seconds.
  expect: { timeout: 30_000 },
  reporter: [['list'], ['json', { outputFile: 'e2e-full/.results/results.json' }]],
  use: { baseURL: WEB, trace: 'retain-on-failure' },
  projects: [
    { name: 'ar-desktop', use: { ...desktop, lang: 'ar' } },
    { name: 'ar-mobile', use: { ...mobile, lang: 'ar' } },
    { name: 'en-desktop', use: { ...desktop, lang: 'en' } },
    { name: 'en-mobile', use: { ...mobile, lang: 'en' } },
  ],
  webServer: [
    {
      command: 'python3 ../tools/e2e_stack.py',
      url: `${API}/health`,
      timeout: 240_000,
      reuseExistingServer: !process.env.CI,
      env: { PETCARE_E2E_API_PORT: new URL(API).port, PETCARE_E2E_WEB_ORIGIN: WEB, PETCARE_E2E_OUTBOX: OUTBOX },
    },
    {
      command: `npx next dev -p ${new URL(WEB).port}`,
      url: WEB,
      timeout: 240_000,
      reuseExistingServer: !process.env.CI,
      env: { NEXT_PUBLIC_API_BASE_URL: API },
    },
  ],
})
