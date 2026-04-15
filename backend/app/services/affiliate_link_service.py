# ============================================
# AfiliaML — Service de Links de Afiliado
# ============================================

import httpx
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
        Gera link de afiliado oficial via API do Mercado Livre (meli.la)
        com lógica de retry e fallback automático.
        """
        from app.services.ml_api_service import ml_api_service

        settings = get_settings()
        produto = await product_repository.buscar_por_id(product_id)
        if not produto:
            raise ValueError("Produto não encontrado")

        original_url = produto.get("originalUrl", "")
        slug = produto.get("slug") or "produto"
        item_id = ml_api_service.extrair_mlb_id(original_url)

        if not item_id:
            raise ValueError("MLB ID não encontrado na URL do produto")

        store_id = settings.MATT_TOOL
        
        # Tentar gerar link oficial via API (meli.la)
        # O ml_api_service.create_social_link já cuida do token e do retry se necessário
        short_link = await ml_api_service.create_social_link(item_id, store_id)

        if short_link:
            strategy = "api_oficial"
            generated_url = short_link
            status = "generated"
        else:
            # Fallback para link longo se a API falhar
            strategy = "fallback"
            generated_url = (
                f"https://www.mercadolivre.com.br/{slug}/p/{item_id}?"
                f"matt_tool={store_id}&"
                f"matt_source=afiliados&"
                f"matt_medium=social"
            )
            status = "fallback"

        # Logar no terminal para acompanhamento
        print(f"🚀 [AffiliateLink] Strat: {strategy} | Item: {item_id} | Link: {generated_url}")

        # Salvar no produto
        await product_repository.atualizar(
            product_id, {"affiliateUrl": generated_url}
        )

        # Registrar log técnico
        await affiliate_link_repository.registrar(
            product_id=product_id,
            original_url=original_url,
            generated_url=generated_url,
            strategy=strategy,
            status="generated" if strategy == "api_oficial" else "fallback",
        )

        return {
            "productId": product_id,
            "affiliateUrl": generated_url,
            "strategy": strategy,
            "status": "generated",
        }

    async def _obter_token(self) -> str | None:
        """Obtém access_token do Redis."""
        return await ml_api_service.get_access_token()

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
