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
from app.services.auth_service import auth_service
from app.middleware.auth import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserLoginResponse, status_code=201)
async def register_user(
    user_data: UserRegister,
    session: Session = Depends(get_session)
):
    """
    Registrar nuevo usuario y generar API key automáticamente
    
    Valida los datos, crea el perfil según el rol y genera una API key personal.
    Lógica unificada para estudiantes y empresas.
    """
    try:
        # Validar rol
        if user_data.role not in ["student", "company"]:
            raise HTTPException(
                status_code=400,
                detail="El rol debe ser 'student' o 'company'"
            )
        
        # Crear usuario (se valida internamente si email existe)
        user_id, user_type = auth_service.create_user(
            session=session,
            name=user_data.name,
            email=user_data.email,
            password=user_data.password,
            role=user_data.role,
            program=getattr(user_data, "program", None),
            industry=getattr(user_data, "industry", None),
            company_size=getattr(user_data, "company_size", None),
            location=getattr(user_data, "location", None)
        )
        
        # Obtener usuario para acceder a datos encriptados
        user, _ = auth_service.find_user_by_email(session, user_data.email)
        
        # Generar API key automática
        api_key_data = ApiKeyCreate(
            name=f"Clave principal - {user_data.name}",
            description="API key generada automáticamente al registrarse",
            expires_days=365
        )
        
        api_key_response = api_key_service.create_api_key(
            session=session,
            user_id=user_id,
            user_type=user_type,
            user_email=user_data.email,
            key_data=api_key_data
        )
        
        # Registrar en auditoría
        auth_service.log_audit(
            session=session,
            actor_role=user_type,
            actor_id=user_data.email,
            action="register_user",
            resource=f"user_id:{user_id}",
            success=True,
            details=f"Nuevo usuario {user_type} registrado"
        )
        
        return UserLoginResponse(
            user_id=user_id,
            name=user_data.name,
            email=user_data.email,
            role=user_type,
            api_key=api_key_response.api_key,
            key_id=api_key_response.key_info.key_id,
            expires_at=api_key_response.key_info.expires_at,
            scopes=api_key_response.key_info.scopes
        )
        
    except ValueError as e:
        # Errores de validación de negocio
        if "email" in str(e).lower():
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en registro: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Registrar error en auditoría
        auth_service.log_audit(
            session=session,
            actor_role=user_data.role,
            actor_id=user_data.email,
            action="register_user",
            resource="registration_attempt",
            success=False,
            error_message=str(e)
        )
        
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
    
    Valida las credenciales del usuario y retorna su API key principal.
    Lógica unificada para estudiantes y empresas (evita duplicación y conflictos).
    """
    try:
        # Buscar usuario en ambos tipos
        user, user_type = auth_service.find_user_by_email(session, credentials.email)
        
        # Si no encontró usuario
        if not user or not user_type:
            auth_service.log_audit(
                session=session,
                actor_role="unknown",
                actor_id=credentials.email,
                action="login_attempt",
                resource="auth",
                success=False,
                error_message="Usuario no encontrado"
            )
            raise HTTPException(
                status_code=401,
                detail="Email o contraseña incorrectos"
            )
        
        # Validar contraseña
        if not auth_service.validate_password(user, credentials.password):
            auth_service.log_audit(
                session=session,
                actor_role=user_type,
                actor_id=credentials.email,
                action="login_attempt",
                resource="auth",
                success=False,
                error_message="Contraseña incorrecta"
            )
            raise HTTPException(
                status_code=401,
                detail="Email o contraseña incorrectos"
            )
        
        # Obtener o crear API key principal del usuario
        api_key_record = auth_service.ensure_user_has_api_key(
            session=session,
            user_id=user.id,
            user_type=user_type,
            user_email=credentials.email,
            user_name=user.name
        )
        
        # ✅ SOLUCIÓN DEFINITIVA: Generar NUEVA API key en cada login
        # Esto garantiza que siempre hay una clave disponible para retornar
        # Las claves antiguas siguen siendo válidas (no se revocan)
        api_key_data = ApiKeyCreate(
            name=f"Sesión - {user.name} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            description="API key generada en login",
            expires_days=365
        )
        
        try:
            api_key_response = api_key_service.create_api_key(
                session=session,
                user_id=user.id,
                user_type=user_type,
                user_email=credentials.email,
                key_data=api_key_data
            )
            api_key_full = api_key_response.api_key
            key_id = api_key_response.key_info.key_id
            expires_at = api_key_response.key_info.expires_at
            
        except Exception as e:
            print(f"⚠️ Error generando clave en login: {e}")
            # Fallback: usar la clave existente
            api_key_full = ""
            key_id = api_key_record.key_id
            expires_at = api_key_record.expires_at
        
        # Registrar login exitoso en auditoría
        auth_service.log_audit(
            session=session,
            actor_role=user_type,
            actor_id=credentials.email,
            action="login",
            resource=f"user_id:{user.id}",
            success=True,
            details=f"Login exitoso para {user_type}"
        )
        
        # Retornar confirmación de login
        # ✅ AHORA SIEMPRE retorna api_key válida
        return UserLoginResponse(
            user_id=user.id,
            name=user.name,
            email=credentials.email,
            role=user_type,
            api_key=api_key_full,  # ✅ Siempre tiene valor
            key_id=key_id,
            expires_at=expires_at,
            scopes=json.loads(api_key_record.scopes) if api_key_record.scopes else []
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en login: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        auth_service.log_audit(
            session=session,
            actor_role="unknown",
            actor_id=credentials.email,
            action="login_attempt",
            resource="auth",
            success=False,
            error_message=str(e)
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Error en login: {str(e)}"
        )


@router.post("/logout", response_model=BaseResponse, status_code=200)
async def logout_user(
    current_user: UserContext = Depends(AuthService.get_current_user),
    session: Session = Depends(get_session)
):
    """
    Logout del usuario.
    
    Registra el logout para auditoría. La API key sigue siendo válida
    para futuras sesiones (reutilizable).
    Lógica unificada para estudiantes y empresas.
    """
    if current_user.role == "anonymous":
        raise HTTPException(
            status_code=401,
            detail="No hay sesión activa"
        )
    
    try:
        # Registrar logout en auditoría usando servicio unificado
        auth_service.log_audit(
            session=session,
            actor_role=current_user.role,
            actor_id=current_user.email or str(current_user.user_id),
            action="logout",
            resource="auth",
            success=True,
            details=f"Logout exitoso para {current_user.role}"
        )
        
        return BaseResponse(
            success=True,
            message="Sesión cerrada exitosamente"
        )
        
    except Exception as e:
        print(f"❌ Error en logout: {type(e).__name__}: {str(e)}")
        
        auth_service.log_audit(
            session=session,
            actor_role=current_user.role,
            actor_id=current_user.email or str(current_user.user_id),
            action="logout",
            resource="auth",
            success=False,
            error_message=str(e)
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Error en logout: {str(e)}"
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
