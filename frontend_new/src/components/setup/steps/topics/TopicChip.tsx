
import { useState, useRef, useEffect } from "react";
import { Topic } from "@/types/brandTypes";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Edit } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface TopicChipProps {
  topic: Topic;
  onUpdate: (updatedTopic: Topic) => void;
}

export const TopicChip = ({ topic, onUpdate }: TopicChipProps) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(topic.name);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isEditing]);

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = () => {
    if (editValue.trim() !== "") {
      onUpdate({
        ...topic,
        name: editValue.trim()
      });
    }
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSave();
    } else if (e.key === "Escape") {
      setEditValue(topic.name); // Reset to original value
      setIsEditing(false);
    }
  };

  // Check if the topic name is longer than 48 characters
  const isLongName = topic.name.length > 48;
  const displayName = isLongName ? `${topic.name.substring(0, 45)}...` : topic.name;

  return (
    <div className="relative inline-block">
      {isEditing ? (
        <div className="min-w-[120px] max-w-full">
          <Input
            ref={inputRef}
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            onBlur={handleSave}
            onKeyDown={handleKeyDown}
            className="py-1 h-8 text-sm focus:ring-[#00FFC2] focus:border-[#00FFC2]"
            autoFocus
          />
        </div>
      ) : (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Badge
                variant="outline"
                className={cn(
                  "px-4 py-2 text-sm cursor-pointer transition-all hover:bg-[#00FFC2]/10",
                  "border-[#00FFC2]/30 hover:border-[#00FFC2]",
                  "group flex items-center gap-1.5 whitespace-nowrap max-w-full",
                  "min-w-[80px]"
                )}
                onClick={handleEdit}
              >
                <span className="truncate">{displayName}</span>
                <Edit className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity ml-1 flex-shrink-0" />
              </Badge>
            </TooltipTrigger>
            {isLongName && (
              <TooltipContent side="top" className="max-w-xs">
                <p>{topic.name}</p>
              </TooltipContent>
            )}
          </Tooltip>
        </TooltipProvider>
      )}
    </div>
  );
};
