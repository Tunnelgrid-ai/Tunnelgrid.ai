
import { 
  Home, 
  Search,
  BarChart2,
  Settings,
  AlertTriangle,
  FileText,
  Info
} from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

export const SidebarNav = () => {
  const location = useLocation();
  
  const navItems = [
    { name: "Dashboard", icon: Home, path: "/" },
    { name: "Brand Audit", icon: Search, path: "/audit" },
    { name: "Sandbox", icon: FileText, path: "/sandbox" },
    { name: "Monitoring", icon: AlertTriangle, path: "/monitoring" },
    { name: "Analytics", icon: BarChart2, path: "/analytics" },
    { name: "Settings", icon: Settings, path: "/settings" },
  ];

  return (
    <div className="space-y-4 py-4">
      <div className="px-3 py-2">
        <div className="mb-8 px-2">
          <Link to="/" className="flex items-center">
            <h2 className="text-2xl font-bold text-white">BrandAI</h2>
            <span className="ml-1 text-xs text-white/70">Oracle</span>
          </Link>
        </div>
        <div className="space-y-1">
          {navItems.map((item) => (
            <Button
              key={item.path}
              variant={location.pathname === item.path ? "secondary" : "ghost"}
              className={cn(
                "w-full justify-start",
                location.pathname === item.path
                  ? "bg-sidebar-accent text-sidebar-accent-foreground"
                  : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
              )}
              asChild
            >
              <Link to={item.path}>
                <item.icon className="mr-2 h-4 w-4" />
                {item.name}
              </Link>
            </Button>
          ))}
        </div>
      </div>
      <div className="px-3 py-2">
        <div className="space-y-1">
          <Button
            variant="ghost"
            className="w-full justify-start text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
            asChild
          >
            <Link to="/help">
              <Info className="mr-2 h-4 w-4" />
              Help & Resources
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
};
