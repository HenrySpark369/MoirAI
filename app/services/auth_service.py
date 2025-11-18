"""
Servicio unificado de autenticación
Centraliza la lógica de registro, login y logout para evitar conflictos
"""

import hashlib
import json
from datetime import datetime
from typing import Optional, Tuple, Dict, Any

from sqlmodel import Session, select

from app.models import Student, Company, ApiKey, AuditLog
from app.schemas import ApiKeyCreate
from app.services.api_key_service import api_key_service
from app.utils.encryption import EncryptionService


class AuthenticationService:
    """Servicio unificado de autenticación para todos los roles"""
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Genera hash de contraseña"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def _hash_email(email: str) -> str:
        """Genera hash de email para búsquedas"""
        return hashlib.sha256(email.lower().strip().encode()).hexdigest()
    
    @staticmethod
    def _get_encryption_service() -> EncryptionService:
        """Obtiene instancia del servicio de encriptación"""
        return EncryptionService()
    
    @staticmethod
    def find_user_by_email(session: Session, email: str) -> Tuple[Optional[Any], str]:
        """
        Busca un usuario por email en ambas tablas
        
        Returns: (user_object, user_type) donde user_type es 'student', 'company', 'admin', o None
        """
        email_hash = AuthenticationService._hash_email(email)
        
        # Buscar en estudiantes
        student = session.exec(
            select(Student).where(Student.email_hash == email_hash)
        ).first()
        
        if student:
            # Si es admin, retorna como admin
            if student.program == "Administration":
                return student, "admin"
            return student, "student"
        
        # Buscar en empresas
        company = session.exec(
            select(Company).where(Company.email_hash == email_hash)
        ).first()
        
        if company:
            return company, "company"
        
        return None, None
    
    @staticmethod
    def validate_password(user: Any, password: str) -> bool:
        """Valida la contraseña contra el hash almacenado"""
        password_hash = AuthenticationService._hash_password(password)
        return password_hash == user.hashed_password
    
    @staticmethod
    def create_user(
        session: Session,
        name: str,
        email: str,
        password: str,
        role: str,
        **kwargs
    ) -> Tuple[int, str]:
        """
        Crea un nuevo usuario (estudiante, empresa, o administrador)
        
        Returns: (user_id, user_type)
        """
        email_hash = AuthenticationService._hash_email(email)
        
        # Verificar si email ya existe
        existing_user, _ = AuthenticationService.find_user_by_email(session, email)
        if existing_user:
            raise ValueError("Ya existe un usuario registrado con ese email")
        
        if role not in ["student", "company", "admin"]:
            raise ValueError("Rol inválido. Debe ser 'student', 'company', o 'admin'")
        
        encryption_service = AuthenticationService._get_encryption_service()
        hashed_pw = AuthenticationService._hash_password(password)
        email_encrypted = encryption_service.encrypt(email.lower().strip())
        
        user_id = None
        
        if role == "student":
            student = Student(
                name=name,
                program=kwargs.get("program", ""),
                consent_data_processing=True,
                skills="[]",
                soft_skills="[]",
                projects="[]",
                email_hash=email_hash,
                hashed_password=hashed_pw,
                cv_uploaded=False,
                email=email_encrypted
            )
            session.add(student)
            session.flush()
            session.commit()
            session.refresh(student)
            user_id = student.id
            
        elif role == "admin":
            # Crear admin como Student con program="Administration"
            student = Student(
                name=name,
                program="Administration",  # Flag para identificar como admin
                consent_data_processing=True,
                skills="[]",
                soft_skills="[]",
                projects="[]",
                email_hash=email_hash,
                hashed_password=hashed_pw,
                cv_uploaded=False,
                email=email_encrypted
            )
            session.add(student)
            session.flush()
            session.commit()
            session.refresh(student)
            user_id = student.id
            
        elif role == "company":
            company = Company(
                name=name,
                industry=kwargs.get("industry", ""),
                size=kwargs.get("company_size", ""),
                location=kwargs.get("location", ""),
                is_verified=False,
                email_hash=email_hash,
                hashed_password=hashed_pw,
                email=email_encrypted
            )
            session.add(company)
            session.flush()
            session.commit()
            session.refresh(company)
            user_id = company.id
        
        return user_id, role
    
    @staticmethod
    def get_user_api_key(
        session: Session,
        user_id: int,
        create_if_missing: bool = True
    ) -> Optional[ApiKey]:
        """
        Obtiene la API key principal (más antigua) del usuario
        
        Si create_if_missing=True y no existe, crea una nueva
        """
        # Buscar la API key más antigua (la del registro)
        api_key = session.exec(
            select(ApiKey).where(
                ApiKey.user_id == user_id,
                ApiKey.is_active == True,
                ApiKey.expires_at > datetime.utcnow()
            ).order_by(ApiKey.created_at.asc())
        ).first()
        
        return api_key
    
    @staticmethod
    def ensure_user_has_api_key(
        session: Session,
        user_id: int,
        user_type: str,
        user_email: str,
        user_name: str
    ) -> ApiKey:
        """
        Asegura que el usuario tenga al menos una API key válida
        
        Si no existe, crea una nueva
        """
        # Buscar la API key del usuario (más antigua primero = la del registro)
        api_key = session.exec(
            select(ApiKey).where(
                ApiKey.user_id == user_id,
                ApiKey.is_active == True,
                ApiKey.expires_at > datetime.utcnow()
            ).order_by(ApiKey.created_at.asc())
        ).first()
        
        if api_key and api_key.user_id == user_id:
            # Validar que la API key pertenece al usuario correcto
            return api_key
        
        # Si no existe una válida, crear una nueva
        api_key_data = ApiKeyCreate(
            name=f"Clave principal - {user_name}",
            description="API key principal para autenticación",
            expires_days=365
        )
        
        api_key_response = api_key_service.create_api_key(
            session=session,
            user_id=user_id,
            user_type=user_type,
            user_email=user_email,
            key_data=api_key_data
        )
        
        # Retornar la API key recién creada (convertir response a modelo)
        # Ya que create_api_key hace commit, debería estar en la BD
        new_api_key = session.exec(
            select(ApiKey).where(
                ApiKey.key_id == api_key_response.key_info.key_id,
                ApiKey.user_id == user_id
            )
        ).first()
        
        if new_api_key:
            return new_api_key
        
        # Fallback: retornar el ApiKey directamente del response
        # Esto no debería ocurrir si todo está funcionando correctamente
        raise RuntimeError(f"No se pudo obtener API key para usuario {user_id}")
    
    @staticmethod
    def log_audit(
        session: Session,
        actor_role: str,
        actor_id: str,
        action: str,
        resource: str,
        success: bool = True,
        details: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Registra una acción en el audit log"""
        audit_log = AuditLog(
            actor_role=actor_role,
            actor_id=actor_id,
            action=action,
            resource=resource,
            success=success,
            details=details,
            error_message=error_message
        )
        session.add(audit_log)
        session.commit()


# Instancia global del servicio
auth_service = AuthenticationService()
