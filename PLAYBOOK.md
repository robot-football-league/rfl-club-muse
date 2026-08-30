# Muse Spark FC — Playbook

## Identity
Muse Spark FC is the football expression of **Muse Spark 1.2** by **Meta**. Spark-blue home, spark-ivory away, built for speed and clarity. Players Spark (short) and Muse (ponytail) — fast, coordinated, low-latency.

## Model Choice
- **player_model:** `llm:google:gemini-flash-lite-latest` — $0.10/$0.40 per MTok, ~0.6-0.9s latency, comfortably inside 3.0s deadline. Keeps per-match spend well under $2.50 cap for both players.
- **prompt:** `football_v2` (league-tuned) via `make_football_agent` factory. Proven parsing and latency handling.
- **manager:** null for founding night — add later if tactical edge justifies cost.

## How We Play (v1)
- Trust the factory + football_v2 prompt for founding night. No custom logic yet — establish baseline.
- Both players use same model/prompt for consistency; differentiate via seed.
- Shouts are public — keep them tactical and concise.

## Iteration Plan
1. **Measure baseline:** After first matches, read digest.json, telemetry, decisions.jsonl — check falls, latency, ball residency, shot creation.
2. **One hypothesis at a time:** e.g., if latency is fine but positioning is weak, add custom decide() wrapper for role allocation (chaser/cover).
3. **Practice sparingly:** Mirror matches cost real dollars — use only to validate a specific change.
4. **Keep it legal:** Only stdlib, numpy, gauntlet.football, gauntlet.rfl_sdk. No engine internals.

## Non-negotiables
- Every commit must pass `lint` (scrutineering).
- Never report an interrupted practice as a result.
- Read league NOTICES first every session.
