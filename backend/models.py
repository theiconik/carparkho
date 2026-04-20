from pydantic import BaseModel, Field


class BudgetAnswers(BaseModel):
    comfortable: int = Field(..., gt=0, description="Comfortable budget in INR")
    stretch: int = Field(..., gt=0, description="Stretch budget in INR")
    price_type: str = Field("on_road", pattern="^(on_road|ex_showroom)$")


class RecommendRequest(BaseModel):
    budget: BudgetAnswers
    passengers: str
    usage_terrain: list[str] = Field(..., min_length=1, max_length=2)
    regret_factors: list[str] = Field(..., min_length=1, max_length=3)
    fuel: str
    transmission: str
    non_negotiables: list[str] = Field(default_factory=list)


class KeySpecs(BaseModel):
    seating_capacity: int
    fuel_type: str
    transmission_type: str
    safety_rating: float
    mileage_kmpl: float
    body_type: str


class CarResult(BaseModel):
    id: str
    make: str
    model: str
    variant: str
    on_road_price: int
    ex_showroom_price: int
    image_url: str
    detail_page_url: str
    key_specs: KeySpecs
    explanation: str
    score: float


class RecommendResponse(BaseModel):
    results: list[CarResult]
    total_matched: int
    banner: str | None = None
    blocker: str | None = None
