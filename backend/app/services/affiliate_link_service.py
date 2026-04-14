# ============================================
# AfiliaML — Service de Links de Afiliado
# ============================================

from app.repositories.product_repo import product_repository
from app.repositories.affiliate_link_repo import affiliate_link_repository
from app.config import get_settings


class AffiliateLinkService:
    async def definir_link(self, product_id: str, affiliate_url: str) -> dict:
        """Define manualmente o link de afiliado de um produto."""
        produto = await product_repository.buscar_por_id(product_id)
        if not produto:
            raise ValueError("Produto não encontrado")

        await product_repository.atualizar(
            product_id, {"affiliateUrl": affiliate_url}
        )

        # Registrar log
        await affiliate_link_repository.registrar(
            product_id=product_id,
            original_url=produto.get("originalUrl", ""),
            generated_url=affiliate_url,
            strategy="manual",
            status="manual",
        )

        return {
            "productId": product_id,
            "affiliateUrl": affiliate_url,
            "strategy": "manual",
            "status": "manual",
        }

    async def gerar_via_template(self, product_id: str) -> dict:
        """Gera link via template configurado."""
        settings = get_settings()
        produto = await product_repository.buscar_por_id(product_id)
        if not produto:
            raise ValueError("Produto não encontrado")

        original_url = produto.get("originalUrl", "")
        template = settings.AFFILIATE_LINK_TEMPLATE
        generated_url = template.replace("{url}", original_url)

        await product_repository.atualizar(
            product_id, {"affiliateUrl": generated_url}
        )

        await affiliate_link_repository.registrar(
            product_id=product_id,
            original_url=original_url,
            generated_url=generated_url,
            strategy="template",
            status="generated",
        )

        return {
            "productId": product_id,
            "affiliateUrl": generated_url,
            "strategy": "template",
            "status": "generated",
        }

    async def remover_link(self, product_id: str) -> dict:
        """Remove o link de afiliado de um produto."""
        produto = await product_repository.buscar_por_id(product_id)
        if not produto:
            raise ValueError("Produto não encontrado")

        await product_repository.atualizar(product_id, {"affiliateUrl": ""})

        return {
            "productId": product_id,
            "affiliateUrl": None,
            "status": "removed",
        }

    async def listar_logs(self, product_id: str) -> list[dict]:
        return await affiliate_link_repository.listar_por_produto(product_id)


affiliate_link_service = AffiliateLinkService()
