# ============================================
# AfiliaML — Router de Dashboard
# ============================================

from fastapi import APIRouter
from app.services.dashboard_service import dashboard_service
from app.utils.api_response import resposta_sucesso

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def stats():
    dados = await dashboard_service.get_stats()
    return resposta_sucesso(dados, "Estatísticas do dashboard")
