"""
Módulo para inicialización de usuario admin desde configuración.
Se ejecuta al iniciar la aplicación si INIT_DEFAULT_ADMIN=true en .env
"""

import logging
from typing import Optional
from sqlmodel import Session, select

from app.core.config import settings
from app.models import Student
from app.services.auth_service import auth_service
from app.services.api_key_service import api_key_service
from app.schemas import ApiKeyCreate

logger = logging.getLogger(__name__)


def init_default_admin(session: Session) -> Optional[int]:
    """
    Inicializa el usuario admin por defecto desde .env
    
    Se ejecuta SOLO si:
    1. INIT_DEFAULT_ADMIN=true en .env
    2. No existe un admin con el email configurado
    
    Args:
        session: Sesión de base de datos
        
    Returns:
        int: ID del usuario admin creado, o None si no se creó
    """
    
    # Verificar si está habilitada la inicialización de admin
    if not settings.INIT_DEFAULT_ADMIN:
        logger.debug("✓ Inicialización de admin deshabilitada (INIT_DEFAULT_ADMIN=false)")
        return None
    
    # Validar configuración requerida
    if not all([
        settings.ADMIN_DEFAULT_EMAIL,
        settings.ADMIN_DEFAULT_PASSWORD,
        settings.ADMIN_DEFAULT_NAME
    ]):
        logger.warning(
            "⚠️  INIT_DEFAULT_ADMIN=true pero valores en blanco en .env "
            "(ADMIN_DEFAULT_EMAIL, ADMIN_DEFAULT_PASSWORD, ADMIN_DEFAULT_NAME)"
        )
        return None
    
    try:
        # Verificar si el admin ya existe
        existing_user, user_type = auth_service.find_user_by_email(
            session,
            settings.ADMIN_DEFAULT_EMAIL
        )
        
        if existing_user:
            if user_type == "admin":
                logger.info(
                    f"✓ Admin ya existe: {settings.ADMIN_DEFAULT_EMAIL} "
                    "(cambiar INIT_DEFAULT_ADMIN=false en .env para evitar intentos repetidos)"
                )
                return existing_user.id
            else:
                logger.warning(
                    f"⚠️  Email existe pero no es admin: {settings.ADMIN_DEFAULT_EMAIL} "
                    f"(tipo: {user_type}). Skipping..."
                )
                return None
        
        # Crear nuevo admin
        logger.info(f"🔧 Creando usuario admin por defecto: {settings.ADMIN_DEFAULT_NAME}")
        
        user_id, user_type = auth_service.create_user(
            session=session,
            name=settings.ADMIN_DEFAULT_NAME,
            email=settings.ADMIN_DEFAULT_EMAIL,
            password=settings.ADMIN_DEFAULT_PASSWORD,
            role="admin"
        )
        
        # Crear API key para el admin
        api_key_data = ApiKeyCreate(
            name="Clave principal - Admin Sistema",
            description="API key generada automáticamente al iniciar",
            expires_days=365
        )
        
        api_key_response = api_key_service.create_api_key(
            session=session,
            user_id=user_id,
            user_type=user_type,
            user_email=settings.ADMIN_DEFAULT_EMAIL,
            key_data=api_key_data
        )
        
        logger.info(
            f"✅ Admin creado exitosamente:\n"
            f"   Email: {settings.ADMIN_DEFAULT_EMAIL}\n"
            f"   API Key prefix: {api_key_response.key_info.key_prefix}\n"
            f"   ⚠️  CAMBIAR CONTRASEÑA EN PRODUCCIÓN"
        )
        
        return user_id
        
    except Exception as e:
        logger.error(
            f"❌ Error inicializando admin por defecto: {type(e).__name__}: {str(e)}"
        )
        import traceback
        traceback.print_exc()
        return None


def verify_admin_access_configured() -> bool:
    """
    Verifica que haya al menos una forma de acceder como admin
    
    Returns:
        bool: True si hay acceso admin disponible
    """
    # Opción 1: Admin por defecto en .env
    if settings.INIT_DEFAULT_ADMIN and settings.ADMIN_DEFAULT_EMAIL:
        return True
    
    # Opción 2: API keys de admin configuradas
    if settings.ADMIN_API_KEYS and len(settings.ADMIN_API_KEYS) > 0:
        return True
    
    logger.warning(
        "⚠️  NO HAY ACCESO ADMIN CONFIGURADO:\n"
        "   • INIT_DEFAULT_ADMIN=false en .env\n"
        "   • No hay ADMIN_API_KEYS configuradas\n"
        "   Use: INIT_DEFAULT_ADMIN=true y configure ADMIN_DEFAULT_* en .env"
    )
    return False
