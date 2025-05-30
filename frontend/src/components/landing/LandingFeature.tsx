
import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";

interface LandingFeatureProps {
  icon: LucideIcon;
  title: string;
  description: string;
}

export const LandingFeature = ({ icon: Icon, title, description }: LandingFeatureProps) => {
  return (
    <Card className="border-none shadow-md hover:shadow-lg transition-shadow">
      <CardContent className="p-6 space-y-4">
        <div className="w-12 h-12 rounded-full bg-accent/20 text-accent flex items-center justify-center">
          <Icon className="h-6 w-6" />
        </div>
        <h3 className="text-xl font-semibold">{title}</h3>
        <p className="text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
};
