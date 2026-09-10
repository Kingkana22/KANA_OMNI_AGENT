import { NextResponse } from "next/server";

const connectors = [
  { id: "github", name: "GitHub", status: "available" },
  { id: "posthog", name: "PostHog", status: "available" },
  { id: "stripe", name: "Stripe", status: "available" },
  { id: "figma", name: "Figma", status: "available" },
  { id: "runway", name: "Runway", status: "available" },
  { id: "notion", name: "Notion", status: "available" },
  { id: "windsor", name: "Windsor.ai", status: "available" },
] as const;

export async function GET() {
  return NextResponse.json({
    ok: true,
    gateway: "KANA Connector Gateway",
    policy: "All external information must pass through the Information Governor before reaching Big Brain.",
    connectors,
  });
}
