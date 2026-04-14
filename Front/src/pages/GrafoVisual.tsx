// ============================================
// AfiliaML — Visualização do Grafo de Produtos
// Materia: Graph Mining - Visualização de redes de co-ocorrência e centralidade.
// ============================================

import { useState, useRef, useMemo } from "react";
import { Layout } from "@/components/layout/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Network, RefreshCw, Info, DollarSign, BarChart3, Tag, Loader2 } from "lucide-react";
import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";

const API = import.meta.env.VITE_API_URL || "http://localhost:3333";

const COMMUNITY_COLORS = [
  "#8b5cf6", "#3b82f6", "#22c55e", "#ef4444", "#f59e0b",
  "#ec4899", "#14b8a6", "#f97316", "#6366f1", "#06b6d4",
];

interface GNode { id: string; title?: string; category?: string; x: number; y: number; vx: number; vy: number; community: number; pageRank: number; price?: number; discountPct?: number; }
interface GEdge { source: string; target: string; weight: number; }

// Force-directed layout (Técnica de Simulação Física)
function forceLayout(nodes: GNode[], edges: GEdge[], width: number, height: number, iterations: number = 60) {
  const k = Math.sqrt((width * height) / Math.max(nodes.length, 1)) * 0.8;

  for (let iter = 0; iter < iterations; iter++) {
    const temp = 1 - iter / iterations;
    const cooling = Math.max(0.01, temp * 5);

    // Repulsão entre nós
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[i].x - nodes[j].x;
        const dy = nodes[i].y - nodes[j].y;
        const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
        const force = (k * k) / dist;
        const fx = (dx / dist) * force * cooling;
        const fy = (dy / dist) * force * cooling;
        nodes[i].vx += fx;
        nodes[i].vy += fy;
        nodes[j].vx -= fx;
        nodes[j].vy -= fy;
      }
    }

    // Atração pelas arestas
    const nodeMap = new Map(nodes.map((n) => [n.id, n]));
    for (const edge of edges) {
      const a = nodeMap.get(typeof edge.source === 'string' ? edge.source : (edge.source as any).id);
      const b = nodeMap.get(typeof edge.target === 'string' ? edge.target : (edge.target as any).id);
      if (!a || !b) continue;
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
      const force = (dist * dist) / k * (edge.weight || 1) * 0.05 * cooling;
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;
      a.vx += fx;
      a.vy += fy;
      b.vx -= fx;
      b.vy -= fy;
    }

    // Aplicar velocidade com dissipação e gravidade central
    for (const node of nodes) {
      // Gravidade leve para o centro
      node.vx += (width / 2 - node.x) * 0.01;
      node.vy += (height / 2 - node.y) * 0.01;

      node.x += node.vx * 0.4;
      node.y += node.vy * 0.4;
      node.vx *= 0.6;
      node.vy *= 0.6;
      
      node.x = Math.max(20, Math.min(width - 20, node.x));
      node.y = Math.max(20, Math.min(height - 20, node.y));
    }
  }
}

