# ============================================
# AfiliaML — Service de Graph Mining
# Construção e análise de grafo de produtos
# ============================================

import json
from app.utils.redis_client import get_redis
from app.repositories.product_repo import product_repository
from app.repositories.price_history_repo import price_history_repository


def _edge_key(a: str, b: str) -> str:
    return f"{a}|{b}" if a < b else f"{b}|{a}"


class GraphMiningService:
    """Serviço de mineração de grafos."""

    async def build_co_occurrence_graph(self) -> dict:
        """Construir grafo de co-ocorrência em campanhas."""
        r = get_redis()
        node_set = set()
        edge_map = {}

        campaign_ids = await r.smembers("campaigns:all")
        for cid in campaign_ids:
            product_ids = list(await r.smembers(f"campaign:{cid}:products"))
            for pid in product_ids:
                node_set.add(pid)

            for i in range(len(product_ids)):
                for j in range(i + 1, len(product_ids)):
                    key = _edge_key(product_ids[i], product_ids[j])
                    if key in edge_map:
                        edge_map[key]["weight"] += 1
                    else:
                        edge_map[key] = {
                            "source": product_ids[i],
                            "target": product_ids[j],
                            "weight": 1,
                        }

        return {
            "nodes": [{"id": id} for id in node_set],
            "edges": list(edge_map.values()),
        }

    async def build_co_click_graph(self) -> dict:
        """Construir grafo de co-clique por IP anonimizado."""
        r = get_redis()
        node_set = set()
        edge_map = {}

        click_ids = await r.zrevrange("clicks:all", 0, -1)
        if not click_ids:
            return {"nodes": [], "edges": []}

        pipe = r.pipeline()
        for id in click_ids:
            pipe.hgetall(f"click:{id}")
        results = await pipe.execute()

        from collections import defaultdict
        from datetime import datetime

        clicks_by_ip = defaultdict(list)
        for data in results:
            if not data:
                continue
            ip = data.get("ip", "")
            if not ip or ip == "unknown":
                continue
            pid = data.get("productId", "")
            try:
                ts = datetime.fromisoformat(data.get("createdAt", "")).timestamp() * 1000
            except Exception:
                continue
            clicks_by_ip[ip].append({"productId": pid, "timestamp": ts})

        WINDOW_MS = 30 * 60 * 1000
        for ip, clicks in clicks_by_ip.items():
            if len(clicks) < 2:
                continue
            clicks.sort(key=lambda c: c["timestamp"])
            for i in range(len(clicks)):
                for j in range(i + 1, len(clicks)):
                    if clicks[j]["timestamp"] - clicks[i]["timestamp"] > WINDOW_MS:
                        break
                    if clicks[i]["productId"] == clicks[j]["productId"]:
                        continue

                    node_set.add(clicks[i]["productId"])
                    node_set.add(clicks[j]["productId"])

                    key = _edge_key(clicks[i]["productId"], clicks[j]["productId"])
                    if key in edge_map:
                        edge_map[key]["weight"] += 1
                    else:
                        edge_map[key] = {
                            "source": clicks[i]["productId"],
                            "target": clicks[j]["productId"],
                            "weight": 1,
                        }

        return {
            "nodes": [{"id": id} for id in node_set],
            "edges": list(edge_map.values()),
        }

    def merge_graphs(self, graph_a: dict, graph_b: dict) -> dict:
        node_set = set()
        edge_map = {}

        for n in graph_a.get("nodes", []):
            node_set.add(n["id"])
        for n in graph_b.get("nodes", []):
            node_set.add(n["id"])

        for e in graph_a.get("edges", []):
            key = _edge_key(e["source"], e["target"])
            edge_map[key] = {**e}

        for e in graph_b.get("edges", []):
            key = _edge_key(e["source"], e["target"])
            if key in edge_map:
                edge_map[key]["weight"] += e["weight"]
            else:
                edge_map[key] = {**e}

        return {
            "nodes": [{"id": id} for id in node_set],
            "edges": list(edge_map.values()),
        }

    def calculate_pagerank(
        self, graph: dict, iterations: int = 20, damping: float = 0.85
    ) -> dict[str, float]:
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        N = len(nodes)
        if N == 0:
            return {}

        scores = {n["id"]: 1 / N for n in nodes}
        adjacency = {n["id"]: [] for n in nodes}
        out_weight = {n["id"]: 0.0 for n in nodes}

        for e in edges:
            adjacency[e["source"]].append({"neighbor": e["target"], "weight": e["weight"]})
            adjacency[e["target"]].append({"neighbor": e["source"], "weight": e["weight"]})
            out_weight[e["source"]] += e["weight"]
            out_weight[e["target"]] += e["weight"]

        for _ in range(iterations):
            new_scores = {}
            for node in nodes:
                nid = node["id"]
                incoming = 0
                for neighbor in adjacency.get(nid, []):
                    ow = out_weight.get(neighbor["neighbor"], 1)
                    incoming += scores.get(neighbor["neighbor"], 0) * (neighbor["weight"] / ow)
                new_scores[nid] = (1 - damping) / N + damping * incoming
            scores = new_scores

        return scores

    def detect_communities(self, graph: dict) -> dict[str, int]:
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        if not nodes:
            return {}

        import random
        labels = {n["id"]: i for i, n in enumerate(nodes)}
        adjacency = {n["id"]: [] for n in nodes}

        for e in edges:
            adjacency[e["source"]].append({"neighbor": e["target"], "weight": e["weight"]})
            adjacency[e["target"]].append({"neighbor": e["source"], "weight": e["weight"]})

        for _ in range(10):
            shuffled = list(nodes)
            random.shuffle(shuffled)
            changed = False

            for node in shuffled:
                nid = node["id"]
                neighbors = adjacency.get(nid, [])
                if not neighbors:
                    continue

                label_weights = {}
                for n in neighbors:
                    lbl = labels[n["neighbor"]]
                    label_weights[lbl] = label_weights.get(lbl, 0) + n["weight"]

                best_label = max(label_weights, key=label_weights.get)
                if best_label != labels[nid]:
                    labels[nid] = best_label
                    changed = True

            if not changed:
                break

        return labels

    def get_graph_stats(self, graph: dict) -> dict:
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        N = len(nodes)
        E = len(edges)

        degree_map = {n["id"]: 0 for n in nodes}
        for e in edges:
            degree_map[e["source"]] = degree_map.get(e["source"], 0) + 1
            degree_map[e["target"]] = degree_map.get(e["target"], 0) + 1

        total_degree = sum(degree_map.values())
        avg_degree = total_degree / N if N > 0 else 0
        density = (2 * E) / (N * (N - 1)) if N > 1 else 0

        sorted_degrees = sorted(degree_map.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "numberOfNodes": N,
            "numberOfEdges": E,
            "averageDegree": round(avg_degree, 2),
            "densidade": round(density, 4),
            "top10PorGrau": [
                {"productId": pid, "degree": d} for pid, d in sorted_degrees
            ],
        }

    async def enrich_graph_with_features(self, graph: dict) -> dict:
        enriched = []
        for node in graph.get("nodes", []):
            produto = await product_repository.buscar_por_id(node["id"])
            if not produto:
                enriched.append(node)
                continue

            price = float(produto.get("price") or 0)
            old_price = float(produto.get("oldPrice") or 0)
            discount = round(((old_price - price) / old_price) * 100) if old_price > price else 0

            enriched.append({
                "id": node["id"],
                "title": produto.get("title", ""),
                "category": produto.get("category", "sem_categoria"),
                "price": price,
                "ratingAverage": float(produto.get("ratingAverage") or 0),
                "discountPct": discount,
            })

        return {"nodes": enriched, "edges": graph.get("edges", [])}


graph_mining_service = GraphMiningService()
