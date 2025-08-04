import { Edit3 } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface EditBadgeProps {
  isEdited?: boolean;
  className?: string;
}

export const EditBadge = ({ isEdited, className = "" }: EditBadgeProps) => {
  if (!isEdited) return null;

  return (
    <Badge 
      variant="secondary" 
      className={`
        bg-blue-500/10 text-blue-400 border-blue-500/20 
        flex items-center gap-1 text-xs px-2 py-1
        ${className}
      `}
    >
      <Edit3 className="h-3 w-3" />
      Edited
    </Badge>
  );
};