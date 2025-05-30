import React from 'react';
import { Persona } from "@/types/brandTypes";
import { ScrollArea } from "@/components/ui/scroll-area";

interface PersonaNavigationProps {
  personas: Persona[];
  selectedPersonaId: string;
  onPersonaSelect: (personaId: string) => void;
  isMobile: boolean;
}

export const PersonaNavigation = ({
  personas,
  selectedPersonaId,
  onPersonaSelect,
  isMobile
}: PersonaNavigationProps) => {
  return isMobile ? (
    <ScrollArea className="w-full overflow-x-auto">
      <div className="flex space-x-2 pb-2">
        {personas.map((persona) => (
          <button
            key={persona.id}
            onClick={() => onPersonaSelect(persona.id as string)}
            className={`shrink-0 px-4 py-2 rounded-lg border-2 transition-all duration-300 ${
              selectedPersonaId === persona.id
                ? "bg-[#00FFC2] border-[#00FFC2] text-black font-medium"
                : "bg-transparent border-[#00FFC2] text-white"
            }`}
          >
            {persona.name}
          </button>
        ))}
      </div>
    </ScrollArea>
  ) : (
    <div className="w-1/4 min-w-[200px]">
      <div className="space-y-2">
        {personas.map((persona) => (
          <button
            key={persona.id}
            onClick={() => onPersonaSelect(persona.id as string)}
            className={`w-full text-left px-4 py-2 rounded-lg border-2 transition-all duration-300 ${
              selectedPersonaId === persona.id
                ? "bg-[#00FFC2] border-[#00FFC2] text-black font-medium"
                : "bg-transparent border-[#00FFC2] text-white"
            }`}
          >
            {persona.name}
          </button>
        ))}
      </div>
    </div>
  );
};
