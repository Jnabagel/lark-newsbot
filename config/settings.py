"""Configuration management for the AI Agent Platform."""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LLM Configuration
    llm_provider: str = Field(default="openai", description="LLM provider: 'openai' or 'anthropic'")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    anthropic_base_url: Optional[str] = Field(default=None, description="Anthropic API base URL")

    # Embeddings
    embedding_model: str = Field(default="text-embedding-ada-002", description="Embedding model name")

    # Lark Webhook
    lark_webhook_url: Optional[str] = Field(default=None, description="Lark webhook URL")
    
    # Lark Bot (for receiving messages)
    lark_app_id: Optional[str] = Field(default=None, description="Lark bot app ID")
    lark_app_secret: Optional[str] = Field(default=None, description="Lark bot app secret")

    # News APIs
    newsapi_key: Optional[str] = Field(default=None, description="NewsAPI.org API key")
    newsdata_key: Optional[str] = Field(default=None, description="NewsData.io API key")

    # Vector Store
    chroma_persist_dir: str = Field(default="./chroma_db", description="ChromaDB persistence directory")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port (Render sets PORT)")

    def get_llm_api_key(self) -> str:
        """Get the appropriate API key based on provider."""
        if self.llm_provider.lower() == "openai":
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
            return self.openai_api_key
        elif self.llm_provider.lower() == "anthropic":
            if not self.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic")
            return self.anthropic_api_key
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    def validate(self) -> None:
        """Validate required settings."""
        if not self.lark_webhook_url:
            raise ValueError("LARK_WEBHOOK_URL is required")


# Global settings instance
settings = Settings()


