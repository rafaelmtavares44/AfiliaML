# ============================================
# AfiliaML — Repositório de Eventos de Clique (Redis)
# ============================================

import uuid
import time
from datetime import datetime, timezone
from app.utils.redis_client import get_redis
from app.repositories.product_repo import to_redis_hash, from_redis_hash


class ClickEventRepository:
    """Repositório de eventos de clique usando Redis."""

    async def registrar(
        self,
        product_id: str,
        campaign_id: str | None = None,
        channel: str | None = None,
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        r = get_redis()
        id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        timestamp = int(time.time() * 1000)

        evento = {
            "id": id,
            "productId": product_id,
            "campaignId": campaign_id or "",
            "channel": channel or "direto",
            "ip": ip or "",
            "userAgent": user_agent or "",
            "createdAt": now,
        }

        pipe = r.pipeline()
        pipe.hset(f"click:{id}", mapping=to_redis_hash(evento))
        pipe.zadd("clicks:all", {id: timestamp})
        pipe.zadd(f"clicks:product:{product_id}", {id: timestamp})
        if campaign_id:
            pipe.zadd(f"clicks:campaign:{campaign_id}", {id: timestamp})
        await pipe.execute()

        return evento

    async def contar_por_produto(self, product_id: str) -> int:
        r = get_redis()
        return await r.zcard(f"clicks:product:{product_id}")

    async def analytics_por_produto(self, product_id: str) -> list[dict]:
        r = get_redis()
        ids = await r.zrevrange(f"clicks:product:{product_id}", 0, -1)
        if not ids:
            return []

        pipe = r.pipeline()
        for id in ids:
            pipe.hgetall(f"click:{id}")
        results = await pipe.execute()

        return [from_redis_hash(d) for d in results if d]

    async def listar_todos(self, limite: int = 1000) -> list[dict]:
        r = get_redis()
        ids = await r.zrevrange("clicks:all", 0, limite - 1)
        if not ids:
            return []

        pipe = r.pipeline()
        for id in ids:
            pipe.hgetall(f"click:{id}")
        results = await pipe.execute()

        return [from_redis_hash(d) for d in results if d]

    async def contar_total(self) -> int:
        r = get_redis()
        return await r.zcard("clicks:all")


click_event_repository = ClickEventRepository()
