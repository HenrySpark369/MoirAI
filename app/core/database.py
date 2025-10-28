"""
Configuración y manejo de la base de datos
"""
from sqlmodel import create_engine, Session, SQLModel
from app.core.config import settings


# Engine de base de datos
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Cambiar a True para debug SQL
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)


async def create_db_and_tables():
    """Crear todas las tablas de la base de datos"""
    SQLModel.metadata.create_all(engine)


async def get_session():
    """Dependency para obtener sesión de base de datos"""
    async with Session(engine) as session:
        yield session
