// ============================================
// AfiliaML — Página de Relatórios
// NOVO: Fase 3.4 — Exportação de dados
// ============================================

import { useState } from "react";
import { Layout } from "@/components/layout/Layout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { CalendarIcon, Download, FileSpreadsheet, DollarSign, MousePointerClick } from "lucide-react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { cn } from "@/lib/utils";

const API = "http://localhost:3333";

export default function Relatorios() {
  const [dataInicio, setDataInicio] = useState<Date>();
  const [dataFim, setDataFim] = useState<Date>();
  const [taxaComissao, setTaxaComissao] = useState("8");
  const [isLoading, setIsLoading] = useState(false);

  const handleDownload = async (endpoint: string, filename: string) => {
    setIsLoading(true);
    try {
      const qs = new URLSearchParams();
      if (endpoint.includes("/clicks")) {
        if (dataInicio) qs.append("dataInicio", dataInicio.toISOString().split("T")[0]);
        if (dataFim) qs.append("dataFim", dataFim.toISOString().split("T")[0]);
      } else if (endpoint.includes("/commission")) {
        qs.append("taxa", (parseFloat(taxaComissao) / 100).toString());
      }
      
      const url = `${API}${endpoint}?${qs.toString()}`;
      
      // Cria link oculto e faz download
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <FileSpreadsheet className="h-6 w-6 text-primary" /> Relatórios e Exportação
          </h1>
          <p className="text-sm text-muted-foreground mt-1">Baixe os dados da sua operação em CSV para análise em planilhas</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {/* Exportação de Produtos */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <FileSpreadsheet className="h-5 w-5 text-blue-500" /> Catálogo de Produtos
              </CardTitle>
              <CardDescription>Baixa todos os produtos ativos com URLs de afiliado, scores de IA e tendências de preço.</CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => handleDownload("/api/reports/products", "produtos_afiliaml.csv")} 
                disabled={isLoading} className="w-full gap-2 transition-all hover:scale-[1.02]">
                <Download className="h-4 w-4" /> Baixar CSV de Produtos
              </Button>
            </CardContent>
          </Card>

          {/* Relatório de Cliques */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <MousePointerClick className="h-5 w-5 text-purple-500" /> Relatório de Cliques
              </CardTitle>
              <CardDescription>Exporta registro de todos os cliques nos seus links, filtrados por data, canal e produto.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Popover>
                  <PopoverTrigger asChild>
                    <Button variant="outline" className={cn("w-full justify-start text-left font-normal", !dataInicio && "text-muted-foreground")}>
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {dataInicio ? format(dataInicio, "dd/MM/yyyy") : "Data Inicial"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
                    <Calendar mode="single" selected={dataInicio} onSelect={setDataInicio} initialFocus locale={ptBR} />
                  </PopoverContent>
                </Popover>

                <Popover>
                  <PopoverTrigger asChild>
                    <Button variant="outline" className={cn("w-full justify-start text-left font-normal", !dataFim && "text-muted-foreground")}>
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {dataFim ? format(dataFim, "dd/MM/yyyy") : "Data Final"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
                    <Calendar mode="single" selected={dataFim} onSelect={setDataFim} initialFocus locale={ptBR} />
                  </PopoverContent>
                </Popover>
              </div>
              <Button onClick={() => handleDownload("/api/reports/clicks", "cliques_afiliaml.csv")} 
                disabled={isLoading} className="w-full gap-2 transition-all hover:scale-[1.02]" variant="secondary">
                <Download className="h-4 w-4" /> Exportar Cliques (CSV)
              </Button>
            </CardContent>
          </Card>

          {/* Estimativa de Comissão */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <DollarSign className="h-5 w-5 text-emerald-500" /> Projeção de Comissão
              </CardTitle>
              <CardDescription>Calcula comissão estimada com base nos cliques reais assumindo 2% de conversão de compras.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-2">
                <div className="flex-1">
                  <label className="text-xs text-muted-foreground mb-1 block">Taxa de Comissão ML (%)</label>
                  <Input type="number" min="1" max="15" step="0.5" value={taxaComissao} onChange={(e) => setTaxaComissao(e.target.value)} />
                </div>
              </div>
              <Button onClick={() => handleDownload("/api/reports/commission", "comissao_afiliaml.csv")} 
                disabled={isLoading} className="w-full gap-2 transition-all hover:scale-[1.02] bg-emerald-600 hover:bg-emerald-700 text-white">
                <Download className="h-4 w-4" /> Gerar Projeção (CSV)
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
  );
}
