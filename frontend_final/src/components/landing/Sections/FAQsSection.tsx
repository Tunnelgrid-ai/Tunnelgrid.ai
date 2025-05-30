
import React from "react";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

interface FAQsSectionProps {
  onAuthClick: (tab: "login" | "book") => void;
}

export const FAQsSection = ({ onAuthClick }: FAQsSectionProps) => {
  // FAQ data
  const faqs = [
    {
      question: "What's the difference between LLM monitoring and AI Search monitoring?",
      answer: "LLM monitoring typically tracks interactions with a specific model like ChatGPT. Our AI Search monitoring provides a comprehensive view across multiple AI search experiences including ChatGPT, Copilot, Google AI Overviews, and Perplexity, showing how your brand appears in each context with actionable insights to improve visibility."
    },
    {
      question: "How do your results differ from manual searches in AI tools?",
      answer: "Manual searches are subject to personal search history, location bias, and inconsistent prompting. Our platform uses standardized, controlled prompts across multiple models to provide reliable, reproducible results that accurately represent how AI systems perceive your brand, eliminating variables that can skew manual testing."
    },
    {
      question: "How often is the data refreshed?",
      answer: "Our platform automatically refreshes your brand's AI visibility data weekly to track changes over time. Premium plans offer daily refreshes, and all customers can trigger manual refreshes after implementing recommendations to see immediate impact."
    },
    {
      question: "How do you handle data privacy and confidentiality?",
      answer: "We prioritize data security and privacy. All brand audits are conducted using isolated instances to prevent cross-contamination. Your competitive intelligence and brand data are encrypted, access-controlled, and never shared with third parties or used to train AI models."
    }
  ];

  return (
    <section id="faqs" className="py-20 md:py-24 bg-charcoal relative">
      <div className="container mx-auto px-4">
        <div className="text-center max-w-3xl mx-auto mb-12 scroll-fade-in">
          <h2 className="text-3xl md:text-4xl font-mono font-bold mb-4">Frequently Asked Questions</h2>
        </div>
        
        <div className="max-w-3xl mx-auto mt-8 scroll-fade-in">
          <Accordion type="single" collapsible className="w-full">
            {faqs.map((faq, index) => (
              <AccordionItem 
                key={index} 
                value={`item-${index}`} 
                className="border-muted scroll-fade-in" 
                data-delay={index * 100}
              >
                <AccordionTrigger className="text-lg font-mono font-medium hover:text-accent py-5 text-left transition-all duration-300">
                  {faq.question}
                </AccordionTrigger>
                <AccordionContent className="text-foreground/70 animate-fade-in">
                  {faq.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
        
        <div className="mt-12 text-center scroll-fade-in" data-delay="400">
          <Button 
            className="bg-accent hover:bg-accent/90 text-primary-foreground font-mono hover-scale"
            onClick={() => onAuthClick("book")}
          >
            Book a meeting
            <ArrowRight className="h-4 w-4 ml-2 transition-transform duration-300 group-hover:translate-x-1" />
          </Button>
        </div>
      </div>
    </section>
  );
};
