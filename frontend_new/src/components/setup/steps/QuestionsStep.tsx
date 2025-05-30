import { useState, useEffect } from "react";
import { Persona, Question, Topic, Product, BrandEntity } from "@/types/brandTypes";
import { useIsMobile } from "@/hooks/use-mobile";
import { QuestionsHeader } from "./questions/QuestionsHeader";
import { PersonaNavigation } from "./questions/PersonaNavigation";
import { QuestionsList } from "./questions/QuestionsList";
import { 
  generateAndStoreQuestions, 
  retryFailedPersonas,
  analyzeQuestionDistribution,
  type QuestionGenerateRequest 
} from "@/services/questionService";
import { Loader2, AlertTriangle, RefreshCw } from "lucide-react";

interface QuestionsStepProps {
  questions: Question[];
  setQuestions: (questions: Question[]) => void;
  personas: Persona[];
  topics: Topic[];
  brandInfo: BrandEntity;
  products: Product[];
  auditContext?: { 
    auditId: string; 
    brandId: string; 
    brandName: string;
    brandDescription: string;
    brandDomain: string;
    selectedProduct: string | null;
    selectedProductId: string | null;
  };
}

export const QuestionsStep = ({
  questions,
  setQuestions,
  personas,
  topics,
  brandInfo,
  products,
  auditContext,
}: QuestionsStepProps) => {
  const [selectedPersonaId, setSelectedPersonaId] = useState<string>(
    personas.length > 0 ? (personas[0].id as string) : ""
  );
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isRetrying, setIsRetrying] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [retryStatus, setRetryStatus] = useState<string | null>(null);
  
  const isMobile = useIsMobile();

  // 🔧 SYNC selectedPersonaId with available personas
  useEffect(() => {
    // If no personas are available, clear selection
    if (personas.length === 0) {
      setSelectedPersonaId("");
      return;
    }
    
    // If current selectedPersonaId is not in the personas array, reset to first persona
    const currentPersonaExists = personas.some(p => p.id === selectedPersonaId);
    if (!currentPersonaExists) {
      console.log(`🔄 selectedPersonaId '${selectedPersonaId}' not found in personas, resetting to first persona`);
      setSelectedPersonaId(personas[0].id as string);
    }
  }, [personas, selectedPersonaId]);

  // Auto-generate questions when component mounts and required data is available
  useEffect(() => {
    const shouldGenerateQuestions = 
      questions.length === 0 && 
      personas.length > 0 && 
      topics.length > 0 && 
      brandInfo.name && 
      brandInfo.website &&
      products.length > 0 &&
      auditContext?.auditId &&
      !isLoading;

    console.log("🔍 Questions generation check:", {
      questionsLength: questions.length,
      personasLength: personas.length,
      topicsLength: topics.length,
      brandName: brandInfo.name,
      brandWebsite: brandInfo.website,
      productsLength: products.length,
      auditId: auditContext?.auditId,
      isLoading,
      shouldGenerate: shouldGenerateQuestions
    });

    if (shouldGenerateQuestions) {
      console.log("✅ Triggering question generation...");
      generateQuestionsForPersonas();
    }
  }, [personas, topics, brandInfo, products, auditContext, questions.length, isLoading]);

  // 🆕 AUTO-RETRY FAILED PERSONAS after initial generation
  useEffect(() => {
    if (questions.length > 0 && personas.length > 0 && !isLoading && !isRetrying) {
      const distribution = analyzeQuestionDistribution(questions, personas);
      
      console.log("📊 Question Distribution Analysis:", distribution);
      
      if (distribution.needsRetry && distribution.failedPersonas.length > 0) {
        console.log(`🔄 Auto-retrying ${distribution.failedPersonas.length} failed personas:`, 
          distribution.failedPersonas.map(p => `${p.name} (${p.count} questions)`));
        
        setRetryStatus(`Retrying ${distribution.failedPersonas.length} personas with insufficient questions...`);
        retryFailedPersonasAutomatically();
      }
    }
  }, [questions, personas, isLoading, isRetrying]);

  const buildQuestionRequest = (): QuestionGenerateRequest | null => {
    if (!auditContext?.auditId) {
      setError("No audit context available for question generation");
      return null;
    }

    // Get the primary product
    const primaryProduct = products[0];
    if (!primaryProduct) {
      setError("No product available for question generation");
      return null;
    }

    return {
      auditId: auditContext.auditId,
      brandName: brandInfo.name || "",
      brandDescription: brandInfo.description || undefined,
      brandDomain: brandInfo.website || "",
      productName: primaryProduct.name || "",
      topics: topics.map(topic => ({
        id: topic.id as string,
        name: topic.name,
        description: topic.description,
      })),
      personas: personas.map(persona => ({
        id: persona.id as string,
        name: persona.name,
        description: persona.description,
        painPoints: persona.painPoints || [],
        motivators: persona.motivators || [],
        demographics: {
          ageRange: persona.demographics?.ageRange || "",
          gender: persona.demographics?.gender || "",
          location: persona.demographics?.location || "",
          goals: persona.demographics?.goals || [],
        },
      })),
    };
  };

  const generateQuestionsForPersonas = async () => {
    const request = buildQuestionRequest();
    if (!request) return;

    setIsLoading(true);
    setError(null);
    setRetryStatus(null);

    try {
      console.log("🚀 Starting question generation process...");
      console.log(`🌐 Generating questions for ${personas.length} personas and ${topics.length} topics...`);
      
      // Generate and store questions
      const { generateResponse, storeResponse } = await generateAndStoreQuestions(request);

      console.log("🎉 Initial API call completed successfully!");

      if (generateResponse.success) {
        console.log(`📊 Generated ${generateResponse.questions.length} questions`);
        setQuestions(generateResponse.questions);
        
        if (generateResponse.source === "fallback") {
          console.warn(`⚠️ Used fallback questions: ${generateResponse.reason}`);
        }

        if (!storeResponse.success) {
          console.warn("⚠️ Questions generated but storage failed:", storeResponse.message);
        }
      } else {
        throw new Error("Question generation failed");
      }

    } catch (err) {
      console.error("💥 Error in generateQuestionsForPersonas:", err);
      
      const errorMessage = err instanceof Error ? err.message : "Failed to generate questions";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const retryFailedPersonasAutomatically = async () => {
    const request = buildQuestionRequest();
    if (!request) return;

    setIsRetrying(true);
    setError(null);

    try {
      console.log("🔄 Starting automatic retry for failed personas...");
      
      const { generateResponse, storeResponse } = await retryFailedPersonas(request);

      console.log("🎉 Retry completed successfully!");

      if (generateResponse.success) {
        console.log(`📊 Total questions after retry: ${generateResponse.questions.length}`);
        setQuestions(generateResponse.questions);
        setRetryStatus(`✅ Retry completed: ${generateResponse.questions.length} total questions`);
        
        // Clear retry status after 3 seconds
        setTimeout(() => setRetryStatus(null), 3000);
      } else {
        throw new Error("Retry failed");
      }

    } catch (err) {
      console.error("💥 Error in retryFailedPersonasAutomatically:", err);
      
      const errorMessage = err instanceof Error ? err.message : "Failed to retry question generation";
      setRetryStatus(`❌ Retry failed: ${errorMessage}`);
      
      // Clear error status after 5 seconds
      setTimeout(() => setRetryStatus(null), 5000);
    } finally {
      setIsRetrying(false);
    }
  };

  // Group questions by persona
  const questionsByPersona: Record<string, Question[]> = {};
  personas.forEach(persona => {
    const personaQuestions = questions.filter(q => q.personaId === persona.id);
    questionsByPersona[persona.id] = personaQuestions.slice(0, 10);
  });

  // Calculate question distribution for UI feedback
  const distribution = questions.length > 0 && personas.length > 0 
    ? analyzeQuestionDistribution(questions, personas)
    : null;

  // Basic logging for verification
  console.log(`🎯 Questions distribution:`, Object.entries(questionsByPersona).map(([personaId, qs]) => ({
    personaName: personas.find(p => p.id === personaId)?.name || personaId,
    count: qs.length
  })));

  // Handle persona selection
  const handlePersonaSelect = (personaId: string) => {
    setSelectedPersonaId(personaId);
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-6">
        <QuestionsHeader />
        <div className="flex flex-col items-center justify-center py-12 space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-[#00FFC2]" />
          <div className="text-center">
            <h3 className="text-lg font-medium text-white">Generating Questions</h3>
            <p className="text-text-secondary mt-2">
              Our AI is creating personalized questions based on your brand, personas, and topics...
            </p>
            <p className="text-sm text-text-secondary mt-1">This may take up to a minute.</p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="space-y-6">
        <QuestionsHeader />
        <div className="flex flex-col items-center justify-center py-12 space-y-4">
          <AlertTriangle className="h-8 w-8 text-red-400" />
          <div className="text-center">
            <h3 className="text-lg font-medium text-red-400">Error Generating Questions</h3>
            <p className="text-text-secondary mt-2 max-w-md">
              {error}
            </p>
            <button
              onClick={generateQuestionsForPersonas}
              className="mt-4 px-4 py-2 bg-[#00FFC2] text-black rounded-lg hover:bg-[#00E5AC] transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  // No data state
  if (personas.length === 0) {
    return (
      <div className="space-y-6">
        <QuestionsHeader />
        <div className="flex flex-col items-center justify-center py-12 space-y-4">
          <div className="text-center">
            <h3 className="text-lg font-medium text-white">No Personas Available</h3>
            <p className="text-text-secondary mt-2">
              Please go back and generate personas before creating questions.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <QuestionsHeader />

      {/* 🆕 RETRY STATUS INDICATOR */}
      {(isRetrying || retryStatus) && (
        <div className="bg-blue-900/20 border border-blue-500 rounded-lg p-3">
          <div className="flex items-center space-x-2">
            {isRetrying ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin text-blue-400" />
                <span className="text-blue-400 text-sm">{retryStatus || "Retrying failed personas..."}</span>
              </>
            ) : (
              <span className="text-blue-400 text-sm">{retryStatus}</span>
            )}
          </div>
        </div>
      )}

      {/* 🆕 QUESTION DISTRIBUTION SUMMARY */}
      {distribution && (
        <div className="bg-card-dark border border-black/20 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-white font-medium">
                Total Questions: {distribution.totalQuestions}
              </span>
              <span className="text-text-secondary text-sm ml-2">
                across {personas.length} personas
              </span>
            </div>
            {distribution.failedPersonas.length > 0 && !isRetrying && (
              <div className="flex items-center space-x-2">
                <AlertTriangle className="h-4 w-4 text-yellow-400" />
                <span className="text-yellow-400 text-sm">
                  {distribution.failedPersonas.length} personas need more questions
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      <div className={`flex ${isMobile ? 'flex-col' : 'flex-row'} gap-4`}>
        {/* Persona navigation */}
        <PersonaNavigation
          personas={personas}
          selectedPersonaId={selectedPersonaId}
          onPersonaSelect={handlePersonaSelect}
          isMobile={isMobile}
        />

        {/* Questions list */}
        <div className={`${isMobile ? 'w-full' : 'w-3/4'}`}>
          <QuestionsList 
            selectedPersonaId={selectedPersonaId}
            personas={personas}
            questionsByPersona={questionsByPersona}
          />
        </div>
      </div>
    </div>
  );
};
