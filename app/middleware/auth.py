"""
Middleware de autenticación y seguridad para MoirAI
Implementa autenticación basada en API keys dinámicas y auditoría
"""
from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException, Header, Request, Depends
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from app.models import AuditLog
from app.schemas import UserContext
from app.services.api_key_service import api_key_service


class Role:
    """Constantes de roles de usuario"""
    STUDENT = "student"
    COMPANY = "company"
    ADMIN = "admin"
    ANONYMOUS = "anonymous"


class AuthService:
    """Servicio de autenticación y autorización"""
    
    @staticmethod
    def get_current_user(
        request: Request,
        x_api_key: Optional[str] = Header(default=None),
        session: Session = Depends(get_session)
    ) -> UserContext:
        """Obtener usuario actual basado en API key dinámica"""
        
        # Usuario anónimo si no hay API key
        if not x_api_key:
            return UserContext(
                role=Role.ANONYMOUS,
                user_id=None,
                email=None,
                permissions=[]
            )
        
        # Verificar API key dinámica primero
        key_info = api_key_service.validate_api_key(session, x_api_key)
        
        if key_info:
            # API key válida - crear contexto de usuario
            user_context = UserContext(
                role=key_info["user_type"],
                user_id=key_info["user_id"],
                email=key_info["user_email"],
                permissions=key_info["scopes"]
            )
        else:
            # Fallback a API keys estáticas (para compatibilidad)
            user_context = AuthService._check_static_api_keys(x_api_key)
        
        # Registrar actividad en log de auditoría
        AuthService._log_activity(
            session=session,
            actor_role=user_context.role,
            actor_id=user_context.email or str(user_context.user_id),
            actor_ip=AuthService._get_client_ip(request),
            action="api_access",
            resource=str(request.url.path),
            success=True,
            details=f"API key: {x_api_key[:10]}..." if x_api_key else None
        )
        
        return user_context
    
    @staticmethod
    def _check_static_api_keys(x_api_key: str) -> UserContext:
        """Fallback para API keys estáticas (compatibilidad)"""
        
        if x_api_key in settings.ADMIN_API_KEYS:
            return UserContext(
                role=Role.ADMIN,
                user_id=None,
                email=None,
                permissions=["read:all", "write:all", "admin:all"]
            )
        elif x_api_key in settings.COMPANY_API_KEYS:
            return UserContext(
                role=Role.COMPANY,
                user_id=None,
                email=None,
                permissions=["read:students", "read:jobs", "write:jobs"]
            )
        elif x_api_key in settings.STUDENT_API_KEYS:
            return UserContext(
                role=Role.STUDENT,
                user_id=None,
                email=None,
                permissions=["read:own", "write:own", "read:jobs"]
            )
        else:
            # API key inválida
            return UserContext(
                role=Role.ANONYMOUS,
                user_id=None,
                email=None,
                permissions=[]
            )
    
    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Obtener IP del cliente desde la request"""
        # Verificar headers de proxy primero
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback a IP del cliente directo
        return request.client.host if request.client else "unknown"
    
    @staticmethod
    def _log_activity(
        session: Session,
        actor_role: str,
        actor_id: Optional[str],
        actor_ip: str,
        action: str,
        resource: Optional[str],
        success: bool,
        details: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Registrar actividad en log de auditoría"""
        if not settings.ENABLE_AUDIT_LOGGING:
            return
        
        audit_log = AuditLog(
            actor_role=actor_role,
            actor_id=actor_id,
            actor_ip=actor_ip,
            action=action,
            resource=resource,
            details=details,
            success=success,
            error_message=error_message
        )
        
        session.add(audit_log)
        session.commit()


class PermissionChecker:
    """Verificador de permisos basado en roles"""
    
    @staticmethod
    def require_role(required_roles: List[str]):
        """Decorator para requerir roles específicos"""
        def decorator(user: UserContext = Depends(AuthService.get_current_user)):
            if user.role not in required_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Acceso denegado. Roles requeridos: {required_roles}. Su rol: {user.role}"
                )
            return user
        return decorator
    
    @staticmethod
    def require_permission(required_permissions: List[str]):
        """Decorator para requerir permisos específicos"""
        def decorator(user: UserContext = Depends(AuthService.get_current_user)):
            if not any(perm in user.permissions for perm in required_permissions):
                raise HTTPException(
                    status_code=403,
                    detail=f"Permisos insuficientes. Requeridos: {required_permissions}"
                )
            return user
        return decorator
    
    @staticmethod
    def student_or_admin():
        """Requiere rol de estudiante o administrador"""
        return PermissionChecker.require_role([Role.STUDENT, Role.ADMIN])
    
    @staticmethod
    def company_or_admin():
        """Requiere rol de empresa o administrador"""
        return PermissionChecker.require_role([Role.COMPANY, Role.ADMIN])
    
    @staticmethod
    def admin_only():
        """Requiere rol de administrador únicamente"""
        return PermissionChecker.require_role([Role.ADMIN])
    
    @staticmethod
    def authenticated():
        """Requiere usuario autenticado (no anónimo)"""
        def decorator(user: UserContext = Depends(AuthService.get_current_user)):
            if user.role == Role.ANONYMOUS:
                raise HTTPException(
                    status_code=401,
                    detail="Autenticación requerida. Proporcione X-API-Key header."
                )
            return user
        return decorator


class SecurityMiddleware:
    """Middleware de seguridad adicional"""
    
    @staticmethod
    def validate_file_upload(file_content: bytes, filename: str) -> bool:
        """Validar archivo subido por seguridad"""
        # Verificar tamaño
        if len(file_content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Archivo demasiado grande. Máximo: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        # Verificar extensión
        file_ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
        if file_ext not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de archivo no permitido. Permitidos: {settings.ALLOWED_FILE_TYPES}"
            )
        
        # Verificaciones básicas de contenido
        # TODO: Implementar escáner de malware en producción
        
        return True
    
    @staticmethod
    def sanitize_text_input(text: str, max_length: int = 10000) -> str:
        """Sanitizar entrada de texto"""
        if not text:
            return ""
        
        # Limitar longitud
        text = text[:max_length]
        
        # Remover caracteres de control peligrosos
        import re
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # TODO: Implementar más validaciones según necesidades
        
        return text.strip()


# Instancias de servicios
auth_service = AuthService()
permission_checker = PermissionChecker()
security_middleware = SecurityMiddleware()


# Funciones de conveniencia para usar en endpoints
def get_current_user(
    request: Request,
    x_api_key: Optional[str] = Header(default=None),
    session: Session = Depends(get_session)
) -> UserContext:
    """Función de conveniencia para obtener usuario actual"""
    return auth_service.get_current_user(request, x_api_key, session)


# Aliases para compatibilidad con código existente
require_student_or_admin = permission_checker.student_or_admin
require_company_or_admin = permission_checker.company_or_admin
require_admin = permission_checker.admin_only
require_authenticated = permission_checker.authenticated
