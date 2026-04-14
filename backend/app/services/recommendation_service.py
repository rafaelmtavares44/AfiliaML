# ============================================
# AfiliaML — Service de Recomendações
# Motor de recomendação combinado: ML + PageRank + Grafo
# ============================================

import json
from app.utils.redis_client import get_redis
from app.repositories.product_repo import product_repository
from app.repositories.click_event_repo import click_event_repository
from app.repositories.price_history_repo import price_history_repository
from app.services.graph_mining_service import graph_mining_service
from app.services.ml_scoring_service import ml_scoring_service

CACHE_TTL = 6 * 60 * 60  # 6 horas


async def _get_graph() -> dict | None:
    r = get_redis()
    data = await r.get("graph:full")
    return json.loads(data) if data else None


async def _get_ml_score(product_id: str) -> float:
    try:
        prediction = await ml_scoring_service.predict(product_id)
        return prediction["score"]
    except Exception:
        return 0.0


async def _get_pagerank_score(product_id: str) -> float:
    r = get_redis()
    score = await r.hget("graph:pagerank", product_id)
    return float(score) if score else 0.0


def _combined_score(ml: float, pr: float, edge: float = 0.0) -> float:
    return round((0.4 * ml + 0.4 * pr + 0.2 * edge) * 10000) / 10000


