import React, { useState } from 'react';
import { Question, Topic } from "@/types/brandTypes";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Edit3, Check, X } from 'lucide-react';
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface QuestionsTableProps {
  questions: Question[];
  topics: Topic[];
  onQuestionUpdate: (questionId: string, updates: Partial<Question>) => void;
  isMobile: boolean;
}



const TOPIC_TYPE_COLORS = {
  'unbranded': 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  'branded': 'bg-green-500/20 text-green-300 border-green-500/30',
  'comparative': 'bg-purple-500/20 text-purple-300 border-purple-500/30'
};

export const QuestionsTable = ({
  questions,
  topics,
  onQuestionUpdate,
  isMobile
}: QuestionsTableProps) => {
  const [editingQuestionId, setEditingQuestionId] = useState<string | null>(null);
  const [editingText, setEditingText] = useState('');

  const startEditing = (question: Question) => {
    setEditingQuestionId(question.id);
    setEditingText(question.text);
  };

  const cancelEditing = () => {
    setEditingQuestionId(null);
    setEditingText('');
  };

  const saveEditing = () => {
    if (editingQuestionId) {
      onQuestionUpdate(editingQuestionId, {
        text: editingText.trim()
      });
    }
    cancelEditing();
  };

  const getTopicTypeStyle = (topicType: string) => {
    return TOPIC_TYPE_COLORS[topicType as keyof typeof TOPIC_TYPE_COLORS] || 'bg-gray-500/20 text-gray-300 border-gray-500/30';
  };

  if (questions.length === 0) {
    return (
      <div className="text-center py-12 text-white/60">
        <p>No questions match the current filters.</p>
      </div>
    );
  }

  if (isMobile) {
    return (
      <TooltipProvider delayDuration={200}>
        <div className="space-y-4">
        {questions.map((question) => {
          const isEditing = editingQuestionId === question.id;
          
          return (
            <div key={question.id} className="bg-background/50 rounded-lg border border-border/30 p-4 space-y-3">
              {/* Question Text */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-white/80">Question</span>
                  {!isEditing && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => startEditing(question)}
                      className="h-8 w-8 p-0 text-white/60 hover:text-white"
                    >
                      <Edit3 className="h-3 w-3" />
                    </Button>
                  )}
                </div>
                
                {isEditing ? (
                  <div className="space-y-3">
                    <Textarea
                      value={editingText}
                      onChange={(e) => setEditingText(e.target.value)}
                      className="min-h-[80px] text-white bg-background border-border/50"
                      placeholder="Enter question text..."
                    />
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={saveEditing}
                        className="flex-1 bg-[#00FFC2] text-black border-[#00FFC2] hover:bg-[#00FFC2]/90"
                      >
                        <Check className="h-3 w-3 mr-1" />
                        Save
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={cancelEditing}
                        className="flex-1 text-white border-border/50 hover:bg-background/50"
                      >
                        <X className="h-3 w-3 mr-1" />
                        Cancel
                      </Button>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-white leading-relaxed">{question.text}</p>
                )}
              </div>

                                            {/* Topic */}
              <div className="space-y-1">
                <span className="text-xs font-medium text-white/80">Topic</span>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <p className="text-xs text-white/60 overflow-hidden text-ellipsis whitespace-nowrap cursor-help">
                      {question.topicName || 'Unknown Topic'}
                    </p>
                  </TooltipTrigger>
                  <TooltipContent side="top" className="bg-gray-800 text-white p-2 rounded max-w-xs">
                    <p>{question.topicName || 'Unknown Topic'}</p>
                  </TooltipContent>
                </Tooltip>
              </div>

                {/* Topic Type */}
                <div className="flex gap-4">
                  <div className="space-y-1">
                    <span className="text-xs font-medium text-white/80">Type</span>
                    <Badge 
                      variant="outline" 
                      className={`text-xs capitalize ${getTopicTypeStyle(question.topicType || 'unbranded')}`}
                    >
                      {question.topicType || 'unbranded'}
                    </Badge>
                  </div>
                </div>
            </div>
          );
        })}
        </div>
      </TooltipProvider>
    );
  }

  // Desktop table view
  return (
    <TooltipProvider delayDuration={200}>
      <div className="bg-background/50 rounded-lg border border-border/30 overflow-hidden">
        <ScrollArea className="w-full overflow-x-auto">
        <div className="min-w-[700px]">
          {/* Table Header */}
          <div className="grid grid-cols-10 gap-3 p-3 bg-background/80 border-b border-border/30 text-xs font-medium text-white/80">
            <div className="col-span-6">Question</div>
            <div className="col-span-2">Topic</div>
            <div className="col-span-2">Topic Type</div>
          </div>

          {/* Table Body */}
          <div className="divide-y divide-border/20">
            {questions.map((question) => {
              const isEditing = editingQuestionId === question.id;
              
              return (
                <div key={question.id} className="grid grid-cols-10 gap-3 p-3 hover:bg-background/30 transition-colors">
                  {/* Question Column */}
                  <div className="col-span-6 space-y-2">
                    {isEditing ? (
                      <div className="space-y-2">
                        <Textarea
                          value={editingText}
                          onChange={(e) => setEditingText(e.target.value)}
                          className="min-h-[60px] text-sm text-white bg-background border-border/50 resize-none"
                          placeholder="Enter question text..."
                        />
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={saveEditing}
                            className="h-8 bg-[#00FFC2] text-black border-[#00FFC2] hover:bg-[#00FFC2]/90"
                          >
                            <Check className="h-3 w-3 mr-1" />
                            Save
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={cancelEditing}
                            className="h-8 text-white border-border/50 hover:bg-background/50"
                          >
                            <X className="h-3 w-3 mr-1" />
                            Cancel
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-start gap-2 group">
                        <p className="text-sm text-white leading-relaxed flex-1">{question.text}</p>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => startEditing(question)}
                          className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100 transition-opacity text-white/60 hover:text-white shrink-0"
                        >
                          <Edit3 className="h-3 w-3" />
                        </Button>
                      </div>
                    )}
                  </div>

                  {/* Topic Column */}
                  <div className="col-span-2 flex items-center">
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <p className="text-sm text-white/60 overflow-hidden text-ellipsis whitespace-nowrap cursor-help">
                          {question.topicName || 'Unknown Topic'}
                        </p>
                      </TooltipTrigger>
                      <TooltipContent side="top" className="bg-gray-800 text-white p-2 rounded max-w-xs">
                        <p>{question.topicName || 'Unknown Topic'}</p>
                      </TooltipContent>
                    </Tooltip>
                  </div>

                  {/* Topic Type Column */}
                  <div className="col-span-2 flex items-center">
                    <Badge 
                      variant="outline" 
                      className={`text-xs capitalize ${getTopicTypeStyle(question.topicType || 'unbranded')}`}
                    >
                      {question.topicType || 'unbranded'}
                    </Badge>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </ScrollArea>
      </div>
    </TooltipProvider>
  );
};