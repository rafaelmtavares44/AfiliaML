# ============================================
# AfiliaML — Models de Link de Afiliado
# ============================================

from pydantic import BaseModel
from typing import Optional


class CriarAffiliateLinkInput(BaseModel):
    """Schema para criação/atualização de link de afiliado."""
    productId: str
    affiliateUrl: str


class AtualizarAffiliateLinkInput(BaseModel):
    """Schema para atualização de link de afiliado."""
    affiliateUrl: Optional[str] = None
