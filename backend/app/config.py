# ============================================
# AfiliaML — Configuração de Ambiente
# Carrega e valida variáveis de ambiente com Pydantic
# ============================================

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configurações do AfiliaML carregadas de variáveis de ambiente."""

    # Servidor
    PORT: int = 3333
    ENV: str = "development"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # CORS
    CORS_ORIGIN: str = "http://localhost:5173,http://localhost:3000"

    # URL base do backend (para links de redirecionamento)
    BASE_URL: str = "http://localhost:3333"

    # Template de link de afiliado
    AFFILIATE_LINK_TEMPLATE: str = (
        "https://www.mercadolivre.com.br/afiliado?url={url}&aff_id=SEU_ID_AQUI"
    )

    # Scraper
    SCRAPER_CRON: str = "0 * * * *"
    SCRAPER_URLS: str = "https://www.mercadolivre.com.br/ofertas"

    # Mercado Livre API
    ML_CLIENT_ID: str = ""
    ML_CLIENT_SECRET: str = ""
    ML_REDIRECT_URI: str = "http://localhost:3333/api/auth/callback"

    # Mercado Livre Afiliados (Oficial)
    MATT_TOOL: str = "48707087"
    MATT_SOURCE: str = "afiliados"
    MATT_MEDIUM: str = "social"

    # Ética e Privacidade
    IP_HASH_SALT: str = "afiliaml-default-salt-2024"
    AFFILIATE_DISCLAIMER: str = (
        "\n\n*Link de afiliado — posso ganhar comissão sem custo adicional para você.*"
    )

    @property
    def cors_origins(self) -> list[str]:
        """Retorna lista de origens CORS permitidas."""
        return [o.strip() for o in self.CORS_ORIGIN.split(",") if o.strip()]

    @property
    def scraper_urls(self) -> list[str]:
        """Retorna lista de URLs do scraper."""
        return [u.strip() for u in self.SCRAPER_URLS.split(",") if u.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Singleton das configurações."""
    return Settings()
