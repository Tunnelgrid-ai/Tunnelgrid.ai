
import { TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CheckCircle } from "lucide-react";
import { STEPS, SetupStep, stepLabels } from "../constants/wizardSteps";
import { useEffect, useState } from "react";

interface WizardTabsProps {
  currentStep: SetupStep;
  setCurrentStep: (step: SetupStep) => void;
  isComplete: (step: SetupStep) => boolean;
}

export const WizardTabs = ({
  currentStep,
  setCurrentStep,
  isComplete
}: WizardTabsProps) => {
  const [animateStep, setAnimateStep] = useState<string | null>(null);

  useEffect(() => {
    // Trigger animation when step changes
    setAnimateStep(currentStep);
    const timer = setTimeout(() => setAnimateStep(null), 500);
    return () => clearTimeout(timer);
  }, [currentStep]);

  return (
    <TabsList className="w-full grid grid-cols-5 mb-0 rounded-t-lg bg-charcoal relative overflow-hidden">
      {/* Progress bar that grows with each completed step */}
      <div 
        className="absolute bottom-0 left-0 h-0.5 bg-accent transition-all duration-300"
        style={{ 
          width: `${((STEPS.indexOf(currentStep) + (isComplete(currentStep) ? 1 : 0.5)) / STEPS.length) * 100}%` 
        }}
      />

      {STEPS.map((step, index) => {
        const isActive = step === currentStep;
        const isCompleted = isComplete(step);
        const stepIndex = STEPS.indexOf(step);
        const currentIndex = STEPS.indexOf(currentStep);

        return (
          <TabsTrigger
            key={step}
            value={step}
            onClick={() => setCurrentStep(step)}
            disabled={false}
            className={`
              relative font-heading tracking-tight text-sm md:text-base py-4 px-4 flex items-center justify-center gap-3
              transition-all duration-300
              ${isActive ? "text-white" : stepIndex < currentIndex ? "text-accent/70" : "text-muted-foreground"}
              ${animateStep === step ? "animate-pulse-subtle" : ""}
            `}
          >
            <span 
              className={`
                flex items-center justify-center w-6 h-6 rounded-full border
                ${isActive ? "border-accent bg-accent/10 text-accent" : 
                  isCompleted ? "border-accent bg-accent text-black" : 
                  "border-muted-foreground bg-transparent"}
                transition-all duration-300
              `}
            >
              {isCompleted ? (
                <CheckCircle className="h-4 w-4" />
              ) : (
                <span className="text-sm">{index + 1}</span>
              )}
            </span>
            <span className="hidden md:inline">{stepLabels[step]}</span>
          </TabsTrigger>
        );
      })}
    </TabsList>
  );
};
