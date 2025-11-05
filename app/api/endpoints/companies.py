"""
Endpoints para gestión de empresas colaboradoras - CRUD completo
Incluye operaciones para crear, leer, actualizar y eliminar empresas
considerando acceso seguro a datos de estudiantes y verificación
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
import json
from datetime import datetime

from app.core.database import get_session
from app.models import Company, Student, AuditLog
from app.schemas import (
    CompanyBase, CompanyCreate, CompanyProfile, UserContext, BaseResponse,
    StudentPublic
)
from app.middleware.auth import AuthService
from app.core.config import settings

router = APIRouter(prefix="/companies", tags=["companies"])

# Constantes
VALID_SIZES = {"startup", "pequeña", "mediana", "grande"}


def _log_audit_action(session: Session, action: str, resource: str, 
                     actor: UserContext, success: bool = True, 
                     details: str = None, error_message: str = None):
    """Helper para registrar acciones de auditoría"""
    audit_log = AuditLog(
        actor_role=actor.role,
        actor_id=str(actor.user_id) if actor.user_id else actor.email,
        action=action,
        resource=resource,
        success=success,
        details=details,
        error_message=error_message
    )
    session.add(audit_log)


def _convert_to_company_profile(company: Company) -> CompanyProfile:
    """Convierte modelo Company a CompanyProfile"""
    return CompanyProfile(
        id=company.id,
        name=company.name,
        email=company.email,
        industry=company.industry,
        size=company.size,
        location=company.location,
        is_verified=company.is_verified,
        is_active=company.is_active,
        created_at=company.created_at
    )


# ============================================================================
# CREATE - Crear Empresa
# ============================================================================

@router.post("/", response_model=CompanyProfile, status_code=201)
async def create_company(
    company_data: CompanyCreate,
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Crear nueva empresa colaboradora.
    
    Campos requeridos:
    - name: Nombre de la empresa (1-100 caracteres)
    - email: Email corporativo (único)
    
    Campos opcionales:
    - industry: Sector industrial (max 50 caracteres)
    - size: Tamaño (startup, pequeña, mediana, grande)
    - location: Ubicación (max 100 caracteres)
    
    La empresa se crea con is_verified=False y requiere validación de admin.
    """
    # Verificar permisos: solo admin y empresas sin autenticación
    if current_user.role not in ["admin", "anonymous"] and current_user.role != "company":
        raise HTTPException(
            status_code=403,
            detail="Solo administradores y empresas pueden crear perfiles"
        )
    
    # Validar tamaño si se proporciona
    if company_data.size and company_data.size not in VALID_SIZES:
        raise HTTPException(
            status_code=400,
            detail=f"Size debe ser uno de: {', '.join(VALID_SIZES)}"
        )
    
    # Verificar email único
    existing = session.exec(
        select(Company).where(Company.email == company_data.email)
    ).first()
    
    if existing:
        _log_audit_action(
            session, "CREATE_COMPANY", f"email:{company_data.email}",
            current_user, success=False, error_message="Email duplicado"
        )
        raise HTTPException(
            status_code=409,
            detail="Ya existe una empresa registrada con ese email"
        )
    
    # Crear empresa
    company = Company(
        name=company_data.name,
        email=company_data.email,
        industry=company_data.industry,
        size=company_data.size,
        location=company_data.location,
        is_verified=False,  # Requiere verificación de admin
        is_active=True
    )
    
    try:
        session.add(company)
        session.commit()
        session.refresh(company)
        
        _log_audit_action(
            session, "CREATE_COMPANY", f"company_id:{company.id}",
            current_user, details=f"Empresa {company.name} creada (email: {company.email})"
        )
        
        return _convert_to_company_profile(company)
        
    except Exception as e:
        session.rollback()
        _log_audit_action(
            session, "CREATE_COMPANY", f"email:{company_data.email}",
            current_user, success=False, error_message=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error creando empresa: {str(e)}"
        )


# ============================================================================
# READ - Listar Empresas
# ============================================================================

