export type Capability = "web" | "code" | "analytics" | "knowledge" | "design" | "media" | "commerce" | "compute" | "cms";

export type Provider = { id: string; capability: Capability; priority: number; configured: boolean };

const providers: Provider[] = [
  { id: "vercel", capability: "web", priority: 1, configured: true },
  { id: "codex", capability: "code", priority: 1, configured: Boolean(process.env.CODEX_TASKS_ENABLED) },
  { id: "github", capability: "code", priority: 2, configured: Boolean(process.env.GITHUB_TOKEN) },
  { id: "posthog", capability: "analytics", priority: 1, configured: Boolean(process.env.POSTHOG_API_KEY) },
  { id: "notion", capability: "knowledge", priority: 1, configured: Boolean(process.env.NOTION_TOKEN) },
  { id: "figma", capability: "design", priority: 1, configured: Boolean(process.env.FIGMA_ACCESS_TOKEN) },
  { id: "runway", capability: "media", priority: 1, configured: Boolean(process.env.RUNWAY_API_KEY) },
  { id: "stripe", capability: "commerce", priority: 1, configured: Boolean(process.env.STRIPE_SECRET_KEY) },
  { id: "wpvibe", capability: "cms", priority: 1, configured: Boolean(process.env.WPVIBE_API_KEY) },
  { id: "huggingface", capability: "compute", priority: 1, configured: Boolean(process.env.HUGGINGFACE_API_KEY) },
  { id: "cerebrium", capability: "compute", priority: 2, configured: Boolean(process.env.CEREBRIUM_API_KEY) },
  { id: "nvidia", capability: "compute", priority: 3, configured: Boolean(process.env.NVIDIA_API_KEY) },
  { id: "amd", capability: "compute", priority: 4, configured: Boolean(process.env.AMD_API_KEY) },
];

export function routeCapability(capability: Capability) {
  return providers.filter(p => p.capability === capability).sort((a,b) => Number(b.configured) - Number(a.configured) || a.priority - b.priority);
}

export function capabilityMatrix() { return providers; }
