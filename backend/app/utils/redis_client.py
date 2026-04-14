# ============================================
# AfiliaML — Cliente Redis (Async Singleton)
# Garante uma única instância de conexão com o Redis
# ============================================

import redis.asyncio as aioredis
from app.config import get_settings

_redis_client: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    """Retorna o cliente Redis singleton."""
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            retry_on_timeout=True,
        )
    return _redis_client


async def connect_redis() -> None:
    """Testa a conexão com o Redis."""
    r = get_redis()
    await r.ping()
    print("Conectado ao Redis")


async def disconnect_redis() -> None:
    """Fecha a conexão com o Redis."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
        print("Redis desconectado")
