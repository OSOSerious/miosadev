# Agent Connectivity and Data Flow — Deep Dive

Scope
- Enumerates every agent, their responsibilities, inputs/outputs, and AI routing contract.
- Defines canonical data contracts (session, message, extraction, progress).
- Maps call graphs and sequencing for common flows with failure modes and retries.

Glossary
- Session: A consultation lifecycle identified by session_id.
- Turn: One user input plus agent response.
- AI Call: Any LLM provider invocation routed via unified_service.

Agents Overview
- CommunicationAgent (entrypoint)
  - Role: Dialogue, information extraction, progress computation, phase recommendation.
  - Inputs: session.state (history, extracted_info, progress), user_message.
  - Outputs: assistant_message, extracted_deltas, proposed_progress, next_question (if needed).
  - AI Calls: Should exclusively use unified_service.ai_service (Groq primary, Moonshot optional fallback) with system_context prompts.
  - Guardrails: Local input gate; schema-based extraction; anti-repetition; hallucination avoidance.
- BackendDeveloperAgent
  - Role: Propose service APIs, data models, and integration points; optionally generate code patches.
  - Inputs: system_context, extracted_info, design decisions.
  - Outputs: API specs, code plan, patches.
  - AI Calls: unified_service only; token/cost metered.
- FrontendDeveloperAgent, DatabaseArchitectAgent, DeploymentAgent, QualityAgent, AnalysisAgent, MCPIntegrationAgent
  - Same pattern: read session context → produce domain plans/artifacts → coordinated by coordinator.

Canonical Data Contracts
- SessionState
  - session_id: str
  - phase: enum [discovery, design, recommendation, build, review]
  - history: [Message] (role: user|assistant|agent, content, ts, agent_name)
  - extracted_info: Dict[str, Any] (schema-driven)
  - progress: float [0..100]
  - last_progress: float [0..100]
  - progress_details: { breakdown: [{dim, weight, score, rationale}], delta, capped }
  - metrics: { calls, input_tokens, output_tokens, cost, by_agent: {...}, by_provider: {...} }
  - preview: { ready: bool, url: Optional[str], last_announced_ready: bool }
- Message
  - role, content, ts, agent_name, tokens_in, tokens_out, model, provider, cost
- ExtractionDelta
  - fields: { name, new_value, confidence, source_message_id, notes }

Call Graphs
- Discovery turn (happy path)
  1) coordinator.receive(user_message)
  2) CommunicationAgent.local_gate(user_message) → if hit: respond locally, metrics unaffected
  3) CommunicationAgent.think() via unified_service → prompts from system_context
  4) Extract with system_context.extract() → merge_delta(extracted_info)
  5) Score progress via system_context.score() → cap via coordinator
  6) coordinator.persist(state) → append to history, update metrics, emit response
- Failure paths
  - Provider timeout → unified_service retries with backoff; fallback model/provider; circuit-breaker tripped after N failures.
  - Extraction failure → return assistant_message without updating extracted_info; flag low-confidence.
  - Progress anomaly → coordinator re-caps and logs anomaly_event.

Routing Contract (unified_service)
- Inputs: { session_id, agent_name, prompt_blocks: {system, context, user}, model_prefs, max_tokens, temperature }
- Outputs: { text, model, provider, usage: { prompt_tokens, completion_tokens }, cost, latency_ms, ok }
- Guarantees: metrics recorded, cost estimated, retries/backoff applied, health-checked models only.

Security & Privacy Annotations
- PII: sanitize user content before joining system prompts; redact emails/phones in logs.
- Secrets: never include env vars or repo secrets in prompts; ensure allowlist-only tool usage.

Open Items
- Verify all agents import unified_service; remove direct groq_service imports.
- Add agent_name tagging to all AI calls to drive per-agent metrics.
