// ============================================
// AfiliaML — Visualização do Grafo de Produtos
// NOVO: Fase 3.2 — Force-directed graph em SVG puro
// ============================================

import { useState, useEffect, useRef, useCallback } from "react";
import { Layout } from "@/components/layout/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Network, RefreshCw, Info } from "lucide-react";
import { Link } from "react-router-dom";

const API = "http://localhost:3333";

const COMMUNITY_COLORS = [
  "#8b5cf6", "#3b82f6", "#22c55e", "#ef4444", "#f59e0b",
  "#ec4899", "#14b8a6", "#f97316", "#6366f1", "#06b6d4",
];

interface GNode { id: string; title?: string; category?: string; x: number; y: number; vx: number; vy: number; community: number; pageRank: number; }
interface GEdge { source: string; target: string; weight: number; }

// Force-directed layout (TypeScript puro)
function forceLayout(nodes: GNode[], edges: GEdge[], width: number, height: number, iterations: number = 80) {
  const k = Math.sqrt((width * height) / Math.max(nodes.length, 1));

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
      const a = nodeMap.get(edge.source);
      const b = nodeMap.get(edge.target);
      if (!a || !b) continue;
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
      const force = (dist * dist) / k * edge.weight * 0.1 * cooling;
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;
      a.vx += fx;
      a.vy += fy;
      b.vx -= fx;
      b.vy -= fy;
    }

    // Aplicar velocidade com dissipação
    for (const node of nodes) {
      node.x += node.vx * 0.5;
      node.y += node.vy * 0.5;
      node.vx *= 0.7;
      node.vy *= 0.7;
      // Manter dentro dos bounds
      node.x = Math.max(30, Math.min(width - 30, node.x));
      node.y = Math.max(30, Math.min(height - 30, node.y));
    }
  }
}

