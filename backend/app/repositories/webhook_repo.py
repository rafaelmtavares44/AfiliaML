# ============================================
# AfiliaML — Repositório de Webhooks (Redis)
# ============================================

import uuid
import json
from datetime import datetime, timezone
from app.utils.redis_client import get_redis
from app.repositories.product_repo import to_redis_hash


class WebhookRepository:
    """Repositório de logs de webhook usando Redis."""

    async def registrar(
        self, provider: str, payload: dict, status: str = "recebido"
    ) -> dict:
        r = get_redis()
        id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        log = {
            "id": id,
            "provider": provider,
            "payload": json.dumps(payload),
            "status": status,
            "createdAt": now,
        }

        pipe = r.pipeline()
        pipe.hset(f"webhook:{id}", mapping=to_redis_hash(log))
        pipe.zadd(
            "webhooks:all",
            {id: int(datetime.now(timezone.utc).timestamp() * 1000)},
        )
        await pipe.execute()

        return log


webhook_repository = WebhookRepository()
