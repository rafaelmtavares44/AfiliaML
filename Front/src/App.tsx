import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Catalogo from "./pages/Catalogo";
import AdicionarProduto from "./pages/AdicionarProduto";
import Compartilhar from "./pages/Compartilhar";
import Recomendacoes from "./pages/Recomendacoes";
import InsightsProduto from "./pages/InsightsProduto";
import GrafoVisual from "./pages/GrafoVisual";
import StatusJobs from "./pages/StatusJobs";
import Relatorios from "./pages/Relatorios";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/catalogo" element={<Catalogo />} />
          <Route path="/adicionar" element={<AdicionarProduto />} />
          <Route path="/compartilhar" element={<Compartilhar />} />
          
          {/* Phase 3 Routes */}
          <Route path="/recomendacoes" element={<Recomendacoes />} />
          <Route path="/produtos/:id/insights" element={<InsightsProduto />} />
          <Route path="/grafo" element={<GrafoVisual />} />
          <Route path="/jobs" element={<StatusJobs />} />
          <Route path="/relatorios" element={<Relatorios />} />
          
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
