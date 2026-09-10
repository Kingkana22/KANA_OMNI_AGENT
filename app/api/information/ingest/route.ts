import { NextResponse } from "next/server";
import { governInformation, type InformationRecord } from "@/lib/information-governor";

export async function POST(request: Request) {
  const body = (await request.json().catch(() => null)) as Partial<InformationRecord> | null;

  if (!body || typeof body.source !== "string" || !body.payload) {
    return NextResponse.json(
      { ok: false, error: "source and payload are required" },
      { status: 400 },
    );
  }

  const governed = governInformation({
    source: body.source,
    kind: body.kind ?? "unknown",
    payload: body.payload,
    observedAt: body.observedAt,
    confidence: body.confidence,
  });

  return NextResponse.json({ ok: true, information: governed }, {
    status: governed.accepted ? 200 : 422,
  });
}
