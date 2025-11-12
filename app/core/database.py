"""
Configuración y manejo de la base de datos
Soporta SQLite para desarrollo y PostgreSQL para producción
"""
from sqlmodel import create_engine, Session, SQLModel
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Determine database type and create engine
is_sqlite = "sqlite" in settings.DATABASE_URL
is_postgresql = "postgresql" in settings.DATABASE_URL

# Engine configuration
engine_kwargs = {
    "echo": False,  # Cambiar a True para debug SQL
}

# Database-specific configurations
if is_sqlite:
    # SQLite configuration
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    logger.info("📊 Using SQLite database (development)")
    
elif is_postgresql:
    # PostgreSQL configuration with connection pooling
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "pool_pre_ping": settings.DB_POOL_PRE_PING,
    })
    logger.info(f"📊 Using PostgreSQL database (production)")
    logger.info(f"   Pool size: {settings.DB_POOL_SIZE}")
    logger.info(f"   Max overflow: {settings.DB_MAX_OVERFLOW}")
    logger.info(f"   Pool recycle: {settings.DB_POOL_RECYCLE}s")

# Create engine
engine = create_engine(settings.DATABASE_URL, **engine_kwargs)


def create_db_and_tables():
    """Crear todas las tablas de la base de datos"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency para obtener sesión de base de datos"""
    with Session(engine) as session:
        yield session
