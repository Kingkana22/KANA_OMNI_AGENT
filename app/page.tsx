"use client";

import { useEffect, useState } from "react";

type Brain = { status: string; mode: string; cycle: number; objective: string; lastDelta: string; updatedAt: string };
type Connector = { id: string; name: string; configured: boolean; capabilities: readonly string[] };

const initialBrain: Brain = {
  status: "ONLINE",
  mode: "OBSERVE",
  cycle: 0,
  objective: "Initialize KANA Big Brain",
  lastDelta: "Vercel control plane initialized",
  updatedAt: "",
};

export default function Home() {
  const [brain, setBrain] = useState(initialBrain);
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [objective, setObjective] = useState("");
  const [plan, setPlan] = useState<any>(null);
  const [audit, setAudit] = useState<any[]>([]);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("Ready");

  async function refresh() {
    const [brainRes, connectorRes, auditRes] = await Promise.all([
      fetch("/api/brain/state"),
      fetch("/api/connectors"),
      fetch("/api/audit?limit=25"),
    ]);
    if (brainRes.ok) setBrain((await brainRes.json()).brain);
    if (connectorRes.ok) setConnectors((await connectorRes.json()).connectors);
    if (auditRes.ok) setAudit((await auditRes.json()).events);
  }

  useEffect(() => { refresh().catch(() => setMessage("Control plane refresh failed")); }, []);

  async function createPlan() {
    if (!objective.trim()) return;
    setBusy(true);
    setMessage("Big Brain is reasoning...");
    try {
      const response = await fetch("/api/brain/plan", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ objective }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Planning failed");
      setPlan(data.plan);
      setMessage("Plan created and audited");
      await refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Planning failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main style={{ minHeight: "100vh", background: "#08090b", color: "#f5f7fa", padding: 32, fontFamily: "Arial, sans-serif" }}>
      <section style={{ maxWidth: 1180, margin: "0 auto" }}>
        <div style={{ opacity: 0.55, letterSpacing: 4, fontSize: 11 }}>KANA SOVEREIGN CORE / CONTROL PLANE</div>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 20, alignItems: "end", flexWrap: "wrap" }}>
          <div>
            <h1 style={{ fontSize: 48, margin: "14px 0 8px" }}>BIG BRAIN</h1>
            <p style={{ opacity: 0.65, maxWidth: 760, lineHeight: 1.6 }}>Objective → Reason → Plan → Execute → Verify → Experience → Evolve.</p>
          </div>
          <div style={{ border: "1px solid #29303a", borderRadius: 999, padding: "8px 14px", fontSize: 12 }}>{brain.status} / {brain.mode}</div>
        </div>

        <div style={{ marginTop: 28, display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(210px,1fr))", gap: 12 }}>
          {["Big Brain", "Information Governor", "Execution", "Verification", "Experience", "Evolution"].map((item) => (
            <div key={item} style={{ border: "1px solid #24272d", padding: 18, borderRadius: 10, background: "#0e1014" }}>
              <div style={{ fontSize: 10, opacity: 0.45, letterSpacing: 2 }}>SYSTEM</div>
              <div style={{ marginTop: 9, fontSize: 17 }}>{item}</div>
              <div style={{ marginTop: 10, fontSize: 11, opacity: 0.5 }}>ACTIVE</div>
            </div>
          ))}
        </div>

        <section style={{ marginTop: 18, border: "1px solid #24272d", borderRadius: 12, padding: 22, background: "#0c0e12" }}>
          <div style={{ fontSize: 11, opacity: 0.5, letterSpacing: 2 }}>OBJECTIVE</div>
          <div style={{ display: "flex", gap: 10, marginTop: 12, flexWrap: "wrap" }}>
            <input value={objective} onChange={(e) => setObjective(e.target.value)} onKeyDown={(e) => e.key === "Enter" && createPlan()} placeholder="Give KANA a measurable objective..." style={{ flex: 1, minWidth: 260, background: "#08090b", color: "white", border: "1px solid #30343c", borderRadius: 8, padding: 13 }} />
            <button disabled={busy} onClick={createPlan} style={{ border: "1px solid #d8dde5", background: "#f5f7fa", color: "#08090b", borderRadius: 8, padding: "0 18px", fontWeight: 700 }}>{busy ? "THINKING..." : "PLAN"}</button>
          </div>
          <div style={{ marginTop: 10, fontSize: 12, opacity: 0.55 }}>{message}</div>
        </section>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(320px,1fr))", gap: 18, marginTop: 18 }}>
          <section style={{ border: "1px solid #24272d", borderRadius: 12, padding: 22, background: "#0c0e12" }}>
            <div style={{ fontSize: 11, opacity: 0.5, letterSpacing: 2 }}>BRAIN STATE</div>
            <pre style={{ whiteSpace: "pre-wrap", fontSize: 12, lineHeight: 1.7, opacity: 0.78 }}>{JSON.stringify(brain, null, 2)}</pre>
          </section>
          <section style={{ border: "1px solid #24272d", borderRadius: 12, padding: 22, background: "#0c0e12" }}>
            <div style={{ fontSize: 11, opacity: 0.5, letterSpacing: 2 }}>CONNECTOR GATEWAY</div>
            <div style={{ marginTop: 12, display: "grid", gap: 9 }}>{connectors.map((c) => <div key={c.id} style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid #20242b", paddingBottom: 8, fontSize: 13 }}><span>{c.name}</span><span style={{ opacity: 0.55 }}>{c.configured ? "CONFIGURED" : "ADAPTER READY"}</span></div>)}</div>
          </section>
        </div>

        {plan && <section style={{ marginTop: 18, border: "1px solid #24272d", borderRadius: 12, padding: 22, background: "#0c0e12" }}>
          <div style={{ fontSize: 11, opacity: 0.5, letterSpacing: 2 }}>LATEST PLAN</div>
          <h2 style={{ fontSize: 20 }}>{plan.strategy}</h2>
          <p style={{ opacity: 0.7 }}>{plan.interpretation}</p>
          <pre style={{ whiteSpace: "pre-wrap", fontSize: 12, lineHeight: 1.6, opacity: 0.78 }}>{JSON.stringify(plan.actions, null, 2)}</pre>
        </section>}

        <section style={{ marginTop: 18, border: "1px solid #24272d", borderRadius: 12, padding: 22, background: "#0c0e12" }}>
          <div style={{ fontSize: 11, opacity: 0.5, letterSpacing: 2 }}>AUDIT STREAM</div>
          <div style={{ marginTop: 12, display: "grid", gap: 8 }}>{audit.length ? audit.map((event) => <div key={event.id} style={{ fontSize: 12, borderBottom: "1px solid #20242b", padding: "8px 0" }}><b>{event.status}</b> — {event.message}<span style={{ opacity: 0.4, marginLeft: 8 }}>{event.timestamp}</span></div>) : <div style={{ opacity: 0.5, fontSize: 12 }}>No events yet.</div>}</div>
        </section>
      </section>
    </main>
  );
}
