# ============================================
# AfiliaML — Script de Seed (Dados Iniciais)
# ============================================

import asyncio
from app.repositories.product_repo import product_repository
from app.repositories.campaign_repo import campaign_repository
from app.utils.redis_client import connect_redis, disconnect_redis

async def seed():
    print("Iniciando seed de dados...")
    await connect_redis()
    
    # Criar Campanha Global
    campanha = await campaign_repository.criar({
        "name": "Campanha Geral 2024",
        "description": "Campanha principal de lançamento",
        "channel": "multi"
    })
    print(f"Campanha criada: {campanha['id']}")
    
    # Criar alguns produtos de teste
    p1 = await product_repository.criar({
        "title": "Celular Smartphone Top de Linha",
        "originalUrl": "https://www.mercadolivre.com.br/produto-teste-1",
        "price": 2500.0,
        "oldPrice": 3000.0,
        "category": "Eletrônicos",
        "featured": True
    })
    
    p2 = await product_repository.criar({
        "title": "Fone de Ouvido Bluetooth Noise Cancelling",
        "originalUrl": "https://www.mercadolivre.com.br/produto-teste-2",
        "price": 450.0,
        "oldPrice": 599.0,
        "category": "Acessórios",
        "featured": True
    })
    
    print(f"{p1['id']} - {p1['title']}")
    print(f"{p2['id']} - {p2['title']}")
    
    # Adicionar produtos à campanha
    await campaign_repository.adicionar_produto(campanha["id"], p1["id"])
    await campaign_repository.adicionar_produto(campanha["id"], p2["id"])
    
    print("Seed finalizado com sucesso!")
    await disconnect_redis()

if __name__ == "__main__":
    asyncio.run(seed())
