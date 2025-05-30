
import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Play } from "lucide-react";
import { Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { AuthDialog } from "./AuthDialog";

export function LandingHero() {
  const {
    user,
    signOut
  } = useAuth();
  const [authDialogOpen, setAuthDialogOpen] = useState(false);
  const [authTab, setAuthTab] = useState<"login" | "book">("book");
  
  const handleAuthClick = (tab: "login" | "book") => {
    setAuthTab(tab);
    setAuthDialogOpen(true);
  };

  return <div className="relative bg-primary text-primary-foreground overflow-hidden">
      {/* Header Navigation */}
      <header className="container mx-auto px-4 py-4 flex items-center justify-between">
        {/* Logo on the left */}
        <div className="flex items-center">
          <Link to="/" className="flex items-center gap-2">
            <img src="/logo.png" alt="TunnelGrid.ai Logo" className="w-8 h-8" />
            <span className="font-bold text-xl">TunnelGrid.ai</span>
          </Link>
        </div>

        {/* Navigation links in center */}
        <nav className="hidden md:flex items-center space-x-6">
          <a href="#features" className="text-primary-foreground/90 hover:text-primary-foreground transition-colors">
            How it Works
          </a>
          <a href="#testimonials" className="text-primary-foreground/90 hover:text-primary-foreground transition-colors">
            Testimonials
          </a>
          <Link to="/blog" className="text-primary-foreground/90 hover:text-primary-foreground transition-colors">
            Blog
          </Link>
        </nav>

        {/* Buttons on the right */}
        <div className="flex items-center space-x-4">
          {user ? <>
              <Link to="/reports">
                <Button variant="outline" className="border-white/20 text-white bg-slate-900 hover:bg-slate-800">
                  Dashboard
                </Button>
              </Link>
              <Button onClick={() => signOut()} variant="outline" className="border-white/20 text-white bg-slate-900 hover:bg-slate-800">
                Log Out
              </Button>
            </> : <>
              <Button variant="outline" className="border-white/20 text-white bg-slate-900 hover:bg-slate-800" onClick={() => handleAuthClick("login")}>
                Login
              </Button>
              <Button className="bg-accent hover:bg-accent/90 text-accent-foreground rounded-full" onClick={() => handleAuthClick("book")}>Book a meeting</Button>
            </>}
        </div>
      </header>

      {/* Main hero content */}
      <div className="container mx-auto px-4 py-20 md:py-32">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <div className="space-y-4">
              <h1 className="text-4xl md:text-5xl font-bold tracking-tight lg:text-7xl">
                Map the <span className="gradient-text">hidden network</span> <br /> of AI search.
              </h1>
              <p className="text-xl text-primary-foreground/90 max-w-lg">
                TunnelGrid.ai maps the hidden network of AI answers so brands can turn mystery into measurable strategy.
              </p>
            </div>

            <div className="flex flex-wrap gap-4">
              <Button size="lg" className="rounded-full bg-accent hover:bg-accent/90 text-accent-foreground" onClick={() => handleAuthClick("book")}>Book a meeting</Button>
              <Button size="lg" variant="link" className="text-primary-foreground flex items-center gap-2">
                <Play className="h-4 w-4" />
                Watch 90-sec video
              </Button>
            </div>
          </div>

          <div className="relative">
            <div className="animate-float shadow-2xl rounded-xl overflow-hidden border border-white/20">
              <img src="/placeholder.svg" alt="TunnelGrid.ai Dashboard" className="w-full h-auto" />
            </div>
            <div className="absolute -bottom-6 -right-6 p-4 bg-accent/10 backdrop-blur-md border border-accent/30 rounded-lg">
              <p className="text-accent font-mono text-sm">
                <span className="font-bold">73%</span> of users now find brands through AI search
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Auth Dialog */}
      <AuthDialog isOpen={authDialogOpen} onOpenChange={setAuthDialogOpen} defaultTab={authTab} />
    </div>;
}
