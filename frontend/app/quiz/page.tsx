"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import ProgressBar from "@/components/ProgressBar";
import BudgetSlider from "@/components/questions/BudgetSlider";
import SingleSelect from "@/components/questions/SingleSelect";
import MultiSelect from "@/components/questions/MultiSelect";
import MultiSelectChips from "@/components/questions/MultiSelectChips";
import { getRecommendations } from "@/lib/api";
import type { QuizAnswers } from "@/lib/types";

const TOTAL_STEPS = 7;

const INITIAL_ANSWERS: QuizAnswers = {
  budget: { comfortable: 1_000_000, stretch: 1_500_000, price_type: "on_road" },
  passengers: "",
  usage_terrain: [],
  regret_factors: [],
  fuel: "",
  transmission: "",
  non_negotiables: [],
};

const PASSENGERS_OPTIONS = [
  { id: "solo", label: "Just me (maybe one passenger)" },
  { id: "couple", label: "Me and my partner" },
  { id: "small_family", label: "Small family — 3 to 4 people, occasional guests" },
  { id: "full_household", label: "Full household — 5+ regularly, including kids or elderly" },
  { id: "varies", label: "Varies a lot — need flexibility" },
];

const TERRAIN_OPTIONS = [
  { id: "dense_city", label: "Dense city traffic — parking is a pain" },
  { id: "highways", label: "Highways and long drives" },
  { id: "bad_roads", label: "Bad roads, potholes, or unpaved stretches" },
  { id: "hills_rain", label: "Hills or heavy rain regularly" },
  { id: "short_errands", label: "Mostly short errands close to home" },
];

const REGRET_OPTIONS = [
  { id: "cramped", label: "Felt cramped or impractical" },
  { id: "expensive_to_run", label: "Expensive to run or service" },
  { id: "not_safe", label: "Didn't feel safe enough" },
  { id: "boring", label: "Boring or didn't turn heads" },
  { id: "poor_terrain", label: "Couldn't handle rough roads or long trips" },
  { id: "depreciated", label: "Depreciated too fast when I tried to sell" },
  { id: "too_much_car", label: "Too much car for what I actually needed" },
];

const FUEL_OPTIONS = [
  { id: "petrol", label: "Petrol" },
  { id: "diesel", label: "Diesel" },
  { id: "hybrid", label: "Hybrid" },
  { id: "electric", label: "Electric" },
  { id: "no_preference", label: "No strong preference — recommend what fits" },
];

const TRANSMISSION_OPTIONS = [
  { id: "manual", label: "Manual" },
  { id: "automatic", label: "Automatic" },
  { id: "either", label: "Either — whichever is better for the car" },
];

const NON_NEGOTIABLES_OPTIONS = [
  { id: "sunroof", label: "Sunroof" },
  { id: "six_airbags", label: "6 airbags or more" },
  { id: "camera_360", label: "360° camera" },
  { id: "ventilated_seats", label: "Ventilated seats" },
  { id: "adas", label: "ADAS features" },
  { id: "third_row", label: "Third row seating" },
  { id: "good_resale", label: "Good resale value" },
  { id: "reliable_brand", label: "Known reliable brand" },
  { id: "surprise_me", label: "None of these — surprise me" },
];

function isStepComplete(step: number, answers: QuizAnswers): boolean {
  switch (step) {
    case 1: return answers.budget.comfortable > 0 && answers.budget.stretch > answers.budget.comfortable;
    case 2: return !!answers.passengers;
    case 3: return answers.usage_terrain.length >= 1;
    case 4: return answers.regret_factors.length >= 1;
    case 5: return !!answers.fuel;
    case 6: return !!answers.transmission;
    case 7: return true; // optional
    default: return false;
  }
}

const STEP_META = [
  { title: "What's your budget?", subtitle: "We'll show cars that fit comfortably, and a few that stretch." },
  { title: "Who's usually in the car?", subtitle: "Think about your typical day, not edge cases." },
  { title: "Where does this car mostly live?", subtitle: "Pick up to 2." },
  { title: "What would make you regret this purchase in 2 years?", subtitle: "Pick up to 3. This helps us understand what matters most." },
  { title: "Fuel preference?", subtitle: null },
  { title: "Transmission?", subtitle: null },
  { title: "Anything non-negotiable?", subtitle: "Skip if nothing is a hard requirement." },
];

