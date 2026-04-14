// ============================================
// AfiliaML — Página de Recomendações
// Materia: Inteligência Artificial - Sistema de recomendação baseado em scoring.
// ============================================

import { useState } from "react";
import { Layout } from "@/components/layout/Layout";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Sparkles, TrendingDown, MousePointerClick, Brain,
  RefreshCw, ImageOff, Link as LinkIcon, CheckCircle2, Loader2
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

const API = import.meta.env.VITE_API_URL || "http://localhost:3333";

const highlightConfig: Record<string, { label: string; color: string; icon: any }> = {
  queda_de_preco: { label: "Queda de Preço", color: "bg-emerald-500", icon: TrendingDown },
  tendencia_de_cliques: { label: "Tendência", color: "bg-blue-500", icon: MousePointerClick },
  alta_relevancia_ml: { label: "Alta Relevância", color: "bg-purple-500", icon: Brain },
};

function RecommendationCard({ item }: { item: any }) {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [imgError, setImgError] = useState(false);
  const config = highlightConfig[item.highlightReason] || highlightConfig.alta_relevancia_ml;
  const Icon = config.icon;
  const score = Math.round((item.combinedScore || 0) * 100);

  // Materia: Empreendedorismo - Conversão de recomendação em venda (Link de Afiliado)
  const generateMutation = useMutation({
    mutationFn: async (productId: string) => {
      const res = await fetch(`${API}/api/affiliate-links/generate/${productId}`, { method: "POST" });
      if (!res.ok) throw new Error("Erro ao gerar link");
      return res.json();
    },
    onSuccess: () => {
      toast({ title: "✅ Link Gerado!", description: "Produto adicionado ao Cofre de Divulgação." });
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
    },
    onError: () => {
      toast({ title: "❌ Erro", description: "Não foi possível gerar o link.", variant: "destructive" });
    }
  });

  return (
    <Card className="group overflow-hidden hover:shadow-lg transition-all duration-300 border-border/40 bg-card">
      <div className="relative aspect-[4/3] overflow-hidden bg-muted">
        {item.imageUrl && !imgError ? (
          <img src={item.imageUrl} alt={item.title} referrerPolicy="no-referrer"
            onError={() => setImgError(true)}
            className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-300" />
        ) : (
          <div className="h-full w-full flex items-center justify-center"><ImageOff className="h-8 w-8 opacity-30" /></div>
        )}
        {item.highlightReason && (
          <Badge className={`absolute top-2 left-2 ${config.color} text-white text-[10px] gap-1`}>
            <Icon className="h-3 w-3" /> {config.label}
          </Badge>
        )}
        {score > 0 && (
          <Badge className="absolute top-2 right-2 bg-black/70 text-white text-[10px]">
            {score}% Match
          </Badge>
        )}
      </div>
      <CardContent className="p-3 space-y-2">
        <h3 className="text-xs font-semibold line-clamp-2 leading-tight h-8">{item.title}</h3>
        <div className="flex items-baseline gap-2">
          <span className="text-base font-bold text-primary">
            {new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(item.price || 0)}
          </span>
          {item.discountPct > 0 && (
            <Badge variant="destructive" className="text-[10px] h-4">-{item.discountPct}%</Badge>
          )}
        </div>
        <div className="space-y-1">
          <div className="flex justify-between text-[10px] text-muted-foreground uppercase font-bold">
            <span>Score Relevância</span>
            <span>{score}%</span>
          </div>
          <Progress value={score} className="h-1.5" />
        </div>
        
        {item.reasonText && (
          <p className="text-[10px] text-muted-foreground line-clamp-2 italic leading-tight">{item.reasonText}</p>
        )}

        <Button 
          variant={item.hasAffiliate ? "secondary" : "default"} 
          size="sm" 
          className="w-full text-xs gap-2 mt-1 shadow-sm"
          disabled={generateMutation.isPending || item.hasAffiliate}
          onClick={() => generateMutation.mutate(item.productId)}
        >
          {generateMutation.isPending ? (
            <Loader2 className="h-3 w-3 animate-spin" />
          ) : item.hasAffiliate ? (
            <><CheckCircle2 className="h-3 w-3 text-green-500" /> No Cofre</>
          ) : (
            <><LinkIcon className="h-3 w-3" /> Gerar Link</>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}

const RecommendationSkeleton = () => (
  <div className="grid gap-3 grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
    {[1, 2, 3, 4, 5].map((i) => (
      <Card key={i} className="overflow-hidden animate-pulse border-border/40">
        <div className="aspect-[4/3] bg-muted" />
        <CardContent className="p-3 space-y-3">
          <div className="h-3 bg-muted rounded w-3/4" />
          <div className="h-4 bg-muted rounded w-1/2" />
          <div className="h-1.5 bg-muted rounded w-full" />
          <div className="h-8 bg-muted rounded w-full" />
        </CardContent>
      </Card>
    ))}
  </div>
);

export default function Recomendacoes() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [selectedChannel, setSelectedChannel] = useState("whatsapp");
  const [selectedCampaign, setSelectedCampaign] = useState("");

  // Materia: Data Mining - Recuperação de padrões minerados do banco (Redis)
  const { data: daily = [], isLoading: loadingDaily } = useQuery({
    queryKey: ["recommendations", "daily"],
    queryFn: async () => {
      const res = await fetch(`${API}/api/recommendations/daily`);
      const d = await res.json();
      return d.data || [];
    }
  });

  const { data: channel = [], isLoading: loadingChannel } = useQuery({
    queryKey: ["recommendations", "channel", selectedChannel],
    queryFn: async () => {
      const res = await fetch(`${API}/api/recommendations/channel/${selectedChannel}`);
      const d = await res.json();
      return d.data || [];
    }
  });

  const { data: campaigns = [] } = useQuery({
    queryKey: ["campaigns"],
    queryFn: async () => {
      const res = await fetch(`${API}/api/campaigns`);
      const d = await res.json();
      return d.data || [];
    }
  });

  const { data: campaign = [], isLoading: loadingCampaign } = useQuery({
    queryKey: ["recommendations", "campaign", selectedCampaign],
    queryFn: async () => {
      if (!selectedCampaign) return [];
      const res = await fetch(`${API}/api/recommendations/campaign/${selectedCampaign}`);
      const d = await res.json();
      return d.data || [];
    },
    enabled: !!selectedCampaign
  });

  const refreshMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch(`${API}/api/recommendations/rebuild-cache`, { method: "POST" });
      if (!res.ok) throw new Error("Erro ao reconstruir cache");
      return res.json();
    },
    onSuccess: () => {
      toast({ title: "✅ Inteligência atualizada!", description: "Os scores de recomendação foram recalculados." });
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
    }
  });

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-primary" /> Recomendações Inteligentes
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              Sugestões personalizadas com IA e análise de grafos de co-ocorrência.
            </p>
          </div>
          <Button onClick={() => refreshMutation.mutate()} disabled={refreshMutation.isPending} variant="outline" size="sm" className="gap-2 shadow-sm">
            <RefreshCw className={`h-4 w-4 ${refreshMutation.isPending ? "animate-spin" : ""}`} />
            {refreshMutation.isPending ? "Recalculando..." : "Recalcular Scores"}
          </Button>
        </div>

        <Tabs defaultValue="daily" className="space-y-4">
          <TabsList className="grid w-full grid-cols-3 rounded-xl bg-muted/50 p-1">
            <TabsTrigger value="daily" className="rounded-lg">⭐ Destaques</TabsTrigger>
            <TabsTrigger value="channel" className="rounded-lg">📱 Por Canal</TabsTrigger>
            <TabsTrigger value="campaign" className="rounded-lg">🎯 Campanhas</TabsTrigger>
          </TabsList>

          <TabsContent value="daily">
            {loadingDaily ? (
              <RecommendationSkeleton />
            ) : daily.length > 0 ? (
              <div className="grid gap-3 grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
                {daily.map((item: any) => <RecommendationCard key={item.productId} item={item} />)}
              </div>
            ) : (
              <div className="text-center py-20 bg-muted/20 rounded-3xl border-2 border-dashed border-border/50">
                <Brain className="h-10 w-10 text-muted-foreground opacity-20 mx-auto mb-4" />
                <p className="text-muted-foreground text-sm font-bold">Sem recomendações hoje.</p>
                <p className="text-muted-foreground text-xs mt-2">Execute o treinamento do modelo ML para gerar sugestões.</p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="channel" className="space-y-4">
            <div className="flex items-center gap-3">
               <Select value={selectedChannel} onValueChange={setSelectedChannel}>
                <SelectTrigger className="w-48 rounded-xl shadow-sm"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="whatsapp">WhatsApp</SelectItem>
                  <SelectItem value="instagram">Instagram</SelectItem>
                  <SelectItem value="facebook">Facebook</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-[10px] text-muted-foreground uppercase font-bold">Filtro por rede social</p>
            </div>
            {loadingChannel ? (
              <RecommendationSkeleton />
            ) : channel.length > 0 ? (
              <div className="grid gap-3 grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
                {channel.map((item: any) => <RecommendationCard key={item.productId} item={item} />)}
              </div>
            ) : (
              <Card><CardContent className="py-12 text-center text-muted-foreground text-sm">Nenhuma recomendação canalizada.</CardContent></Card>
            )}
          </TabsContent>

          <TabsContent value="campaign" className="space-y-4">
            <Select value={selectedCampaign} onValueChange={setSelectedCampaign}>
              <SelectTrigger className="w-64 rounded-xl shadow-sm"><SelectValue placeholder="Selecione uma campanha" /></SelectTrigger>
              <SelectContent>
                {campaigns.map((c: any) => (
                  <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            {loadingCampaign ? (
              <RecommendationSkeleton />
            ) : campaign.length > 0 ? (
              <div className="grid gap-3 grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
                {campaign.map((item: any) => <RecommendationCard key={item.productId} item={item} />)}
              </div>
            ) : (
              <div className="text-center py-20 bg-muted/20 rounded-xl">
                 <p className="text-muted-foreground text-sm">{selectedCampaign ? "Nenhuma recomendação para esta campanha." : "Selecione uma campanha para ver o foco da IA."}</p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
}
