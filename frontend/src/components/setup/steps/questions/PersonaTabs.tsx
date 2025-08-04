import React from 'react';
import { Persona, Question } from "@/types/brandTypes";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";

interface PersonaTabsProps {
  personas: Persona[];
  selectedPersonaId: string;
  onPersonaSelect: (personaId: string) => void;
  questionsByPersona: Record<string, Question[]>;
}

export const PersonaTabs = ({
  personas,
  selectedPersonaId,
  onPersonaSelect,
  questionsByPersona
}: PersonaTabsProps) => {
  const getQuestionCount = (personaId: string) => {
    return questionsByPersona[personaId]?.length || 0;
  };

  return (
    <div className="w-full">
      <div className="mb-3">
        <h3 className="text-sm font-medium text-white/80 mb-2">Select Persona</h3>
        <p className="text-xs text-white/60">
          Choose a persona to view and edit their questions
        </p>
      </div>
      
      <ScrollArea className="w-full overflow-x-auto">
        <div className="flex gap-2 pb-2 min-w-max">
          {personas.map((persona) => {
            const questionCount = getQuestionCount(persona.id as string);
            const isSelected = selectedPersonaId === persona.id;
            
            return (
              <button
                key={persona.id}
                onClick={() => onPersonaSelect(persona.id as string)}
                className={`relative px-4 py-3 rounded-lg border-2 transition-all duration-300 whitespace-nowrap min-w-0 ${
                  isSelected
                    ? "bg-[#00FFC2] border-[#00FFC2] text-black font-medium shadow-lg"
                    : "bg-background/50 border-border/50 text-white hover:bg-[#00FFC2]/10 hover:border-[#00FFC2]/50"
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className="min-w-0">
                    <div className="font-medium text-sm truncate max-w-[120px]">
                      {persona.name}
                    </div>
                    <div className={`text-xs truncate max-w-[120px] mt-0.5 ${
                      isSelected ? "text-black/70" : "text-white/60"
                    }`}>
                      {persona.description}
                    </div>
                  </div>
                  
                  <Badge 
                    variant="secondary" 
                    className={`text-xs shrink-0 ${
                      isSelected 
                        ? "bg-black/20 text-black border-black/20" 
                        : "bg-white/20 text-white border-white/20"
                    }`}
                  >
                    {questionCount}
                  </Badge>
                </div>
                
                {/* Active indicator */}
                {isSelected && (
                  <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-6 h-0.5 bg-black rounded-full"></div>
                )}
              </button>
            );
          })}
        </div>
      </ScrollArea>
    </div>
  );
};