
import React, { useState, useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import { AuthDialog } from "@/components/landing/AuthDialog";
import { HeroSection } from "@/components/landing/Sections/HeroSection";
import { HeaderSection } from "@/components/landing/Sections/HeaderSection";
import { HowItWorksSection } from "@/components/landing/Sections/HowItWorksSection";
import { BenefitsSection } from "@/components/landing/Sections/BenefitsSection";
import { ScreenshotSection } from "@/components/landing/Sections/ScreenshotSection";
import { FAQsSection } from "@/components/landing/Sections/FAQsSection";
import { CTASection } from "@/components/landing/Sections/CTASection";
import { FooterSection } from "@/components/landing/Sections/FooterSection";
import { ScrollAnimationScript } from "@/components/landing/Sections/ScrollAnimationScript";

export default function Index() {
  const location = useLocation();
  const [authDialogOpen, setAuthDialogOpen] = useState(false);
  const [authDialogTab, setAuthDialogTab] = useState<"login" | "book">("book");
  const [isHeaderSticky, setIsHeaderSticky] = useState(false);
  const [activeSectionId, setActiveSectionId] = useState("");
  
  // Refs for scroll animations
  const howItWorksRef = useRef<HTMLDivElement>(null);
  const benefitsRef = useRef<HTMLDivElement>(null);
  const screenshotRef = useRef<HTMLDivElement>(null);
  const faqsRef = useRef<HTMLDivElement>(null);
  
  // Check for auth dialog state from navigation
  useEffect(() => {
    if (location.state && location.state.openAuthDialog) {
      setAuthDialogTab(location.state.authTab || "login");
      setAuthDialogOpen(true);
      
      // Clear the state so it doesn't reopen on page refresh
      window.history.replaceState({}, document.title);
    }
  }, [location.state]);
  
  // Handle sticky header
  useEffect(() => {
    const handleScroll = () => {
      setIsHeaderSticky(window.scrollY > 50);
      
      // Handle active section for navigation
      const sections = [
        { id: "hero", ref: null },
        { id: "how-it-works", ref: howItWorksRef },
        { id: "benefits", ref: benefitsRef },
        { id: "screenshot", ref: screenshotRef },
        { id: "faqs", ref: faqsRef }
      ];
      
      let currentSection = "";
      sections.forEach(section => {
        if (section.ref && section.ref.current) {
          const rect = section.ref.current.getBoundingClientRect();
          if (rect.top <= 100 && rect.bottom >= 100) {
            currentSection = section.id;
          }
        }
      });
      
      if (currentSection) {
        setActiveSectionId(currentSection);
      } else if (window.scrollY < 100) {
        setActiveSectionId("hero");
      }

      // Trigger scroll animations
      document.querySelectorAll('.scroll-fade-in').forEach(el => {
        const rect = el.getBoundingClientRect();
        const isVisible = (
          rect.top <= (window.innerHeight || document.documentElement.clientHeight) * 0.85 &&
          rect.bottom >= 0
        );
        
        if (isVisible) {
          el.classList.add('visible');
        }
      });
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);
  
  // Handle citation bloom animation
  useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('active');
        } else {
          entry.target.classList.remove('active');
        }
      });
    }, { threshold: 0.3 });
    
    const citationBloom = document.querySelector('.citation-bloom');
    if (citationBloom) {
      observer.observe(citationBloom);
    }
    
    return () => {
      if (citationBloom) {
        observer.unobserve(citationBloom);
      }
    };
  }, []);
  
  const handleAuthClick = (tab: "login" | "book") => {
    setAuthDialogTab(tab);
    setAuthDialogOpen(true);
  };

  return (
    <div className="flex flex-col min-h-screen bg-charcoal text-foreground">
      {/* Header */}
      <HeaderSection 
        isHeaderSticky={isHeaderSticky} 
        activeSectionId={activeSectionId} 
        onAuthClick={handleAuthClick} 
      />

      <main className="flex-1">
        {/* Hero Section */}
        <HeroSection onAuthClick={handleAuthClick} />

        {/* How It Works Section */}
        <div ref={howItWorksRef}>
          <HowItWorksSection onAuthClick={handleAuthClick} />
        </div>
        
        {/* Benefits Section */}
        <div ref={benefitsRef}>
          <BenefitsSection onAuthClick={handleAuthClick} />
        </div>

        {/* Screenshot Demo Section */}
        <div ref={screenshotRef}>
          <ScreenshotSection onAuthClick={handleAuthClick} />
        </div>
        
        {/* FAQs Section */}
        <div ref={faqsRef}>
          <FAQsSection onAuthClick={handleAuthClick} />
        </div>

        {/* CTA Section */}
        <CTASection onAuthClick={handleAuthClick} />
      </main>

      <FooterSection />

      {/* Book meeting dialog */}
      <AuthDialog 
        isOpen={authDialogOpen}
        onOpenChange={setAuthDialogOpen}
        defaultTab={authDialogTab}
      />
      
      {/* Add client-side JS for animations */}
      <ScrollAnimationScript />
    </div>
  );
}
