# ============================================
# AfiliaML — Router de Campanhas
# ============================================

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.campaign_service import campaign_service
from app.utils.api_response import resposta_sucesso, resposta_erro

router = APIRouter(prefix="/api/campaigns", tags=["Campanhas"])


@router.post("")
async def criar(body: dict):
    try:
        campanha = await campaign_service.criar(body)
        return JSONResponse(
            content=resposta_sucesso(campanha, "Campanha criada"), status_code=201
        )
    except Exception as e:
        return JSONResponse(content=resposta_erro(str(e), 400), status_code=400)


@router.get("")
async def listar():
    campanhas = await campaign_service.listar_todas()
    return resposta_sucesso(campanhas, "Campanhas carregadas")


@router.get("/{campaign_id}")
async def buscar(campaign_id: str):
    try:
        campanha = await campaign_service.buscar_por_id(campaign_id)
        return resposta_sucesso(companha, "Campanha encontrada")
    except ValueError:
        return JSONResponse(content=resposta_erro("Campanha não encontrada", 404), status_code=404)


@router.put("/{campaign_id}")
async def atualizar(campaign_id: str, body: dict):
    try:
        campanha = await campaign_service.atualizar(campaign_id, body)
        return resposta_sucesso(campanha, "Campanha atualizada")
    except ValueError:
        return JSONResponse(content=resposta_erro("Campanha não encontrada", 404), status_code=404)


@router.delete("/{campaign_id}")
async def remover(campaign_id: str):
    try:
        await campaign_service.remover(campaign_id)
        return resposta_sucesso(None, "Campanha removida")
    except ValueError:
        return JSONResponse(content=resposta_erro("Campanha não encontrada", 404), status_code=404)


@router.post("/{campaign_id}/products")
async def adicionar_produto(campaign_id: str, body: dict):
    product_id = body.get("productId", "")
    await campaign_service.adicionar_produto(campaign_id, product_id)
    return resposta_sucesso(None, "Produto adicionado à campanha")


@router.delete("/{campaign_id}/products/{product_id}")
async def remover_produto(campaign_id: str, product_id: str):
    await campaign_service.remover_produto(campaign_id, product_id)
    return resposta_sucesso(None, "Produto removido da campanha")


@router.get("/{campaign_id}/products")
async def listar_produtos(campaign_id: str):
    produtos = await campaign_service.listar_produtos(campaign_id)
    return resposta_sucesso(produtos, "Produtos da campanha")
