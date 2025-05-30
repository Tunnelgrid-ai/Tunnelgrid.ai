
import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { QuoteIcon } from "lucide-react";

interface LandingTestimonialProps {
  quote: string;
  author: string;
  role: string;
  company: string;
}

export const LandingTestimonial = ({
  quote,
  author,
  role,
  company,
}: LandingTestimonialProps) => {
  return (
    <Card className="h-full border-none shadow-md hover:shadow-lg transition-shadow">
      <CardContent className="p-6 flex flex-col h-full">
        <div className="mb-4 text-accent">
          <QuoteIcon className="h-6 w-6" />
        </div>
        <p className="text-lg mb-6 flex-grow">{quote}</p>
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center">
            {author.charAt(0)}
          </div>
          <div>
            <div className="font-medium">{author}</div>
            <div className="text-sm text-muted-foreground">
              {role}, {company}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
