
import { TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CheckCircle } from "lucide-react";
import { STEPS, SetupStep, stepLabels } from "./constants/wizardSteps";
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
  const activeIndex = STEPS.indexOf(currentStep);
  const totalSteps = STEPS.length;

  useEffect(() => {
    // Trigger animation when step changes
    setAnimateStep(currentStep);
    const timer = setTimeout(() => setAnimateStep(null), 500);
    return () => clearTimeout(timer);
  }, [currentStep]);

  return (
    <TabsList className="flex w-full border-b border-border/40 relative overflow-x-auto scrollbar-hide bg-charcoal rounded-t-lg">
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
              flex-1 min-w-[140px] px-4 py-3 relative text-center
              font-heading text-sm sm:text-base
              data-[state=active]:text-foreground data-[state=active]:font-semibold
              data-[state=active]:before:bg-brand-purple
              before:absolute before:-left-px before:inset-y-0 before:w-0.5
              hover:bg-muted/20 transition
              ${isActive ? "text-white" : stepIndex < currentIndex ? "text-accent/70" : "text-muted-foreground"}
              ${animateStep === step ? "animate-pulse-subtle" : ""}
            `}
          >
            <span className="flex items-center justify-center gap-2">
              <span 
                className={`
                  w-6 h-6 rounded-full border border-border/60 text-xs flex items-center
                  justify-center
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
            </span>
          </TabsTrigger>
        );
      })}
      
      {/* Progress bar */}
      <span
        style={{ width: `${((activeIndex + 1) / totalSteps) * 100}%` }}
        className="absolute bottom-0 left-0 h-0.5 bg-brand-purple transition-all duration-300"
      />
    </TabsList>
  );
};
