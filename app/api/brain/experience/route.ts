import { NextResponse } from "next/server";

const experiences: Array<{
  id: string;
  objective: string;
  outcome: "SUCCESS" | "FAILURE" | "NO_PROGRESS";
  delta: string;
  timestamp: string;
}> = [];

export async function GET() {
  return NextResponse.json({ ok: true, experiences });
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const objective = String(body.objective || "").trim();
  const outcome = body.outcome;
  const delta = String(body.delta || "").trim();

  if (!objective || !["SUCCESS", "FAILURE", "NO_PROGRESS"].includes(outcome) || !delta) {
    return NextResponse.json(
      { ok: false, error: "objective, outcome and delta are required" },
      { status: 400 },
    );
  }

  const experience = {
    id: crypto.randomUUID(),
    objective,
    outcome,
    delta,
    timestamp: new Date().toISOString(),
  };

  experiences.push(experience);
  return NextResponse.json({ ok: true, experience }, { status: 201 });
}
