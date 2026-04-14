# ============================================
# AfiliaML — Script de Reset Seguro
# Limpa caches mas preserva dados fundamentais
# ============================================

import asyncio
from app.utils.redis_client import get_redis, connect_redis, disconnect_redis

async def reset_safe():
    print("Iniciando reset seguro...")
    await connect_redis()
    r = get_redis()
    
    # Limpar caches de recomendação e grafo
    keys_to_del = [
        "graph:full",
        "graph:pagerank",
        "recommendations:daily",
        "recommendations:channel:whatsapp",
        "recommendations:channel:instagram",
        "recommendations:channel:facebook"
    ]
    
    for key in keys_to_del:
        await r.delete(key)
        print(f"Limpo: {key}")
    
    # Limpar logs de auditoria ML se necessário (opcional)
    # await r.delete("ml_predictions:all")
    
    print("Reset concluído.")
    await disconnect_redis()

if __name__ == "__main__":
    asyncio.run(reset_safe())
