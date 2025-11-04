"""
Modelos de datos para MoirAI
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

# Importar modelos específicos
from .user import User, UserCreate, UserRead, UserUpdate
from .job_scraping import (
    JobApplicationDB,
    SearchQueryDB,
    SearchResultDB,
    UserJobAlertDB,
    ScrapingLogDB
)


# ============================================================================
# MODELOS DE DOMINIO PRINCIPAL
# ============================================================================

class Student(SQLModel, table=True):
    """Modelo de estudiante UNRC"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, description="Nombre completo del estudiante")
    email: str = Field(unique=True, max_length=100, description="Email institucional")
    program: Optional[str] = Field(max_length=100, description="Programa académico")
    
    # Password hash (opcional - para autenticación futura)
    password_hash: Optional[str] = Field(default=None, max_length=255, description="Hash de contraseña")
    
    # Datos de privacidad y consentimiento (LFPDPPP)
    consent_data_processing: bool = Field(default=True, description="Consentimiento para procesamiento de datos")
    consent_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Perfil y habilidades (almacenados como JSON strings)
    profile_text: Optional[str] = Field(description="Texto crudo del currículum")
    skills: Optional[str] = Field(description="Lista de habilidades técnicas (JSON)")
    soft_skills: Optional[str] = Field(description="Lista de habilidades blandas (JSON)")
    projects: Optional[str] = Field(description="Lista de proyectos (JSON)")
    
    # Metadatos
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    last_active: Optional[datetime] = None
    is_active: bool = Field(default=True)


class Company(SQLModel, table=True):
    """Modelo de empresa colaboradora"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, description="Nombre de la empresa")
    email: str = Field(unique=True, max_length=100, description="Email de contacto")
    industry: Optional[str] = Field(max_length=50, description="Sector industrial")
    size: Optional[str] = Field(max_length=20, description="Tamaño de empresa (startup, pequeña, mediana, grande)")
    location: Optional[str] = Field(max_length=100, description="Ubicación principal")
    
    # Password hash (opcional - para autenticación futura)
    password_hash: Optional[str] = Field(default=None, max_length=255, description="Hash de contraseña")
    
    # Estado y verificación
    is_verified: bool = Field(default=False, description="Empresa verificada por UNRC")
    is_active: bool = Field(default=True)
    
    # Metadatos
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class JobPosition(SQLModel, table=True):
    """
    Modelo unificado de posición laboral
    Sirve tanto para empleos publicados por empresas como para empleos scrapeados
    """
    __tablename__ = "job_positions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Información básica (campos obligatorios)
    title: str = Field(max_length=200, description="Título del puesto")
    company: str = Field(max_length=150, description="Nombre de la empresa")
    location: str = Field(max_length=150, description="Ubicación del trabajo")
    description: str = Field(description="Descripción completa del puesto")
    
    # Campos específicos para empleos de empresas registradas
    company_id: Optional[int] = Field(default=None, foreign_key="company.id", description="ID de empresa registrada (si aplica)")
    
    # Campos específicos para empleos scrapeados
    external_job_id: Optional[str] = Field(default=None, index=True, description="ID externo del empleo (ej: OCC ID)")
    external_url: Optional[str] = Field(default=None, description="URL original del empleo")
    source: str = Field(default="internal", description="Fuente del empleo (internal, occ, linkedin, etc.)")
    
    # Información detallada
    requirements: Optional[str] = Field(default=None, description="Requisitos técnicos y experiencia")
    salary_range: Optional[str] = Field(default=None, max_length=100, description="Rango salarial")
    benefits: Optional[str] = Field(default=None, description="Beneficios ofrecidos (JSON)")
    
    # Categorización y filtros
    job_type: str = Field(default="full-time", description="Tipo de trabajo (full-time, part-time, contract, etc.)")
    work_mode: Optional[str] = Field(default=None, description="Modalidad (presencial, remoto, híbrido)")
    category: Optional[str] = Field(default=None, max_length=100, description="Categoría laboral")
    experience_level: Optional[str] = Field(default=None, max_length=50, description="Nivel de experiencia requerido")
    education_required: Optional[str] = Field(default=None, max_length=100, description="Educación requerida")
    skills: Optional[str] = Field(default=None, description="Habilidades requeridas (JSON)")
    
    # Información de la empresa (para empleos externos)
    company_verified: bool = Field(default=False, description="Si la empresa está verificada")
    company_logo: Optional[str] = Field(default=None, description="URL del logo de la empresa")
    
    # Metadatos y estado
    publication_date: Optional[datetime] = Field(default=None, description="Fecha de publicación original")
    scraped_at: Optional[datetime] = Field(default=None, description="Fecha de scraping (si aplica)")
    is_active: bool = Field(default=True, description="Si el empleo está activo")
    is_featured: bool = Field(default=False, description="Si es empleo destacado")
    expires_at: Optional[datetime] = Field(default=None, description="Fecha de expiración")
    
    # Metadatos del sistema (updated_at es suficiente)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Última actualización")


# ============================================================================
# MODELOS DE AUDITORÍA Y SEGURIDAD
# ============================================================================

class JobMatchEvent(SQLModel, table=True):
    """Eventos de matching entre estudiante y trabajos"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id")
    job_position_id: Optional[int] = Field(foreign_key="job_positions.id", default=None)
    
    # Detalles del matching
    query: str = Field(description="Query utilizada para la búsqueda")
    match_score: Optional[float] = Field(description="Puntuación de compatibilidad")
    num_results: int = Field(description="Número de resultados obtenidos")
    source: str = Field(default="internal", description="Fuente del matching (internal, occ, jsearch, etc.)")
    
    # Metadatos
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(SQLModel, table=True):
    """Log de auditoría para cumplimiento de seguridad y privacidad"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Actor que realizó la acción
    actor_role: str = Field(max_length=20, description="Rol del actor (student, company, admin)")
    actor_id: Optional[str] = Field(max_length=100, description="Identificador del actor")
    actor_ip: Optional[str] = Field(max_length=45, description="Dirección IP del actor")
    
    # Acción realizada
    action: str = Field(max_length=50, description="Acción realizada")
    resource: Optional[str] = Field(max_length=100, description="Recurso afectado")
    details: Optional[str] = Field(description="Detalles adicionales de la acción")
    
    # Estado y resultado
    success: bool = Field(default=True, description="Si la acción fue exitosa")
    error_message: Optional[str] = Field(description="Mensaje de error si aplica")
    
    # Metadatos
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserSession(SQLModel, table=True):
    """Sesiones de usuario para tracking y seguridad"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(description="ID del usuario")
    user_type: str = Field(max_length=20, description="Tipo de usuario")
    session_token: str = Field(unique=True, description="Token de sesión")
    ip_address: Optional[str] = Field(max_length=45)
    user_agent: Optional[str] = Field(description="User agent del navegador")
    
    # Estado
    is_active: bool = Field(default=True)
    expires_at: datetime = Field(description="Fecha de expiración")
    
    # Metadatos
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)


