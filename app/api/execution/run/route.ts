import { NextResponse } from "next/server";
import { executeAction, type ExecutionAction } from "@/lib/execution-engine";

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const objective = String(body.objective || "").trim();
  const action = body.action as ExecutionAction | undefined;

  if (!objective || !action || typeof action !== "object") {
    return NextResponse.json({ ok: false, error: "objective and action are required" }, { status: 400 });
  }

  const result = await executeAction(objective, action);
  const status = result.outcome === "SUCCESS" ? 200 : result.outcome === "NO_PROGRESS" ? 409 : 422;
  return NextResponse.json({ ok: result.outcome === "SUCCESS", execution: result }, { status });
}
