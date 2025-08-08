"""
Settings configuration for PropCalc
Modern Pydantic Settings with environment variable support
"""

import os
from typing import Optional, List
from functools import lru_cache

from pydantic import Field, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = Field(default="PropCalc Backend", description="Application name")
    version: str = Field(default="2.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="production", description="Environment (development, staging, production)")
    
    # Database
    database_url: str = Field(
        default="postgresql://vantage_user:vantage_password@localhost:5432/vantage_ai",
        description="Database connection URL"
    )
    
    # API
    api_prefix: str = Field(default="/api", description="API prefix")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="CORS allowed origins"
    )
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT tokens"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration in minutes")
    
    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    
    # External APIs
    dld_api_url: Optional[str] = Field(None, description="DLD API URL")
    dld_api_key: Optional[str] = Field(None, description="DLD API key")
    
    # Sentry
    sentry_dsn: Optional[str] = Field(None, description="Sentry DSN")
    sentry_environment: str = Field(default="production", description="Sentry environment")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, description="Rate limit per minute")
    rate_limit_per_hour: int = Field(default=1000, description="Rate limit per hour")
    
    # Cache
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    cache_max_size: int = Field(default=1000, description="Cache max size")
    
    # File Upload
    max_file_size: int = Field(default=10 * 1024 * 1024, description="Max file size in bytes")
    allowed_file_types: List[str] = Field(
        default=[".csv", ".xlsx", ".json"],
        description="Allowed file types"
    )
    
    # Data Processing
    batch_size: int = Field(default=1000, description="Batch size for data processing")
    max_workers: int = Field(default=4, description="Maximum number of workers")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    metrics_port: int = Field(default=9090, description="Metrics port")
    
    # DLD Integration
    dld_data_directory: str = Field(
        default="./data",
        description="Directory for DLD data files"
    )
    dld_update_interval: int = Field(
        default=3600,
        description="DLD data update interval in seconds"
    )
    
    # KML Integration
    kml_data_directory: str = Field(
        default="./data",
        description="Directory for KML data files"
    )
    
    # Validation
    @validator("environment")
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v.upper()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Create settings instance
settings = get_settings()

# Environment-specific settings
class DevelopmentSettings(Settings):
    """Development environment settings"""
    debug: bool = True
    environment: str = "development"
    log_level: str = "DEBUG"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]

class StagingSettings(Settings):
    """Staging environment settings"""
    environment: str = "staging"
    debug: bool = False
    log_level: str = "INFO"

class ProductionSettings(Settings):
    """Production environment settings"""
    environment: str = "production"
    debug: bool = False
    log_level: str = "WARNING"
    cors_origins: List[str] = ["https://propcalc.ai", "https://www.propcalc.ai"]

def get_environment_settings() -> Settings:
    """Get environment-specific settings"""
    env = os.getenv("ENVIRONMENT", "production").lower()
    
    if env == "development":
        return DevelopmentSettings()
    elif env == "staging":
        return StagingSettings()
    else:
        return ProductionSettings()

# Export settings
__all__ = ["Settings", "get_settings", "get_environment_settings", "settings"]
