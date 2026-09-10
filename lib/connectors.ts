export const connectorRegistry = [
  { id: "github", name: "GitHub", env: "GITHUB_TOKEN", capabilities: ["repository", "issues", "pull_requests", "files"] },
  { id: "posthog", name: "PostHog", env: "POSTHOG_API_KEY", capabilities: ["analytics", "events", "feature_flags"] },
  { id: "stripe", name: "Stripe", env: "STRIPE_SECRET_KEY", capabilities: ["customers", "products", "payments"] },
  { id: "figma", name: "Figma", env: "FIGMA_ACCESS_TOKEN", capabilities: ["files", "design"] },
  { id: "runway", name: "Runway", env: "RUNWAY_API_KEY", capabilities: ["generation", "media"] },
  { id: "notion", name: "Notion", env: "NOTION_TOKEN", capabilities: ["pages", "databases", "search"] },
  { id: "windsor", name: "Windsor.ai", env: "WINDSOR_API_KEY", capabilities: ["marketing_data", "attribution"] },
] as const;

export function connectorStatus() {
  return connectorRegistry.map((connector) => ({
    ...connector,
    configured: Boolean(process.env[connector.env]),
  }));
}
