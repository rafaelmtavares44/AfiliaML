# ============================================
# AfiliaML — Models de Campanha
# ============================================

from pydantic import BaseModel, Field
from typing import Optional


class CriarCampanhaInput(BaseModel):
    """Schema para criação de campanha."""
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    channel: str = Field(..., min_length=2)
    status: Optional[str] = "ativa"


class AtualizarCampanhaInput(BaseModel):
    """Schema para atualização de campanha."""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    channel: Optional[str] = None
    status: Optional[str] = None


class AdicionarProdutoCampanhaInput(BaseModel):
    """Schema para adicionar produto a campanha."""
    productId: str
