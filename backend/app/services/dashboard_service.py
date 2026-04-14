# ============================================
# AfiliaML — Service de Dashboard
# ============================================

from app.repositories.product_repo import product_repository
from app.repositories.campaign_repo import campaign_repository
from app.repositories.click_event_repo import click_event_repository
from app.repositories.share_event_repo import share_event_repository
from app.repositories.affiliate_link_repo import affiliate_link_repository


class DashboardService:
    async def get_stats(self) -> dict:
        total_products = await product_repository.contar_ativos()
        featured_products = await product_repository.contar_destaque()
        total_campaigns = await campaign_repository.contar()
        total_links = await affiliate_link_repository.contar_total()
        total_clicks = await click_event_repository.contar_total()
        total_shares = await share_event_repository.contar_total()

        conversion_rate = (
            round(total_clicks / total_shares, 4) if total_shares > 0 else 0
        )

        return {
            "totalProducts": total_products,
            "featuredProducts": featured_products,
            "totalCampaigns": total_campaigns,
            "totalLinksGenerated": total_links,
            "totalClicks": total_clicks,
            "totalShares": total_shares,
            "conversionRate": conversion_rate,
        }


dashboard_service = DashboardService()
