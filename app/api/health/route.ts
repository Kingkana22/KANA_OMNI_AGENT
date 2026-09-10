import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({
    system: 'KANA SOVEREIGN CORE',
    runtime: 'vercel',
    status: 'online',
    brain: 'initializing',
    timestamp: new Date().toISOString(),
  })
}
