# ============================================
# AfiliaML — Service da API do Mercado Livre
# Enriquece dados de produtos via API REST do ML
# ============================================

import re
import time
import httpx
from app.utils.redis_client import get_redis
from app.config import get_settings

# Rate limiting interno
_last_request_time = 0
_MIN_INTERVAL = 0.3  # 300ms


async def _rate_limited_get(url: str, headers: dict) -> httpx.Response | None:
    """Faz GET com rate limiting."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < _MIN_INTERVAL:
        import asyncio
        await asyncio.sleep(_MIN_INTERVAL - elapsed)
    _last_request_time = time.time()

    async with httpx.AsyncClient(timeout=10.0) as client:
        return await client.get(url, headers=headers)


class MLApiService:
    """Serviço de integração com a API do Mercado Livre."""

    async def get_access_token(self) -> str | None:
        r = get_redis()
        return await r.get("ml:access_token")

    async def refresh_access_token(self) -> str | None:
        r = get_redis()
        settings = get_settings()

        refresh_token = await r.get("ml:refresh_token")
        if not refresh_token:
            print("❌ mlApi: Nenhum refresh_token encontrado no Redis")
            return None

        if not settings.ML_CLIENT_ID or not settings.ML_CLIENT_SECRET:
            print("❌ mlApi: ML_CLIENT_ID ou ML_CLIENT_SECRET não configurados")
            return None

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://api.mercadolibre.com/oauth/token",
                    data={
                        "grant_type": "refresh_token",
                        "client_id": settings.ML_CLIENT_ID,
                        "client_secret": settings.ML_CLIENT_SECRET,
                        "refresh_token": refresh_token,
                    },
                    headers={
                        "accept": "application/json",
                        "content-type": "application/x-www-form-urlencoded",
                    },
                )
                response.raise_for_status()
                data = response.json()

            access_token = data.get("access_token")
            new_refresh = data.get("refresh_token")

            await r.set("ml:access_token", access_token)
            if new_refresh:
                await r.set("ml:refresh_token", new_refresh)

            print("🔄 mlApi: Access token renovado com sucesso")
            return access_token
        except Exception as e:
            print(f"❌ mlApi: Erro ao renovar token: {e}")
            return None

    async def authenticated_get(self, url: str) -> dict | None:
        """GET autenticado com retry se token expirou."""
        token = await self.get_access_token()
        if not token:
            token = await self.refresh_access_token()
            if not token:
                return None

        try:
            resp = await _rate_limited_get(
                url, {"Authorization": f"Bearer {token}"}
            )
            if resp and resp.status_code == 200:
                return resp.json()
            elif resp and resp.status_code == 401:
                # Token expirado
                print("🔄 mlApi: Token expirado, renovando...")
                token = await self.refresh_access_token()
                if not token:
                    return None
                resp = await _rate_limited_get(
                    url, {"Authorization": f"Bearer {token}"}
                )
                if resp and resp.status_code == 200:
                    return resp.json()
            return None
        except Exception as e:
            print(f"❌ mlApi: Erro na requisição: {e}")
            return None

    def extrair_mlb_id(self, url: str) -> str | None:
        """Extrair MLB ID de uma URL do Mercado Livre."""
        if not url:
            return None

        patterns = [
            r"MLB[_\-]?(\d+)",
            r"/p/(MLB\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                raw = match.group(0).upper().replace("-", "").replace("_", "")
                mlb_match = re.search(r"MLB(\d+)", raw)
                if mlb_match:
                    return f"MLB{mlb_match.group(1)}"
        return None

    async def get_item_details(self, item_id: str) -> dict | None:
        data = await self.authenticated_get(
            f"https://api.mercadolibre.com/items/{item_id}"
        )
        if not data:
            return None

        # Pegar a melhor imagem disponível
        pictures = data.get("pictures", [])
        image_url = pictures[0].get("url") if pictures else data.get("thumbnail")

        return {
            "price": data.get("price", 0.0),
            "oldPrice": data.get("original_price"),
            "imageUrl": image_url,
            "soldQuantity": data.get("sold_quantity", 0),
            "availableQuantity": data.get("available_quantity", 0),
            "condition": data.get("condition", "unknown"),
            "freeShipping": data.get("shipping", {}).get("free_shipping", False),
            "installmentsCount": (data.get("installments") or {}).get("quantity"),
            "sellerId": data.get("seller_id", 0),
            "categoryId": data.get("category_id", ""),
        }

    async def authenticated_post(self, url: str, data: dict) -> dict | None:
        """POST autenticado com retry se token expirou."""
        token = await self.get_access_token()
        if not token:
            token = await self.refresh_access_token()
            if not token:
                return None

        async def _make_post(t):
            async with httpx.AsyncClient(timeout=10.0) as client:
                return await client.post(
                    url, 
                    json=data, 
                    headers={
                        "Authorization": f"Bearer {t}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    }
                )

        try:
            resp = await _make_post(token)
            if resp.status_code in [200, 201]:
                return resp.json()
            elif resp.status_code == 401:
                print("🔄 mlApi: Token expirado em POST, renovando...")
                token = await self.refresh_access_token()
                if not token:
                    return None
                resp = await _make_post(token)
                if resp.status_code in [200, 201]:
                    return resp.json()
            
            print(f"❌ mlApi POST Error: {resp.status_code} - {resp.text}")
            return None
        except Exception as e:
            print(f"❌ mlApi: Erro na requisição POST: {e}")
            return None

    async def create_social_link(self, item_id: str, store_id: str) -> str | None:
        """
        Gera link curto meli.la via API oficial /social/links.
        """
        payload = {
            "item_id": item_id,
            "store_id": str(store_id),
            "channel": "whatsapp"
        }
        
        result = await self.authenticated_post(
            "https://api.mercadolibre.com/social/links",
            payload
        )
        
        if not result:
            return None
            
        # Tentar campos possíveis na resposta do ML
        # Doc indica short_link ou url ou permalink
        return (
            result.get("short_link") or 
            result.get("link") or 
            result.get("url") or 
            result.get("permalink")
        )


ml_api_service = MLApiService()
