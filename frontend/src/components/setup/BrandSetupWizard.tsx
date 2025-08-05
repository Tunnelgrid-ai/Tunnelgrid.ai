import { Tabs, TabsContent } from "@/components/ui/tabs";
import { BrandInfoStep } from "./steps/BrandInfoStep";
import { TopicsStep } from "./steps/TopicsStep";
import { PersonasStep } from "./steps/PersonasStep";
import { QuestionsStep } from "./steps/QuestionsStep";
import { ReviewStep } from "./steps/ReviewStep";
import { AnalysisLoadingScreen } from "../analysis/AnalysisLoadingScreen";
import { WizardNavigation } from "./components/WizardNavigation";
import { WizardProgress } from "./components/WizardProgress";
import { useWizardState } from "./hooks/useWizardState";
import type { Product, BrandEntity } from "@/types/brandTypes";
import { useEffect } from "react";

interface BrandSetupWizardProps {
  brand: BrandEntity;
  brandDescription: string;
  studyId?: string; // NEW: Optional study ID for editing existing studies
}

export const BrandSetupWizard = ({
  brand,
  brandDescription,
  studyId
}: BrandSetupWizardProps) => {
  const {
    currentStep,
    setCurrentStep,
    brandInfo,
    setBrandInfo,
    setBrandInfoWithProgress, // NEW: Use setter with progress saving
    products,
    availableProducts,
    topics,
    setTopics,
    setTopicsWithProgress, // NEW: Use setter with progress saving
    personas,
    setPersonas,
    setPersonasWithProgress, // NEW: Use setter with progress saving
    questions,
    setQuestions,
    setQuestionsWithProgress, // NEW: Use setter with progress saving
    handleNext,
    prevStep,
    isComplete,
    getCurrentStepIndex,
    submitSetup,
    setProducts,
    setProductsWithProgress, // NEW: Use setter with progress saving
    brandId,
    handleAuditCreated,
    getAuditContext,
    setTriggerAuditCreation,
    handleNextWithAuditCheck,
    // Analysis loading state
    analysisLoading,
    setAnalysisLoading,
    analysisJobId,
    analysisProgress,
    auditId,
    // NEW: Study management functions
    initializeStudy,
    currentStudy,
    studyId: wizardStudyId
  } = useWizardState();

  // Initialize study if studyId is provided
  useEffect(() => {
    if (studyId && !wizardStudyId) {
      console.log('🔄 Initializing study with ID:', studyId);
      initializeStudy(studyId);
    }
  }, [studyId, wizardStudyId, initializeStudy]);

  // Set brandDescription in brandInfo when component mounts
  useEffect(() => {
    if (brandDescription && !brandInfo.description) {
      setBrandInfo(prev => ({
        ...prev,
        description: brandDescription
      }));
    }
  }, [brandDescription, brandInfo.description, setBrandInfo]);

  // Show loading screen when analysis is running
  if (analysisLoading) {
    return (
      <AnalysisLoadingScreen
        auditId={auditId || ''}
        jobId={analysisJobId}
        onComplete={(results) => {
          console.log('✅ Analysis completed:', results);
          setAnalysisLoading(false);
          // TODO: Navigate to results page
          // navigate(`/results/${auditId}`);
        }}
        onError={(error) => {
          console.error('❌ Analysis failed:', error);
          setAnalysisLoading(false);
        }}
        onCancel={() => {
          console.log('🚫 Analysis cancelled by user');
          setAnalysisLoading(false);
        }}
      />
    );
  }

  return (
    <div className="bg-charcoal rounded-lg shadow-lg border border-black/20">
      <div className="px-6 pt-6 md:pt-8 md:px-8">
        <WizardProgress 
          currentStep={currentStep}
          isComplete={isComplete}
        />
      </div>
      
      <Tabs value={currentStep} className="w-full animate-fade-in">
        <TabsContent value="brand-info" className="p-6 md:p-8 pt-0">
          <BrandInfoStep 
            brandInfo={brandInfo} 
            setBrandInfo={setBrandInfoWithProgress} 
            products={products}
            setProducts={setProductsWithProgress}
            brandDescription={brandDescription}
            availableProducts={availableProducts}
            brandId={brandId}
            onAuditCreated={handleAuditCreated}
            setTriggerAuditCreation={setTriggerAuditCreation}
          />
        </TabsContent>

        <TabsContent value="topics" className="p-6 md:p-8 pt-0">
          <TopicsStep 
            topics={topics} 
            setTopics={setTopicsWithProgress} 
            products={products}
            auditContext={getAuditContext()}
          />
        </TabsContent>

        <TabsContent value="personas" className="p-6 md:p-8 pt-0">
          <PersonasStep 
            personas={personas} 
            setPersonas={setPersonasWithProgress} 
            topics={topics}
            products={products}
            auditContext={getAuditContext()}
          />
        </TabsContent>

        <TabsContent value="questions" className="p-6 md:p-8 pt-0">
          <QuestionsStep 
            questions={questions} 
            setQuestions={setQuestionsWithProgress} 
            personas={personas}
            topics={topics}
            brandInfo={brandInfo}
            products={products}
            auditContext={getAuditContext()}
          />
        </TabsContent>

        <TabsContent value="review" className="p-6 md:p-8 pt-0">
          <ReviewStep 
            brandInfo={brandInfo}
            products={products}
            topics={topics}
            personas={personas}
            questions={questions}
          />
        </TabsContent>

        <WizardNavigation
          currentStep={currentStep}
          getCurrentStepIndex={getCurrentStepIndex}
          onPrevious={prevStep}
          onNext={handleNextWithAuditCheck}
          onSubmit={submitSetup}
        />
      </Tabs>
    </div>
  );
};
