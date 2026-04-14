# ============================================
# AfiliaML — Script de Reprocessamento (API ML)
# Corrige preços e imagens usando a API Oficial
# ============================================

import asyncio
from app.services.product_service import product_service
from app.utils.redis_client import connect_redis, disconnect_redis

async def reprocessar_com_api(p):
    pid = p["id"]
    title = p.get("title", "")
    
    # Só faz sentido para produtos do Mercado Livre
    if p.get("store") != "mercadolivre" and "mercadolivre.com.br" not in p.get("originalUrl", ""):
        return False

    try:
        print(f"Reprocessando via API [{pid}]: {title[:30]}...")
        
        # O método enriquecer já busca na API e atualiza o repo
        await product_service.enriquecer(pid)
        return True
    except Exception as e:
        print(f"  Falha no enriquecimento via API: {e}")
        return False

async def main():
    await connect_redis()
    print("Iniciando reprocessamento via API Oficial do ML...")
    
    produtos_all = await product_service.listar_todos()
    
    # Filtrar produtos do ML
    produtos = [
        p for p in produtos_all 
        if p.get("store") == "mercadolivre" or "mercadolivre.com.br" in p.get("originalUrl", "")
    ]
    
    total = len(produtos)
    print(f"Total de produtos para processar: {total}")
    
    # Vamos processar todos, pois a API é rápida e segura
    corrigidos = 0
    for i, p in enumerate(produtos):
        if await reprocessar_com_api(p):
            corrigidos += 1
        
        # Rate limit preventivo (API ML permite muito mais, mas vamos ser educados)
        if (i + 1) % 10 == 0:
            print(f"Progresso: {i+1}/{total}...")
            await asyncio.sleep(0.5)

    print(f"Reprocessamento concluído! {corrigidos} produtos foram enriquecidos/corrigidos.")
    await disconnect_redis()

if __name__ == "__main__":
    asyncio.run(main())
