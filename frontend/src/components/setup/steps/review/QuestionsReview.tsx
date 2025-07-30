import React, { useState } from 'react';
import { Question, Persona } from "@/types/brandTypes";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ChevronDown, ChevronRight, Edit, Check, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface QuestionsReviewProps {
  questions: Question[];
  personas: Persona[];
  onQuestionUpdate?: (questionId: string, newText: string) => void;
}

export const QuestionsReview = ({ questions, personas, onQuestionUpdate }: QuestionsReviewProps) => {
  const [openPersonas, setOpenPersonas] = useState<Set<string>>(new Set());
  const [editingQuestionId, setEditingQuestionId] = useState<string | null>(null);
  const [editText, setEditText] = useState<string>("");

  const togglePersona = (personaId: string) => {
    const newOpenPersonas = new Set(openPersonas);
    if (newOpenPersonas.has(personaId)) {
      newOpenPersonas.delete(personaId);
    } else {
      newOpenPersonas.add(personaId);
    }
    setOpenPersonas(newOpenPersonas);
  };

  const handleEditClick = (question: Question) => {
    setEditingQuestionId(question.id);
    setEditText(question.text);
  };

  const handleSaveEdit = () => {
    if (editingQuestionId && editText.trim() && onQuestionUpdate) {
      onQuestionUpdate(editingQuestionId, editText.trim());
      setEditingQuestionId(null);
      setEditText("");
    }
  };

  const handleCancelEdit = () => {
    setEditingQuestionId(null);
    setEditText("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSaveEdit();
    } else if (e.key === "Escape") {
      handleCancelEdit();
    }
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
                        <div className="flex items-start gap-2 group">
                          <div className="flex-1 break-words">
                            {editingQuestionId === question.id ? (
                              <Input
                                value={editText}
                                onChange={(e) => setEditText(e.target.value)}
                                onKeyDown={handleKeyDown}
                                className="text-sm bg-background border-[#00FFC2] focus:border-[#00FFC2] text-white"
                                autoFocus
                              />
                            ) : (
                              <span>{question.text}</span>
                            )}
                          </div>
                          <div className="flex items-center gap-1 opacity-60 hover:opacity-100 transition-opacity">
                            {editingQuestionId === question.id ? (
                              <>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={handleSaveEdit}
                                  className="h-6 w-6 p-0 text-green-400 hover:text-green-300"
                                >
                                  <Check className="h-3 w-3" />
                                </Button>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={handleCancelEdit}
                                  className="h-6 w-6 p-0 text-red-400 hover:text-red-300"
                                >
                                  <X className="h-3 w-3" />
                                </Button>
                              </>
                            ) : (
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handleEditClick(question)}
                                className="h-6 w-6 p-0 text-[#00FFC2] hover:text-[#00E5AC]"
                              >
                                <Edit className="h-3 w-3" />
                              </Button>
                            )}
                          </div>
                        </div>
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
