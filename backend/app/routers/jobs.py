# ============================================
# AfiliaML — Router de Fila de Jobs
# ============================================

from fastapi import APIRouter
from app.utils.api_response import resposta_sucesso

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.get("/status")
async def get_all_jobs():
    """Status das filas de processamento (APScheduler)."""
    # Em Python estamos usando APScheduler ao invés de BullMQ
    # Retornamos um mock para manter compatibilidade com o frontend
    return resposta_sucesso({
        "queues": [{
            "name": "default",
            "waiting": 0,
            "active": 0,
            "completed": 100,
            "failed": 0
        }],
        "scheduler": "running"
    }, "Status das filas")
