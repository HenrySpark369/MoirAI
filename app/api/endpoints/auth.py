"""
Endpoints para autenticación y gestión de usuarios
Incluye registro, login y gestión de API keys
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
import json

from app.core.database import get_session
from app.models import Student, Company, ApiKey, AuditLog
from app.schemas import (
    UserRegister, UserLoginResponse, UserResponse, ApiKeyCreate, ApiKeyCreatedResponse,
    ApiKeyResponse, ApiKeysList, UserContext, BaseResponse
)
from app.services.api_key_service import api_key_service
from app.middleware.auth import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserLoginResponse, status_code=201)
async def register_user(
    user_data: UserRegister,
    session: Session = Depends(get_session)
):
    """
    Registrar nuevo usuario y generar API key automáticamente
    
    Crea el perfil del usuario según su rol y genera una API key personal.
    """
    # Verificar si el email ya existe
    existing_student = session.execute(
        select(Student).where(Student.email == user_data.email)
    ).scalar_one_or_none()
    
    existing_company = session.execute(
        select(Company).where(Company.email == user_data.email)
    ).scalar_one_or_none()
    
    if existing_student or existing_company:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un usuario registrado con ese email"
        )
    
    # Crear usuario según el rol
    user_id = None
    
    # Hash de la contraseña
    password_hash = AuthService.get_password_hash(user_data.password)
    
    if user_data.role == "student":
        student = Student(
            name=user_data.name,
            email=user_data.email,
            password_hash=password_hash,
            program=user_data.program,
            consent_data_processing=True,
            skills="[]",
            soft_skills="[]", 
            projects="[]"
        )
        session.add(student)
        session.commit()
        session.refresh(student)
        user_id = student.id
        
    elif user_data.role == "company":
        company = Company(
            name=user_data.name,
            email=user_data.email,
            password_hash=password_hash,
            industry=user_data.industry,
            size=user_data.company_size,
            location=user_data.location,
            is_verified=False  # Requiere verificación manual
        )
        session.add(company)
        session.commit()
        session.refresh(company)
        user_id = company.id
        
    elif user_data.role == "admin":
        # Los administradores deben ser creados manualmente por seguridad
        raise HTTPException(
            status_code=403,
            detail="Los administradores deben ser creados manualmente"
        )
    
    # Generar API key automática
    api_key_data = ApiKeyCreate(
        name=f"Clave principal - {user_data.name}",
        description="API key generada automáticamente al registrarse",
        expires_days=365  # Expira en 1 año
    )
    
    api_key_response = api_key_service.create_api_key(
        session=session,
        user_id=user_id,
        user_type=user_data.role,
        user_email=user_data.email,
        key_data=api_key_data
    )
    
    # Registrar en auditoría
    audit_log = AuditLog(
        actor_role=user_data.role,
        actor_id=user_data.email,
        action="register_user",
        resource=f"user_id:{user_id}",
        success=True,
        details=f"Nuevo usuario {user_data.role} registrado"
    )
    session.add(audit_log)
    session.commit()
    
    # Generar token JWT
    token_data = {
        "sub": user_data.email,
        "role": user_data.role,
        "user_id": user_id
    }
    access_token = AuthService.create_access_token(token_data)

    # Construir respuesta
    user_response = UserResponse(
        id=user_id,
        name=user_data.name,
        email=user_data.email,
        role=user_data.role
    )

    return UserLoginResponse(
        token=access_token,
        user=user_response,
        api_key=api_key_response.key
    )


@router.post("/api-keys", response_model=ApiKeyCreatedResponse)
async def create_api_key(
    key_data: ApiKeyCreate,
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Crear nueva API key para el usuario autenticado
    
    Permite a los usuarios generar claves adicionales con diferentes permisos.
    """
    if current_user.role == "anonymous":
        raise HTTPException(
            status_code=401,
            detail="Debe autenticarse para crear API keys"
        )
    
    if not current_user.user_id:
        raise HTTPException(
            status_code=400,
            detail="No se pudo identificar el usuario"
        )
    
    # Verificar límite de claves por usuario
    existing_keys = session.exec(
        select(ApiKey).where(
            ApiKey.user_id == current_user.user_id,
            ApiKey.user_type == current_user.role,
            ApiKey.is_active == True
        )
    ).all()
    
    if len(existing_keys) >= 10:  # Máximo 10 claves activas por usuario
        raise HTTPException(
            status_code=400,
            detail="Ha alcanzado el límite máximo de API keys (10)"
        )
    
    api_key_response = api_key_service.create_api_key(
        session=session,
        user_id=current_user.user_id,
        user_type=current_user.role,
        user_email=current_user.email,
        key_data=key_data
    )
    
    # Registrar en auditoría
    audit_log = AuditLog(
        actor_role=current_user.role,
        actor_id=current_user.email,
        action="create_api_key",
        resource=f"key_id:{api_key_response.key_info.key_id}",
        success=True,
        details=f"Nueva API key creada: {key_data.name}"
    )
    session.add(audit_log)
    session.commit()
    
    return api_key_response


