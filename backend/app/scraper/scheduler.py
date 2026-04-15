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

CATEGORY_URLS = {
    "ofertas": "https://www.mercadolivre.com.br/ofertas",
    "ofertas-relampago": "https://www.mercadolivre.com.br/ofertas?container_id=MLB779362-1",
    "precos-imbativeis": "https://www.mercadolivre.com.br/ofertas?container_id=MLB779363-1",
    "outlet": "https://www.mercadolivre.com.br/ofertas?container_id=MLB779365-1",
    "celulares": "https://www.mercadolivre.com.br/ofertas?category=MLB1051",
    "notebooks": "https://www.mercadolivre.com.br/ofertas?category=MLB1648",
    "menos-de-100": "https://www.mercadolivre.com.br/ofertas?price=*-100",
    "compra-internacional": "https://www.mercadolivre.com.br/ofertas?cbi=true",
    "calcados": "https://www.mercadolivre.com.br/ofertas?category=MLB1430",
    "audio": "https://www.mercadolivre.com.br/ofertas?category=MLB1000",
    "televisores": "https://www.mercadolivre.com.br/ofertas?category=MLB1000",
    "ferramentas": "https://www.mercadolivre.com.br/ofertas?category=MLB4314",
    "smartwatches": "https://www.mercadolivre.com.br/ofertas?category=MLB3937",
    "supermercado": "https://www.mercadolivre.com.br/ofertas?category=MLB1434",
    "caixas-de-som": "https://www.mercadolivre.com.br/ofertas?category=MLB1000",
    "perfumes": "https://www.mercadolivre.com.br/ofertas?category=MLB6284",
    "moda": "https://www.mercadolivre.com.br/ofertas?category=MLB1430",
    "esportes": "https://www.mercadolivre.com.br/ofertas?category=MLB1499",
}

async def run_all_scrapers_task(categoria: str = "ofertas"):
    """Tarefa principal: roda scrapers, treina ML e atualiza recomendações."""
    print(f"[Job] Iniciando ciclo completo de processamento para a categoria: {categoria}...")
    settings = get_settings()
    
    # 1. Scrapers
    target_url = CATEGORY_URLS.get(categoria, "https://www.mercadolivre.com.br/ofertas")
    
    await scraper_mercadolivre_ofertas(target_url, categoria)
    
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
