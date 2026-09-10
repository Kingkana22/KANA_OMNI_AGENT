import { NextResponse } from "next/server";
import { executeCapability } from "@/lib/provider-gateway";
import type { Capability } from "@/lib/capability-router";

const allowed: Capability[] = ["web","code","analytics","knowledge","design","media","commerce","compute","cms"];

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const capability = String(body.capability) as Capability;
  const objective = String(body.objective || "").trim();
  if (!allowed.includes(capability) || !objective) return NextResponse.json({ ok:false, error:"capability and objective are required" }, { status:400 });
  const result = await executeCapability({ capability, input: body.input ?? {}, objective });
  return NextResponse.json(result, { status: result.ok ? 200 : 422 });
}
