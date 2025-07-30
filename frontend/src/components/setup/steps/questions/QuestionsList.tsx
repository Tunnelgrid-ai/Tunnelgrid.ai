import React, { useState } from 'react';
import { Persona, Question } from "@/types/brandTypes";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Edit, Check, X } from "lucide-react";

interface QuestionsListProps {
  selectedPersonaId: string;
  personas: Persona[];
  questionsByPersona: Record<string, Question[]>;
  onQuestionUpdate?: (questionId: string, newText: string) => void;
}

export const QuestionsList = ({ 
  selectedPersonaId, 
  personas, 
  questionsByPersona,
  onQuestionUpdate 
}: QuestionsListProps) => {
  const [editingQuestionId, setEditingQuestionId] = useState<string | null>(null);
  const [editText, setEditText] = useState<string>("");

  const selectedPersona = personas.find(p => p.id === selectedPersonaId);
  const questionsForSelected = questionsByPersona[selectedPersonaId];

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

  return (
    <div 
      className="bg-card-dark rounded-lg border-2 border-[#00FFC2] p-4 h-[400px] overflow-auto"
    >
      {selectedPersonaId && personas.find(p => p.id === selectedPersonaId) ? (
        <div className="space-y-4">
          <h3 className="font-medium text-white">
            Questions for {personas.find(p => p.id === selectedPersonaId)?.name}
          </h3>
          
          {questionsByPersona[selectedPersonaId] && 
            questionsByPersona[selectedPersonaId].length > 0 ? (
            <div>
              <ol className="space-y-3 list-decimal pl-6">
                {questionsByPersona[selectedPersonaId].map((question, index) => (
                  <li key={question.id || index} className="text-sm text-white">
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
                          <span>
                            {question.text || `[MISSING TEXT - Question ID: ${question.id}]`}
                          </span>
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
            </div>
          ) : (
            <div>
              <p className="text-text-secondary text-center py-8">
                No questions available for this persona.
              </p>
            </div>
          )}
        </div>
      ) : (
        <div>
          <p className="text-text-secondary text-center py-8">
            Select a persona to view questions.
          </p>
        </div>
      )}
    </div>
  );
};
