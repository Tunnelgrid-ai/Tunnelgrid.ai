import { useState } from "react";
import { Topic } from "@/types/brandTypes";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Edit3, Save, X, Trash2 } from "lucide-react";

interface TopicCardProps {
  topic: Topic;
  onEdit?: (topicId: string, updates: Partial<Topic>) => void;
  onDelete?: (topicId: string) => void;
}

export const TopicCard: React.FC<TopicCardProps> = ({
  topic,
  onEdit,
  onDelete
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedName, setEditedName] = useState(topic.name);

  const handleSave = () => {
    if (onEdit && topic.id) {
      onEdit(topic.id, {
        name: editedName.trim()
      });
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedName(topic.name);
    setIsEditing(false);
  };

  const handleDelete = () => {
    if (onDelete && topic.id && confirm(`Are you sure you want to delete "${topic.name}"?`)) {
      onDelete(topic.id);
    }
  };

  return (
    <div className="p-4 bg-background/50 rounded-lg border border-border/30 hover:border-border/50 transition-colors">
      {!isEditing ? (
        <>
          {/* View Mode */}
          <div className="flex items-start justify-between">
            <div className="flex-1 space-y-1">
              <h4 className="font-medium text-white">{topic.name}</h4>
            </div>
            
            <div className="flex items-center gap-1 ml-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsEditing(true)}
                className="h-8 w-8 p-0"
              >
                <Edit3 className="h-3 w-3" />
              </Button>
              
              {onDelete && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleDelete}
                  className="h-8 w-8 p-0 text-red-400 hover:text-red-300"
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              )}
            </div>
          </div>
        </>
      ) : (
        <>
          {/* Edit Mode */}
          <div className="space-y-3">
            <Input
              value={editedName}
              onChange={(e) => setEditedName(e.target.value)}
              placeholder="Topic name"
              className="bg-background border-input"
            />
            
            <div className="flex items-center gap-2 justify-end">
              <Button
                variant="outline"
                size="sm"
                onClick={handleCancel}
              >
                <X className="h-3 w-3 mr-1" />
                Cancel
              </Button>
              
              <Button
                size="sm"
                onClick={handleSave}
                disabled={!editedName.trim()}
                className="bg-accent hover:bg-accent/90 text-black"
              >
                <Save className="h-3 w-3 mr-1" />
                Save
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}; 