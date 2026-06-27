"""Lecture des variables d'environnement via Pydantic Settings."""
from pydantic import field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    groq_api_key: str = ""
    groq_model: str = "llama3-8b-8192"
    groq_timeout: int = 8
    frontend_urls: str | list[str] = "http://localhost:5173"
    environment: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @field_validator("frontend_urls", mode="before")
    @classmethod
    def parse_frontend_urls(cls, v):
        """Parse une string CSV en liste d'URLs.

        Accepte deux formats depuis l'env :
        - CSV : FRONTEND_URLS=http://localhost:5173,http://127.0.0.1:5173
        - JSON : FRONTEND_URLS=["http://localhost:5173","http://127.0.0.1:5173"]
        """
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            return [url.strip() for url in v.split(",") if url.strip()]
        raise ValueError(f"frontend_urls doit etre une liste ou une string CSV, recu : {type(v)}")

    @property
    def frontend_canonical_url(self) -> str:
        """URL principale du frontend, utilisee pour construire les liens publics."""
        return self.frontend_urls[0]

    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
