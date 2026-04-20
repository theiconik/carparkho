import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import pytest
from scorer import score_and_rank, _compute_weights
from models import BudgetAnswers, RecommendRequest

ROOT = Path(__file__).parent.parent.parent
SCORING_CONFIG = json.loads((ROOT / "scoring-config.json").read_text())


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


def _make_car(id: str = "car", **overrides) -> dict:
    base = {
        "id": id,
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
    base["id"] = id
    base.update(overrides)
    return base


class TestWeightComputation:
    def test_default_weights_sum_to_100(self):
        request = _make_request(usage_terrain=["highways"], regret_factors=["expensive_to_run"])
        weights = _compute_weights(SCORING_CONFIG, request)
        # Default weights: 20+15+15+10+10+10+10+5+5 = 100
        default_sum = sum(SCORING_CONFIG["dimensions"][d]["default_weight"] for d in SCORING_CONFIG["dimensions"])
        assert default_sum == 100

    def test_boost_increases_safety_weight(self):
        base_request = _make_request(regret_factors=["expensive_to_run"])
        boosted_request = _make_request(regret_factors=["not_safe"])
        base_weights = _compute_weights(SCORING_CONFIG, base_request)
        boosted_weights = _compute_weights(SCORING_CONFIG, boosted_request)
        assert boosted_weights["safety"] > base_weights["safety"]

    def test_boost_increases_city_weight(self):
        base_request = _make_request(usage_terrain=["highways"])
        boosted_request = _make_request(usage_terrain=["dense_city"])
        base_weights = _compute_weights(SCORING_CONFIG, base_request)
        boosted_weights = _compute_weights(SCORING_CONFIG, boosted_request)
        assert boosted_weights["city_maneuverability"] > base_weights["city_maneuverability"]

    def test_multiple_boosts_stack(self):
        request = _make_request(regret_factors=["not_safe", "cramped", "poor_terrain"])
        weights = _compute_weights(SCORING_CONFIG, request)
        # safety boosted by 15 (not_safe), space by 10 (cramped), ride by 10 (poor_terrain)
        assert weights["safety"] == 15 + 15
        assert weights["space_practicality"] >= 15 + 10


class TestScoreAndRank:
    def test_returns_top_n(self):
        cars = [_make_car(id=f"car_{i}") for i in range(5)]
        request = _make_request()
        results = score_and_rank(cars, request, SCORING_CONFIG, top_n=3)
        assert len(results) == 3

    def test_returns_all_if_fewer_than_top_n(self):
        cars = [_make_car(id="only")]
        request = _make_request()
        results = score_and_rank(cars, request, SCORING_CONFIG, top_n=3)
        assert len(results) == 1

    def test_scores_are_0_to_100(self):
        cars = [_make_car(id=f"c{i}") for i in range(4)]
        request = _make_request()
        results = score_and_rank(cars, request, SCORING_CONFIG)
        for _, score, _ in results:
            assert 0 <= score <= 100

    def test_results_sorted_descending(self):
        cars = [_make_car(id=f"c{i}") for i in range(4)]
        request = _make_request()
        results = score_and_rank(cars, request, SCORING_CONFIG)
        scores = [s for _, s, _ in results]
        assert scores == sorted(scores, reverse=True)

    def test_price_tiebreaker_lower_wins(self):
        # Two identical cars, different prices — lower price should rank higher on tie
        car_cheap = _make_car(id="cheap", on_road_price=800_000)
        car_expensive = _make_car(id="expensive", on_road_price=900_000)
        request = _make_request()
        results = score_and_rank([car_cheap, car_expensive], request, SCORING_CONFIG)
        assert results[0][0]["id"] == "cheap"

    def test_top_dimensions_returned(self):
        cars = [_make_car(id="single")]
        request = _make_request()
        results = score_and_rank(cars, request, SCORING_CONFIG)
        _, _, top_dims = results[0]
        assert isinstance(top_dims, list)
        assert len(top_dims) == 3

    def test_empty_input_returns_empty(self):
        request = _make_request()
        results = score_and_rank([], request, SCORING_CONFIG)
        assert results == []

    def test_price_fit_car_within_comfortable_scores_higher(self):
        # Car within comfortable budget should score higher on price_fit than stretch car
        car_comfortable = _make_car(id="cheap", on_road_price=900_000)
        car_stretch = _make_car(id="stretch", on_road_price=1_150_000)
        request = _make_request()
        results = score_and_rank([car_comfortable, car_stretch], request, SCORING_CONFIG)
        # Comfortable price car should rank first
        assert results[0][0]["id"] == "cheap"
