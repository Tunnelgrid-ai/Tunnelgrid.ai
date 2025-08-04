import { useState } from "react";
import { Persona, Topic, Product } from "@/types/brandTypes";
import { 
  Accordion, 
  AccordionItem, 
  AccordionTrigger, 
  AccordionContent 
} from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { updatePersona, type PersonaUpdateRequest } from "@/services/personasService";

import { Pencil, Save, X, Loader2 } from "lucide-react";

interface EditablePersonaListProps {
  personas: Persona[];
  topics: Topic[];
  products: Product[];
  onPersonaUpdate: (updatedPersona: Persona) => void;
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

export const EditablePersonaList = ({ personas, topics, products, onPersonaUpdate }: EditablePersonaListProps) => {
  // Use provided personas or fallback to dummy personas if empty
  const displayPersonas = personas.length > 0 ? personas : dummyPersonas;
  
  const [editingPersonaId, setEditingPersonaId] = useState<string | null>(null);
  const [editingPersona, setEditingPersona] = useState<Persona | null>(null);
  const [openAccordionValue, setOpenAccordionValue] = useState<string | undefined>(
    displayPersonas.length > 0 ? displayPersonas[0].id as string : undefined
  );
  const [showAdditionalContext, setShowAdditionalContext] = useState(false);
  const [additionalContext, setAdditionalContext] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const startEditing = (persona: Persona) => {
    setEditingPersonaId(persona.id as string);
    setEditingPersona({ ...persona });
    // Load existing additional context if it exists
    setAdditionalContext(persona.additionalContext || '');
    setShowAdditionalContext(!!persona.additionalContext);
    // Automatically open the accordion when editing starts
    setOpenAccordionValue(persona.id as string);
  };

  const cancelEditing = () => {
    setEditingPersonaId(null);
    setEditingPersona(null);
    // Reset additional context states
    setShowAdditionalContext(false);
    setAdditionalContext('');
  };

  const saveEditing = async () => {
    if (!editingPersona) return;
    
    setIsSaving(true);
    setSaveError(null);
    
    try {
      // Prepare update request
      const updateRequest: PersonaUpdateRequest = {
        name: editingPersona.name,
        description: editingPersona.description,
        painPoints: editingPersona.painPoints,
        motivators: editingPersona.motivators,
        demographics: editingPersona.demographics
      };
      
      // Call API to update persona
      const response = await updatePersona(editingPersona.id as string, updateRequest);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to update persona');
      }
      
      // Include additional context in the saved persona for local state
      const updatedPersona = {
        ...editingPersona,
        additionalContext: additionalContext.trim() || undefined,
        editedByUser: true
      };
      
      // Update local state via parent component
      onPersonaUpdate(updatedPersona);
      
      console.log('✅ Persona updated successfully:', editingPersona.id);
      
      // Reset editing state
      setEditingPersonaId(null);
      setEditingPersona(null);
      setShowAdditionalContext(false);
      setAdditionalContext('');
      
    } catch (error) {
      console.error('❌ Failed to update persona:', error);
      setSaveError(error instanceof Error ? error.message : 'Failed to update persona');
    } finally {
      setIsSaving(false);
    }
  };

  const updateEditingPersona = (field: string, value: any) => {
    if (!editingPersona) return;
    
    if (field.includes('.')) {
      const [parent, child] = field.split('.');
      setEditingPersona({
        ...editingPersona,
        [parent]: {
          ...(editingPersona[parent as keyof Persona] as object || {}),
          [child]: value
        }
      });
    } else {
      setEditingPersona({
        ...editingPersona,
        [field]: value
      });
    }
  };



