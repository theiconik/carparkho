import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import pytest

from models import BudgetAnswers, RecommendRequest
from recommendation import RecommendationService
from settings import Settings

ROOT = Path(__file__).parent.parent
QUESTIONS_CONFIG = json.loads((ROOT / "questions-config.json").read_text(encoding="utf-8"))
SCORING_CONFIG = json.loads((ROOT / "scoring-config.json").read_text(encoding="utf-8"))


def _make_request(**overrides) -> RecommendRequest:
    defaults = dict(
        budget=BudgetAnswers(comfortable=1_000_000, stretch=1_200_000, price_type="on_road"),
        passengers="small_family",
        usage_terrain=["dense_city"],
        regret_factors=["expensive_to_run"],
        fuel="petrol",
        transmission="either",
        non_negotiables=[],
    )
    defaults.update(overrides)
    return RecommendRequest(**defaults)


def _make_car(**overrides) -> dict:
    base = {
        "id": "test_car",
        "make": "Test",
        "model": "Car",
        "variant": "Base",
        "body_type": "hatchback",
        "seating_capacity": 5,
        "fuel_type": "petrol",
        "transmission_type": "manual",
        "ex_showroom_price": 800_000,
        "on_road_price": 900_000,
        "mileage_kmpl": 20.0,
        "power_bhp": 80,
        "torque_nm": 100,
        "ground_clearance_mm": 170,
        "boot_space_liters": 250,
        "length_mm": 3900,
        "turning_radius_m": 5.0,
        "safety_rating": 4.0,
        "airbag_count": 6,
        "service_cost_index": 0.7,
        "brand_reliability_index": 0.8,
        "resale_value_5yr_percent": 60,
        "key_features": [],
        "image_url": "https://example.com/car.jpg",
        "detail_page_url": "https://example.com/car",
    }
    base.update(overrides)
    return base


@pytest.fixture
def no_llm_settings() -> Settings:
    return Settings(openrouter_api_key=None)


@pytest.mark.asyncio
async def test_car_count(no_llm_settings: Settings):
    cars = [_make_car()]
    svc = RecommendationService(
        cars=cars,
        questions_config=QUESTIONS_CONFIG,
        scoring_config=SCORING_CONFIG,
        settings=no_llm_settings,
    )
    assert svc.car_count == 1


@pytest.mark.asyncio
async def test_one_match_includes_banner_and_result(no_llm_settings: Settings):
    car = _make_car(id="only", on_road_price=900_000)
    svc = RecommendationService(
        cars=[car],
        questions_config=QUESTIONS_CONFIG,
        scoring_config=SCORING_CONFIG,
        settings=no_llm_settings,
    )
    response = await svc.recommend(_make_request())
    assert response.total_matched == 1
    assert response.banner is not None
    assert "Only 1 car" in response.banner
    assert len(response.results) == 1
    assert response.results[0].id == "only"
    assert "matched your preferences" in response.results[0].explanation


@pytest.mark.asyncio
async def test_zero_matches_returns_blocker(no_llm_settings: Settings):
    car = _make_car(on_road_price=2_000_000)
    svc = RecommendationService(
        cars=[car],
        questions_config=QUESTIONS_CONFIG,
        scoring_config=SCORING_CONFIG,
        settings=no_llm_settings,
    )
    response = await svc.recommend(_make_request())
    assert response.total_matched == 0
    assert response.results == []
    assert response.blocker is not None
