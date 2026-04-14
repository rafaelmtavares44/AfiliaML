# ============================================
# AfiliaML — Service de Compartilhamento
# ============================================

from app.repositories.product_repo import product_repository
from app.repositories.share_event_repo import share_event_repository
from app.config import get_settings


class ShareService:
    async def compartilhar(
        self,
        product_id: str,
        channel: str,
        campaign_id: str | None = None,
        message: str | None = None,
    ) -> dict:
        settings = get_settings()
        produto = await product_repository.buscar_por_id(product_id)
        if not produto:
            raise ValueError("Produto não encontrado")

        title = produto.get("title", "")
        price = produto.get("price", 0)
        affiliate_url = produto.get("affiliateUrl", "")
        base_url = settings.BASE_URL

        # Gerar link de redirecionamento
        slug = produto.get("slug", "")
        redirect_url = f"{base_url}/r/{slug}"

        # Montar mensagem
        if not message:
            message = (
                f"🔥 {title}\n"
                f"💰 R$ {price}\n"
                f"🔗 {redirect_url if slug else affiliate_url}"
                f"{settings.AFFILIATE_DISCLAIMER}"
            )

        # Registrar evento
        evento = await share_event_repository.registrar(
            product_id=product_id,
            channel=channel,
            message=message,
            campaign_id=campaign_id,
        )

        return {
            **evento,
            "redirectUrl": redirect_url,
            "affiliateUrl": affiliate_url,
        }


share_service = ShareService()
