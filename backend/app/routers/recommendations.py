# ============================================
# AfiliaML — Router de Recomendações
# ============================================

from fastapi import APIRouter
from app.services.recommendation_service import recommendation_service
from app.utils.api_response import resposta_sucesso, resposta_erro
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/recommendations", tags=["Recomendações"])


@router.get("/daily")
async def get_daily():
    """Top produtos do dia baseados em queda de preço e relevância."""
    try:
        recs = await recommendation_service.get_daily_top_products(10)
        return resposta_sucesso(recs, "Principais ofertas de hoje")
    except Exception as e:
        return JSONResponse(content=resposta_erro(str(e), 500), status_code=500)


@router.get("/similar/{product_id}")
async def get_similar(product_id: str, limit: int = 5):
    """Produtos similares baseados no grafo."""
    try:
        recs = await recommendation_service.get_similar_products(product_id, limit)
        return resposta_sucesso(recs, "Produtos similares encontrados")
    except Exception as e:
        return JSONResponse(content=resposta_erro(str(e), 404), status_code=404)


@router.get("/explain/{product_id}")
async def explain(product_id: str):
    """Explica 'por que' um produto foi recomendado."""
    try:
        explanation = await recommendation_service.explain_product(product_id)
        return resposta_sucesso(explanation, "Explicação de recomendação")
    except Exception as e:
        return JSONResponse(content=resposta_erro(str(e), 404), status_code=404)


@router.post("/rebuild-cache")
async def rebuild_cache():
    """Força rebuild do cache de recomendações."""
    summary = await recommendation_service.cache_recommendations()
    return resposta_sucesso(summary, "Cache de recomendações atualizado")
