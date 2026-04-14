# ============================================
# AfiliaML — Router de Redirecionamento Curto
# ============================================

from fastapi import APIRouter, Request, Header
from fastapi.responses import RedirectResponse
from app.repositories.product_repo import product_repository
from app.repositories.click_event_repo import click_event_repository

router = APIRouter(tags=["Redirecionamento"])


@router.get("/r/{slug}")
async def redirect_slug(
    slug: str, 
    request: Request,
    user_agent: str | None = Header(None)
):
    """Redireciona links curtos p/ link de afiliado e registra clique."""
    produto = await product_repository.buscar_por_slug(slug)
    
    if not produto:
        # Se não achar o produto, redireciona p/ o site principal (Front)
        return RedirectResponse(url="https://afiliaml.com", status_code=302)
    
    # Registrar Clique
    try:
        await click_event_repository.registrar(
            product_id=produto["id"],
            ip=request.client.host if request.client else "unknown",
            user_agent=user_agent
        )
    except Exception as e:
        print(f"Erro ao registrar clique: {e}")

    # Redirecionar para o link de afiliado
    target_url = produto.get("affiliateUrl") or produto.get("originalUrl")
    return RedirectResponse(url=target_url, status_code=302)
