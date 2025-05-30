import { useState, useEffect } from "react";
import { Product, Topic, Persona } from "@/types/brandTypes";
import { ReadOnlyPersonaList } from "./personas/ReadOnlyPersonaList";
import { PersonasHeader } from "./personas/PersonasHeader";
import { 
  generatePersonas, 
  storePersonas, 
  getPersonasByAudit,
  convertToFrontendPersona,
  convertToApiPersona,
  type PersonaGenerateRequest
} from "@/services/personasService";
import { RefreshCw, Sparkles, Database, AlertCircle, CheckCircle } from "lucide-react";

interface PersonasStepProps {
  personas: Persona[];
  setPersonas: (personas: Persona[]) => void;
  topics: Topic[];
  products: Product[];
  auditContext?: {
    auditId?: string | null;
    brandId?: string | null;
    brandName?: string;
    brandDescription?: string;
    brandDomain?: string;
    selectedProduct?: string | null;
    selectedProductId?: string | null;
  };
}

export const PersonasStep = ({
  personas,
  setPersonas,
  topics,
  products,
  auditContext,
}: PersonasStepProps) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [hasAttemptedGeneration, setHasAttemptedGeneration] = useState(false);
  const [generationStatus, setGenerationStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  
  useEffect(() => {
    const generatePersonasAutomatically = async () => {
      if (hasAttemptedGeneration || personas.length > 0 || !auditContext?.auditId) {
        return;
      }

      console.log('🎯 Auto-generating personas for audit:', auditContext.auditId);
      setHasAttemptedGeneration(true);
      setGenerationStatus('loading');

      // First, try to load existing personas from database
      if (auditContext.auditId) {
        try {
          const existingPersonas = await getPersonasByAudit(auditContext.auditId);
          if (existingPersonas.success && existingPersonas.personas.length > 0) {
            console.log('📋 Found existing personas in database:', existingPersonas.personas.length);
            const frontendPersonas = existingPersonas.personas.map(convertToFrontendPersona);
            setPersonas(frontendPersonas);
            setGenerationStatus('success');
            return;
          }
        } catch (error) {
          console.warn('⚠️ Could not load existing personas, proceeding with generation');
        }
      }

      // If no existing personas, generate new ones
      await handleGeneratePersonas();
    };

    generatePersonasAutomatically();
  }, [auditContext, hasAttemptedGeneration, personas.length]);

  const handleGeneratePersonas = async () => {
    if (!auditContext?.brandName || !auditContext?.brandDomain || !auditContext?.selectedProduct) {
      setGenerationStatus('error');
      return;
    }

    if (!auditContext?.brandId || !auditContext?.selectedProductId) {
      setGenerationStatus('error');
      return;
    }

    if (topics.length === 0) {
      setGenerationStatus('error');
      return;
    }

    setIsGenerating(true);
    setGenerationStatus('loading');

    try {
      const request: PersonaGenerateRequest = {
        brandName: auditContext.brandName,
        brandDescription: auditContext.brandDescription || `${auditContext.brandName} brand analysis`,
        brandDomain: auditContext.brandDomain,
        productName: auditContext.selectedProduct,
        brandId: auditContext.brandId,
        productId: auditContext.selectedProductId,
        topics: topics.map(t => t.name),
        auditId: auditContext.auditId || undefined,
        additionalContext: `Analysis for ${auditContext.brandName} focusing on ${auditContext.selectedProduct}`
      };

      console.log('🚀 Generating personas with request:', request);

      const response = await generatePersonas(request);

      if (response.success && response.personas.length > 0) {
        const frontendPersonas = response.personas.map(convertToFrontendPersona);
        setPersonas(frontendPersonas);
        setGenerationStatus('success');

        // Automatically store personas in database if audit ID exists
        if (auditContext.auditId) {
          try {
            await storePersonas({
              auditId: auditContext.auditId,
              brandId: auditContext.brandId || undefined,
              personas: response.personas
            });
            console.log('✅ Personas automatically stored in database');
          } catch (storeError) {
            console.warn('⚠️ Failed to store personas automatically:', storeError);
            // Don't show error to user since personas are still generated
          }
        }

        console.log('✅ Personas generated and set:', frontendPersonas.length);
      } else {
        throw new Error(response.reason || 'Failed to generate personas');
      }

    } catch (error) {
      console.error('❌ Error generating personas:', error);
      setGenerationStatus('error');
      
    } finally {
      setIsGenerating(false);
    }
  };

  // Show loading state
  if (generationStatus === 'loading' || isGenerating) {
    return (
      <div className="space-y-6">
        <PersonasHeader />
        
        <div className="flex items-center justify-center space-x-3 p-8 bg-card-dark rounded-lg border border-black/20">
          <RefreshCw className="h-6 w-6 animate-spin text-brand-purple" />
          <span className="text-lg text-text-secondary">
            Creating customer personas...
          </span>
        </div>
      </div>
    );
  }

  // Show error state  
  if (generationStatus === 'error') {
    return (
      <div className="space-y-6">
        <PersonasHeader />
        
        <div className="flex items-center justify-center space-x-3 p-8 bg-card-dark rounded-lg border border-red-500/20">
          <AlertCircle className="h-6 w-6 text-red-500" />
          <span className="text-lg text-red-400">
            Unable to create personas. Please try again later.
          </span>
        </div>
      </div>
    );
  }

  // Show personas when ready
  if (personas.length > 0) {
    return (
      <div className="space-y-6">
        <PersonasHeader />
        
        <ReadOnlyPersonaList
          personas={personas}
          topics={topics}
          products={products}
        />
      </div>
    );
  }

  // Default state
  return (
    <div className="space-y-6">
      <PersonasHeader />
      
      <div className="flex items-center justify-center space-x-3 p-8 bg-card-dark rounded-lg border border-black/20">
        <Sparkles className="h-6 w-6 text-brand-purple" />
        <span className="text-lg text-text-secondary">
          Complete previous steps to create personas
        </span>
      </div>
    </div>
  );
};
