import { useState } from "react";
import { Layout } from "@/components/layout/Layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { categories } from "@/data/mockProducts";
import { 
  Plus, 
  Link2, 
  Image, 
  Tag, 
  DollarSign,
  Sparkles,
  Save
} from "lucide-react";

const AdicionarProduto = () => {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    originalPrice: "",
    discountPrice: "",
    imageUrl: "",
    affiliateLink: "",
    category: "",
    freeShipping: true,
    featured: false,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    // Simular salvamento
    await new Promise((resolve) => setTimeout(resolve, 1000));

    toast({
      title: "Produto adicionado!",
      description: "Seu produto foi cadastrado com sucesso.",
    });

    setFormData({
      title: "",
      description: "",
      originalPrice: "",
      discountPrice: "",
      imageUrl: "",
      affiliateLink: "",
      category: "",
      freeShipping: true,
      featured: false,
    });

    setIsLoading(false);
  };

  const discountPercent = formData.originalPrice && formData.discountPrice
    ? Math.round((1 - parseFloat(formData.discountPrice) / parseFloat(formData.originalPrice)) * 100)
    : 0;

  return (
    <Layout>
      <div className="max-w-2xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Adicionar Produto
          </h1>
          <p className="text-muted-foreground">
            Cadastre uma nova oferta com seu link de afiliado
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Informações Básicas */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Tag className="h-5 w-5 text-primary" />
                Informações do Produto
              </CardTitle>
              <CardDescription>
                Preencha os dados básicos do produto
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="title">Título do Produto</Label>
                <Input
                  id="title"
                  placeholder="Ex: Fone de Ouvido Bluetooth JBL"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Descrição</Label>
                <Textarea
                  id="description"
                  placeholder="Descreva os principais benefícios do produto..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="category">Categoria</Label>
                <Select
                  value={formData.category}
                  onValueChange={(value) => setFormData({ ...formData, category: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione uma categoria" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.filter(c => c !== "Todos").map((category) => (
                      <SelectItem key={category} value={category}>
                        {category}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Preços */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="h-5 w-5 text-success" />
                Preços
              </CardTitle>
              <CardDescription>
                Informe o preço original e o preço promocional
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="originalPrice">Preço Original (R$)</Label>
                  <Input
                    id="originalPrice"
                    type="number"
                    step="0.01"
                    placeholder="349.99"
                    value={formData.originalPrice}
                    onChange={(e) => setFormData({ ...formData, originalPrice: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="discountPrice">Preço com Desconto (R$)</Label>
                  <Input
                    id="discountPrice"
                    type="number"
                    step="0.01"
                    placeholder="199.90"
                    value={formData.discountPrice}
                    onChange={(e) => setFormData({ ...formData, discountPrice: e.target.value })}
                    required
                  />
                </div>
              </div>

              {discountPercent > 0 && (
                <div className="flex items-center gap-2 p-3 rounded-lg bg-success/10 text-success">
                  <Sparkles className="h-4 w-4" />
                  <span className="font-medium">
                    Desconto de {discountPercent}%
                  </span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Links e Imagem */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Link2 className="h-5 w-5 text-secondary" />
                Links e Mídia
              </CardTitle>
              <CardDescription>
                Adicione o link de afiliado e imagem do produto
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="affiliateLink">Link de Afiliado</Label>
                <Input
                  id="affiliateLink"
                  type="url"
                  placeholder="https://mercadolivre.com.br/produto?aff=SEU_ID"
                  value={formData.affiliateLink}
                  onChange={(e) => setFormData({ ...formData, affiliateLink: e.target.value })}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="imageUrl">URL da Imagem</Label>
                <Input
                  id="imageUrl"
                  type="url"
                  placeholder="https://exemplo.com/imagem.jpg"
                  value={formData.imageUrl}
                  onChange={(e) => setFormData({ ...formData, imageUrl: e.target.value })}
                />
              </div>

              {formData.imageUrl && (
                <div className="relative aspect-square w-32 rounded-lg overflow-hidden border border-border">
                  <img
                    src={formData.imageUrl}
                    alt="Preview"
                    referrerPolicy="no-referrer"
                    className="h-full w-full object-cover"
                    onError={(e) => {
                      e.currentTarget.src = "/placeholder.svg";
                    }}
                  />
                </div>
              )}
            </CardContent>
          </Card>

          {/* Opções */}
          <Card>
            <CardHeader>
              <CardTitle>Opções</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Frete Grátis</Label>
                  <p className="text-sm text-muted-foreground">
                    Este produto tem frete grátis?
                  </p>
                </div>
                <Switch
                  checked={formData.freeShipping}
                  onCheckedChange={(checked) => setFormData({ ...formData, freeShipping: checked })}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Produto em Destaque</Label>
                  <p className="text-sm text-muted-foreground">
                    Mostrar na página inicial?
                  </p>
                </div>
                <Switch
                  checked={formData.featured}
                  onCheckedChange={(checked) => setFormData({ ...formData, featured: checked })}
                />
              </div>
            </CardContent>
          </Card>

          {/* Submit */}
          <Button
            type="submit"
            size="lg"
            className="w-full gap-2"
            disabled={isLoading}
          >
            {isLoading ? (
              <>Salvando...</>
            ) : (
              <>
                <Save className="h-4 w-4" />
                Salvar Produto
              </>
            )}
          </Button>
        </form>
      </div>
    </Layout>
  );
};

export default AdicionarProduto;
