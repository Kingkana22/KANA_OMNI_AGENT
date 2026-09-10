import { NextResponse } from "next/server";

type CycleResult = {
  ok: boolean;
  cycle: number;
  status: "NO_PROGRESS" | "DELTA_DETECTED";
  delta: string;
  nextMode: "PLAN" | "EXECUTE" | "DIAGNOSE";
};

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const objective = String(body.objective || "Unnamed objective").trim();

  if (!objective) {
    return NextResponse.json({ ok: false, error: "Objective is required" }, { status: 400 });
  }

  const result: CycleResult = {
    ok: true,
    cycle: Date.now(),
    status: "DELTA_DETECTED",
    delta: `Objective registered: ${objective}`,
    nextMode: "PLAN",
  };

  return NextResponse.json(result);
}
