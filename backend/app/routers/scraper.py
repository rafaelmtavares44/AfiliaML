# ============================================
# AfiliaML — Router de Scraper
# ============================================

from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
from app.utils.api_response import resposta_sucesso, resposta_erro
from app.scraper.scheduler import run_all_scrapers_task
from app.scraper.vitrine import sincronizar_vitrine

router = APIRouter(prefix="/api/scraper", tags=["Scraper"])


@router.get("/categorias")
async def get_categorias():
    """Retorna a lista de categorias do Mercado Livre para raspagem."""
    categorias = [
        {"id": "ofertas", "nome": "🔥 Todas as Ofertas"},
        {"id": "ofertas-relampago", "nome": "⚡ Ofertas Relâmpago"},
        {"id": "precos-imbativeis", "nome": "💰 Preços Imbatíveis"},
        {"id": "outlet", "nome": "🛒 Outlet"},
        {"id": "celulares", "nome": "📱 Celulares"},
        {"id": "notebooks", "nome": "💻 Notebooks"},
        {"id": "menos-de-100", "nome": "💸 Menos de R$100"},
        {"id": "compra-internacional", "nome": "✈️ Internacional"},
        {"id": "calcados", "nome": "👟 Tênis"},
        {"id": "audio", "nome": "🎧 Fones"},
        {"id": "televisores", "nome": "📺 TVs"},
        {"id": "ferramentas", "nome": "🛠️ Ferramentas"},
        {"id": "smartwatches", "nome": "⌚ Smartwatches"},
        {"id": "supermercado", "nome": "🛒 Supermercado"},
        {"id": "caixas-de-som", "nome": "🔊 Caixas de som"},
        {"id": "perfumes", "nome": "🧴 Perfumes"},
        {"id": "moda", "nome": "👕 Moda"},
        {"id": "esportes", "nome": "🏋️ Esportes e Fitness"},
    ]
    return resposta_sucesso(categorias)


@router.post("/run")
async def run_scraper(body: dict, background_tasks: BackgroundTasks):
    """Aciona a execução do scraper para uma categoria específica."""
    categoria = body.get("categoria", "ofertas")
    background_tasks.add_task(run_all_scrapers_task, categoria)
    return resposta_sucesso({"categoria": categoria}, "Scraper iniciado em segundo plano")


@router.get("/status")
async def get_status():
    """Retorna o status atual do scraper."""
    return resposta_sucesso({"status": "idle", "last_run": None}, "Status do scraper")


@router.post("/sync-vitrine")
async def sync_vitrine():
    """Aciona a sincronização da vitrine social no Mercado Livre."""
    try:
        total = await sincronizar_vitrine()
        return resposta_sucesso({"total": total}, "Vitrine sincronizada com sucesso!")
    except Exception as e:
        return JSONResponse(content=resposta_erro(str(e), 400), status_code=400)
