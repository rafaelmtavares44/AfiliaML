# ============================================
# AfiliaML — Router de Scraper
# ============================================

from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
from app.utils.api_response import resposta_sucesso, resposta_erro
from app.scraper.scheduler import run_all_scrapers_task

router = APIRouter(prefix="/api/scraper", tags=["Scraper"])


@router.post("/run")
async def run_scraper(background_tasks: BackgroundTasks):
    """Aciona a execução do scraper em segundo plano."""
    background_tasks.add_task(run_all_scrapers_task)
    return resposta_sucesso(None, "Scraper iniciado em segundo plano")


@router.get("/status")
async def get_status():
    """Retorna o status atual do scraper (mockado por enquanto)."""
    # Em uma implementação real, poderíamos consultar o estado do APScheduler
    return resposta_sucesso({"status": "idle", "last_run": None}, "Status do scraper")
