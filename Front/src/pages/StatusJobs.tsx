// ============================================
// AfiliaML — Monitoramento de Tarefas Agendadas
// Materia: Sistemas Distribuídos - Monitoramento de jobs assíncronos.
// ============================================

import { Layout } from "@/components/layout/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Pause, Play, RefreshCw, Clock, 
  Terminal, Activity, CheckCircle2, AlertCircle, Loader2
} from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";

const API = import.meta.env.VITE_API_URL || "http://localhost:3333";

export default function StatusJobs() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Materia: Computação Paralela - Polling de estado de threads em segundo plano
  const { data, isLoading } = useQuery({
    queryKey: ["jobs", "status"],
    queryFn: async () => {
      const res = await fetch(`${API}/api/jobs/status`);
      const d = await res.json();
      return d.data;
    },
    refetchInterval: 10000, // Atualiza a cada 10s
  });

  const toggleMutation = useMutation({
    mutationFn: async (jobId: string) => {
      const res = await fetch(`${API}/api/jobs/toggle/${jobId}`, { method: "POST" });
      if (!res.ok) throw new Error("Erro ao alternar estado do job");
      return res.json();
    },
    onSuccess: (data) => {
      toast({ title: `📦 Job ${data.data.status}`, description: `A tarefa foi ${data.data.status} com sucesso.` });
      queryClient.invalidateQueries({ queryKey: ["jobs", "status"] });
    }
  });

  const jobs = data?.jobs || [];

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2 text-foreground">
              <Activity className="h-6 w-6 text-emerald-500" /> Status do Sistema
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              Monitoramento em tempo real do agendador baseada em CRON.
            </p>
          </div>
          <Badge variant={data?.scheduler_running ? "default" : "destructive"} className="gap-2 px-3 py-1 rounded-full">
            <span className={`h-2 w-2 rounded-full ${data?.scheduler_running ? "bg-emerald-400 animate-pulse" : "bg-red-400"}`} />
            {data?.scheduler_running ? "Scheduler Online" : "Scheduler Offline"}
          </Badge>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
           <Card className="border-border/40 bg-card shadow-sm"><CardContent className="p-4 flex items-center gap-4">
            <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center"><Terminal className="h-5 w-5 text-primary" /></div>
            <div>
              <p className="text-[10px] uppercase font-bold text-muted-foreground">Jobs Ativos</p>
              <p className="text-xl font-bold">{jobs.filter((j: any) => j.pending).length}</p>
            </div>
          </CardContent></Card>
          <Card className="border-border/40 bg-card shadow-sm"><CardContent className="p-4 flex items-center gap-4">
            <div className="h-10 w-10 rounded-xl bg-blue-500/10 flex items-center justify-center"><Clock className="h-5 w-5 text-blue-500" /></div>
            <div>
              <p className="text-[10px] uppercase font-bold text-muted-foreground">Próxima Janela</p>
              <p className="text-xl font-bold">{jobs[0]?.next_run ? new Date(jobs[0].next_run).toLocaleTimeString() : "--:--"}</p>
            </div>
          </CardContent></Card>
          <Card className="border-border/40 bg-card shadow-sm"><CardContent className="p-4 flex items-center gap-4">
            <div className="h-10 w-10 rounded-xl bg-emerald-500/10 flex items-center justify-center"><CheckCircle2 className="h-5 w-5 text-emerald-500" /></div>
            <div>
              <p className="text-[10px] uppercase font-bold text-muted-foreground">Integridade</p>
              <p className="text-sm font-bold text-emerald-600">Sistemas Operacionais</p>
            </div>
          </CardContent></Card>
        </div>

        <Card className="border-border/40 shadow-md">
          <CardHeader className="border-b border-border/40 bg-muted/20">
            <CardTitle className="text-sm font-bold flex items-center gap-2">
              <RefreshCw className="h-4 w-4" /> APScheduler Tasks
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-muted/30 text-muted-foreground text-[10px] uppercase font-bold">
                  <tr>
                    <th className="text-left p-4">Tarefa</th>
                    <th className="text-left p-4">Trigger</th>
                    <th className="text-left p-4">Próxima Execução</th>
                    <th className="text-center p-4">Status</th>
                    <th className="text-right p-4">Ação</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/40 font-medium">
                  {isLoading ? (
                    <tr><td colSpan={5} className="p-8 text-center text-muted-foreground animate-pulse">Carregando tarefas...</td></tr>
                  ) : jobs.length === 0 ? (
                    <tr><td colSpan={5} className="p-8 text-center text-muted-foreground">Nenhum job encontrado.</td></tr>
                  ) : (
                    jobs.map((job: any) => (
                      <tr key={job.id} className="hover:bg-muted/10 transition-colors">
                        <td className="p-4">
                          <div className="flex flex-col">
                            <span className="font-bold">{job.name || job.id}</span>
                            <span className="text-[10px] text-muted-foreground">ID: {job.id}</span>
                          </div>
                        </td>
                        <td className="p-4"><code className="bg-muted px-2 py-0.5 rounded text-[11px]">{job.trigger}</code></td>
                        <td className="p-4 text-xs">
                          {job.next_run ? new Date(job.next_run).toLocaleString('pt-BR') : "Desativado"}
                        </td>
                        <td className="p-4 text-center">
                          <Badge variant={job.pending ? "default" : "secondary"} className="text-[10px] uppercase font-bold">
                            {job.pending ? "Agendado" : "Pausado"}
                          </Badge>
                        </td>
                        <td className="p-4 text-right">
                          <Button 
                            variant="outline" 
                            size="sm" 
                            className={`rounded-xl border-border/60 ${job.pending ? 'hover:bg-red-50 text-red-600' : 'hover:bg-emerald-50 text-emerald-600'}`}
                            onClick={() => toggleMutation.mutate(job.id)}
                            disabled={toggleMutation.isPending}
                          >
                            {job.pending ? <Pause className="h-3.5 w-3.5 mr-1" /> : <Play className="h-3.5 w-3.5 mr-1" />}
                            {job.pending ? "Pausar" : "Ativar"}
                          </Button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        <div className="rounded-2xl bg-blue-500/10 border border-blue-200 p-4 flex gap-4 items-start">
          <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
          <div className="space-y-1">
            <h4 className="text-sm font-bold text-blue-900">Nota Acadêmica: Ética em IA</h4>
            <p className="text-xs text-blue-700 leading-relaxed">
              O monitoramento de jobs automáticos (scrapers) garante o cumprimento dos limites de requisição (*rate limiting*) respeitando os termos de uso da plataforma parceira e a ética no tratamento de dados públicos.
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
}
