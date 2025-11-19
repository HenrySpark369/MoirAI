"""
Endpoints para autenticación y gestión de usuarios
Incluye registro, login y gestión de API keys
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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
    session: AsyncSession = Depends(get_session)
):
    """
    Registrar nuevo usuario y generar API key automáticamente (ASYNC version)
    
    Valida los datos, crea el perfil según el rol y genera una API key personal.
    Lógica unificada para estudiantes y empresas.
    """
    import secrets
    try:
        # Validar rol
        if user_data.role not in ["student", "company"]:
            raise HTTPException(
                status_code=400,
                detail="El rol debe ser 'student' o 'company'"
            )
        
        # ✅ ASYNC: Verificar si el email ya existe
        email_hash = hashlib.sha256(user_data.email.lower().strip().encode()).hexdigest()
        
        result = await session.execute(
            select(Student).where(Student.email_hash == email_hash)
        )
        if result.scalars().first():
            raise HTTPException(status_code=409, detail="Email ya registrado en estudiantes")
        
        result = await session.execute(
            select(Company).where(Company.email_hash == email_hash)
        )
        if result.scalars().first():
            raise HTTPException(status_code=409, detail="Email ya registrado en empresas")
        
        # ✅ ASYNC: Crear usuario
        password_hash = hashlib.sha256(user_data.password.encode()).hexdigest()
        
        if user_data.role == "student":
            user = Student(
                name=user_data.name,
                email=user_data.email,  # Se encripta en el setter
                email_hash=email_hash,
                hashed_password=password_hash,
                program=getattr(user_data, "program", None),
                is_active=True
            )
        else:  # company
            user = Company(
                name=user_data.name,
                email=user_data.email,  # Se encripta en el setter
                email_hash=email_hash,
                hashed_password=password_hash,
                industry=getattr(user_data, "industry", None),
                company_size=getattr(user_data, "company_size", None),
                location=getattr(user_data, "location", None),
                is_active=True
            )
        
        session.add(user)
        await session.flush()  # Get user.id without committing
        
        # ✅ ASYNC: Crear API key para el usuario
        import secrets
        
        # Generar componentes de la clave
        key_id = secrets.token_urlsafe(16)
        secret_part = secrets.token_urlsafe(32)
        full_key = f"{key_id}_{secret_part}"
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()
        
        # Determinar prefijo según tipo de usuario
        prefix_map = {"student": "stu_", "company": "com_", "admin": "adm_"}
        prefix = prefix_map.get(user_data.role, "key_")
        key_prefix = f"{prefix}{key_id[:8]}"
        
        # Crear registro de API key
        api_key_record = ApiKey(
            key_id=key_id,
            key_hash=key_hash,
            key_prefix=key_prefix,
            user_id=user.id,
            user_type=user_data.role,
            user_email=user_data.email,
            name=f"Registration API Key - {user_data.name}",
            scopes=json.dumps(["read", "write"]),
            is_active=True,
            expires_at=datetime.utcnow().replace(year=datetime.utcnow().year + 1)
        )
        session.add(api_key_record)
        await session.commit()
        await session.refresh(api_key_record)
        
        return UserLoginResponse(
            user_id=user.id,
            name=user_data.name,
            email=user_data.email,
            role=user_data.role,
            api_key=full_key,
            key_id=api_key_record.key_id,
            expires_at=api_key_record.expires_at,
            scopes=json.loads(api_key_record.scopes) if api_key_record.scopes else []
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en registro: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Registrar error en auditoría
        await auth_service.log_audit(
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
    session: AsyncSession = Depends(get_session)
):
    """
    Login con email y contraseña (ASYNC version).
    
    Valida las credenciales del usuario y retorna su API key principal.
    Lógica unificada para estudiantes y empresas (evita duplicación y conflictos).
    """
    try:
        # ✅ ASYNC: Buscar usuario en tabla de estudiantes
        email_hash = hashlib.sha256(credentials.email.lower().strip().encode()).hexdigest()
        result = await session.execute(
            select(Student).where(Student.email_hash == email_hash)
        )
        user = result.scalars().first()
        user_type = "student"
        
        # Si no es estudiante, buscar en empresas
        if not user:
            result = await session.execute(
                select(Company).where(Company.email_hash == email_hash)
            )
            user = result.scalars().first()
            user_type = "company"
        
        # Si no encontró usuario
        if not user or not user_type:
            raise HTTPException(
                status_code=401,
                detail="Email o contraseña incorrectos"
            )
        
        # ✅ Validar contraseña
        password_hash = hashlib.sha256(credentials.password.encode()).hexdigest()
        if password_hash != user.hashed_password:
            raise HTTPException(
                status_code=401,
                detail="Email o contraseña incorrectos"
            )
        
        # ✅ SOLUCIÓN DEFINITIVA: Generar NUEVA API key en cada login
        # Esto garantiza que siempre hay una clave disponible para retornar
        # Las claves antiguas siguen siendo válidas (no se revocan)
        import secrets
        
        try:
            # Generar componentes de la clave
            key_id = secrets.token_urlsafe(16)
            secret_part = secrets.token_urlsafe(32)
            full_key = f"{key_id}_{secret_part}"
            key_hash = hashlib.sha256(full_key.encode()).hexdigest()
            
            # Determinar prefijo según tipo de usuario
            prefix_map = {"student": "stu_", "company": "com_", "admin": "adm_"}
            prefix = prefix_map.get(user_type, "key_")
            key_prefix = f"{prefix}{key_id[:8]}"
            
            # Crear registro de API key
            api_key_record = ApiKey(
                key_id=key_id,
                key_hash=key_hash,
                key_prefix=key_prefix,
                user_id=user.id,
                user_type=user_type,
                user_email=credentials.email,
                name=f"Sesión - {user.name} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                description="API key generada en login",
                scopes=json.dumps(["read", "write"]),
                is_active=True,
                expires_at=datetime.utcnow().replace(year=datetime.utcnow().year + 1)
            )
            session.add(api_key_record)
            await session.commit()
            await session.refresh(api_key_record)
            
            # Retornar la clave completa
            api_key_to_return = full_key
            
        except Exception as e:
            print(f"⚠️ Error generando clave en login: {e}")
            # Fallback: buscar una clave existente
            result = await session.execute(
                select(ApiKey).where(
                    (ApiKey.user_id == user.id) & (ApiKey.user_type == user_type)
                ).order_by(ApiKey.created_at.desc())
            )
            api_key_record = result.scalars().first()
            
            if not api_key_record:
                raise HTTPException(
                    status_code=500,
                    detail="No se pudo generar clave de API"
                )
            
            api_key_to_return = ""  # No retornar clave antigua
        
        # Retornar confirmación de login con API key
        return UserLoginResponse(
            user_id=user.id,
            name=user.name,
            email=credentials.email,
            role=user_type,
            api_key=api_key_to_return,
            key_id=api_key_record.key_id,
            expires_at=api_key_record.expires_at,
            scopes=json.loads(api_key_record.scopes) if api_key_record.scopes else []
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en login: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Error en login: {str(e)}"
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Error en login: {str(e)}"
        )


@router.post("/logout", response_model=BaseResponse, status_code=200)
async def logout_user(
    current_user: UserContext = Depends(AuthService.get_current_user),
    session: AsyncSession = Depends(get_session)
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
        await auth_service.log_audit(
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
        
        await auth_service.log_audit(
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
    session: AsyncSession = Depends(get_session)
):
    """
    Endpoint adicional para autenticación basada en contraseña.
    Retorna token/API key para la sesión.
    """
    # Redirigir a /login
    return await login_user(credentials, session)


@router.post("/api-keys", response_model=ApiKeyCreatedResponse)
async def create_api_key(
    key_data: ApiKeyCreate,
    session: AsyncSession = Depends(get_session),
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
    result = await session.execute(
        select(ApiKey).where(
            (ApiKey.user_id == current_user.user_id) &
            (ApiKey.user_type == current_user.role) &
            (ApiKey.is_active == True)
        )
    )
    existing_keys = result.scalars().all()
    
    if len(existing_keys) >= 10:  # Máximo 10 claves activas por usuario
        raise HTTPException(
            status_code=400,
            detail="Ha alcanzado el límite máximo de API keys (10)"
        )
    
    api_key_response = await api_key_service.create_api_key(
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
    await session.commit()
    
    return api_key_response


@router.get("/api-keys", response_model=ApiKeysList)
async def list_api_keys(
    session: AsyncSession = Depends(get_session),
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
    
    keys = await api_key_service.get_user_api_keys(
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
    session: AsyncSession = Depends(get_session),
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
    
    success = await api_key_service.revoke_api_key(
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
    await session.commit()
    
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
        "name": getattr(current_user, 'name', None) or current_user.email.split('@')[0],
        "role": current_user.role,
        "permissions": current_user.permissions
    }


@router.post("/cleanup-expired-keys", response_model=BaseResponse)
async def cleanup_expired_keys(
    session: AsyncSession = Depends(get_session),
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
    
    cleaned_count = await api_key_service.cleanup_expired_keys(session)
    
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
    await session.commit()
    
    return BaseResponse(
        success=True,
        message=f"Se desactivaron {cleaned_count} claves expiradas"
    )
