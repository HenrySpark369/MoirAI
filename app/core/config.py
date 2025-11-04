"""
Configuración central de la aplicación MoirAI
Manejo de variables de entorno y configuraciones de seguridad
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Configuración principal de la aplicación"""
    
    # Base configuration
    PROJECT_NAME: str = "MoirAI - UNRC Job Matching Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./moirai.db",
        description="URL de conexión a la base de datos"
    )
    
    # Security
    # IMPORTANT: SECRET_KEY must be set in environment variables (.env file)
    # Generate a secure key using: python -c "import secrets; print(secrets.token_urlsafe(32))"
    # Never commit the actual SECRET_KEY to version control
    SECRET_KEY: str = Field(
        ...,
        description="Clave secreta para JWT tokens - REQUERIDA en .env"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # CORS - URLs permitidas para el frontend (configurables via .env)
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://localhost:8080",
        "http://localhost:5173",  # Vite default port
        "http://localhost:5174"   # Vite alternative port
    ]
    
    # Job Search Providers
    JSEARCH_API_KEY: Optional[str] = None
    JSEARCH_HOST: str = "jsearch.p.rapidapi.com"
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [".pdf", ".docx", ".txt"]
    
    # NLP Configuration
    SPACY_MODEL: str = "en_core_web_sm"
    MAX_SKILLS_EXTRACTED: int = 30
    MAX_SOFT_SKILLS_EXTRACTED: int = 20
    MAX_PROJECTS_EXTRACTED: int = 20
    
    # Privacy and Security (LFPDPPP compliance)
    DATA_RETENTION_DAYS: int = 365
    REQUIRE_CONSENT: bool = True
    ENABLE_AUDIT_LOGGING: bool = True
    
    # Performance
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # API Keys por rol (desarrollo - reemplazar con OAuth2 en producción)
    ADMIN_API_KEYS: List[str] = []
    COMPANY_API_KEYS: List[str] = []
    STUDENT_API_KEYS: List[str] = []

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    class Config:
        env_file = ".env"
        case_sensitive = True

# Instancia global de configuración
settings = Settings()
