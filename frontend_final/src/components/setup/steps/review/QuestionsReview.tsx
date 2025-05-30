import React from 'react';
import { Question, Persona } from "@/types/brandTypes";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ChevronDown, ChevronRight } from "lucide-react";
import { useState } from "react";

interface QuestionsReviewProps {
  questions: Question[];
  personas: Persona[];
}

export const QuestionsReview = ({ questions, personas }: QuestionsReviewProps) => {
  const [openPersonas, setOpenPersonas] = useState<Set<string>>(new Set());

  const togglePersona = (personaId: string) => {
    const newOpenPersonas = new Set(openPersonas);
    if (newOpenPersonas.has(personaId)) {
      newOpenPersonas.delete(personaId);
    } else {
      newOpenPersonas.add(personaId);
    }
    setOpenPersonas(newOpenPersonas);
  };

  // Group questions by persona
  const questionsByPersona: Record<string, Question[]> = {};
  personas.forEach(persona => {
    const personaQuestions = questions.filter(q => q.personaId === persona.id);
    questionsByPersona[persona.id] = personaQuestions;
  });

  if (questions.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-text-secondary">No questions have been generated yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="text-sm text-text-secondary">
        Total Questions: {questions.length} across {personas.length} personas
      </div>

      {personas.map((persona) => {
        const personaQuestions = questionsByPersona[persona.id] || [];
        const isOpen = openPersonas.has(persona.id);

        return (
          <Collapsible
            key={persona.id}
            open={isOpen}
            onOpenChange={() => togglePersona(persona.id)}
          >
            <CollapsibleTrigger className="flex items-center justify-between w-full p-3 bg-card-dark border border-black/20 rounded-lg hover:bg-card-dark/80 transition-colors">
              <div className="flex items-center space-x-3">
                {isOpen ? (
                  <ChevronDown className="h-4 w-4 text-[#00FFC2]" />
                ) : (
                  <ChevronRight className="h-4 w-4 text-[#00FFC2]" />
                )}
                <span className="font-medium text-white">{persona.name}</span>
                <span className="text-sm text-text-secondary">
                  ({personaQuestions.length} questions)
                </span>
              </div>
            </CollapsibleTrigger>

            <CollapsibleContent className="mt-2">
              <div className="p-4 bg-background border border-black/20 rounded-lg">
                {personaQuestions.length > 0 ? (
                  <ol className="space-y-2 list-decimal pl-6">
                    {personaQuestions.map((question, index) => (
                      <li key={question.id} className="text-sm text-white">
                        {question.text}
                      </li>
                    ))}
                  </ol>
                ) : (
                  <p className="text-text-secondary text-center py-4">
                    No questions generated for this persona.
                  </p>
                )}
              </div>
            </CollapsibleContent>
          </Collapsible>
        );
      })}
    </div>
  );
};
