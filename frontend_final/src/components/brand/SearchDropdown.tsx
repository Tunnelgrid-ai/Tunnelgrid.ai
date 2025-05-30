import { Check } from "lucide-react";
import { cn } from "@/lib/utils";
import { forwardRef } from "react";

interface Brand {
  id: string;
  name: string;
  domain: string;
  logo?: string;
}

interface SearchDropdownProps {
  filteredBrands: Brand[];
  activeIndex: number;
  selectedBrand: Brand | null;
  isVisible: boolean;
  noResultsFound: boolean;
  loading?: boolean;
  error?: string | null;
  onSelectBrand: (brand: Brand) => void;
}

export const SearchDropdown = forwardRef<HTMLDivElement, SearchDropdownProps>(
  ({ filteredBrands, activeIndex, selectedBrand, isVisible, noResultsFound, loading, error, onSelectBrand }, ref) => {
    if (!isVisible || (!filteredBrands.length && !noResultsFound && !loading && !error)) {
      return null;
    }

    return (
      <div 
        className="absolute top-full left-0 w-full z-50 bg-background border-2 border-t-0 border-border/30 rounded-b-lg shadow-lg mt-[-1px]" 
        style={{
          maxHeight: '300px',
          overflowY: 'auto',
        }}
      >
        <div 
          ref={ref}
          className="py-1"
          id="search-results-list"
          role="listbox"
        >
          {loading && (
            <div className="py-6 text-center text-sm text-muted-foreground">Loading...</div>
          )}
          {error && !loading && (
            <div className="py-6 text-center text-sm text-red-500">{error}</div>
          )}
          {noResultsFound && !loading && !error && (
            <div className="py-6 text-center text-sm">No brands found</div>
          )}
          {filteredBrands.length > 0 && !loading && !error && (
            <div>
              {filteredBrands.map((brand, index) => (
                <div
                  key={brand.id}
                  id={`brand-item-${brand.id}`}
                  onClick={() => onSelectBrand(brand)}
                  className={cn(
                    "flex items-center py-3 px-3 cursor-pointer border border-transparent transition-all duration-200",
                    activeIndex === index 
                      ? "border-accent/80 shadow-[0_0_8px_rgba(59,255,211,0.3)] bg-accent/5" 
                      : "hover:border-accent/80 hover:shadow-[0_0_8px_rgba(59,255,211,0.3)] focus:border-accent/80 focus:shadow-[0_0_8px_rgba(59,255,211,0.3)]"
                  )}
                  role="option"
                  aria-selected={activeIndex === index}
                >
                  <div className="flex items-center gap-3 flex-1">
                    <div className="w-10 h-10 bg-slate-800 rounded-md flex items-center justify-center overflow-hidden">
                      {brand.logo ? (
                        <img src={brand.logo} alt={brand.name} className="w-full h-full object-cover" />
                      ) : (
                        <span className="text-sm font-medium">
                          {brand.name.substring(0, 2)}
                        </span>
                      )}
                    </div>
                    <div>
                      <p className="font-medium">{brand.name}</p>
                      <p className="text-sm text-muted-foreground">{brand.domain}</p>
                    </div>
                  </div>
                  <Check className={cn("h-4 w-4 text-accent", selectedBrand?.id === brand.id ? "opacity-100" : "opacity-0")} />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }
);

SearchDropdown.displayName = "SearchDropdown";
