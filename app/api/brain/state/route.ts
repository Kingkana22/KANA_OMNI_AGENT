import { NextResponse } from "next/server";

export type BrainState = {
  status: "ONLINE" | "PAUSED" | "ERROR";
  mode: "OBSERVE" | "PLAN" | "EXECUTE" | "EVOLVE";
  cycle: number;
  objective: string;
  lastDelta: string;
  updatedAt: string;
};

let state: BrainState = {
  status: "ONLINE",
  mode: "OBSERVE",
  cycle: 0,
  objective: "Initialize KANA Big Brain",
  lastDelta: "Vercel control plane initialized",
  updatedAt: new Date().toISOString(),
};

export async function GET() {
  return NextResponse.json({ ok: true, brain: state });
}

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));

  state = {
    ...state,
    ...body,
    cycle: Number.isFinite(Number(body.cycle)) ? Number(body.cycle) : state.cycle,
    updatedAt: new Date().toISOString(),
  };

  return NextResponse.json({ ok: true, brain: state });
}
