import type { QuizAnswers } from "@/lib/types";

export function isStepComplete(step: number, answers: QuizAnswers): boolean {
  switch (step) {
    case 1:
      return answers.budget.comfortable > 0 && answers.budget.stretch > answers.budget.comfortable;
    case 2:
      return !!answers.passengers;
    case 3:
      return answers.usage_terrain.length >= 1;
    case 4:
      return answers.regret_factors.length >= 1;
    case 5:
      return !!answers.fuel;
    case 6:
      return !!answers.transmission;
    case 7:
      return true;
    default:
      return false;
  }
}
