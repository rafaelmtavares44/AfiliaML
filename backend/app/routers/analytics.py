# ============================================
# AfiliaML — Router de Analytics
# ============================================

from fastapi import APIRouter
from app.services.analytics_service import analytics_service
from app.utils.api_response import resposta_sucesso

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/clicks/{product_id}")
async def clicks_por_produto(product_id: str):
    clicks = await analytics_service.clicks_por_produto(product_id)
    return resposta_sucesso(clicks, "Cliques do produto carregados")


@router.get("/summary")
async def resumo():
    resumo = await analytics_service.resumo_geral()
    return resposta_sucesso(resumo, "Resumo geral carregado")
