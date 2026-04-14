import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { 
  LayoutDashboard, 
  ShoppingBag, 
  PlusCircle, 
  Share2,
  Sparkles,
  Network,
  Activity,
  FileSpreadsheet,
  Menu,
  X
} from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/catalogo", label: "Catálogo", icon: ShoppingBag },
  { to: "/adicionar", label: "Adicionar", icon: PlusCircle },
  { to: "/compartilhar", label: "Compartilhar", icon: Share2 },
  { to: "/recomendacoes", label: "Recomendações", icon: Sparkles },
  { to: "/grafo", label: "Grafo", icon: Network },
  { to: "/jobs", label: "Jobs", icon: Activity },
  { to: "/relatorios", label: "Relatórios", icon: FileSpreadsheet },
];

export function Header() {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-card/80 backdrop-blur-lg">
      <div className="container flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
            <span className="text-xl font-bold text-primary-foreground">A</span>
          </div>
          <span className="text-xl font-bold text-foreground">
            Afilia<span className="text-secondary">ML</span>
          </span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.to;
            return (
              <Link key={item.to} to={item.to}>
                <Button
                  variant={isActive ? "default" : "ghost"}
                  size="sm"
                  className={cn(
                    "gap-2 transition-all duration-200",
                    isActive && "shadow-md"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Button>
              </Link>
            );
          })}
        </nav>

        {/* Mobile Menu Button */}
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </Button>
      </div>

      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <nav className="md:hidden border-t border-border bg-card p-4 animate-fade-in">
          <div className="flex flex-col gap-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.to;
              return (
                <Link 
                  key={item.to} 
                  to={item.to}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <Button
                    variant={isActive ? "default" : "ghost"}
                    className="w-full justify-start gap-2"
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </Button>
                </Link>
              );
            })}
          </div>
        </nav>
      )}
    </header>
  );
}
