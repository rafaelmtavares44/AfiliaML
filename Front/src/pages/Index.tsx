import { useState, useEffect, useCallback } from "react";
import { Layout } from "@/components/layout/Layout";
import { StatsCard } from "@/components/dashboard/StatsCard";
import { ProductCard } from "@/components/products/ProductCard";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  ShoppingBag, 
  MousePointerClick, 
  MessageCircle, 
  TrendingUp,
  ArrowRight,
  Sparkles,
  RefreshCw
} from "lucide-react";
import { Link } from "react-router-dom";

const API_BASE = "http://localhost:3333";
const API_HEADERS = { "Content-Type": "application/json" };

const Index = () => {
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalClicks: 0,
    messagesShared: 0,
    conversionRate: 0,
  });
  
  const [latestProducts, setLatestProducts] = useState<any[]>([]);
  const [highlights, setHighlights] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isScraping, setIsScraping] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState("todos");

  const fetchCategories = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/scraper/categorias`);
      const data = await res.json();
      if (data.success) {
        setCategories(data.data);
      }
    } catch (error) {
      console.error("Erro ao carregar categorias:", error);
    }
  };

  const fetchAll = useCallback(async (categoria?: string) => {
    const cat = categoria ?? selectedCategory;
    try {
      setLoading(true);
      
      // Montar URLs com filtro de categoria
      let statsUrl = `${API_BASE}/api/dashboard/stats`;
      let productsUrl = `${API_BASE}/api/products/catalog?limite=24&hasAffiliate=false`;
      
      if (cat !== "todos") {
        statsUrl += `?categoria=${cat}`;
        productsUrl += `&categoria=${cat}`;
      }

      let recommendationsUrl = `${API_BASE}/api/recommendations/daily`;

      const [statsRes, productsRes, recRes] = await Promise.all([
        fetch(statsUrl, { headers: API_HEADERS }),
        fetch(productsUrl, { headers: API_HEADERS }),
        fetch(recommendationsUrl, { headers: API_HEADERS }).catch(() => null),
      ]);
      
      const statsData = await statsRes.json();
      if (statsData.success) {
        setStats({
          totalProducts: statsData.data.totalProducts ?? 0,
          totalClicks: statsData.data.totalClicks ?? 0,
          messagesShared: statsData.data.totalShares ?? 0,
          conversionRate: statsData.data.conversionRate ?? 0,
        });
      }
      const productsData = await productsRes.json();
      if (productsData.success) {
        setLatestProducts(productsData.data);
      }
      if (recRes && recRes.ok) {
        const recData = await recRes.json();
        if (recData.success) {
          setHighlights((recData.data || []).slice(0, 3));
        }
      }
    } catch (error) {
      console.error("Erro no fetch:", error);
    } finally {
      setLoading(false);
    }
  }, [selectedCategory]);

  useEffect(() => {
    fetchCategories();
    fetchAll();
  }, [fetchAll]);

  const handleScraper = async (categoria?: string) => {
    const cat = categoria ?? selectedCategory;
    try {
      setIsScraping(true);
      const res = await fetch(`${API_BASE}/api/scraper/run`, {
        method: "POST",
        headers: { ...API_HEADERS, "Content-Type": "application/json" },
        body: JSON.stringify({ categoria: cat === "todos" ? "ofertas" : cat }),
      });
      const data = await res.json();
      if (data.success) {
        alert(`✅ Robô ativado para [${cat}]! Ofertas raspadas com sucesso!`);
        await fetchAll(cat);
      }
    } catch (error) {
      alert("❌ Erro. Verifique se o backend está rodando.");
    } finally {
      setIsScraping(false);
    }
  };

  const handleSyncVitrine = async () => {
    try {
      setIsScraping(true);
      const res = await fetch(`${API_BASE}/api/scraper/sync-vitrine`, {
        method: "POST",
        headers: API_HEADERS,
      });
      const data = await res.json();
      if (data.success) {
        alert(`✅ Vitrine Sincronizada! ${data.data.total} links oficiais atualizados.`);
        await fetchAll();
      }
    } catch (error) {
      alert("❌ Erro ao sincronizar vitrine.");
    } finally {
      setIsScraping(false);
    }
  };

  const handleCategoryClick = (catId: string) => {
    setSelectedCategory(catId);
    fetchAll(catId);
  };

  return (
    <Layout>
      <div className="space-y-6">
        <section className="relative overflow-hidden rounded-xl bg-gradient-to-br from-primary via-primary to-primary/80 p-6 text-primary-foreground">
          <div className="relative z-10">
            <h1 className="text-2xl md:text-3xl font-bold mb-1">Painel AfiliaML</h1>
            <p className="text-sm opacity-90 mb-4 max-w-xl">
              Gerencie ofertas, ative robôs e acompanhe seus lucros.
            </p>
            <div className="flex flex-col gap-4">
              <div className="flex flex-wrap items-center gap-3 mt-4">
                <Button variant="secondary" size="sm" className="gap-1.5 h-10 px-4 font-bold shadow-md hover:scale-105 transition-all" onClick={() => handleScraper("ofertas")} disabled={isScraping}>
                  {isScraping ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                  {isScraping ? "Buscando Ofertas..." : "Buscar Ofertas ML Agora!"}
                </Button>
                <Link to="/compartilhar">
                  <Button variant="outline" size="sm" className="gap-1.5 h-10 px-4 bg-white/10 border-white/20 hover:bg-white/20 text-white font-medium">
                    Ver Cofre de Divulgação
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </section>

        <section className="grid gap-3 grid-cols-2 lg:grid-cols-4">
          <StatsCard title="Produtos" value={stats.totalProducts} icon={ShoppingBag} variant="primary" />
          <StatsCard title="Cliques" value={(stats.totalClicks ?? 0).toLocaleString("pt-BR")} icon={MousePointerClick} />
          <StatsCard title="Mensagens" value={stats.messagesShared ?? 0} icon={MessageCircle} variant="secondary" />
          <StatsCard title="Conversão" value={`${stats.conversionRate ?? 0}%`} icon={TrendingUp} />
        </section>

        <section>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between py-3 px-4">
              <CardTitle className="flex items-center gap-2 text-base">
                <Sparkles className="h-4 w-4 text-primary" />
                Últimas Ofertas
              </CardTitle>
              <Link to="/catalogo">
                <Button variant="ghost" size="sm" className="gap-1 text-xs">
                  Ver todas <ArrowRight className="h-3 w-3" />
                </Button>
              </Link>
            </CardHeader>
            <CardContent className="px-4 pb-4 pt-0">
              {loading ? (
                <p className="text-center text-muted-foreground py-6 text-sm">Carregando...</p>
              ) : latestProducts.length > 0 ? (
                <div className="grid gap-2 grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8">
                  {latestProducts.map((p: any) => (
                    <ProductCard key={p.id} product={p} variant="compact" />
                  ))}
                </div>
              ) : (
                <p className="text-center text-muted-foreground py-6 text-sm">Nenhuma oferta ainda. Clique no Robô!</p>
              )}
            </CardContent>
          </Card>
        </section>

        {highlights.length > 0 && (
          <section>
            <Card className="border-primary/20 bg-primary/5">
              <CardHeader className="flex flex-row items-center justify-between py-3 px-4">
                <CardTitle className="flex items-center gap-2 text-base">
                  <Sparkles className="h-4 w-4 text-purple-500" />
                  Destaques Inteligentes
                </CardTitle>
                <Link to="/recomendacoes">
                  <Button variant="outline" size="sm" className="gap-1 text-xs">
                    Ver todas as recomendações <ArrowRight className="h-3 w-3" />
                  </Button>
                </Link>
              </CardHeader>
              <CardContent className="px-4 pb-4 pt-0">
                <div className="grid gap-3 grid-cols-1 md:grid-cols-3">
                  {highlights.map((h: any) => (
                    <Card key={h.productId} className="flex gap-3 p-3 overflow-hidden">
                      <div className="h-16 w-16 shrink-0 bg-muted rounded overflow-hidden">
                        {h.imageUrl ? (
                          <img src={h.imageUrl} alt={h.title} className="w-full h-full object-cover" />
                        ) : null}
                      </div>
                      <div className="flex-1 min-w-0">
                        <Link to={`/produtos/${h.productId}/insights`} className="hover:underline">
                          <h4 className="text-xs font-semibold line-clamp-2 leading-tight">{h.title}</h4>
                        </Link>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-sm font-bold text-primary">
                            {new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(h.price)}
                          </span>
                          <span className="text-[10px] bg-primary/10 text-primary px-1.5 py-0.5 rounded font-medium">
                            {Math.round(h.combinedScore * 100)}% Match
                          </span>
                        </div>
                        <p className="text-[10px] text-muted-foreground mt-1 truncate">{h.reasonText}</p>
                      </div>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </section>
        )}
      </div>
    </Layout>
  );
};

export default Index;
