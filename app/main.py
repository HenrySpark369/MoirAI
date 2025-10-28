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

from .core.config import settings
from .core.database import create_db_and_tables
from .api.endpoints import students, auth
from .schemas import ErrorResponse

# Crear aplicación FastAPI
# Crear aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="MoirAI - Plataforma de Matching Laboral UNRC"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers de endpoints
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(students.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def on_startup():
    """Inicialización de la aplicación"""
    await create_db_and_tables()

# Manejo de errores
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

# Event handlers
@app.on_event("startup")
async def on_startup():
    """Initialize database on startup"""
    await create_db_and_tables()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)