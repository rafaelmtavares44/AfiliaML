// ============================================
// AfiliaML — Página de Status de Jobs
// NOVO: Fase 3.2 — Monitoramento de filas BullMQ
// ============================================

import { useState, useEffect, useCallback } from "react";
import { Layout } from "@/components/layout/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import {
  RefreshCw, Play, Clock, CheckCircle2, XCircle, Loader2,
  Bot, Zap, Brain, Sparkles
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const API = "http://localhost:3333";

const queueConfig: Record<string, { label: string; icon: any; color: string }> = {
  scraper: { label: "Scraper", icon: Bot, color: "text-blue-500" },
  enrichment: { label: "Enriquecimento", icon: Zap, color: "text-yellow-500" },
  mlTraining: { label: "ML Training", icon: Brain, color: "text-purple-500" },
  recommendations: { label: "Recomendações", icon: Sparkles, color: "text-emerald-500" },
};

function QueueCard({ name, data }: { name: string; data: any }) {
  const config = queueConfig[name] || { label: name, icon: RefreshCw, color: "text-gray-500" };
  const Icon = config.icon;
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center gap-2 mb-3">
          <Icon className={`h-5 w-5 ${config.color}`} />
          <h3 className="font-medium text-sm">{config.label}</h3>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="flex items-center gap-1.5 text-xs">
            <Clock className="h-3 w-3 text-amber-500" />
            <span className="text-muted-foreground">Aguardando:</span>
            <Badge variant="secondary" className="text-[10px]">{data?.waiting ?? 0}</Badge>
          </div>
          <div className="flex items-center gap-1.5 text-xs">
            <Loader2 className="h-3 w-3 text-blue-500 animate-spin" />
            <span className="text-muted-foreground">Ativo:</span>
            <Badge variant="secondary" className="text-[10px]">{data?.active ?? 0}</Badge>
          </div>
          <div className="flex items-center gap-1.5 text-xs">
            <CheckCircle2 className="h-3 w-3 text-green-500" />
            <span className="text-muted-foreground">Concluído:</span>
            <Badge className="text-[10px] bg-green-500/10 text-green-600">{data?.completed ?? 0}</Badge>
          </div>
          <div className="flex items-center gap-1.5 text-xs">
            <XCircle className="h-3 w-3 text-red-500" />
            <span className="text-muted-foreground">Falhou:</span>
            <Badge variant="destructive" className="text-[10px]">{data?.failed ?? 0}</Badge>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function StatusJobs() {
  const { toast } = useToast();
  const [status, setStatus] = useState<any>(null);
  const [history, setHistory] = useState<any>(null);
  const [loadingAction, setLoadingAction] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    try {
      const r = await fetch(`${API}/api/jobs/status`);
      const d = await r.json();
      if (d.success) setStatus(d.data);
    } catch {}
  }, []);

  const fetchHistory = async () => {
    try {
      const r = await fetch(`${API}/api/jobs/history`);
      const d = await r.json();
      if (d.success) setHistory(d.data);
    } catch {}
  };

  // Auto-refresh a cada 10 segundos
  useEffect(() => {
    fetchStatus();
    fetchHistory();
    const interval = setInterval(fetchStatus, 10000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  const executeAction = async (endpoint: string, label: string) => {
    setLoadingAction(label);
    try {
      const r = await fetch(`${API}${endpoint}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
      const d = await r.json();
      if (d.success) {
        toast({ title: `✅ ${label}`, description: d.message });
        setTimeout(() => { fetchStatus(); fetchHistory(); }, 2000);
      } else {
        toast({ title: `❌ Erro`, description: d.message, variant: "destructive" });
      }
    } catch { toast({ title: "❌ Erro de conexão", variant: "destructive" }); }
    finally { setLoadingAction(null); }
  };

  // Coletar jobs do histórico para tabela
  const allJobs: any[] = [];
  if (history) {
    for (const [queue, data] of Object.entries(history) as [string, any][]) {
      for (const job of (data.completed || [])) allJobs.push({ ...job, queue, status: "completed" });
      for (const job of (data.failed || [])) allJobs.push({ ...job, queue, status: "failed" });
    }
  }
  allJobs.sort((a, b) => new Date(b.createdAt || 0).getTime() - new Date(a.createdAt || 0).getTime());

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <RefreshCw className="h-6 w-6 text-primary" /> Status dos Jobs
          </h1>
          <p className="text-sm text-muted-foreground">Monitoramento em tempo real das filas de processamento (atualiza a cada 10s)</p>
        </div>

        {/* Queue cards */}
        <div className="grid gap-3 grid-cols-2 lg:grid-cols-4">
          {status && Object.entries(status).map(([name, data]) => (
            <QueueCard key={name} name={name} data={data} />
          ))}
        </div>

        {/* Action buttons */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Ações</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              <Button size="sm" variant="outline" className="gap-2" disabled={!!loadingAction}
                onClick={() => executeAction("/api/jobs/scrape", "Scraping")}>
                {loadingAction === "Scraping" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                Executar Scraping Agora
              </Button>
              <Button size="sm" variant="outline" className="gap-2" disabled={!!loadingAction}
                onClick={() => executeAction("/api/jobs/enrich-all", "Enriquecimento")}>
                {loadingAction === "Enriquecimento" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Zap className="h-4 w-4" />}
                Enriquecer Todos os Produtos
              </Button>
              <Button size="sm" variant="outline" className="gap-2" disabled={!!loadingAction}
                onClick={() => executeAction("/api/jobs/train-model", "Treinamento")}>
                {loadingAction === "Treinamento" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Brain className="h-4 w-4" />}
                Treinar Modelo
              </Button>
              <Button size="sm" variant="outline" className="gap-2" disabled={!!loadingAction}
                onClick={() => executeAction("/api/recommendations/refresh", "Recomendações")}>
                {loadingAction === "Recomendações" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                Atualizar Recomendações
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* History table */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Histórico de Jobs</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-20">Fila</TableHead>
                  <TableHead className="w-20">Status</TableHead>
                  <TableHead>Job</TableHead>
                  <TableHead className="w-24">Duração</TableHead>
                  <TableHead className="w-36">Data</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {allJobs.slice(0, 20).map((job, i) => (
                  <TableRow key={i}>
                    <TableCell>
                      <Badge variant="outline" className="text-[10px]">
                        {queueConfig[job.queue]?.label || job.queue}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={`text-[10px] ${job.status === "completed" ? "bg-green-500/10 text-green-600" : "bg-red-500/10 text-red-600"}`}>
                        {job.status === "completed" ? "✅ OK" : "❌ Falha"}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-xs truncate max-w-32">{job.name}</TableCell>
                    <TableCell className="text-xs text-muted-foreground">{job.duration || "—"}</TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {job.createdAt ? new Date(job.createdAt).toLocaleString("pt-BR") : "—"}
                    </TableCell>
                  </TableRow>
                ))}
                {allJobs.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center text-muted-foreground py-8">
                      Nenhum job executado ainda.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}
