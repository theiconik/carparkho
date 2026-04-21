import type { QuizAnswers } from "@/lib/types";

export const TOTAL_STEPS = 7;

export const INITIAL_ANSWERS: QuizAnswers = {
  budget: { comfortable: 1_000_000, stretch: 1_500_000, price_type: "on_road" },
  passengers: "",
  usage_terrain: [],
  regret_factors: [],
  fuel: "",
  transmission: "",
  non_negotiables: [],
};

export const PASSENGERS_OPTIONS = [
  { id: "solo", label: "Just me (maybe one passenger)" },
  { id: "couple", label: "Me and my partner" },
  { id: "small_family", label: "Small family — 3 to 4 people, occasional guests" },
  { id: "full_household", label: "Full household — 5+ regularly, including kids or elderly" },
  { id: "varies", label: "Varies a lot — need flexibility" },
] as const;

export const TERRAIN_OPTIONS = [
  { id: "dense_city", label: "Dense city traffic — parking is a pain" },
  { id: "highways", label: "Highways and long drives" },
  { id: "bad_roads", label: "Bad roads, potholes, or unpaved stretches" },
  { id: "hills_rain", label: "Hills or heavy rain regularly" },
  { id: "short_errands", label: "Mostly short errands close to home" },
] as const;

export const REGRET_OPTIONS = [
  { id: "cramped", label: "Felt cramped or impractical" },
  { id: "expensive_to_run", label: "Expensive to run or service" },
  { id: "not_safe", label: "Didn't feel safe enough" },
  { id: "boring", label: "Boring or didn't turn heads" },
  { id: "poor_terrain", label: "Couldn't handle rough roads or long trips" },
  { id: "depreciated", label: "Depreciated too fast when I tried to sell" },
  { id: "too_much_car", label: "Too much car for what I actually needed" },
] as const;

export const FUEL_OPTIONS = [
  { id: "petrol", label: "Petrol" },
  { id: "diesel", label: "Diesel" },
  { id: "hybrid", label: "Hybrid" },
  { id: "electric", label: "Electric" },
  { id: "no_preference", label: "No strong preference — recommend what fits" },
] as const;

export const TRANSMISSION_OPTIONS = [
  { id: "manual", label: "Manual" },
  { id: "automatic", label: "Automatic" },
  { id: "either", label: "Either — whichever is better for the car" },
] as const;

export const NON_NEGOTIABLES_OPTIONS = [
  { id: "sunroof", label: "Sunroof" },
  { id: "six_airbags", label: "6 airbags or more" },
  { id: "camera_360", label: "360° camera" },
  { id: "ventilated_seats", label: "Ventilated seats" },
  { id: "adas", label: "ADAS features" },
  { id: "third_row", label: "Third row seating" },
  { id: "good_resale", label: "Good resale value" },
  { id: "reliable_brand", label: "Known reliable brand" },
  { id: "surprise_me", label: "None of these — surprise me" },
] as const;

export const STEP_META = [
  { title: "What's your budget?", subtitle: "We'll show cars that fit comfortably, and a few that stretch." },
  { title: "Who's usually in the car?", subtitle: "Think about your typical day, not edge cases." },
  { title: "Where does this car mostly live?", subtitle: "Pick up to 2." },
  { title: "What would make you regret this purchase in 2 years?", subtitle: "Pick up to 3. This helps us understand what matters most." },
  { title: "Fuel preference?", subtitle: null },
  { title: "Transmission?", subtitle: null },
  { title: "Anything non-negotiable?", subtitle: "Skip if nothing is a hard requirement." },
] as const;
