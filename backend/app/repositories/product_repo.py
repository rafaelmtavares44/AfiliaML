# ============================================
# AfiliaML — Repositório de Produtos (Redis)
# Camada de acesso aos dados de produtos via Redis
# ============================================

import uuid
from datetime import datetime, timezone
from app.utils.redis_client import get_redis
from app.utils.slugify import gerar_slug, gerar_slug_unico


# Prefixos de chaves Redis
def _key_product(id: str) -> str:
    return f"product:{id}"


KEY_ALL_PRODUCTS = "products:all"
KEY_ACTIVE_PRODUCTS = "products:active"
KEY_FEATURED_PRODUCTS = "products:featured"
KEY_SLUG_INDEX = "products:by-slug"


def _key_category(cat: str) -> str:
    return f"products:category:{cat}"


# Serializar dados para Hash Redis
def to_redis_hash(dados: dict) -> dict[str, str]:
    result = {}
    for key, value in dados.items():
        if value is None:
            result[key] = ""
        elif isinstance(value, bool):
            result[key] = "1" if value else "0"
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        else:
            result[key] = str(value)
    return result


# Desserializar Hash Redis para dict tipado
def from_redis_hash(hash_data: dict[str, str]) -> dict:
    boolean_fields = {"featured", "active", "freeShipping"}
    number_fields = {"price", "oldPrice", "ratingAverage"}
    integer_fields = {"soldQuantity", "ratingCount"}

    result = {}
    for key, value in hash_data.items():
        if key in boolean_fields:
            result[key] = value == "1"
        elif key in integer_fields:
            result[key] = int(value) if value else None
        elif key in number_fields:
            result[key] = float(value) if value else None
        elif value == "":
            result[key] = None
        else:
            result[key] = value
    return result


