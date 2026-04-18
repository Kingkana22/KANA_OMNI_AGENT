# RESEARCH DATA: GitHub_-_vercel-chatbot:_A_full-featured,_hackable_Next.js_AI_chatbot_built_by_Vercel_·_GitHub
SOURCE URL: https://github.com/vercel/chatbot
DATE: Thu Apr 16 04:22:10 2026
--------------------------------------------------

Skip to content
Navigation Menu
Sign in
Appearance settings
Appearance settings
Dismiss alert
vercel
/
chatbot
Public template
You must be signed in to change notification settings
Code
Issues
5
Pull requests
10
Actions
Security and quality
Additional navigation options
vercel/chatbot
 main
Go to file
Code
Folders and files
Name Last commit message Last commit date
Latest commit
dancer
update links in README.md (#1476)
2 weeks ago
146b3cb
 · 2 weeks ago
Apr 2, 2026
History
.cursor/rules
Restore Ultracite + fix sidebar (#1233)
7 months agoSep 22, 2025
.github/workflows
feat: v1 — persistent shell, model gateway, artifact improvements (
last monthMar 20, 2026
.vscode
fix: title generation + ai sdk upgrade (#1392)
3 months agoJan 16, 2026
app
feat: v1 — persistent shell, model gateway, artifact improvements (
last monthMar 20, 2026
artifacts
feat: v1 — persistent shell, model gateway, artifact improvements (
last monthMar 20, 2026
components
feat: v1 — persistent shell, model gateway, artifact improvements (
last monthMar 20, 2026
hooks
feat: v1 — persistent shell, model gateway, artifact improvements (
last monthMar 20, 2026
lib
feat: v1 — persistent shell, model gateway, artifact improvements (
last monthMar 20, 2026
public
feat: v1 — persistent shell, model gateway, artifact improvements (
last monthMar 20, 2026
tests
feat: v1 — persistent shell, model gateway, artifact improvements (
last monthMar 20, 2026
last month
last month
2 years ago
2 weeks ago
last month
last month
last month
last month
2 months ago
last month
last month
4 months ago
last month
7 months ago
last month
5 months ago
7 months ago
last month
View all files
Repository files navigation
README
License
Security
Chatbot
Chatbot (formerly AI Chatbot) is a free, open-source template built with Next.js and the AI SDK that helps you quickly build powerful chatbot applications.
Read Docs · Features · Model Providers · Deploy Your Own · Running locally

Features
Next.js App Router
Advanced routing for seamless navigation and performance
React Server Components (RSCs) and Server Actions for server-side rendering and increased performance
AI SDK
Unified API for generating text, structured objects, and tool calls with LLMs
Hooks for building dynamic chat and generative user interfaces
Supports OpenAI, Anthropic, Google, xAI, and other model providers via AI Gateway
shadcn/ui
Styling with Tailwind CSS
Component primitives from Radix UI for accessibility and flexibility
Data Persistence
Neon Serverless Postgres for saving chat history and user data
Vercel Blob for efficient file storage
Auth.js
Simple and secure authentication
Model Providers
This template uses the Vercel AI Gateway to access multiple AI models through a unified interface. Models are configured in lib/ai/models.ts with per-model provider routing. Included models: Mistral, Moonshot, DeepSeek, OpenAI, and xAI.
AI Gateway Authentication
For Vercel deployments: Authentication is handled automatically via OIDC tokens.
For non-Vercel deployments: You need to provide an AI Gateway API key by setting the AI_GATEWAY_API_KEY environment variable in your .env.local file.
With the AI SDK, you can also switch to direct LLM providers like OpenAI, Anthropic, Cohere, and many more with just a few lines of code.
Deploy Your Own
You can deploy your own version of Chatbot to Vercel with one click:
Running locally
You will need to use the environment variables defined in .env.example to run Chatbot. It's recommended you use Vercel Environment Variables for this, but a .env file is all that is necessary.
Note: You should not commit your .env file or it will expose secrets that will allow others to control access to your various AI and authentication provider accounts.
Install Vercel CLI: npm i -g vercel
Link local instance with Vercel and GitHub accounts (creates .vercel directory): vercel link
Download your environment variables: vercel env pull
pnpm install
pnpm db:migrate # Setup database or apply latest database changes
pnpm dev
Your app template should now be running on localhost:3000.
Contributors
85
+ 71 contributors
Languages
TypeScript
96.0%
JavaScript
2.2%
CSS
1.8%
Footer
© 2026 GitHub, Inc.
Footer navigation
Terms
Privacy
Security
Status
Community
Docs
Contact
Manage cookies
Do not share my personal information