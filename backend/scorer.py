"""
Weighted multi-dimension scoring for filtered cars.
Each car gets a score 0–100. Top N are returned, tie-broken by lower on_road_price.
"""

from models import RecommendRequest


def _compute_weights(scoring_config: dict, request: RecommendRequest) -> dict[str, float]:
    """Start from default weights and add boosts based on user answers."""
    dimensions = scoring_config["dimensions"]
    weights: dict[str, float] = {dim: cfg["default_weight"] for dim, cfg in dimensions.items()}

    for rule in scoring_config["boost_rules"]:
        cond = rule["condition"]
        question_id = cond["question"]
        answer = _get_answer(request, question_id)

        matched = False
        if "includes" in cond:
            matched = isinstance(answer, list) and cond["includes"] in answer
        elif "equals" in cond:
            matched = answer == cond["equals"]

        if matched:
            dim = rule["dimension"]
            weights[dim] = weights.get(dim, 0) + rule["boost"]

    return weights


def _get_answer(request: RecommendRequest, question_id: str):
    mapping = {
        "budget": request.budget,
        "passengers": request.passengers,
        "usage_terrain": request.usage_terrain,
        "regret_factors": request.regret_factors,
        "fuel": request.fuel,
        "transmission": request.transmission,
        "non_negotiables": request.non_negotiables,
    }
    return mapping.get(question_id)


def _normalize(values: list[float], inverse: bool = False) -> list[float]:
    """Min-max normalize a list of values to [0, 1]. Inverse = smaller is better."""
    if not values:
        return values
    min_v, max_v = min(values), max(values)
    if max_v == min_v:
        return [1.0] * len(values)
    normalized = [(v - min_v) / (max_v - min_v) for v in values]
    if inverse:
        normalized = [1.0 - n for n in normalized]
    return normalized


def _price_fit_scores(cars: list[dict], request: RecommendRequest) -> list[float]:
    """Score = 1 if price <= comfortable_budget, linearly decays to 0 at stretch_budget."""
    comfortable = request.budget.comfortable
    stretch = request.budget.stretch
    scores = []
    for car in cars:
        price = car["on_road_price"] if request.budget.price_type == "on_road" else car["ex_showroom_price"]
        if price <= comfortable:
            scores.append(1.0)
        elif price >= stretch:
            scores.append(0.0)
        else:
            scores.append(1.0 - (price - comfortable) / (stretch - comfortable))
    return scores


def _safety_scores(cars: list[dict]) -> list[float]:
    ratings = [c["safety_rating"] for c in cars]
    airbags = [c["airbag_count"] for c in cars]
    norm_ratings = _normalize(ratings)
    norm_airbags = _normalize(airbags)
    return [(r + a) / 2 for r, a in zip(norm_ratings, norm_airbags)]


def _space_scores(cars: list[dict]) -> list[float]:
    boot = _normalize([c["boot_space_liters"] for c in cars])
    seating = _normalize([c["seating_capacity"] for c in cars])
    return [(b + s) / 2 for b, s in zip(boot, seating)]


def _ride_quality_scores(cars: list[dict]) -> list[float]:
    return _normalize([c["ground_clearance_mm"] for c in cars])


def _running_cost_scores(cars: list[dict]) -> list[float]:
    mileage = _normalize([c["mileage_kmpl"] for c in cars])
    # Lower service_cost_index = cheaper to run = better; inverse normalize
    service = _normalize([c["service_cost_index"] for c in cars], inverse=True)
    return [(m + s) / 2 for m, s in zip(mileage, service)]


def _city_maneuverability_scores(cars: list[dict]) -> list[float]:
    # Smaller turning radius + shorter length = better city car → inverse normalize
    turning = _normalize([c["turning_radius_m"] for c in cars], inverse=True)
    length = _normalize([c["length_mm"] for c in cars], inverse=True)
    return [(t + l) / 2 for t, l in zip(turning, length)]


def _highway_capability_scores(cars: list[dict]) -> list[float]:
    power = _normalize([c["power_bhp"] for c in cars])
    torque = _normalize([c["torque_nm"] for c in cars])
    return [(p + t) / 2 for p, t in zip(power, torque)]


def _reliability_scores(cars: list[dict]) -> list[float]:
    return [c["brand_reliability_index"] for c in cars]


def _resale_scores(cars: list[dict]) -> list[float]:
    return _normalize([c["resale_value_5yr_percent"] for c in cars])


DIMENSION_SCORERS = {
    "price_fit": _price_fit_scores,
    "safety": _safety_scores,
    "space_practicality": _space_scores,
    "ride_quality": _ride_quality_scores,
    "running_cost": _running_cost_scores,
    "city_maneuverability": _city_maneuverability_scores,
    "highway_capability": _highway_capability_scores,
    "reliability": _reliability_scores,
    "resale_value": _resale_scores,
}


def score_and_rank(
    cars: list[dict],
    request: RecommendRequest,
    scoring_config: dict,
    top_n: int = 3,
) -> list[tuple[dict, float, list[str]]]:
    """
    Returns list of (car, score, top_dimensions) sorted descending by score.
    top_dimensions = names of the 3 highest-weight dimensions for that car.
    Tie-breaker: lower on_road_price wins.
    """
    if not cars:
        return []

    weights = _compute_weights(scoring_config, request)
    total_weight = sum(weights.values()) or 1.0

    # Compute per-dimension scores for all cars
    dim_scores: dict[str, list[float]] = {}
    for dim, scorer in DIMENSION_SCORERS.items():
        if dim == "price_fit":
            dim_scores[dim] = scorer(cars, request)
        else:
            dim_scores[dim] = scorer(cars)

    # Compute weighted total score for each car
    car_scores: list[float] = []
    for i in range(len(cars)):
        total = sum(
            weights.get(dim, 0) * dim_scores[dim][i]
            for dim in DIMENSION_SCORERS
        )
        car_scores.append((total / total_weight) * 100)

    # Determine top 3 dimensions by weight for explanation context
    sorted_dims_by_weight = sorted(weights.items(), key=lambda x: x[1], reverse=True)
    top_dim_names = [d for d, _ in sorted_dims_by_weight[:3]]

    # Build result tuples and sort
    results = list(zip(cars, car_scores, [top_dim_names] * len(cars)))
    results.sort(key=lambda x: (-x[1], x[0]["on_road_price"]))

    return results[:top_n]
