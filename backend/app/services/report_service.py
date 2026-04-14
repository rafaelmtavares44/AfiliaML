# ============================================
# AfiliaML — Service de Relatórios
# Exportação de dados em CSV
# ============================================

from app.utils.redis_client import get_redis
from app.repositories.product_repo import product_repository
from app.repositories.click_event_repo import click_event_repository
from app.repositories.share_event_repo import share_event_repository
from app.repositories.price_history_repo import price_history_repository


class ReportService:

    async def gerar_relatorio_produtos(self) -> list[dict]:
        produtos = await product_repository.listar_todos()
        rows = []

        for produto in produtos:
            if not produto:
                continue
            pid = str(produto.get("id", ""))
            price = float(produto.get("price") or 0)
            old_price = float(produto.get("oldPrice") or 0)
            discount_pct = (
                round(((old_price - price) / old_price) * 100)
                if old_price > price else 0
            )

            clicks = await click_event_repository.contar_por_produto(pid)
            shares = await share_event_repository.contar_por_produto(pid)

            r = get_redis()
            ml_score = 0.0
            try:
                score_str = await r.hget("graph:pagerank", pid)
                ml_score = float(score_str) if score_str else 0.0
            except Exception:
                pass

            tendencia = "estavel"
            try:
                tendencia = await price_history_repository.calcular_tendencia(pid)
            except Exception:
                pass

            rows.append({
                "id": pid,
                "titulo": produto.get("title", ""),
                "categoria": produto.get("category", ""),
                "loja": produto.get("store", "mercadolivre"),
                "preco": price,
                "precoAntigo": old_price,
                "descontoPct": discount_pct,
                "linkAfiliado": produto.get("affiliateUrl", ""),
                "cliques30d": clicks,
                "compartilhamentos30d": shares,
                "mlScore": round(ml_score, 4),
                "tendenciaPreco": tendencia,
                "criadoEm": produto.get("createdAt", ""),
            })

        return rows

    async def gerar_relatorio_cliques(
        self, data_inicio: str | None = None, data_fim: str | None = None
    ) -> list[dict]:
        from datetime import datetime

        clicks = await click_event_repository.listar_todos(10000)
        filtrados = clicks

        if data_inicio:
            inicio = datetime.fromisoformat(data_inicio).timestamp() * 1000
            filtrados = [
                c for c in filtrados
                if datetime.fromisoformat(str(c.get("createdAt", ""))).timestamp() * 1000 >= inicio
            ]
        if data_fim:
            fim = (datetime.fromisoformat(data_fim).timestamp() + 86400) * 1000
            filtrados = [
                c for c in filtrados
                if datetime.fromisoformat(str(c.get("createdAt", ""))).timestamp() * 1000 <= fim
            ]

        return [
            {
                "id": c.get("id", ""),
                "produtoId": c.get("productId", ""),
                "canal": c.get("channel", "direto"),
                "campanhaId": c.get("campaignId", ""),
                "ipHash": c.get("ip", ""),
                "data": c.get("createdAt", ""),
            }
            for c in filtrados
        ]

    async def gerar_relatorio_comissao(self, taxa: float = 0.08) -> list[dict]:
        produtos = await product_repository.listar_todos()
        rows = []
        total_comissao = 0.0
        total_cliques = 0
        total_conversoes = 0

        for produto in produtos:
            if not produto:
                continue
            pid = str(produto.get("id", ""))
            price = float(produto.get("price") or 0)
            clicks = await click_event_repository.contar_por_produto(pid)
            if clicks == 0:
                continue

            conversoes = int(clicks * 0.02)
            comissao = conversoes * price * taxa
            total_cliques += clicks
            total_conversoes += conversoes
            total_comissao += comissao

            rows.append({
                "produtoId": pid,
                "titulo": produto.get("title", ""),
                "preco": price,
                "cliques": clicks,
                "conversoesEstimadas": conversoes,
                "taxaConversao": "2%",
                "taxaComissao": f"{taxa * 100:.0f}%",
                "comissaoEstimada": round(comissao, 2),
            })

        rows.append({
            "produtoId": "TOTAL",
            "titulo": "--- TOTAL ---",
            "preco": 0,
            "cliques": total_cliques,
            "conversoesEstimadas": total_conversoes,
            "taxaConversao": "2%",
            "taxaComissao": f"{taxa * 100:.0f}%",
            "comissaoEstimada": round(total_comissao, 2),
        })

        return rows

    def exportar_csv(self, data: list[dict]) -> str:
        if not data:
            return ""

        headers = list(data[0].keys())
        csv_rows = [",".join(headers)]

        for row in data:
            values = []
            for h in headers:
                val = row.get(h, "")
                s = str(val) if val is not None else ""
                if "," in s or '"' in s or "\n" in s:
                    s = f'"{s.replace(chr(34), chr(34)+chr(34))}"'
                values.append(s)
            csv_rows.append(",".join(values))

        return "\n".join(csv_rows)


report_service = ReportService()