class ApiKey(SQLModel, table=True):
    """API Keys para autenticación de usuarios"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    key_id: str = Field(unique=True, max_length=32, description="Identificador público de la clave")
    key_hash: str = Field(max_length=256, description="Hash de la clave secreta")
    key_prefix: str = Field(max_length=10, description="Prefijo visible de la clave")
    
    # Usuario propietario
    user_id: int = Field(description="ID del usuario propietario")
    user_type: str = Field(max_length=20, description="Tipo de usuario (student, company, admin)")
    user_email: str = Field(max_length=100, description="Email del usuario")
    
    # Metadatos de la clave
    name: str = Field(max_length=100, description="Nombre descriptivo de la clave")
    description: Optional[str] = Field(description="Descripción del propósito de la clave")
    
    # Permisos y alcances
    scopes: str = Field(description="Permisos JSON de la clave")
    
    # Control de acceso
    allowed_ips: Optional[str] = Field(description="IPs permitidas (JSON array)")
    rate_limit: int = Field(default=1000, description="Límite de requests por hora")
    
    # Estado y seguridad
    is_active: bool = Field(default=True)
    last_used_at: Optional[datetime] = None
    usage_count: int = Field(default=0, description="Número de veces usada")
    
    # Expiración
    expires_at: Optional[datetime] = None
    
    # Metadatos
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


# ============================================================================
# EXPORTACIONES
# ============================================================================

__all__ = [
    # User models
    "User",
    "UserCreate", 
    "UserRead",
    "UserUpdate",
    
    # Core models
    "Student",
    "Company", 
    "JobPosition",
    "JobMatchEvent",
    "AuditLog",
    "UserSession",
    "ApiKey",
    
    # Job scraping models
    "JobApplicationDB",
    "SearchQueryDB",
    "SearchResultDB", 
    "UserJobAlertDB",
    "ScrapingLogDB",
]
