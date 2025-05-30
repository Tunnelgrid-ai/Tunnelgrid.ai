
export const STEPS = [
  "brand-info",
  "topics",
  "personas",
  "questions",
  "review"
] as const;

export type SetupStep = typeof STEPS[number];

export const stepLabels = {
  "brand-info": "Brand & Product",
  "topics": "Topics",
  "personas": "Personas",
  "questions": "Questions",
  "review": "Review"
};
