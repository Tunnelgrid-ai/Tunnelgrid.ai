
import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Product, Topic, Persona } from "@/types/brandTypes";
import { PainPointsInput } from "./PainPointsInput";
import { MotivatorsInput } from "./MotivatorsInput";
import { DemographicsInput } from "./DemographicsInput";
import { 
  Accordion, 
  AccordionItem, 
  AccordionTrigger, 
  AccordionContent 
} from "@/components/ui/accordion";
import { ChevronDown } from "lucide-react";

interface PersonaFormProps {
  editingPersonaId: string | null;
  persona: {
    name: string;
    description: string;
    painPoints: string[];
    motivators: string[];
    demographics: {
      ageRange?: string;
      gender?: string;
      location?: string;
      goals?: string[];
    };
    topicId: string;
    productId: string;
  };
  topics: Topic[];
  products: Product[];
  onSubmit: () => void;
  onValueChange: (field: string, value: any) => void;
}

export const PersonaForm = ({ 
  editingPersonaId, 
  persona, 
  topics, 
  products, 
  onSubmit, 
  onValueChange 
}: PersonaFormProps) => {
  return (
    <div className="border border-black/20 rounded-lg p-4 space-y-4 bg-card-dark">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="persona-name">Persona Name</Label>
          <Input
            id="persona-name"
            value={persona.name}
            onChange={(e) => onValueChange("name", e.target.value)}
            placeholder="e.g., Budget-Conscious Fitness Enthusiast"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="persona-description">Short Description</Label>
          <Input
            id="persona-description"
            value={persona.description}
            onChange={(e) => onValueChange("description", e.target.value)}
            placeholder="Briefly describe this persona"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {topics.length > 0 && (
          <div className="space-y-2">
            <Label htmlFor="topic-select">Related Topic (optional)</Label>
            <Select
              value={persona.topicId}
              onValueChange={(value) => onValueChange("topicId", value)}
            >
              <SelectTrigger id="topic-select">
                <SelectValue placeholder="Select a topic" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">None</SelectItem>
                {topics.map((topic) => (
                  <SelectItem key={topic.id} value={topic.id as string}>
                    {topic.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        {products.length > 0 && (
          <div className="space-y-2">
            <Label htmlFor="product-select">Related Product (optional)</Label>
            <Select
              value={persona.productId}
              onValueChange={(value) => onValueChange("productId", value)}
            >
              <SelectTrigger id="product-select">
                <SelectValue placeholder="Select a product" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">None</SelectItem>
                {products.map((product) => (
                  <SelectItem key={product.id} value={product.id as string}>
                    {product.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}
      </div>

      <PainPointsInput 
        painPoints={persona.painPoints} 
        setPainPoints={(points) => onValueChange("painPoints", points)} 
      />

      <MotivatorsInput 
        motivators={persona.motivators} 
        setMotivators={(motivators) => onValueChange("motivators", motivators)} 
      />

      <DemographicsInput 
        demographics={persona.demographics} 
        setDemographics={(demographics) => onValueChange("demographics", demographics)} 
      />

      <div className="flex justify-end">
        <Button onClick={onSubmit}>
          {editingPersonaId ? "Update Persona" : "Add Persona"}
        </Button>
      </div>
    </div>
  );
};
