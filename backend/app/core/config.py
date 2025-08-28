"""
Application Configuration
"""
from typing import List, Optional, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    email_reset_token_expire_hours: int = Field(default=48, env="EMAIL_RESET_TOKEN_EXPIRE_HOURS")
    
    # Admin User
    first_superuser_email: str = Field(default="admin@pneumonia-app.com", env="FIRST_SUPERUSER_EMAIL")
    first_superuser_password: str = Field(default="admin123!", env="FIRST_SUPERUSER_PASSWORD")
    
    # Model Configuration
    onnx_model_path: str = Field(default="model/pneumonia_model.onnx", env="ONNX_MODEL_PATH")
    model_config_path: str = Field(default="model/model_config.json", env="MODEL_CONFIG_PATH")
    confidence_threshold: float = Field(default=0.7, env="CONFIDENCE_THRESHOLD")
    model_input_size: int = Field(default=224, env="MODEL_INPUT_SIZE")
    
    # File Upload
    upload_dir: str = Field(default="uploads", env="UPLOAD_DIR")
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    allowed_extensions: List[str] = Field(default=["jpg", "jpeg", "png", "dcm"], env="ALLOWED_EXTENSIONS")
    
    # CORS
    backend_cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        env="BACKEND_CORS_ORIGINS"
    )
    
    # Redis (optional)
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # Medical Compliance
    enable_audit_logging: bool = Field(default=True, env="ENABLE_AUDIT_LOGGING")
    data_retention_days: int = Field(default=2555, env="DATA_RETENTION_DAYS")  # 7 years
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return v
    
    @field_validator("allowed_extensions", mode="before")
    @classmethod
    def assemble_allowed_extensions(cls, v):
        """Parse allowed extensions from string."""
        if isinstance(v, str):
            return [ext.strip().lower() for ext in v.split(",")]
        elif isinstance(v, list):
            return [ext.lower() for ext in v]
        return v


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
