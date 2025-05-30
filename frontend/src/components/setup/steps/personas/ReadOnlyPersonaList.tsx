
import { Persona, Topic, Product } from "@/types/brandTypes";
import { 
  Accordion, 
  AccordionItem, 
  AccordionTrigger, 
  AccordionContent 
} from "@/components/ui/accordion";
import { useState } from "react";

interface ReadOnlyPersonaListProps {
  personas: Persona[];
  topics: Topic[];
  products: Product[];
}

// Dummy personas for testing
const dummyPersonas: Persona[] = [
  {
    id: "dummy-1",
    name: "Tech Professional",
    description: "Technology professionals who are looking for advanced solutions to improve workflow efficiency.",
    painPoints: ["Limited time for research", "Complex integration requirements", "Need for reliable support"],
    motivators: ["Productivity improvements", "Time savings", "Cutting-edge features"],
    demographics: {
      ageRange: "28-45",
      gender: "All genders",
      location: "Urban areas",
      goals: ["Streamline workflows", "Reduce overhead costs"]
    }
  },
  {
    id: "dummy-2",
    name: "Small Business Owner",
    description: "Entrepreneurs and small business owners seeking cost-effective solutions.",
    painPoints: ["Budget constraints", "Limited technical knowledge", "Need for simple solutions"],
    motivators: ["Cost savings", "Easy implementation", "Growth opportunities"],
    demographics: {
      ageRange: "30-55",
      gender: "All genders",
      location: "Nationwide",
      goals: ["Expand customer base", "Optimize operations"]
    }
  },
  {
    id: "dummy-3",
    name: "Creative Professional",
    description: "Designers, writers, and content creators who need tools to enhance their creative output.",
    painPoints: ["Deadline pressures", "Need for inspiration", "Technical limitations"],
    motivators: ["Enhanced creative freedom", "Collaboration features", "Portfolio showcase options"],
    demographics: {
      ageRange: "25-40",
      gender: "All genders",
      location: "Urban creative hubs",
      goals: ["Improve creative output", "Find new clients"]
    }
  }
];

export const ReadOnlyPersonaList = ({ personas, topics, products }: ReadOnlyPersonaListProps) => {
  // Use provided personas or fallback to dummy personas if empty
  const displayPersonas = personas.length > 0 ? personas : dummyPersonas;
  
  const [defaultValue, setDefaultValue] = useState<string | undefined>(
    displayPersonas.length > 0 ? displayPersonas[0].id as string : undefined
  );

  return (
    <Accordion
      type="single"
      collapsible
      defaultValue={defaultValue}
      className="w-full space-y-2"
    >
      {displayPersonas.map((persona) => (
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
            </div>
          </AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  );
};
