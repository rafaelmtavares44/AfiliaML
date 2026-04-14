import { useState, useEffect, useCallback } from "react";
import { Layout } from "@/components/layout/Layout";
import { Search, MessageCircle, Send, RefreshCw, Sparkles, ArrowRight, Trash } from "lucide-react";
import { Link } from "react-router-dom";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";

const API_BASE = "http://localhost:3333";
const API_HEADERS = { "Content-Type": "application/json" };

const Compartilhar = () => {
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [sharingId, setSharingId] = useState<string | null>(null);
  const [editingProductId, setEditingProductId] = useState<string | null>(null);
  const [editingMessage, setEditingMessage] = useState("");
  const [manualAffiliateLink, setManualAffiliateLink] = useState("");

  const fetchCatalog = useCallback(async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/api/products/catalog?limite=100&hasAffiliate=true`, { headers: API_HEADERS });
      const data = await res.json();
      if (data.success) {
        setProducts(data.data);
      }
    } catch (error) {
      console.error("Erro ao carregar o catálogo para compartilhar:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCatalog();
  }, [fetchCatalog]);

  const handleShareWhatsApp = async (productId: string) => {
    try {
      setSharingId(productId);
      const res = await fetch(`${API_BASE}/api/share/whatsapp/${productId}`, {
        method: "POST",
        headers: API_HEADERS,
      });
      const data = await res.json();

      if (data.success && data.data.message) {
        setEditingProductId(productId);
        setEditingMessage(data.data.message);
        setManualAffiliateLink(""); // Reseta ao abrir um novo produto
      }
    } catch (error) {
      console.error("Erro ao gerar link:", error);
    } finally {
      setSharingId(null);
    }
  };

  const handleManualLinkChange = (newLink: string) => {
    setManualAffiliateLink(newLink);
    // Substituir o link na mensagem de edição
    // O padrão da mensagem geralmente termina em "🔗 Confira aqui: [LINK]"
    if (newLink) {
      const updatedMsg = editingMessage.replace(/🔗 Confira aqui: .*/, `🔗 Confira aqui: ${newLink}`);
      setEditingMessage(updatedMsg);
    }
  };

  const handleSendWhatsApp = () => {
    const encoded = encodeURIComponent(editingMessage);
    window.open(`https://wa.me/?text=${encoded}`, "_blank");
    setEditingProductId(null);
    setEditingMessage("");
    setManualAffiliateLink("");
  };

  const handleCancelEdit = () => {
    setEditingProductId(null);
    setEditingMessage("");
    setManualAffiliateLink("");
  };

  const filteredProducts = products.filter((p: any) => {
    const hasAffiliateLink = p.affiliateUrl && p.affiliateUrl !== "" && !p.affiliateUrl.includes("exemplo123");
    const matchesSearch = (p.title ?? "").toLowerCase().includes(searchTerm.toLowerCase());
    return hasAffiliateLink && matchesSearch;
  });

  return (
    <Layout>
      <div className="space-y-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Cofre de Divulgação</h1>
          <p className="text-muted-foreground text-sm mt-0.5">
            Visualize sua postagem e personalize antes de enviar.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar produto no cofre..."
              className="pl-10 h-11 text-sm rounded-xl shadow-sm border-muted-foreground/20 focus:ring-primary"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <Button variant="outline" size="icon" className="h-11 w-11 rounded-xl shadow-sm" onClick={fetchCatalog} disabled={loading}>
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          </Button>
        </div>

        {loading ? (
          <p className="text-center text-muted-foreground py-12 text-sm italic">Sincronizando produtos...</p>
        ) : filteredProducts.length > 0 ? (
          <div className="grid gap-3 lg:grid-cols-2">
            {filteredProducts.map((product: any) => (
              <Card key={product.id} className={`overflow-hidden border-border/50 transition-all duration-300 ${editingProductId === product.id ? "ring-2 ring-primary shadow-lg" : "hover:shadow-md"}`}>
                <CardContent className="p-0">
                  <div className="p-4 flex items-start gap-4">
                    <div className="w-16 h-16 rounded-lg overflow-hidden bg-muted border border-border/50 flex-shrink-0 shadow-sm">
                      {product.imageUrl ? (
                        <img src={product.imageUrl} alt={product.title} referrerPolicy="no-referrer" className="w-full h-full object-cover" />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-muted-foreground text-xs font-medium">PNG</div>
                      )}
                    </div>

                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-foreground text-sm line-clamp-2 leading-snug">{product.title}</h3>
                      <div className="flex items-center gap-2 mt-2">
                        <span className="text-lg font-bold text-primary">R$ {(product.price ?? 0).toFixed(2)}</span>
                        {product.oldPrice && (
                          <span className="text-xs line-through text-muted-foreground">de R$ {(product.oldPrice ?? 0).toFixed(2)}</span>
                        )}
                      </div>
                    </div>

                    <div className="flex flex-col sm:flex-row gap-2">
                      <Button
                        size="sm"
                        onClick={async () => {
                          if(confirm("Tem certeza que deseja remover este produto do cofre e deletá-lo do sistema?")) {
                            await fetch(`${API_BASE}/api/products/${product.id}`, { method: 'DELETE' });
                            window.location.reload();
                          }
                        }}
                        className="bg-red-50 text-red-500 border border-red-100 hover:bg-red-100 hover:text-red-600 rounded-full h-10 w-10 p-0 shadow-sm transition-all"
                      >
                        <Trash className="h-4 w-4" />
                      </Button>

                      <Button
                        size="sm"
                        onClick={() => handleShareWhatsApp(product.id)}
                        disabled={sharingId === product.id || editingProductId === product.id}
                        className="bg-[#25D366] hover:bg-[#128C7E] text-white font-bold rounded-full h-10 w-10 p-0 shadow-lg"
                      >
                        {sharingId === product.id ? <RefreshCw className="h-4 w-4 animate-spin" /> : <MessageCircle className="h-5 w-5" />}
                      </Button>
                    </div>
                  </div>

                  {editingProductId === product.id && (
                    <div className="bg-muted/30 border-t border-border p-4 animate-in slide-in-from-top-2 duration-300">
                      
                      {/* Campo de Link Manual (Agora por item) */}
                      <div className="mb-4 bg-primary/10 border border-primary/20 p-3 rounded-lg space-y-1.5 shadow-sm">
                        <label className="text-[10px] font-bold text-primary uppercase tracking-wider flex items-center gap-1.5">
                          🔗 Link de Afiliado Manual (Opcional)
                        </label>
                        <Input 
                          placeholder="Cole aqui seu link meli.la ou similar..." 
                          className="h-9 text-xs bg-background border-primary/30 focus-visible:ring-primary"
                          value={manualAffiliateLink}
                          onChange={(e) => handleManualLinkChange(e.target.value)}
                        />
                      </div>

                      <div className="grid gap-4 md:grid-cols-2">
                        <div className="space-y-3">
                          <label className="text-xs font-bold text-muted-foreground uppercase flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
                            Editar Mensagem
                          </label>
                          <Textarea
                            value={editingMessage}
                            onChange={(e) => setEditingMessage(e.target.value)}
                            className="min-h-[180px] text-xs leading-relaxed border-border/50 bg-background shadow-inner"
                            placeholder="Sua mensagem..."
                          />
                        </div>

                        <div className="space-y-3">
                          <label className="text-xs font-bold text-muted-foreground uppercase flex items-center gap-2">
                            📱 Preview no WhatsApp
                          </label>
                          <div className="bg-[#E5DDD5] rounded-xl p-3 min-h-[180px] relative overflow-hidden shadow-inner border border-black/5">
                            {/* Papel de parede estilo WhatsApp */}
                            <div className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[url('https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png')]" />
                            
                            <div className="relative z-10 bg-white rounded-lg p-3 shadow-sm max-w-[85%] ml-auto text-[11px] leading-tight flex flex-col gap-1 border-l-4 border-primary/40">
                              <div className="whitespace-pre-wrap text-foreground">{editingMessage}</div>
                              <span className="text-[9px] text-muted-foreground self-end mt-1">10:42 PM ✔️✔️</span>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="flex gap-2 mt-6">
                        <Button
                          onClick={handleSendWhatsApp}
                          className="flex-1 bg-[#25D366] hover:bg-[#128C7E] text-white font-bold gap-2 h-11 rounded-xl shadow-md transition-all hover:scale-[1.02] active:scale-95"
                        >
                          <Send className="h-4 w-4" />
                          Enviar no App
                        </Button>
                        <Button 
                          onClick={async () => {
                            await navigator.clipboard.writeText(editingMessage);
                            alert('Texto completo copiado! Basta colar (Ctrl+V) no WhatsApp que já está aberto.');
                          }} 
                          variant="secondary" 
                          className="h-11 rounded-xl px-6 bg-secondary/50 font-semibold"
                        >
                          Copiar Texto
                        </Button>
                        <Button onClick={handleCancelEdit} variant="outline" className="h-11 rounded-xl px-6 text-muted-foreground hover:bg-red-50 hover:text-red-500 hover:border-red-200">
                          Fechar
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="text-center py-20 bg-muted/20 rounded-3xl border-2 border-dashed border-border/50">
            <Sparkles className="h-10 w-10 text-primary opacity-20 mx-auto mb-4" />
            <p className="text-muted-foreground text-sm font-bold">O seu cofre está vazio.</p>
            <p className="text-muted-foreground text-xs mt-2 max-w-xs mx-auto">
              Vá na aba <span className="text-primary font-bold">Catálogo</span>, escolha produtos e clique em <span className="text-primary font-bold">Afiliar</span> para que eles apareçam aqui com os links oficiais!
            </p>
            <Link to="/catalogo">
              <Button variant="outline" size="sm" className="mt-6 gap-2">
                Ir para o Catálogo <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Compartilhar;
