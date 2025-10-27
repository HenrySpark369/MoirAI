"""
Modelos de base de datos para el sistema de rastreo de empleos
Utiliza el modelo unificado JobPosition del archivo __init__.py
"""

from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship, JSON, Column


class SearchQueryDB(SQLModel, table=True):
    """Modelo para almacenar consultas de búsqueda realizadas"""
    __tablename__ = "search_queries"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    keyword: str
    location: Optional[str] = None
    filters: dict = Field(default={}, sa_column=Column(JSON))
    total_results: int = 0
    
    # Metadatos
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relaciones
    search_results: List["SearchResultDB"] = Relationship(back_populates="search_query")


class SearchResultDB(SQLModel, table=True):
    """Modelo para vincular búsquedas con ofertas encontradas"""
    __tablename__ = "search_results"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    search_query_id: int = Field(foreign_key="search_queries.id")
    job_position_id: int = Field(foreign_key="job_positions.id")
    relevance_score: Optional[float] = None
    position_in_results: int  # Posición en los resultados de búsqueda
    
    # Metadatos
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relaciones
    search_query: SearchQueryDB = Relationship(back_populates="search_results")


class JobApplicationDB(SQLModel, table=True):
    """Modelo para rastrear aplicaciones a empleos"""
    __tablename__ = "job_applications"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    job_position_id: int = Field(foreign_key="job_positions.id")
    
    # Estado de la aplicación
    status: str = Field(default="pending", description="pending, applied, viewed, rejected, accepted")
    application_date: datetime = Field(default_factory=datetime.utcnow)
    external_application_url: Optional[str] = None
    notes: Optional[str] = None
    
    # Metadatos
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserJobAlertDB(SQLModel, table=True):
    """Modelo para alertas de trabajo personalizadas"""
    __tablename__ = "user_job_alerts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    
    # Criterios de alerta
    keywords: List[str] = Field(sa_column=Column(JSON))
    location: Optional[str] = None
    salary_min: Optional[int] = None
    work_mode: Optional[str] = None
    company_verified_only: bool = Field(default=False)
    
    # Configuración de notificaciones
    is_active: bool = Field(default=True)
    frequency: str = Field(default="daily", description="daily, weekly, immediate")
    last_notification: Optional[datetime] = None
    
    # Metadatos
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ScrapingLogDB(SQLModel, table=True):
    """Modelo para logging de actividades de scraping"""
    __tablename__ = "scraping_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Información de la operación
    operation_type: str = Field(description="search, detail_fetch, monitoring")
    search_keyword: Optional[str] = None
    results_count: int = Field(default=0)
    success: bool = Field(default=True)
    error_message: Optional[str] = None
    
    # Metadatos de rendimiento
    response_time_ms: Optional[int] = None
    source_url: Optional[str] = None
    
    # Metadatos
    created_at: datetime = Field(default_factory=datetime.utcnow)
