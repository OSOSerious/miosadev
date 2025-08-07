# Agent Connectivity Map

Purpose: Document how agents connect, what services they call, and data that flows between them.

- Entry: `CommunicationAgent`
- Downstream Agents: Backend, Frontend, Database, Deployment, Quality, Analysis, MCP Integration
- AI Routing: Prefer `app/core/ai/unified_service.ai_service` for all calls
- Context Sources: `system_context`, `miosa_capabilities`, session state in coordinator
- Orchestration: `orchestration/coordinator.py` is source of truth for session, phase, and progress caps

Actions:
- Migrate direct `groq_service` usages to `unified_service`
- Instrument all providers for tokens/costs
- Standardize prompts via `system_context`
