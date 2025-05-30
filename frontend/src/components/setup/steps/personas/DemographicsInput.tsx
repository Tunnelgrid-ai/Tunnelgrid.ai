
import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { X, PlusCircle } from "lucide-react";

interface Demographics {
  ageRange?: string;
  gender?: string;
  location?: string;
  goals?: string[];
}

interface DemographicsInputProps {
  demographics: Demographics;
  setDemographics: (demographics: Demographics) => void;
}

export const DemographicsInput = ({ 
  demographics, 
  setDemographics 
}: DemographicsInputProps) => {
  const [goal, setGoal] = useState("");

  const addGoal = () => {
    if (goal.trim()) {
      setDemographics({
        ...demographics,
        goals: [...(demographics.goals || []), goal.trim()],
      });
      setGoal("");
    }
  };

  const removeGoal = (index: number) => {
    if (demographics.goals) {
      const updated = [...demographics.goals];
      updated.splice(index, 1);
      setDemographics({
        ...demographics,
        goals: updated,
      });
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-md font-heading font-medium">Demographics (Optional)</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="space-y-2">
          <Label htmlFor="age-range">Age Range</Label>
          <Input
            id="age-range"
            value={demographics.ageRange || ""}
            onChange={(e) =>
              setDemographics({
                ...demographics,
                ageRange: e.target.value,
              })
            }
            placeholder="e.g., 25-34"
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="gender">Gender</Label>
          <Input
            id="gender"
            value={demographics.gender || ""}
            onChange={(e) =>
              setDemographics({
                ...demographics,
                gender: e.target.value,
              })
            }
            placeholder="e.g., Any"
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="location">Location</Label>
          <Input
            id="location"
            value={demographics.location || ""}
            onChange={(e) =>
              setDemographics({
                ...demographics,
                location: e.target.value,
              })
            }
            placeholder="e.g., Urban areas"
          />
        </div>
      </div>
      
      <div className="space-y-2">
        <Label>Goals</Label>
        <div className="flex space-x-2">
          <Input
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="e.g., Save money while staying fit"
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                addGoal();
                e.preventDefault();
              }
            }}
          />
          <Button type="button" onClick={addGoal}>
            <PlusCircle className="h-4 w-4 mr-2" /> Add
          </Button>
        </div>

        {demographics.goals && demographics.goals.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {demographics.goals.map((item, index) => (
              <div
                key={index}
                className="flex items-center bg-card-dark border border-black/20 rounded-full px-3 py-1"
              >
                <span className="text-sm">{item}</span>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-5 w-5 p-0 ml-1"
                  onClick={() => removeGoal(index)}
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
