import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  ExternalLink, 
  MessageCircle, 
  Copy,
  Check,
  ImageOff,
  Sparkles,
  Trash
} from "lucide-react";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";

interface ProductCardProps {
  product: any;
  variant?: "default" | "compact";
}

export function ProductCard({ product, variant = "compact" }: ProductCardProps) {
  const { toast } = useToast();
  const [copied, setCopied] = useState(false);
  const [imgError, setImgError] = useState(false);
  const [isAffiliating, setIsAffiliating] = useState(false);

  const title = product.title ?? "Sem título";
  const imageUrl = product.imageUrl ?? product.image ?? "";
  const originalPrice = product.originalPrice ?? product.oldPrice ?? 0;
  const discountPrice = product.discountPrice ?? product.price ?? 0;
  const discountPercent = product.discountPercent ?? (originalPrice > 0 ? Math.round((1 - discountPrice / originalPrice) * 100) : 0);
  const affiliateLink = product.affiliateUrl ?? product.affiliateLink ?? product.link ?? "#";
  const freeShipping = product.freeShipping ?? false;

  const formatPrice = (price: number) =>
    new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(price ?? 0);

  const generateWhatsAppMessage = () =>
    encodeURIComponent(
      `📺 ${imageUrl}\n\n🔥 *OFERTA!*\n*${title}*\n❌ ~${formatPrice(originalPrice)}~\n✅ *${formatPrice(discountPrice)}* (-${discountPercent}%)\n${freeShipping ? "🚚 Frete Grátis\n" : ""}👉 ${affiliateLink}`
    );

  const handleCopyLink = async () => {
    await navigator.clipboard.writeText(affiliateLink);
    setCopied(true);
    toast({ title: "Link copiado!" });
    setTimeout(() => setCopied(false), 2000);
  };

  const handleShareWhatsApp = () => {
    window.open(`https://wa.me/?text=${generateWhatsAppMessage()}`, "_blank");
  };

  return (
    <Card className="group overflow-hidden transition-shadow hover:shadow-md border-border/40 bg-card">
      {/* Image */}
      <a href={product.originalUrl} target="_blank" rel="noopener noreferrer" title="Clicar para abrir no Mercado Livre">
        <div className="relative aspect-[4/3] overflow-hidden bg-muted">
          {imageUrl && !imgError ? (
            <img
              src={imageUrl}
              alt={title}
              referrerPolicy="no-referrer"
              onError={() => setImgError(true)}
              className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
            />
          ) : (
            <div className="h-full w-full flex items-center justify-center bg-muted text-muted-foreground">
              <ImageOff className="h-6 w-6 opacity-40" />
            </div>
          )}
          {discountPercent >= 30 && (
            <Badge className="absolute left-1 top-1 text-[10px] px-1 py-0 bg-destructive text-destructive-foreground">
              -{discountPercent}%
            </Badge>
          )}
          {product.mlScore !== undefined && product.mlScore > 0 && (
            <Badge className={`absolute right-1 top-1 text-[10px] px-1 py-0 text-white ${
              product.mlScore >= 0.65 ? 'bg-green-500' : product.mlScore >= 0.35 ? 'bg-yellow-500' : 'bg-red-500'
            }`}>
              {Math.round(product.mlScore * 100)}% Relevância
            </Badge>
          )}
        </div>
      </a>

      {/* Content */}
      <CardContent className="p-2">
        <h3 className="text-xs font-medium text-card-foreground line-clamp-2 leading-tight mb-1">
          {title}
        </h3>
        <div className="flex items-baseline gap-1 flex-wrap">
          <span className="text-sm font-bold text-primary leading-none">
            {formatPrice(discountPrice)}
          </span>
          {originalPrice > 0 && originalPrice !== discountPrice && (
            <span className="text-[10px] text-muted-foreground line-through">
              {formatPrice(originalPrice)}
            </span>
          )}
        </div>

        {/* Actions - Inserção de Link / Afiliação */}
        <div className="mt-2 text-center">
          {product.affiliateUrl ? (
            <div className="flex gap-2">
              <Button size="sm" variant="outline" className="flex-1 text-xs h-8 border-green-500 text-green-600 hover:bg-green-50">
                <Check className="h-3.5 w-3.5 mr-1" /> Afiliado!
              </Button>
              <Button size="sm" variant="outline" className="h-8 px-2" onClick={handleCopyLink} title="Copiar link">
                <Copy className="h-3.5 w-3.5" />
              </Button>
            </div>
          ) : (
            <Button 
              size="sm" 
              variant="default" 
              className="w-full text-xs h-8 bg-primary hover:bg-primary/90 hover:scale-105 transition-all text-black font-bold" 
              disabled={isAffiliating}
              onClick={async () => {
              try {
                setIsAffiliating(true);
                const res = await fetch(`http://localhost:3333/api/products/${product.id}/affiliate`, {
                  method: 'POST',
                });
                const data = await res.json();
                if (res.ok && data.success) {
                  toast({ title: "Afiliado com Sucesso!", description: "Link oficial gerado." });
                  window.location.reload();
                } else {
                  // Fallback se n tiver configurado etc..
                  toast({ title: "Atenção", description: data.error || "Verifique auth do ML", variant: "destructive" });
                }
              } catch (e) {
                toast({ title: "Erro ao afiliar", variant: "destructive" });
              } finally {
                setIsAffiliating(false);
              }
            }}>
              {isAffiliating ? <Check className="h-4 w-4 mr-1 text-black animate-pulse" /> : <Sparkles className="h-4 w-4 mr-1 text-black" />}
              {isAffiliating ? "Gerando..." : "💰 Afiliar (Meli.la)"}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
