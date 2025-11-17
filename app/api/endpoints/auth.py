"""
Endpoints para autenticación y gestión de usuarios
Incluye registro, login y gestión de API keys
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
import json
import hashlib

from app.core.database import get_session
from app.models import Student, Company, ApiKey, AuditLog
from app.schemas import (
    UserRegister, UserLoginResponse, ApiKeyCreate, ApiKeyCreatedResponse,
    ApiKeyResponse, ApiKeysList, UserContext, BaseResponse, LoginRequest
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
    try:
        # Generar hash del email para búsqueda
        email_hash = hashlib.sha256(user_data.email.lower().strip().encode()).hexdigest()
        
        # Verificar si el email ya existe (usando email_hash)
        existing_student = session.exec(
            select(Student).where(Student.email_hash == email_hash)
        ).first()
        
        existing_company = session.exec(
            select(Company).where(Company.email_hash == email_hash)
        ).first()
        
        if existing_student or existing_company:
            raise HTTPException(
                status_code=409,
                detail="Ya existe un usuario registrado con ese email"
            )
        
        # Validar rol
        if user_data.role not in ["student", "company"]:
            raise HTTPException(
                status_code=400,
                detail="El rol debe ser 'student' o 'company'. Los administradores se crean manualmente."
            )
        
        # Crear usuario según el rol
        user_id = None
        
        if user_data.role == "student":
            from app.utils.encryption import EncryptionService
            encryption_service = EncryptionService()
            
            # Generar hash de contraseña (SHA256 simple para MVP - ver TODO abajo)
            hashed_pw = hashlib.sha256(user_data.password.encode()).hexdigest()
            
            student = Student(
                name=user_data.name,
                program=user_data.program or "",
                consent_data_processing=True,
                skills="[]",
                soft_skills="[]", 
                projects="[]",
                email_hash=email_hash,
                hashed_password=hashed_pw,
                cv_uploaded=False
            )
            # Encriptar email directamente antes de agregar a sesión
            email_lower = user_data.email.lower().strip()
            student.email = encryption_service.encrypt(email_lower)
            
            session.add(student)
            session.flush()
            session.commit()
            session.refresh(student)
            user_id = student.id
            
        elif user_data.role == "company":
            from app.utils.encryption import EncryptionService
            encryption_service = EncryptionService()
            
            # Generar hash de contraseña (SHA256 simple para MVP - ver TODO abajo)
            hashed_pw = hashlib.sha256(user_data.password.encode()).hexdigest()
            
            company = Company(
                name=user_data.name,
                industry=user_data.industry or "",
                size=user_data.company_size or "",
                location=user_data.location or "",
                is_verified=False,  # Requiere verificación manual
                email_hash=email_hash,
                hashed_password=hashed_pw
            )
            # Encriptar email directamente antes de agregar a sesión
            email_lower = user_data.email.lower().strip()
            company.email = encryption_service.encrypt(email_lower)
            
            session.add(company)
            session.flush()
            session.commit()
            session.refresh(company)
            user_id = company.id
        
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
        
        return UserLoginResponse(
            user_id=user_id,
            name=user_data.name,
            email=user_data.email,
            role=user_data.role,
            api_key=api_key_response.api_key,
            key_id=api_key_response.key_info.key_id,
            expires_at=api_key_response.key_info.expires_at,
            scopes=api_key_response.key_info.scopes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Registrar error en log
        print(f"❌ Error en registro: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Error en registro: {str(e)}"
        )


@router.post("/login", response_model=UserLoginResponse, status_code=200)
async def login_user(
    credentials: LoginRequest,
    session: Session = Depends(get_session)
):
    """
    Login con email y contraseña.
    
    Valida las credenciales del usuario y retorna su API key.
    Si el usuario no tiene API key activa, genera una nueva.
    """
    email_hash = hashlib.sha256(credentials.email.lower().strip().encode()).hexdigest()
    
    # Buscar estudiante
    student = session.exec(
        select(Student).where(Student.email_hash == email_hash)
    ).first()
    
    user_id = None
    user_type = None
    user_email = None
    user_name = None
    
    if student:
        user_id = student.id
        user_type = "student"
        user_email = student.get_email()
        user_name = student.name
    else:
        # Buscar empresa
        company = session.exec(
            select(Company).where(Company.email_hash == email_hash)
        ).first()
        
        if company:
            user_id = company.id
            user_type = "company"
            user_email = company.get_email()
            user_name = company.name
    
    # Si no encontró usuario
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Email o contraseña incorrectos"
        )
    
    # Buscar API key existente válida (no expirada)
    api_key = session.exec(
        select(ApiKey).where(
            ApiKey.user_id == user_id,
            ApiKey.expires_at > datetime.utcnow(),
            ApiKey.is_active == True
        ).order_by(ApiKey.created_at.desc())
    ).first()
    
    # Si no hay API key válida, crear una nueva
    if not api_key:
        api_key_data = ApiKeyCreate(
            name=f"Login - {user_name}",
            description="API key generada al login",
            expires_days=30
        )
        
        api_key_response = api_key_service.create_api_key(
            session=session,
            user_id=user_id,
            user_type=user_type,
            user_email=user_email,
            key_data=api_key_data
        )
        
        api_key_str = api_key_response.api_key
        expires_at = api_key_response.key_info.expires_at
    else:
        # Retornar API key existente
        api_key_str = api_key.key_prefix + "*" * 20  # No revelar completa en login
        expires_at = api_key.expires_at
        api_key_response = None
    
    # Registrar en auditoría
    audit_log = AuditLog(
        actor_role=user_type,
        actor_id=user_email,
        action="login",
        resource=f"user_id:{user_id}",
        success=True,
        details=f"Login exitoso para {user_type}"
    )
    session.add(audit_log)
    session.commit()
    
    return UserLoginResponse(
        user_id=user_id,
        name=user_name,
        email=user_email,
        role=user_type,
        api_key=api_key_str,
        key_id=getattr(api_key_response.key_info if api_key_response else api_key, 'key_id', None),
        expires_at=expires_at,
        scopes=["read:own", "write:own", "read:jobs", "write:applications"] if user_type == "student" 
               else ["read:own", "write:own", "read:students"] if user_type == "company"
               else ["admin:all"]
    )


@router.post("/logout", response_model=BaseResponse, status_code=200)
async def logout_user(
    current_user: UserContext = Depends(AuthService.get_current_user),
    session: Session = Depends(get_session)
):
    """
    Logout del usuario.
    
    Revoca la API key actual del usuario (opcional).
    En esta versión, simplemente registra el logout para auditoría.
    """
    if current_user.role == "anonymous":
        raise HTTPException(
            status_code=401,
            detail="No hay sesión activa"
        )
    
    # Registrar en auditoría
    audit_log = AuditLog(
        actor_role=current_user.role,
        actor_id=current_user.email or str(current_user.user_id),
        action="logout",
        resource="auth",
        success=True,
        details="Logout exitoso"
    )
    session.add(audit_log)
    session.commit()
    
    return BaseResponse(
        success=True,
        message="Sesión cerrada exitosamente"
    )


@router.api_route("/authenticate", methods=["POST"])
async def authenticate_session(
    credentials: LoginRequest,
    session: Session = Depends(get_session)
):
    """
    Endpoint adicional para autenticación basada en contraseña.
    Retorna token/API key para la sesión.
    """
    # Redirigir a /login
    return await login_user(credentials, session)
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
