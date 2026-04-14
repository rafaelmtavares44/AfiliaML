# ============================================
# AfiliaML — Router de Grafo de Produtos
# ============================================

from fastapi import APIRouter
from app.services.graph_mining_service import graph_mining_service
from app.utils.api_response import resposta_sucesso, resposta_erro
from app.utils.redis_client import get_redis
import json

router = APIRouter(prefix="/api/graph", tags=["Grafo"])


@router.get("/visualization")
async def get_visualization():
    """Retorna dados do grafo para visualização no frontend."""
    # Tenta pegar do cache
    r = get_redis()
    cache = await r.get("graph:full")
    if cache:
        graph = json.loads(cache)
    else:
        # Reconstrói se não houver cache
        co_occurrence = await graph_mining_service.build_co_occurrence_graph()
        co_click = await graph_mining_service.build_co_click_graph()
        graph = graph_mining_service.merge_graphs(co_occurrence, co_click)
        await r.setex("graph:full", 3600, json.dumps(graph))

    enriched = await graph_mining_service.enrich_graph_with_features(graph)
    return resposta_sucesso(enriched, "Grafo de visualização carregado")


@router.get("/stats")
async def get_stats():
    """Retorna estatísticas de análise do grafo."""
    r = get_redis()
    cache = await r.get("graph:full")
    if not cache:
        return resposta_erro("Grafo não processado. Execute o treinamento de ML primeiro.", 404)
    
    graph = json.loads(cache)
    stats = graph_mining_service.get_graph_stats(graph)
    return resposta_sucesso(stats, "Estatísticas do grafo")


@router.post("/process")
async def process_graph():
    """Força o processamento do grafo e cálculo do PageRank."""
    co_occurrence = await graph_mining_service.build_co_occurrence_graph()
    co_click = await graph_mining_service.build_co_click_graph()
    graph = graph_mining_service.merge_graphs(co_occurrence, co_click)
    
    # Calcular PageRank
    scores = graph_mining_service.calculate_pagerank(graph)
    
    # Salvar resultados
    r = get_redis()
    await r.setex("graph:full", 3600, json.dumps(graph))
    
    if scores:
        await r.hset("graph:pagerank", mapping={pid: str(s) for pid, s in scores.items()})
        
    return resposta_sucesso(
        {"nodes": len(graph["nodes"]), "edges": len(graph["edges"])}, 
        "Grafo processado e PageRank atualizado"
    )
