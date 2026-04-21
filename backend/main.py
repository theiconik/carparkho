import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from catalog import JsonCarCatalogRepository
from models import RecommendRequest, RecommendResponse
from recommendation import RecommendationService
from settings import Settings

_settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(
        level=getattr(logging, _settings.log_level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    repo = JsonCarCatalogRepository(_settings.cars_dataset_path)
    cars = repo.load_cars()
    questions_config = json.loads(_settings.questions_config_path.read_text(encoding="utf-8"))
    scoring_config = json.loads(_settings.scoring_config_path.read_text(encoding="utf-8"))

    app.state.settings = _settings
    app.state.recommendation_service = RecommendationService(
        cars=cars,
        questions_config=questions_config,
        scoring_config=scoring_config,
        settings=_settings,
    )
    yield


app = FastAPI(title="Car Parkho API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(_settings.cors_origins),
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.post("/api/recommend", response_model=RecommendResponse)
async def recommend(request: RecommendRequest, req: Request) -> RecommendResponse:
    svc: RecommendationService = req.app.state.recommendation_service
    return await svc.recommend(request)


@app.get("/health")
def health(req: Request) -> dict:
    svc: RecommendationService = req.app.state.recommendation_service
    return {"status": "ok", "cars_loaded": svc.car_count}
