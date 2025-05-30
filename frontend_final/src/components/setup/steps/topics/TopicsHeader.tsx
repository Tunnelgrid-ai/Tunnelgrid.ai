
import React from "react";

interface TopicsHeaderProps {
  step?: number;
  totalSteps?: number;
}

export const TopicsHeader: React.FC<TopicsHeaderProps> = ({ 
  step = 2, 
  totalSteps = 5 
}) => {
  return (
    <div>
      {/*<div className="flex items-center gap-2 mb-2">
        <span className="bg-brand-purple/20 text-brand-purple text-xs font-medium px-2.5 py-1 rounded-full">
          Step {step} of {totalSteps}
        </span>
      </div>*/}
      <h2 className="text-2xl font-heading mb-2 text-white tracking-tight bg-gradient-to-r from-brand-blue via-brand-purple to-brand-cyan bg-clip-text text-transparent">
        Brand Topics
      </h2>
      <p className="text-muted-foreground mb-6">
        These are the key topics that your audience commonly discusses about your brand. 
        Click on any topic to edit it.
      </p>
    </div>
  );
};
