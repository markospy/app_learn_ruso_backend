from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "sqlite:///./app_learn_ruso.db"

    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    # CORS - accepts comma-separated string and converts to list
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:8080"

    # App
    app_name: str = "Russian Learning API"
    app_version: str = "1.0.0"
    app_debug: bool = False  # Renamed to avoid conflict with system DEBUG env var

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS origins string to list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = ""  # No prefix, use exact field names
        # Ignore system environment variables that might conflict
        extra = "ignore"


settings = Settings()

