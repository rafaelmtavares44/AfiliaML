# ============================================
# AfiliaML — Models de Produto
# Schemas Pydantic para validação de dados
# ============================================

from pydantic import BaseModel, Field
from typing import Optional


class CriarProdutoInput(BaseModel):
    """Schema para criação de produto."""
    title: str = Field(..., min_length=3, max_length=300)
    originalUrl: str
    price: float = Field(..., ge=0)
    oldPrice: Optional[float] = None
    description: Optional[str] = None
    affiliateUrl: Optional[str] = None
    imageUrl: Optional[str] = None
    store: Optional[str] = "mercadolivre"
    category: Optional[str] = None
    featured: Optional[bool] = False


class AtualizarProdutoInput(BaseModel):
    """Schema para atualização parcial de produto."""
    title: Optional[str] = Field(None, min_length=3, max_length=300)
    originalUrl: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    oldPrice: Optional[float] = None
    description: Optional[str] = None
    affiliateUrl: Optional[str] = None
    imageUrl: Optional[str] = None
    store: Optional[str] = None
    category: Optional[str] = None
    featured: Optional[bool] = None
    active: Optional[bool] = None
    status: Optional[str] = None
    # Campos de enriquecimento ML API
    mlItemId: Optional[str] = None
    soldQuantity: Optional[int] = None
    ratingAverage: Optional[float] = None
    ratingCount: Optional[int] = None
    freeShipping: Optional[bool] = None
