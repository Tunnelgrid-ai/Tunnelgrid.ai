import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

interface Brand {
  id: string;
  name: string;
  domain: string;
  logo?: string;
}

interface BrandCardProps {
  brand: Brand;
  onAnalyze: () => void;
  onBack: () => void;
}

export const BrandCard = ({ brand, onAnalyze, onBack }: BrandCardProps) => {
  return (
    <div className="flex flex-col items-center justify-center py-8">
      <div className="w-24 h-24 bg-slate-800 rounded-lg flex items-center justify-center overflow-hidden mb-4 shadow-sm">
        {brand.logo ? (
          <img src={brand.logo} alt={brand.name} className="w-full h-full object-cover" />
        ) : (
          <span className="text-2xl font-medium">
            {brand.name.substring(0, 2)}
          </span>
        )}
      </div>
      <h2 className="text-2xl font-bold mb-1 font-mono tracking-tight">{brand.name}</h2>
      <p className="text-sm text-muted-foreground mb-8">{brand.domain}</p>
      
      <Button onClick={onAnalyze} className="w-full max-w-md text-lg py-6 bg-accent hover:bg-accent/90 text-accent-foreground">
        Setup Audit
        <ArrowRight className="ml-2 h-5 w-5" />
      </Button>
      
      <Button variant="ghost" size="sm" className="mt-4" onClick={onBack}>
        Search for another brand
      </Button>
    </div>
  );
};
