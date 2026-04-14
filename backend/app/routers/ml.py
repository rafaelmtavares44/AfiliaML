# ============================================
# AfiliaML — Router de Machine Learning
# ============================================

from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
from app.services.ml_scoring_service import ml_scoring_service
from app.services.ml_audit_service import ml_audit_service
from app.utils.api_response import resposta_sucesso, resposta_erro

router = APIRouter(prefix="/api/ml", tags=["ML"])


@router.post("/train")
async def train_model():
    """Treina o modelo Naive Bayes com os dados atuais."""
    try:
        resultado = await ml_scoring_service.train_model()
        return resposta_sucesso(resultado, "Modelo treinado com sucesso!")
    except Exception as e:
        return JSONResponse(
            content=resposta_erro(str(e), 400),
            status_code=400
        )


@router.get("/status")
async def get_status():
    """Retorna o status e métricas do modelo atual."""
    status = await ml_scoring_service.get_model_status()
    return resposta_sucesso(status, "Status do modelo ML")


@router.get("/predict/{product_id}")
async def predict_product(product_id: str):
    """Gera predição de relevância para um produto específico."""
    try:
        resultado = await ml_scoring_service.predict(product_id)
        return resposta_sucesso(resultado, "Predição gerada com sucesso")
    except Exception as e:
        return JSONResponse(
            content=resposta_erro(str(e), 400),
            status_code=400
        )


@router.get("/audit/{product_id}")
async def audit_product(product_id: str):
    """Retorna o histórico de auditoria de predições do produto."""
    historico = await ml_audit_service.listar_predicoes(product_id)
    return resposta_sucesso(historico, "Auditoria ML carregada")
