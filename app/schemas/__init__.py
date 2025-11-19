"""
Esquemas Pydantic para validación de entrada y salida de la API
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


# Base schemas
class BaseResponse(BaseModel):
    """Esquema base para respuestas de la API"""
    success: bool = True
    message: Optional[str] = None


# Student schemas
class StudentBase(BaseModel):
    """Esquema base para estudiante"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    program: Optional[str] = Field(None, max_length=100)


class StudentCreate(StudentBase):
    """Esquema para crear estudiante"""
    consent_data_processing: bool = True
    skills: List[str] = []
    soft_skills: List[str] = []
    projects: List[str] = []


class StudentUpdate(BaseModel):
    """Esquema para actualizar estudiante"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    program: Optional[str] = Field(None, max_length=100)


class StudentSkillsUpdate(BaseModel):
    """Esquema para actualizar habilidades de estudiante"""
    skills: Optional[List[str]] = None
    soft_skills: Optional[List[str]] = None
    projects: Optional[List[str]] = None


class StudentProfile(BaseModel):
    """Esquema para perfil completo de estudiante"""
    id: int
    name: str
    email: str
    program: Optional[str]
    skills: List[str] = []
    soft_skills: List[str] = []
    projects: List[str] = []
    cv_uploaded: bool = False
    cv_filename: Optional[str] = None
    created_at: datetime
    last_active: Optional[datetime] = None
    is_active: bool


class StudentPublic(BaseModel):
    """
    ✅ Esquema PÚBLICO de estudiante (para empresas sin autenticación)
    
    Incluye SOLO información no-sensible:
    - Datos básicos del perfil
    - Habilidades técnicas y blandas
    - Proyectos completados
    - Indicadores de CV (pero NO contenido)
    - Metadatos públicos
    
    EXCLUYE datos sensibles:
    - Email (encriptado)
    - Teléfono (encriptado)  
    - Historiales académicos detallados
    - Contenido del CV (profile_text)
    """
    id: int
    name: str
    program: Optional[str]
    skills: List[str] = []
    soft_skills: List[str] = []
    projects: List[str] = []
    
    # ✅ NUEVO: Información de CV (metadata, pero NO contenido)
    cv_uploaded: bool = False
    cv_filename: Optional[str] = None
    
    # ✅ NUEVO: Metadatos no-sensibles
    created_at: datetime
    last_active: Optional[datetime] = None


# Company schemas
class CompanyBase(BaseModel):
    """Esquema base para empresa"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    industry: Optional[str] = Field(None, max_length=50)
    size: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=100)


class CompanyCreate(CompanyBase):
    """Esquema para crear empresa"""
    pass


class CompanyProfile(CompanyBase):
    """Esquema para perfil de empresa"""
    id: int
    is_verified: bool
    is_active: bool
    created_at: datetime


# Job Position schemas
class JobPositionBase(BaseModel):
    """Esquema base para posición laboral"""
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10)
    requirements: Optional[str] = None
    location: Optional[str] = Field(None, max_length=100)
    salary_range: Optional[str] = Field(None, max_length=50)
    job_type: str = Field(default="full-time")


class JobPositionCreate(JobPositionBase):
    """Esquema para crear posición laboral"""
    pass


class JobPositionResponse(JobPositionBase):
    """Esquema de respuesta para posición laboral"""
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None


# Job Search schemas
class JobItem(BaseModel):
    """Esquema para trabajo encontrado en búsqueda"""
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    description: Optional[str] = None
    match_score: Optional[float] = None


class JobSearchRequest(BaseModel):
    """Esquema para solicitud de búsqueda de trabajos"""
    query: str = Field(..., min_length=1)
    location: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=50)


class JobRecommendationResponse(BaseModel):
    """Esquema para respuesta de recomendaciones"""
    student_id: int
    jobs: List[JobItem]
    total_found: int
    query_used: str
    generated_at: datetime


# Matching schemas
class MatchingCriteria(BaseModel):
    """Criterios para filtrado y matching"""
    skills: Optional[List[str]] = None
    projects: Optional[List[str]] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None


class MatchResult(BaseModel):
    """Resultado de matching"""
    student: StudentPublic
    score: float
    matching_skills: List[str] = []
    matching_projects: List[str] = []


# Resume upload schemas
class ResumeUploadRequest(BaseModel):
    """Metadatos para subida de currículum"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    program: Optional[str] = Field(None, max_length=100)


class ResumeAnalysisResponse(BaseModel):
    """Respuesta del análisis de currículum"""
    student: StudentProfile
    extracted_skills: List[str]
    extracted_soft_skills: List[str]
    extracted_projects: List[str]
    analysis_confidence: float = 0.0


# Admin schemas
class KPIResponse(BaseModel):
    """Respuesta de KPIs para administradores"""
    total_students: int
    active_students: int
    total_companies: int
    verified_companies: int
    total_positions: int
    active_positions: int
    matches_generated_last_30d: int
    avg_results_per_match: float
    student_placement_rate: float
    generated_at: datetime


class AuditLogResponse(BaseModel):
    """Respuesta de log de auditoría"""
    id: int
    actor_role: str
    action: str
    resource: Optional[str]
    success: bool
    created_at: datetime


# Authentication schemas
class UserContext(BaseModel):
    """Contexto de usuario autenticado"""
    role: str
    user_id: Optional[int] = None
    email: Optional[str] = None
    permissions: List[str] = []


class UserRegister(BaseModel):
    """Esquema para registro de usuario"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    role: str = Field(..., pattern="^(student|company|admin)$")
    password: str = Field(..., min_length=6, description="Contraseña del usuario")
    # Campos específicos por rol
    program: Optional[str] = Field(None, max_length=100, description="Para estudiantes")
    industry: Optional[str] = Field(None, max_length=50, description="Para empresas")
    company_size: Optional[str] = Field(None, max_length=20, description="Para empresas")
    location: Optional[str] = Field(None, max_length=100, description="Para empresas")


class LoginRequest(BaseModel):
    """Esquema para login con email y contraseña"""
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=6, description="Contraseña del usuario")


class UserLoginResponse(BaseModel):
    """Respuesta de login exitoso"""
    user_id: int
    name: str
    email: str
    role: str
    api_key: str
    key_id: str
    expires_at: Optional[datetime] = None
    scopes: List[str] = []


class ApiKeyCreate(BaseModel):
    """Esquema para crear nueva API key"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    scopes: List[str] = []
    expires_days: Optional[int] = Field(None, ge=1, le=365, description="Días hasta expiración")
    allowed_ips: Optional[List[str]] = None
    rate_limit: int = Field(default=1000, ge=100, le=10000)


class ApiKeyResponse(BaseModel):
    """Respuesta con información de API key"""
    key_id: str
    name: str
    description: Optional[str]
    key_prefix: str
    scopes: List[str]
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime]
    usage_count: int
    expires_at: Optional[datetime]
    rate_limit: int


class ApiKeyCreatedResponse(BaseModel):
    """Respuesta al crear una nueva API key (incluye la clave completa)"""
    api_key: str  # Solo se muestra una vez
    key_info: ApiKeyResponse


class ApiKeysList(BaseModel):
    """Lista de API keys del usuario"""
    keys: List[ApiKeyResponse]
    total: int


# Error schemas
class ErrorResponse(BaseModel):
    """Esquema para respuestas de error"""
    success: bool = False
    error_code: str
    message: str
    details: Optional[dict] = None


# Pagination schemas
class PaginatedResponse(BaseModel):
    """Esquema para respuestas paginadas"""
    items: List[dict]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool
