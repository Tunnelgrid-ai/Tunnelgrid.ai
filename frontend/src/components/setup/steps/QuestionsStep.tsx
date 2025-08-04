import { useState, useEffect, useMemo } from "react";
import { Persona, Question, Topic, Product, BrandEntity } from "@/types/brandTypes";
import { useIsMobile } from "@/hooks/use-mobile";
import { QuestionsHeader } from "./questions/QuestionsHeader";
import { PersonaRail } from "./questions/PersonaRail";
import { QuestionsTable } from "./questions/QuestionsTable";
import { 
  generateAndStoreQuestions, 
  retryFailedPersonas,
  analyzeQuestionDistribution,
  questionService,
  type QuestionGenerateRequest 
} from "@/services/questionService";
import { Loader2, AlertTriangle, RefreshCw } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";

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
  auditContext
}: QuestionsStepProps) => {
  const isMobile = useIsMobile();
  const [isGenerating, setIsGenerating] = useState(false);
  const [isRetrying, setIsRetrying] = useState(false);
  const [retryStatus, setRetryStatus] = useState<string | null>(null);
  const [selectedPersonaId, setSelectedPersonaId] = useState<string>(
    personas.length > 0 ? personas[0].id as string : ""
  );
  const [error, setError] = useState<string | null>(null);
  


  // Group questions by persona ID for easy lookup
  const questionsByPersona = useMemo(() => {
    return questions.reduce((acc, question) => {
      if (!acc[question.personaId]) {
        acc[question.personaId] = [];
      }
      acc[question.personaId].push(question);
      return acc;
    }, {} as Record<string, Question[]>);
  }, [questions]);

  // Get questions for selected persona (no filtering)
  const filteredQuestions = useMemo(() => {
    return questionsByPersona[selectedPersonaId] || [];
  }, [questionsByPersona, selectedPersonaId]);



  // Question update handler
  const handleQuestionUpdate = async (questionId: string, updates: Partial<Question>) => {
    try {
      // Update local state immediately for responsive UI
      const updatedQuestions = questions.map(q => 
        q.id === questionId ? { ...q, ...updates, editedByUser: true } : q
      );
      setQuestions(updatedQuestions);

      // Call backend API to persist changes
      const response = await questionService.updateQuestion(questionId, updates);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to update question');
      }
      
      console.log('✅ Question updated successfully:', questionId, updates);
      
    } catch (error) {
      console.error('❌ Failed to update question:', error);
      setError('Failed to update question. Please try again.');
      
      // Revert optimistic update on error
      setQuestions(questions);
    }
  };

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
      !isGenerating;

    if (shouldGenerateQuestions) {
      handleGenerateQuestions();
    }
  }, [personas, topics, brandInfo, products, auditContext]);

  // Sync selectedPersonaId with available personas
  useEffect(() => {
    if (personas.length === 0) {
      setSelectedPersonaId("");
      return;
    }
    
    const currentPersonaExists = personas.some(p => p.id === selectedPersonaId);
    if (!currentPersonaExists) {
      setSelectedPersonaId(personas[0].id as string);
    }
  }, [personas, selectedPersonaId]);

  const handleGenerateQuestions = async () => {
    if (!auditContext?.auditId || personas.length === 0 || topics.length === 0) {
      console.warn('⚠️ Missing required data for question generation');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      // Get the primary product
      const primaryProduct = products[0];
      if (!primaryProduct) {
        setError("No product available for question generation");
        return;
      }

      const generateRequest: QuestionGenerateRequest = {
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

      console.log('🚀 Generating questions for all personas...');
      const { generateResponse, storeResponse } = await generateAndStoreQuestions(generateRequest);
      
      console.log("🎉 Initial API call completed successfully!");

      if (generateResponse.success) {
        console.log(`📊 Generated ${generateResponse.questions.length} questions`);
        
        // Transform questions to include required fields
        const transformedQuestions = generateResponse.questions.map(q => ({
          ...q,
          topicId: q.topicId || getTopicIdForQuestion(q, topics),
          topicName: q.topicName || getTopicNameForQuestion(q, topics),
          topicType: getTopicTypeForQuestion(q, topics)
        }));
        
        setQuestions(transformedQuestions);
        
        if (generateResponse.source === "fallback") {
          console.warn(`⚠️ Used fallback questions: ${generateResponse.reason}`);
        }

        if (!storeResponse.success) {
          console.warn("⚠️ Questions generated but storage failed:", storeResponse.message);
        }
        
        console.log('✅ Questions generated successfully');
      } else {
        throw new Error("Question generation failed");
      }
    } catch (error) {
      console.error('💥 Error generating questions:', error);
      setError(error instanceof Error ? error.message : 'Failed to generate questions');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRetryFailedPersonas = async () => {
    if (!auditContext?.auditId) return;

    setIsRetrying(true);
    setRetryStatus("Retrying failed personas...");

    try {
      // Get the primary product
      const primaryProduct = products[0];
      if (!primaryProduct) {
        setRetryStatus("❌ No product available for retry");
        setTimeout(() => setRetryStatus(null), 5000);
        return;
      }

      const generateRequest: QuestionGenerateRequest = {
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

      console.log("🔄 Starting automatic retry for failed personas...");
      
      const { generateResponse, storeResponse } = await retryFailedPersonas(generateRequest);
      
      console.log("🎉 Retry completed successfully!");

      if (generateResponse.success) {
        console.log(`📊 Total questions after retry: ${generateResponse.questions.length}`);
        
        const transformedQuestions = generateResponse.questions.map(q => ({
          ...q,
          topicId: q.topicId || getTopicIdForQuestion(q, topics),
          topicName: q.topicName || getTopicNameForQuestion(q, topics),
          topicType: getTopicTypeForQuestion(q, topics)
        }));
        
        setQuestions(transformedQuestions);
        setRetryStatus(`✅ Retry completed: ${generateResponse.questions.length} total questions`);
        
        // Clear retry status after 3 seconds
        setTimeout(() => setRetryStatus(null), 3000);
      } else {
        throw new Error("Retry failed");
      }
    } catch (error) {
      console.error('💥 Error retrying personas:', error);
      setRetryStatus(`❌ Retry failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setTimeout(() => setRetryStatus(null), 5000);
    } finally {
      setIsRetrying(false);
    }
  };

  // Helper functions
  const getTopicIdForQuestion = (question: Question, topics: Topic[]): string => {
    const topic = topics.find(t => t.name === question.topicName);
    return topic?.id || '';
  };

  const getTopicNameForQuestion = (question: Question, topics: Topic[]): string => {
    if (question.topicName) return question.topicName;
    const topic = topics.find(t => t.id === question.topicId);
    return topic?.name || 'Unknown Topic';
  };

  const getTopicTypeForQuestion = (question: Question, topics: Topic[]): 'unbranded' | 'branded' | 'comparative' => {
    // First try to find by topicId if it exists
    if (question.topicId) {
      const topic = topics.find(t => t.id === question.topicId);
      if (topic) return topic.category;
    }
    
    // Fall back to topicName
    if (question.topicName) {
      const topic = topics.find(t => t.name === question.topicName);
      if (topic) return topic.category;
    }
    
    // Default fallback
    return 'unbranded';
  };

  // Loading state
  if (isGenerating) {
    return (
      <div className="space-y-6">
        <QuestionsHeader />
        <div className="flex flex-col items-center justify-center py-12 space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-[#00FFC2]" />
          <div className="text-center">
            <h3 className="text-lg font-medium text-white">Generating Questions</h3>
            <p className="text-text-secondary mt-2">
              Creating personalized questions for each customer persona...
            </p>
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
        <Alert className="border-red-500/20 bg-red-500/5">
          <AlertTriangle className="h-4 w-4 text-red-400" />
          <AlertDescription className="text-sm">
            <p className="text-red-400 font-medium">Error: {error}</p>
            <Button 
              onClick={handleGenerateQuestions}
              className="mt-3 bg-red-500 hover:bg-red-600 text-white"
              size="sm"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Try Again
            </Button>
          </AlertDescription>
        </Alert>
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



      {/* Retry Status Indicator */}
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

      {/* Main Layout - Vertical Stack */}
      <div className="space-y-6">
        {/* Persona Grid - Top */}
        <PersonaRail
          personas={personas}
          selectedPersonaId={selectedPersonaId}
          onPersonaSelect={setSelectedPersonaId}
          questionsByPersona={questionsByPersona}
        />



        {/* Questions Table */}
        <QuestionsTable
          questions={filteredQuestions}
          topics={topics}
          onQuestionUpdate={handleQuestionUpdate}
          isMobile={isMobile}
        />

        {/* Retry Button for incomplete personas */}
        {questionsByPersona && Object.keys(questionsByPersona).length < personas.length && (
          <div className="flex justify-center pt-4">
            <Button
              onClick={handleRetryFailedPersonas}
              disabled={isRetrying}
              className="bg-yellow-600 hover:bg-yellow-700 text-white"
            >
              {isRetrying ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Retrying...
                </>
              ) : (
                <>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Retry Failed Personas
                </>
              )}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};