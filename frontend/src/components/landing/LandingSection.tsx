
import React from "react";
import { cn } from "@/lib/utils";

interface LandingSectionProps {
  title?: string;
  description?: string;
  className?: string;
  children: React.ReactNode;
}

export const LandingSection = ({
  title,
  description,
  className,
  children
}: LandingSectionProps) => {
  return (
    <section className={cn("py-16 md:py-24", className)}>
      <div className="container mx-auto px-4 md:px-6">
        {(title || description) && (
          <div className="text-center max-w-3xl mx-auto mb-12">
            {title && <h2 className="text-3xl md:text-4xl font-bold mb-4">{title}</h2>}
            {description && <p className="text-lg text-muted-foreground">{description}</p>}
          </div>
        )}
        {children}
      </div>
    </section>
  );
};
