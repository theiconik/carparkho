import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import pytest
from filter import hard_filter
from models import BudgetAnswers, RecommendRequest

ROOT = Path(__file__).parent.parent.parent
QUESTIONS_CONFIG = json.loads((ROOT / "questions-config.json").read_text())


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


class TestBudgetFilter:
    def test_car_within_stretch_passes(self):
        car = _make_car(on_road_price=1_100_000)
        request = _make_request()
        result, blocker = hard_filter([car], request, QUESTIONS_CONFIG)
        assert len(result) == 1
        assert blocker is None

    def test_car_above_stretch_blocked(self):
        car = _make_car(on_road_price=1_300_000)
        request = _make_request()
        result, blocker = hard_filter([car], request, QUESTIONS_CONFIG)
        assert len(result) == 0

    def test_car_at_comfortable_budget_passes(self):
        car = _make_car(on_road_price=1_000_000)
        request = _make_request()
        result, _ = hard_filter([car], request, QUESTIONS_CONFIG)
        assert len(result) == 1

    def test_ex_showroom_price_type(self):
        car = _make_car(ex_showroom_price=1_100_000, on_road_price=1_300_000)
        request = _make_request(
            budget=BudgetAnswers(comfortable=1_000_000, stretch=1_200_000, price_type="ex_showroom")
        )
        result, _ = hard_filter([car], request, QUESTIONS_CONFIG)
        assert len(result) == 1


class TestSeatingFilter:
    def test_sufficient_seating_passes(self):
        car = _make_car(seating_capacity=7)
        request = _make_request(passengers="full_household")
        result, _ = hard_filter([car], request, QUESTIONS_CONFIG)
        assert len(result) == 1

    def test_insufficient_seating_blocked(self):
        car = _make_car(seating_capacity=5)
        request = _make_request(passengers="full_household")  # needs 7
        result, blocker = hard_filter([car], request, QUESTIONS_CONFIG)
        assert len(result) == 0

    def test_exact_minimum_passes(self):
        car = _make_car(seating_capacity=5)
        request = _make_request(passengers="small_family")  # needs 5
        result, _ = hard_filter([car], request, QUESTIONS_CONFIG)
        assert len(result) == 1


class TestFuelFilter:
    def test_matching_fuel_passes(self):
        car = _make_car(fuel_type="diesel")
        request = _make_request(fuel="diesel")
        result, _ = hard_filter([car], request, QUESTIONS_CONFIG)
        assert len(result) == 1

    def test_mismatched_fuel_blocked(self):
        car = _make_car(fuel_type="diesel")
        request = _make_request(fuel="petrol")
        result, blocker = hard_filter([car], request, QUESTIONS_CONFIG)
        assert len(result) == 0

    def test_no_preference_allows_all_fuels(self):
        cars = [_make_car(fuel_type=ft, id=ft) for ft in ["petrol", "diesel", "electric"]]
        request = _make_request(fuel="no_preference")
        result, _ = hard_filter(cars, request, QUESTIONS_CONFIG)
        assert len(result) == 3

    def test_hybrid_matches_mild_and_strong(self):
        cars = [
            _make_car(fuel_type="mild_hybrid", id="mild"),
            _make_car(fuel_type="strong_hybrid", id="strong"),
            _make_car(fuel_type="hybrid", id="hybrid"),
        ]
        request = _make_request(fuel="hybrid")
        result, _ = hard_filter(cars, request, QUESTIONS_CONFIG)
        assert len(result) == 3


class TestTransmissionFilter:
    def test_automatic_matches_amt_cvt_dct(self):
        cars = [
            _make_car(transmission_type="amt", id="amt"),
            _make_car(transmission_type="cvt", id="cvt"),
            _make_car(transmission_type="dct", id="dct"),
            _make_car(transmission_type="automatic", id="auto"),
        ]
        request = _make_request(transmission="automatic")
        result, _ = hard_filter(cars, request, QUESTIONS_CONFIG)
        assert len(result) == 4

    def test_manual_only_blocks_automatic(self):
        car = _make_car(transmission_type="automatic")
        request = _make_request(transmission="manual")
        result, _ = hard_filter([car], request, QUESTIONS_CONFIG)
        assert len(result) == 0

    def test_either_allows_all(self):
        cars = [
            _make_car(transmission_type="manual", id="m"),
            _make_car(transmission_type="automatic", id="a"),
        ]
        request = _make_request(transmission="either")
        result, _ = hard_filter(cars, request, QUESTIONS_CONFIG)
        assert len(result) == 2


class TestNonNegotiablesFilter:
    def test_car_with_required_feature_passes(self):
        car = _make_car(key_features=["sunroof", "adas"])
        request = _make_request(non_negotiables=["sunroof"])
        result, _ = hard_filter([car], request, QUESTIONS_CONFIG)
        assert len(result) == 1

    def test_car_missing_required_feature_blocked(self):
        car = _make_car(key_features=["power_steering"])
        request = _make_request(non_negotiables=["sunroof"])
        result, blocker = hard_filter([car], request, QUESTIONS_CONFIG)
        assert len(result) == 0

    def test_soft_boost_options_not_treated_as_hard_filter(self):
        # "good_resale" has no required_feature — should not block
        car = _make_car(key_features=[])
        request = _make_request(non_negotiables=["good_resale"])
        result, _ = hard_filter([car], request, QUESTIONS_CONFIG)
        assert len(result) == 1

    def test_no_non_negotiables_skips_filter(self):
        car = _make_car(key_features=[])
        request = _make_request(non_negotiables=[])
        result, _ = hard_filter([car], request, QUESTIONS_CONFIG)
        assert len(result) == 1


class TestBlockerDetection:
    def test_blocker_is_non_negotiables_when_features_block(self):
        # A car that passes budget/seating/fuel/transmission but fails features
        car = _make_car(key_features=[])
        request = _make_request(non_negotiables=["sunroof"])
        result, blocker = hard_filter([car], request, QUESTIONS_CONFIG)
        assert len(result) == 0
        assert blocker == "required features"

    def test_blocker_is_budget_when_only_budget_blocks(self):
        car = _make_car(on_road_price=2_000_000)
        request = _make_request()
        result, blocker = hard_filter([car], request, QUESTIONS_CONFIG)
        assert len(result) == 0
        assert blocker == "budget"

    def test_blocker_is_fuel_when_fuel_blocks(self):
        car = _make_car(fuel_type="electric")
        request = _make_request(fuel="petrol")
        result, blocker = hard_filter([car], request, QUESTIONS_CONFIG)
        assert len(result) == 0
        assert blocker == "fuel type"

    def test_no_blocker_when_cars_pass(self):
        car = _make_car()
        request = _make_request()
        result, blocker = hard_filter([car], request, QUESTIONS_CONFIG)
        assert len(result) == 1
        assert blocker is None
