"""Orchestrates filter → score → LLM explanations for the recommend API."""

from __future__ import annotations

from filter import hard_filter
from llm import generate_explanations
from models import CarResult, KeySpecs, RecommendRequest, RecommendResponse
from scorer import score_and_rank
from settings import Settings


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


class RecommendationService:
    def __init__(
        self,
        *,
        cars: list[dict],
        questions_config: dict,
        scoring_config: dict,
        settings: Settings,
    ) -> None:
        self._cars = cars
        self._questions_config = questions_config
        self._scoring_config = scoring_config
        self._settings = settings

    @property
    def car_count(self) -> int:
        return len(self._cars)

    async def recommend(self, request: RecommendRequest) -> RecommendResponse:
        filtered_cars, blocker = hard_filter(self._cars, request, self._questions_config)

        if not filtered_cars:
            return RecommendResponse(
                results=[],
                total_matched=0,
                blocker=blocker,
            )

        ranked = score_and_rank(filtered_cars, request, self._scoring_config, top_n=3)
        request_data = request.model_dump()
        explanations = await generate_explanations(ranked, request_data, self._settings)

        results = [
            _build_car_result(car, score, explanation)
            for (car, score, _), explanation in zip(ranked, explanations)
        ]

        total_matched = len(filtered_cars)
        banner = None
        if total_matched < 3:
            banner = (
                f"Only {total_matched} car{'s' if total_matched > 1 else ''} matched your "
                "must-haves. Adjust your preferences to see more."
            )

        return RecommendResponse(
            results=results,
            total_matched=total_matched,
            banner=banner,
        )