@router.get("/", response_model=dict)
async def list_companies(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Límite de resultados"),
    industry: Optional[str] = Query(None, description="Filtrar por sector"),
    size: Optional[str] = Query(None, description="Filtrar por tamaño"),
    location: Optional[str] = Query(None, description="Filtrar por ubicación"),
    is_verified: Optional[bool] = Query(None, description="Filtrar por verificación"),
    sort_by: str = Query("name", description="Ordenar por: name, created_at"),
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Listar empresas con filtros y paginación.
    
    Control de acceso:
    - Admin: ve todas las empresas (activas + inactivas)
    - Company: solo empresas verificadas y activas
    - Student: solo empresas verificadas y activas
    - Anonymous: no tiene acceso
    """
    # Control de acceso: solo usuarios autenticados
    if current_user.role == "anonymous":
        raise HTTPException(
            status_code=401,
            detail="Debe estar autenticado para listar empresas"
        )
    
    # Construir query base según rol
    query = select(Company)
    
    if current_user.role != "admin":
        # No-admins solo ven empresas verificadas y activas
        query = query.where(
            Company.is_verified == True,
            Company.is_active == True
        )
    
    # Aplicar filtros
    if industry:
        query = query.where(Company.industry == industry)
    
    if size:
        if size not in VALID_SIZES:
            raise HTTPException(
                status_code=400,
                detail=f"Size debe ser uno de: {', '.join(VALID_SIZES)}"
            )
        query = query.where(Company.size == size)
    
    if location:
        query = query.where(Company.location.ilike(f"%{location}%"))
    
    if is_verified is not None:
        query = query.where(Company.is_verified == is_verified)
    
    # Ordenamiento
    if sort_by == "created_at":
        query = query.order_by(Company.created_at.desc())
    else:  # default: name
        query = query.order_by(Company.name)
    
    # Obtener total
    total = session.exec(select(func.count(Company.id)).select_from(Company)).one()
    
    # Aplicar paginación
    companies = session.exec(query.offset(skip).limit(limit)).all()
    
    # Convertir a perfiles
    data = [_convert_to_company_profile(c) for c in companies]
    
    _log_audit_action(
        session, "LIST_COMPANIES", "companies",
        current_user, details=f"Listar empresas (skip={skip}, limit={limit})"
    )
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": data
    }


# ============================================================================
# READ - Obtener Empresa Específica
# ============================================================================

@router.get("/{company_id}", response_model=CompanyProfile)
async def get_company(
    company_id: int,
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Obtener detalles de una empresa específica.
    
    Control de acceso:
    - Admin: acceso completo a cualquier empresa
    - Owner (company): acceso a su propia empresa
    - Company (otro): solo si está verificada
    - Student: solo si está verificada
    - Anonymous: no tiene acceso
    """
    company = session.exec(
        select(Company).where(Company.id == company_id)
    ).first()
    
    if not company:
        _log_audit_action(
            session, "GET_COMPANY", f"company_id:{company_id}",
            current_user, success=False, error_message="Empresa no encontrada"
        )
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada"
        )
    
    # Control de acceso
    if current_user.role == "anonymous":
        raise HTTPException(
            status_code=401,
            detail="Debe estar autenticado para ver empresas"
        )
    
    if current_user.role not in ["admin"] and not company.is_active:
        raise HTTPException(
            status_code=404,
            detail="Empresa no disponible"
        )
    
    if current_user.role == "company" and current_user.user_id != company_id:
        # Company puede ver solo si la empresa está verificada
        if not company.is_verified:
            raise HTTPException(
                status_code=403,
                detail="Empresa no verificada"
            )
    
    _log_audit_action(
        session, "GET_COMPANY", f"company_id:{company_id}",
        current_user, details=f"Obtener empresa: {company.name}"
    )
    
    return _convert_to_company_profile(company)


# ============================================================================
# READ - Buscar Candidatos Estudiantes
# ============================================================================

