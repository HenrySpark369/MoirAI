"""
Aplicación principal de MoirAI
FastAPI app con todos los endpoints y configuración
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn
from datetime import datetime

from app.core.config import settings
from app.core.database import create_db_and_tables
from app.api.endpoints import students, auth
from app.schemas import ErrorResponse


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    **MoirAI - Plataforma de Matching Laboral UNRC**
    
    API RESTful para conectar estudiantes de la Universidad Nacional de Río Cuarto 
    con oportunidades laborales mediante análisis inteligente de perfiles y matchmaking automatizado.
    
    ## Características principales:
    
    -   Análisis NLP de Currículums**: Extracción automática de habilidades técnicas, blandas y proyectos
    *   Matchmaking Inteligente**: Algoritmos de compatibilidad entre perfiles y vacantes
    *   Búsqueda Multi-proveedor**: Integración con múltiples fuentes de trabajos
    *   Gestión de Roles**: Acceso diferenciado para estudiantes, empresas y administradores
    *   Cumplimiento LFPDPPP**: Protección de datos y auditoría integrada
    *   Arquitectura Escalable**: FastAPI + PostgreSQL + modelos de ML

    ## Roles de Usuario:
    
    * **Estudiantes**: Gestión de perfil, recomendaciones personalizadas
    * **Empresas**: Búsqueda y filtrado de candidatos, publicación de vacantes
    * **Administradores**: KPIs, gestión de usuarios, auditoría del sistema
    """,
    contact={
        "name": "UNRC - Ciencia de Datos para Negocios",
        "url": "https://www.ing.unrc.edu.ar/",
        "email": "contacto@ing.unrc.edu.ar"
    },
    license_info={
        "name": "Apache License, Version 2.0",
        "url": "https://opensource.org/license/apache-2-0"
    }
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Event handlers
@app.on_event("startup")
async def startup_event():
    """Inicializar aplicación"""
    # Crear tablas de base de datos
    create_db_and_tables()
    print(f"🚀 {settings.PROJECT_NAME} iniciado correctamente")
    print(f"📊 Base de datos: {settings.DATABASE_URL}")
    print(f"🔐 Audit logging: {'✅' if settings.ENABLE_AUDIT_LOGGING else '❌'}")


@app.on_event("shutdown")
async def shutdown_event():
    """Limpiar recursos al cerrar"""
    print(f"🛑 {settings.PROJECT_NAME} detenido")


# Manejadores de errores globales
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejar errores de validación de Pydantic"""
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Error de validación en los datos enviados",
            details={
                "errors": exc.errors(),
                "body": exc.body if hasattr(exc, 'body') else None
            }
        ).dict()
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Manejar errores HTTP generales"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_code="HTTP_ERROR",
            message=str(exc.detail),
            details={
                "status_code": exc.status_code,
                "path": str(request.url.path)
            }
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Manejar errores generales no capturados"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error_code="INTERNAL_ERROR",
            message="Error interno del servidor",
            details={
                "type": type(exc).__name__,
                "path": str(request.url.path)
            }
        ).dict()
    )


# Endpoints principales
@app.get("/", tags=["root"])
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": f"Bienvenido a {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint para monitoreo"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "environment": "development" if settings.DATABASE_URL.startswith("sqlite") else "production"
    }


@app.get("/info", tags=["info"])
async def api_info():
    """Información detallada de la API"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "Plataforma de matching laboral para estudiantes UNRC",
        "features": [
            "Análisis NLP de currículums",
            "Matchmaking inteligente",
            "Búsqueda multi-proveedor de trabajos",
            "Gestión de roles y permisos",
            "Auditoría y compliance LFPDPPP",
            "API RESTful escalable"
        ],
        "endpoints": {
            "students": "/api/v1/students - Gestión de estudiantes",
            "jobs": "/api/v1/jobs - Búsqueda de trabajos",
            "companies": "/api/v1/companies - Gestión de empresas", 
            "matching": "/api/v1/matching - Algoritmos de matchmaking",
            "admin": "/api/v1/admin - Panel administrativo"
        },
        "documentation": "/docs",
        "contact": "contacto@ing.unrc.edu.ar"
    }


@app.get("/compliance", tags=["compliance"])
async def compliance_info():
    """
    Información de cumplimiento y privacidad
    Transparencia según LFPDPPP y estándares ISO/IEC 27001
    """
    return {
        "privacy_by_design": True,
        "data_minimization": True,
        "pseudonymization": False,  # TODO: Implementar en producción
        "consent_required": settings.REQUIRE_CONSENT,
        "data_subject_rights": [
            "Acceso a datos personales",
            "Rectificación de datos incorrectos", 
            "Cancelación/eliminación de datos",
            "Oposición al tratamiento de datos"
        ],
        "retention_policy": f"Datos de estudiantes inactivos por {settings.DATA_RETENTION_DAYS} días son anonimizados",
        "audit_logging": settings.ENABLE_AUDIT_LOGGING,
        "encryption_at_rest": "Configurar cifrado a nivel de base de datos en producción",
        "encryption_in_transit": "TLS 1.3 requerido en producción",
        "data_protection_standards": [
            "Ley Federal de Protección de Datos Personales en Posesión de Particulares (LFPDPPP)",
            "ISO/IEC 27001 - Gestión de Seguridad de la Información"
        ],
        "contact_dpo": "dpo@unrc.edu.ar",
        "last_updated": "2025-01-15",
        "notice": "Esta información es de referencia. Consulte documentos legales oficiales para términos vinculantes."
    }


# Incluir routers de endpoints
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(students.router, prefix=settings.API_V1_STR)

# TODO: Incluir otros routers cuando estén implementados
# app.include_router(jobs.router, prefix=settings.API_V1_STR)
# app.include_router(companies.router, prefix=settings.API_V1_STR)
# app.include_router(matching.router, prefix=settings.API_V1_STR)
# app.include_router(admin.router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    # Ejecutar aplicación directamente
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
