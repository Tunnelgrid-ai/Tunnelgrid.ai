
import React from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ArrowRight, LineChart, Shield, Zap } from "lucide-react";

interface BenefitsSectionProps {
  onAuthClick: (tab: "login" | "book") => void;
}

export const BenefitsSection = ({ onAuthClick }: BenefitsSectionProps) => {
  // Benefits data
  const benefits = [
    {
      icon: <LineChart className="h-8 w-8 text-accent" />,
      title: "AI Visibility Mapping",
      description: "Map your brand's presence across all major AI models in one dashboard with a visual grid of connections."
    },
    {
      icon: <Shield className="h-8 w-8 text-accent" />,
      title: "Citation Intelligence",
      description: "Identify which sources AI models rely on when discussing your brand and optimize those critical pathways."
    },
    {
      icon: <Zap className="h-8 w-8 text-accent" />,
      title: "Strategic Orchestration",
      description: "Follow prioritized recommendations to shift from reacting to actively orchestrating your AI narratives."
    }
  ];

  return (
    <section id="benefits" className="py-20 md:py-24 bg-charcoal relative">
      <div className="container mx-auto px-4">
        <div className="text-center max-w-3xl mx-auto mb-12 scroll-fade-in">
          <h2 className="text-3xl md:text-4xl font-mono font-bold mb-4">Turn Mystery Into Strategy</h2>
          <p className="text-lg text-foreground/80">
            Don't leave your brand's AI presence to chance. Our platform helps you take control.
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8 mt-12">
          {benefits.map((benefit, index) => (
            <Card key={index} className={`bg-darkgray enhanced-card scroll-fade-in`} data-delay={index * 150}>
              <CardContent className="p-8 flex flex-col h-full">
                <div className="mb-6 transform transition-transform duration-500 group-hover:scale-110">{benefit.icon}</div>
                <h3 className="text-xl font-mono font-bold mb-3">{benefit.title}</h3>
                <p className="text-foreground/70 flex-grow">{benefit.description}</p>
                <div className="mt-6 transition-transform duration-300 hover:translate-x-1">
                  <Button variant="link" className="p-0 text-accent hover:text-accent/80 font-mono group">
                    Learn more
                    <ArrowRight className="h-4 w-4 ml-2 transition-transform duration-300 group-hover:translate-x-1" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};
