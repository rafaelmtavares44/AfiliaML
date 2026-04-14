# ============================================
# AfiliaML — Router de Fila de Jobs
# Materia: Computação Paralela - Gerenciamento de tarefas em background.
# ============================================

from fastapi import APIRouter
from app.utils.api_response import resposta_sucesso, resposta_erro
from app.scraper.scheduler import scheduler
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.get("/status")
async def get_all_jobs():
    """Status real do APScheduler."""
    jobs_list = []
    for job in scheduler.get_jobs():
        jobs_list.append({
            "id": job.id,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "name": job.name,
            "trigger": str(job.trigger),
            "pending": job.next_run_time is not None
        })
    
    return resposta_sucesso({
        "jobs": jobs_list,
        "scheduler_running": scheduler.running,
        # Mantendo estrutura para compatibilidade de UI se necessário
        "queues": [{
            "name": "APScheduler",
            "active": len(jobs_list),
            "scheduler": "running" if scheduler.running else "stopped"
        }]
    }, "Status das tarefas agendadas")


@router.post("/toggle/{job_id}")
async def toggle_job(job_id: str):
    """Ativa ou desativa um job específico."""
    job = scheduler.get_job(job_id)
    if not job:
        return JSONResponse(content=resposta_erro("Job não encontrado", 404), status_code=404)
    
    if job.next_run_time:
        job.pause()
        status = "pausado"
    else:
        job.resume()
        status = "retomado"
        
    return resposta_sucesso({"id": job_id, "status": status}, f"Job {status} com sucesso")
