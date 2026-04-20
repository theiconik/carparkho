"""
Hard-filter cars based on user answers.
Returns only cars that satisfy all active constraints.
"""

from models import RecommendRequest

# Ordered from most niche → most fundamental for blocker detection
BLOCKER_ORDER = [
    "non_negotiables",
    "fuel",
    "transmission",
    "seating",
    "budget",
]

BLOCKER_LABELS = {
    "non_negotiables": "required features",
    "fuel": "fuel type",
    "transmission": "transmission type",
    "seating": "seating capacity",
    "budget": "budget",
}


def _passes_budget(car: dict, request: RecommendRequest) -> bool:
    price = car["on_road_price"] if request.budget.price_type == "on_road" else car["ex_showroom_price"]
    return price <= request.budget.stretch


def _passes_seating(car: dict, request: RecommendRequest, questions_config: dict) -> bool:
    passengers_q = next(q for q in questions_config["questions"] if q["id"] == "passengers")
    selected_option = next((o for o in passengers_q["options"] if o["id"] == request.passengers), None)
    if selected_option is None:
        return True
    min_seating = selected_option.get("min_seating", 1)
    return car["seating_capacity"] >= min_seating


def _passes_fuel(car: dict, request: RecommendRequest, questions_config: dict) -> bool:
    fuel_q = next(q for q in questions_config["questions"] if q["id"] == "fuel")
    selected_option = next((o for o in fuel_q["options"] if o["id"] == request.fuel), None)
    if selected_option is None:
        return True
    allowed = selected_option.get("matches_fuel_types", [])
    return car["fuel_type"] in allowed


def _passes_transmission(car: dict, request: RecommendRequest, questions_config: dict) -> bool:
    tx_q = next(q for q in questions_config["questions"] if q["id"] == "transmission")
    selected_option = next((o for o in tx_q["options"] if o["id"] == request.transmission), None)
    if selected_option is None:
        return True
    allowed = selected_option.get("matches_transmission_types", [])
    return car["transmission_type"] in allowed


def _check_feature(car: dict, feature: str) -> bool:
    """Check a required_feature against the car, handling synthetic feature names."""
    if feature == "airbags_min_6":
        return car.get("airbag_count", 0) >= 6
    return feature in car.get("key_features", [])


def _passes_non_negotiables(car: dict, request: RecommendRequest, questions_config: dict) -> bool:
    if not request.non_negotiables:
        return True

    nn_q = next(q for q in questions_config["questions"] if q["id"] == "non_negotiables")
    required_features: list[str] = []
    for sel_id in request.non_negotiables:
        option = next((o for o in nn_q["options"] if o["id"] == sel_id), None)
        if option and option.get("required_feature"):
            required_features.append(option["required_feature"])

    if not required_features:
        return True

    return all(_check_feature(car, feat) for feat in required_features)


def _apply_filters(
    cars: list[dict],
    request: RecommendRequest,
    questions_config: dict,
    skip: str | None = None,
) -> list[dict]:
    """Apply all hard filters, optionally skipping one constraint by name."""
    result = []
    for car in cars:
        if skip != "budget" and not _passes_budget(car, request):
            continue
        if skip != "seating" and not _passes_seating(car, request, questions_config):
            continue
        if skip != "fuel" and not _passes_fuel(car, request, questions_config):
            continue
        if skip != "transmission" and not _passes_transmission(car, request, questions_config):
            continue
        if skip != "non_negotiables" and not _passes_non_negotiables(car, request, questions_config):
            continue
        result.append(car)
    return result


def hard_filter(
    cars: list[dict],
    request: RecommendRequest,
    questions_config: dict,
) -> tuple[list[dict], str | None]:
    """
    Returns (filtered_cars, blocker_label).
    blocker_label is None unless zero cars pass all filters,
    in which case it names the first constraint whose removal unlocks results.
    """
    filtered = _apply_filters(cars, request, questions_config)
    if filtered:
        return filtered, None

    # Zero results — detect blocker by dropping one constraint at a time
    for constraint in BLOCKER_ORDER:
        if _apply_filters(cars, request, questions_config, skip=constraint):
            return [], BLOCKER_LABELS[constraint]

    return [], "no_cars_found"
