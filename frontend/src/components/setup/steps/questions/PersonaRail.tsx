import React from 'react';
import { Persona, Question } from "@/types/brandTypes";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface PersonaRailProps {
  personas: Persona[];
  selectedPersonaId: string;
  onPersonaSelect: (personaId: string) => void;
  questionsByPersona: Record<string, Question[]>;
}

export const PersonaRail = ({
  personas,
  selectedPersonaId,
  onPersonaSelect,
  questionsByPersona
}: PersonaRailProps) => {
  return (
    <TooltipProvider delayDuration={200}>
      <div className="w-full">
        {/* Desktop Grid View */}
        <div className="hidden sm:block">
          <div className="grid grid-cols-4 gap-3 place-content-center max-w-3xl mx-auto">
            {personas.map((persona) => {
              const isSelected = selectedPersonaId === persona.id;
              
              return (
                <Tooltip key={persona.id}>
                  <TooltipTrigger asChild>
                    <button
                      onClick={() => onPersonaSelect(persona.id as string)}
                      className={`px-3 py-2 rounded-lg border-2 transition-all duration-300 text-center min-h-[44px] ${
                        isSelected
                          ? "bg-[#00FFC2] border-[#00FFC2] text-black font-medium shadow-lg"
                          : "bg-background/50 border-border/50 text-white hover:bg-[#00FFC2]/10 hover:border-[#00FFC2]/50"
                      }`}
                    >
                      <div className="font-medium text-sm truncate">
                        {persona.name}
                      </div>
                    </button>
                  </TooltipTrigger>
                  <TooltipContent side="top" className="bg-gray-800 text-white p-3 rounded max-w-xs">
                    <div className="space-y-1">
                      <p className="font-medium">{persona.name}</p>
                      <p className="text-sm text-gray-300">{persona.description}</p>
                    </div>
                  </TooltipContent>
                </Tooltip>
              );
            })}
            {/* Empty cell for centering if needed */}
            {personas.length === 7 && <div></div>}
          </div>
        </div>

        {/* Mobile Horizontal Scroll */}
        <div className="sm:hidden">
          <ScrollArea className="w-full overflow-x-auto">
            <div className="flex gap-2 pb-2 min-w-max">
              {personas.map((persona) => {
                const isSelected = selectedPersonaId === persona.id;
                
                return (
                  <Tooltip key={persona.id}>
                    <TooltipTrigger asChild>
                      <button
                        onClick={() => onPersonaSelect(persona.id as string)}
                        className={`px-3 py-2 rounded-lg border-2 transition-all duration-300 whitespace-nowrap ${
                          isSelected
                            ? "bg-[#00FFC2] border-[#00FFC2] text-black font-medium shadow-lg"
                            : "bg-background/50 border-border/50 text-white hover:bg-[#00FFC2]/10 hover:border-[#00FFC2]/50"
                        }`}
                      >
                        <div className="font-medium text-sm">
                          {persona.name}
                        </div>
                      </button>
                    </TooltipTrigger>
                    <TooltipContent side="top" className="bg-gray-800 text-white p-3 rounded max-w-xs">
                      <div className="space-y-1">
                        <p className="font-medium">{persona.name}</p>
                        <p className="text-sm text-gray-300">{persona.description}</p>
                      </div>
                    </TooltipContent>
                  </Tooltip>
                );
              })}
            </div>
          </ScrollArea>
        </div>
      </div>
    </TooltipProvider>
  );
};