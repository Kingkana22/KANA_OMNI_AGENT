import { NextResponse } from "next/server";
import { connectorStatus } from "@/lib/connectors";

export async function GET() {
  return NextResponse.json({
    ok: true,
    gateway: "KANA Connector Gateway",
    policy: "External information must pass through the Information Governor before reaching Big Brain.",
    connectors: connectorStatus(),
  });
}
