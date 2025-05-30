/**
 * TOPICS STEP COMPONENT - SECURE BACKEND INTEGRATION
 * 
 * PURPOSE: Generate and manage consumer perception topics for brand analysis
 * 
 * FEATURES:
 * - AI-powered topics generation via secure backend
 * - Real-time editing with optimistic UI updates
 * - Auto-save functionality with error handling
 * - Source indicators (AI generated vs user edited vs existing)
 * - Regeneration capability with confirmation
 * - Loading states and comprehensive error handling
 * 
 * SECURITY BENEFITS:
 * - No API keys exposed in frontend
 * - All AI calls routed through secure backend
 * - Rate limiting handled server-side
 * 
 * ARCHITECTURE:
 * Component → Backend Service → FastAPI → GroqCloud → Database
 */

import React, { useState, useEffect, useRef } from 'react';
import { Topic } from '../../types/brandTypes';
import { generateTopics, checkBackendHealth } from '../../services/groqService';
import { saveTopics, getTopics, TopicWithMetadata } from '../../services/topicsService';
import { useToast } from '../../hooks/use-toast';

interface TopicsStepProps {
  auditId: string;
  brandName: string;
  brandDomain: string;
  productName: string;
  industry?: string;
  onComplete: (topics: Topic[]) => void;
}

interface EditingTopic extends TopicWithMetadata {
  isEditing?: boolean;
  pendingSave?: boolean;
}

/**
 * MAIN COMPONENT: TopicsStep with Backend Integration
 */
