# ============================================
# AfiliaML — Utilitário de Slugify
# Gera slugs únicos para produtos
# ============================================

import uuid
from slugify import slugify as _slugify


def gerar_slug(texto: str) -> str:
    """Gera um slug a partir de um texto."""
    return _slugify(texto, max_length=120)


def gerar_slug_unico(texto: str) -> str:
    """Gera um slug único adicionando sufixo UUID."""
    base = gerar_slug(texto)
    sufixo = uuid.uuid4().hex[:6]
    return f"{base}-{sufixo}"
