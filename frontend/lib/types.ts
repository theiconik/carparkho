export interface BudgetAnswers {
  comfortable: number;
  stretch: number;
  price_type: "on_road" | "ex_showroom";
}

export interface QuizAnswers {
  budget: BudgetAnswers;
  passengers: string;
  usage_terrain: string[];
  regret_factors: string[];
  fuel: string;
  transmission: string;
  non_negotiables: string[];
}

export interface KeySpecs {
  seating_capacity: number;
  fuel_type: string;
  transmission_type: string;
  safety_rating: number;
  mileage_kmpl: number;
  body_type: string;
}

export interface CarResult {
  id: string;
  make: string;
  model: string;
  variant: string;
  on_road_price: number;
  ex_showroom_price: number;
  image_url: string;
  detail_page_url: string;
  key_specs: KeySpecs;
  explanation: string;
  score: number;
}

export interface RecommendResponse {
  results: CarResult[];
  total_matched: number;
  banner: string | null;
  blocker: string | null;
}
