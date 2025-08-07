# Unified AI Routing Service — Technical Spec

Purpose
- Provide a single entrypoint for all LLM calls with consistent guardrails, metrics, retries, and fallbacks.

API (Python signature)
```python
async def complete(
    *,
    session_id: str,
    agent_name: str,
    messages: list[dict],  # [{role: system|user|assistant, content: str}]
    model_prefs: list[str] = ("llama3-groq-70b-8192", "llama3-groq-8b-8192"),
    provider_prefs: list[str] = ("groq", "moonshot"),
    max_tokens: int = 1024,
    temperature: float = 0.2,
    timeout_s: float = 30.0,
    budget_guard: bool = True,
) -> dict:
    """Return {text, model, provider, usage:{prompt_tokens, completion_tokens}, cost, latency_ms, ok} or raise."""
```

Responsibilities
- Model/provider allowlist and preference order
- Health check gating (skip unhealthy backends)
- Retry/backoff (exponential with jitter) on 429/5xx/timeouts
- Circuit breaker per provider+model (open after N failures in window, half-open probes)
- Token and cost estimation + per-session aggregation
- Prompt sanitation (PII redaction, secrets filtering) before dispatch
- Context compression when token budget near limits (summary window / distillation)

Data Contracts
- Inputs
  - messages: validated roles; system message comes first; user last
  - session_id, agent_name required for metrics scoping
- Outputs
  - usage: exact if provider gives; else estimated via tokenizer
  - cost: computed by pricing table; per-provider overrideable
  - errors: structured {type, provider, model, attempt, status, message}

Retry & Backoff
- Attempts: up to 3 per provider+model
- Base backoff: 0.5s * 2^attempt + jitter(0..200ms)
- Switch provider when:
  - provider in open state OR
  - all preferred models exhausted with non-retryable errors

Circuit Breaker
- Threshold: 5 failures in 60s window → open for 120s
- Half-open: allow 1 probe; close on success; reopen on failure

Budget Guardrails
- Per-request: max_tokens_out cap (default 1024)
- Per-session: token_budget (configurable); when exceeded:
  - compress history (latest-k + summarized-older)
  - or return error with guidance

Prompt Sanitation
- Remove emails/phones if sanitization enabled for logs; anonymize user IDs
- Escape or neutralize injection patterns (e.g., "ignore previous instructions") by reinforcing system instruction preamble

Metrics Schema
```json
{
  "session_id": "...",
  "agent_name": "CommunicationAgent",
  "provider": "groq",
  "model": "llama3-groq-70b-8192",
  "latency_ms": 812,
  "usage": {"prompt_tokens": 324, "completion_tokens": 186},
  "cost": 0.0023,
  "call_number": 7,
  "ok": true,
  "ts": "2025-08-08T05:12:00Z"
}
```

Validation Rules
- Reject unknown roles
- Require at least one user message
- Enforce model/provider allowlist

Examples
- Provider down → fallback path to Moonshot; cost/usage aggregated; logs annotated with fallback=true
- Token budget exceeded → summary of history injected; completion limited to 300 tokens

Checklist (Implementation)
- [ ] Centralize provider adapters with a common interface
- [ ] Implement health registry and breaker per (provider, model)
- [ ] Add tokenizer-based token counts per provider
- [ ] Add context compressor (semantic or sliding-window summarizer)
- [ ] Wire per-session budget + enforcement hooks
- [ ] Emit metrics to coordinator and optional /metrics API
