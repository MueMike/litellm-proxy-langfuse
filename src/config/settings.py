"""Configuration settings for LiteLLM proxy with LangFuse integration."""

import os
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LangFuse Configuration
    langfuse_public_key: Optional[str] = Field(None, alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: Optional[str] = Field(None, alias="LANGFUSE_SECRET_KEY")
    langfuse_host: str = Field("https://cloud.langfuse.com", alias="LANGFUSE_HOST")
    langfuse_enabled: bool = Field(True, alias="LANGFUSE_ENABLED")

    # Proxy Configuration
    proxy_host: str = Field("0.0.0.0", alias="PROXY_HOST")
    proxy_port: int = Field(8000, alias="PROXY_PORT")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    debug_mode: bool = Field(False, alias="DEBUG_MODE")

    # LLM Provider API Keys
    openai_api_key: Optional[str] = Field(None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, alias="ANTHROPIC_API_KEY")
    azure_api_key: Optional[str] = Field(None, alias="AZURE_API_KEY")
    azure_api_base: Optional[str] = Field(None, alias="AZURE_API_BASE")
    azure_api_version: Optional[str] = Field(None, alias="AZURE_API_VERSION")
    aws_access_key_id: Optional[str] = Field(None, alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(None, alias="AWS_SECRET_ACCESS_KEY")
    aws_region_name: Optional[str] = Field("us-east-1", alias="AWS_REGION_NAME")
    google_application_credentials: Optional[str] = Field(
        None, alias="GOOGLE_APPLICATION_CREDENTIALS"
    )
    vertex_project: Optional[str] = Field(None, alias="VERTEX_PROJECT")
    vertex_location: Optional[str] = Field("us-central1", alias="VERTEX_LOCATION")
    cohere_api_key: Optional[str] = Field(None, alias="COHERE_API_KEY")
    huggingface_api_key: Optional[str] = Field(None, alias="HUGGINGFACE_API_KEY")

    # Security & Authentication
    litellm_master_key: Optional[str] = Field(None, alias="LITELLM_MASTER_KEY")
    require_auth: bool = Field(False, alias="REQUIRE_AUTH")

    # Advanced Settings
    max_retries: int = Field(3, alias="MAX_RETRIES")
    request_timeout: int = Field(600, alias="REQUEST_TIMEOUT")
    enable_streaming: bool = Field(True, alias="ENABLE_STREAMING")
    enable_caching: bool = Field(False, alias="ENABLE_CACHING")
    cache_ttl: int = Field(3600, alias="CACHE_TTL")

    # Rate Limiting
    enable_rate_limiting: bool = Field(False, alias="ENABLE_RATE_LIMITING")
    rate_limit_rpm: int = Field(60, alias="RATE_LIMIT_RPM")
    rate_limit_tpm: int = Field(90000, alias="RATE_LIMIT_TPM")

    # Monitoring & Metrics
    enable_prometheus: bool = Field(True, alias="ENABLE_PROMETHEUS")
    prometheus_port: int = Field(9090, alias="PROMETHEUS_PORT")
    enable_request_logging: bool = Field(True, alias="ENABLE_REQUEST_LOGGING")
    enable_cost_tracking: bool = Field(True, alias="ENABLE_COST_TRACKING")

    # Config file paths
    config_file: str = Field("config/config.yaml", alias="CONFIG_FILE")
    model_config_file: str = Field("config/model_config.yaml", alias="MODEL_CONFIG_FILE")

    def is_langfuse_configured(self) -> bool:
        """Check if LangFuse is properly configured."""
        return bool(
            self.langfuse_enabled
            and self.langfuse_public_key
            and self.langfuse_secret_key
            and self.langfuse_host
        )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
