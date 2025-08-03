import { STEPS, SetupStep, stepLabels } from "../constants/wizardSteps";
import { CheckCircle } from "lucide-react";
import { Progress } from "@/components/ui/progress";

interface WizardProgressProps {
  currentStep: SetupStep;
  isComplete: (step: SetupStep) => boolean;
}

export const WizardProgress = ({ currentStep, isComplete }: WizardProgressProps) => {
  const currentIndex = STEPS.indexOf(currentStep);
  const progressPercentage = ((currentIndex + 1) / STEPS.length) * 100;
  
  return (
    <div className="mb-8 space-y-4">
      {/* Step Counter */}
      <div className="text-center">
        <p className="text-sm text-muted-foreground">
          Step {currentIndex + 1}/{STEPS.length}
        </p>
      </div>
      
      {/* Progress Bar */}
      <div className="w-full">
        <Progress 
          value={progressPercentage} 
          className="h-2 bg-secondary"
        />
      </div>
      
      {/* Step Indicators */}
      <div className="flex justify-between items-center text-xs font-medium gap-1">
        {STEPS.map((step, idx) => {
          const stepComplete = isComplete(step);
          const isCurrent = step === currentStep;
          
          return (
            <div 
              key={step} 
              className={`flex items-center gap-1 ${isCurrent ? "text-accent" : 
                stepComplete ? "text-accent" : "text-muted-foreground"}`}
            >
              {stepComplete ? (
                <CheckCircle className="h-3.5 w-3.5 text-accent" />
              ) : (
                <span className={`w-5 h-5 rounded-full border flex items-center justify-center text-[10px] ${
                  isCurrent ? "border-accent text-accent bg-accent/10" : "border-muted-foreground text-muted-foreground"
                }`}>
                  {idx + 1}
                </span>
              )}
              <span className="hidden sm:inline text-xs">{stepLabels[step]}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
