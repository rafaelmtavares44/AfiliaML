# ============================================
# AfiliaML — Utilitário de Processamento em Chunks
# Processa listas em lotes para evitar sobrecarga
# ============================================

import asyncio
from typing import TypeVar, Callable, Awaitable

T = TypeVar("T")
R = TypeVar("R")


async def processar_em_chunks(
    items: list[T],
    chunk_size: int,
    fn: Callable[[T], Awaitable[R]],
) -> list[R]:
    """
    Processa uma lista em chunks paralelos.
    Equivalente ao processarEmChunks do TypeScript.
    """
    resultados: list[R] = []

    for i in range(0, len(items), chunk_size):
        chunk = items[i : i + chunk_size]
        tasks = [fn(item) for item in chunk]
        chunk_results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in chunk_results:
            if not isinstance(result, Exception):
                resultados.append(result)

    return resultados
