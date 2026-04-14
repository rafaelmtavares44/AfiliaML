# ============================================
# AfiliaML — Repositório de Campanhas (Redis)
# ============================================

import uuid
from datetime import datetime, timezone
from app.utils.redis_client import get_redis
from app.repositories.product_repo import to_redis_hash, from_redis_hash

KEY_ALL_CAMPAIGNS = "campaigns:all"


def _key_campaign(id: str) -> str:
    return f"campaign:{id}"


def _key_campaign_products(id: str) -> str:
    return f"campaign:{id}:products"


class CampaignRepository:
    """Repositório de campanhas usando Redis."""

    async def criar(self, dados: dict) -> dict:
        r = get_redis()
        id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        campanha = {
            "id": id,
            **dados,
            "description": dados.get("description", ""),
            "status": dados.get("status", "ativa"),
            "createdAt": now,
            "updatedAt": now,
        }

        pipe = r.pipeline()
        pipe.hset(_key_campaign(id), mapping=to_redis_hash(campanha))
        pipe.sadd(KEY_ALL_CAMPAIGNS, id)
        await pipe.execute()

        return from_redis_hash(to_redis_hash(campanha))

    async def listar_todas(self) -> list[dict]:
        r = get_redis()
        ids = await r.smembers(KEY_ALL_CAMPAIGNS)
        if not ids:
            return []

        pipe = r.pipeline()
        for id in ids:
            pipe.hgetall(_key_campaign(id))
        results = await pipe.execute()

        campanhas = []
        for data in results:
            if data and len(data) > 0:
                campanhas.append(from_redis_hash(data))

        campanhas.sort(key=lambda c: c.get("createdAt", ""), reverse=True)
        return campanhas

    async def buscar_por_id(self, id: str) -> dict | None:
        r = get_redis()
        data = await r.hgetall(_key_campaign(id))
        if not data:
            return None
        return from_redis_hash(data)

    async def atualizar(self, id: str, dados: dict) -> dict | None:
        r = get_redis()
        existing = await r.hgetall(_key_campaign(id))
        if not existing:
            return None

        dados["updatedAt"] = datetime.now(timezone.utc).isoformat()
        await r.hset(_key_campaign(id), mapping=to_redis_hash(dados))
        return await self.buscar_por_id(id)

    async def remover(self, id: str) -> bool:
        r = get_redis()
        pipe = r.pipeline()
        pipe.delete(_key_campaign(id))
        pipe.srem(KEY_ALL_CAMPAIGNS, id)
        pipe.delete(_key_campaign_products(id))
        await pipe.execute()
        return True

    async def adicionar_produto(self, campaign_id: str, product_id: str) -> bool:
        r = get_redis()
        await r.sadd(_key_campaign_products(campaign_id), product_id)
        return True

    async def remover_produto(self, campaign_id: str, product_id: str) -> bool:
        r = get_redis()
        await r.srem(_key_campaign_products(campaign_id), product_id)
        return True

    async def listar_produtos(self, campaign_id: str) -> list[str]:
        r = get_redis()
        return list(await r.smembers(_key_campaign_products(campaign_id)))

    async def contar(self) -> int:
        r = get_redis()
        return await r.scard(KEY_ALL_CAMPAIGNS)


campaign_repository = CampaignRepository()
