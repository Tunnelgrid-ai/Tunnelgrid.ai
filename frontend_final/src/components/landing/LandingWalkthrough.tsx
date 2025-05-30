
import React from "react";
import { Card, CardContent } from "@/components/ui/card";

export const LandingWalkthrough = () => {
  return (
    <section className="py-16 md:py-24 bg-white">
      <div className="container mx-auto px-4 md:px-6">
        <div className="text-center mb-12 max-w-3xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">See How It Works</h2>
          <p className="text-lg text-muted-foreground">
            Discover how Rabbit Hole Analytics gives you unparalleled visibility into AI's perception of your brand
          </p>
        </div>

        <div className="relative">
          <div className="grid md:grid-cols-3 gap-8 md:gap-4 relative z-10">
            <Card className="shadow-lg md:translate-y-8 animate-fade-in">
              <CardContent className="p-6">
                <div className="aspect-video bg-muted rounded-md mb-4 overflow-hidden">
                  <img 
                    src="/placeholder.svg" 
                    alt="AI Visibility Score Dashboard" 
                    className="w-full h-full object-cover"
                  />
                </div>
                <h3 className="text-xl font-semibold mb-2">1. Measure Your AI Score</h3>
                <p className="text-muted-foreground">
                  Get your proprietary AI Visibility + Influence Score (0-100) across all major AI models.
                </p>
              </CardContent>
            </Card>

            <Card className="shadow-lg md:translate-y-0 animate-fade-in [animation-delay:200ms]">
              <CardContent className="p-6">
                <div className="aspect-video bg-muted rounded-md mb-4 overflow-hidden">
                  <img 
                    src="/placeholder.svg" 
                    alt="Multi-model Sentiment Analysis" 
                    className="w-full h-full object-cover"
                  />
                </div>
                <h3 className="text-xl font-semibold mb-2">2. Analyze Perception</h3>
                <p className="text-muted-foreground">
                  See side-by-side comparisons of how different AI models represent your brand and products.
                </p>
              </CardContent>
            </Card>

            <Card className="shadow-lg md:translate-y-8 animate-fade-in [animation-delay:400ms]">
              <CardContent className="p-6">
                <div className="aspect-video bg-muted rounded-md mb-4 overflow-hidden">
                  <img 
                    src="/placeholder.svg" 
                    alt="Action Plan Generator" 
                    className="w-full h-full object-cover"
                  />
                </div>
                <h3 className="text-xl font-semibold mb-2">3. Implement Fixes</h3>
                <p className="text-muted-foreground">
                  Follow your personalized action plan to improve AI visibility and correct misrepresentations.
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="absolute top-1/2 left-0 w-full h-0.5 bg-accent/30 -translate-y-1/2 hidden md:block"></div>
        </div>
      </div>
    </section>
  );
};
