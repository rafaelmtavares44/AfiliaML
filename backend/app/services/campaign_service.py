# ============================================
# AfiliaML — Service de Campanhas
# ============================================

from app.repositories.campaign_repo import campaign_repository


class CampaignService:
    async def criar(self, dados: dict) -> dict:
        return await campaign_repository.criar(dados)

    async def listar_todas(self) -> list[dict]:
        return await campaign_repository.listar_todas()

    async def buscar_por_id(self, id: str) -> dict:
        campanha = await campaign_repository.buscar_por_id(id)
        if not campanha:
            raise ValueError("Campanha não encontrada")
        return campanha

    async def atualizar(self, id: str, dados: dict) -> dict:
        campanha = await campaign_repository.atualizar(id, dados)
        if not campanha:
            raise ValueError("Campanha não encontrada")
        return campanha

    async def remover(self, id: str) -> bool:
        campanha = await campaign_repository.buscar_por_id(id)
        if not campanha:
            raise ValueError("Campanha não encontrada")
        return await campaign_repository.remover(id)

    async def adicionar_produto(self, campaign_id: str, product_id: str) -> bool:
        return await campaign_repository.adicionar_produto(campaign_id, product_id)

    async def remover_produto(self, campaign_id: str, product_id: str) -> bool:
        return await campaign_repository.remover_produto(campaign_id, product_id)

    async def listar_produtos(self, campaign_id: str) -> list[str]:
        return await campaign_repository.listar_produtos(campaign_id)


campaign_service = CampaignService()
