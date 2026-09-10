import { audit } from "@/lib/audit";
import { checkRetryAllowed, registerFailure } from "@/lib/anti-loop";

export type ExecutionAction = {
  id?: string;
  type: "http" | "connector" | "analysis";
  target: string;
  input?: unknown;
  expected?: string;
  assumptions?: string[];
  strategy?: string;
  parameters?: Record<string, unknown>;
};

export type ExecutionOutcome = "SUCCESS" | "FAILURE" | "NO_PROGRESS";

const CONNECTORS = new Set(["github", "posthog", "stripe", "figma", "runway", "notion", "windsor"]);

function normalizeTarget(target: string) {
  return target.trim().toLowerCase();
}

function validate(action: ExecutionAction) {
  if (!action.type || !action.target) return "type and target are required";
  if (action.type === "connector" && !CONNECTORS.has(normalizeTarget(action.target))) {
    return `Connector '${action.target}' is not registered.`;
  }
  if (action.type === "http") {
    try {
      const url = new URL(action.target);
      if (!["http:", "https:"].includes(url.protocol)) return "Only HTTP(S) targets are allowed.";
    } catch {
      return "HTTP target must be a valid URL.";
    }
  }
  return null;
}

async function runAdapter(action: ExecutionAction) {
  if (action.type === "analysis") {
    return { ok: true, kind: "analysis", result: action.input ?? null };
  }

  if (action.type === "connector") {
    return {
      ok: false,
      kind: "connector",
      connector: action.target,
      error: "Connector adapter is registered but credentials/API operation are not configured yet.",
    };
  }

  const response = await fetch(action.target, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(action.input ?? {}),
    signal: AbortSignal.timeout(15000),
  });

  const text = await response.text();
  return {
    ok: response.ok,
    status: response.status,
    result: text.slice(0, 12000),
  };
}

function verify(action: ExecutionAction, result: unknown): { outcome: ExecutionOutcome; delta: string } {
  if (action.type === "connector" && typeof result === "object" && result !== null && "ok" in result && (result as { ok: boolean }).ok === false) {
    return { outcome: "FAILURE", delta: "Connector execution is not configured." };
  }

  if (typeof result === "object" && result !== null && "ok" in result && (result as { ok: boolean }).ok === false) {
    return { outcome: "FAILURE", delta: "Execution adapter reported failure." };
  }

  if (action.expected) {
    const serialized = JSON.stringify(result);
    if (!serialized.includes(action.expected)) {
      return { outcome: "NO_PROGRESS", delta: "Execution completed but the expected verification marker was not found." };
    }
  }

  return { outcome: "SUCCESS", delta: `Verified ${action.type} execution against ${action.target}.` };
}

export async function executeAction(objective: string, action: ExecutionAction) {
  const executionId = crypto.randomUUID();
  const validationError = validate(action);

  if (validationError) {
    audit({ executionId, type: "BLOCKED", status: "FAILURE", message: validationError, data: action });
    return { executionId, outcome: "FAILURE" as const, delta: validationError };
  }

  const retry = checkRetryAllowed({
    objective,
    type: action.type,
    target: action.target,
    assumptions: action.assumptions,
    strategy: action.strategy,
    parameters: action.parameters,
  });

  if (!retry.allowed) {
    audit({ executionId, type: "BLOCKED", status: "FAILURE", message: retry.reason, data: { action, previousFailure: retry.previousFailure } });
    return { executionId, outcome: "FAILURE" as const, delta: retry.reason, blocked: true, fingerprint: retry.fingerprint };
  }

  audit({ executionId, type: "EXECUTION_STARTED", status: "INFO", message: `Executing ${action.type} against ${action.target}.`, data: action });

  try {
    const result = await runAdapter(action);
    const verification = verify(action, result);

    audit({ executionId, type: "EXECUTION_RESULT", status: verification.outcome, message: verification.delta, data: result });
    audit({ executionId, type: "VERIFICATION", status: verification.outcome, message: verification.delta, data: { expected: action.expected } });

    if (verification.outcome === "FAILURE") {
      registerFailure({
        fingerprint: retry.fingerprint,
        objective,
        actionType: action.type,
        target: action.target,
        assumptions: action.assumptions ?? [],
        strategy: action.strategy ?? "default",
        parameters: action.parameters ?? {},
        reason: verification.delta,
      });
    }

    return { executionId, ...verification, result, fingerprint: retry.fingerprint };
  } catch (error) {
    const delta = error instanceof Error ? error.message : "Unknown execution error";
    registerFailure({
      fingerprint: retry.fingerprint,
      objective,
      actionType: action.type,
      target: action.target,
      assumptions: action.assumptions ?? [],
      strategy: action.strategy ?? "default",
      parameters: action.parameters ?? {},
      reason: delta,
    });
    audit({ executionId, type: "EXECUTION_RESULT", status: "FAILURE", message: delta });
    return { executionId, outcome: "FAILURE" as const, delta, fingerprint: retry.fingerprint };
  }
}
