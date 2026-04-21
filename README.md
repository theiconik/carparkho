<div align="center">

<img src="carparkho.png" alt="Car Parkho Logo" width="180" />

# Car Parkho

**A guided car recommender — answer 7 questions, get your top 3 matches.**

![Build Passing](https://img.shields.io/badge/build-passing-brightgreen?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=flat-square&logo=nextdotjs&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-38BDF8?style=flat-square&logo=tailwindcss&logoColor=white)

</div>

---

## What is Car Parkho?

Car Parkho is a quiz-style car recommendation MVP. The user answers **7 guided questions** (budget, fuel type, seating, use case, etc.) and the engine:

1. **Hard-filters** cars that don't meet must-have constraints
2. **Scores** remaining cars on a weighted 0–100 scale
3. **Returns the top 3** with LLM-generated natural language explanations (powered by OpenRouter)

Zero sign-up. No database. Just answer → recommend.

---

## Tech Stack

| Layer    | Technology                                                                       |
| -------- | -------------------------------------------------------------------------------- |
| Frontend | Next.js 16 (App Router), React 19, TypeScript                                    |
| Styling  | Tailwind CSS v4                                                                  |
| Backend  | FastAPI (Python), Uvicorn                                                        |
| LLM      | OpenRouter API (default model: `anthropic/claude-haiku-4-5`)                     |
| Testing  | pytest, pytest-asyncio                                                           |
| Config   | JSON files (`cars-dataset.json`, `scoring-config.json`, `questions-config.json`) |

---

## Getting Started

### Prerequisites

- **Node.js** 18+ and **npm**
- **Python** 3.11+
- An **OpenRouter API key** → [openrouter.ai/keys](https://openrouter.ai/keys)

---

### Backend

```bash
# 1. Enter the backend directory
cd backend

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables (see Environment Variables section below)
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY

# 5. Start the server
uvicorn main:app --reload --port 8000
```

The API is now available at `http://localhost:8000`.

Run tests with:

```bash
pytest                          # all tests
pytest tests/test_scorer.py     # single file
```

---

### Frontend

```bash
# 1. Enter the frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Set up environment variables
cp .env.local.example .env.local
# Edit .env.local if your backend runs on a port other than 8000

# 4. Start the dev server
npm run dev
```

The app is now available at `http://localhost:3000`.

---

## Environment Variables

### Backend — `backend/.env`

Copy `backend/.env.example` to `backend/.env` and fill in values.

| Variable                     | Required | Default                                         | Description                                                                       |
| ---------------------------- | -------- | ----------------------------------------------- | --------------------------------------------------------------------------------- |
| `OPENROUTER_API_KEY`         | **Yes**  | —                                               | Your OpenRouter API key. Without it, explanations fall back to a template string. |
| `OPENROUTER_MODEL`           | No       | `anthropic/claude-haiku-4-5`                    | Any model slug from openrouter.ai                                                 |
| `OPENROUTER_BASE_URL`        | No       | `https://openrouter.ai/api/v1/chat/completions` | OpenRouter endpoint                                                               |
| `OPENROUTER_TIMEOUT_SECONDS` | No       | `30`                                            | Max seconds to wait for the LLM response                                          |
| `CORS_ORIGINS`               | No       | `http://localhost:3000,http://127.0.0.1:3000`   | Comma-separated allowed origins                                                   |
| `LOG_LEVEL`                  | No       | `INFO`                                          | Set to `DEBUG` to log full OpenRouter JSON responses                              |
| `CARS_DATASET_PATH`          | No       | `./cars-dataset.json`                           | Override path to the cars dataset                                                 |
| `QUESTIONS_CONFIG_PATH`      | No       | `./questions-config.json`                       | Override path to questions config                                                 |
| `SCORING_CONFIG_PATH`        | No       | `./scoring-config.json`                         | Override path to scoring config                                                   |

### Frontend — `frontend/.env.local`

Copy `frontend/.env.local.example` to `frontend/.env.local`.

| Variable              | Required | Default                 | Description                     |
| --------------------- | -------- | ----------------------- | ------------------------------- |
| `NEXT_PUBLIC_API_URL` | No       | `http://localhost:8000` | Base URL of the FastAPI backend |

---

## Project Structure

```
carparkho/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── filter.py               # Hard-filter logic
│   ├── scorer.py               # Weighted scoring (0–100)
│   ├── llm.py                  # OpenRouter LLM call
│   ├── recommendation.py       # Orchestrates filter → score → LLM
│   ├── cars-dataset.json       # Car data (no DB)
│   ├── questions-config.json   # Question → filter field mapping
│   ├── scoring-config.json     # Weights, boosts, hard-filter rules
│   ├── requirements.txt
│   └── tests/
├── frontend/
│   ├── app/                    # Next.js App Router pages
│   ├── components/             # Question type components
│   ├── hooks/
│   └── lib/
├── docs/
│   ├── PRD.md
│   ├── UI-Design-System.md
│   └── Future Scope.md
└── README.md
```

---

## Key Notes

- The **LLM call is server-side only** — `OPENROUTER_API_KEY` is never exposed to the browser.
- All 3 car explanations are generated in **a single OpenRouter call** per session.
- If the LLM call fails or times out (>30s), the app gracefully falls back to a template explanation.
- Scoring weights and hard-filter rules live in `scoring-config.json` — tune them without redeploying.
