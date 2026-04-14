import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Backend roles (petcare_pilot_session auth) → normalised middleware role
const ROLE_ALIAS: Record<string, string> = {
  platform_admin: 'admin',
  clinic_admin: 'admin',
  veterinarian: 'vet',
  // legacy short-form values kept for compatibility
  admin: 'admin',
  vet: 'vet',
  owner: 'owner',
  pharmacy: 'pharmacy',
}

const protectedRoutes: Record<string, string[]> = {
  '/owner': ['owner', 'admin'],
  '/vet': ['vet', 'admin'],
  '/pharmacy': ['pharmacy', 'admin'],
  '/admin': ['admin'],
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

  const role = ROLE_ALIAS[rawRole] ?? rawRole

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
  matcher: ['/owner/:path*', '/vet/:path*', '/pharmacy/:path*', '/admin/:path*'],
}