  return (
    <div className="w-full">
      <Accordion
        type="single"
        collapsible
        value={openAccordionValue}
        onValueChange={setOpenAccordionValue}
        className="w-full space-y-2"
      >
        {displayPersonas.map((persona) => (
          <AccordionItem
            key={persona.id}
            value={persona.id as string}
            className="border border-[#3A3A3A] rounded-lg bg-card-dark overflow-hidden"
            style={{ borderRadius: '8px' }}
          >
            <AccordionTrigger 
              className="px-4 py-3 text-left font-medium text-base hover:no-underline group relative"
              style={{ padding: '16px' }}
            >
              <h3 className="font-medium">{persona.name}</h3>
              {editingPersonaId !== persona.id && (
                <div
                  className="absolute right-12 top-1/2 transform -translate-y-1/2 p-2 rounded-md hover:bg-accent/10 cursor-pointer transition-colors"
                  onClick={(e) => {
                    e.stopPropagation();
                    startEditing(persona);
                  }}
                >
                  <Pencil className="h-4 w-4" />
                </div>
              )}
            </AccordionTrigger>
            <AccordionContent className="pb-4" style={{ padding: '0 16px 16px 16px' }}>
              {editingPersonaId === persona.id && editingPersona ? (
                <div className="space-y-4">
                  {/* Title */}
                  <div className="space-y-2">
                    <Label className="text-sm font-mono" style={{ fontSize: '14px' }}>Title</Label>
                    <Input
                      value={editingPersona.name}
                      onChange={(e) => updateEditingPersona('name', e.target.value)}
                      className="w-full"
                    />
                  </div>

                  {/* Summary */}
                  <div className="space-y-2">
                    <Label className="text-sm font-mono" style={{ fontSize: '14px' }}>Summary</Label>
                    <Textarea
                      value={editingPersona.description}
                      onChange={(e) => updateEditingPersona('description', e.target.value)}
                      className="w-full"
                      rows={3}
                    />
                  </div>

                  {/* Pain Points */}
                  <div className="space-y-2">
                    <Label className="text-sm font-mono" style={{ fontSize: '14px' }}>Pain Points</Label>
                    <Textarea
                      value={editingPersona.painPoints.length ? '• ' + editingPersona.painPoints.join('\n• ') : ''}
                      onChange={(e) => {
                        const points = e.target.value.split('\n').map(point => 
                          point.replace(/^•\s*/, '').trim()
                        ).filter(point => point.length > 0);
                        updateEditingPersona('painPoints', points);
                      }}
                      placeholder="• Enter pain points, one per line"
                      className="w-full min-h-[80px]"
                      rows={4}
                    />
                  </div>

                  {/* Motivators */}
                  <div className="space-y-2">
                    <Label className="text-sm font-mono" style={{ fontSize: '14px' }}>Motivators</Label>
                    <Textarea
                      value={editingPersona.motivators.length ? '• ' + editingPersona.motivators.join('\n• ') : ''}
                      onChange={(e) => {
                        const motivators = e.target.value.split('\n').map(motivator => 
                          motivator.replace(/^•\s*/, '').trim()
                        ).filter(motivator => motivator.length > 0);
                        updateEditingPersona('motivators', motivators);
                      }}
                      placeholder="• Enter motivators, one per line"
                      className="w-full min-h-[80px]"
                      rows={4}
                    />
                  </div>

                  {/* Demographics */}
                  <div className="space-y-2">
                    <Label className="text-sm font-mono" style={{ fontSize: '14px' }}>Demographics</Label>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="space-y-1">
                        <Label className="text-xs">Age Range</Label>
                        <Input
                          value={editingPersona.demographics?.ageRange || ''}
                          onChange={(e) => updateEditingPersona('demographics.ageRange', e.target.value)}
                          placeholder="e.g., 25-34"
                        />
                      </div>
                      <div className="space-y-1">
                        <Label className="text-xs">Gender</Label>
                        <Input
                          value={editingPersona.demographics?.gender || ''}
                          onChange={(e) => updateEditingPersona('demographics.gender', e.target.value)}
                          placeholder="e.g., All genders"
                        />
                      </div>
                      <div className="space-y-1">
                        <Label className="text-xs">Location</Label>
                        <Input
                          value={editingPersona.demographics?.location || ''}
                          onChange={(e) => updateEditingPersona('demographics.location', e.target.value)}
                          placeholder="e.g., Urban areas"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Goals */}
                  <div className="space-y-2">
                    <Label className="text-sm font-mono" style={{ fontSize: '14px' }}>Goals</Label>
                    <Textarea
                      value={editingPersona.demographics?.goals?.length ? '• ' + editingPersona.demographics.goals.join('\n• ') : ''}
                      onChange={(e) => {
                        const goals = e.target.value.split('\n').map(goal => 
                          goal.replace(/^•\s*/, '').trim()
                        ).filter(goal => goal.length > 0);
                        updateEditingPersona('demographics.goals', goals);
                      }}
                      placeholder="• Enter goals, one per line"
                      className="w-full min-h-[60px]"
                      rows={3}
                    />
                  </div>

                  {/* Add Additional Context */}
                  <div className="pt-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowAdditionalContext(!showAdditionalContext)}
                      className="w-full"
                    >
                      {showAdditionalContext ? 'Hide Additional Context' : 'Add Additional Context'}
                    </Button>
                  </div>

                  {/* Additional Context Text Area */}
                  {showAdditionalContext && (
                    <div className="space-y-2 pt-2">
                      <Label className="text-sm font-mono" style={{ fontSize: '14px' }}>Additional Context</Label>
                      <Textarea
                        value={additionalContext}
                        onChange={(e) => setAdditionalContext(e.target.value)}
                        placeholder="Add any additional context, traits, or details about this persona..."
                        className="w-full min-h-[80px]"
                        rows={4}
                      />
                    </div>
                  )}



                  {/* Error display */}
                  {saveError && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                      <p className="text-sm text-red-600">{saveError}</p>
                    </div>
                  )}

                  {/* Save/Cancel buttons */}
                  <div className="flex gap-2 pt-4">
                    <Button onClick={saveEditing} className="flex-1" disabled={isSaving}>
                      {isSaving ? (
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <Save className="h-4 w-4 mr-2" />
                      )}
                      {isSaving ? 'Saving...' : 'Save'}
                    </Button>
                    <Button variant="outline" onClick={cancelEditing} className="flex-1" disabled={isSaving}>
                      <X className="h-4 w-4 mr-2" />
                      Cancel
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <p className="text-sm text-text-secondary">{persona.description}</p>
                  
                  {/* Pain Points */}
                  {persona.painPoints.length > 0 && (
                    <div>
                      <h4 className="font-medium text-sm mb-1 font-mono" style={{ fontSize: '14px' }}>Pain Points:</h4>
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
                      <h4 className="font-medium text-sm mb-1 font-mono" style={{ fontSize: '14px' }}>Motivators:</h4>
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
                      <h4 className="font-medium text-sm mb-1 font-mono" style={{ fontSize: '14px' }}>Demographics:</h4>
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
                            <p className="font-medium font-mono" style={{ fontSize: '14px' }}>Goals:</p>
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

                  {/* Additional Context */}
                  {persona.additionalContext && (
                    <div>
                      <h4 className="font-medium text-sm mb-1 font-mono" style={{ fontSize: '14px' }}>Additional Context:</h4>
                      <p className="text-sm text-text-secondary whitespace-pre-wrap">{persona.additionalContext}</p>
                    </div>
                  )}

                </div>
              )}
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </div>
  );
};