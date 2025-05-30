import React from "react";
import { Button } from "@/components/ui/button";
import { Play, ChevronDown } from "lucide-react";
interface HeroSectionProps {
  onAuthClick: (tab: "login" | "book") => void;
}
export const HeroSection = ({
  onAuthClick
}: HeroSectionProps) => {
  return <section id="hero" className="relative min-h-screen flex items-center pt-16 overflow-hidden">
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-b from-charcoal via-navy/90 to-charcoal/90"></div>
        {/* Background grid network animation */}
        <div className="absolute inset-0 opacity-20">
          <svg width="100%" height="100%" viewBox="0 0 800 800" xmlns="http://www.w3.org/2000/svg">
            <g className="citation-bloom">
              <circle className="dot" cx="400" cy="400" r="8" fill="#3BFFD3" />
              <circle className="dot" cx="320" cy="300" r="6" fill="#3BFFD3" />
              <circle className="dot" cx="480" cy="320" r="6" fill="#3BFFD3" />
              <circle className="dot" cx="520" cy="450" r="5" fill="#3BFFD3" />
              <circle className="dot" cx="280" cy="460" r="5" fill="#3BFFD3" />
              <circle className="dot" cx="350" cy="500" r="5" fill="#3BFFD3" />
              <circle className="dot" cx="450" cy="510" r="5" fill="#3BFFD3" />
              <line className="line" x1="400" y1="400" x2="320" y2="300" stroke="#3BFFD3" strokeWidth="1" />
              <line className="line" x1="400" y1="400" x2="480" y2="320" stroke="#3BFFD3" strokeWidth="1" />
              <line className="line" x1="400" y1="400" x2="520" y2="450" stroke="#3BFFD3" strokeWidth="1" />
              <line className="line" x1="400" y1="400" x2="280" y2="460" stroke="#3BFFD3" strokeWidth="1" />
              <line className="line" x1="400" y1="400" x2="350" y2="500" stroke="#3BFFD3" strokeWidth="1" />
              <line className="line" x1="400" y1="400" x2="450" y2="510" stroke="#3BFFD3" strokeWidth="1" />
            </g>
          </svg>
        </div>
      </div>
      
      <div className="container mx-auto px-4 py-20 md:py-32 relative z-10">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div className="space-y-8 animate-fade-in">
            <div className="space-y-6">
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-mono font-bold leading-tight tracking-tight">
                Map the hidden <br /> 
                <span className="text-accent">network of AI search.</span>
              </h1>
              <p className="text-xl text-foreground/80 max-w-lg">
                TunnelGrid.ai maps the hidden network of AI answers so brands can turn mystery into measurable strategy.
              </p>
            </div>

            <div className="flex flex-wrap gap-4">
              <Button size="lg" className="bg-accent hover:bg-accent/90 text-primary-foreground font-mono" onClick={() => onAuthClick("book")}>
                Book a meeting
              </Button>
              <Button size="lg" variant="link" className="text-foreground/90 hover:text-accent flex items-center gap-2">
                <Play className="h-4 w-4" />
                Watch 90-sec demo
              </Button>
            </div>
          </div>

          <div className="relative hidden md:block">
            <div className="animate-float shadow-2xl rounded-xl overflow-hidden border border-white/10 backdrop-blur-sm">
              
            </div>
            <div className="absolute -bottom-6 -right-6 p-4 bg-accent/10 backdrop-blur-md border border-accent/30 rounded-lg">
              <p className="text-accent font-mono text-sm">
                <span className="font-bold">73%</span> of users now find brands through AI search
              </p>
            </div>
          </div>
        </div>
        
        {/* Scroll indicator */}
        <div className="absolute bottom-10 left-1/2 transform -translate-x-1/2 animate-bounce">
          <a href="#how-it-works" className="flex flex-col items-center text-foreground/50 hover:text-accent">
            <span className="text-xs mb-2 font-mono">Scroll</span>
            <ChevronDown className="h-6 w-6" />
          </a>
        </div>
      </div>
    </section>;
};