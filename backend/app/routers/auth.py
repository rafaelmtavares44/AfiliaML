# ============================================
# AfiliaML — Router de Auth (Mercado Livre OAuth)
# ============================================

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, RedirectResponse
from app.config import get_settings
from app.utils.redis_client import get_redis
from app.utils.api_response import resposta_sucesso, resposta_erro
import httpx

router = APIRouter(prefix="/api/auth", tags=["Autenticação"])


@router.get("/url")
async def get_auth_url():
    settings = get_settings()
    url = (
        f"https://auth.mercadolivre.com.br/authorization?"
        f"response_type=code&client_id={settings.ML_CLIENT_ID}"
        f"&redirect_uri={settings.ML_REDIRECT_URI}"
    )
    return resposta_sucesso({"url": url}, "URL de autenticação gerada")


@router.get("/authorize")
async def authorize():
    """Redireciona diretamente para o Mercado Livre."""
    settings = get_settings()
    url = (
        f"https://auth.mercadolivre.com.br/authorization?"
        f"response_type=code&client_id={settings.ML_CLIENT_ID}"
        f"&redirect_uri={settings.ML_REDIRECT_URI}"
    )
    return RedirectResponse(url=url)


@router.get("/callback")
async def callback(code: str = Query(...)):
    settings = get_settings()
    r = get_redis()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.mercadolibre.com/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": settings.ML_CLIENT_ID,
                    "client_secret": settings.ML_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": settings.ML_REDIRECT_URI,
                },
                headers={
                    "accept": "application/json",
                    "content-type": "application/x-www-form-urlencoded",
                },
            )
            response.raise_for_status()
            data = response.json()

        await r.set("ml:access_token", data["access_token"])
        if data.get("refresh_token"):
            await r.set("ml:refresh_token", data["refresh_token"])

        return resposta_sucesso(
            {"authenticated": True}, "Autenticação com Mercado Livre concluída!"
        )
    except Exception as e:
        return JSONResponse(
            content=resposta_erro(f"Erro na autenticação: {e}", 400),
            status_code=400,
        )
