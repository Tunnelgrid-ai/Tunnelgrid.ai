
import React, { forwardRef } from "react";
import { Search, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

interface SearchInputProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onKeyDown: (e: React.KeyboardEvent) => void;
  onFocus: () => void;
  onSubmit: () => void;
  activeDescendant?: string;
}

export const SearchInput = forwardRef<HTMLInputElement, SearchInputProps>(
  ({ value, onChange, onKeyDown, onFocus, onSubmit, activeDescendant }, ref) => {
    return (
      <div className="rounded-lg overflow-hidden border-2 bg-background border-border/30 shadow-md">
        <div className="relative h-[52px]">
          <div className="flex items-center border-b px-3 h-[52px] min-h-[52px]">
            <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
            <input 
              ref={ref}
              type="text"
              placeholder="Type a brand name..." 
              value={value} 
              onChange={onChange} 
              className="flex-1 bg-transparent border-none outline-none pr-16"
              onKeyDown={onKeyDown}
              onFocus={onFocus}
              role="combobox"
              aria-controls="search-results-list"
              aria-activedescendant={activeDescendant}
            />
            <div className="absolute right-3 top-1/2 -translate-y-1/2 z-10">
              <Button 
                size="sm" 
                className="bg-[#3BFFD3] hover:bg-[#3BFFD3]/90 text-black font-medium rounded-full px-4" 
                onClick={onSubmit}
              >
                <span className="mr-1">Go</span>
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }
);

SearchInput.displayName = "SearchInput";
