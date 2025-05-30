import { useState, useEffect, useRef } from "react";
import { useDebounce } from "./use-debounce";

interface Brand {
  id: string;
  name: string;
  domain: string;
  logo?: string;
}

interface UseSearchProps {
  onSelectBrand: (brand: Brand) => void;
}

export function useSearch({ onSelectBrand }: UseSearchProps) {
  const [search, setSearch] = useState("");
  const [filteredBrands, setFilteredBrands] = useState<Brand[]>([]);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [isDropdownVisible, setIsDropdownVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const debouncedSearch = useDebounce(search, 300);

  // Fetch brands from FastAPI backend, then construct logo URLs using Logo.dev image API
  useEffect(() => {
    if (debouncedSearch) {
      setLoading(true);
      setError(null);
      fetch(`/api/brand-search?q=${encodeURIComponent(debouncedSearch)}`)
        .then((res) => res.json())
        .then((data) => {
          if (Array.isArray(data)) {
            const brands = data.map((item: any) => ({
              id: item.domain || item.name,
              name: item.name,
              domain: item.domain,
              logo: item.logo,
            }));
            setFilteredBrands(brands);
          } else {
            setFilteredBrands([]);
            setError("No results found.");
          }
        })
        .catch(() => {
          setFilteredBrands([]);
          setError("Failed to fetch suggestions.");
        })
        .finally(() => {
          setLoading(false);
          setActiveIndex(-1); // Reset active index when results change
        });
    } else {
      setFilteredBrands([]);
      setError(null);
    }
  }, [debouncedSearch]);

  const handleSelectBrand = (brand: Brand) => {
    setSearch("");
    setIsDropdownVisible(false);
    onSelectBrand(brand);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!filteredBrands.length) return;

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setActiveIndex((prev) => {
          const newIndex = prev < filteredBrands.length - 1 ? prev + 1 : prev;
          return newIndex;
        });
        break;
      case "ArrowUp":
        e.preventDefault();
        setActiveIndex((prev) => {
          const newIndex = prev > 0 ? prev - 1 : 0;
          return newIndex;
        });
        break;
      case "Enter":
        e.preventDefault();
        if (activeIndex >= 0) {
          handleSelectBrand(filteredBrands[activeIndex]);
        } else if (filteredBrands.length > 0) {
          handleSelectBrand(filteredBrands[0]);
        }
        break;
      case "Escape":
        e.preventDefault();
        setSearch("");
        setIsDropdownVisible(false);
        break;
      default:
        break;
    }
  };

  const scrollActiveItemIntoView = (
    index: number,
    resultsListRef: React.RefObject<HTMLDivElement>
  ) => {
    if (resultsListRef.current && index >= 0) {
      const items = resultsListRef.current.querySelectorAll('[role="option"]');
      if (items[index]) {
        items[index].scrollIntoView({ block: "nearest" });
      }
    }
  };

  const hasSearchResults = filteredBrands.length > 0;
  const noResultsFound =
    debouncedSearch !== "" && filteredBrands.length === 0 && !loading && !error;

  return {
    search,
    setSearch,
    filteredBrands,
    activeIndex,
    setActiveIndex,
    isDropdownVisible,
    setIsDropdownVisible,
    handleSelectBrand,
    handleKeyDown,
    scrollActiveItemIntoView,
    hasSearchResults,
    noResultsFound,
    loading,
    error,
  };
}
