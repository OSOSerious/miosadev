# Progress Integrity & Phase Gating

Source of Truth
- Coordinator stores `progress`, `last_progress`, `phase`.
- Agents propose progress; coordinator enforces cap.

Rules
- Quality-based scoring via `system_context.calculate_quality_progress`.
- Cap delta to +10–12% per turn.
- Phase thresholds: discovery < design < recommendation/generation.

Actions
- Ensure all agents use system_context for scoring.
- Apply server-side cap in coordinator for all updates.
