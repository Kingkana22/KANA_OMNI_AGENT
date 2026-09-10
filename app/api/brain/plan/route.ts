import { NextResponse } from "next/server";
import { planObjective } from "@/lib/big-brain";
import { audit } from "@/lib/audit";

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const objective = String(body.objective || "").trim();

  if (!objective) {
    return NextResponse.json({ ok: false, error: "objective is required" }, { status: 400 });
  }

  try {
    const plan = await planObjective(objective, body.context);
    audit({ type: "BRAIN_DECISION", status: "SUCCESS", message: `Plan created for objective: ${objective}`, data: plan });
    return NextResponse.json({ ok: true, plan });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Big Brain planning failed.";
    audit({ type: "BRAIN_DECISION", status: "FAILURE", message });
    return NextResponse.json({ ok: false, error: message }, { status: 502 });
  }
}
