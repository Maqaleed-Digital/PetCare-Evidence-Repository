import { NextRequest, NextResponse } from 'next/server'

export async function POST(req: NextRequest) {
  const body = await req.json()
  console.log(JSON.stringify({ type: 'ui_audit_test', body }))
  return NextResponse.json({ accepted: true })
}
