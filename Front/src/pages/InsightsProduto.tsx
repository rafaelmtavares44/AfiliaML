// ============================================
// AfiliaML — Página de Insights de Produto
// NOVO: Fase 3.2 — Detalhes inteligentes com ML + Grafo
// ============================================

import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Brain, TrendingUp, TrendingDown, Minus, Network,
  Info, ArrowLeft, ImageOff, ExternalLink
} from "lucide-react";

const API = "http://localhost:3333";

// Gauge SVG circular
function ScoreGauge({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const r = 54;
  const circumference = 2 * Math.PI * r;
  const offset = circumference - (pct / 100) * circumference;
  const color = pct >= 65 ? "#22c55e" : pct >= 35 ? "#eab308" : "#ef4444";

  return (
    <div className="flex flex-col items-center">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r={r} fill="none" stroke="#e5e7eb" strokeWidth="10" />
        <circle cx="70" cy="70" r={r} fill="none" stroke={color} strokeWidth="10"
          strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={offset}
          transform="rotate(-90 70 70)" style={{ transition: "stroke-dashoffset 1s ease" }} />
        <text x="70" y="65" textAnchor="middle" className="text-2xl font-bold" fill={color}>{pct}</text>
        <text x="70" y="85" textAnchor="middle" className="text-xs" fill="#9ca3af">de 100</text>
      </svg>
    </div>
  );
}

const featureLabels: Record<string, string> = {
  clicksLast7Days: "Cliques (7 dias)",
  discountPct: "Desconto (%)",
  categoryEncoded: "Categoria",
  priceNormalized: "Preço",
  sharesLast7Days: "Compartilhamentos (7 dias)",
  ratingAverage: "Avaliação Média",
  ratingCountNorm: "Qtd de Avaliações",
  soldQuantityNorm: "Vendas",
  freeShipping: "Frete Grátis",
  conversionRate: "Taxa de Conversão",
  pageRankScore: "Relevância (Grafo)",
  priceTrend: "Tendência de Preço",
};

const trendIcons: Record<string, any> = {
  subindo: TrendingUp,
  caindo: TrendingDown,
  estavel: Minus,
};

export default function InsightsProduto() {
  const { id } = useParams();
  const [explain, setExplain] = useState<any>(null);
  const [similar, setSimilar] = useState<any[]>([]);
  const [priceHistory, setPriceHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    fetchData();
  }, [id]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [explainRes, similarRes, histRes] = await Promise.all([
        fetch(`${API}/api/recommendations/${id}/explain`),
        fetch(`${API}/api/recommendations/similar/${id}`),
        fetch(`${API}/api/products/${id}/price-history?dias=30`),
      ]);
      const explainData = await explainRes.json();
      const similarData = await similarRes.json();
      const histData = await histRes.json();

      if (explainData.success) setExplain(explainData.data);
      if (similarData.success) setSimilar(similarData.data || []);
      if (histData.success) setPriceHistory(histData.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Layout><div className="py-20 text-center text-muted-foreground">Carregando insights...</div></Layout>;
  }

  if (!explain) {
    return <Layout><div className="py-20 text-center text-muted-foreground">Produto não encontrado.</div></Layout>;
  }

  const TrendIcon = trendIcons[explain.priceTrend] || Minus;
  const totalProducts = 163; // Estimativa baseada no grafo
  const prScoreNorm = Math.max(0.001, explain.pageRankScore);
  const percentil = Math.round((1 - prScoreNorm) * 100);

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <Link to="/recomendacoes">
            <Button variant="ghost" size="sm"><ArrowLeft className="h-4 w-4 mr-1" /> Voltar</Button>
          </Link>
          <div>
            <h1 className="text-xl font-bold">{explain.title}</h1>
            <p className="text-sm text-muted-foreground">Insights completos com IA</p>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {/* Score de Relevância */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Brain className="h-4 w-4 text-purple-500" /> Score de Relevância
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <ScoreGauge score={explain.mlScore} />
              <div className="space-y-2">
                {(explain.topFeatures || []).map((f: any, i: number) => (
                  <div key={i} className="flex justify-between text-xs">
                    <span className="text-muted-foreground">{featureLabels[f.feature] || f.feature}</span>
                    <Badge variant={f.contribution > 0 ? "default" : "secondary"} className="text-[10px]">
                      {f.contribution > 0 ? "+" : ""}{f.contribution.toFixed(2)}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Histórico de Preço */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <TrendIcon className="h-4 w-4" /> Histórico de Preço
                <Badge variant="outline" className="text-[10px] ml-auto">{explain.priceTrend}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {priceHistory.length > 0 ? (
                <div className="space-y-1">
                  {priceHistory.slice(0, 8).map((h: any, i: number) => (
                    <div key={i} className="flex justify-between text-xs border-b border-border/30 pb-1">
                      <span className="text-muted-foreground">
                        {new Date(h.scrapedAt || h.timestamp).toLocaleDateString("pt-BR")}
                      </span>
                      <span className="font-medium">
                        {new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(h.price)}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-muted-foreground">Sem histórico disponível.</p>
              )}
            </CardContent>
          </Card>

          {/* Posição no Grafo */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Network className="h-4 w-4 text-blue-500" /> Posição no Grafo
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div className="text-center p-2 rounded-lg bg-muted/50">
                  <p className="text-lg font-bold text-primary">Top {percentil > 0 ? percentil : 1}%</p>
                  <p className="text-[10px] text-muted-foreground">PageRank</p>
                </div>
                <div className="text-center p-2 rounded-lg bg-muted/50">
                  <p className="text-lg font-bold text-primary">Nicho {explain.communityId >= 0 ? explain.communityId : "—"}</p>
                  <p className="text-[10px] text-muted-foreground">Comunidade</p>
                </div>
              </div>
              <div className="space-y-1">
                <p className="text-xs font-medium">Vizinhos próximos:</p>
                {(explain.neighbors || []).length > 0 ? (
                  (explain.neighbors || []).map((n: any, i: number) => (
                    <Link key={i} to={`/produtos/${n.productId}/insights`}
                      className="block text-xs text-primary hover:underline truncate">
                      • {n.title} (peso: {n.edgeWeight})
                    </Link>
                  ))
                ) : (
                  <p className="text-xs text-muted-foreground">Nenhum vizinho encontrado.</p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Produtos Similares */}
        {similar.length > 0 && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Produtos Similares</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
                {similar.map((s: any) => (
                  <Link key={s.productId} to={`/produtos/${s.productId}/insights`}
                    className="group block border rounded-lg overflow-hidden hover:shadow-md transition-shadow">
                    <div className="aspect-[4/3] overflow-hidden bg-muted">
                      {s.imageUrl ? (
                        <img src={s.imageUrl} alt={s.title} referrerPolicy="no-referrer"
                          className="h-full w-full object-cover group-hover:scale-105 transition-transform" />
                      ) : (
                        <div className="h-full w-full flex items-center justify-center">
                          <ImageOff className="h-6 w-6 opacity-30" />
                        </div>
                      )}
                    </div>
                    <div className="p-2">
                      <h4 className="text-xs font-medium line-clamp-2">{s.title}</h4>
                      <p className="text-xs font-bold text-primary mt-1">
                        {new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(s.price)}
                      </p>
                      <p className="text-[10px] text-muted-foreground mt-1 line-clamp-1">{s.similarityReason}</p>
                    </div>
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Explicação da IA */}
        <Card className="border-primary/20 bg-primary/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Info className="h-4 w-4 text-primary" /> Por que este produto foi recomendado?
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="text-sm">{explain.reasonText}</p>
            <p className="text-[10px] text-muted-foreground italic">
              ⚠️ Esta recomendação é gerada por algoritmo de inteligência artificial e pode não refletir resultados garantidos.
              Os scores são baseados em dados históricos e padrões detectados automaticamente.
            </p>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}
