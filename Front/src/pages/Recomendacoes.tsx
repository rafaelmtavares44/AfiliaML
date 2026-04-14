// ============================================
// AfiliaML — Página de Recomendações
// NOVO: Fase 3.2 — Dashboard inteligente
// ============================================

import { useState, useEffect } from "react";
import { Layout } from "@/components/layout/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Sparkles, TrendingDown, MousePointerClick, Brain,
  RefreshCw, ImageOff, ArrowRight
} from "lucide-react";
import { Link } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

const API = "http://localhost:3333";

const highlightConfig: Record<string, { label: string; color: string; icon: any }> = {
  queda_de_preco: { label: "Queda de Preço", color: "bg-emerald-500", icon: TrendingDown },
  tendencia_de_cliques: { label: "Tendência", color: "bg-blue-500", icon: MousePointerClick },
  alta_relevancia_ml: { label: "Alta Relevância", color: "bg-purple-500", icon: Brain },
};

function RecommendationCard({ item }: { item: any }) {
  const [imgError, setImgError] = useState(false);
  const config = highlightConfig[item.highlightReason] || highlightConfig.alta_relevancia_ml;
  const Icon = config.icon;
  const score = Math.round((item.combinedScore || 0) * 100);

  return (
    <Card className="group overflow-hidden hover:shadow-lg transition-all duration-300 border-border/40">
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
            {score}%
          </Badge>
        )}
      </div>
      <CardContent className="p-3 space-y-2">
        <h3 className="text-sm font-medium line-clamp-2 leading-tight">{item.title}</h3>
        <div className="flex items-baseline gap-2">
          <span className="text-base font-bold text-primary">
            {new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(item.price || 0)}
          </span>
          {item.discountPct > 0 && (
            <Badge variant="destructive" className="text-[10px]">-{item.discountPct}%</Badge>
          )}
        </div>
        <Progress value={score} className="h-1.5" />
        {item.reasonText && (
          <p className="text-[11px] text-muted-foreground line-clamp-2">{item.reasonText}</p>
        )}
        <Link to={`/produtos/${item.productId}/insights`}>
          <Button variant="ghost" size="sm" className="w-full text-xs gap-1 mt-1">
            Ver Insights <ArrowRight className="h-3 w-3" />
          </Button>
        </Link>
      </CardContent>
    </Card>
  );
}

export default function Recomendacoes() {
  const { toast } = useToast();
  const [daily, setDaily] = useState<any[]>([]);
  const [channel, setChannel] = useState<any[]>([]);
  const [campaign, setCampaign] = useState<any[]>([]);
  const [selectedChannel, setSelectedChannel] = useState("whatsapp");
  const [selectedCampaign, setSelectedCampaign] = useState("");
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchDaily();
    fetchCampaigns();
  }, []);

  useEffect(() => { fetchChannel(selectedChannel); }, [selectedChannel]);
  useEffect(() => { if (selectedCampaign) fetchCampaign(selectedCampaign); }, [selectedCampaign]);

  const fetchDaily = async () => {
    setLoading(true);
    try {
      const r = await fetch(`${API}/api/recommendations/daily`);
      const d = await r.json();
      if (d.success) setDaily(d.data || []);
    } catch {} finally { setLoading(false); }
  };

  const fetchChannel = async (ch: string) => {
    try {
      const r = await fetch(`${API}/api/recommendations/channel/${ch}`);
      const d = await r.json();
      if (d.success) setChannel(d.data || []);
    } catch {}
  };

  const fetchCampaigns = async () => {
    try {
      const r = await fetch(`${API}/api/campaigns`);
      const d = await r.json();
      if (d.success) {
        setCampaigns(d.data || []);
        if (d.data?.length > 0) setSelectedCampaign(d.data[0].id);
      }
    } catch {}
  };

  const fetchCampaign = async (id: string) => {
    try {
      const r = await fetch(`${API}/api/recommendations/campaign/${id}`);
      const d = await r.json();
      if (d.success) setCampaign(d.data || []);
    } catch {}
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await fetch(`${API}/api/recommendations/refresh`, { method: "POST" });
      toast({ title: "✅ Cache atualizado!" });
      await fetchDaily();
      await fetchChannel(selectedChannel);
    } catch { toast({ title: "❌ Erro", variant: "destructive" }); }
    finally { setRefreshing(false); }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-primary" /> Recomendações Inteligentes
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              Sugestões personalizadas com IA e análise de grafo
            </p>
          </div>
          <Button onClick={handleRefresh} disabled={refreshing} variant="outline" size="sm" className="gap-2">
            <RefreshCw className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
            {refreshing ? "Atualizando..." : "Recalcular"}
          </Button>
        </div>

        <Tabs defaultValue="daily" className="space-y-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="daily">⭐ Destaques do Dia</TabsTrigger>
            <TabsTrigger value="channel">📱 Por Canal</TabsTrigger>
            <TabsTrigger value="campaign">🎯 Para Campanhas</TabsTrigger>
          </TabsList>

          <TabsContent value="daily">
            {loading ? (
              <p className="text-center text-muted-foreground py-12">Carregando recomendações...</p>
            ) : daily.length > 0 ? (
              <div className="grid gap-3 grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
                {daily.map((item: any) => <RecommendationCard key={item.productId} item={item} />)}
              </div>
            ) : (
              <Card><CardContent className="py-12 text-center text-muted-foreground">
                Nenhuma recomendação disponível. Execute o ML treinamento primeiro.
              </CardContent></Card>
            )}
          </TabsContent>

          <TabsContent value="channel" className="space-y-4">
            <Select value={selectedChannel} onValueChange={setSelectedChannel}>
              <SelectTrigger className="w-48"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="whatsapp">WhatsApp</SelectItem>
                <SelectItem value="instagram">Instagram</SelectItem>
                <SelectItem value="facebook">Facebook</SelectItem>
              </SelectContent>
            </Select>
            {channel.length > 0 ? (
              <div className="grid gap-3 grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
                {channel.map((item: any) => <RecommendationCard key={item.productId} item={item} />)}
              </div>
            ) : (
              <Card><CardContent className="py-12 text-center text-muted-foreground">
                Nenhuma recomendação para este canal.
              </CardContent></Card>
            )}
          </TabsContent>

          <TabsContent value="campaign" className="space-y-4">
            <Select value={selectedCampaign} onValueChange={setSelectedCampaign}>
              <SelectTrigger className="w-64"><SelectValue placeholder="Selecione uma campanha" /></SelectTrigger>
              <SelectContent>
                {campaigns.map((c: any) => (
                  <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            {campaign.length > 0 ? (
              <div className="grid gap-3 grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
                {campaign.map((item: any) => <RecommendationCard key={item.productId} item={item} />)}
              </div>
            ) : (
              <Card><CardContent className="py-12 text-center text-muted-foreground">
                {selectedCampaign ? "Nenhuma recomendação para esta campanha." : "Selecione uma campanha."}
              </CardContent></Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
}