@router.get("/api-keys", response_model=ApiKeysList)
async def list_api_keys(
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Listar todas las API keys del usuario autenticado
    
    Muestra información de las claves sin exponer los valores secretos.
    """
    if current_user.role == "anonymous" or not current_user.user_id:
        raise HTTPException(
            status_code=401,
            detail="Debe autenticarse para ver sus API keys"
        )
    
    keys = api_key_service.get_user_api_keys(
        session=session,
        user_id=current_user.user_id,
        user_type=current_user.role
    )
    
    return ApiKeysList(
        keys=keys,
        total=len(keys)
    )


@router.delete("/api-keys/{key_id}", response_model=BaseResponse)
async def revoke_api_key(
    key_id: str,
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Revocar una API key específica
    
    Desactiva permanentemente la clave especificada.
    """
    if current_user.role == "anonymous" or not current_user.user_id:
        raise HTTPException(
            status_code=401,
            detail="Debe autenticarse para revocar API keys"
        )
    
    success = api_key_service.revoke_api_key(
        session=session,
        key_id=key_id,
        user_id=current_user.user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="API key no encontrada o no pertenece al usuario"
        )
    
    # Registrar en auditoría
    audit_log = AuditLog(
        actor_role=current_user.role,
        actor_id=current_user.email,
        action="revoke_api_key",
        resource=f"key_id:{key_id}",
        success=True,
        details="API key revocada por el usuario"
    )
    session.add(audit_log)
    session.commit()
    
    return BaseResponse(
        success=True,
        message="API key revocada exitosamente"
    )


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Obtener información del usuario autenticado
    
    Retorna el contexto y permisos del usuario actual.
    """
    if current_user.role == "anonymous":
        raise HTTPException(
            status_code=401,
            detail="Debe autenticarse para ver su información"
        )
    
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "role": current_user.role,
        "permissions": current_user.permissions
    }


@router.post("/cleanup-expired-keys", response_model=BaseResponse)
async def cleanup_expired_keys(
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Limpiar claves expiradas (solo admin)
    
    Tarea de mantenimiento para desactivar claves vencidas.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Solo administradores pueden ejecutar tareas de limpieza"
        )
    
    cleaned_count = api_key_service.cleanup_expired_keys(session)
    
    # Registrar en auditoría
    audit_log = AuditLog(
        actor_role=current_user.role,
        actor_id=current_user.email,
        action="cleanup_expired_keys",
        resource="system",
        success=True,
        details=f"Limpiadas {cleaned_count} claves expiradas"
    )
    session.add(audit_log)
    session.commit()
    
    return BaseResponse(
        success=True,
        message=f"Se desactivaron {cleaned_count} claves expiradas"
    )
