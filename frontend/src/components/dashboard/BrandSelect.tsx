
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Check, ChevronsUpDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface Brand {
  id: string;
  name: string;
}

const dummyBrands: Brand[] = [
  { id: "1", name: "TechPulse" },
  { id: "2", name: "EcoSmart" },
  { id: "3", name: "FitForward" },
  { id: "4", name: "NutriWell" },
];

interface BrandSelectProps {
  onSelect: (brandId: string) => void;
}

export function BrandSelect({ onSelect }: BrandSelectProps) {
  const [open, setOpen] = useState(false);
  const [selectedBrand, setSelectedBrand] = useState<Brand>(dummyBrands[0]);

  const handleSelect = (brand: Brand) => {
    setSelectedBrand(brand);
    onSelect(brand.id);
    setOpen(false);
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="justify-between w-[200px]"
        >
          {selectedBrand ? selectedBrand.name : "Select brand..."}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[200px] p-0">
        <div className="max-h-[300px] overflow-auto">
          {dummyBrands.map((brand) => (
            <Button
              key={brand.id}
              variant="ghost"
              className={cn(
                "flex w-full justify-start",
                selectedBrand?.id === brand.id && "bg-accent text-accent-foreground"
              )}
              onClick={() => handleSelect(brand)}
            >
              <Check
                className={cn(
                  "mr-2 h-4 w-4",
                  selectedBrand?.id === brand.id ? "opacity-100" : "opacity-0"
                )}
              />
              {brand.name}
            </Button>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
}