export default function TopicsStep({
  auditId,
  brandName,
  brandDomain,
  productName,
  industry,
  onComplete
}: TopicsStepProps) {
  // STATE MANAGEMENT
  const [topics, setTopics] = useState<EditingTopic[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [showRegenerateConfirm, setShowRegenerateConfirm] = useState(false);
  const [backendHealth, setBackendHealth] = useState<string>('checking');
  const [error, setError] = useState<string | null>(null);
  
  const { toast } = useToast();
  const saveTimeoutsRef = useRef<Map<string, NodeJS.Timeout>>(new Map());
  const mountedRef = useRef(true);

  // CLEANUP: Component unmount
  useEffect(() => {
    return () => {
      mountedRef.current = false;
      // Clear any pending save timeouts
      saveTimeoutsRef.current.forEach(timeout => clearTimeout(timeout));
      saveTimeoutsRef.current.clear();
    };
  }, []);

  // INITIALIZATION: Check backend health and load/generate topics
  useEffect(() => {
    initializeTopics();
  }, [auditId]);

  /**
   * INITIALIZATION FUNCTION: Backend Health Check + Topics Loading
   */
  const initializeTopics = async () => {
    if (!mountedRef.current) return;
    
    try {
      setLoading(true);
      setError(null);
      
      // STEP 1: Check backend health
      console.log('🔍 Checking backend health...');
      const health = await checkBackendHealth();
      
      if (!mountedRef.current) return;
      
      if (health) {
        setBackendHealth(health.services.groqapi === 'available' ? 'healthy' : 'degraded');
        console.log('✅ Backend health check passed:', health);
      } else {
        setBackendHealth('unhealthy');
        console.warn('⚠️ Backend health check failed');
      }

      // STEP 2: Try to load existing topics
      console.log('📥 Checking for existing topics...');
      const existingTopics = await getTopics(auditId);
      
      if (!mountedRef.current) return;

      if (existingTopics && existingTopics.length > 0) {
        // Use existing topics
        console.log(`✅ Found ${existingTopics.length} existing topics`);
        setTopics(existingTopics.map(topic => ({ ...topic, isEditing: false, pendingSave: false })));
        setLoading(false);
        return;
      }

      // STEP 3: Generate new topics if none exist
      console.log('🤖 No existing topics found, generating new ones...');
      await generateAndSaveTopics(false);

    } catch (error) {
      console.error('❌ Error initializing topics:', error);
      
      if (!mountedRef.current) return;
      
      setError('Failed to initialize topics. Please try again.');
      setBackendHealth('unhealthy');
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  };

  /**
   * CORE FUNCTION: Generate and Save Topics
   */
  const generateAndSaveTopics = async (isRegeneration = false) => {
    if (!mountedRef.current) return;
    
    try {
      if (isRegeneration) {
        setRegenerating(true);
      } else {
        setGenerating(true);
      }
      
      setError(null);

      // Call backend API for topics generation
      console.log('📡 Calling backend API for topics generation...');
      
      const generatedTopics = await generateTopics(
        brandName,
        brandDomain,
        productName,
        industry,
        undefined // additionalContext - could be added to props if needed
      );

      if (!mountedRef.current) return;

      if (!generatedTopics || generatedTopics.length === 0) {
        throw new Error('No topics were generated');
      }

      console.log(`✅ Generated ${generatedTopics.length} topics from backend`);

      // Save to database
      console.log('💾 Saving topics to database...');
      await saveTopics(auditId, generatedTopics);

      // Update state
      const topicsWithMetadata: EditingTopic[] = generatedTopics.map(topic => ({
        ...topic,
        editedByUser: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        isEditing: false,
        pendingSave: false
      }));

      setTopics(topicsWithMetadata);

      // Success feedback
      const sourceMessage = generatedTopics[0]?.id?.includes('fallback') 
        ? 'Generated fallback topics (AI temporarily unavailable)'
        : 'Generated AI-powered topics successfully';

    } catch (error) {
      console.error('❌ Error generating topics:', error);
      
      if (!mountedRef.current) return;
      
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setError(errorMessage);
    } finally {
      if (mountedRef.current) {
        setGenerating(false);
        setRegenerating(false);
        setShowRegenerateConfirm(false);
      }
    }
  };

  /**
   * HANDLER: Topic Name Change with Auto-save
   */
  const handleTopicNameChange = (topicId: string, newName: string) => {
    // Update state immediately (optimistic update)
    setTopics(prevTopics => 
      prevTopics.map(topic => 
        topic.id === topicId 
          ? { ...topic, name: newName, editedByUser: true, pendingSave: true }
          : topic
      )
    );

    // Clear existing timeout for this topic
    const existingTimeout = saveTimeoutsRef.current.get(topicId);
    if (existingTimeout) {
      clearTimeout(existingTimeout);
    }

    // Set new auto-save timeout
    const newTimeout = setTimeout(() => {
      autoSaveTopic(topicId, { name: newName });
    }, 1000); // 1 second debounce

    saveTimeoutsRef.current.set(topicId, newTimeout);
  };

  /**
   * HANDLER: Topic Description Change with Auto-save
   */
  const handleTopicDescriptionChange = (topicId: string, newDescription: string) => {
    // Update state immediately (optimistic update)
    setTopics(prevTopics => 
      prevTopics.map(topic => 
        topic.id === topicId 
          ? { ...topic, description: newDescription, editedByUser: true, pendingSave: true }
          : topic
      )
    );

    // Clear existing timeout for this topic
    const existingTimeout = saveTimeoutsRef.current.get(topicId);
    if (existingTimeout) {
      clearTimeout(existingTimeout);
    }

    // Set new auto-save timeout
    const newTimeout = setTimeout(() => {
      autoSaveTopic(topicId, { description: newDescription });
    }, 1000); // 1 second debounce

    saveTimeoutsRef.current.set(topicId, newTimeout);
  };

  /**
   * UTILITY: Auto-save Topic Changes
   */
  const autoSaveTopic = async (topicId: string, changes: Partial<Topic>) => {
    if (!mountedRef.current) return;
    
    try {
      // Get current topic data
      const currentTopic = topics.find(t => t.id === topicId);
      if (!currentTopic) return;

      // Prepare updated topic
      const updatedTopic = { ...currentTopic, ...changes };

      // Save to database
      await saveTopics(auditId, [updatedTopic]);

      // Update state to remove pending save indicator
      if (mountedRef.current) {
        setTopics(prevTopics => 
          prevTopics.map(topic => 
            topic.id === topicId 
              ? { ...topic, ...changes, pendingSave: false, updatedAt: new Date().toISOString() }
              : topic
          )
        );
      }

      console.log(`✅ Auto-saved topic: ${topicId}`);

    } catch (error) {
      console.error('❌ Auto-save failed:', error);
      
      if (mountedRef.current) {
        // Remove pending save indicator on error
        setTopics(prevTopics => 
          prevTopics.map(topic => 
            topic.id === topicId ? { ...topic, pendingSave: false } : topic
          )
        );
      }
    }
  };

  /**
   * HANDLER: Regenerate Topics with Confirmation
   */
  const handleRegenerate = () => {
    setShowRegenerateConfirm(true);
  };

  const confirmRegenerate = () => {
    generateAndSaveTopics(true);
  };

  /**
   * HANDLER: Continue to Next Step
   */
  const handleContinue = () => {
    // Clear any pending timeouts
    saveTimeoutsRef.current.forEach(timeout => clearTimeout(timeout));
    saveTimeoutsRef.current.clear();

    // Convert back to basic Topic format for the callback
    const basicTopics: Topic[] = topics.map(({ isEditing, pendingSave, editedByUser, createdAt, updatedAt, ...topic }) => topic);
    
    onComplete(basicTopics);
  };

  /**
   * UTILITY: Get Source Indicator
   */
  const getSourceIndicator = (topic: EditingTopic) => {
    if (topic.editedByUser) {
      return { text: 'Edited', color: 'text-blue-600 bg-blue-50', icon: '✏️' };
    } else if (topic.id.includes('fallback')) {
      return { text: 'Fallback', color: 'text-yellow-600 bg-yellow-50', icon: '🔄' };
    } else {
      return { text: 'AI Generated', color: 'text-green-600 bg-green-50', icon: '🤖' };
    }
  };

  /**
   * UTILITY: Get Backend Health Status
   */
  const getHealthStatus = () => {
    switch (backendHealth) {
      case 'healthy':
        return { text: 'AI Available', color: 'text-green-600', icon: '✅' };
      case 'degraded':
        return { text: 'AI Degraded', color: 'text-yellow-600', icon: '⚠️' };
      case 'unhealthy':
        return { text: 'AI Unavailable', color: 'text-red-600', icon: '❌' };
      default:
        return { text: 'Checking...', color: 'text-gray-600', icon: '🔍' };
    }
  };

  // LOADING STATE
  if (loading) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <div className="inline-flex items-center space-x-2 text-blue-600">
            <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            <span>Initializing topics...</span>
          </div>
        </div>
      </div>
    );
  }

  // ERROR STATE
  if (error && topics.length === 0) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <div className="text-red-600 mb-4">❌ {error}</div>
          <button
            onClick={initializeTopics}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const healthStatus = getHealthStatus();

  // MAIN RENDER
  return (
    <div className="space-y-6">
      {/* Header with Health Status */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900">Research Topics</h3>
          <p className="mt-1 text-sm text-gray-600">
            AI-generated topics for analyzing consumer perception of {productName}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`text-sm ${healthStatus.color}`}>
            {healthStatus.icon} {healthStatus.text}
          </span>
        </div>
      </div>

      {/* Topics List */}
      <div className="space-y-4">
        {topics.map((topic, index) => {
          const source = getSourceIndicator(topic);
          
          return (
            <div key={topic.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-gray-500">Topic {index + 1}</span>
                  <span className={`px-2 py-1 text-xs rounded-full ${source.color}`}>
                    {source.icon} {source.text}
                  </span>
                  {topic.pendingSave && (
                    <span className="text-xs text-blue-600">Saving...</span>
                  )}
                </div>
              </div>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Topic Name
                  </label>
                  <input
                    type="text"
                    value={topic.name}
                    onChange={(e) => handleTopicNameChange(topic.id, e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter topic name..."
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={topic.description}
                    onChange={(e) => handleTopicDescriptionChange(topic.id, e.target.value)}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Describe what this topic covers..."
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between pt-4">
        <button
          onClick={handleRegenerate}
          disabled={generating || regenerating}
          className="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
        >
          {regenerating ? (
            <span className="flex items-center space-x-2">
              <div className="w-4 h-4 border-2 border-gray-600 border-t-transparent rounded-full animate-spin"></div>
              <span>Regenerating...</span>
            </span>
          ) : (
            '🔄 Regenerate Topics'
          )}
        </button>

        <button
          onClick={handleContinue}
          disabled={generating || regenerating || topics.some(t => t.pendingSave)}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Continue
        </button>
      </div>

      {/* Regeneration Confirmation Modal */}
      {showRegenerateConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Regenerate Topics?
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              This will replace all current topics with newly generated ones. Any edits you've made will be lost.
            </p>
            <div className="flex space-x-3">
              <button
                onClick={() => setShowRegenerateConfirm(false)}
                className="flex-1 px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmRegenerate}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Regenerate
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 