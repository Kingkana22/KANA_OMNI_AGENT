export type AuditEvent = {
  id: string;
  executionId?: string;
  type: "EXECUTION_STARTED" | "EXECUTION_RESULT" | "VERIFICATION" | "BLOCKED" | "BRAIN_DECISION" | "SYSTEM";
  status: "INFO" | "SUCCESS" | "FAILURE" | "NO_PROGRESS";
  message: string;
  data?: unknown;
  timestamp: string;
};

const events: AuditEvent[] = [];

export function audit(event: Omit<AuditEvent, "id" | "timestamp">) {
  const item: AuditEvent = {
    ...event,
    id: crypto.randomUUID(),
    timestamp: new Date().toISOString(),
  };
  events.push(item);
  return item;
}

export function listAudit(limit = 100) {
  return events.slice(-Math.max(1, Math.min(limit, 500))).reverse();
}
