
import { Persona, Topic, Product } from "@/types/brandTypes";
import { 
  Accordion, 
  AccordionItem, 
  AccordionTrigger, 
  AccordionContent 
} from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { Edit, Trash2 } from "lucide-react";
import { useState } from "react";

interface PersonaAccordionListProps {
  personas: Persona[];
  topics: Topic[];
  products: Product[];
  onEdit: (persona: Persona) => void;
  onDelete: (id: string) => void;
}

export const PersonaAccordionList = ({ personas, topics, products, onEdit, onDelete }: PersonaAccordionListProps) => {
  const [defaultValue, setDefaultValue] = useState<string | undefined>(
    personas.length > 0 ? personas[0].id as string : undefined
  );

  if (personas.length === 0) {
    return null;
  }

  return (
    <Accordion
      type="single"
      collapsible
      defaultValue={defaultValue}
      className="w-full space-y-2"
    >
      {personas.map((persona) => (
        <AccordionItem
          key={persona.id}
          value={persona.id as string}
          className="border border-black/20 rounded-lg bg-card-dark overflow-hidden"
        >
          <AccordionTrigger className="px-4 py-3 text-left font-semibold text-base hover:no-underline">
            {persona.name}
          </AccordionTrigger>
          <AccordionContent className="px-4 pb-4">
            <div className="space-y-4">
              <p className="text-sm text-text-secondary">{persona.description}</p>
              
              {/* Pain Points */}
              {persona.painPoints.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm mb-1">Pain Points:</h4>
                  <ul className="list-disc pl-5 space-y-1">
                    {persona.painPoints.map((point, idx) => (
                      <li key={idx} className="text-sm">{point}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Motivators */}
              {persona.motivators.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm mb-1">Motivators:</h4>
                  <ul className="list-disc pl-5 space-y-1">
                    {persona.motivators.map((motivator, idx) => (
                      <li key={idx} className="text-sm">{motivator}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Demographics */}
              {persona.demographics && Object.keys(persona.demographics).length > 0 && (
                <div>
                  <h4 className="font-medium text-sm mb-1">Demographics:</h4>
                  <div className="text-sm space-y-1">
                    {persona.demographics.ageRange && (
                      <p>Age: {persona.demographics.ageRange}</p>
                    )}
                    {persona.demographics.gender && (
                      <p>Gender: {persona.demographics.gender}</p>
                    )}
                    {persona.demographics.location && (
                      <p>Location: {persona.demographics.location}</p>
                    )}
                    {persona.demographics.goals && persona.demographics.goals.length > 0 && (
                      <div>
                        <p className="font-medium">Goals:</p>
                        <ul className="list-disc pl-5">
                          {persona.demographics.goals.map((goal, idx) => (
                            <li key={idx}>{goal}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              {/* Related Topics/Products */}
              {(persona.topicId || persona.productId) && (
                <div className="text-sm">
                  <h4 className="font-medium mb-1">Related To:</h4>
                  {persona.topicId && (
                    <p>
                      Topic: {topics.find(t => t.id === persona.topicId)?.name}
                    </p>
                  )}
                  {persona.productId && (
                    <p>
                      Product: {products.find(p => p.id === persona.productId)?.name}
                    </p>
                  )}
                </div>
              )}
              
              <div className="flex justify-end gap-2 pt-2 mt-2 border-t border-black/10">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onEdit(persona)}
                >
                  <Edit className="h-4 w-4 mr-2" /> Edit
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="text-red-500"
                  onClick={() => onDelete(persona.id as string)}
                >
                  <Trash2 className="h-4 w-4 mr-2" /> Delete
                </Button>
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  );
};
