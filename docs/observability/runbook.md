# Observability & Runbook

Logging
- Tag with session_id, agent_name.
- Log LLM call boxes + session summaries.
- Log preview lifecycle and background builds.

Dashboards
- Tokens, cost, calls, latency, fallback rate, errors by agent.

Incidents
- Hallucination → check local gate, tighten prompts.
- Progress jump → verify coordinator cap; add tests.
- Provider failure → circuit breaker, switch model/provider.
