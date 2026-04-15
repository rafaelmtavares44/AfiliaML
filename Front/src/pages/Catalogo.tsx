import { useState, useEffect, useCallback } from "react";
import { Layout } from "@/components/layout/Layout";
import { ProductCard } from "@/components/products/ProductCard";
import { Search, Filter, RefreshCw } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const API_BASE = "http://localhost:3333";
const API_HEADERS = { "Content-Type": "application/json" };

const Catalogo = () => {
  const [products, setProducts] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
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

  const handleSyncVitrine = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/api/scraper/sync-vitrine`, {
        method: "POST",
        headers: API_HEADERS,
      });
      const data = await res.json();
      if (data.success) {
        alert(`✅ Vitrine Sincronizada! ${data.data.total} links oficiais atualizados.`);
        fetchCatalog(selectedCategory);
      }
    } catch (error) {
      alert("❌ Erro ao sincronizar vitrine.");
    } finally {
      setLoading(false);
    }
  };

  const fetchCatalog = useCallback(async (cat = "todos") => {
    try {
      setLoading(true);
      let url = `${API_BASE}/api/products/catalog?limite=300&hasAffiliate=true`;
      if (cat !== "todos") {
        url += `&categoria=${cat}`;
      }
      const res = await fetch(url);
      const data = await res.json();
      if (data.success) {
        setProducts(data.data);
      }
    } catch (error) {
      console.error("Erro ao carregar o catálogo:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCategories();
    fetchCatalog();
  }, [fetchCatalog]);

  const handleCategoryClick = (catId: string) => {
    setSelectedCategory(catId);
    fetchCatalog(catId);
  };

  const filteredProducts = products.filter((p: any) =>
    (p.title ?? "").toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex flex-col gap-4">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Catálogo de Produtos Afiliados</h1>
            <p className="text-muted-foreground text-sm mt-0.5">
              Aqui estão os produtos que você já afiliou e que podem ir para o cofre de divulgação.
            </p>
          </div>

          {/* Barra de Categorias */}
          <div className="flex items-center gap-2 overflow-x-auto pb-2 -mx-2 px-2 no-scrollbar">
            <Button
              variant={selectedCategory === "todos" ? "default" : "outline"}
              size="sm"
              className="rounded-full whitespace-nowrap"
              onClick={() => handleCategoryClick("todos")}
            >
              🏠 Todos
            </Button>
            {categories.filter(c => c.id !== "ofertas").map((cat) => (
              <Button
                key={cat.id}
                variant={selectedCategory === cat.id ? "default" : "outline"}
                size="sm"
                className="rounded-full whitespace-nowrap"
                onClick={() => handleCategoryClick(cat.id)}
              >
                {cat.nome}
              </Button>
            ))}
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar afiliado..."
              className="pl-10 h-10 text-sm rounded-xl"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <Button variant="outline" size="icon" className="h-10 w-10 rounded-xl" onClick={() => fetchCatalog(selectedCategory)} disabled={loading} title="Recarregar tela">
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          </Button>
          <Button variant="default" className="h-10 rounded-xl bg-primary text-black font-bold shadow-sm" onClick={handleSyncVitrine} disabled={loading}>
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            Sincronizar Vitrine
          </Button>
        </div>

        {loading ? (
          <p className="text-center text-muted-foreground py-8 text-sm">Buscando ofertas...</p>
        ) : filteredProducts.length > 0 ? (
          <div className="grid gap-2 grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8">
            {filteredProducts.map((product: any) => (
              <ProductCard key={product.id} product={product} variant="compact" />
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-muted-foreground text-sm">Nenhuma oferta encontrada.</p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Catalogo;
