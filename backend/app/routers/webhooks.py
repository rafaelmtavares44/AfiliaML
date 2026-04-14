# ============================================
# AfiliaML — Router de Webhooks
# ============================================

from fastapi import APIRouter, Request
from app.services.webhook_service import webhook_service
from app.utils.api_response import resposta_sucesso

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])


@router.post("/mercadolivre")
async def ml_webhook(request: Request):
    """Recebe webhooks oficiais do Mercado Livre."""
    payload = await request.json()
    log = await webhook_service.processar_mercadolivre(payload)
    return resposta_sucesso({"webhookId": log["id"]}, "Webhook recebido")
