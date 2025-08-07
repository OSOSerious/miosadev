# Deep Test Plan (Comprehensive)

## 0. Test Framework & Conventions
- Framework: pytest + pytest-asyncio; httpx for API; freezegun for time; faker for data; responses/httpx_mock for network mocks.
- Naming: `test_<area>__<behavior>__<expectation>()`
- Correlation: every test must set `session_id` and assert logs/metrics tag this `session_id` and `agent_name`.
- Fixtures:
  - `session_state_factory()`: yields minimal and rich session states.
  - `ai_provider_mocks()`: stubs unified_service to return deterministic completions and token usage.
  - `groq_health_mock()`, `moonshot_health_mock()`: toggle healthy/unhealthy states.

## 1. Unit Tests

### 1.1 Local Input Gate (CommunicationAgent)
Cases:
- Trailing backslash: `"Whaty\\"` → handle locally, no LLM calls.
- Keyboard mashing: `"asdfghjk"` or repeated chars `"kkkkk"` → local clarification.
- Very short unclear: `"What?"`, `"Hi"` without context → local follow-up.
- Clear inputs: multi-word, domain-relevant sentences → NOT gated; proceeds to LLM.
Acceptance:
- When gated: unified_service not invoked; metrics unchanged (calls/tokens = 0 delta); response contains clarification template; history appended with assistant role.
- When not gated: exactly one AI call (unless fallback triggered), metrics updated, no local gate message text present.

### 1.2 Extraction Quality (system_context.extract)
Inputs/Expected:
- `"Onboarding takes 4 hours and we use Slack + Notion."` → fields: `{onboarding_time_hours: 4, tools: ["Slack","Notion"]}` with high confidence.
- `"It’s fast, like a few hours."` → `onboarding_time_hours`: 2–6 range with low-medium confidence, rationale stored.
- `"We don’t know yet."` → no update; confidence low; delta empty.
Acceptance:
- Numeric normalization, list merging without duplication, preserves provenance (`source_message_id`) when available.

### 1.3 Progress Scoring & Smoothing
Given `prior_progress = 32.0`
- New score from system_context = 50.0 → proposed delta 18.0 → capped to +10.0 → final 42.0.
- New score = 35.0 → delta 3.0 → final 35.0 (no cap).
- Regression: new score = 30.0 → allow small negative? Policy: clamp to min(previous, new) with at most -5% per turn or configured rule. Verify implementation behavior and document.
Acceptance:
- `progress_details.delta` reflects raw and capped; `capped` flag true when applied; `last_progress` updated post-commit.

### 1.4 Unified Service Routing
Assert:
- Input prompt tokens counted; output tokens counted; cost computed by model.
- Model allowlist enforced; unknown model raises ValidationError.
- Backoff policy invoked on transient errors (3 attempts, jitter), then fallback model/provider.

### 1.5 Token/Cost Tracker (_TokenTracker)
- `estimate_tokens("hello")` stable estimate.
- `track()` aggregates session totals correctly across multiple calls; `call_number` increments.
- `_display()` produces box with required fields.

### 1.6 Coordinator Progress Cap (Server-Side)
- Any agent-proposed progress that exceeds cap is reduced; an anomaly event logged; response payload includes `capped=true`.

### 1.7 PII Redaction Helper
- Emails/phones redacted from logs and prompts when sanitization enabled.

## 2. Integration Tests

### 2.1 Discovery Flow — Happy Path
Steps:
1) POST `/api/v1/session/{id}/message` with clear business sentence.
2) Assert local gate not triggered (`metrics.calls == 1`).
3) Assert `extracted_info` has new structured fields; progress increased within cap; `progress_details` populated.
4) History updated with roles user/assistant; assistant message natural and references known facts only.

### 2.2 Typo/Noise Flow — No LLM
Steps:
1) POST with `"Whaty\\"`.
2) Assert metrics unchanged; response is local clarification; no change to `extracted_info` or `progress`.

