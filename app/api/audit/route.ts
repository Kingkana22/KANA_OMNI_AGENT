import { NextResponse } from "next/server";
import { listAudit } from "@/lib/audit";
import { listFailures } from "@/lib/anti-loop";

export async function GET(request: Request) {
  const url = new URL(request.url);
  const limit = Number(url.searchParams.get("limit") || 100);
  return NextResponse.json({ ok: true, events: listAudit(limit), failures: listFailures() });
}
