# ============================================
# AfiliaML — Repositório de Links de Afiliado (Redis)
# ============================================

import uuid
from datetime import datetime, timezone
from app.utils.redis_client import get_redis
from app.repositories.product_repo import to_redis_hash, from_redis_hash


class AffiliateLinkRepository:
    """Repositório de logs de links de afiliado usando Redis."""

    async def registrar(
        self,
        product_id: str,
        original_url: str,
        generated_url: str | None,
        strategy: str,
        status: str,
        error_message: str | None = None,
    ) -> dict:
        r = get_redis()
        id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        log = {
            "id": id,
            "productId": product_id,
            "originalUrl": original_url,
            "generatedUrl": generated_url or "",
            "strategy": strategy,
            "status": status,
            "errorMessage": error_message or "",
            "createdAt": now,
        }

        pipe = r.pipeline()
        pipe.hset(f"affiliate_log:{id}", mapping=to_redis_hash(log))
        pipe.zadd(
            f"affiliate_logs:product:{product_id}",
            {id: int(datetime.now(timezone.utc).timestamp() * 1000)},
        )
        pipe.zadd(
            "affiliate_logs:all",
            {id: int(datetime.now(timezone.utc).timestamp() * 1000)},
        )
        await pipe.execute()

        return log

    async def listar_por_produto(self, product_id: str) -> list[dict]:
        r = get_redis()
        ids = await r.zrevrange(
            f"affiliate_logs:product:{product_id}", 0, -1
        )
        if not ids:
            return []

        pipe = r.pipeline()
        for id in ids:
            pipe.hgetall(f"affiliate_log:{id}")
        results = await pipe.execute()

        return [from_redis_hash(d) for d in results if d]

    async def contar_total(self) -> int:
        r = get_redis()
        return await r.zcard("affiliate_logs:all")


affiliate_link_repository = AffiliateLinkRepository()
