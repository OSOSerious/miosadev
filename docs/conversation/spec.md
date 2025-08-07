# Conversation Integrity Spec

Principles
- Local gate handles typos/unclear inputs (no LLM).
- Information-driven progression using `system_context.information_schema`.
- Anti-repetition of question types; natural, single next question.
- No hallucinated context; reflect only session-known facts.

Enforcement
- Use `system_context` for context, extraction, progress.
- Include "what we know vs missing" to steer LLM.
- Coordinator enforces universal progress caps.

Tests
- Typo → local response; 0 LLM calls.
- After process question, next question is different type when other gaps exist.
- Quantified detail increases progress smoothly (≤ cap per turn).
