
import React from "react";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

interface CTASectionProps {
  onAuthClick: (tab: "login" | "book") => void;
}

export const CTASection = ({ onAuthClick }: CTASectionProps) => {
  return (
    <section className="py-16 md:py-20 bg-accent text-primary-foreground relative overflow-hidden">
      {/* Top section divider */}
      <div className="section-divider bg-charcoal before:from-charcoal before:to-accent absolute top-0 left-0 w-full"></div>
      
      {/* Background animated elements */}
      <div className="absolute inset-0 overflow-hidden z-0">
        <div className="blob absolute -right-64 -top-64 w-96 h-96 bg-white/5 rounded-full"></div>
        <div className="blob absolute -left-32 -bottom-32 w-64 h-64 bg-white/5 rounded-full" style={{animationDelay: '2s'}}></div>
      </div>
      
      <div className="container mx-auto px-4 text-center relative z-10">
        <div className="max-w-3xl mx-auto space-y-6 scroll-fade-in">
          <h2 className="text-3xl md:text-4xl font-mono font-bold">Ready to map your brand's AI network?</h2>
          <p className="text-xl">
            Join the 250+ companies already gaining an advantage with TunnelGrid.ai
          </p>
          <div className="pt-4 scroll-fade-in" data-delay="200">
            <Button 
              size="lg" 
              className="bg-primary-foreground text-accent hover:bg-primary-foreground/90 font-mono hover-scale"
              onClick={() => onAuthClick("book")}
            >
              Book Your Demo
              <ArrowRight className="h-4 w-4 ml-2 transition-transform duration-300 group-hover:translate-x-1" />
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};
