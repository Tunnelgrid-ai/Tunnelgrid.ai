/**
 * TOPICS STEP - AI-POWERED CATEGORIZED TOPICS GENERATION WITH DATABASE PERSISTENCE
 * 
 * PURPOSE: Generate categorized AI-powered topics for brand analysis
 * FEATURES:
 * - Categorized topics: 4 unbranded, 3 branded, 3 comparative
 * - Database persistence for topics (load existing or store new)
 * - Edit topics in-place with optimistic updates
 * - Visual explanation of topic categories and structure
 * 
 * WORKFLOW:
 * 1. Component loads → Check for existing topics in database
 * 2. If found → Load existing topics and categorize them
 * 3. If not found → Generate new categorized topics via AI and store in database
 * 4. User can edit topics inline with real-time database updates
 * 5. Topics are passed to wizard state for use in next steps
 */

import { useState, useEffect, useRef } from "react";
import { Topic, Product } from "@/types/brandTypes";
import { TopicsExplanationSection } from "./topics/TopicsExplanationSection";
import { TopicsAccordionSection } from "./topics/TopicsAccordionSection";
import { Accordion } from "@/components/ui/accordion";
import { Loader2, AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";

// Services for AI generation and database storage
import { generateTopics } from "@/services/groqService";
import { 
  storeTopics,
  getTopicsForAudit,
  updateTopicRequest,
  checkTopicsExist,
  UpdateTopicRequest
} from "@/services/topicsService";

interface TopicsStepProps {
  topics: Topic[];
  setTopics: (topics: Topic[]) => void;
  products: Product[];
  auditContext?: {
    auditId: string | null;
    brandId: string | null;
    brandName: string;
    brandDomain: string;
    selectedProduct: string | null;
    selectedProductId: string | null;
  };
}

export const TopicsStep: React.FC<TopicsStepProps> = ({ 
  topics, 
  setTopics, 
  products, 
  auditContext 
}) => {
  // 🔍 DEBUG: Log component props on every render
  console.log('🔍 TopicsStep Component Debug:', {
    topicsCount: topics.length,
    topics: topics,
    hasAuditContext: !!auditContext,
    auditId: auditContext?.auditId,
    brandName: auditContext?.brandName,
    selectedProduct: auditContext?.selectedProduct,
    auditContext: auditContext
  });

  // STATE: Loading and process tracking
  const [isGenerating, setIsGenerating] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  
  // STATE: Error and status management
  const [error, setError] = useState<string | null>(null);
  const [generationSource, setGenerationSource] = useState<'ai' | 'fallback' | null>(null);
  const [hasExistingTopics, setHasExistingTopics] = useState(false);
  
  // REF: Container ref for scroll management
  const containerRef = useRef<HTMLDivElement>(null);

  // Initialize topics on component load
  useEffect(() => {
    const initializeTopics = async () => {
      if (!auditContext?.auditId) {
        console.warn('⚠️ No auditId provided, skipping topics initialization');
        return;
      }

      if (topics.length > 0) {
        console.log('✅ Topics already exist in state, skipping initialization');
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        // STEP 2: Check if topics already exist
        console.log('🔍 Checking for existing topics for audit:', auditContext.auditId);
        
        const existCheck = await checkTopicsExist(auditContext.auditId);
        
        if (!existCheck.success) {
          throw new Error(existCheck.error || 'Failed to check existing topics');
        }

        if (existCheck.data?.exists) {
          // STEP 3: Load existing topics from database
          console.log('📖 Loading existing topics from database');
          setHasExistingTopics(true);
          
          const existingTopics = await getTopicsForAudit(auditContext.auditId);
          
          if (existingTopics.success && existingTopics.data) {
            setTopics(existingTopics.data);
            console.log(`✅ Loaded ${existingTopics.data.length} existing topics`);
          } else {
            throw new Error(existingTopics.error || 'Failed to load existing topics');
          }
        } else {
          // STEP 4: Generate new topics via AI
          await generateAndStoreTopics();
        }

      } catch (error) {
        console.error('💥 Error initializing topics:', error);
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    initializeTopics();
  }, [auditContext?.auditId]);

  // Ensure page stays at top when component loads or finishes loading
  useEffect(() => {
    // Force scroll to top with multiple methods
    const scrollToTop = () => {
      if (containerRef.current) {
        containerRef.current.scrollIntoView({ 
          behavior: 'instant', 
          block: 'start' 
        });
      }
      // Also scroll window to top
      window.scrollTo({ top: 0, behavior: 'instant' });
      // Force document scroll
      document.documentElement.scrollTop = 0;
      document.body.scrollTop = 0;
    };
    
    scrollToTop();
    
    // Also run after a brief delay to catch any async rendering
    const timeoutId = setTimeout(scrollToTop, 100);
    
    return () => clearTimeout(timeoutId);
  }, [isLoading, topics.length]);

  /**
   * FUNCTION: Generate and Store New Categorized Topics
   * 
   * PURPOSE: AI-powered topics generation with database storage
   * ENSURES: Proper category distribution (4 unbranded, 3 branded, 3 comparative)
   */
  const generateAndStoreTopics = async () => {
    if (!auditContext?.auditId || !auditContext.brandName || !auditContext.selectedProduct) {
      throw new Error('Missing required context for topics generation');
    }

    setIsGenerating(true);
    
    try {
      console.log('🤖 Generating categorized topics with AI for:', {
        brandName: auditContext.brandName,
        brandDomain: auditContext.brandDomain,
        productName: auditContext.selectedProduct
      });
      
      // STEP 2: Generate topics using GroqCloud
      const generatedTopics = await generateTopics(
        auditContext.brandName,
        auditContext.brandDomain,
        auditContext.selectedProduct
      );
      
      setGenerationSource('ai');
      console.log(`✅ Generated ${generatedTopics.length} categorized topics via AI`);
      
      // STEP 3: Store topics in database
      console.log('💾 Storing categorized topics in database...');
      
      const storeResult = await storeTopics({
        auditId: auditContext.auditId,
        topics: generatedTopics,
        source: 'ai',
        replaceExisting: false
      });
      
      if (!storeResult.success || !storeResult.data) {
        throw new Error(storeResult.error || 'Failed to store topics');
      }
      
      // STEP 4: Update wizard state with stored topics
      setTopics(storeResult.data);
      
      console.log(`⏱️ Categorized topics generation completed successfully`);

    } catch (error) {
      console.error('💥 Error generating/storing categorized topics:', error);
      throw error;
    } finally {
      setIsGenerating(false);
    }
  };

  /**
   * FUNCTION: Handle Topic Editing
   * 
   * PURPOSE: Update topic in database and local state
   */
  const handleEditTopic = async (topicId: string, updates: Partial<Topic>) => {
    if (!auditContext?.auditId) return;

    setIsSaving(true);
    
    try {
      // Find the topic to get current category
      const currentTopic = topics.find(t => t.id === topicId);
      if (!currentTopic) {
        throw new Error('Topic not found');
      }

      const updateRequest: UpdateTopicRequest = {
        auditId: auditContext.auditId,
        topicId: topicId,
        name: updates.name || currentTopic.name,
        description: updates.description || currentTopic.description || ''
      };

      const result = await updateTopicRequest(updateRequest);
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to update topic');
      }

      // Update local state
      const updatedTopics = topics.map(topic => 
        topic.id === topicId 
          ? { ...topic, ...updates, editedByUser: true }
          : topic
      );
      setTopics(updatedTopics);

      console.log(`✅ Updated topic: ${topicId}`);

    } catch (error) {
      console.error('💥 Error updating topic:', error);
      setError(error instanceof Error ? error.message : 'Failed to update topic');
    } finally {
      setIsSaving(false);
    }
  };

  // Group topics by category
  const groupedTopics = {
    unbranded: topics.filter(t => t.category === 'unbranded'),
    branded: topics.filter(t => t.category === 'branded'),
    comparative: topics.filter(t => t.category === 'comparative')
  };

  // Loading state
  if (isLoading) {
    return (
      <div ref={containerRef} className="space-y-8">
        {/* Show explanation section even during loading */}
        <TopicsExplanationSection />
        
        {/* Loading spinner below explanation */}
        <div className="flex flex-col items-center justify-center py-12 space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-accent" />
          <p className="text-sm text-muted-foreground">
            {isGenerating ? 'Generating categorized topics...' : 'Loading topics...'}
          </p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div ref={containerRef} className="space-y-4">
        <Alert className="border-red-500/20 bg-red-500/5">
          <AlertCircle className="h-4 w-4 text-red-400" />
          <AlertDescription className="text-sm">
            <strong className="text-red-400">Error loading topics:</strong> {error}
          </AlertDescription>
        </Alert>
        
        <div className="flex justify-center">
          <Button
            onClick={() => window.location.reload()}
            variant="outline"
            className="border-accent/20 text-accent hover:bg-accent/10"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="space-y-8">
      {/* Explanation Section */}
      <TopicsExplanationSection />
      
      {/* Topics Accordion - Only Unbranded expanded by default */}
      <Accordion 
        type="single" 
        collapsible 
        defaultValue="unbranded"
        className="w-full space-y-4"
      >
        {/* Unbranded Topics Section */}
        <TopicsAccordionSection 
          value="unbranded"
          title="Unbranded Topics"
          description="For monitoring whether AI mentions your brand in unprompted questions"
          topics={groupedTopics.unbranded}
          categoryColor="bg-slate-800/50 border-slate-700/50"
          onEditTopic={handleEditTopic}
        />
        
        {/* Branded Topics Section */}
        <TopicsAccordionSection 
          value="branded"
          title="Branded Topics" 
          description="For monitoring what AI says about your brand when directly prompted"
          topics={groupedTopics.branded}
          categoryColor="bg-slate-800/50 border-slate-700/50"
          onEditTopic={handleEditTopic}
        />
        
        {/* Comparative Topics Section */}
        <TopicsAccordionSection 
          value="comparative"
          title="Comparative Topics"
          description="For monitoring how AI portrays your brand compared to others"
          topics={groupedTopics.comparative}
          categoryColor="bg-slate-800/50 border-slate-700/50"
          onEditTopic={handleEditTopic}
        />
      </Accordion>
    </div>
  );
};
