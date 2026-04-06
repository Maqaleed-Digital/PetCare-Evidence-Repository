import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({
    status: 'ok',
    surface: 'petcare-web',
    ts: new Date().toISOString()
  })
}
