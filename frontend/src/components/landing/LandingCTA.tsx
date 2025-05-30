
import React from "react";
import { Button } from "@/components/ui/button";

export const LandingCTA = () => {
  return (
    <section className="bg-accent text-accent-foreground py-16 md:py-20">
      <div className="container mx-auto px-4 md:px-6 text-center">
        <div className="max-w-3xl mx-auto space-y-6">
          <h2 className="text-3xl md:text-4xl font-bold">Ready to see your brand through AI's eyes?</h2>
          <p className="text-lg text-accent-foreground/90">
            Join the 250+ companies already gaining an advantage with Rabbit Hole Analytics.
          </p>
          <div className="pt-4">
            <Button size="lg" className="rounded-full bg-white text-accent hover:bg-white/90">
              Book Your Demo
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};
