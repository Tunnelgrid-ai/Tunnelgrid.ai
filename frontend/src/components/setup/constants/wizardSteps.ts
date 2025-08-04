
export const STEPS = [
  "brand-info",
  "topics",
  "personas",
  "questions",
  "review"
] as const;

export type SetupStep = typeof STEPS[number];

export const stepLabels = {
  "brand-info": "Verify Brand & Product",
  "topics": "Select Topics",
  "personas": "Review Personas", 
  "questions": "Review & Edit Prompts",
  "review": "Review & Launch"
};
