# Test Plan (Agents + AI)

Unit
- Input gate regex coverage.
- Progress smoothing boundaries.
- Extraction quality (quantified vs vague).

Integration
- Coordinator start/continue: 0 LLM on typo; last_progress & progress_details present.
- Multi-agent through unified_service; metrics captured.

Load
- High-frequency short inputs → near-zero tokens due to local gate; no rate limits.
