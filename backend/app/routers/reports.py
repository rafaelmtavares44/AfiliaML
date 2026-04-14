# ============================================
# AfiliaML — Router de Relatórios
# ============================================

from fastapi import APIRouter, Response
from app.services.report_service import report_service
from app.utils.api_response import resposta_sucesso

router = APIRouter(prefix="/api/reports", tags=["Relatórios"])


@router.get("/products/csv")
async def export_products():
    """Exporta relatório de produtos em CSV."""
    data = await report_service.gerar_relatorio_produtos()
    csv = report_service.exportar_csv(data)
    
    return Response(
        content=csv,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=relatorio_produtos.csv"}
    )


@router.get("/clicks/csv")
async def export_clicks(start: str | None = None, end: str | None = None):
    """Exporta relatório de cliques em CSV."""
    data = await report_service.gerar_relatorio_cliques(start, end)
    csv = report_service.exportar_csv(data)
    
    return Response(
        content=csv,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=relatorio_cliques.csv"}
    )


@router.get("/estimated-commission/csv")
async def export_commission():
    """Exporta relatório de comissão estimada em CSV."""
    data = await report_service.gerar_relatorio_comissao()
    csv = report_service.exportar_csv(data)
    
    return Response(
        content=csv,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=comissao_estimada.csv"}
    )
