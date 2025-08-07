/**
 * WIZARD STATE HOOK - UPDATED WITH AUDIT ID MANAGEMENT
 * 
 * PURPOSE: Manages all state for the brand setup wizard, including audit tracking
 * 
 * NEW FUNCTIONALITY: 
 * - Stores audit ID when audit is created in BrandInfoStep
 * - Passes audit ID to other steps for topics/personas/questions generation
 * - Tracks audit status throughout the wizard process
 */

import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { BrandEntity, Product, Topic, Persona, Question } from "@/types/brandTypes";
import { STEPS, SetupStep } from "../constants/wizardSteps";
import { v4 as uuidv4 } from 'uuid';

// Add study management imports and functionality
import { 
  studyService, 
  Study, 
  StudyStep, 
  StudyStatus,
  saveProgress,
  getProgress 
} from '@/services/studyService';

export const useWizardState = () => {
  const location = useLocation();
  const [currentStep, setCurrentStep] = useState<SetupStep>("brand-info");
  const [brandInfo, setBrandInfo] = useState<BrandEntity>({
    name: "",
    aliases: [],
    website: "",
    socialLinks: [],
  });
  const [products, setProducts] = useState<Product[]>([]); // Selected products for wizard state
  const [availableProducts, setAvailableProducts] = useState<Product[]>([]); // All products from API for display
  const [topics, setTopics] = useState<Topic[]>([]);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [questions, setQuestions] = useState<Question[]>([]);
  
  /**
   * NEW STATE: Audit ID Management
   * 
   * PURPOSE: Track the audit created in BrandInfoStep throughout the wizard
   * 
   * WHY WE NEED THIS:
   * - Topics generation requires audit_id for database storage
   * - Personas generation links to the specific audit
   * - Questions generation also needs the audit context
   * - Final submission updates audit status to 'completed'
   * 
   * FLOW:
   * 1. BrandInfoStep creates audit → sets auditId
   * 2. TopicsStep uses auditId for topics generation/storage
   * 3. PersonasStep uses auditId for personas generation
   * 4. QuestionsStep uses auditId for questions generation
   * 5. Review/Submit updates audit status to 'completed'
   */
  const [auditId, setAuditId] = useState<string | null>(null);
  
  /**
   * NEW STATE: Brand ID from Search
   * 
   * PURPOSE: Store brand ID from the search step for audit creation
   * 
   * WHY: BrandInfoStep needs brand_id to create audit entries
   * WHEN: Set when user navigates from search page with selected brand
   */
  const [brandId, setBrandId] = useState<string | null>(null);
  
  // Analysis loading state
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisJobId, setAnalysisJobId] = useState<string>('');
  const [analysisProgress, setAnalysisProgress] = useState(0);
  
  // Persist analysis state to prevent disappearing on re-renders
  useEffect(() => {
    const savedJobId = sessionStorage.getItem('analysisJobId');
    const savedLoading = sessionStorage.getItem('analysisLoading');
    
    if (savedJobId && savedLoading === 'true') {
      setAnalysisJobId(savedJobId);
      setAnalysisLoading(true);
      console.log('🔄 Restored analysis state from session storage');
    }
  }, []);
  
  // Clear analysis state when starting a new brand setup or when no brand is selected
  useEffect(() => {
    if (location.state?.selectedBrand) {
      // Clear any existing analysis state when starting a new brand setup
      sessionStorage.removeItem('analysisLoading');
      sessionStorage.removeItem('analysisJobId');
      setAnalysisLoading(false);
      setAnalysisJobId('');
      console.log('🧹 Cleared previous analysis state for new brand setup');
    } else if (!location.state?.selectedBrand && !location.state?.manualSetup) {
      // Also clear analysis state when no brand is selected (prevents lingering state)
      sessionStorage.removeItem('analysisLoading');
      sessionStorage.removeItem('analysisJobId');
      setAnalysisLoading(false);
      setAnalysisJobId('');
      console.log('🧹 Cleared analysis state - no brand selected');
    }
  }, [location.state?.selectedBrand, location.state?.manualSetup]);
  
  // Save analysis state to session storage
  useEffect(() => {
    if (analysisLoading) {
      sessionStorage.setItem('analysisLoading', 'true');
      sessionStorage.setItem('analysisJobId', analysisJobId);
    } else {
      sessionStorage.removeItem('analysisLoading');
      sessionStorage.removeItem('analysisJobId');
    }
  }, [analysisLoading, analysisJobId]);

  // Add study state to the hook
  const [currentStudy, setCurrentStudy] = useState<Study | null>(null);
  const [studyId, setStudyId] = useState<string | null>(null);
  
  // Add study management functions
  const loadStudyProgress = async (studyId: string) => {
    try {
      const result = await getProgress(studyId);
      if (result.success && result.data) {
        // Restore wizard state from saved progress
        const stepData = result.data.step_data;
        
        // Restore brand info
        if (stepData.brandInfo) {
          setBrandInfo(stepData.brandInfo);
        }
        
        // Restore personas
        if (stepData.personas) {
          setPersonas(stepData.personas);
        }
        
        // Restore products
        if (stepData.products) {
          setProducts(stepData.products);
        }
        
        // Restore questions
        if (stepData.questions) {
          setQuestions(stepData.questions);
        }
        
        // Restore topics
        if (stepData.topics) {
          setTopics(stepData.topics);
        }
        
        console.log('✅ Study progress restored successfully');
      }
    } catch (error) {
      console.error('❌ Failed to load study progress:', error);
    }
  };

  const saveStudyProgress = async (stepName: StudyStep, stepData: any) => {
    if (!studyId) return;
    
    try {
      const progressPercentage = studyService.calculateProgressPercentage(stepName);
      
      const result = await saveProgress(studyId, {
        step_name: stepName,
        step_data: stepData,
        progress_percentage: progressPercentage
      });
      
      if (result.success) {
        console.log('✅ Study progress saved successfully');
      } else {
        console.error('❌ Failed to save study progress:', result.error);
      }
    } catch (error) {
      console.error('❌ Error saving study progress:', error);
    }
  };
  
  // Initialize brand information and products if available from navigation state
  useEffect(() => {
    if (location.state?.selectedBrand) {
      const { name, domain, brand_id } = location.state.selectedBrand;
      setBrandInfo({
        name,
        aliases: [],
        website: domain,
        socialLinks: [],
      });
      
      // NEW: Store brand ID for audit creation
      if (brand_id) {
        setBrandId(brand_id);
        console.log('📝 Brand ID stored for audit creation:', brand_id);
      }
    }

    // Initialize available products from API data if available
    if (location.state?.product && Array.isArray(location.state.product)) {
      const apiProducts: Product[] = location.state.product.map((productName: string, index: number) => ({
        id: uuidv4(), // Generate proper UUID instead of string ID
        name: productName,
        valueProps: []
      }));
      setAvailableProducts(apiProducts);
      // Don't set products here - let user select
      console.log('📝 Available products loaded:', apiProducts.length);
    }
  }, [location.state]);

  /**
   * NEW FUNCTION: Handle Audit Creation Success
   * 
   * PURPOSE: Called by BrandInfoStep when audit is successfully created
   * 
   * WHAT IT DOES:
   * 1. Stores the audit ID for use in subsequent steps
   * 2. Logs the audit creation for debugging
   * 3. Proceeds to next step (Topics)
   * 
   * @param createdAuditId - The ID of the newly created audit
   */
  const handleAuditCreated = (createdAuditId: string) => {
    console.log('🎉 Audit created successfully in wizard:', createdAuditId);
    setAuditId(createdAuditId);
    
    // Automatically proceed to Topics step
    nextStep();
  };

  /**
   * NEW FUNCTION: Get Audit Context
   * 
   * PURPOSE: Provides all audit-related information needed by other steps
   * 
   * RETURNS: Object with audit ID, brand ID, and related info for API calls
   * 
   * USED BY: TopicsStep, PersonasStep, QuestionsStep for generating content
   */
  const getAuditContext = () => {
    return {
      auditId,
      brandId,
      brandName: brandInfo.name,
      brandDescription: brandInfo.description || `${brandInfo.name} brand analysis`,
      brandDomain: brandInfo.website,
      selectedProduct: products[0]?.name || null,
      selectedProductId: products[0]?.id || null
    };
  };

  const getCurrentStepIndex = () => STEPS.indexOf(currentStep);
  
  const nextStep = () => {
    const currentIndex = getCurrentStepIndex();
    if (currentIndex < STEPS.length - 1) {
      setCurrentStep(STEPS[currentIndex + 1]);
    }
  };

  const prevStep = () => {
    const currentIndex = getCurrentStepIndex();
    if (currentIndex > 0) {
      setCurrentStep(STEPS[currentIndex - 1]);
    }
  };

  /**
   * UPDATED: Validation with Audit Context
   * 
   * Added audit ID validation for steps that require it
   */
  const validateCurrentStep = (): boolean => {
    switch (currentStep) {
      case "brand-info":
        if (!brandInfo.name || !brandInfo.website || products.length === 0) {
          console.log('❌ Missing brand information or products');
          return false;
        }
        // NEW: Don't require audit ID here since it gets created in this step
        return true;
        
      case "topics":
        // NEW: Require audit ID for topics step
        if (!auditId) {
          console.log('❌ Audit ID required for topics step');
          return false;
        }
        if (topics.length === 0) {
          console.log('❌ No topics selected');
          return false;
        }
        return true;
        
      case "personas":
        // NEW: Require audit ID for personas step
        if (!auditId) {
          console.log('❌ Audit ID required for personas step');
          return false;
        }
        // Remove validation for personas since this step is now read-only
        return true;
        
      case "questions":
        // NEW: Require audit ID for questions step
        if (!auditId) {
          console.log('❌ Audit ID required for questions step');
          return false;
        }
        if (questions.length === 0) {
          console.log('❌ No questions defined');
          return false;
        }
        return true;
        
      case "review":
        // NEW: Require audit ID for final review
        if (!auditId) {
          console.log('❌ Audit ID required for final review');
          return false;
        }
        return true;
    }
  };

  /**
   * UPDATED: Handle Next with Audit Awareness
   * 
   * Special handling for brand-info step where audit gets created
   */
  const handleNext = () => {
    // Special case: Don't validate brand-info step here since audit creation happens in component
    if (currentStep === "brand-info") {
      // BrandInfoStep component will handle audit creation and call handleAuditCreated
      console.log('⏳ Waiting for audit creation in BrandInfoStep...');
      // We'll need to expose a way for BrandInfoStep to trigger this
      return;
    }
    
    // For all other steps, use normal validation
    if (validateCurrentStep()) {
      nextStep();
    }
  };

  /**
   * NEW FUNCTION: Trigger Audit Creation
   * 
   * PURPOSE: Called by WizardNavigation when on brand-info step
   * This will be connected to BrandInfoStep's audit creation logic
   */
  const [triggerAuditCreation, setTriggerAuditCreation] = useState<(() => void) | null>(null);

  const handleNextWithAuditCheck = () => {
    if (currentStep === "brand-info" && triggerAuditCreation) {
      // Trigger audit creation in BrandInfoStep
      triggerAuditCreation();
    } else {
      // Normal next step flow
      handleNext();
    }
  };

  /**
   * UPDATED: Step Completion with Audit Context
   */
  const isComplete = (step: SetupStep): boolean => {
    switch (step) {
      case "brand-info":
        // Step is complete when audit has been created
        return !!brandInfo.name && !!brandInfo.website && products.length > 0 && !!auditId;
        
      case "topics":
        return topics.length > 0 && !!auditId;
        
      case "personas":
        // Always mark personas step as complete since it's read-only (if audit exists)
        return !!auditId;
        
      case "questions":
        return questions.length > 0 && !!auditId;
        
      case "review":
        return false; // Review is never "complete"
    }
  };

  /**
   * UPDATED: Submit Setup with Audit Completion AND AI Analysis
   * 
   * PURPOSE: Handle final wizard submission, mark audit as completed, and start AI analysis
   * 
   * WORKFLOW:
   * 1. Validate all required data is present
   * 2. Process final submission (existing logic)
   * 3. Mark audit as 'completed' in database
   * 4. Start AI analysis job
   * 5. Navigate to analysis loading screen
   */
  const submitSetup = async () => {
    try {
      // STEP 1: Validate we have an audit to complete
      if (!auditId) {
        console.error('❌ No audit ID available for completion');
        return;
      }

      // STEP 2: Validate required data
      if (!brandInfo || !products.length || !topics.length || !personas.length || !questions.length) {
        console.log('❌ Validation failed:', {
          brandInfo: !!brandInfo,
          products: products.length,
          topics: topics.length,
          personas: personas.length,
          questions: questions.length
        });
        return;
      }

      console.log('🚀 Submitting setup and completing audit:', auditId);

      // STEP 2.5: Create or update study if we have study management
      if (!studyId && brandId) {
        console.log('📝 Creating new study...');
        try {
          const { createStudy } = await import('@/services/studyService');
          const studyResult = await createStudy({
            brand_id: brandId, // Use the actual brand ID
            study_name: `${brandInfo.name} Brand Analysis`,
            study_description: `Brand analysis study for ${brandInfo.name}`
          });

          if (studyResult.success) {
            setStudyId(studyResult.data.study_id);
            console.log('✅ Study created successfully:', studyResult.data.study_id);
          } else {
            console.warn('⚠️ Failed to create study, continuing without study management:', studyResult.error);
          }
        } catch (error) {
          console.warn('⚠️ Error creating study, continuing without study management:', error);
        }
      } else if (!brandId) {
        console.log('⚠️ No brand ID available, skipping study creation');
      }

      // STEP 3: Mark setup as complete (ready for analysis)
      console.log('📝 Calling markSetupComplete...');
      const { markSetupComplete } = await import('@/services/auditService');
      const setupResult = await markSetupComplete(auditId);

      console.log('📋 Setup completion result:', setupResult);

      if (!setupResult.success) {
        console.error('❌ Setup completion failed:', setupResult.error);
        throw new Error(setupResult.error || 'Failed to mark setup as complete');
      }

      console.log('✅ Setup marked as complete, ready for analysis:', auditId);

      // STEP 4: Start AI analysis and show loading screen
      console.log('🤖 Starting AI analysis for audit:', auditId);
      
      // Import analysis service dynamically to avoid circular dependencies
      const { startAnalysisJob } = await import('@/services/analysisService');
      
      // Set loading state to show the loading screen immediately
      setAnalysisLoading(true);
      
      // Start the analysis job and get job ID immediately
      const analysisResult = await startAnalysisJob(auditId);
      
      if (analysisResult.success) {
        console.log('🎉 AI analysis job started successfully');
        setAnalysisJobId(analysisResult.data.job_id);
        // Keep loading screen active - it will handle completion via polling
      } else {
        console.error('❌ AI analysis failed:', 'Unknown error');
        setAnalysisLoading(false);
        throw new Error('Failed to start AI analysis');
      }

    } catch (error) {
      console.error('💥 Error completing setup:', error);
      
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      
      // Log error details for debugging
      if (errorMessage.includes('Database error')) {
        console.error('🗄️ Database connection issue');
      } else if (errorMessage.includes('not found')) {
        console.error('🔍 Audit record not found');
      } else if (errorMessage.includes('Failed to complete audit')) {
        console.error('❌ Unable to complete audit');
      }
    }
  };

  // Add study initialization
  const initializeStudy = async (studyId: string) => {
    setStudyId(studyId);
    await loadStudyProgress(studyId);
  };

  // Update existing setter functions to save progress
  const setBrandInfoWithProgress = (info: BrandEntity) => {
    setBrandInfo(info);
    if (studyId) {
      saveStudyProgress(StudyStep.BRAND_INFO, { brandInfo: info });
    }
  };

  const setPersonasWithProgress = (personas: Persona[]) => {
    setPersonas(personas);
    if (studyId) {
      saveStudyProgress(StudyStep.PERSONAS, { personas });
    }
  };

  const setProductsWithProgress = (products: Product[]) => {
    setProducts(products);
    if (studyId) {
      saveStudyProgress(StudyStep.PRODUCTS, { products });
    }
  };

  const setQuestionsWithProgress = (questions: Question[]) => {
    setQuestions(questions);
    if (studyId) {
      saveStudyProgress(StudyStep.QUESTIONS, { questions });
    }
  };

  const setTopicsWithProgress = (topics: Topic[]) => {
    setTopics(topics);
    if (studyId) {
      saveStudyProgress(StudyStep.TOPICS, { topics });
    }
  };

  // Return study management functions
  return {
    currentStep,
    setCurrentStep,
    brandInfo,
    setBrandInfo,
    setBrandInfoWithProgress, // NEW: Setter with progress saving
    products,
    setProducts,
    setProductsWithProgress, // NEW: Setter with progress saving
    availableProducts,
    topics,
    setTopics,
    setTopicsWithProgress, // NEW: Setter with progress saving
    personas,
    setPersonas,
    setPersonasWithProgress, // NEW: Setter with progress saving
    questions,
    setQuestions,
    setQuestionsWithProgress, // NEW: Setter with progress saving
    nextStep,
    prevStep,
    handleNext,
    isComplete,
    getCurrentStepIndex,
    submitSetup,
    // NEW: Audit-related functions and state
    auditId,
    setAuditId,
    brandId,
    setBrandId,
    handleAuditCreated,
    getAuditContext,
    // NEW: Trigger audit creation
    triggerAuditCreation,
    setTriggerAuditCreation,
    handleNextWithAuditCheck,
    // NEW: Analysis loading state
    analysisLoading,
    setAnalysisLoading,
    analysisJobId,
    setAnalysisJobId,
    analysisProgress,
    setAnalysisProgress,
    // NEW: Study management functions
    currentStudy,
    setCurrentStudy,
    studyId,
    setStudyId,
    initializeStudy,
    saveStudyProgress,
    loadStudyProgress
  };
};
