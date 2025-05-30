
import { Persona, Topic, Product } from "@/types/brandTypes";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Edit, Trash2 } from "lucide-react";

interface PersonaCardProps {
  persona: Persona;
  topics: Topic[];
  products: Product[];
  onEdit: (persona: Persona) => void;
  onDelete: (id: string) => void;
}

export const PersonaCard = ({ 
  persona, 
  topics, 
  products, 
  onEdit, 
  onDelete 
}: PersonaCardProps) => {
  return (
    <Card key={persona.id} className="bg-card-dark border-black/20">
      <CardHeader>
        <CardTitle className="font-heading">{persona.name}</CardTitle>
        <CardDescription>{persona.description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h4 className="text-sm font-semibold font-heading mb-1">Pain Points:</h4>
          <ul className="list-disc pl-5 space-y-1">
            {persona.painPoints.map((point, idx) => (
              <li key={idx} className="text-sm">{point}</li>
            ))}
          </ul>
        </div>
        
        <div>
          <h4 className="text-sm font-semibold font-heading mb-1">Motivators:</h4>
          <ul className="list-disc pl-5 space-y-1">
            {persona.motivators.map((item, idx) => (
              <li key={idx} className="text-sm">{item}</li>
            ))}
          </ul>
        </div>
        
        {persona.demographics && Object.keys(persona.demographics).length > 0 && (
          <div>
            <h4 className="text-sm font-semibold font-heading mb-1">Demographics:</h4>
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
        
        {(persona.topicId || persona.productId) && (
          <div className="text-sm">
            <h4 className="font-semibold font-heading mb-1">Related To:</h4>
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
      </CardContent>
      <CardFooter className="flex justify-end space-x-2">
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
      </CardFooter>
    </Card>
  );
};
