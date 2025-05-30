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
import { useToast } from "@/hooks/use-toast";
import { STEPS, SetupStep } from "../constants/wizardSteps";
import { v4 as uuidv4 } from 'uuid';

export const useWizardState = () => {
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
  
  const { toast } = useToast();
  const location = useLocation();

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
    
    // Show success message
    toast({
      title: "Analysis Started",
      description: "Your brand audit has been initiated!",
      variant: "default"
    });
    
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
          toast({
            title: "Missing information",
            description: "Please provide brand information and select at least one product.",
            variant: "destructive",
          });
          return false;
        }
        // NEW: Don't require audit ID here since it gets created in this step
        return true;
        
      case "topics":
        // NEW: Require audit ID for topics step
        if (!auditId) {
          toast({
            title: "Audit Required",
            description: "Please complete the brand information step first.",
            variant: "destructive",
          });
          return false;
        }
        if (topics.length === 0) {
          toast({
            title: "No topics selected",
            description: "Please select or add at least one topic.",
            variant: "destructive",
          });
          return false;
        }
        return true;
        
      case "personas":
        // NEW: Require audit ID for personas step
        if (!auditId) {
          toast({
            title: "Audit Required",
            description: "Please complete the previous steps first.",
            variant: "destructive",
          });
          return false;
        }
        // Remove validation for personas since this step is now read-only
        return true;
        
      case "questions":
        // NEW: Require audit ID for questions step
        if (!auditId) {
          toast({
            title: "Audit Required",
            description: "Please complete the previous steps first.",
            variant: "destructive",
          });
          return false;
        }
        if (questions.length === 0) {
          toast({
            title: "No questions defined",
            description: "Please add at least one question.",
            variant: "destructive",
          });
          return false;
        }
        return true;
        
      case "review":
        // NEW: Require audit ID for final review
        if (!auditId) {
          toast({
            title: "Audit Required",
            description: "Please complete all previous steps first.",
            variant: "destructive",
          });
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
   * UPDATED: Submit Setup with Audit Completion
   * 
   * PURPOSE: Handle final wizard submission and mark audit as completed
   * 
   * WORKFLOW:
   * 1. Validate all required data is present
   * 2. Process final submission (existing logic)
   * 3. Mark audit as 'completed' in database
   * 4. Show success feedback and redirect
   */
  const submitSetup = async () => {
    try {
      // STEP 1: Validate we have an audit to complete
      if (!auditId) {
        console.error('❌ No audit ID available for completion');
        toast({
          title: "Submission Error",
          description: "No audit information found. Please restart the process.",
          variant: "destructive"
        });
        return;
      }

      // STEP 2: Validate required data
      if (!brandInfo || !products.length || !topics.length) {
        toast({
          title: "Incomplete Setup",
          description: "Please complete all steps before submitting.",
          variant: "destructive"
        });
        return;
      }

      console.log('🚀 Submitting setup and completing audit:', auditId);

      // STEP 3: Complete the audit in database
      const { completeAudit } = await import('@/services/auditService');
      const completionResult = await completeAudit(auditId);

      if (!completionResult.success) {
        throw new Error(completionResult.error || 'Failed to complete audit');
      }

      // STEP 4: Show success message
      toast({
        title: "Setup Complete!",
        description: "Your brand analysis setup has been completed and saved.",
        variant: "default"
      });

      console.log('✅ Wizard completed successfully with audit:', auditId);

      // STEP 5: Could add navigation to results page here
      // navigate('/dashboard') or similar

    } catch (error) {
      console.error('💥 Error completing setup:', error);
      
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      toast({
        title: "Submission Failed",
        description: errorMessage,
        variant: "destructive"
      });
    }
  };

  return {
    currentStep,
    setCurrentStep,
    brandInfo,
    setBrandInfo,
    products,
    setProducts,
    availableProducts,
    topics,
    setTopics,
    personas,
    setPersonas,
    questions,
    setQuestions,
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
  };
};
