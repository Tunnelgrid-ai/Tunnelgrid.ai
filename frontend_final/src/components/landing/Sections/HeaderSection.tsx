
import React from "react";
import { Button } from "@/components/ui/button";

interface HeaderSectionProps {
  isHeaderSticky: boolean;
  activeSectionId: string;
  onAuthClick: (tab: "login" | "book") => void;
}

export const HeaderSection = ({
  isHeaderSticky,
  activeSectionId,
  onAuthClick
}: HeaderSectionProps) => {
  return (
    <header className={`sticky-header fixed top-0 left-0 w-full z-50 transition-all duration-300 ${isHeaderSticky ? 'scrolled' : ''}`}>
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center">
          <a href="#" className="flex items-center gap-2">
            <img src="/logo.png" alt="TunnelGrid.ai Logo" className="w-8 h-8" />
            <span className="font-mono font-bold text-xl">TunnelGrid.ai</span>
          </a>
        </div>

        {/* Navigation - only show on desktop and when scrolled on mobile */}
        <nav className={`hidden md:flex items-center space-x-6 ${isHeaderSticky ? 'flex' : ''}`}>
          <a href="#how-it-works" className={`text-foreground/80 hover:text-accent transition-colors ${activeSectionId === 'how-it-works' ? 'text-accent' : ''}`}>
            How It Works
          </a>
          <a href="#benefits" className={`text-foreground/80 hover:text-accent transition-colors ${activeSectionId === 'benefits' ? 'text-accent' : ''}`}>
            Benefits
          </a>
          <a href="#faqs" className={`text-foreground/80 hover:text-accent transition-colors ${activeSectionId === 'faqs' ? 'text-accent' : ''}`}>
            FAQs
          </a>
        </nav>

        {/* CTA buttons */}
        <div className="flex items-center space-x-4">
          <Button 
            variant="outline"
            className="border-white/20 text-white bg-slate-900 hover:bg-slate-800"
            onClick={() => onAuthClick("login")}
          >
            Login
          </Button>
          <Button 
            className="bg-accent text-primary-foreground hover:bg-accent/90"
            onClick={() => onAuthClick("book")}
          >
            Book a meeting
          </Button>
        </div>
      </div>
    </header>
  );
};
