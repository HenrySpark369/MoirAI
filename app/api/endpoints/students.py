"""
Endpoints para gestión de estudiantes - CRUD completo
Incluye operaciones para crear, leer, actualizar y eliminar estudiantes
considerando historias de usuario y flujos de trabajo académicos
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlmodel import Session, select, func
import json
import hashlib
from datetime import datetime, timedelta

from app.core.database import get_session
from app.models import Student, AuditLog, Company
from app.schemas import (
    StudentProfile, StudentCreate, StudentUpdate, StudentSkillsUpdate, ResumeUploadRequest,
    ResumeAnalysisResponse, UserContext, BaseResponse, PaginatedResponse,
    StudentPublic
)
from app.services.nlp_service import nlp_service
from app.utils.file_processing import extract_text_from_upload
from app.middleware.auth import AuthService
from app.core.config import settings

router = APIRouter(prefix="/students", tags=["students"])


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


def _convert_to_student_profile(student: Student) -> StudentProfile:
    """Convierte modelo Student a StudentProfile"""
    return StudentProfile(
        id=student.id,
        name=student.name,
        email=student.email,
        program=student.program,
        skills=json.loads(student.skills or "[]"),
        soft_skills=json.loads(student.soft_skills or "[]"),
        projects=json.loads(student.projects or "[]"),
        created_at=student.created_at,
        last_active=student.last_active,
        is_active=student.is_active
    )


# === CREAR ESTUDIANTES ===

@router.post("/", response_model=StudentProfile, status_code=201)
async def create_student(
    student_data: StudentCreate,
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Crear estudiante manualmente sin currículum
    
    Historia de usuario: Como administrador, quiero poder registrar estudiantes
    manualmente para casos donde no tienen currículum digital disponible.
    """
    # Verificar permisos: solo estudiantes y administradores
    if current_user.role not in ["student", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Solo estudiantes y administradores pueden crear perfiles"
        )
    # Verificar si ya existe estudiante con ese email
    existing = session.exec(
        select(Student).where(Student.email == student_data.email)
    ).first()
    
    if existing:
        _log_audit_action(
            session, "CREATE_STUDENT", f"email:{student_data.email}",
            current_user, success=False, error_message="Email ya existe"
        )
        raise HTTPException(
            status_code=409,
            detail="Ya existe un estudiante registrado con ese email"
        )
    
    # Crear estudiante
    student = Student(
        name=student_data.name,
        email=student_data.email,
        program=student_data.program,
        consent_data_processing=student_data.consent_data_processing,
        skills=json.dumps(student_data.skills),  # Convertir lista a JSON
        soft_skills=json.dumps(student_data.soft_skills),  # Convertir lista a JSON
        projects=json.dumps(student_data.projects)  # Convertir lista a JSON
    )
    
    try:
        session.add(student)
        session.commit()
        session.refresh(student)
        
        _log_audit_action(
            session, "CREATE_STUDENT", f"student_id:{student.id}",
            current_user, details=f"Estudiante {student.name} creado manualmente"
        )
        
        return _convert_to_student_profile(student)
        
    except Exception as e:
        session.rollback()
        _log_audit_action(
            session, "CREATE_STUDENT", f"email:{student_data.email}",
            current_user, success=False, error_message=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error creando estudiante: {str(e)}"
        )


