# ============================================
# AfiliaML — Models de Compartilhamento
# ============================================

from pydantic import BaseModel
from typing import Optional


class CriarShareInput(BaseModel):
    """Schema para registrar compartilhamento."""
    productId: str
    channel: str
    campaignId: Optional[str] = None
    message: Optional[str] = None
