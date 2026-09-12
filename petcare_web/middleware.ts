import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// PRE2_RULING=2-C. Canonical machine role IDs are the ONLY authorization
// tokens. This map is PRESENTATION/ROUTING: it turns a canonical role into a UI
// route category so the browser does not render a surface the backend would
// refuse. The backend decides authority; this only decides what is shown.
//
// Removed here, deliberately:
//
//   pharmacy      PHARMACY_ROLE=REMOVE. It is not an authorization principal,
//                 so it is not a role, so it has no category. The pharmacy
//                 SURFACE is retained and rebound below.
//   clinic_admin  a dead alias — it matched no vocabulary the serving layer has
//                 ever minted, so nothing could ever have carried it.
//   admin/vet     "legacy short-form values kept for compatibility". They are
//                 not canonical ids, nothing mints them, and keeping them meant
//                 a cookie could carry a value the backend would reject while
//                 the UI let it through.
const ROUTE_CATEGORY_BY_ROLE: Record<string, string> = {
  platform_admin: 'admin',
  veterinarian: 'vet',
  owner: 'owner',
  // Catalogued, but no backend route names it. It reaches self-service only —
  // granting it a privileged category here would show surfaces the API refuses.
  // DOMAIN_CAPABILITY_PENDING_ROLE_BINDING.
  partner_clinic_admin: 'clinic',
}

const protectedRoutes: Record<string, string[]> = {
  '/owner': ['owner', 'admin'],
  '/vet': ['vet', 'admin'],
  // PHARMACY_DOMAIN_CAPABILITIES=RETAIN_PENDING_ROLE_REBINDING.
  //
  // The surface stays; its authority is rebound to the actor the backend
  // already proves may perform the underlying act. Dispensing requires
  // VETERINARIAN — asserted by T-DISP-01 as a positive control and by
  // T-DISP-03/04 as negative ones — so the dispensing surface is bound to the
  // veterinarian, not to a role that no longer exists.
  //
  // The page's other regions (safety checks, cold chain) have no governed
  // backend action behind them yet; they are reachable but non-authoritative,
  // and are recorded as DOMAIN_CAPABILITY_PENDING_ROLE_BINDING rather than
  // granted to anyone by this change.
  '/pharmacy': ['vet', 'admin'],
  '/admin': ['admin'],
  // /account is any authenticated user (settings + PDPL rights). `clinic` is
  // included because self-service is not a privileged surface; `pharmacy` is
  // gone because it is not a role.
  '/account': ['owner', 'vet', 'clinic', 'admin'],
}

export function middleware(req: NextRequest) {
  const path = req.nextUrl.pathname
  const entry = Object.entries(protectedRoutes).find(
    ([prefix]) => path === prefix || path.startsWith(`${prefix}/`)
  )
  if (!entry) return NextResponse.next()

  const [, allowedRoles] = entry

  const rawRole =
    req.headers.get('x-petcare-role') ||
    req.cookies.get('petcare_role')?.value ||
    ''

  // `?? ''` and NOT `?? rawRole`. The previous form passed an unmapped value
  // straight through, so a cookie carrying `admin` — a value the serving layer
  // never mints — matched `['admin']` and opened the admin surface. An unknown
  // role now has no category and is denied. (ROLE-04, ROLE-06.)
  const role = ROUTE_CATEGORY_BY_ROLE[rawRole] ?? ''

  if (!role || !allowedRoles.includes(role)) {
    const url = req.nextUrl.clone()
    url.pathname = '/unauthorized'
    url.searchParams.set('from', req.nextUrl.pathname)
    url.searchParams.set('required', allowedRoles.join(','))
    return NextResponse.redirect(url)
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/owner/:path*', '/vet/:path*', '/pharmacy/:path*', '/admin/:path*', '/account/:path*'],
}
