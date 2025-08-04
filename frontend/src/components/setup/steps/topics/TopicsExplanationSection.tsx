import { Alert, AlertDescription } from "@/components/ui/alert";
import { Target } from "lucide-react";

export const TopicsExplanationSection = () => {
  return (
    <div className="space-y-6">
      <Alert className="border-accent/20 bg-accent/5">
        <Target className="h-4 w-4 text-accent" />
        <AlertDescription className="text-sm space-y-4">
          <div>
            <h3 className="text-accent font-semibold mb-2">Why topics matter</h3>
            <p className="text-muted-foreground">
              Topics organize your brand-monitoring strategy. They show where AI mentions your brand: casual chat, direct questions, or competitor comparisons - so you see the complete picture of your brand in conversation.
            </p>
          </div>
          
          <div className="border-t border-accent/10 pt-4">
            <p className="text-white">
              <span className="text-accent font-medium">We've already set up topics for you.</span>
            </p>
            <p className="text-muted-foreground mt-1">
              Review the list, keep what fits, and edit anything that doesn't.
            </p>
          </div>
        </AlertDescription>
      </Alert>
    </div>
  );
};