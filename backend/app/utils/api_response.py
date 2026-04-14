# ============================================
# AfiliaML — Utilitário de Resposta Padronizada
# Todas as respostas da API seguem este formato
# ============================================

from typing import Any
import math


def resposta_sucesso(
    dados: Any = None,
    mensagem: str = "Operação realizada com sucesso",
    status_code: int = 200,
) -> dict:
    """Cria uma resposta de sucesso padronizada."""
    return {
        "success": True,
        "message": mensagem,
        "data": dados,
    }


def resposta_erro(
    mensagem: str = "Erro interno do servidor",
    status_code: int = 500,
    erros: Any = None,
) -> dict:
    """Cria uma resposta de erro padronizada."""
    return {
        "success": False,
        "message": mensagem,
        "errors": erros,
    }


def resposta_paginada(
    dados: list,
    total: int,
    pagina: int,
    limite: int,
    mensagem: str = "Dados carregados com sucesso",
) -> dict:
    """Cria uma resposta paginada padronizada."""
    total_paginas = math.ceil(total / limite) if limite > 0 else 0

    return {
        "success": True,
        "message": mensagem,
        "data": dados,
        "pagination": {
            "total": total,
            "pagina": pagina,
            "limite": limite,
            "totalPaginas": total_paginas,
            "temProxima": pagina < total_paginas,
            "temAnterior": pagina > 1,
        },
    }
