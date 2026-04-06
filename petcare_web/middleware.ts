import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const protectedRoutes: Record<string, string[]> = {
  '/owner': ['owner', 'admin'],
  '/vet': ['vet', 'admin'],
  '/pharmacy': ['pharmacy', 'admin'],
  '/admin': ['admin']
}

export function middleware(req: NextRequest) {
  const path = req.nextUrl.pathname
  const entry = Object.entries(protectedRoutes).find(([prefix]) => path === prefix || path.startsWith(`${prefix}/`))
  if (!entry) return NextResponse.next()

  const [, roles] = entry
  const role = req.headers.get('x-petcare-role') || req.cookies.get('petcare_role')?.value || ''

  if (!role || !roles.includes(role)) {
    const url = req.nextUrl.clone()
    url.pathname = '/unauthorized'
    url.searchParams.set('from', req.nextUrl.pathname)
    url.searchParams.set('required', roles.join(','))
    return NextResponse.redirect(url)
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/owner/:path*', '/vet/:path*', '/pharmacy/:path*', '/admin/:path*']
}
