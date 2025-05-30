
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, ArrowRight } from "lucide-react";
import { SetupStep } from "../constants/wizardSteps";

interface WizardNavigationProps {
  currentStep: SetupStep;
  getCurrentStepIndex: () => number;
  onPrevious: () => void;
  onNext: () => void;
  onSubmit: () => void;
}

export const WizardNavigation = ({
  currentStep,
  getCurrentStepIndex,
  onPrevious,
  onNext,
  onSubmit
}: WizardNavigationProps) => {
  return (
    <div className="p-6 border-t border-black/20 flex justify-between">
      <Button
        variant="ghost"
        size="sm"
        onClick={onPrevious}
        disabled={getCurrentStepIndex() === 0}
        className="text-text-secondary hover:text-white"
      >
        <ChevronLeft className="mr-2 h-4 w-4" /> Previous
      </Button>

      {currentStep !== "review" ? (
        <Button onClick={onNext} className="min-w-[160px]">
          Next <ChevronRight className="ml-2 h-4 w-4" />
        </Button>
      ) : (
        <Button onClick={onSubmit} className="min-w-[160px]">
          Submit <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      )}
    </div>
  );
};
