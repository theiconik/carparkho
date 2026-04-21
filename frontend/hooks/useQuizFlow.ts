"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { getRecommendations } from "@/lib/api";
import { INITIAL_ANSWERS, STEP_META, TOTAL_STEPS } from "@/lib/quiz/constants";
import { RESULTS_STORAGE_KEY } from "@/lib/quiz/storage";
import { isStepComplete } from "@/lib/quiz/validation";
import type { QuizAnswers } from "@/lib/types";

export function useQuizFlow() {
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
    setIsLoading(true);
    setError(null);
    try {
      const response = await getRecommendations(answers);
      sessionStorage.setItem(RESULTS_STORAGE_KEY, JSON.stringify(response));
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

  return {
    step,
    answers,
    setAnswers,
    meta,
    canProceed,
    isLoading,
    error,
    totalSteps: TOTAL_STEPS,
    handleNext,
    handleBack,
  };
}
