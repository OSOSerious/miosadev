# AI Governance & Token/Cost Controls

- Providers: Groq (instrumented), Moonshot (to instrument), unify via `app/core/ai/unified_service.py`.
- Guardrails: Local input gate for typos/unclear, prompt safety (no unstated assumptions), provider allowlist.
- Token/Cost: Per-call/session metrics, approximate cost by model; add per-session/token ceilings and backoff/circuit breakers.
- Metrics API: expose `get_session_metrics()` via HTTP for UI/CLI.
- Action Items:
  1) Route all agents through unified_service
  2) Instrument Moonshot like Groq
  3) Add per-session token budget + compression
  4) Centralize prompt construction helpers