export default function GrafoVisual() {
  const [stats, setStats] = useState<any>(null);
  const [nodes, setNodes] = useState<GNode[]>([]);
  const [edges, setEdges] = useState<GEdge[]>([]);
  const [communities, setCommunities] = useState<Map<number, number>>(new Map());
  const [selectedNode, setSelectedNode] = useState<GNode | null>(null);
  const [loading, setLoading] = useState(true);
  const svgRef = useRef<SVGSVGElement>(null);

  const SVG_W = 800;
  const SVG_H = 600;

  useEffect(() => { fetchGraph(); }, []);

  const fetchGraph = async () => {
    setLoading(true);
    try {
      // Construir grafo
      const buildRes = await fetch(`${API}/api/graph/build`);
      const buildData = await buildRes.json();
      if (buildData.success) setStats(buildData.data.stats);

      // Buscar grafo completo do cache
      const graphRes = await fetch(`${API}/api/graph/pagerank`);
      const graphData = await graphRes.json();

      const commRes = await fetch(`${API}/api/graph/communities`);
      const commData = await commRes.json();

      // Mapear comunidades
      const commMap = new Map<string, number>();
      if (commData.success) {
        (commData.data || []).forEach((c: any, communityIdx: number) => {
          (c.members || []).forEach((m: any) => {
            commMap.set(m.productId, communityIdx);
          });
        });
      }

      // Criar nós
      const prNodes: GNode[] = (graphData.data || []).slice(0, 80).map((item: any, i: number) => ({
        id: item.productId,
        title: item.title || "Produto",
        category: "",
        x: SVG_W / 2 + (Math.random() - 0.5) * SVG_W * 0.8,
        y: SVG_H / 2 + (Math.random() - 0.5) * SVG_H * 0.8,
        vx: 0, vy: 0,
        community: commMap.get(item.productId) ?? i,
        pageRank: item.score || 0.001,
      }));

      // Aplicar force layout
      forceLayout(prNodes, [], SVG_W, SVG_H, 80);

      setNodes(prNodes);
      setEdges([]);

      // Contar comunidades
      const commCount = new Map<number, number>();
      prNodes.forEach((n) => {
        commCount.set(n.community % 10, (commCount.get(n.community % 10) || 0) + 1);
      });
      setCommunities(commCount);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const maxPR = Math.max(...nodes.map((n) => n.pageRank), 0.001);

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Network className="h-6 w-6 text-blue-500" /> Grafo de Produtos
            </h1>
            <p className="text-sm text-muted-foreground">Visualização interativa das relações entre produtos</p>
          </div>
          <Button onClick={fetchGraph} disabled={loading} variant="outline" size="sm" className="gap-2">
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            Reconstruir
          </Button>
        </div>

        {/* Stats cards */}
        {stats && (
          <div className="grid gap-3 grid-cols-2 md:grid-cols-4">
            <Card><CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-primary">{stats.numberOfNodes}</p>
              <p className="text-xs text-muted-foreground">Nós (Produtos)</p>
            </CardContent></Card>
            <Card><CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-blue-500">{stats.numberOfEdges}</p>
              <p className="text-xs text-muted-foreground">Arestas (Relações)</p>
            </CardContent></Card>
            <Card><CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-purple-500">{stats.averageDegree}</p>
              <p className="text-xs text-muted-foreground">Grau Médio</p>
            </CardContent></Card>
            <Card><CardContent className="p-4 text-center">
              <p className="text-2xl font-bold text-emerald-500">{stats.densidade}</p>
              <p className="text-xs text-muted-foreground">Densidade</p>
            </CardContent></Card>
          </div>
        )}

        <div className="grid gap-4 lg:grid-cols-4">
          {/* SVG Graph */}
          <Card className="lg:col-span-3">
            <CardContent className="p-2">
              {loading ? (
                <div className="flex items-center justify-center h-[600px] text-muted-foreground">
                  Calculando layout do grafo...
                </div>
              ) : (
                <svg ref={svgRef} viewBox={`0 0 ${SVG_W} ${SVG_H}`} className="w-full h-auto border rounded-lg bg-background"
                  style={{ minHeight: 400 }}>
                  {/* Arestas */}
                  {edges.map((e, i) => {
                    const a = nodes.find((n) => n.id === e.source);
                    const b = nodes.find((n) => n.id === e.target);
                    if (!a || !b) return null;
                    return (
                      <line key={i} x1={a.x} y1={a.y} x2={b.x} y2={b.y}
                        stroke="#94a3b8" strokeWidth={Math.max(0.5, e.weight * 0.5)}
                        opacity={Math.min(0.6, e.weight * 0.2)} />
                    );
                  })}
                  {/* Nós */}
                  {nodes.map((node) => {
                    const radius = Math.max(3, Math.min(12, (node.pageRank / maxPR) * 12));
                    const color = COMMUNITY_COLORS[node.community % 10];
                    const isSelected = selectedNode?.id === node.id;
                    return (
                      <g key={node.id} onClick={() => setSelectedNode(node)} style={{ cursor: "pointer" }}>
                        <circle cx={node.x} cy={node.y} r={radius + (isSelected ? 3 : 0)}
                          fill={color} stroke={isSelected ? "#fff" : "none"} strokeWidth={2}
                          opacity={0.85}>
                          <title>{node.title}</title>
                        </circle>
                      </g>
                    );
                  })}
                </svg>
              )}
            </CardContent>
          </Card>

          {/* Sidebar */}
          <div className="space-y-4">
            {/* Legenda */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Legenda de Nichos</CardTitle>
              </CardHeader>
              <CardContent className="space-y-1">
                {Array.from(communities.entries()).slice(0, 10).map(([community, count]) => (
                  <div key={community} className="flex items-center gap-2 text-xs">
                    <div className="w-3 h-3 rounded-full" style={{ background: COMMUNITY_COLORS[community % 10] }} />
                    <span>Nicho {community}</span>
                    <Badge variant="secondary" className="text-[10px] ml-auto">{count}</Badge>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Detalhes do nó selecionado */}
            {selectedNode && (
              <Card className="border-primary/30">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">Produto Selecionado</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <p className="text-xs font-medium line-clamp-3">{selectedNode.title}</p>
                  <div className="grid grid-cols-2 gap-2 text-[10px]">
                    <div className="bg-muted/50 rounded p-1.5 text-center">
                      <p className="font-bold">{(selectedNode.pageRank * 100).toFixed(1)}%</p>
                      <p className="text-muted-foreground">PageRank</p>
                    </div>
                    <div className="bg-muted/50 rounded p-1.5 text-center">
                      <p className="font-bold">Nicho {selectedNode.community}</p>
                      <p className="text-muted-foreground">Comunidade</p>
                    </div>
                  </div>
                  <Link to={`/produtos/${selectedNode.id}/insights`}>
                    <Button variant="default" size="sm" className="w-full text-xs mt-2">
                      Ver Insights Completos
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
