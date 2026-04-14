# ============================================
# AfiliaML — Router de Compartilhamento
# ============================================

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.share_service import share_service
from app.utils.api_response import resposta_sucesso, resposta_erro

router = APIRouter(prefix="/api/share", tags=["Compartilhamento"])


@router.post("")
async def compartilhar(body: dict):
    try:
        resultado = await share_service.compartilhar(
            product_id=body.get("productId", ""),
            channel=body.get("channel", "whatsapp"),
            campaign_id=body.get("campaignId"),
            message=body.get("message"),
        )
        return JSONResponse(
            content=resposta_sucesso(resultado, "Compartilhamento registrado"),
            status_code=201,
        )
    except ValueError as e:
        return JSONResponse(content=resposta_erro(str(e), 404), status_code=404)