class RecommendationService:

    async def get_daily_top_products(self, limit: int = 10) -> list[dict]:
        all_products = await product_repository.listar_todos()
        results = []
        seen = set()

        # 1. Queda de preço
        for produto in all_products[:50]:
            if not produto:
                continue
            pid = str(produto.get("id", ""))
            try:
                historico = await price_history_repository.buscar_por_produto(pid, 2)
                if len(historico) >= 2:
                    latest = float(historico[0].get("price", 0))
                    previous = float(historico[1].get("price", 0))
                    if previous > 0 and latest < previous:
                        drop = ((previous - latest) / previous) * 100
                        if drop > 3 and pid not in seen:
                            seen.add(pid)
                            ml_s = await _get_ml_score(pid)
                            pr_s = await _get_pagerank_score(pid)
                            results.append({
                                "productId": pid,
                                "title": produto.get("title", ""),
                                "category": produto.get("category", "sem_categoria"),
                                "price": float(produto.get("price", 0)),
                                "imageUrl": produto.get("imageUrl", ""),
                                "mlScore": round(ml_s, 4),
                                "pageRankScore": round(pr_s, 4),
                                "combinedScore": _combined_score(ml_s, pr_s),
                                "highlightReason": "queda_de_preco",
                                "reasonText": f"Preço caiu {drop:.0f}% recentemente.",
                            })
            except Exception:
                pass

        # 2. Cliques recentes
        for produto in all_products[:50]:
            if not produto:
                continue
            pid = str(produto.get("id", ""))
            if pid in seen:
                continue
            clicks = await click_event_repository.contar_por_produto(pid)
            if clicks > 0:
                seen.add(pid)
                ml_s = await _get_ml_score(pid)
                pr_s = await _get_pagerank_score(pid)
                results.append({
                    "productId": pid,
                    "title": produto.get("title", ""),
                    "category": produto.get("category", "sem_categoria"),
                    "price": float(produto.get("price", 0)),
                    "imageUrl": produto.get("imageUrl", ""),
                    "mlScore": round(ml_s, 4),
                    "pageRankScore": round(pr_s, 4),
                    "combinedScore": _combined_score(ml_s, pr_s),
                    "highlightReason": "tendencia_de_cliques",
                    "reasonText": f"{clicks} clique(s) registrado(s) — produto com engajamento.",
                })

        # 3. Top ML + PageRank
        for produto in all_products[:30]:
            if not produto:
                continue
            pid = str(produto.get("id", ""))
            if pid in seen:
                continue
            seen.add(pid)
            ml_s = await _get_ml_score(pid)
            pr_s = await _get_pagerank_score(pid)
            combined = _combined_score(ml_s, pr_s)

            old_price = float(produto.get("oldPrice") or 0)
            price = float(produto.get("price") or 0)
            discount_pct = round(((old_price - price) / old_price) * 100) if old_price > price else 0

            results.append({
                "productId": pid,
                "title": produto.get("title", ""),
                "category": produto.get("category", "sem_categoria"),
                "price": price,
                "imageUrl": produto.get("imageUrl", ""),
                "discountPct": discount_pct,
                "mlScore": round(ml_s, 4),
                "pageRankScore": round(pr_s, 4),
                "combinedScore": combined,
                "highlightReason": "alta_relevancia_ml",
                "reasonText": f"Score combinado de ML ({ml_s*100:.0f}%) e PageRank ({pr_s*100:.1f}%).",
            })

        results.sort(key=lambda x: x["combinedScore"], reverse=True)
        return results[:limit]

    async def get_similar_products(self, product_id: str, limit: int = 5) -> list[dict]:
        produto = await product_repository.buscar_por_id(product_id)
        if not produto:
            raise ValueError("Produto não encontrado")

        graph = await _get_graph()
        neighbors = []

        if graph:
            for e in graph.get("edges", []):
                if e["source"] == product_id:
                    neighbors.append({"id": e["target"], "weight": e["weight"]})
                elif e["target"] == product_id:
                    neighbors.append({"id": e["source"], "weight": e["weight"]})

        if not neighbors:
            all_products = await product_repository.listar_todos()
            category = produto.get("category", "")
            for p in all_products:
                if not p or p.get("id") == product_id:
                    continue
                if category and p.get("category") == category:
                    neighbors.append({"id": str(p["id"]), "weight": 1})
                if len(neighbors) >= limit * 3:
                    break
            if not neighbors:
                for p in all_products[: limit * 3]:
                    if not p or p.get("id") == product_id:
                        continue
                    neighbors.append({"id": str(p["id"]), "weight": 0.5})

        results = []
        for n in neighbors:
            p = await product_repository.buscar_por_id(n["id"])
            if not p:
                continue
            ml_s = await _get_ml_score(n["id"])
            pr_s = await _get_pagerank_score(n["id"])
            combined = _combined_score(ml_s, pr_s, n["weight"])
            results.append({
                "productId": n["id"],
                "title": p.get("title", ""),
                "price": float(p.get("price", 0)),
                "imageUrl": p.get("imageUrl", ""),
                "combinedScore": combined,
                "similarityReason": (
                    f"Co-relacionado no grafo com peso {n['weight']}, mesma rede de produtos."
                    if n["weight"] > 0
                    else f"Mesmo segmento de categoria: {p.get('category', 'geral')}."
                ),
            })

        results.sort(key=lambda x: x["combinedScore"], reverse=True)
        return results[:limit]

    async def cache_recommendations(self) -> dict:
        r = get_redis()
        print("📦 Atualizando cache de recomendações...")

        daily = await self.get_daily_top_products(15)
        await r.setex("recommendations:daily", CACHE_TTL, json.dumps(daily))

        channels = ["whatsapp", "instagram", "facebook"]
        summary = {"daily": len(daily)}

        for channel in channels:
            recs = await self.get_daily_top_products(10)  # Simplified
            await r.setex(f"recommendations:channel:{channel}", CACHE_TTL, json.dumps(recs))
            summary[channel] = len(recs)

        print(f"📦 Cache de recomendações atualizado: {summary}")
        return summary

    async def explain_product(self, product_id: str) -> dict:
        produto = await product_repository.buscar_por_id(product_id)
        if not produto:
            raise ValueError("Produto não encontrado")

        ml_s = await _get_ml_score(product_id)
        pr_s = await _get_pagerank_score(product_id)

        graph = await _get_graph()
        community_id = -1
        neighbors = []
        if graph:
            labels = graph_mining_service.detect_communities(graph)
            community_id = labels.get(product_id, -1)

            for e in graph.get("edges", []):
                if e["source"] == product_id or e["target"] == product_id:
                    nid = e["target"] if e["source"] == product_id else e["source"]
                    n = next((n for n in graph["nodes"] if n["id"] == nid), None)
                    neighbors.append({
                        "productId": nid,
                        "title": n.get("title", "Desconhecido") if n else "Desconhecido",
                        "edgeWeight": e["weight"],
                    })
            neighbors.sort(key=lambda x: x["edgeWeight"], reverse=True)
            neighbors = neighbors[:5]

        price_history = []
        try:
            hist = await price_history_repository.buscar_por_produto(product_id, 7)
            price_history = hist[:10]
        except Exception:
            pass

        tendencia = await price_history_repository.calcular_tendencia(product_id)
        combined = _combined_score(ml_s, pr_s)
        title = produto.get("title", "")

        return {
            "productId": product_id,
            "title": title,
            "mlScore": round(ml_s, 4),
            "pageRankScore": round(pr_s, 4),
            "combinedScore": combined,
            "communityId": community_id,
            "topFeatures": [],
            "neighbors": neighbors,
            "priceHistory": price_history,
            "priceTrend": tendencia,
            "reasonText": (
                f'O produto "{title}" tem score combinado de {combined*100:.0f}%. '
                f"O modelo de ML atribuiu {ml_s*100:.0f}% de relevância. "
                f"No grafo, pertence ao nicho {community_id if community_id >= 0 else 'não classificado'} "
                f"com {len(neighbors)} conexões diretas. "
                f"Tendência de preço: {tendencia}."
            ),
        }


recommendation_service = RecommendationService()
