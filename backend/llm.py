"""
Single OpenRouter API call to generate plain-language explanations for top 3 cars.
Falls back to a template string if the call fails or times out.
"""

from __future__ import annotations

import json
import logging

import httpx

from settings import Settings

logger = logging.getLogger(__name__)

DIMENSION_LABELS = {
    "price_fit": "price fit",
    "safety": "safety",
    "space_practicality": "space and practicality",
    "ride_quality": "ride quality",
    "running_cost": "running cost",
    "city_maneuverability": "city maneuverability",
    "highway_capability": "highway capability",
    "reliability": "reliability",
    "resale_value": "resale value",
}


def _template_explanation(car: dict, top_dimensions: list[str]) -> str:
    dim_labels = [DIMENSION_LABELS.get(d, d) for d in top_dimensions[:3]]
    return f"This car matched your preferences for {', '.join(dim_labels)}."


def _build_prompt(
    ranked_cars: list[tuple[dict, float, list[str]]],
    request_data: dict,
) -> str:
    cars_context = []
    for car, score, top_dims in ranked_cars:
        dim_labels = [DIMENSION_LABELS.get(d, d) for d in top_dims[:3]]
        cars_context.append({
            "name": f"{car['make']} {car['model']} {car['variant']}",
            "on_road_price_inr": car["on_road_price"],
            "fuel_type": car["fuel_type"],
            "transmission": car["transmission_type"],
            "seating": car["seating_capacity"],
            "mileage_kmpl": car["mileage_kmpl"],
            "safety_rating_stars": car["safety_rating"],
            "ground_clearance_mm": car["ground_clearance_mm"],
            "power_bhp": car["power_bhp"],
            "top_scoring_dimensions": dim_labels,
        })

    prompt = f"""You are a helpful car advisor. A user has answered 7 questions to find their ideal car.

User answers:
- Budget: comfortable ₹{request_data['budget']['comfortable']:,}, stretch ₹{request_data['budget']['stretch']:,}
- Passengers: {request_data['passengers']}
- Usage terrain: {', '.join(request_data['usage_terrain'])}
- Regret factors: {', '.join(request_data['regret_factors'])}
- Fuel preference: {request_data['fuel']}
- Transmission: {request_data['transmission']}
- Non-negotiables: {', '.join(request_data['non_negotiables']) if request_data['non_negotiables'] else 'none'}

Top 3 recommended cars:
{json.dumps(cars_context, indent=2)}

For each car, write a 2–3 sentence explanation in plain, friendly language explaining why it suits this user.
Focus on the top_scoring_dimensions and the user's stated priorities. Do not mention scores or rankings.

Respond with a JSON array of exactly 3 strings, one explanation per car, in the same order as the cars above.
Example format: ["Explanation for car 1.", "Explanation for car 2.", "Explanation for car 3."]"""

    return prompt


async def generate_explanations(
    ranked_cars: list[tuple[dict, float, list[str]]],
    request_data: dict,
    settings: Settings,
) -> list[str]:
    """
    Returns a list of explanation strings, one per car.
    Falls back to template strings on any error or timeout.
    """
    api_key = settings.openrouter_api_key

    if not api_key:
        logger.info("OpenRouter API key not set; using template explanations")
        return [_template_explanation(car, dims) for car, _, dims in ranked_cars]

    prompt = _build_prompt(ranked_cars, request_data)
    timeout = httpx.Timeout(settings.openrouter_timeout_seconds)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                settings.openrouter_base_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.openrouter_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                },
            )
            if response.status_code != 200:
                logger.warning(
                    "OpenRouter error status=%s body=%s",
                    response.status_code,
                    response.text[:2000],
                )
            else:
                try:
                    payload = response.json()
                except json.JSONDecodeError:
                    logger.warning("OpenRouter returned non-JSON body (status 200)")
                else:
                    logger.debug("OpenRouter response: %s", json.dumps(payload, ensure_ascii=False))
                    content = payload["choices"][0]["message"]["content"].strip()

                    if content.startswith("```"):
                        content = content.split("```", 2)[1]
                        if content.startswith("json"):
                            content = content[4:]
                        content = content.strip()
                        if content.endswith("```"):
                            content = content[:-3].strip()

                    explanations = json.loads(content)
                    if isinstance(explanations, list) and len(explanations) == len(ranked_cars):
                        return explanations
                    logger.warning(
                        "OpenRouter returned unexpected explanation shape: type=%s len=%s expected_len=%s",
                        type(explanations).__name__,
                        len(explanations) if isinstance(explanations, list) else None,
                        len(ranked_cars),
                    )

    except json.JSONDecodeError as e:
        logger.error("Failed to parse LLM JSON output: %s", e)
    except Exception as e:
        logger.error("LLM call failed: %s", e)

    return [_template_explanation(car, dims) for car, _, dims in ranked_cars]
