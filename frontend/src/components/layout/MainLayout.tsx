import { Toaster } from "@/components/ui/toaster";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Menu, LogOut } from "lucide-react";
import { cn } from "@/lib/utils";
import { SidebarProvider, SidebarTrigger, SidebarInset } from "@/components/ui/sidebar";
import { AppSidebar } from "./AppSidebar";
import { useIsMobile } from "@/hooks/use-mobile";
import { useAuth } from "@/contexts/AuthContext";
import { Navigate } from "react-router-dom";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

interface MainLayoutProps {
  children: React.ReactNode;
  fullWidth?: boolean;
  requireAuth?: boolean;
}

export const MainLayout = ({
  children,
  fullWidth = false,
  requireAuth = true
}: MainLayoutProps) => {
  const isMobile = useIsMobile();
  const {
    user,
    loading,
    signOut
  } = useAuth();

  // DEVELOPMENT MODE: Authentication check is disabled for development
  // For production: Change DEVELOPMENT_MODE to false to restore authentication
  const DEVELOPMENT_MODE = true;
  
  if (requireAuth && !loading && !user && !DEVELOPMENT_MODE) {
    return <Navigate to="/auth" replace />;
  }
  
  return (
    <SidebarProvider defaultOpen={!isMobile}>
      <div className="flex min-h-screen w-full bg-background">
        <AppSidebar />
        <SidebarInset className={cn("px-4 py-6 md:px-8", fullWidth ? "max-w-none" : "max-w-7xl mx-auto")}>
          <header className="flex items-center justify-between mb-6">
            <SidebarTrigger className="md:hidden" />
            
            {user && (
              <div className="ml-auto flex items-center gap-2">
                <Avatar className="h-8 w-8">
                  <AvatarFallback>U</AvatarFallback>
                </Avatar>
                <Button variant="ghost" size="sm" onClick={() => signOut()}>
                  <LogOut className="h-4 w-4 mr-2" />
                  Logout
                </Button>
              </div>
            )}
          </header>
          <main>{children}</main>
        </SidebarInset>
      </div>
      <Toaster />
    </SidebarProvider>
  );
};