export default function QuizPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [answers, setAnswers] = useState<QuizAnswers>(INITIAL_ANSWERS);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const meta = STEP_META[step - 1];
  const canProceed = isStepComplete(step, answers);

  const handleNext = async () => {
    if (!canProceed) return;
    if (step < TOTAL_STEPS) {
      setStep((s) => s + 1);
      return;
    }
    // Final step — submit
    setIsLoading(true);
    setError(null);
    try {
      const response = await getRecommendations(answers);
      sessionStorage.setItem("carparkho_results", JSON.stringify(response));
      router.push("/results");
    } catch {
      setError("Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    if (step > 1) setStep((s) => s - 1);
    else router.push("/");
  };

  return (
    <main className="min-h-screen flex flex-col bg-[#F7F8FA]">
      {/* Header */}
      <header className="px-5 pt-5 pb-4 bg-white border-b border-border">
        <div className="w-full max-w-sm mx-auto flex flex-col gap-4">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={handleBack}
              className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors text-secondary"
              aria-label="Go back"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 20 20">
                <path d="M12 4l-6 6 6 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
            <div className="flex items-center gap-1.5">
              <Image src="/logo.png" alt="Car Parkho" width={22} height={22} className="rounded-md" />
              <span className="text-coral text-sm font-bold">Car Parkho</span>
            </div>
          </div>
          <ProgressBar current={step} total={TOTAL_STEPS} />
        </div>
      </header>

      {/* Question */}
      <div className="flex-1 overflow-y-auto px-5 py-6">
        <div className="w-full max-w-sm mx-auto flex flex-col gap-6">
          <div>
            <h1 className="text-charcoal text-2xl font-bold leading-snug">{meta.title}</h1>
            {meta.subtitle && (
              <p className="text-secondary text-sm mt-1.5">{meta.subtitle}</p>
            )}
          </div>

          {step === 1 && (
            <BudgetSlider
              value={answers.budget}
              onChange={(budget) => setAnswers((a) => ({ ...a, budget }))}
            />
          )}
          {step === 2 && (
            <SingleSelect
              options={PASSENGERS_OPTIONS}
              value={answers.passengers}
              onChange={(passengers) => setAnswers((a) => ({ ...a, passengers }))}
            />
          )}
          {step === 3 && (
            <MultiSelect
              options={TERRAIN_OPTIONS}
              value={answers.usage_terrain}
              onChange={(usage_terrain) => setAnswers((a) => ({ ...a, usage_terrain }))}
              maxSelections={2}
            />
          )}
          {step === 4 && (
            <MultiSelect
              options={REGRET_OPTIONS}
              value={answers.regret_factors}
              onChange={(regret_factors) => setAnswers((a) => ({ ...a, regret_factors }))}
              maxSelections={3}
            />
          )}
          {step === 5 && (
            <SingleSelect
              options={FUEL_OPTIONS}
              value={answers.fuel}
              onChange={(fuel) => setAnswers((a) => ({ ...a, fuel }))}
            />
          )}
          {step === 6 && (
            <SingleSelect
              options={TRANSMISSION_OPTIONS}
              value={answers.transmission}
              onChange={(transmission) => setAnswers((a) => ({ ...a, transmission }))}
            />
          )}
          {step === 7 && (
            <MultiSelectChips
              options={NON_NEGOTIABLES_OPTIONS}
              value={answers.non_negotiables}
              onChange={(non_negotiables) => setAnswers((a) => ({ ...a, non_negotiables }))}
            />
          )}

          {error && (
            <p className="text-red-500 text-sm text-center">{error}</p>
          )}
        </div>
      </div>

      {/* Footer CTA */}
      <div className="px-5 py-4 bg-white border-t border-border">
        <div className="w-full max-w-sm mx-auto flex flex-col gap-3">
          <button
            type="button"
            onClick={handleNext}
            disabled={!canProceed || isLoading}
            className="w-full py-4 bg-coral text-white text-base font-bold rounded-[8px] hover:bg-orange-600 transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
                Finding your cars…
              </>
            ) : step === TOTAL_STEPS ? (
              "Show my recommendations →"
            ) : (
              "Next →"
            )}
          </button>
          {step === TOTAL_STEPS && (
            <p className="text-secondary text-xs text-center">
              This takes about 3–5 seconds
            </p>
          )}
        </div>
      </div>
    </main>
  );
}
