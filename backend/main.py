import json
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from filter import hard_filter
from llm import generate_explanations
from models import CarResult, KeySpecs, RecommendRequest, RecommendResponse
from scorer import score_and_rank

ROOT = Path(__file__).parent.parent

_cars: list[dict] = []
_questions_config: dict = {}
_scoring_config: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _cars, _questions_config, _scoring_config
    _cars = json.loads((ROOT / "cars-dataset.json").read_text())["cars"]
    _questions_config = json.loads((ROOT / "questions-config.json").read_text())
    _scoring_config = json.loads((ROOT / "scoring-config.json").read_text())
    yield


app = FastAPI(title="Car Parkho API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
    ],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)


def _build_car_result(car: dict, score: float, explanation: str) -> CarResult:
    return CarResult(
        id=car["id"],
        make=car["make"],
        model=car["model"],
        variant=car["variant"],
        on_road_price=car["on_road_price"],
        ex_showroom_price=car["ex_showroom_price"],
        image_url=car["image_url"],
        detail_page_url=car["detail_page_url"],
        key_specs=KeySpecs(
            seating_capacity=car["seating_capacity"],
            fuel_type=car["fuel_type"],
            transmission_type=car["transmission_type"],
            safety_rating=car["safety_rating"],
            mileage_kmpl=car["mileage_kmpl"],
            body_type=car["body_type"],
        ),
        explanation=explanation,
        score=round(score, 2),
    )


@app.post("/api/recommend", response_model=RecommendResponse)
async def recommend(request: RecommendRequest) -> RecommendResponse:
    filtered_cars, blocker = hard_filter(_cars, request, _questions_config)

    if not filtered_cars:
        return RecommendResponse(
            results=[],
            total_matched=0,
            blocker=blocker,
        )

    ranked = score_and_rank(filtered_cars, request, _scoring_config, top_n=3)

    request_data = request.model_dump()
    explanations = await generate_explanations(ranked, request_data)

    results = [
        _build_car_result(car, score, explanation)
        for (car, score, _), explanation in zip(ranked, explanations)
    ]

    total_matched = len(filtered_cars)
    banner = None
    if total_matched < 3:
        banner = f"Only {total_matched} car{'s' if total_matched > 1 else ''} matched your must-haves. Adjust your preferences to see more."

    return RecommendResponse(
        results=results,
        total_matched=total_matched,
        banner=banner,
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "cars_loaded": len(_cars)}
