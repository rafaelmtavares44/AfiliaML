# ============================================
# AfiliaML — Agendador de Tarefas
# Gerencia a execução periódica dos scrapers
# ============================================

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.config import get_settings
from app.scraper.mercadolivre import scraper_mercadolivre_ofertas
from app.scraper.vitrine import sincronizar_vitrine
from app.services.ml_scoring_service import ml_scoring_service
from app.services.recommendation_service import recommendation_service
import asyncio

scheduler = AsyncIOScheduler()

async def run_all_scrapers_task():
    """Tarefa principal: roda scrapers, treina ML e atualiza recomendações."""
    print("[Job] Iniciando ciclo completo de processamento...")
    settings = get_settings()
    
    # 1. Scrapers
    for url in settings.scraper_urls:
        await scraper_mercadolivre_ofertas(url)
    
    await sincronizar_vitrine()
    
    # 2. ML & Graph (só se tiver produtos suficientes)
    try:
        print("[Job] Treinando modelo ML...")
        await ml_scoring_service.train_model()
        
        print("[Job] Atualizando recomendações...")
        await recommendation_service.cache_recommendations()
    except Exception as e:
        print(f"[Job] Falha no pós-processamento: {e}")

    print("[Job] Ciclo concluído!")


def start_scheduler():
    """Inicia o agendador."""
    settings = get_settings()
    
    # Adicionar tarefa do scraper baseado no CRON do .env
    trigger = CronTrigger.from_crontab(settings.SCRAPER_CRON)
    scheduler.add_job(run_all_scrapers_task, trigger, id="scrapers_main")
    
    # Iniciar
    scheduler.start()
    print(f"Scheduler iniciado! CRON: {settings.SCRAPER_CRON}")


def shutdown_scheduler():
    """Finaliza o agendador."""
    if scheduler.running:
        scheduler.shutdown()
        print("⏰ Scheduler finalizado.")
