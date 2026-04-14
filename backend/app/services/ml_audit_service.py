# ============================================
# AfiliaML — Service de Auditoria ML
# Registra predições para rastreabilidade
# ============================================

import uuid
import json
from datetime import datetime, timezone
from app.utils.redis_client import get_redis


class MLAuditService:
    async def registrar_predicao(self, dados: dict) -> None:
        r = get_redis()
        id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)

        log = {
            "id": id,
            "productId": dados.get("productId", ""),
            "score": str(dados.get("score", 0)),
            "classification": dados.get("classification", ""),
            "featuresSnapshot": json.dumps(dados.get("featuresSnapshot", {})),
            "modelVersion": dados.get("modelVersion", ""),
            "createdAt": now,
        }

        pipe = r.pipeline()
        pipe.hset(f"ml_prediction:{id}", mapping=log)
        pipe.zadd("ml_predictions:all", {id: timestamp})
        pipe.zadd(
            f"ml_predictions:product:{dados.get('productId', '')}",
            {id: timestamp},
        )
        await pipe.execute()

    async def listar_predicoes(
        self, product_id: str | None = None, limite: int = 50
    ) -> list[dict]:
        r = get_redis()
        if product_id:
            ids = await r.zrevrange(
                f"ml_predictions:product:{product_id}", 0, limite - 1
            )
        else:
            ids = await r.zrevrange("ml_predictions:all", 0, limite - 1)

        if not ids:
            return []

        pipe = r.pipeline()
        for id in ids:
            pipe.hgetall(f"ml_prediction:{id}")
        results = await pipe.execute()

        return [d for d in results if d]


ml_audit_service = MLAuditService()
