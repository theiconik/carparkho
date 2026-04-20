"""
Single OpenRouter API call to generate plain-language explanations for top 3 cars.
Falls back to a template string if the call fails or exceeds 3 seconds.
"""

import json
import os
import httpx

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")
TIMEOUT_SECONDS = 30.0

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
) -> list[str]:
    """
    Returns a list of explanation strings, one per car.
    Falls back to template strings on any error or timeout.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        print("No API key found, falling back to template explanations")
        return [_template_explanation(car, dims) for car, _, dims in ranked_cars]

    prompt = _build_prompt(ranked_cars, request_data)

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                },
            )
            if response.status_code != 200:
                print(f"LLM error {response.status_code}: {response.text}")
                raise httpx.HTTPStatusError("bad status", request=response.request, response=response)
            content = response.json()["choices"][0]["message"]["content"].strip()
            print(f"LLM Response: {response.json()}")

            # Strip markdown code fence if present (e.g. ```json ... ```)
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

    except Exception as e:
        print(f"LLM call failed: {e}")

    return [_template_explanation(car, dims) for car, _, dims in ranked_cars]
