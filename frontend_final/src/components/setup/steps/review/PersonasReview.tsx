
import { Persona, Product, Topic } from "@/types/brandTypes";
import { 
  Accordion, 
  AccordionItem, 
  AccordionTrigger, 
  AccordionContent 
} from "@/components/ui/accordion";

interface PersonasReviewProps {
  personas: Persona[];
  topics: Topic[];
  products: Product[];
}

export const PersonasReview = ({ personas, topics, products }: PersonasReviewProps) => {
  if (personas.length === 0) {
    return (
      <div className="text-center p-4 bg-card-dark rounded-md border border-black/20">
        <p className="text-text-secondary">No personas available.</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <Accordion
        type="single"
        collapsible
        defaultValue={personas[0]?.id as string}
        className="w-full"
      >
        {personas.map((persona) => (
          <AccordionItem
            key={persona.id}
            value={persona.id as string}
            className="border border-black/20 rounded-lg bg-card-dark"
          >
            <AccordionTrigger className="px-4 py-3 text-left font-semibold text-base hover:no-underline">
              {persona.name}
            </AccordionTrigger>
            <AccordionContent className="px-4 pb-4">
              <div className="space-y-3">
                <p className="text-sm text-text-secondary">{persona.description}</p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h5 className="text-sm font-medium">Pain Points:</h5>
                    <ul className="list-disc pl-5 space-y-1 mt-1">
                      {persona.painPoints.map((point, idx) => (
                        <li key={idx} className="text-xs">{point}</li>
                      ))}
                    </ul>
                  </div>
                  
                  <div>
                    <h5 className="text-sm font-medium">Motivators:</h5>
                    <ul className="list-disc pl-5 space-y-1 mt-1">
                      {persona.motivators.map((item, idx) => (
                        <li key={idx} className="text-xs">{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                {(persona.topicId || persona.productId) && (
                  <div className="mt-2 text-xs">
                    <h5 className="font-medium">Related To:</h5>
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
    </div>
  );
};
