# ============================================
# AfiliaML — Service de Analytics
# ============================================

from app.repositories.click_event_repo import click_event_repository
from app.repositories.share_event_repo import share_event_repository


class AnalyticsService:
    async def clicks_por_produto(self, product_id: str) -> list[dict]:
        return await click_event_repository.analytics_por_produto(product_id)

    async def resumo_geral(self) -> dict:
        total_clicks = await click_event_repository.contar_total()
        total_shares = await share_event_repository.contar_total()

        return {
            "totalClicks": total_clicks,
            "totalShares": total_shares,
            "conversionRate": (
                round(total_clicks / total_shares, 4) if total_shares > 0 else 0
            ),
        }


analytics_service = AnalyticsService()