export default function GrafoVisual() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  const SVG_W = 800;
  const SVG_H = 600;

  // Materia: Data Mining - Coleta de propriedades grafocêntricas (PageRank, Stats)
  const { data: stats } = useQuery({
    queryKey: ["graph", "stats"],
    queryFn: async () => {
      const res = await fetch(`${API}/api/graph/stats`);
      const d = await res.json();
      return d.data;
    }
  });

  const { data: graphData, isLoading: loadingGraph } = useQuery({
    queryKey: ["graph", "viz"],
    queryFn: async () => {
      const res = await fetch(`${API}/api/graph/visualization`);
      const d = await res.json();
      
      // Mapear PageRank do Redis secundário (destaques do dia costumam ter PR calculado)
      const prRes = await fetch(`${API}/api/recommendations/daily`);
      const prData = await prRes.json();
      const prMap = new Map((prData.data || []).map((i: any) => [i.productId, i.pageRankScore]));

      const nodes: GNode[] = (d.data?.nodes || []).map((n: any, i: number) => ({
        ...n,
        x: SVG_W / 2 + (Math.random() - 0.5) * SVG_W * 0.6,
        y: SVG_H / 2 + (Math.random() - 0.5) * SVG_H * 0.6,
        vx: 0, vy: 0,
        community: n.community || (i % 10), 
        pageRank: prMap.get(n.id) || 0.01
      }));

      const edges: GEdge[] = d.data?.edges || [];
      forceLayout(nodes, edges, SVG_W, SVG_H, 100);
      return { nodes, edges };
    }
  });

  const rebuildMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch(`${API}/api/graph/process`, { method: "POST" });
      if (!res.ok) throw new Error("Erro ao processar");
      return res.json();
    },
    onSuccess: () => {
      toast({ title: "✅ Grafo reconstruído!" });
      queryClient.invalidateQueries({ queryKey: ["graph"] });
    }
  });

  const selectedNode = useMemo(() => 
    graphData?.nodes.find(n => n.id === selectedNodeId), 
    [graphData, selectedNodeId]
  );

  const maxPR = useMemo(() => 
    Math.max(...(graphData?.nodes.map(n => n.pageRank) || [0.001]), 0.001), 
    [graphData]
  );

  const communityStats = useMemo(() => {
    const counts = new Map<number, number>();
    graphData?.nodes.forEach(n => {
      counts.set(n.community, (counts.get(n.community) || 0) + 1);
    });
    return Array.from(counts.entries()).sort((a, b) => b[1] - a[1]).slice(0, 10);
  }, [graphData]);

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Network className="h-6 w-6 text-blue-500" /> Grafo de Produtos
            </h1>
            <p className="text-sm text-muted-foreground">Relacionamentos por co-ocorrência em campanhas e cliques.</p>
          </div>
          <Button onClick={() => rebuildMutation.mutate()} disabled={rebuildMutation.isPending} variant="outline" size="sm" className="gap-2 shadow-sm">
            <RefreshCw className={`h-4 w-4 ${rebuildMutation.isPending ? "animate-spin" : ""}`} />
            Reanalisar Grafo
          </Button>
        </div>

        {stats && (
          <div className="grid gap-3 grid-cols-2 md:grid-cols-4">
            <Card className="bg-muted/30 border-none shadow-sm"><CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-primary">{stats.numberOfNodes}</p>
              <p className="text-[10px] uppercase font-bold text-muted-foreground">Produtos (Nós)</p>
            </CardContent></Card>
            <Card className="bg-muted/30 border-none shadow-sm"><CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-blue-500">{stats.numberOfEdges}</p>
              <p className="text-[10px] uppercase font-bold text-muted-foreground">Links (Arestas)</p>
            </CardContent></Card>
            <Card className="bg-muted/30 border-none shadow-sm"><CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-purple-500">{stats.averageDegree}</p>
              <p className="text-[10px] uppercase font-bold text-muted-foreground">Grau Médio</p>
            </CardContent></Card>
            <Card className="bg-muted/30 border-none shadow-sm"><CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-emerald-500">{stats.densidade}</p>
              <p className="text-[10px] uppercase font-bold text-muted-foreground">Densidade</p>
            </CardContent></Card>
          </div>
        )}

        <div className="grid gap-4 lg:grid-cols-4">
          <Card className="lg:col-span-3 border-border/40 bg-card overflow-hidden">
            <CardContent className="p-0 relative">
              {loadingGraph ? (
                <div className="flex flex-col items-center justify-center h-[600px] text-muted-foreground gap-4">
                  <Loader2 className="h-10 w-10 animate-spin opacity-20" />
                  <p className="text-sm animate-pulse">Computando layout do grafo...</p>
                </div>
              ) : (
                <svg ref={svgRef} viewBox={`0 0 ${SVG_W} ${SVG_H}`} className="w-full h-[600px] bg-background">
                  <defs>
                    <radialGradient id="nodeGradient">
                      <stop offset="0%" stopColor="white" stopOpacity="0.4" />
                      <stop offset="100%" stopColor="transparent" stopOpacity="0" />
                    </radialGradient>
                  </defs>
                  
                  {/* Edges */}
                  <g>
                    {graphData?.edges.map((e, i) => {
                      const a = graphData.nodes.find(n => n.id === (typeof e.source === 'string' ? e.source : (e.source as any).id));
                      const b = graphData.nodes.find(n => n.id === (typeof e.target === 'string' ? e.target : (e.target as any).id));
                      if (!a || !b) return null;
                      return (
                        <line key={i} x1={a.x} y1={a.y} x2={b.x} y2={b.y}
                          stroke="#cbd5e1" strokeWidth={Math.max(0.5, (e.weight || 1) * 0.3)}
                          opacity={0.3} />
                      );
                    })}
                  </g>
                  
                  {/* Nodes */}
                  <g>
                    {graphData?.nodes.map((node) => {
                      const radius = 5 + (node.pageRank / maxPR) * 15;
                      const color = COMMUNITY_COLORS[node.community % 10];
                      const isSelected = selectedNodeId === node.id;
                      
                      return (
                        <g key={node.id} onClick={() => setSelectedNodeId(node.id)} style={{ cursor: "pointer" }}
                           className="transition-all duration-300">
                          {isSelected && (
                             <circle cx={node.x} cy={node.y} r={radius + 8} fill={color} opacity={0.15} className="animate-pulse" />
                          )}
                          <circle cx={node.x} cy={node.y} r={radius}
                            fill={color} stroke={isSelected ? "white" : "none"} strokeWidth={2}
                            opacity={0.9} className="hover:opacity-100 shadow-lg" />
                        </g>
                      );
                    })}
                  </g>
                </svg>
              )}
            </CardContent>
          </Card>

          <div className="space-y-4">
            <Card className="border-border/40">
              <CardHeader className="p-3 border-b border-border/40">
                <CardTitle className="text-xs uppercase tracking-wider font-bold text-muted-foreground flex items-center gap-2">
                  <Info className="h-3.5 w-3.5" /> Nichos Identificados
                </CardTitle>
              </CardHeader>
              <CardContent className="p-3 space-y-2">
                {communityStats.map(([community, count]) => (
                  <div key={community} className="flex items-center gap-2 text-xs">
                    <div className="w-2.5 h-2.5 rounded-full" style={{ background: COMMUNITY_COLORS[community % 10] }} />
                    <span className="font-medium">Nicho #{community}</span>
                    <Badge variant="outline" className="text-[9px] ml-auto bg-muted/50 border-none">{count} prod.</Badge>
                  </div>
                ))}
              </CardContent>
            </Card>

            {selectedNode ? (
              <Card className="border-primary/20 shadow-lg animate-in fade-in slide-in-from-right-2">
                <CardHeader className="p-3 bg-primary/5 border-b border-primary/10">
                  <CardTitle className="text-xs uppercase font-bold text-primary">Detalhes do Produto</CardTitle>
                </CardHeader>
                <CardContent className="p-3 space-y-4">
                  <div>
                    <h3 className="text-xs font-bold line-clamp-3 leading-tight mb-2">{selectedNode.title || "Produto sem título"}</h3>
                    <div className="flex items-center gap-2">
                       <Badge variant="outline" className="text-[10px] bg-muted/50 border-none flex items-center gap-1">
                        <Tag className="h-3 w-3" /> {selectedNode.category || "Geral"}
                      </Badge>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div className="bg-muted/30 p-2 rounded-lg">
                      <p className="text-[9px] uppercase font-bold text-muted-foreground mb-1">Preço Atual</p>
                      <div className="flex items-center gap-1 text-primary font-bold">
                        <DollarSign className="h-3 w-3" />
                        <span className="text-sm">{(selectedNode.price || 0).toFixed(2)}</span>
                      </div>
                    </div>
                    <div className="bg-muted/30 p-2 rounded-lg">
                      <p className="text-[9px] uppercase font-bold text-muted-foreground mb-1">PageRank</p>
                      <div className="flex items-center gap-1 text-purple-600 font-bold">
                        <BarChart3 className="h-3 w-3" />
                        <span className="text-sm">{(selectedNode.pageRank * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <div className="flex justify-between text-[9px] uppercase font-bold text-muted-foreground">
                      <span>Centralidade no Grafo</span>
                      <span>{(selectedNode.pageRank / maxPR * 100).toFixed(0)}%</span>
                    </div>
                    <Progress value={(selectedNode.pageRank / maxPR * 100)} className="h-1.5" />
                  </div>

                  <Link to={`/produtos/${selectedNode.id}/insights`}>
                    <Button variant="default" size="sm" className="w-full text-xs font-bold rounded-xl shadow-md h-9">
                      Ver Insights Avançados
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ) : (
              <div className="h-40 flex flex-col items-center justify-center text-center p-4 bg-muted/20 border-2 border-dashed border-border/40 rounded-xl">
                <Network className="h-8 w-8 text-muted-foreground opacity-20 mb-2" />
                <p className="text-[10px] text-muted-foreground font-medium">Clique em um nó do grafo para analisar métricas de rede.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
