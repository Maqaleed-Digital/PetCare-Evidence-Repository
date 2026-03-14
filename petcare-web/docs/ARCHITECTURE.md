# Architecture — petcare-web (PH-UI-1A)

## Overview

`petcare-web` is a read-only Next.js App Router shell. It provides role-scoped
views (Owner, Vet, Admin) and a live API health indicator. It does not mutate
backend state.

## Stack

| Layer        | Technology                      |
|--------------|---------------------------------|
| Framework    | Next.js 15 (App Router)         |
| Language     | TypeScript                      |
| Styling      | Tailwind CSS                    |
| Runtime      | Node.js 20                      |

## Directory Layout

```
petcare-web/
  app/
    layout.tsx              Root layout — wraps every page in LayoutWrapper
    page.tsx                Home / Dashboard — shows ApiHealthIndicator
    owner/page.tsx          Owner portal (read-only shell)
    vet/page.tsx            Vet portal (read-only shell)
    admin/page.tsx          Admin portal (read-only shell)
    api/proxy/health/route.ts   Server-side proxy → api.myveticare.com/health
    api/proxy/ready/route.ts    Server-side proxy → api.myveticare.com/ready
  components/
    Navbar.tsx              Top bar
    Sidebar.tsx             Role navigation
    LayoutWrapper.tsx       Composes Navbar + Sidebar + main
    StatusCard.tsx          Single metric card
    DashboardGrid.tsx       Responsive card grid
    ApiHealthIndicator.tsx  Polls proxy routes, renders status cards
  hooks/
    useApiHealth.ts         Polls /api/proxy/health + /api/proxy/ready every 30s
  services/
    api.service.ts          fetch wrappers for proxy routes
  types/
    api.ts                  HealthResponse, ReadyResponse, ApiHealthState
  config/
    api.ts                  Canonical upstream URL + proxy paths + timeout
  docs/
    ARCHITECTURE.md         This file
    API_INTEGRATION.md      Proxy design rationale
```

## Constraints

- No backend mutation — all pages are read-only.
- No direct browser calls to `api.myveticare.com` — CORS solved via server-side
  proxy routes under `/api/proxy/*`.
- No authentication in PH-UI-1A scope.