@router.get("/{company_id}/search-students", response_model=dict)
async def search_students(
    company_id: int,
    skills: Optional[List[str]] = Query(None, description="Habilidades técnicas"),
    soft_skills: Optional[List[str]] = Query(None, description="Habilidades blandas"),
    location: Optional[str] = Query(None, description="Ubicación"),
    program: Optional[str] = Query(None, description="Programa académico"),
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Límite de resultados"),
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Buscar candidatos (estudiantes) que coincidan con criterios específicos.
    
    REQUISITO: La empresa DEBE estar verificada (is_verified=True)
    
    Parámetros de búsqueda (todos opcionales):
    - skills: List de habilidades técnicas
    - soft_skills: List de habilidades blandas
    - location: Ubicación del estudiante
    - program: Programa académico
    - skip/limit: Paginación
    
    Control de acceso:
    - Solo empresas verificadas pueden buscar
    - Solo empresas pueden acceder a este endpoint
    - Admin puede buscar desde cualquier empresa
    """
    # Verificar que el usuario es empresa o admin
    if current_user.role not in ["company", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Solo empresas verificadas pueden buscar candidatos"
        )
    
    # Obtener la empresa
    company = session.exec(
        select(Company).where(Company.id == company_id)
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada"
        )
    
    # Verificar que la empresa está verificada
    if not company.is_verified:
        _log_audit_action(
            session, "SEARCH_STUDENTS", f"company_id:{company_id}",
            current_user, success=False, error_message="Empresa no verificada"
        )
        raise HTTPException(
            status_code=403,
            detail="La empresa debe estar verificada para buscar candidatos"
        )
    
    # Verificar ownership (si no es admin, debe ser la propia empresa)
    if current_user.role == "company" and current_user.user_id != company_id:
        raise HTTPException(
            status_code=403,
            detail="Solo puedes buscar desde tu propia empresa"
        )
    
    # Construir query de búsqueda
    query = select(Student).where(Student.is_active == True)
    
    # Filtrar por habilidades técnicas (búsqueda en JSON)
    if skills:
        for skill in skills:
            query = query.where(Student.skills.ilike(f"%{skill}%"))
    
    # Filtrar por habilidades blandas (búsqueda en JSON)
    if soft_skills:
        for soft_skill in soft_skills:
            query = query.where(Student.soft_skills.ilike(f"%{soft_skill}%"))
    
    # Filtrar por ubicación
    if location:
        # Nota: En el modelo actual, location no está en Student
        # Se podría agregar en el futuro
        pass
    
    # Filtrar por programa
    if program:
        query = query.where(Student.program == program)
    
    # Obtener total
    total = session.exec(select(func.count(Student.id)).select_from(Student)).one()
    
    # Aplicar paginación
    students = session.exec(query.offset(skip).limit(limit)).all()
    
    # Convertir a StudentPublic (información pública)
    data = []
    for student in students:
        data.append({
            "id": student.id,
            "name": student.name,
            "program": student.program,
            "skills": json.loads(student.skills or "[]"),
            "soft_skills": json.loads(student.soft_skills or "[]"),
            "projects": json.loads(student.projects or "[]"),
        })
    
    _log_audit_action(
        session, "SEARCH_STUDENTS", f"company_id:{company_id}",
        current_user, details=f"Búsqueda de estudiantes (skills={skills}, found={len(data)})"
    )
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": data
    }


# ============================================================================
# UPDATE - Actualizar Empresa
# ============================================================================

@router.put("/{company_id}", response_model=CompanyProfile)
async def update_company(
    company_id: int,
    company_data: CompanyCreate,
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Actualizar datos de una empresa.
    
    Campos actualizables:
    - name, industry, size, location
    
    Campos NO actualizables:
    - email (inmutable para auditoría)
    - is_verified (usar endpoint /verify)
    - is_active (usar endpoint /activate)
    
    Control de acceso:
    - Owner (company): puede actualizar su propia empresa
    - Admin: puede actualizar cualquier empresa
    """
    company = session.exec(
        select(Company).where(Company.id == company_id)
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada"
        )
    
    # Control de acceso: owner o admin
    if current_user.role == "company" and current_user.user_id != company_id:
        raise HTTPException(
            status_code=403,
            detail="Solo puedes actualizar tu propia empresa"
        )
    
    if current_user.role not in ["company", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para actualizar empresas"
        )
    
    # Validar tamaño si se proporciona
    if company_data.size and company_data.size not in VALID_SIZES:
        raise HTTPException(
            status_code=400,
            detail=f"Size debe ser uno de: {', '.join(VALID_SIZES)}"
        )
    
    # Actualizar campos
    try:
        company.name = company_data.name
        company.industry = company_data.industry
        company.size = company_data.size
        company.location = company_data.location
        company.updated_at = datetime.utcnow()
        
        session.add(company)
        session.commit()
        session.refresh(company)
        
        _log_audit_action(
            session, "UPDATE_COMPANY", f"company_id:{company.id}",
            current_user, details=f"Empresa {company.name} actualizada"
        )
        
        return _convert_to_company_profile(company)
        
    except Exception as e:
        session.rollback()
        _log_audit_action(
            session, "UPDATE_COMPANY", f"company_id:{company_id}",
            current_user, success=False, error_message=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error actualizando empresa: {str(e)}"
        )


# ============================================================================
# PATCH - Verificar Empresa (Admin Only)
# ============================================================================

@router.patch("/{company_id}/verify", response_model=BaseResponse)
async def verify_company(
    company_id: int,
    is_verified: bool,
    reason: Optional[str] = Query(None, max_length=500),
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Verificar o rechazar empresa (SOLO ADMIN).
    
    Parámetros:
    - is_verified: true para verificar, false para rechazar
    - reason: Razón del rechazo (opcional)
    
    Solo administradores pueden ejecutar esta operación.
    """
    # Verificar que es admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Solo administradores pueden verificar empresas"
        )
    
    company = session.exec(
        select(Company).where(Company.id == company_id)
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada"
        )
    
    try:
        company.is_verified = is_verified
        company.updated_at = datetime.utcnow()
        
        session.add(company)
        session.commit()
        session.refresh(company)
        
        _log_audit_action(
            session, "VERIFY_COMPANY", f"company_id:{company.id}",
            current_user, details=f"Empresa {company.name} verificada: {is_verified}, reason: {reason}"
        )
        
        return BaseResponse(
            success=True,
            message=f"Empresa {'verificada' if is_verified else 'rechazada'} exitosamente"
        )
        
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error verificando empresa: {str(e)}"
        )


# ============================================================================
# PATCH - Activar/Desactivar Empresa
# ============================================================================

@router.patch("/{company_id}/activate", response_model=BaseResponse)
async def activate_company(
    company_id: int,
    is_active: bool,
    reason: Optional[str] = Query(None, max_length=500),
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Activar o desactivar empresa (soft delete).
    
    Parámetros:
    - is_active: true para activar, false para desactivar
    - reason: Razón de desactivación (opcional)
    
    Control de acceso:
    - Owner: puede desactivar su propia empresa
    - Admin: puede activar/desactivar cualquier empresa
    """
    company = session.exec(
        select(Company).where(Company.id == company_id)
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada"
        )
    
    # Control de acceso
    if current_user.role == "company" and current_user.user_id != company_id:
        raise HTTPException(
            status_code=403,
            detail="Solo puedes activar/desactivar tu propia empresa"
        )
    
    if current_user.role not in ["company", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para activar/desactivar empresas"
        )
    
    try:
        company.is_active = is_active
        company.updated_at = datetime.utcnow()
        
        session.add(company)
        session.commit()
        session.refresh(company)
        
        _log_audit_action(
            session, "ACTIVATE_COMPANY", f"company_id:{company.id}",
            current_user, details=f"Empresa {company.name} {'activada' if is_active else 'desactivada'}, reason: {reason}"
        )
        
        return BaseResponse(
            success=True,
            message=f"Empresa {'activada' if is_active else 'desactivada'} exitosamente"
        )
        
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error activando/desactivando empresa: {str(e)}"
        )


# ============================================================================
# DELETE - Eliminar Empresa
# ============================================================================

@router.delete("/{company_id}", response_model=BaseResponse)
async def delete_company(
    company_id: int,
    permanently: bool = Query(False, description="Hard delete (admin only)"),
    reason: Optional[str] = Query(None, max_length=500),
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Eliminar empresa (soft delete por defecto).
    
    Parámetros:
    - permanently: true para hard delete (SOLO ADMIN), false para soft delete (default)
    - reason: Razón de eliminación (requerida para hard delete)
    
    Comportamientos:
    - Soft delete: Marca como inactiva (reversible)
    - Hard delete: Elimina físicamente (solo admin, con razón)
    
    Control de acceso:
    - Owner: puede hacer soft delete de su empresa
    - Admin: puede hacer soft o hard delete
    """
    company = session.exec(
        select(Company).where(Company.id == company_id)
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada"
        )
    
    # Control de acceso
    if current_user.role == "company" and current_user.user_id != company_id:
        raise HTTPException(
            status_code=403,
            detail="Solo puedes eliminar tu propia empresa"
        )
    
    if current_user.role not in ["company", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para eliminar empresas"
        )
    
    # Hard delete solo para admin
    if permanently and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Solo administradores pueden hacer eliminación permanente"
        )
    
    # Razón requerida para hard delete
    if permanently and not reason:
        raise HTTPException(
            status_code=422,
            detail="Se requiere razón para eliminación permanente"
        )
    
    try:
        if permanently:
            # Hard delete (eliminación física)
            session.delete(company)
            session.commit()
            
            _log_audit_action(
                session, "DELETE_COMPANY_HARD", f"company_id:{company_id}",
                current_user, details=f"Empresa {company.name} eliminada permanentemente, reason: {reason}"
            )
            
            return BaseResponse(
                success=True,
                message="Empresa eliminada permanentemente"
            )
        else:
            # Soft delete (cambiar a inactiva)
            company.is_active = False
            company.updated_at = datetime.utcnow()
            
            session.add(company)
            session.commit()
            session.refresh(company)
            
            _log_audit_action(
                session, "DELETE_COMPANY_SOFT", f"company_id:{company_id}",
                current_user, details=f"Empresa {company.name} desactivada (soft delete), reason: {reason}"
            )
            
            return BaseResponse(
                success=True,
                message="Empresa desactivada (puede ser reactivada)"
            )
        
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error eliminando empresa: {str(e)}"
        )
