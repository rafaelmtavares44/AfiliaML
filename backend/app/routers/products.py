# ============================================
# AfiliaML — Router de Produtos
# ============================================

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from app.services.product_service import product_service
from app.utils.api_response import resposta_sucesso, resposta_erro, resposta_paginada

router = APIRouter(prefix="/api/products", tags=["Produtos"])


@router.post("")
async def criar(body: dict):
    try:
        produto = await product_service.criar(body)
        return JSONResponse(
            content=resposta_sucesso(produto, "Produto criado com sucesso"),
            status_code=201,
        )
    except Exception as e:
        return JSONResponse(
            content=resposta_erro(str(e), 400), status_code=400
        )


@router.get("")
async def listar_todos():
    produtos = await product_service.listar_todos()
    return resposta_sucesso(produtos, "Produtos carregados com sucesso")


@router.get("/featured/list")
async def listar_destaque():
    produtos = await product_service.listar_destaque(4)
    return resposta_sucesso(produtos, "Produtos em destaque carregados")


@router.get("/catalog")
async def catalogo(
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=500),
    busca: str | None = None,
    categoria: str | None = None,
    loja: str | None = None,
    destaque: str | None = None,
    hasAffiliate: str | None = None,
):
    dest = True if destaque == "true" else (False if destaque == "false" else None)
    has_aff = True if hasAffiliate == "true" else (False if hasAffiliate == "false" else None)

    result = await product_service.catalogo({
        "pagina": pagina,
        "limite": limite,
        "busca": busca,
        "categoria": categoria,
        "loja": loja,
        "destaque": dest,
        "hasAffiliate": has_aff,
    })

    return resposta_paginada(
        result["produtos"],
        result["total"],
        pagina,
        limite,
        "Catálogo carregado com sucesso",
    )


@router.get("/{product_id}")
async def buscar_por_id(product_id: str):
    try:
        produto = await product_service.buscar_por_id(product_id)
        return resposta_sucesso(produto, "Produto encontrado")
    except ValueError:
        return JSONResponse(
            content=resposta_erro("Produto não encontrado", 404),
            status_code=404,
        )


@router.put("/{product_id}")
async def atualizar(product_id: str, body: dict):
    try:
        produto = await product_service.atualizar(product_id, body)
        return resposta_sucesso(produto, "Produto atualizado com sucesso")
    except ValueError:
        return JSONResponse(
            content=resposta_erro("Produto não encontrado", 404),
            status_code=404,
        )


@router.delete("/{product_id}")
async def remover(product_id: str):
    try:
        await product_service.remover(product_id)
        return resposta_sucesso(None, "Produto removido com sucesso")
    except ValueError:
        return JSONResponse(
            content=resposta_erro("Produto não encontrado", 404),
            status_code=404,
        )


@router.get("/{product_id}/price-history")
async def historico_precos(product_id: str, dias: int | None = None):
    try:
        resultado = await product_service.buscar_historico_precos(product_id, dias)
        return resposta_sucesso(resultado, "Histórico de preços carregado")
    except ValueError:
        return JSONResponse(
            content=resposta_erro("Produto não encontrado", 404),
            status_code=404,
        )


@router.post("/{product_id}/enrich")
async def enriquecer(product_id: str):
    try:
        resultado = await product_service.enriquecer(product_id)
        return resposta_sucesso(resultado, "Produto enriquecido com dados da API do ML")
    except ValueError as e:
        return JSONResponse(
            content=resposta_erro(str(e), 400), status_code=400
        )


@router.post("/{product_id}/affiliate")
async def gerar_link_afiliado(product_id: str):
    from app.services.affiliate_link_service import affiliate_link_service
    try:
        resultado = await affiliate_link_service.gerar_via_template(product_id)
        return resposta_sucesso(resultado, "Link de afiliado gerado com sucesso")
    except Exception as e:
        return JSONResponse(
            content=resposta_erro(str(e), 400), status_code=400
        )
