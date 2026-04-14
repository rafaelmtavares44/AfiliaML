# ============================================
# AfiliaML — Router de Links de Afiliado
# ============================================

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.affiliate_link_service import affiliate_link_service
from app.utils.api_response import resposta_sucesso, resposta_erro

router = APIRouter(prefix="/api/affiliate-links", tags=["Links de Afiliado"])


@router.post("")
async def definir_link(body: dict):
    try:
        resultado = await affiliate_link_service.definir_link(
            body.get("productId", ""), body.get("affiliateUrl", "")
        )
        return JSONResponse(
            content=resposta_sucesso(resultado, "Link de afiliado definido"),
            status_code=201,
        )
    except ValueError as e:
        return JSONResponse(content=resposta_erro(str(e), 404), status_code=404)


@router.post("/generate/{product_id}")
async def gerar_template(product_id: str):
    try:
        resultado = await affiliate_link_service.gerar_via_template(product_id)
        return resposta_sucesso(resultado, "Link gerado via template")
    except ValueError as e:
        return JSONResponse(content=resposta_erro(str(e), 404), status_code=404)


@router.delete("/{product_id}")
async def remover_link(product_id: str):
    try:
        resultado = await affiliate_link_service.remover_link(product_id)
        return resposta_sucesso(resultado, "Link removido")
    except ValueError as e:
        return JSONResponse(content=resposta_erro(str(e), 404), status_code=404)


@router.get("/logs/{product_id}")
async def listar_logs(product_id: str):
    logs = await affiliate_link_service.listar_logs(product_id)
    return resposta_sucesso(logs, "Logs carregados")
