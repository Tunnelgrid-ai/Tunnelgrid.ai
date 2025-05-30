
import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { X, PlusCircle } from "lucide-react";

interface MotivatorsInputProps {
  motivators: string[];
  setMotivators: (motivators: string[]) => void;
}

export const MotivatorsInput = ({ motivators, setMotivators }: MotivatorsInputProps) => {
  const [motivator, setMotivator] = useState("");

  const addMotivator = () => {
    if (motivator.trim()) {
      setMotivators([...motivators, motivator.trim()]);
      setMotivator("");
    }
  };

  const removeMotivator = (index: number) => {
    const updated = [...motivators];
    updated.splice(index, 1);
    setMotivators(updated);
  };

  return (
    <div className="space-y-2">
      <Label>Motivators</Label>
      <div className="flex space-x-2">
        <Input
          value={motivator}
          onChange={(e) => setMotivator(e.target.value)}
          placeholder="e.g., Wants to support sustainable brands"
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              addMotivator();
              e.preventDefault();
            }
          }}
        />
        <Button type="button" onClick={addMotivator}>
          <PlusCircle className="h-4 w-4 mr-2" /> Add
        </Button>
      </div>

      {motivators.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-2">
          {motivators.map((item, index) => (
            <div
              key={index}
              className="flex items-center bg-card-dark border border-black/20 rounded-full px-3 py-1"
            >
              <span className="text-sm">{item}</span>
              <Button
                variant="ghost"
                size="sm"
                className="h-5 w-5 p-0 ml-1"
                onClick={() => removeMotivator(index)}
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
