# ============================================
# AfiliaML — Repositório de Eventos de Compartilhamento (Redis)
# ============================================

import uuid
import time
from datetime import datetime, timezone
from app.utils.redis_client import get_redis
from app.repositories.product_repo import to_redis_hash, from_redis_hash


class ShareEventRepository:
    """Repositório de eventos de compartilhamento usando Redis."""

    async def registrar(
        self,
        product_id: str,
        channel: str,
        message: str,
        campaign_id: str | None = None,
    ) -> dict:
        r = get_redis()
        id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        timestamp = int(time.time() * 1000)

        evento = {
            "id": id,
            "productId": product_id,
            "campaignId": campaign_id or "",
            "channel": channel,
            "message": message,
            "createdAt": now,
        }

        pipe = r.pipeline()
        pipe.hset(f"share:{id}", mapping=to_redis_hash(evento))
        pipe.zadd("shares:all", {id: timestamp})
        pipe.zadd(f"shares:product:{product_id}", {id: timestamp})
        await pipe.execute()

        return evento

    async def contar_por_produto(self, product_id: str) -> int:
        r = get_redis()
        return await r.zcard(f"shares:product:{product_id}")

    async def listar_por_produto(self, product_id: str) -> list[dict]:
        r = get_redis()
        ids = await r.zrevrange(f"shares:product:{product_id}", 0, -1)
        if not ids:
            return []

        pipe = r.pipeline()
        for id in ids:
            pipe.hgetall(f"share:{id}")
        results = await pipe.execute()

        return [from_redis_hash(d) for d in results if d]

    async def contar_total(self) -> int:
        r = get_redis()
        return await r.zcard("shares:all")


share_event_repository = ShareEventRepository()
