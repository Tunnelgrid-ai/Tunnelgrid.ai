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
    <div className="mb-6 space-y-2">
      <div className="w-full">
        <Progress 
          value={progressPercentage} 
          className="h-1.5 bg-secondary"
        />
      </div>
      
      {/*
      <div className="flex justify-between items-center text-xs font-medium gap-1">
        {STEPS.map((step, idx) => {
          const stepComplete = isComplete(step);
          const isCurrent = step === currentStep;
          
          return (
            <div 
              key={step} 
              className={`flex items-center gap-1 ${isCurrent ? "text-[#00FFC2]" : 
                stepComplete ? "text-[#00FFC2]" : "text-text-secondary"}`}
            >
              {stepComplete ? (
                <CheckCircle className="h-3.5 w-3.5 text-[#00FFC2]" />
              ) : (
                <span className={`w-5 h-5 rounded-full border flex items-center justify-center text-[10px] ${
                  isCurrent ? "border-[#00FFC2] text-[#00FFC2]" : "border-text-secondary text-text-secondary"
                }`}>
                  {idx + 1}
                </span>
              )}
              <span className="hidden sm:inline">{stepLabels[step]}</span>
            </div>
          );
        })}
      </div>
      */}
    </div>
  );
};
