# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Car Parkho — a guided car recommender MVP. User answers 7 questions → deterministic hard filter + weighted scoring → top 3 car recommendations with LLM-generated explanations.

## Stack

- **Frontend:** Next.js (App Router), mobile-first, Tailwind CSS
- **Backend:** FastAPI (Python), in-memory mock data (no DB)
- **LLM:** OpenRouter API (`OPENROUTER_API_KEY` env var), model string is configurable — default `anthropic/claude-haiku-4-5`
- **Config files (`/backend`):** `questions-config.json`, `scoring-config.json`, `cars-dataset.json` — backend loads these at startup

## Dev Commands

### Frontend (`/frontend`)
```bash
npm run dev       # start Next.js on :3000
npm run build
npm run lint
```

### Backend (`/backend`)
```bash
uvicorn main:app --reload --port 8000
pip install -r requirements.txt
pytest                        # run all tests
pytest tests/test_scorer.py   # single test file
```

## Architecture

### Backend flow
`POST /api/recommend` receives 7 answers → `filter.py` hard-filters cars → `scorer.py` scores remaining (0–100) → top 3 passed to `llm.py` for a single OpenRouter call → returns ranked list with explanations.

- Hard filter rules and scoring weights/boosts live in `scoring-config.json`, loaded at startup — no redeploy needed to tune weights
- `questions-config.json` drives option→filter field mapping (e.g. `matches_fuel_types`, `min_seating`, `required_feature`)
- LLM fallback: if OpenRouter call fails or exceeds 3s, return template string `"This car matched your preferences for [top 3 dimensions]."`
- Blocker detection for zero-results: re-run filter removing one constraint at a time to identify which constraint blocked all results

### Frontend flow
Single quiz state machine across 7 screens → `POST /api/recommend` → results page. Back-navigation preserves answers (do not reset state).

- One component per question type: `budget_slider`, `single_select`, `multi_select`, `multi_select_chips`
- Progress indicator shows `{current}/7`
- Results page shows 3 cards: image, name, on-road price, 2–3 line explanation, key specs, link to detail page
- Edge cases: fewer than 3 results shows banner; zero results shows empty state with blocker reason

## Design System

| Token | Value |
|-------|-------|
| Primary Coral | `#F05C35` |
| Charcoal Dark | `#2A2C32` |
| Surface White | `#FFFFFF` |
| Text Secondary | `#7A7D82` |
| Border Light | `#D1D4D7` |
| Border Radius | `8px` |
| Font | Inter (or Proxima Nova) |

Active states use Coral. Primary CTA button: Coral bg, white bold text. Radio active: Coral ring + dot + label.

## Key Constraints

- LLM call is **server-side only** — never expose `OPENROUTER_API_KEY` to client
- One OpenRouter call per session generates all 3 explanations in a single structured prompt (not 3 separate calls)
- `mileage_kmpl` for EVs represents km/kWh equivalent — treat as comparable for `running_cost` scoring
- `scoring-config.json` boost rules are additive — multiple boosts stack on same dimension
- Tie-breaker: lower `on_road_price` wins
