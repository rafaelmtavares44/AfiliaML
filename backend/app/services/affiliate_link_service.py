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
        """
        Gera link via template oficial do Mercado Livre Afiliados.
        Materia: Empreendedorismo - Automação de monetização via afiliados.
        """
        from app.services.ml_api_service import ml_api_service
        
        settings = get_settings()
        produto = await product_repository.buscar_por_id(product_id)
        if not produto:
            raise ValueError("Produto não encontrado")

        original_url = produto.get("originalUrl", "")
        slug = produto.get("slug") or "produto"
        mlb_id = ml_api_service.extrair_mlb_id(original_url) or product_id

        # Padrao oficial: https://www.mercadolivre.com.br/{slug}/p/{MLB_ID}?matt_tool={tool}&matt_source={source}&matt_medium={medium}
        generated_url = (
            f"https://www.mercadolivre.com.br/{slug}/p/{mlb_id}?"
            f"matt_tool={settings.MATT_TOOL}&"
            f"matt_source={settings.MATT_SOURCE}&"
            f"matt_medium={settings.MATT_MEDIUM}"
        )

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
