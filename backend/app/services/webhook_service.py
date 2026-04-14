# ============================================
# AfiliaML — Service de Webhooks
# ============================================

from app.repositories.webhook_repo import webhook_repository


class WebhookService:
    async def processar_mercadolivre(self, payload: dict) -> dict:
        log = await webhook_repository.registrar(
            provider="mercadolivre",
            payload=payload,
            status="recebido",
        )
        # TODO: Processar payload do ML
        return log


webhook_service = WebhookService()
