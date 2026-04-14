# ============================================
# AfiliaML — Tipos e Enums Comuns
# Definições compartilhadas em todo o projeto
# ============================================

from enum import Enum


class CanalCompartilhamento(str, Enum):
    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TELEGRAM = "telegram"
    CUSTOM = "custom"
    OTHERS = "others"


class StatusProduto(str, Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    PENDENTE = "pendente"


class StatusCampanha(str, Enum):
    ATIVA = "ativa"
    PAUSADA = "pausada"
    ENCERRADA = "encerrada"


class StatusLinkAfiliado(str, Enum):
    GENERATED = "generated"
    MANUAL = "manual"
    PENDING = "pending_manual_generation"
    FAILED = "failed"


class EstrategiaLink(str, Enum):
    MANUAL = "manual"
    TEMPLATE = "template"
    PENDING = "pending"
