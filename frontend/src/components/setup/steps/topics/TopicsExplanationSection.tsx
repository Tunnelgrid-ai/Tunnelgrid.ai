import { Alert, AlertDescription } from "@/components/ui/alert";
import { Target, Folder } from "lucide-react";

export const TopicsExplanationSection = () => {
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-heading font-semibold text-white">Configure Topics</h2>
      
      <Alert className="border-accent/20 bg-accent/5">
        <Target className="h-4 w-4 text-accent" />
        <AlertDescription className="text-sm space-y-3">
          <p>
            <span className="text-accent font-medium">Topics organize your brand monitoring strategy. </span> 
             Each topic represents a different way your customers might discuss your brand, helping you understand how your brand appears in various conversation contexts.
          </p>
          
          <div className="bg-background/50 rounded-lg p-4 space-y-3">
            <div className="flex items-center gap-2">
              <Folder className="h-4 w-4 text-accent" />
              <span className="font-medium text-white">Topic Categories:</span>
            </div>
            
            <div className="ml-6 space-y-2 text-xs">
              <div className="flex items-start gap-2">
                <div className="w-2 h-2 bg-blue-400 rounded-full mt-1.5 flex-shrink-0"></div>
                <div className="text-muted-foreground">
                  <span className="text-blue-400 font-medium">Unbranded:</span> Monitor when AI mentions your brand naturally in general discussions
                </div>
              </div>
              
              <div className="flex items-start gap-2">
                <div className="w-2 h-2 bg-green-400 rounded-full mt-1.5 flex-shrink-0"></div>
                <div className="text-muted-foreground">
                  <span className="text-green-400 font-medium">Branded:</span> Track what AI says when directly asked about your brand
                </div>
              </div>
              
              <div className="flex items-start gap-2">
                <div className="w-2 h-2 bg-purple-400 rounded-full mt-1.5 flex-shrink-0"></div>
                <div className="text-muted-foreground">
                  <span className="text-purple-400 font-medium">Comparative:</span> Understand how AI compares your brand to competitors
                </div>
              </div>
            </div>
          </div>
        </AlertDescription>
      </Alert>
    </div>
  );
}; 