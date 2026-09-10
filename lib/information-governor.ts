export type InformationKind =
  | "analytics"
  | "commerce"
  | "creative"
  | "engineering"
  | "finance"
  | "knowledge"
  | "marketing"
  | "operations"
  | "research"
  | "security"
  | "unknown";

export type InformationRecord = {
  source: string;
  kind: InformationKind;
  payload: unknown;
  observedAt?: string;
  confidence?: number;
};

export type GovernedInformation = InformationRecord & {
  id: string;
  receivedAt: string;
  confidence: number;
  freshness: "fresh" | "stale" | "unknown";
  provenance: "declared" | "unknown";
  accepted: boolean;
  reason: string;
};

const MAX_CONFIDENCE = 1;

export function governInformation(input: InformationRecord): GovernedInformation {
  const now = Date.now();
  const observed = input.observedAt ? Date.parse(input.observedAt) : NaN;
  const ageHours = Number.isNaN(observed) ? Infinity : (now - observed) / 3_600_000;
  const confidence = Math.max(0, Math.min(MAX_CONFIDENCE, Number(input.confidence ?? 0.5)));
  const freshness = Number.isFinite(ageHours)
    ? ageHours <= 24 ? "fresh" : "stale"
    : "unknown";

  const accepted = Boolean(input.source && input.kind !== "unknown" && confidence >= 0.4);

  return {
    ...input,
    id: crypto.randomUUID(),
    receivedAt: new Date(now).toISOString(),
    confidence,
    freshness,
    provenance: input.source ? "declared" : "unknown",
    accepted,
    reason: accepted
      ? "Information passed governor thresholds."
      : "Rejected: missing source, unknown information kind, or confidence below threshold.",
  };
}
