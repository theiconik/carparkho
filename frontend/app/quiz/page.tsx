"use client";

import Image from "next/image";
import ProgressBar from "@/components/ProgressBar";
import BudgetSlider from "@/components/questions/BudgetSlider";
import SingleSelect from "@/components/questions/SingleSelect";
import MultiSelect from "@/components/questions/MultiSelect";
import MultiSelectChips from "@/components/questions/MultiSelectChips";
import { useQuizFlow } from "@/hooks/useQuizFlow";
import {
  FUEL_OPTIONS,
  NON_NEGOTIABLES_OPTIONS,
  PASSENGERS_OPTIONS,
  REGRET_OPTIONS,
  TERRAIN_OPTIONS,
  TRANSMISSION_OPTIONS,
} from "@/lib/quiz/constants";

export default function QuizPage() {
  const {
    step,
    answers,
    setAnswers,
    meta,
    canProceed,
    isLoading,
    error,
    totalSteps,
    handleNext,
    handleBack,
  } = useQuizFlow();

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
          <ProgressBar current={step} total={totalSteps} />
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
              options={[...PASSENGERS_OPTIONS]}
              value={answers.passengers}
              onChange={(passengers) => setAnswers((a) => ({ ...a, passengers }))}
            />
          )}
          {step === 3 && (
            <MultiSelect
              options={[...TERRAIN_OPTIONS]}
              value={answers.usage_terrain}
              onChange={(usage_terrain) => setAnswers((a) => ({ ...a, usage_terrain }))}
              maxSelections={2}
            />
          )}
          {step === 4 && (
            <MultiSelect
              options={[...REGRET_OPTIONS]}
              value={answers.regret_factors}
              onChange={(regret_factors) => setAnswers((a) => ({ ...a, regret_factors }))}
              maxSelections={3}
            />
          )}
          {step === 5 && (
            <SingleSelect
              options={[...FUEL_OPTIONS]}
              value={answers.fuel}
              onChange={(fuel) => setAnswers((a) => ({ ...a, fuel }))}
            />
          )}
          {step === 6 && (
            <SingleSelect
              options={[...TRANSMISSION_OPTIONS]}
              value={answers.transmission}
              onChange={(transmission) => setAnswers((a) => ({ ...a, transmission }))}
            />
          )}
          {step === 7 && (
            <MultiSelectChips
              options={[...NON_NEGOTIABLES_OPTIONS]}
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
            ) : step === totalSteps ? (
              "Show my recommendations →"
            ) : (
              "Next →"
            )}
          </button>
          {step === totalSteps && (
            <p className="text-secondary text-xs text-center">
              This takes about 3–5 seconds
            </p>
          )}
        </div>
      </div>
    </main>
  );
}
