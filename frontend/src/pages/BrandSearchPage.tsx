import { useState, useCallback, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { MainLayout } from "@/components/layout/MainLayout";
import { SearchBar } from "@/components/brand/SearchBar";
import { cn } from "@/lib/utils";
import { CheckCircle, BarChart3, Users, Settings, Play } from "lucide-react";

interface Brand {
  id: string;
  name: string;
  domain: string;
  logo_url: string;
}

// Mock data for brands
const mockBrands: Brand[] = [
  {
    id: "1",
    name: "Nike",
    domain: "nike.com",
    logo_url: "https://placehold.co/100x100?text=Nike"
  },
  {
    id: "2",
    name: "Nike Air Jordan",
    domain: "jordan.nike.com",
    logo_url: "https://placehold.co/100x100?text=AJ"
  },
  {
    id: "3",
    name: "Nike Inc.",
    domain: "about.nike.com",
    logo_url: "https://placehold.co/100x100?text=Nike+Inc"
  },
  {
    id: "4",
    name: "Adidas",
    domain: "adidas.com",
    logo_url: "https://placehold.co/100x100?text=Adidas"
  },
  {
    id: "5",
    name: "TechPulse",
    domain: "techpulse.io",
    logo_url: "https://placehold.co/100x100?text=TP"
  },
  {
    id: "6",
    name: "EcoSmart",
    domain: "ecosmart.com",
    logo_url: "https://placehold.co/100x100?text=Eco"
  }
];

const steps = [
  {
    label: "Verify Brand Details",
    icon: <CheckCircle className="h-4 w-4 text-green-300" />,
    bg: "bg-green-900/80"
  },
  {
    label: "Select Topics",
    icon: <BarChart3 className="h-4 w-4 text-blue-300" />,
    bg: "bg-blue-900/80"
  },
  {
    label: "Define Personas",
    icon: <Users className="h-4 w-4 text-purple-300" />,
    bg: "bg-purple-900/80"
  },
  {
    label: "Customize Questions",
    icon: <Settings className="h-4 w-4 text-orange-300" />,
    bg: "bg-orange-900/80"
  },
  {
    label: "Review & Launch",
    icon: <Play className="h-4 w-4 text-emerald-300" />,
    bg: "bg-emerald-900/80"
  }
];

const BrandSearchPage = () => {
  const navigate = useNavigate();
  const [selectedBrand, setSelectedBrand] = useState<Brand | null>(null);
  const [animateGrid, setAnimateGrid] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  // Just set the selected brand, don't navigate yet
  const handleSelectBrand = useCallback((brand: Brand | null) => {
    setSelectedBrand(brand);
  }, []);

  // Handle "Go" button click - this is when we process and navigate
  const handleGoClick = useCallback(async () => {
    if (!selectedBrand || isProcessing) return;

    setIsProcessing(true);
    
    try {
      // 1. Insert brand
      const insertResponse = await fetch("/api/brands/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          brand_name: selectedBrand.name,
          domain: selectedBrand.domain,
        }),
      });
      const insertResult = await insertResponse.json();
      if (!insertResponse.ok) {
        alert("Failed to save brand: " + (insertResult.detail || "Unknown error"));
        return;
      }

      // Extract brand_id from insertion result
      const brandId = insertResult.data?.brand_id;
      if (!brandId) {
        alert("Failed to get brand ID from database");
        return;
      }

      // 2. Call OpenAI API via backend /analyze endpoint
      const analyzeResponse = await fetch("/api/brands/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          brand_name: selectedBrand.name,
          domain: selectedBrand.domain,
        }),
      });
      const analyzeResult = await analyzeResponse.json();
      if (!analyzeResponse.ok) {
        alert("Failed to get brand info: " + (analyzeResult.detail || "Unknown error"));
        return;
      }

      // 3. Parse the results
      const { description, product } = analyzeResult;

      // 4. Update DB with description and product
      const updateResponse = await fetch("/api/brands/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          brand_name: selectedBrand.name,
          brand_description: description,
          product,
        }),
      });
      const updateResult = await updateResponse.json();
      if (!updateResponse.ok) {
        alert("Failed to update brand/product: " + (updateResult.detail || "Unknown error"));
        return;
      }

      // 5. Navigate to setup page with all the data
      navigate("/setup", { 
        state: { 
          selectedBrand: {
            ...selectedBrand,
            brand_id: brandId
          }, 
          description, 
          product 
        } 
      });
    } catch (error) {
      console.error("Error processing brand:", error);
      alert("An error occurred while processing the brand. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  }, [navigate, selectedBrand, isProcessing]);

  // Animation trigger for grid
  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimateGrid(true);
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  // Check for reduced motion preference
  const prefersReducedMotion = typeof window !== 'undefined' && 
    window.matchMedia && 
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto min-h-[calc(100vh-6rem)] flex flex-col justify-center items-center px-4 relative">
        {/* Grid background - ultra-subtle */}
        <div className="absolute inset-0 grid grid-cols-12 grid-rows-12 pointer-events-none">
          {Array.from({length: 144}).map((_, i) => (
            <div 
              key={i} 
              className={cn(
                "border border-accent/5 opacity-0 transition-opacity duration-500", 
                animateGrid && !prefersReducedMotion && "opacity-8"
              )} 
              style={{
                transitionDelay: `${Math.random() * 1000}ms`
              }} 
            />
          ))}
        </div>

        {/* Welcome Section */}
        <div className="w-full flex flex-col items-center mt-12 mb-8 z-10">
          <h1 className="font-heading text-4xl font-bold mb-4 text-white tracking-tight text-center">
            Welcome to TunnelGrid Brand Audit!
          </h1>
          <p className="text-lg text-muted-foreground mb-10 text-center">
            Track your brand visibility across AI systems with our guided setup process.
          </p>

          {/* Steps Row */}
          <div className="w-full flex flex-row items-center justify-center gap-0 mb-12 relative">
            {steps.map((step, idx) => (
              <div key={step.label} className="flex flex-col items-center flex-1 min-w-[120px]">
                <div className={cn(
                  "rounded-xl flex items-center justify-center w-16 h-16 mb-3 shadow-sm",
                  step.bg
                )}>
                  {step.icon}
                </div>
                <span className="text-sm text-white font-medium text-center mb-2 min-h-[40px]">
                  {step.label}
                </span>
                {/* Connecting line except after last step */}
                {idx < steps.length - 1 && (
                  <div className="absolute top-1/2 left-full w-[calc(100%/5-64px)] h-0.5 bg-white/10 z-0" style={{marginLeft: 0, marginRight: 0}}></div>
                )}
              </div>
            ))}
          </div>

          {/* Ready to get started card */}
          <div className="w-full max-w-xl mx-auto bg-[#232b36] border border-border/30 rounded-2xl shadow-lg px-8 py-10 flex flex-col items-center mb-4">
            <h2 className="text-2xl font-bold text-white mb-2 text-center">Ready to get started?</h2>
            <p className="text-base text-muted-foreground mb-6 text-center">Search for your brand to begin the audit</p>
            <div className="w-full flex flex-col items-center">
              <div className="w-full">
                <SearchBar 
                  selectedBrand={selectedBrand}
                  onSelectBrand={handleSelectBrand}
                  onGoClick={handleGoClick}
                  isProcessing={isProcessing}
                />
              </div>
              {selectedBrand && (
                <div className="mt-4 text-center">
                  <p className="text-sm text-green-400">
                    ✓ Selected: <span className="font-medium">{selectedBrand.name}</span>
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Click "Go" to begin the audit
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default BrandSearchPage;
