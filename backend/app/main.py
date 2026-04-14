# ============================================
# AfiliaML Backend — Python (FastAPI)
# API de Inteligência e Automação p/ Afiliados
# ============================================

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time

from app.config import get_settings
from app.utils.redis_client import connect_redis, disconnect_redis
from app.scraper.scheduler import start_scheduler, shutdown_scheduler
from app.utils.api_response import resposta_sucesso

# Importar Routers
from app.routers import (
    products, campaigns, affiliate_links, shares,
    analytics, dashboard, auth, graph, ml,
    jobs, recommendations, reports, redirect,
    webhooks, scraper
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação (startup/shutdown)."""
    # Startup
    print("AfiliaML Backend iniciando...")
    await connect_redis()
    start_scheduler()
    yield
    # Shutdown
    print("AfiliaML Backend desligando...")
    shutdown_scheduler()
    await disconnect_redis()

app = FastAPI(
    title="AfiliaML API",
    description="Backend de automação de afiliados com ML e Grafos",
    version="1.0.0 (Python Port)",
    lifespan=lifespan
)

# Configurações
settings = get_settings()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de Logging de Tempo de Resposta
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Rota de Saúde
@app.get("/api/health", tags=["Geral"])
async def health():
    return resposta_sucesso({"status": "online", "env": settings.ENV})

# Registrar Routers
app.include_router(products.router)
app.include_router(campaigns.router)
app.include_router(affiliate_links.router)
app.include_router(shares.router)
app.include_router(analytics.router)
app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(graph.router)
app.include_router(ml.router)
app.include_router(jobs.router)
app.include_router(recommendations.router)
app.include_router(reports.router)
app.include_router(webhooks.router)
app.include_router(scraper.router)

# Rota de Redirecionamento Curto (fora do prefixo /api)
app.include_router(redirect.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
