
import { Question } from "@/types/brandTypes";

// Generates dummy questions for a given persona ID
export const getDummyQuestions = (personaId: string): Question[] => {
  const baseQuestions = [
    "What specific features are you looking for in our solution?",
    "How important is pricing compared to functionality for you?",
    "What challenges are you currently facing with existing solutions?",
    "How much time do you typically spend researching before making a decision?",
    "What would make you immediately reject a solution?",
    "How do you prefer to receive customer support?",
    "What integrations are essential for your workflow?",
    "How do you measure the success of implementing a new solution?",
    "Who else is involved in your decision-making process?",
    "What timeline are you working with for implementation?"
  ];
  
  return baseQuestions.map((text, index) => ({
    id: `dummy-${personaId}-${index}`,
    text,
    personaId
  }));
};