@router.post("/upload_resume", response_model=ResumeAnalysisResponse)
async def upload_resume(
    meta: str = Form(..., description="JSON con datos del estudiante"),
    file: UploadFile = File(..., description="Archivo de currículum (PDF/DOCX/TXT)"),
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Subir y analizar currículum de estudiante
    
    Historia de usuario: Como estudiante, quiero subir mi currículum para que
    el sistema extraiga automáticamente mis habilidades y proyectos.
    
    Extrae habilidades técnicas, blandas y proyectos usando NLP
    """
    # Verificar permisos: solo estudiantes y administradores
    if current_user.role not in ["student", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Solo estudiantes y administradores pueden subir currículums"
        )
    # Validar metadatos
    try:
        meta_dict = json.loads(meta)
        student_data = ResumeUploadRequest(**meta_dict)
    except Exception as e:
        _log_audit_action(
            session, "UPLOAD_RESUME", f"email:{meta[:50]}...",
            current_user, success=False, error_message=f"Metadatos inválidos: {str(e)}"
        )
        raise HTTPException(
            status_code=400, 
            detail=f"Metadatos inválidos: {str(e)}"
        )
    
    # Verificar si ya existe estudiante con ese email (usando hash para comparación segura)
    email_hash = hashlib.sha256(student_data.email.lower().encode()).hexdigest()
    existing = session.exec(
        select(Student).where(Student.email_hash == email_hash)
    ).first()
    
    if existing:
        _log_audit_action(
            session, "UPLOAD_RESUME", f"email:{student_data.email}",
            current_user, success=False, error_message="Email ya existe"
        )
        raise HTTPException(
            status_code=409,
            detail="Ya existe un estudiante registrado con ese email"
        )
    
    # Extraer texto del archivo
    try:
        resume_text = extract_text_from_upload(file)
        if len(resume_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="El currículum debe contener al menos 50 caracteres de texto"
            )
    except Exception as e:
        _log_audit_action(
            session, "UPLOAD_RESUME", f"email:{student_data.email}",
            current_user, success=False, error_message=f"Error procesando archivo: {str(e)}"
        )
        raise HTTPException(
            status_code=400,
            detail=f"Error procesando archivo: {str(e)}"
        )
    
    # Análisis NLP
    try:
        analysis = nlp_service.analyze_resume(resume_text)
    except Exception as e:
        _log_audit_action(
            session, "UPLOAD_RESUME", f"email:{student_data.email}",
            current_user, success=False, error_message=f"Error en análisis NLP: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error en análisis NLP: {str(e)}"
        )
    
    # Crear estudiante
    student = Student(
        name=student_data.name,
        program=student_data.program,
        consent_data_processing=True,
        profile_text=resume_text[:20000],  # Limitar texto almacenado
        skills=json.dumps(analysis["skills"]),
        soft_skills=json.dumps(analysis["soft_skills"]),
        projects=json.dumps(analysis["projects"])
    )
    
    # Usar set_email() para encriptar automáticamente
    student.set_email(student_data.email)
    
    session.add(student)
    session.commit()
    session.refresh(student)
    
    _log_audit_action(
        session, "UPLOAD_RESUME", f"student_id:{student.id}",
        current_user, details=f"Currículum procesado para {student.name}"
    )
    
    # Preparar respuesta
    student_profile = _convert_to_student_profile(student)
    
    return ResumeAnalysisResponse(
        student=student_profile,
        extracted_skills=analysis["skills"],
        extracted_soft_skills=analysis["soft_skills"],
        extracted_projects=analysis["projects"],
        analysis_confidence=analysis["confidence"]
    )


# === LEER ESTUDIANTES ===

@router.get("/", response_model=List[StudentProfile])
async def list_students(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de registros"),
    program: Optional[str] = Query(None, description="Filtrar por programa académico"),
    active_only: bool = Query(True, description="Solo estudiantes activos"),
    search: Optional[str] = Query(None, description="Buscar por nombre o email"),
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Listar estudiantes con filtros y paginación
    
    Historia de usuario: Como administrador, quiero ver una lista paginada
    de estudiantes con opciones de búsqueda y filtrado para gestionar eficientemente
    la base de datos estudiantil.
    """
    # Verificar permisos: solo estudiantes y administradores
    if current_user.role not in ["student", "admin", "company"]:
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado para listar estudiantes"
        )
    query = select(Student)
    
    # Aplicar filtros
    if active_only:
        query = query.where(Student.is_active == True)
    
    if program:
        query = query.where(Student.program.ilike(f"%{program}%"))
    
    if search:
        search_filter = (
            Student.name.ilike(f"%{search}%") |
            Student.email.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    
    # Aplicar paginación
    query = query.offset(skip).limit(min(limit, settings.MAX_PAGE_SIZE))
    
    students = session.exec(query).all()
    
    _log_audit_action(
        session, "LIST_STUDENTS", f"count:{len(students)}",
        current_user, details=f"Listado con filtros: program={program}, search={search}"
    )
    
    return [_convert_to_student_profile(student) for student in students]


@router.get("/stats", response_model=dict)
async def get_students_stats(
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Obtener estadísticas de estudiantes
    
    Historia de usuario: Como administrador, quiero ver estadísticas generales
    sobre los estudiantes para tomar decisiones informadas.
    """
    # Solo administradores pueden ver estadísticas
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Solo administradores pueden ver estadísticas"
        )
    # Contadores básicos
    total_students = session.exec(select(func.count(Student.id))).first()
    active_students = session.exec(
        select(func.count(Student.id)).where(Student.is_active == True)
    ).first()
    
    # Estudiantes por programa
    programs_query = session.exec(
        select(Student.program, func.count(Student.id))
        .where(Student.is_active == True)
        .group_by(Student.program)
    ).all()
    
    programs_stats = {program: count for program, count in programs_query if program}
    
    # Estudiantes recientes (últimos 30 días)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_students = session.exec(
        select(func.count(Student.id))
        .where(Student.created_at >= thirty_days_ago)
    ).first()
    
    stats = {
        "total_students": total_students,
        "active_students": active_students,
        "inactive_students": total_students - active_students,
        "students_by_program": programs_stats,
        "recent_registrations_30d": recent_students,
        "generated_at": datetime.utcnow()
    }
    
    _log_audit_action(
        session, "VIEW_STATS", "students_stats",
        current_user, details="Consulta de estadísticas de estudiantes"
    )
    
    return stats


@router.get("/{student_id}", response_model=StudentProfile)
async def get_student(
    student_id: int,
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Obtener perfil de estudiante por ID
    
    Historia de usuario: Como administrador o estudiante, quiero ver los detalles
    completos de un perfil estudiantil para revisar información y hacer seguimiento.
    """
    # Verificar permisos básicos
    if current_user.role not in ["student", "admin", "company"]:
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado para ver perfiles de estudiantes"
        )
    student = session.get(Student, student_id)
    if not student:
        _log_audit_action(
            session, "GET_STUDENT", f"student_id:{student_id}",
            current_user, success=False, error_message="Estudiante no encontrado"
        )
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    # Verificar permisos: estudiantes solo pueden ver su propio perfil
    if current_user.role == "student" and current_user.user_id != student_id:
        _log_audit_action(
            session, "GET_STUDENT", f"student_id:{student_id}",
            current_user, success=False, error_message="Acceso denegado"
        )
        raise HTTPException(
            status_code=403, 
            detail="No tiene permisos para ver este perfil"
        )
    
    _log_audit_action(
        session, "GET_STUDENT", f"student_id:{student_id}",
        current_user, details=f"Consulta de perfil de {student.name}"
    )
    
    return _convert_to_student_profile(student)


@router.get("/email/{email}", response_model=StudentProfile)
async def get_student_by_email(
    email: str,
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Obtener estudiante por email
    
    Historia de usuario: Como administrador, quiero buscar estudiantes por email
    para resolver consultas de soporte o verificar registros.
    """
    # Solo administradores pueden buscar por email
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Solo administradores pueden buscar por email"
        )
    
    student = session.exec(
        select(Student).where(Student.email == email)
    ).first()
    
    if not student:
        _log_audit_action(
            session, "GET_STUDENT_BY_EMAIL", f"email:{email}",
            current_user, success=False, error_message="Estudiante no encontrado"
        )
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    _log_audit_action(
        session, "GET_STUDENT_BY_EMAIL", f"email:{email}",
        current_user, details=f"Búsqueda por email de {student.name}"
    )
    
    return _convert_to_student_profile(student)


# === ACTUALIZAR ESTUDIANTES ===

@router.put("/{student_id}", response_model=StudentProfile)
async def update_student(
    student_id: int,
    student_update: StudentUpdate,
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Actualizar datos básicos de estudiante
    
    Historia de usuario: Como estudiante, quiero poder actualizar mi información
    personal como nombre y programa académico para mantener mi perfil actualizado.
    """
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    # Verificar permisos: estudiantes solo pueden editar su propio perfil
    if current_user.role == "student" and current_user.user_id != student_id:
        raise HTTPException(
            status_code=403,
            detail="No tiene permisos para editar este perfil"
        )
    
    # Registrar valores anteriores para auditoría
    old_values = {
        "name": student.name,
        "program": student.program
    }
    
    # Actualizar campos proporcionados
    updated_fields = []
    if student_update.name is not None:
        student.name = student_update.name
        updated_fields.append("name")
    if student_update.program is not None:
        student.program = student_update.program
        updated_fields.append("program")
    
    student.updated_at = datetime.utcnow()
    
    try:
        session.add(student)
        session.commit()
        session.refresh(student)
        
        _log_audit_action(
            session, "UPDATE_STUDENT", f"student_id:{student_id}",
            current_user, 
            details=f"Campos actualizados: {', '.join(updated_fields)}. Valores anteriores: {old_values}"
        )
        
        return _convert_to_student_profile(student)
        
    except Exception as e:
        session.rollback()
        _log_audit_action(
            session, "UPDATE_STUDENT", f"student_id:{student_id}",
            current_user, success=False, error_message=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error actualizando estudiante: {str(e)}"
        )


@router.patch("/{student_id}/skills", response_model=StudentProfile)
async def update_student_skills(
    student_id: int,
    skills_data: StudentSkillsUpdate,
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Actualizar habilidades de estudiante manualmente
    
    Historia de usuario: Como estudiante, quiero poder agregar o quitar habilidades
    de mi perfil para reflejar mejor mi experiencia actual.
    
    Formato esperado (esquema StudentSkillsUpdate):
    {
        "skills": ["Python", "JavaScript"],
        "soft_skills": ["Trabajo en equipo", "Liderazgo"],
        "projects": ["Proyecto web", "App móvil"]
    }
    """
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    # Verificar permisos
    if current_user.role == "student" and current_user.user_id != student_id:
        raise HTTPException(
            status_code=403,
            detail="No tiene permisos para editar este perfil"
        )
    
    # Validar y actualizar habilidades
    try:
        if skills_data.skills is not None:
            student.skills = json.dumps(skills_data.skills)
            
        if skills_data.soft_skills is not None:
            student.soft_skills = json.dumps(skills_data.soft_skills)
            
        if skills_data.projects is not None:
            student.projects = json.dumps(skills_data.projects)
        
        student.updated_at = datetime.utcnow()
        
        session.add(student)
        session.commit()
        session.refresh(student)
        
        _log_audit_action(
            session, "UPDATE_SKILLS", f"student_id:{student_id}",
            current_user, details=f"Habilidades actualizadas manualmente"
        )
        
        return _convert_to_student_profile(student)
        
    except Exception as e:
        session.rollback()
        _log_audit_action(
            session, "UPDATE_SKILLS", f"student_id:{student_id}",
            current_user, success=False, error_message=str(e)
        )
        raise HTTPException(
            status_code=400,
            detail=f"Error actualizando habilidades: {str(e)}"
        )


@router.patch("/{student_id}/activate", response_model=BaseResponse)
async def activate_student(
    student_id: int,
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Reactivar estudiante (deshacer soft delete)
    
    Historia de usuario: Como administrador, quiero poder reactivar estudiantes
    que fueron marcados como inactivos por error.
    """
    # Solo administradores pueden reactivar
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Solo administradores pueden reactivar estudiantes"
        )
    
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    if student.is_active:
        return BaseResponse(
            success=True,
            message="El estudiante ya está activo"
        )
    
    student.is_active = True
    student.updated_at = datetime.utcnow()
    
    session.add(student)
    session.commit()
    
    _log_audit_action(
        session, "ACTIVATE_STUDENT", f"student_id:{student_id}",
        current_user, details=f"Estudiante {student.name} reactivado"
    )
    
    return BaseResponse(
        success=True,
        message="Estudiante reactivado exitosamente"
    )


# === ELIMINAR ESTUDIANTES ===

@router.delete("/{student_id}", response_model=BaseResponse)
async def delete_student(
    student_id: int,
    permanent: bool = Query(False, description="Eliminación permanente (solo admin)"),
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Eliminar estudiante (soft delete por defecto)
    
    Historia de usuario: Como administrador, quiero poder desactivar estudiantes
    que ya no están en la universidad, pero mantener sus datos para auditoría.
    En casos excepcionales, quiero poder eliminar permanentemente.
    """
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    # Solo administradores pueden hacer eliminación permanente
    if permanent and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Solo administradores pueden eliminar permanentemente"
        )
    
    if permanent:
        # Eliminación permanente - solo admin
        try:
            session.delete(student)
            session.commit()
            
            _log_audit_action(
                session, "DELETE_STUDENT_PERMANENT", f"student_id:{student_id}",
                current_user, details=f"Eliminación permanente de {student.name}"
            )
            
            return BaseResponse(
                success=True,
                message="Estudiante eliminado permanentemente"
            )
            
        except Exception as e:
            session.rollback()
            _log_audit_action(
                session, "DELETE_STUDENT_PERMANENT", f"student_id:{student_id}",
                current_user, success=False, error_message=str(e)
            )
            raise HTTPException(
                status_code=500,
                detail=f"Error eliminando estudiante: {str(e)}"
            )
    else:
        # Soft delete: marcar como inactivo
        student.is_active = False
        student.updated_at = datetime.utcnow()
        
        session.add(student)
        session.commit()
        
        _log_audit_action(
            session, "DELETE_STUDENT_SOFT", f"student_id:{student_id}",
            current_user, details=f"Desactivación de {student.name}"
        )
        
        return BaseResponse(
            success=True,
            message="Estudiante desactivado exitosamente"
        )


# === OPERACIONES ESPECIALES ===

@router.post("/{student_id}/reanalyze", response_model=ResumeAnalysisResponse)
async def reanalyze_student_profile(
    student_id: int,
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Re-analizar perfil de estudiante con NLP actualizado
    
    Historia de usuario: Como administrador, quiero poder re-procesar los currículums
    cuando el sistema de NLP mejore para actualizar automáticamente las habilidades.
    """
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    if not student.profile_text:
        raise HTTPException(
            status_code=400,
            detail="No hay texto de currículum para re-analizar"
        )
    
    # Re-análisis NLP
    try:
        analysis = nlp_service.analyze_resume(student.profile_text)
    except Exception as e:
        _log_audit_action(
            session, "REANALYZE_STUDENT", f"student_id:{student_id}",
            current_user, success=False, error_message=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error en re-análisis: {str(e)}"
        )
    
    # Actualizar estudiante
    student.skills = json.dumps(analysis["skills"])
    student.soft_skills = json.dumps(analysis["soft_skills"])
    student.projects = json.dumps(analysis["projects"])
    student.updated_at = datetime.utcnow()
    
    session.add(student)
    session.commit()
    session.refresh(student)
    
    _log_audit_action(
        session, "REANALYZE_STUDENT", f"student_id:{student_id}",
        current_user, details=f"Re-análisis NLP completado para {student.name}"
    )
    
    # Preparar respuesta
    student_profile = _convert_to_student_profile(student)
    
    return ResumeAnalysisResponse(
        student=student_profile,
        extracted_skills=analysis["skills"],
        extracted_soft_skills=analysis["soft_skills"],
        extracted_projects=analysis["projects"],
        analysis_confidence=analysis["confidence"]
    )


@router.post("/bulk-reanalyze", response_model=BaseResponse)
async def bulk_reanalyze_students(
    student_ids: List[int],
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Re-analizar múltiples estudiantes en lote
    
    Historia de usuario: Como administrador, quiero poder re-procesar múltiples
    currículums al mismo tiempo para optimizar el tiempo de actualización.
    """
    # Solo administradores pueden hacer operaciones en lote
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Solo administradores pueden realizar operaciones en lote"
        )
    
    if len(student_ids) > 50:
        raise HTTPException(
            status_code=400,
            detail="Máximo 50 estudiantes por operación en lote"
        )
    
    processed = 0
    errors = []
    
    for student_id in student_ids:
        try:
            student = session.get(Student, student_id)
            if not student or not student.profile_text:
                errors.append(f"Estudiante {student_id}: sin texto de currículum")
                continue
            
            analysis = nlp_service.analyze_resume(student.profile_text)
            
            student.skills = json.dumps(analysis["skills"])
            student.soft_skills = json.dumps(analysis["soft_skills"])
            student.projects = json.dumps(analysis["projects"])
            student.updated_at = datetime.utcnow()
            
            session.add(student)
            processed += 1
            
        except Exception as e:
            errors.append(f"Estudiante {student_id}: {str(e)}")
    
    session.commit()
    
    _log_audit_action(
        session, "BULK_REANALYZE", f"count:{len(student_ids)}",
        current_user, 
        details=f"Procesados: {processed}, Errores: {len(errors)}"
    )
    
    message = f"Re-análisis completado. Procesados: {processed}"
    if errors:
        message += f", Errores: {len(errors)}"
    
    return BaseResponse(
        success=True,
        message=message
    )


@router.get("/{student_id}/public", response_model=StudentPublic)
async def get_student_public_profile(
    student_id: int,
    session: Session = Depends(get_session)
):
    """
    Obtener perfil público de estudiante (sin autenticación)
    
    Historia de usuario: Como empresa, quiero poder ver perfiles públicos
    de estudiantes para evaluar candidatos potenciales sin necesidad de
    autenticación completa.
    """
    student = session.get(Student, student_id)
    if not student or not student.is_active:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    return StudentPublic(
        id=student.id,
        name=student.name,
        program=student.program,
        skills=json.loads(student.skills or "[]"),
        soft_skills=json.loads(student.soft_skills or "[]"),
        projects=json.loads(student.projects or "[]")
    )


@router.post("/{student_id}/update-activity", response_model=BaseResponse)
async def update_student_activity(
    student_id: int,
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Actualizar última actividad del estudiante
    
    Historia de usuario: Como sistema, quiero registrar cuando un estudiante
    está activo para mostrar información relevante a las empresas.
    """
    # Verificar permisos: estudiantes solo pueden actualizar su propia actividad
    if current_user.role == "student" and current_user.user_id != student_id:
        raise HTTPException(
            status_code=403,
            detail="Solo puede actualizar su propia actividad"
        )
    
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    student.last_active = datetime.utcnow()
    session.add(student)
    session.commit()
    
    return BaseResponse(
        success=True,
        message="Actividad actualizada"
    )


@router.get("/search/skills", response_model=List[StudentPublic])
async def search_students_by_skills(
    skills: List[str] = Query(..., description="Lista de habilidades a buscar"),
    min_matches: int = Query(1, ge=1, description="Mínimo de habilidades que deben coincidir"),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Buscar estudiantes por habilidades específicas (búsqueda integrada de matching)
    
    Historia de usuario: Como empresa, quiero buscar estudiantes que tengan
    habilidades específicas que necesito para mis proyectos.
    
    🔒 Autorización:
    - Solo empresas verificadas y administradores
    - Los estudiantes no pueden usar este endpoint
    
    📊 Respuesta:
    - Lista de estudiantes públicos ordenados por número de coincidencias
    - Cada estudiante incluye habilidades, proyectos y programa
    
    💡 Algoritmo:
    - Búsqueda case-insensitive en habilidades técnicas y blandas
    - Ordenamiento por relevancia (más coincidencias primero)
    - Paginación mediante limit
    """
    # Autorización: solo empresas verificadas y admins
    if current_user.role not in ["company", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Solo empresas verificadas pueden buscar por habilidades"
        )
    
    # Si es empresa, verificar que está verificada
    if current_user.role == "company":
        company = session.get(Company, current_user.user_id)
        if not company or not company.is_verified:
            raise HTTPException(
                status_code=403,
                detail="La empresa debe estar verificada para buscar candidatos"
            )
    
    students = session.exec(
        select(Student).where(Student.is_active == True)
    ).all()
    
    matching_students = []
    
    for student in students:
        student_skills = json.loads(student.skills or "[]")
        student_soft_skills = json.loads(student.soft_skills or "[]")
        all_student_skills = student_skills + student_soft_skills
        
        # Contar coincidencias (case-insensitive)
        matches = 0
        for skill in skills:
            if any(skill.lower() in s.lower() or s.lower() in skill.lower() 
                   for s in all_student_skills):
                matches += 1
        
        if matches >= min_matches:
            student_public = StudentPublic(
                id=student.id,
                name=student.name,
                program=student.program,
                skills=student_skills,
                soft_skills=student_soft_skills,
                projects=json.loads(student.projects or "[]")
            )
            matching_students.append((student_public, matches))
    
    # Ordenar por número de coincidencias (mayor a menor)
    matching_students.sort(key=lambda x: x[1], reverse=True)
    
    # Limitar resultados
    result = [student for student, _ in matching_students[:limit]]
    
    _log_audit_action(
        session, "SEARCH_BY_SKILLS", f"skills:{','.join(skills)}",
        current_user, details=f"Encontrados {len(result)} estudiantes"
    )
    
    return result
