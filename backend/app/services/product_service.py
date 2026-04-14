# ============================================
# AfiliaML — Service de Produtos
# Lógica de negócio para operações com produtos
# ============================================

from app.repositories.product_repo import product_repository
from app.repositories.price_history_repo import price_history_repository
from app.services.ml_api_service import ml_api_service


class ProductService:
    """Serviço de produtos."""

    async def criar(self, dados: dict) -> dict:
        return await product_repository.criar(dados)

    async def listar_todos(self) -> list[dict]:
        return await product_repository.listar_todos()

    async def listar_destaque(self, limite: int = 4) -> list[dict]:
        return await product_repository.listar_destaque(limite)

    async def buscar_por_id(self, id: str) -> dict:
        produto = await product_repository.buscar_por_id(id)
        if not produto:
            raise ValueError("Produto não encontrado")
        return produto

    async def catalogo(self, params: dict) -> dict:
        return await product_repository.catalogo(params)

    async def atualizar(self, id: str, dados: dict) -> dict:
        produto = await product_repository.atualizar(id, dados)
        if not produto:
            raise ValueError("Produto não encontrado")
        return produto

    async def remover(self, id: str) -> dict:
        produto = await product_repository.buscar_por_id(id)
        if not produto:
            raise ValueError("Produto não encontrado")
        return await product_repository.remover(id)

    async def buscar_historico_precos(
        self, product_id: str, dias: int | None = None
    ) -> dict:
        produto = await product_repository.buscar_por_id(product_id)
        if not produto:
            raise ValueError("Produto não encontrado")

        historico = await price_history_repository.buscar_por_produto(
            product_id, dias or 30
        )
        tendencia = await price_history_repository.calcular_tendencia(product_id)

        return {
            "productId": product_id,
            "historico": historico,
            "tendencia": tendencia,
            "totalRegistros": len(historico),
        }

    async def enriquecer(self, product_id: str) -> dict:
        produto = await product_repository.buscar_por_id(product_id)
        if not produto:
            raise ValueError("Produto não encontrado")

        original_url = produto.get("originalUrl", "")
        ml_item_id = ml_api_service.extrair_mlb_id(original_url)

        if not ml_item_id:
            raise ValueError(
                "Não foi possível extrair o MLB ID da URL do produto"
            )

        details = await ml_api_service.get_item_details(ml_item_id)
        rating = await ml_api_service.get_item_rating(ml_item_id)

        dados_atualizacao = {"mlItemId": ml_item_id}
        if details:
            dados_atualizacao["soldQuantity"] = details["soldQuantity"]
            dados_atualizacao["freeShipping"] = details["freeShipping"]
            
            # Corrigir dados críticos se o API retornou novos valores
            if details.get("price"):
                dados_atualizacao["price"] = details["price"]
            if details.get("oldPrice"):
                dados_atualizacao["oldPrice"] = details["oldPrice"]
            if details.get("imageUrl"):
                dados_atualizacao["imageUrl"] = details["imageUrl"]
                
        if rating:
            dados_atualizacao["ratingAverage"] = rating["ratingAverage"]
            dados_atualizacao["ratingCount"] = rating["ratingCount"]

        await product_repository.atualizar(product_id, dados_atualizacao)
        return {
            "productId": product_id,
            "mlItemId": ml_item_id,
            "enrichedFields": list(dados_atualizacao.keys()),
        }


product_service = ProductService()
