
import React from "react";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

interface HowItWorksSectionProps {
  onAuthClick: (tab: "login" | "book") => void;
}

export const HowItWorksSection = ({ onAuthClick }: HowItWorksSectionProps) => {
  // How it works steps data - Updated to follow the Narrative Arc
  const howItWorksSteps = [
    {
      icon: <div className="w-12 h-12 rounded-full bg-muted text-accent flex items-center justify-center">1</div>,
      title: "The Maze",
      description: "AI search results feel random; brands can't see how or why they appear in responses"
    },
    {
      icon: <div className="w-12 h-12 rounded-full bg-muted text-accent flex items-center justify-center">2</div>,
      title: "The Descent",
      description: "TunnelGrid.ai drills into multiple AI models, capturing every answer, citation, and nuance"
    },
    {
      icon: <div className="w-12 h-12 rounded-full bg-muted text-accent flex items-center justify-center">3</div>,
      title: "The Grid",
      description: "Raw chaos turns into a visual grid: nodes = sources, lines = influence pathways"
    },
    {
      icon: <div className="w-12 h-12 rounded-full bg-muted text-accent flex items-center justify-center">4</div>,
      title: "The Control Room",
      description: "Shift from reaction to orchestration—optimizing content and steering AI narratives"
    }
  ];

  return (
    <section id="how-it-works" className="py-20 md:py-24 bg-navy relative">
      {/* Top section divider */}
      <div className="section-divider bg-charcoal before:from-charcoal before:to-navy absolute top-0 left-0 w-full"></div>
      
      <div className="container mx-auto px-4">
        <div className="text-center max-w-3xl mx-auto mb-12 scroll-fade-in">
          <h2 className="text-3xl md:text-4xl font-mono font-bold mb-4">From Maze to Control Room</h2>
          <p className="text-lg text-foreground/80">Our platform gives you unprecedented visibility into how AI models perceive and present your brand.</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mt-12">
          {howItWorksSteps.map((step, index) => (
            <div key={index} className={`scroll-fade-in stagger-${index + 1}`} data-delay={index * 100}>
              <div className="flex flex-col items-center text-center space-y-4 p-6 bg-darkgray rounded-lg enhanced-card">
                {step.icon}
                <h3 className="text-xl font-mono font-bold">{step.title}</h3>
                <p className="text-foreground/70">{step.description}</p>
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-12 text-center scroll-fade-in" data-delay="400">
          <Button 
            className="bg-accent hover:bg-accent/90 text-primary-foreground font-mono hover-scale"
            onClick={() => onAuthClick("book")}
          >
            Map your brand today
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        </div>
      </div>
      
      {/* Bottom section divider */}
      <div className="section-divider bg-navy before:from-navy before:to-charcoal absolute bottom-0 left-0 w-full transform rotate-180"></div>
    </section>
  );
};
