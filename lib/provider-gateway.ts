import { routeCapability, type Capability } from "./capability-router";
import { governInformation } from "./information-governor";

export type ProviderRequest = { capability: Capability; input: unknown; objective: string };
export type ProviderResult = { ok: boolean; provider: string; capability: Capability; output: unknown; governed: boolean; error?: string };

export async function executeCapability(request: ProviderRequest): Promise<ProviderResult> {
  const candidates = routeCapability(request.capability);
  const provider = candidates.find(p => p.configured) ?? candidates[0];
  if (!provider) return { ok: false, provider: "none", capability: request.capability, output: null, governed: false, error: "No provider registered" };

  if (provider.id === "vercel" && request.capability === "web") {
    return { ok: true, provider: provider.id, capability: request.capability, output: { status: "runtime-ready", input: request.input }, governed: true };
  }

  const governed = governInformation({ source: provider.id, kind: request.capability === "analytics" ? "analytics" : "unknown", payload: request.input, confidence: 0.5 });
  if (!governed.accepted) return { ok: false, provider: provider.id, capability: request.capability, output: null, governed: false, error: governed.reason };

  return { ok: false, provider: provider.id, capability: request.capability, output: { status: "adapter-ready", objective: request.objective }, governed: true, error: "Provider adapter requires its external API credentials and endpoint implementation." };
}
