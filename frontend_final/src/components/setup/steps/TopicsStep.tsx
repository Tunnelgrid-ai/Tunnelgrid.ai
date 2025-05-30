/**
 * TOPICS STEP - AI-POWERED TOPICS GENERATION WITH DATABASE PERSISTENCE
 * 
 * PURPOSE: Generate AI-powered topics for brand analysis using GroqCloud
 * FEATURES:
 * - Automatic topics generation on component load
 * - Database persistence for topics (load existing or store new)
 * - Edit topics in-place with optimistic updates
 * - Integration with BrandSetupWizard state management
 * 
 * WORKFLOW:
 * 1. Component loads → Check for existing topics in database
 * 2. If found → Load existing topics
 * 3. If not found → Generate new topics via AI and store in database
 * 4. User can edit topics inline with real-time database updates
 * 5. Topics are passed to wizard state for use in next steps
 */

import { useState, useEffect } from "react";
import { Topic, Product } from "@/types/brandTypes";
import { TopicsHeader } from "./topics/TopicsHeader";
import { TopicsGrid } from "./topics/TopicsGrid";
import { Loader2, AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";

// NEW IMPORTS: Services for AI generation and database storage
import { generateTopics } from "@/services/groqService";
import { 
  storeTopics,
  getTopicsForAudit,
  updateTopicRequest,
  checkTopicsExist,
  UpdateTopicRequest
} from "@/services/topicsService";

/**
 * INTERFACE: Enhanced TopicsStep Props
 * 
 * NEW ADDITION: auditContext for database operations
 * Contains all audit-related information from wizard state
 */
interface TopicsStepProps {
  topics: Topic[];
  setTopics: (topics: Topic[]) => void;
  products: Product[];
  // NEW: Audit context for database operations
  auditContext?: {
    auditId: string | null;
    brandId: string | null;
    brandName: string;
    brandDomain: string;
    selectedProduct: string | null;
    selectedProductId: string | null;
  };
}

/**
 * COMPONENT: Enhanced TopicsStep
 * 
 * FEATURES:
 * - Automatic topics generation on first load
 * - Database persistence with audit linkage
 * - Real-time editing with auto-save
 * - Loading states and error handling
 * - Source indicators (AI vs user-edited)
 */
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
  
  const [editingId, setEditingId] = useState<string | null>(null);
  const [newTopic, setNewTopic] = useState({ name: '', reason: '' });
  const [showAddForm, setShowAddForm] = useState(false);

  // 🔍 DEBUG: Log key information on every render
  console.log('🔍 TopicsStep Debug:', {
    topicsCount: topics.length,
    hasAuditContext: !!auditContext,
    auditId: auditContext?.auditId,
    brandName: auditContext?.brandName,
    selectedProduct: auditContext?.selectedProduct,
    topics: topics
  });

  /**
   * EFFECT: Initialize Topics on Component Load
   * 
   * WORKFLOW:
   * 1. Check if audit context is available
   * 2. Check if topics already exist in database
   * 3. If exist → load from database
   * 4. If not exist → generate new topics via AI
   * 5. Store generated topics in database
   * 6. Update wizard state with topics
   */
  useEffect(() => {
    const initializeTopics = async () => {
      console.log('🔍 useEffect initializeTopics called with auditContext:', auditContext);
      console.log('🔍 Current topics state:', topics);
      
      // STEP 1: Validate audit context
      if (!auditContext?.auditId) {
        console.warn('⚠️ No audit ID available for topics generation');
        console.log('🔍 auditContext details:', auditContext);
        setError('Audit information missing. Please complete the previous step.');
        return;
      }
      if (!auditContext.brandName || !auditContext.selectedProduct) {
        console.warn('⚠️ Missing brand or product information');
        console.log('🔍 brandName:', auditContext.brandName, 'selectedProduct:', auditContext.selectedProduct);
        setError('Brand and product information required for topics generation.');
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
  }, [auditContext?.auditId]); // Re-run if audit ID changes

  /**
   * FUNCTION: Generate and Store New Topics
   * 
   * PURPOSE: AI-powered topics generation with database storage
   * 
   * WORKFLOW:
   * 1. Prepare generation request with brand/product context
   * 2. Call GroqCloud API for AI topic generation
   * 3. Store generated topics in Supabase database
   * 4. Update wizard state with new topics
   * 5. Show success/error feedback to user
   */
  const generateAndStoreTopics = async () => {
    if (!auditContext?.auditId || !auditContext.brandName || !auditContext.selectedProduct) {
      throw new Error('Missing required context for topics generation');
    }

    setIsGenerating(true);
    
    try {
      console.log('🤖 Generating topics with AI for:', {
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
      
      setGenerationSource('ai'); // groqService returns topics directly now
      console.log(`✅ Generated ${generatedTopics.length} topics via AI`);
      
      // STEP 3: Store topics in database
      console.log('💾 Storing topics in database...');
      
      const storeResult = await storeTopics({
        auditId: auditContext.auditId,
        topics: generatedTopics,
        source: 'ai', // Topics came from AI
        replaceExisting: false
      });
      
      if (!storeResult.success || !storeResult.data) {
        throw new Error(storeResult.error || 'Failed to store topics');
      }
      
      // STEP 4: Update wizard state with stored topics
      setTopics(storeResult.data);
      
      console.log(`⏱️ Generation completed successfully`);

    } catch (error) {
      console.error('💥 Error generating/storing topics:', error);
      throw error; // Re-throw to be handled by calling function
    } finally {
      setIsGenerating(false);
    }
  };

  /**
   * FUNCTION: Update Topic
   * 
   * PURPOSE: Handle topic editing with database persistence
   * 
   * WORKFLOW:
   * 1. Optimistically update UI immediately
   * 2. Send update to database
   * 3. Update with server response (includes timestamps)
   * 4. If error → rollback optimistic update + show error
   * 5. If success → keep optimistic update
   */
  const handleUpdateTopic = async (updatedTopic: Topic) => {
    if (!auditContext?.auditId) {
      return;
    }

    // STEP 1: Optimistic update (immediate UI feedback)
    const previousTopics = [...topics];
    const optimisticTopics = topics.map(topic => 
      topic.id === updatedTopic.id ? updatedTopic : topic
    );
    setTopics(optimisticTopics);

    try {
      setIsSaving(true);

      // STEP 2: Determine what fields changed
      const originalTopic = previousTopics.find(t => t.id === updatedTopic.id);
      const updateRequest: UpdateTopicRequest = {
        topicId: updatedTopic.id,
        auditId: auditContext.auditId,
      };

      // Add changed fields to update request
      if (originalTopic?.name !== updatedTopic.name) {
        updateRequest.name = updatedTopic.name;
      }
      if (originalTopic?.description !== updatedTopic.description) {
        updateRequest.description = updatedTopic.description;
      }

      // Skip database call if nothing actually changed
      if (!updateRequest.name && !updateRequest.description) {
        console.log('📝 No changes detected, skipping database update');
        setIsSaving(false);
        return;
      }

      // STEP 3: Save to database
      const updateResult = await updateTopicRequest(updateRequest);
      
      if (!updateResult.success) {
        throw new Error(updateResult.error || 'Failed to update topic');
      }

      // STEP 4: Update with server response (includes timestamps)
      if (updateResult.data) {
        const finalTopics = topics.map(topic => 
          topic.id === updatedTopic.id ? updateResult.data! : topic
        );
        setTopics(finalTopics);
      }

      console.log('✅ Topic updated successfully:', updatedTopic.name);

    } catch (error) {
      // STEP 5: Rollback on error
      console.error('❌ Failed to update topic:', error);
      setTopics(previousTopics); // Revert optimistic update
      
    } finally {
      setIsSaving(false);
    }
  };

  // RENDER: Loading state
  if (isLoading) {
    return (
      <div className="space-y-8 animate-fade-in">
        <TopicsHeader />
        <div className="flex items-center justify-center py-12">
          <div className="text-center space-y-4">
            <Loader2 className="h-8 w-8 animate-spin mx-auto text-brand-purple" />
            <div className="space-y-2">
              <p className="text-lg font-medium">Loading Topics...</p>
              <p className="text-sm text-text-secondary">
                {hasExistingTopics ? 'Retrieving your saved topics' : 'Generating topics for your analysis'}
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // RENDER: Error state
  if (error) {
    return (
      <div className="space-y-8 animate-fade-in">
        <TopicsHeader />
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error}
          </AlertDescription>
        </Alert>
        <div className="flex justify-center">
          <Button 
            onClick={() => window.location.reload()} 
            variant="outline"
            className="flex items-center gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  // RENDER: Main topics interface
  return (
    <div className="space-y-8 animate-fade-in">
      <TopicsHeader />
      
      {/* Topics Grid */}
      <TopicsGrid 
        topics={topics} 
        onUpdateTopic={handleUpdateTopic}
      />
      
      {/* Simple Instructions */}
      <div className="text-center text-sm text-text-secondary">
        <p>Click any topic to edit it</p>
      </div>
    </div>
  );
};
