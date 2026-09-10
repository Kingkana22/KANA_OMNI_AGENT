type BrainPlan = {
  objective: string;
  interpretation: string;
  assumptions: string[];
  strategy: string;
  actions: Array<{
    type: "analysis" | "http" | "connector";
    target: string;
    input?: unknown;
    expected?: string;
    assumptions?: string[];
    strategy?: string;
    parameters?: Record<string, unknown>;
  }>;
  successCriteria: string[];
};

const SYSTEM = `You are KANA Big Brain. You are the reasoning and planning layer of a sovereign autonomous digital intelligence system.
Return ONLY valid JSON matching this schema:
{"objective":string,"interpretation":string,"assumptions":string[],"strategy":string,"actions":[{"type":"analysis|http|connector","target":string,"input":any,"expected":string,"assumptions":string[],"strategy":string,"parameters":object}],"successCriteria":string[]}
Rules:
- Prefer the smallest verifiable action sequence.
- Never claim an action happened unless the execution layer reports it.
- Use registered connectors only: github, posthog, stripe, figma, runway, notion, windsor.
- Do not invent credentials or connector capabilities.
- If an objective is ambiguous, state assumptions explicitly.
- Every action must have a verification path.`;

function extractText(data: any): string {
  if (typeof data?.output_text === "string") return data.output_text;
  const chunks = data?.output?.flatMap((item: any) => item?.content ?? []) ?? [];
  return chunks.map((item: any) => item?.text ?? "").join("");
}

export async function planObjective(objective: string, context?: unknown): Promise<BrainPlan> {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) throw new Error("OPENAI_API_KEY is not configured.");

  const response = await fetch("https://api.openai.com/v1/responses", {
    method: "POST",
    headers: {
      authorization: `Bearer ${apiKey}`,
      "content-type": "application/json",
    },
    body: JSON.stringify({
      model: process.env.KANA_BRAIN_MODEL || "gpt-5.6-luna",
      instructions: SYSTEM,
      input: JSON.stringify({ objective, context: context ?? null }),
    }),
    signal: AbortSignal.timeout(60000),
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(`Big Brain API error ${response.status}: ${message.slice(0, 2000)}`);
  }

  const data = await response.json();
  const text = extractText(data).trim();
  const json = JSON.parse(text.replace(/^```json\s*/i, "").replace(/```$/i, ""));

  if (!json.objective || !json.strategy || !Array.isArray(json.actions)) {
    throw new Error("Big Brain returned an invalid plan.");
  }

  return json as BrainPlan;
}
