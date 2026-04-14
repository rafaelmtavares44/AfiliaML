# ============================================
# AfiliaML — Repositório de Histórico de Preços (Redis)
# ============================================

import uuid
import time
from datetime import datetime, timezone
from app.utils.redis_client import get_redis
from app.repositories.product_repo import to_redis_hash, from_redis_hash


class PriceHistoryRepository:
    """Repositório de histórico de preços usando Redis."""

    async def registrar(
        self, product_id: str, price: float, old_price: float | None = None
    ) -> dict:
        r = get_redis()
        id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        timestamp = int(time.time() * 1000)

        registro = {
            "id": id,
            "productId": product_id,
            "price": price,
            "oldPrice": old_price if old_price else "",
            "scrapedAt": now,
        }

        pipe = r.pipeline()
        pipe.hset(f"price_history:{id}", mapping=to_redis_hash(registro))
        pipe.zadd(f"price_history:product:{product_id}", {id: timestamp})
        await pipe.execute()

        return registro

    async def buscar_por_produto(
        self, product_id: str, limite: int = 30
    ) -> list[dict]:
        r = get_redis()
        ids = await r.zrevrange(
            f"price_history:product:{product_id}", 0, limite - 1
        )
        if not ids:
            return []

        pipe = r.pipeline()
        for id in ids:
            pipe.hgetall(f"price_history:{id}")
        results = await pipe.execute()

        registros = []
        for data in results:
            if data:
                parsed = from_redis_hash(data)
                # Garantir que price é float
                if "price" in parsed and parsed["price"] is not None:
                    parsed["price"] = float(parsed["price"])
                registros.append(parsed)

        return registros

    async def calcular_tendencia(self, product_id: str) -> str:
        """Calcula a tendência de preço: subindo, caindo ou estavel."""
        historico = await self.buscar_por_produto(product_id, 5)

        if len(historico) < 2:
            return "estavel"

        precos = [float(h.get("price", 0)) for h in historico if h.get("price")]
        if len(precos) < 2:
            return "estavel"

        # historico está ordenado desc (mais recente primeiro)
        mais_recente = precos[0]
        mais_antigo = precos[-1]

        if mais_antigo == 0:
            return "estavel"

        variacao = (mais_recente - mais_antigo) / mais_antigo

        if variacao > 0.03:
            return "subindo"
        elif variacao < -0.03:
            return "caindo"
        return "estavel"


price_history_repository = PriceHistoryRepository()