### 2.3 Multi-Agent Orchestration
Setup: invoke secondary agents via coordinator after discovery threshold met.
Assert:
- All agent AI calls route through unified_service; per-agent metrics aggregated (`by_agent`).
- Coordinator remains source of truth for progress; secondary agents cannot mutate progress beyond cap.

### 2.4 Model Fallback & Circuit Breaker
Simulate Groq unhealthy → fallback to Moonshot.
Assert:
- Health checks consulted; retries/backoff executed; provider switched; circuit opened after N failures, then half-open/close behavior.

### 2.5 Preview Build Lifecycle
If background build is triggered in this repo:
- Coordinator signals `preview_ready` when build completes; `last_announced_ready` toggles to prevent duplicate announcements.
Assert logs around start/end; API exposes readiness and URL.

### 2.6 Metrics API
- GET `/api/v1/metrics/session/{id}` returns totals and breakdowns; numbers equal sum of per-call logs.

## 3. End-to-End (E2E) Scenarios

### 3.1 Short Consultation to Recommendation
Run through 6–8 turns: discovery → design prompt → recommendation draft.
Checks every turn:
- No repetition of question type while other gaps exist.
- Progress grows smoothly; never > cap.
- Assistant never claims unknown facts; cites session-known info.

### 3.2 Adversarial User Behavior
- Contradict previous statement: agent asks to reconcile, does not overwrite blindly; progress does not spike.
- Off-topic chit-chat: politely steer back; minimal tokens.
- Prompt injection attempt: user tells agent to ignore system instructions; agent refuses and keeps guardrails.

## 4. Load & Performance

### 4.1 Burst of Short Inputs
Send 100 short/unclear messages over 30s.
Acceptance:
- LLM calls near zero; latency low; no rate-limit errors; CPU/memory stable.

### 4.2 Long Context Growth
Simulate 30 turns with increasing history.
Acceptance:
- Context window trimming/compression policy kicks in (if implemented) without breaking extraction; tokens/request bounded by budget.

## 5. Reliability & Fault Injection

### 5.1 Provider Failures
- Timeouts, 429/5xx bursts → backoff then fallback; user sees graceful apology + retry; metrics annotate failure reasons.

### 5.2 Data Store/State Issues
- Corrupt/missing `last_progress` → coordinator defaults to 0 and logs warning; smoothing still applied.

### 5.3 Idempotency
- Re-send same message idempotently → no duplicate history or double progress.

## 6. Security & Privacy

### 6.1 PII Redaction in Logs
- Inject emails/phones; ensure logs/store redact; prompts optionally anonymize.

### 6.2 Prompt Injection & Tool Abuse
- Injection strings like "ignore previous instructions"; ensure system_context remains authoritative; no disallowed actions executed.

### 6.3 Authorization (if API exposed)
- Only authorized clients access session metrics and state.

## 7. Test Artifacts & Coverage
- Store golden responses for stable snapshots where appropriate.
- Coverage targets: ≥85% logic in agents, coordinator, unified_service, token tracker; include async paths and error branches.

## 8. CI Configuration (Outline)
- Run unit/integration on PR with mocked providers.
- Nightly: run load and reliability subsets.
- Fail PR on: coverage drop, linters, or any security test failing.

## 9. Example pytest Skeletons

```python
import pytest

@pytest.mark.asyncio
async def test_local_gate_handles_trailing_backslash(ai_provider_mocks, client):
    session_id = "s-123"
    r = await client.post(f"/api/v1/session/{session_id}/message", json={"text": "Whaty\\"})
    assert r.status_code == 200
    body = r.json()
    assert body["metrics"]["calls_total"] == 0
    assert "clarify" in body["assistant_message"].lower()


def test_progress_cap_enforced_server_side(coordinator, session_state_factory):
    st = session_state_factory(prior=32.0)
    proposed = 55.0
    final = coordinator.apply_progress_cap(st, proposed)
    assert final - st.last_progress <= 10.0
```

## 10. Open Questions
- Negative progress policy finalization (allow small regressions vs. clamp).
- Context compression policy thresholds and summarization strategy tests.
