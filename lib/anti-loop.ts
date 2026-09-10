import crypto from "node:crypto";

export type FailureRecord = {
  fingerprint: string;
  objective: string;
  actionType: string;
  target: string;
  assumptions: string[];
  strategy: string;
  parameters: Record<string, unknown>;
  failedAt: string;
  reason: string;
};

const failures: FailureRecord[] = [];

function stable(value: unknown): string {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(stable).join(",")}]`;
  return `{${Object.keys(value as Record<string, unknown>).sort().map((k) => `${JSON.stringify(k)}:${stable((value as Record<string, unknown>)[k])}`).join(",")}}`;
}

export function fingerprintAction(input: {
  objective: string;
  type: string;
  target: string;
  assumptions?: string[];
  strategy?: string;
  parameters?: Record<string, unknown>;
}) {
  return crypto.createHash("sha256").update(stable(input)).digest("hex");
}

export function registerFailure(record: Omit<FailureRecord, "failedAt">) {
  failures.push({ ...record, failedAt: new Date().toISOString() });
}

export function checkRetryAllowed(input: {
  objective: string;
  type: string;
  target: string;
  assumptions?: string[];
  strategy?: string;
  parameters?: Record<string, unknown>;
}) {
  const fingerprint = fingerprintAction(input);
  const previous = failures.find((item) => item.fingerprint === fingerprint);
  return {
    allowed: !previous,
    fingerprint,
    previousFailure: previous ?? null,
    reason: previous
      ? "Identical action under identical conditions is blocked after verified failure. Change strategy, assumptions, parameters, or capability."
      : "No identical verified failure found.",
  };
}

export function listFailures() {
  return [...failures].reverse();
}
