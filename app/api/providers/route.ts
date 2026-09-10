import { NextResponse } from "next/server";
import { capabilityMatrix } from "@/lib/capability-router";

export async function GET() {
  return NextResponse.json({ ok: true, providers: capabilityMatrix() });
}
