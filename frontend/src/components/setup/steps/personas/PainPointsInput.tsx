
import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { X, PlusCircle } from "lucide-react";

interface PainPointsInputProps {
  painPoints: string[];
  setPainPoints: (points: string[]) => void;
}

export const PainPointsInput = ({ painPoints, setPainPoints }: PainPointsInputProps) => {
  const [painPoint, setPainPoint] = useState("");

  const addPainPoint = () => {
    if (painPoint.trim()) {
      setPainPoints([...painPoints, painPoint.trim()]);
      setPainPoint("");
    }
  };

  const removePainPoint = (index: number) => {
    const updated = [...painPoints];
    updated.splice(index, 1);
    setPainPoints(updated);
  };

  return (
    <div className="space-y-2">
      <Label>Pain Points</Label>
      <div className="flex space-x-2">
        <Input
          value={painPoint}
          onChange={(e) => setPainPoint(e.target.value)}
          placeholder="e.g., Finding affordable quality products"
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              addPainPoint();
              e.preventDefault();
            }
          }}
        />
        <Button type="button" onClick={addPainPoint}>
          <PlusCircle className="h-4 w-4 mr-2" /> Add
        </Button>
      </div>

      {painPoints.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-2">
          {painPoints.map((point, index) => (
            <div
              key={index}
              className="flex items-center bg-card-dark border border-black/20 rounded-full px-3 py-1"
            >
              <span className="text-sm">{point}</span>
              <Button
                variant="ghost"
                size="sm"
                className="h-5 w-5 p-0 ml-1"
                onClick={() => removePainPoint(index)}
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