class ProductRepository:
    """Repositório de produtos usando Redis."""

    async def criar(self, dados: dict) -> dict:
        """Criar novo produto."""
        r = get_redis()
        id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        # Gerar slug
        slug = gerar_slug(dados.get("title", ""))
        existente = await r.hget(KEY_SLUG_INDEX, slug)
        if existente:
            slug = gerar_slug_unico(dados.get("title", ""))

        produto = {
            "id": id,
            **dados,
            "slug": slug,
            "description": dados.get("description", ""),
            "affiliateUrl": dados.get("affiliateUrl", ""),
            "imageUrl": dados.get("imageUrl", ""),
            "oldPrice": dados.get("oldPrice", ""),
            "store": dados.get("store", "mercadolivre"),
            "category": dados.get("category", ""),
            "featured": dados.get("featured", False),
            "active": True,
            "status": "ativo",
            "createdAt": now,
            "updatedAt": now,
        }

        pipe = r.pipeline()
        pipe.hset(_key_product(id), mapping=to_redis_hash(produto))
        pipe.sadd(KEY_ALL_PRODUCTS, id)
        pipe.sadd(KEY_ACTIVE_PRODUCTS, id)
        pipe.hset(KEY_SLUG_INDEX, slug, id)

        if produto.get("featured"):
            pipe.sadd(KEY_FEATURED_PRODUCTS, id)
        if produto.get("category"):
            pipe.sadd(_key_category(produto["category"]), id)

        await pipe.execute()
        return from_redis_hash(to_redis_hash(produto))

    async def listar_todos(self) -> list[dict]:
        """Buscar todos os produtos ativos."""
        r = get_redis()
        ids = await r.smembers(KEY_ACTIVE_PRODUCTS)
        if not ids:
            return []

        pipe = r.pipeline()
        for id in ids:
            pipe.hgetall(_key_product(id))
        results = await pipe.execute()

        produtos = []
        for data in results:
            if data and len(data) > 0:
                produtos.append(from_redis_hash(data))

        # Ordenar por createdAt desc
        produtos.sort(
            key=lambda p: p.get("createdAt", ""),
            reverse=True,
        )
        return produtos

    async def buscar_por_id(self, id: str) -> dict | None:
        """Buscar produto por ID."""
        r = get_redis()
        data = await r.hgetall(_key_product(id))
        if not data:
            return None
        return from_redis_hash(data)

    async def buscar_por_slug(self, slug: str) -> dict | None:
        """Buscar produto por slug."""
        r = get_redis()
        id = await r.hget(KEY_SLUG_INDEX, slug)
        if not id:
            return None
        return await self.buscar_por_id(id)

    async def atualizar(self, id: str, dados: dict) -> dict | None:
        """Atualizar produto."""
        r = get_redis()
        existing = await r.hgetall(_key_product(id))
        if not existing:
            return None

        dados_atualizados = {**dados}
        dados_atualizados["updatedAt"] = datetime.now(timezone.utc).isoformat()

        # Se o título mudou, regenera o slug
        if "title" in dados and dados["title"]:
            slug = gerar_slug(dados["title"])
            existente_id = await r.hget(KEY_SLUG_INDEX, slug)
            if existente_id and existente_id != id:
                slug = gerar_slug_unico(dados["title"])
            # Remove slug antigo
            if existing.get("slug"):
                await r.hdel(KEY_SLUG_INDEX, existing["slug"])
            dados_atualizados["slug"] = slug
            await r.hset(KEY_SLUG_INDEX, slug, id)

        # Atualizar hash
        await r.hset(
            _key_product(id), mapping=to_redis_hash(dados_atualizados)
        )

        # Atualizar índice de featured
        if "featured" in dados:
            if dados["featured"]:
                await r.sadd(KEY_FEATURED_PRODUCTS, id)
            else:
                await r.srem(KEY_FEATURED_PRODUCTS, id)

        # Atualizar índice de categoria
        if "category" in dados and dados["category"]:
            if existing.get("category"):
                await r.srem(_key_category(existing["category"]), id)
            await r.sadd(_key_category(dados["category"]), id)

        return await self.buscar_por_id(id)

    async def remover(self, id: str) -> dict | None:
        """Remover produto (soft delete)."""
        r = get_redis()
        await r.hset(
            _key_product(id),
            mapping=to_redis_hash(
                {
                    "active": False,
                    "status": "inativo",
                    "updatedAt": datetime.now(timezone.utc).isoformat(),
                }
            ),
        )
        await r.srem(KEY_ACTIVE_PRODUCTS, id)
        await r.srem(KEY_FEATURED_PRODUCTS, id)
        return await self.buscar_por_id(id)

    async def listar_destaque(self, limite: int = 8) -> list[dict]:
        """Buscar produtos em destaque."""
        r = get_redis()
        ids = await r.smembers(KEY_FEATURED_PRODUCTS)
        if not ids:
            return []

        pipe = r.pipeline()
        for id in ids:
            pipe.hgetall(_key_product(id))
        results = await pipe.execute()

        produtos = []
        for data in results:
            if data and len(data) > 0:
                produtos.append(from_redis_hash(data))

        produtos.sort(key=lambda p: p.get("createdAt", ""), reverse=True)
        return produtos[:limite]

    async def catalogo(self, params: dict) -> dict:
        """Catálogo com paginação e filtros."""
        r = get_redis()
        pagina = params.get("pagina", 1)
        limite = params.get("limite", 20)
        busca = params.get("busca")
        categoria = params.get("categoria")
        loja = params.get("loja")
        destaque = params.get("destaque")
        has_affiliate = params.get("hasAffiliate")

        if destaque:
            ids = await r.smembers(KEY_FEATURED_PRODUCTS)
        elif categoria:
            ids = await r.smembers(_key_category(categoria))
            active_ids = await r.smembers(KEY_ACTIVE_PRODUCTS)
            ids = ids & active_ids  # Interseção
        else:
            ids = await r.smembers(KEY_ACTIVE_PRODUCTS)

        if not ids:
            return {"produtos": [], "total": 0}

        pipe = r.pipeline()
        for id in ids:
            pipe.hgetall(_key_product(id))
        results = await pipe.execute()

        produtos = []
        for data in results:
            if data and len(data) > 0:
                produtos.append(from_redis_hash(data))

        # Filtros
        if busca:
            busca_lower = busca.lower()
            produtos = [
                p
                for p in produtos
                if busca_lower in str(p.get("title", "")).lower()
                or busca_lower in str(p.get("description", "")).lower()
            ]
        if loja:
            produtos = [p for p in produtos if p.get("store") == loja]
        if has_affiliate is not None:
            produtos = [
                p
                for p in produtos
                if (bool(p.get("affiliateUrl")) == has_affiliate)
            ]

        # Ordenar por data de criação
        produtos.sort(key=lambda p: p.get("createdAt", ""), reverse=True)

        total = len(produtos)
        skip = (pagina - 1) * limite
        produtos_paginados = produtos[skip : skip + limite]

        return {"produtos": produtos_paginados, "total": total}

    async def contar_ativos(self) -> int:
        """Contar produtos ativos."""
        r = get_redis()
        return await r.scard(KEY_ACTIVE_PRODUCTS)

    async def contar_destaque(self) -> int:
        """Contar produtos em destaque."""
        r = get_redis()
        return await r.scard(KEY_FEATURED_PRODUCTS)


# Singleton
product_repository = ProductRepository()
