"""
Endpoints para gestión de estudiantes - CRUD completo (ASYNC)
Incluye operaciones para crear, leer, actualizar y eliminar estudiantes
considerando historias de usuario y flujos de trabajo académicos
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, BackgroundTasks, status, Request
from fastapi.responses import FileResponse, StreamingResponse
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import json
import hashlib
from datetime import datetime, timedelta
import logging
import re
import io

# PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

from app.core.database import get_session
from app.models import Student, AuditLog, Company, JobApplicationDB
from app.schemas import (
    StudentProfile, StudentCreate, StudentUpdate, StudentSkillsUpdate, ResumeUploadRequest,
    ResumeAnalysisResponse, UserContext, BaseResponse, PaginatedResponse,
    StudentPublic
)
from app.services.text_vectorization_service import text_vectorization_service, TermExtractor
from app.services.cv_extractor_v2_spacy import CVExtractorV2
from app.utils.file_processing import extract_text_from_upload, extract_text_from_upload_async, CVFileValidator
from app.middleware.auth import AuthService
from app.core.config import settings

router = APIRouter(prefix="/students", tags=["students"])

logger = logging.getLogger(__name__)


async def _log_audit_action(session: AsyncSession, action: str, resource: str, 
                     actor: UserContext, success: bool = True, 
                     details: str = None, error_message: str = None):
    """Helper para registrar acciones de auditoría de forma asincrónica"""
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
    await session.commit()


def _extract_resume_analysis(resume_text: str) -> dict:
    """
    Procesar análisis de CV para extraer skills, soft_skills y proyectos estructurados.
    
    Usa analyze_document() de text_vectorization_service para obtener features,
    luego los procesa según la lógica de negocio del endpoint.
    
    Retorna:
        Dict con: {
            "skills": [...],
            "soft_skills": [...],
            "projects": [...],
            "confidence": float
        }
    """
    if not resume_text or len(resume_text.strip()) < 50:
        return {
            "skills": [],
            "soft_skills": [],
            "projects": [],
            "confidence": 0.0
        }
    
    try:
        # Usar analyze_document (genérico) para obtener features
        doc_analysis = text_vectorization_service.analyze_document(resume_text)
        
        # Extraer skills de los términos técnicos
        # technical_terms es List[Tuple[term, relevance]]
        technical_terms = doc_analysis.get("technical_terms", [])
        skills = [term[0] if isinstance(term, tuple) else term 
                 for term in technical_terms]
        skills = skills[:settings.MAX_SKILLS_EXTRACTED]
        
        # Extraer soft_skills de las habilidades blandas detectadas
        # soft_skills es List[Tuple[skill, relevance]]
        soft_skills_detected = doc_analysis.get("soft_skills", [])
        soft_skills = [skill[0] if isinstance(skill, tuple) else skill 
                      for skill in soft_skills_detected]
        soft_skills = soft_skills[:settings.MAX_SOFT_SKILLS_EXTRACTED]
        
        # Extraer proyectos de las keyphrases
        # keyphrases es List[Tuple[phrase, score]]
        keyphrases = doc_analysis.get("keyphrases", [])
        projects = []
        project_keywords = {
            "proyecto", "project", "desarrollo", "developed", "created", "implementé",
            "sistema", "system", "aplicación", "application", "plataforma", "platform"
        }
        
        for phrase, score in keyphrases:
            phrase_lower = str(phrase).lower()
            if any(kw in phrase_lower for kw in project_keywords):
                projects.append(str(phrase))
                if len(projects) >= settings.MAX_PROJECTS_EXTRACTED:
                    break
        
        # Calcular confianza basada en elementos encontrados
        total_found = len(skills) + len(soft_skills) + len(projects)
        confidence = min(1.0, total_found / 10.0)
        
        return {
            "skills": skills,
            "soft_skills": soft_skills,
            "projects": projects,
            "confidence": round(confidence, 2)
        }
    
    except Exception as e:
        # Fallback: análisis básico con hardcoded skills
        print(f"⚠️ Error en _extract_resume_analysis: {str(e)}, usando fallback básico")
        
        resume_clean = resume_text.lower()
        technical_skills = {
            "python", "java", "javascript", "typescript", "csharp", "cpp", "rust", "go",
            "react", "vue", "angular", "fastapi", "django", "flask", "spring",
            "postgresql", "mongodb", "redis", "docker", "kubernetes", "aws",
            "machine learning", "tensorflow", "pytorch", "pandas", "numpy",
            "sql", "rest", "api", "microservices", "linux", "git"
        }
        
        skills = [skill for skill in technical_skills if skill in resume_clean]
        skills = skills[:settings.MAX_SKILLS_EXTRACTED]
        
        return {
            "skills": skills,
            "soft_skills": [],
            "projects": [],
            "confidence": min(1.0, len(skills) / 10.0)
        }


def _extract_harvard_cv_fields(resume_text: str) -> dict:
    """
    Extrae campos estructurados del CV en formato Harvard.
    
    Mejora la extracción para manejar CVs en español y formatos variables.
    
    Retorna:
        Dict con: {
            "objective": str,
            "education": List[Dict],
            "experience": List[Dict],
            "certifications": List[str],
            "languages": List[str]
        }
    """
    import re
    
    if not resume_text or len(resume_text.strip()) < 50:
        return {
            "objective": None,
            "education": [],
            "experience": [],
            "certifications": [],
            "languages": []
        }
    
    try:
        lines = resume_text.split('\n')
        text_lower = resume_text.lower()
        
        # 1️⃣ Extraer OBJETIVO: Primer párrafo después del contacto
        objective = None
        contact_end_idx = 0
        
        # Encontrar dónde termina la información de contacto
        for i, line in enumerate(lines[:15]):
            line = line.strip()
            if not line:
                continue
            # Si la línea contiene email, teléfono, o URLs, es parte del contacto
            if ('@' in line and '.' in line) or any(char.isdigit() for char in line if char not in ['/', '-', ' ']) or 'http' in line:
                contact_end_idx = i + 1
            # Si encontramos una línea que parece ser el inicio del objetivo
            elif len(line) > 50 and not any(keyword in line.lower() for keyword in ['educación', 'education', 'experiencia', 'experience', 'habilidades', 'skills']):
                break
        
        # El objetivo es el párrafo que sigue al contacto
        objective_lines = []
        for i in range(contact_end_idx, min(len(lines), contact_end_idx + 10)):
            line = lines[i].strip()
            if line and len(line) > 20 and not any(keyword in line.lower() for keyword in ['educación', 'education', 'experiencia', 'experience', 'habilidades', 'skills', 'certific', 'idioma']):
                objective_lines.append(line)
                if len(' '.join(objective_lines)) > 300:  # Limitar a ~300 caracteres
                    break
        
        if objective_lines:
            objective = ' '.join(objective_lines)[:500]
        
        # 2️⃣ Extraer EDUCACIÓN: Buscar patrones de universidades y títulos
        education = []
        edu_keywords = [
            'universidad', 'university', 'instituto', 'institute', 'colegio', 'school',
            'licenciatura', 'degree', 'bachiller', 'master', 'maestría', 'doctorado', 'phd',
            'ingeniería', 'engineering', 'ciencia', 'science', 'tecnología', 'technology'
        ]
        
        # Buscar párrafos que contengan keywords de educación
        paragraphs = resume_text.split('\n\n')
        for para in paragraphs:
            para_lower = para.lower()
            if any(keyword in para_lower for keyword in edu_keywords):
                lines_in_para = [l.strip() for l in para.split('\n') if l.strip()]
                
                if len(lines_in_para) >= 1:
                    edu_record = {
                        "institution": "",
                        "degree": "",
                        "field_of_study": "",
                        "graduation_year": None
                    }
                    
                    # Primera línea suele ser la institución
                    edu_record["institution"] = lines_in_para[0]
                    
                    # Buscar año de graduación
                    year_match = re.search(r'(20\d{2}|19\d{2})', para)
                    if year_match:
                        edu_record["graduation_year"] = int(year_match.group(1))
                    
                    # Buscar título académico
                    for line in lines_in_para:
                        if any(keyword in line.lower() for keyword in ['licenciatura', 'degree', 'bachiller', 'master', 'maestría', 'ingeniería', 'ciencia']):
                            edu_record["degree"] = line
                            break
                    
                    # Campo de estudio (si hay más líneas)
                    if len(lines_in_para) >= 3:
                        edu_record["field_of_study"] = lines_in_para[2]
                    
                    if edu_record["institution"]:
                        education.append(edu_record)
        
        # Limitar a máximo 3 educaciones
        education = education[:3]
        
        # 3️⃣ Extraer EXPERIENCIA: Buscar patrones de trabajo
        experience = []
        exp_keywords = [
            'experiencia', 'experience', 'trabajo', 'job', 'puesto', 'position',
            'empresa', 'company', 'organización', 'organization'
        ]
        
        # Buscar párrafos que contengan keywords de experiencia
        for para in paragraphs:
            para_lower = para.lower()
            if any(keyword in para_lower for keyword in exp_keywords) or re.search(r'\d{4}\s*[-–]\s*(presente|actual|actualidad|\d{4})', para_lower):
                lines_in_para = [l.strip() for l in para.split('\n') if l.strip()]
                
                if len(lines_in_para) >= 2:
                    exp_record = {
                        "position": "",
                        "company": "",
                        "start_date": None,
                        "end_date": None,
                        "description": ""
                    }
                    
                    # Buscar fechas (formato: 2020-2022, 2020/2022, 2020 – 2022, 2020 - Presente)
                    date_match = re.search(r'(\d{4})\s*[-–/]\s*(presente|actual|actualidad|(\d{4}))?', para, re.IGNORECASE)
                    if date_match:
                        exp_record["start_date"] = date_match.group(1)
                        if date_match.group(2) and date_match.group(2).lower() not in ['presente', 'actual', 'actualidad']:
                            exp_record["end_date"] = date_match.group(2)
                        elif date_match.group(3):
                            exp_record["end_date"] = date_match.group(3)
                    
                    # Primera línea significativa suele ser el puesto
                    first_line = lines_in_para[0]
                    if not re.search(r'\d{4}', first_line):  # Si no tiene fecha
                        exp_record["position"] = first_line
                        if len(lines_in_para) >= 2:
                            exp_record["company"] = lines_in_para[1]
                    else:
                        # Si la primera línea tiene fecha, buscar el puesto en la siguiente
                        if len(lines_in_para) >= 2:
                            exp_record["position"] = lines_in_para[1]
                            if len(lines_in_para) >= 3:
                                exp_record["company"] = lines_in_para[2]
                    
                    # Descripción: resto del párrafo
                    desc_lines = []
                    for line in lines_in_para[2:]:
                        if line and len(line) > 10:
                            desc_lines.append(line)
                    
                    exp_record["description"] = ' '.join(desc_lines) if desc_lines else para
                    
                    if exp_record["position"]:
                        experience.append(exp_record)
        
        # Limitar a máximo 4 experiencias
        experience = experience[:4]
        
        # 4️⃣ Extraer CERTIFICACIONES: Buscar menciones de certificados
        certifications = []
        cert_keywords = ['certific', 'course', 'diploma', 'diplomado', 'capacitación', 'training', 'workshop']
        
        for para in paragraphs:
            para_lower = para.lower()
            if any(keyword in para_lower for keyword in cert_keywords):
                lines_in_para = [l.strip() for l in para.split('\n') if l.strip()]
                certifications.extend(lines_in_para[:3])  # Máximo 3 por párrafo
        
        certifications = certifications[:5]  # Máximo 5 total
        
        # 5️⃣ Extraer IDIOMAS: Buscar menciones de idiomas
        languages = []
        lang_patterns = [
            r'(inglés|english)[\s:]*([a-zA-Z\s]+)',
            r'(español|spanish)[\s:]*([a-zA-Z\s]+)',
            r'(francés|french)[\s:]*([a-zA-Z\s]+)',
            r'(alemán|german)[\s:]*([a-zA-Z\s]+)',
            r'(portugués|portuguese)[\s:]*([a-zA-Z\s]+)',
            r'(italiano|italian)[\s:]*([a-zA-Z\s]+)',
            r'(chino|chinese)[\s:]*([a-zA-Z\s]+)'
        ]
        
        for pattern in lang_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                lang_name = match[0] if isinstance(match, tuple) else match
                level = match[1] if isinstance(match, tuple) and len(match) > 1 else ""
                lang_entry = lang_name.strip()
                if level:
                    lang_entry += f": {level.strip()}"
                if lang_entry not in languages:
                    languages.append(lang_entry)
        
        languages = languages[:5]  # Máximo 5 idiomas
        
        return {
            "objective": objective,
            "education": education,
            "experience": experience,
            "certifications": certifications,
            "languages": languages
        }
    
    except Exception as e:
        print(f"⚠️ Error en _extract_harvard_cv_fields mejorado: {str(e)}")
        return {
            "objective": None,
            "education": [],
            "experience": [],
            "certifications": [],
            "languages": []
        }


def _convert_to_student_profile(student: Student) -> StudentProfile:
    """Convierte modelo Student a StudentProfile"""
    # Extraer first_name y last_name del nombre combinado si no están presentes
    first_name = student.first_name
    last_name = student.last_name
    
    if not first_name or not last_name:
        parts = student.name.split(' ', 1)
        if not first_name:
            first_name = parts[0] if parts else ""
        if not last_name:
            last_name = parts[1] if len(parts) > 1 else ""
    
    return StudentProfile(
        id=student.id,
        name=student.name,
        role="student",  # ✅ INCLUIR role para que frontend siempre sepa el rol
        first_name=first_name,
        last_name=last_name,
        email=student.get_email(),  # ✅ DESENCRIPTAR email antes de retornar
        phone=student.get_phone(),  # ✅ DESENCRIPTAR phone antes de retornar
        bio=student.bio,
        program=student.program,
        career=student.career,
        semester=student.semester,
        skills=json.loads(student.skills or "[]"),
        soft_skills=json.loads(student.soft_skills or "[]"),
        projects=json.loads(student.projects or "[]"),
        # ✅ Harvard CV Fields (NEW)
        objective=student.objective,
        education=json.loads(student.education or "[]") if student.education else None,
        experience=json.loads(student.experience or "[]") if student.experience else None,
        certifications=json.loads(student.certifications or "[]") if student.certifications else None,
        languages=json.loads(student.languages or "[]") if student.languages else None,
        # 🤖 ML Classification Fields (NEW)
        industry=student.industry,
        seniority_level=student.seniority_level,
        cv_uploaded=student.cv_uploaded or False,
        cv_filename=student.cv_filename,
        cv_upload_date=student.cv_upload_date,
        created_at=student.created_at,
        last_active=student.last_active,
        is_active=student.is_active
    )


# === CREAR ESTUDIANTES ===

@router.post("/", response_model=StudentProfile, status_code=201)
async def create_student(
    student_data: StudentCreate,
    session: AsyncSession = Depends(get_session),
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
    existing = (await session.execute(
        select(Student).where(Student.email == student_data.email)
    )).scalars().first()
    
    if existing:
        await _log_audit_action(
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
        await session.commit()
        await session.refresh(student)
        
        await _log_audit_action(
            session, "CREATE_STUDENT", f"student_id:{student.id}",
            current_user, details=f"Estudiante {student.name} creado manualmente"
        )
        
        return _convert_to_student_profile(student)
        
    except Exception as e:
        session.rollback()
        await _log_audit_action(
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
    session: AsyncSession = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Subir y analizar currículum de estudiante
    
    Historia de usuario: Como estudiante, quiero subir mi currículum para que
    el sistema extraiga automáticamente mis habilidades y proyectos.
    
    Flujo:
    - Si el estudiante NO EXISTE: crea un nuevo registro y lo asocia al email
    - Si el estudiante YA EXISTE: actualiza su CV y habilidades extraídas
    
    Extrae habilidades técnicas, blandas y proyectos usando NLP
    """
    # Validar metadatos
    try:
        meta_dict = json.loads(meta)
        student_data = ResumeUploadRequest(**meta_dict)
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {str(e)}")
        await _log_audit_action(
            session, "UPLOAD_RESUME", f"email:{meta[:50] if meta else 'unknown'}...",
            current_user, success=False, error_message=f"JSON inválido: {str(e)}"
        )
        raise HTTPException(
            status_code=400, 
            detail=f"Metadatos JSON inválidos: {str(e)}"
        )
    except ValueError as e:
        print(f"❌ Validation error: {str(e)}")
        await _log_audit_action(
            session, "UPLOAD_RESUME", f"email:{meta_dict.get('email', 'unknown')}",
            current_user, success=False, error_message=f"Validación fallida: {str(e)}"
        )
        raise HTTPException(
            status_code=400, 
            detail=f"Validación de metadatos fallida: {str(e)}"
        )
    except Exception as e:
        print(f"❌ Unexpected error in metadata parsing: {str(e)}")
        await _log_audit_action(
            session, "UPLOAD_RESUME", f"email:unknown",
            current_user, success=False, error_message=f"Error inesperado: {str(e)}"
        )
        raise HTTPException(
            status_code=400, 
            detail=f"Error procesando metadatos: {str(e)}"
        )
    
    # Verificar permisos: solo estudiantes, administradores y empresas (para demo)
    # En modo demo (emails con "demo"), permitir cualquier rol
    is_demo_mode = "demo" in meta_dict.get("email", "").lower()
    if not is_demo_mode and current_user.role not in ["student", "admin", "company"]:
        raise HTTPException(
            status_code=403,
            detail="Solo estudiantes, administradores y empresas pueden subir currículums"
        )
    
    # Verificar si ya existe estudiante con ese email (usando hash para comparación segura)
    email_hash = hashlib.sha256(student_data.email.lower().encode()).hexdigest()
    result = await session.execute(
        select(Student).where(Student.email_hash == email_hash)
    )
    existing = result.scalars().first()
    
    # Extraer texto del archivo (usando versión async para no bloquear)
    try:
        resume_text = await extract_text_from_upload_async(file)
        if len(resume_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="El currículum debe contener al menos 50 caracteres de texto"
            )
    except Exception as e:
        await _log_audit_action(
            session, "UPLOAD_RESUME", f"email:{student_data.email}",
            current_user, success=False, error_message=f"Error procesando archivo: {str(e)}"
        )
        raise HTTPException(
            status_code=400,
            detail=f"Error procesando archivo: {str(e)}"
        )
    
    # Análisis NLP
    try:
        import logging
        logger = logging.getLogger(__name__)
        
        analysis = _extract_resume_analysis(resume_text)
        harvard_fields = _extract_harvard_cv_fields(resume_text)
        
        # ✅ FALLBACK UNSUPERVISED: Si regex no encontró campos clave → usa unsupervised extractor
        if (not harvard_fields.get("education") and 
            not harvard_fields.get("experience") and
            len(resume_text.split()) > 50):  # Solo si hay suficiente contenido
            
            logger.info("🔄 Regex no encontró campos, intentando extracción con spaCy NLP...")
            
            try:
                # Usar CVExtractorV2 con soporte bilingual automático (es + en)
                extractor = CVExtractorV2()
                spacy_result = extractor.extract(resume_text)
                
                # Convertir resultado de CVExtractorV2 (dataclass) a dict compatible con el código existente
                harvard_fields = {
                    "objective": spacy_result.objective,
                    "education": [
                        {
                            "institution": edu.institution,
                            "degree": edu.degree,
                            "field_of_study": edu.field,
                            "graduation_year": edu.end_year  # end_year es el año de graduación
                        }
                        for edu in spacy_result.education
                    ],
                    "experience": [
                        {
                            "position": exp.position,
                            "company": exp.company,
                            "start_date": str(exp.start_year) if exp.start_year else None,
                            "end_date": str(exp.end_year) if exp.end_year else None,
                            "description": exp.description
                        }
                        for exp in spacy_result.experience
                    ],
                    "certifications": spacy_result.certifications,
                    "languages": spacy_result.languages if isinstance(spacy_result.languages, list) else list(spacy_result.languages.keys()),
                    "extraction_method": "spacy_nlp_v2",
                    "confidence": 0.75  # CVExtractorV2 proporciona confianza a nivel de campos individuales
                }
                logger.info(f"✅ Extracción spaCy NLP exitosa. Educación: {len(spacy_result.education)}, Experiencia: {len(spacy_result.experience)}")
            
            except Exception as e:
                logger.error(f"❌ Error en extracción spaCy NLP: {str(e)}")
                # Fallback: mantener resultado de regex (podría estar vacío)
        
        # 🤖 CLASIFICACIÓN AUTOMÁTICA ML: Usar modelos entrenados para inferir industria y seniority
        try:
            from app.services.cv_classification_service import cv_classification_service
            cv_classification = cv_classification_service.classify_cv(resume_text, extracted_data=analysis)
            
            # Agregar campos inferidos por ML
            inferred_industry = cv_classification.industry.value if cv_classification.industry else None
            inferred_seniority = cv_classification.seniority.value if cv_classification.seniority else None
            
            logger.info(f"🤖 Clasificación ML completada - Industria: {inferred_industry}, Seniority: {inferred_seniority}")
            
        except Exception as e:
            logger.warning(f"⚠️ Error en clasificación ML: {str(e)} - Continuando sin clasificación automática")
            inferred_industry = None
            inferred_seniority = None
    
    except Exception as e:
        await _log_audit_action(
            session, "UPLOAD_RESUME", f"email:{student_data.email}",
            current_user, success=False, error_message=f"Error en análisis NLP: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error en análisis NLP: {str(e)}"
        )
    
    # Si el estudiante YA EXISTE: actualizar su CV y habilidades
    if existing:
        student = existing
        action_type = "UPDATE"
        
        # Actualizar datos
        if student_data.name:
            student.name = student_data.name
            # Actualizar first_name y last_name del nombre
            name_parts = student_data.name.split(' ', 1)
            student.first_name = name_parts[0] if len(name_parts) > 0 else ""
            student.last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        if student_data.program:
            student.program = student_data.program
        
        # Actualizar CV análisis
        student.profile_text = resume_text[:20000]
        student.skills = json.dumps(analysis["skills"])
        student.soft_skills = json.dumps(analysis["soft_skills"])
        student.projects = json.dumps(analysis["projects"])
        
        # ✅ Guardar campos Harvard CV (NEW)
        student.objective = harvard_fields["objective"]
        student.education = json.dumps(harvard_fields["education"])
        student.experience = json.dumps(harvard_fields["experience"])
        student.certifications = json.dumps(harvard_fields["certifications"])
        student.languages = json.dumps(harvard_fields["languages"])
        
        # 🤖 Guardar clasificación ML automática (NEW)
        if inferred_industry:
            student.industry = inferred_industry
        if inferred_seniority:
            student.seniority_level = inferred_seniority
        
        # ✅ Actualizar banderas de CV (FIX: persistencia en BD)
        student.cv_uploaded = True
        student.cv_filename = file.filename
        student.cv_upload_date = datetime.utcnow()
        
        await _log_audit_action(
            session, "UPLOAD_RESUME", f"student_id:{student.id}",
            current_user, details=f"Currículum actualizado para {student.name}"
        )
    
    # Si el estudiante NO EXISTE: crear uno nuevo
    else:
        action_type = "CREATE"
        # Extraer first_name y last_name del nombre completo
        name_parts = student_data.name.split(' ', 1) if student_data.name else ["", ""]
        first_name = name_parts[0] if len(name_parts) > 0 else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        student = Student(
            name=student_data.name,
            first_name=first_name,
            last_name=last_name,
            program=student_data.program,
            consent_data_processing=True,
            profile_text=resume_text[:20000],  # Limitar texto almacenado
            skills=json.dumps(analysis["skills"]),
            soft_skills=json.dumps(analysis["soft_skills"]),
            projects=json.dumps(analysis["projects"]),
            # ✅ Guardar campos Harvard CV (NEW)
            objective=harvard_fields["objective"],
            education=json.dumps(harvard_fields["education"]),
            experience=json.dumps(harvard_fields["experience"]),
            certifications=json.dumps(harvard_fields["certifications"]),
            languages=json.dumps(harvard_fields["languages"]),
            # 🤖 Guardar clasificación ML automática (NEW)
            industry=inferred_industry,
            seniority_level=inferred_seniority,
            # ✅ Establecer banderas de CV (FIX: persistencia en BD)
            cv_uploaded=True,
            cv_filename=file.filename,
            cv_upload_date=datetime.utcnow()
        )
        
        # Usar set_email() para encriptar automáticamente
        student.set_email(student_data.email)
        
        session.add(student)
        
        await _log_audit_action(
            session, "UPLOAD_RESUME", f"email:{student_data.email}",
            current_user, details=f"Nuevo estudiante registrado: {student_data.name}"
        )
    
    await session.commit()
    await session.refresh(student)
    
    await _log_audit_action(
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
    session: AsyncSession = Depends(get_session),
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
    
    result = await session.execute(query)
    students = result.scalars().all()
    
    await _log_audit_action(
        session, "LIST_STUDENTS", f"count:{len(students)}",
        current_user, details=f"Listado con filtros: program={program}, search={search}"
    )
    
    return [_convert_to_student_profile(student) for student in students]


@router.get("/stats", response_model=dict)
async def get_students_stats(
    session: AsyncSession = Depends(get_session),
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
    total_students = await session.execute(select(func.count(Student.id))).scalars().first()
    active_students = (await session.execute(
        select(func.count(Student.id)).where(Student.is_active == True)
    )).scalars().first()
    
    # Estudiantes por programa
    programs_query = (await session.execute(
        select(Student.program, func.count(Student.id))
        .where(Student.is_active == True)
        .group_by(Student.program)
    )).all()
    
    programs_stats = {program: count for program, count in programs_query if program}
    
    # Estudiantes recientes (últimos 30 días)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_students = (await session.execute(
        select(func.count(Student.id))
        .where(Student.created_at >= thirty_days_ago)
    )).scalars().first()
    
    stats = {
        "total_students": total_students,
        "active_students": active_students,
        "inactive_students": total_students - active_students,
        "students_by_program": programs_stats,
        "recent_registrations_30d": recent_students,
        "generated_at": datetime.utcnow()
    }
    
    await _log_audit_action(
        session, "VIEW_STATS", "students_stats",
        current_user, details="Consulta de estadísticas de estudiantes"
    )
    
    return stats


# ============================================================================
# SPECIFIC STUDENT ENDPOINTS (Must be before generic /{student_id})
# ============================================================================

@router.get("/profile", response_model=StudentProfile)
async def get_student_profile(
    current_user: UserContext = Depends(AuthService.get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Obtener el perfil completo del estudiante actual
    
    Retorna:
    - Información personal del estudiante
    - Habilidades técnicas y blandas
    - Proyectos realizados
    - Fechas de creación y última actividad
    """
    try:
        # Verificar que es estudiante
        if current_user.role != "student":
            raise HTTPException(
                status_code=403,
                detail="Solo estudiantes pueden acceder a sus perfiles"
            )
        
        # Buscar estudiante
        student = (await session.execute(
            select(Student).where(Student.email_hash == hashlib.sha256(current_user.email.encode()).hexdigest())
        )).scalars().first()
        
        if not student:
            raise HTTPException(status_code=404, detail="Perfil de estudiante no encontrado")
        
        profile = _convert_to_student_profile(student)
        
        await _log_audit_action(
            session, "GET_PROFILE", f"student_id:{student.id}",
            current_user, details="Perfil obtenido exitosamente"
        )
        
        return profile
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting profile: {e}")
        await _log_audit_action(
            session, "GET_PROFILE", f"student_id:{current_user.user_id}",
            current_user, success=False, error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-applications", response_model=dict)
async def get_my_applications(
    status: Optional[str] = Query(None),
    limit: int = Query(20),
    offset: int = Query(0),
    current_user: UserContext = Depends(AuthService.get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Obtener todas las aplicaciones del estudiante actual
    
    Parámetros:
    - status: Filtrar por estado (pending, accepted, rejected, withdrawn)
    - limit: Número de resultados por página (default: 20)
    - offset: Número de registros a saltar (default: 0)
    
    Retorna:
    - Lista de aplicaciones con detalles del empleador
    - Información de scoring de compatibilidad
    - Estado y fecha de aplicación
    """
    try:
        # Verificar que es estudiante
        if current_user.role != "student":
            raise HTTPException(
                status_code=403,
                detail="Solo estudiantes pueden ver sus aplicaciones"
            )
        
        # Buscar estudiante
        student = (await session.execute(
            select(Student).where(Student.email_hash == hashlib.sha256(current_user.email.encode()).hexdigest())
        )).scalars().first()
        
        if not student:
            raise HTTPException(status_code=404, detail="Perfil de estudiante no encontrado")
        
        # Construir query de aplicaciones
        from app.models import JobApplicationDB
        query = select(JobApplicationDB).where(JobApplicationDB.user_id == student.id)
        
        # Filtrar por estado si se proporciona
        if status:
            query = query.where(JobApplicationDB.status == status)
        
        # Obtener total de registros
        total_query = select(JobApplicationDB).where(JobApplicationDB.user_id == student.id)
        if status:
            total_query = total_query.where(JobApplicationDB.status == status)
        total = len((await session.execute(total_query)).scalars().all())
        
        # Aplicar paginación
        applications = (await session.execute(query.offset(offset).limit(limit))).scalars().all()
        # Enriquecer con detalles de empleos
        result = []
        for app in applications:
            from app.models import JobPosition
            job = await session.get(JobPosition, app.job_position_id)
            if job:
                result.append({
                    "id": app.id,
                    "job_id": job.id,
                    "job_title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "status": app.status,
                    "applied_date": app.application_date,
                    "updated_date": app.updated_at,
                    "match_score": getattr(app, 'match_score', None)
                })
        
        await _log_audit_action(
            session, "GET_APPLICATIONS", f"student_id:{student.id}",
            current_user, details=f"Obtenidas {len(result)} aplicaciones"
        )
        
        # Retornar wrapper con aplicaciones y total
        return {
            "applications": result,
            "total": total,
            "success": True
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting applications: {e}")
        await _log_audit_action(
            session, "GET_APPLICATIONS", f"student_id:{current_user.user_id}",
            current_user, success=False, error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/demo/applications", response_model=dict)
async def get_demo_applications(
    status: Optional[str] = Query(None),
    limit: int = Query(20),
    offset: int = Query(0),
):
    """
    Obtener aplicaciones demo para estudiantes en modo demo
    
    Parámetros:
    - status: Filtrar por estado (pending, accepted, rejected, withdrawn)
    - limit: Número de resultados por página (default: 20)
    - offset: Número de registros a saltar (default: 0)
    
    Retorna:
    - Lista de aplicaciones mock con detalles de empleos
    """
    try:
        # Mock applications data - using real scraped job IDs
        mock_applications = [
            {
                "id": "demo_app_1",
                "job_id": "20862184",  # Real scraped job ID
                "job_title": "Desarrollador Python (Híbrida)",
                "company": "CORUS E3 CONSULTING SERVICES",
                "location": "Ciudad de México",
                "status": "pending",
                "applied_date": "2025-11-25T10:30:00",
                "updated_date": "2025-11-25T10:30:00",
                "match_score": 85
            },
            {
                "id": "demo_app_2",
                "job_id": "20856168",  # Real scraped job ID
                "job_title": "Desarrollador Python CCTV",
                "company": "SYGNO",
                "location": "Remoto",
                "status": "accepted",
                "applied_date": "2025-11-20T14:15:00",
                "updated_date": "2025-11-22T09:00:00",
                "match_score": 92
            },
            {
                "id": "demo_app_3",
                "job_id": "20857647",  # Real scraped job ID
                "job_title": "Tester pruebas Automatizadas Python-Selenium",
                "company": "Empresa Confidencial",
                "location": "Córdoba",
                "status": "rejected",
                "applied_date": "2025-11-15T16:45:00",
                "updated_date": "2025-11-18T11:30:00",
                "match_score": 78
            },
            {
                "id": "demo_app_4",
                "job_id": "20862184",  # Another application to same job
                "job_title": "Desarrollador Python (Híbrida)",
                "company": "CORUS E3 CONSULTING SERVICES",
                "location": "Buenos Aires",
                "status": "pending",
                "applied_date": "2025-11-28T08:20:00",
                "updated_date": "2025-11-28T08:20:00",
                "match_score": 88
            }
        ]
        
        # Filter by status if provided
        if status:
            filtered_applications = [app for app in mock_applications if app["status"] == status]
        else:
            filtered_applications = mock_applications
        
        # Apply pagination
        total = len(filtered_applications)
        start = offset
        end = start + limit
        paginated_applications = filtered_applications[start:end]
        
        logger.info(f"🎭 Demo applications retrieved: {len(paginated_applications)} applications (total: {total})")
        
        return {
            "applications": paginated_applications,
            "total": total,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting demo applications: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get demo applications")


@router.delete("/applications/{application_id}", response_model=dict)
async def withdraw_application(
    application_id: str,
    current_user: UserContext = Depends(AuthService.get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Retirar una aplicación a un empleo (estudiante)

    Parámetros:
    - application_id: ID de la aplicación

    Retorna:
    - Confirmación de retiro exitoso
    """
    try:
        # Check if this is a demo application
        if application_id.startswith("demo_app_"):
            logger.info(f"🎭 Demo application withdrawal: {application_id}")
            return {
                "success": True,
                "message": "Application withdrawn successfully (demo mode)",
                "application_id": application_id
            }

        # For real applications, check if it exists and belongs to current user
        result = await session.execute(
            select(JobApplicationDB).where(
                JobApplicationDB.id == application_id,
                JobApplicationDB.student_id == current_user.user_id
            )
        )
        application = result.scalars().first()

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found or does not belong to current user"
            )

        # Update application status to withdrawn
        application.status = "withdrawn"
        application.updated_at = datetime.utcnow()

        # Create audit log
        audit_log = AuditLog(
            action="WITHDRAW_APPLICATION",
            details=f"application_id:{application_id}",
            actor_id=current_user.user_id,
            actor_role=current_user.role,
            target_type="application",
            target_id=application_id,
            ip_address=None,
            user_agent=None
        )
        session.add(audit_log)

        await session.commit()

        logger.info(f"✅ Application withdrawn: {application_id} by student {current_user.user_id}")

        return {
            "success": True,
            "message": "Application withdrawn successfully",
            "application_id": application_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error withdrawing application {application_id}: {e}", exc_info=True)
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to withdraw application"
        )
async def get_student_recommendations(
    limit: int = Query(10),
    current_user: UserContext = Depends(AuthService.get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Obtener recomendaciones de empleos personalizadas para el estudiante
    
    Parámetros:
    - limit: Número máximo de recomendaciones (default: 10)
    
    Retorna:
    - Lista de empleos recomendados ordenados por score de compatibilidad
    - Score de matching incluido en cada recomendación
    """
    try:
        # Verificar que es estudiante
        if current_user.role != "student":
            raise HTTPException(
                status_code=403,
                detail="Solo estudiantes pueden obtener recomendaciones"
            )
        
        # Buscar estudiante
        student = (await session.execute(
            select(Student).where(Student.email_hash == hashlib.sha256(current_user.email.encode()).hexdigest())
        )).scalars().first()
        
        if not student:
            raise HTTPException(status_code=404, detail="Perfil de estudiante no encontrado")
        
        # Obtener habilidades del estudiante
        student_skills = json.loads(student.skills or "[]")
        
        # Buscar empleos activos
        from app.models import JobPosition
        all_jobs = (await session.execute(
            select(JobPosition).where(JobPosition.is_active == True)
        )).scalars().all()
        
        # Calcular scores de compatibilidad y ordenar
        scored_jobs = []
        for job in all_jobs:
            job_skills = json.loads(job.skills or "[]") if job.skills else []
            
            # Calcular score basado en coincidencia de skills
            matches = sum(1 for skill in student_skills if any(skill.lower() in js.lower() or js.lower() in skill.lower() for js in job_skills))
            score = (matches / len(job_skills)) * 100 if job_skills else 50
            
            scored_jobs.append({
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "description": job.description[:200] + "..." if len(job.description) > 200 else job.description,
                "match_score": round(score, 2),
                "job_type": job.job_type,
                "publication_date": job.publication_date
            })
        
        # Ordenar por score descendente
        scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Limitar resultados
        recommendations = scored_jobs[:limit]
        
        await _log_audit_action(
            session, "GET_RECOMMENDATIONS", f"student_id:{student.id}",
            current_user, details=f"Obtenidas {len(recommendations)} recomendaciones"
        )
        
        # Retornar wrapper con recomendaciones
        return {
            "recommendations": recommendations,
            "total": len(recommendations),
            "generated_at": datetime.now().isoformat(),
            "success": True
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        await _log_audit_action(
            session, "GET_RECOMMENDATIONS", f"student_id:{current_user.user_id}",
            current_user, success=False, error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ✅ NUEVO ENDPOINT CRÍTICO: GET /me
# Obtiene el perfil COMPLETO del usuario autenticado desde BD
# Usado por frontend para sincronización de datos
# ============================================================================

@router.get("/me", response_model=StudentProfile)
async def get_my_profile(
    session: AsyncSession = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    ✅ ENDPOINT CRÍTICO: Obtener perfil COMPLETO del usuario autenticado
    
    Este es el endpoint que el frontend DEBE usar para obtener datos frescos de BD.
    
    Características:
    - ✅ No requiere parámetro de ID (usa usuario autenticado)
    - ✅ Retorna StudentProfile completo con CV, skills, etc.
    - ✅ Sincronización de datos del usuario
    - ✅ Recuperación de datos si localStorage fue borrado
    
    Retorna: StudentProfile con TODOS los campos:
    {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "program": "Ingeniería en Sistemas",
        "skills": ["Python", "FastAPI"],
        "soft_skills": ["Liderazgo"],
        "projects": ["Proyecto web"],
        "cv_uploaded": true,
        "cv_filename": "cv.pdf",
        "created_at": "2025-11-19T10:30:00",
        "last_active": "2025-11-19T12:00:00",
        "is_active": true
    }
    """
    try:
        # Verificar que es estudiante
        if current_user.role != "student":
            raise HTTPException(
                status_code=403,
                detail="Solo estudiantes pueden acceder a este endpoint"
            )
        
        # Buscar estudiante por su ID
        student = await session.get(Student, current_user.user_id)
        
        if not student:
            await _log_audit_action(
                session, "GET_PROFILE_ME", f"user_id:{current_user.user_id}",
                current_user, success=False, error_message="Estudiante no encontrado"
            )
            raise HTTPException(
                status_code=404,
                detail="Estudiante no encontrado"
            )
        
        # Actualizar last_active
        student.last_active = datetime.utcnow()
        session.add(student)
        await session.commit()
        
        await _log_audit_action(
            session, "GET_PROFILE_ME", f"student_id:{student.id}",
            current_user, details="Perfil completo del usuario autenticado"
        )
        
        return _convert_to_student_profile(student)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting my profile: {e}")
        await _log_audit_action(
            session, "GET_PROFILE_ME", f"user_id:{current_user.user_id}",
            current_user, success=False, error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


def get_synthetic_student_profile(student_id: int) -> StudentProfile:
    """Obtiene un perfil de estudiante desde la base de datos de CVs sintéticos"""
    import sqlite3
    import json
    import random
    from datetime import datetime
    
    try:
        # Conectar a la base de datos de CVs sintéticos
        db_path = "cv_simulator/training_data_cvs.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Buscar CV por ID (para casos donde el ID coincida)
        cursor.execute("SELECT id, industry, seniority, cv_text, annotations FROM cv_dataset WHERE id = ?", (str(student_id),))
        row = cursor.fetchone()
        
        if not row:
            # Si no existe, buscar uno aleatorio para demo (esto es normal en demo mode)
            cursor.execute("SELECT id, industry, seniority, cv_text, annotations FROM cv_dataset ORDER BY RANDOM() LIMIT 1")
            row = cursor.fetchone()
            
            if not row:
                # Si no hay CVs sintéticos, crear un perfil básico
                conn.close()
                return StudentProfile(
                    id=student_id,
                    name=f"Estudiante Demo {student_id}",
                    role="student",
                    first_name=f"Demo {student_id}",
                    last_name="Student",
                    email=f"demo{student_id}@unrc.edu.ar",
                    phone="+54 351 123 4567",
                    bio="Estudiante demo generado sintéticamente.",
                    program="Ingeniería en Sistemas",
                    career="Ingeniería en Sistemas",
                    semester="6",
                    skills=["Python", "JavaScript", "SQL"],
                    soft_skills=["Trabajo en equipo", "Comunicación"],
                    projects=["Proyecto de desarrollo web"],
                    objective="Desarrollarme profesionalmente en tecnología.",
                    education=[{
                        "institution": "Universidad Nacional de Córdoba",
                        "degree": "Ingeniería en Sistemas",
                        "field_of_study": "Ingeniería en Sistemas",
                        "graduation_year": 2026
                    }],
                    experience=[],
                    certifications=[],
                    languages=["Español (Nativo)", "Inglés (Básico)"],
                    industry="Tecnología",
                    seniority_level="Junior",
                    cv_uploaded=True,
                    cv_filename=f"cv_demo_{student_id}.pdf",
                    cv_upload_date=datetime.now().isoformat(),
                    created_at=datetime.now().isoformat(),
                    last_active=datetime.now().isoformat(),
                    is_active=True
                )
        
        profile_id, industry, seniority, cv_text, annotations_json = row
        
        # Parsear annotations
        annotations = json.loads(annotations_json) if annotations_json else {}
        
        # Extraer información del CV usando el extractor Harvard como fallback
        harvard_fields = _extract_harvard_cv_fields(cv_text)
        
        # Usar annotations como fuente principal, harvard_fields como fallback
        profile_data = {
            "id": student_id,  # Usar el ID solicitado, no el del CV sintético
            "name": annotations.get("name") or harvard_fields.get("name", f"Estudiante {student_id}"),
            "role": "student",
            "first_name": annotations.get("first_name") or (annotations.get("name", "").split()[0] if annotations.get("name") else f"Demo {student_id}"),
            "last_name": annotations.get("last_name") or (" ".join(annotations.get("name", "").split()[1:]) if annotations.get("name") and len(annotations.get("name", "").split()) > 1 else "Student"),
            "email": annotations.get("email", f"demo{student_id}@unrc.edu.ar"),
            "phone": annotations.get("phone", "+54 351 123 4567"),
            "bio": harvard_fields.get("objective", "Estudiante generado sintéticamente para demo."),
            "program": annotations.get("program", "Ingeniería en Sistemas"),
            "career": annotations.get("career", "Ingeniería en Sistemas"),
            "semester": annotations.get("semester", "6"),
            "skills": annotations.get("skills", ["Python", "JavaScript", "SQL"]),
            "soft_skills": annotations.get("soft_skills", ["Trabajo en equipo", "Comunicación"]),
            "projects": annotations.get("projects", ["Proyecto de desarrollo web"]),
            "objective": harvard_fields.get("objective", "Desarrollarme profesionalmente."),
            "education": harvard_fields.get("education", [{
                "institution": "Universidad Nacional de Córdoba",
                "degree": "Ingeniería en Sistemas",
                "field_of_study": "Ingeniería en Sistemas",
                "graduation_year": 2026
            }]),
            "experience": harvard_fields.get("experience", []),
            "certifications": harvard_fields.get("certifications", []),
            "languages": annotations.get("languages", ["Español (Nativo)", "Inglés (Básico)"]),
            "industry": industry,
            "seniority_level": seniority,
            "cv_uploaded": True,
            "cv_filename": f"cv_synthetic_{profile_id}.pdf",
            "cv_upload_date": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "is_active": True
        }
        
        conn.close()
        return StudentProfile(**profile_data)
        
    except Exception as e:
        print(f"Error obteniendo perfil sintético para student_id {student_id}: {e}")
        # Retornar perfil básico en caso de error
        return StudentProfile(
            id=student_id,
            name=f"Estudiante Demo {student_id}",
            role="student",
            first_name=f"Demo {student_id}",
            last_name="Student",
            email=f"demo{student_id}@unrc.edu.ar",
            phone="+54 351 123 4567",
            bio="Estudiante demo generado sintéticamente.",
            program="Ingeniería en Sistemas",
            career="Ingeniería en Sistemas",
            semester="6",
            skills=["Python", "JavaScript", "SQL"],
            soft_skills=["Trabajo en equipo", "Comunicación"],
            projects=["Proyecto de desarrollo web"],
            objective="Desarrollarme profesionalmente en tecnología.",
            education=[{
                "institution": "Universidad Nacional de Córdoba",
                "degree": "Ingeniería en Sistemas",
                "field_of_study": "Ingeniería en Sistemas",
                "graduation_year": 2026
            }],
            experience=[],
            certifications=[],
            languages=["Español (Nativo)", "Inglés (Básico)"],
            industry="Tecnología",
            seniority_level="Junior",
            cv_uploaded=True,
            cv_filename=f"cv_demo_{student_id}.pdf",
            cv_upload_date=datetime.now().isoformat(),
            created_at=datetime.now().isoformat(),
            last_active=datetime.now().isoformat(),
            is_active=True
        )


@router.get("/{student_id}", response_model=StudentProfile)
async def get_student(
    student_id: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Obtener perfil de estudiante por ID
    
    Historia de usuario: Como administrador o estudiante, quiero ver los detalles
    completos de un perfil estudiantil para revisar información y hacer seguimiento.
    
    Soporta tanto IDs numéricos de estudiantes reales como IDs de string del CV simulator.
    """
    # Handle demo mode
    demo_header = request.headers.get("X-Demo-Mode")
    if demo_header == "true" and current_user and current_user.role == "anonymous":
        current_user = UserContext(
            role="company",
            user_id=999,
            email="demo@company.com"
        )
    
    # Verificar permisos básicos
    if current_user.role not in ["student", "admin", "company"]:
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado para ver perfiles de estudiantes"
        )
    
    # Detectar si es un ID del CV simulator (string que parece UUID)
    import re
    is_cv_simulator_id = bool(re.match(r'^[a-f0-9\-]{36}$', student_id) or student_id.startswith('demo_'))
    
    if is_cv_simulator_id:
        # Buscar en CV simulator database
        try:
            import sqlite3
            import json
            from pathlib import Path
            
            db_path = Path(__file__).parent.parent.parent.parent / "cv_simulator" / "training_data_cvs.db"
            
            if not db_path.exists():
                raise HTTPException(status_code=404, detail="CV simulator database not found")
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Buscar el CV por ID (remover prefijo demo_ si existe)
            actual_id = student_id.replace('demo_', '')
            cursor.execute("""
                SELECT id, industry, seniority, cv_text, annotations, created_at
                FROM cv_dataset
                WHERE id = ?
            """, (actual_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found in CV simulator")
            
            profile_id, industry, seniority, cv_text, annotations_json, created_at = row
            
            # Parsear annotations
            annotations = json.loads(annotations_json) if annotations_json else {}
            
            # Crear perfil detallado compatible con StudentProfile
            profile = {
                "id": int(profile_id) if profile_id.isdigit() else hash(profile_id) % 10000,  # Convertir a int para compatibilidad
                "name": annotations.get("name", f"Estudiante Demo {profile_id}"),
                "role": "student",
                "first_name": annotations.get("name", f"Estudiante Demo {profile_id}").split()[0] if annotations.get("name") else f"Estudiante{profile_id}",
                "last_name": " ".join(annotations.get("name", f"Estudiante Demo {profile_id}").split()[1:]) if annotations.get("name") and len(annotations.get("name").split()) > 1 else f"Demo{profile_id}",
                "email": annotations.get("email", f"cv{profile_id}@example.com"),
                "phone": annotations.get("phone", "+52 55 1234 5678"),
                "bio": annotations.get("bio", f"Estudiante de {annotations.get('program', 'Ingeniería en Sistemas')} con experiencia en {industry}."),
                "program": annotations.get("program", "Ingeniería en Sistemas"),
                "career": annotations.get("program", "Ingeniería en Sistemas"),
                "semester": "6",
                "skills": annotations.get("skills", ["Python", "JavaScript", "SQL"]),
                "soft_skills": annotations.get("soft_skills", ["Trabajo en equipo", "Comunicación"]),
                "projects": [proj.get("name", "Proyecto sin nombre") if isinstance(proj, dict) else str(proj) for proj in annotations.get("projects", ["Proyecto de desarrollo web", "Análisis de datos"])],
                "objective": f"Desarrollar carrera en {industry} aplicando conocimientos técnicos.",
                "education": [
                    {
                        "institution": annotations.get("university", "UNRC"),
                        "degree": annotations.get("program", "Ingeniería en Sistemas"),
                        "field_of_study": annotations.get("program", "Ingeniería en Sistemas"),
                        "graduation_year": 2026
                    }
                ],
                "experience": [
                    {
                        "position": f"{seniority} {industry}",
                        "company": f"Empresa {industry}",
                        "start_date": "2023-01",
                        "end_date": "2024-12",
                        "description": f"Experiencia laboral en {industry}."
                    }
                ],
                "certifications": [f"Certificación en {skill}" for skill in annotations.get("skills", [])[:2]],
                "languages": ["Español (Nativo)", "Inglés (Intermedio)"],
                "industry": industry,
                "seniority_level": seniority,
                "cv_uploaded": True,
                "cv_filename": f"cv_demo_{profile_id}.pdf",
                "cv_upload_date": created_at,
                "created_at": created_at,
                "last_active": "2025-11-30T00:00:00",
                "is_active": True
            }
            
            await _log_audit_action(
                session, "GET_STUDENT", f"cv_simulator_id:{student_id}",
                current_user, details=f"Perfil CV simulator retornado: {profile['name']}"
            )
            
            return StudentProfile(**profile)
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error getting CV simulator student {student_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error loading CV simulator student: {str(e)}")
    
    # Si no es ID del CV simulator, intentar convertir a int y buscar en tabla Student
    try:
        numeric_id = int(student_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid student ID format")
    
    student = await session.get(Student, numeric_id)
    if not student:
        # Check if demo mode and return synthetic profile
        demo_header = request.headers.get("X-Demo-Mode")
        if demo_header == "true":
            synthetic_student = get_synthetic_student_profile(numeric_id)
            await _log_audit_action(
                session, "GET_STUDENT", f"student_id:{numeric_id}",
                current_user, details="Perfil sintético demo retornado"
            )
            return synthetic_student
        
        await _log_audit_action(
            session, "GET_STUDENT", f"student_id:{numeric_id}",
            current_user, success=False, error_message="Estudiante no encontrado"
        )
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    # Verificar permisos: estudiantes solo pueden ver su propio perfil
    if current_user.role == "student" and current_user.user_id != numeric_id:
        await _log_audit_action(
            session, "GET_STUDENT", f"student_id:{numeric_id}",
            current_user, success=False, error_message="Acceso denegado"
        )
        raise HTTPException(
            status_code=403, 
            detail="No tiene permisos para ver este perfil"
        )
    
    await _log_audit_action(
        session, "GET_STUDENT", f"student_id:{numeric_id}",
        current_user, details=f"Consulta de perfil de {student.name}"
    )
    
    return _convert_to_student_profile(student)


@router.get("/email/{email}", response_model=StudentProfile)
async def get_student_by_email(
    email: str,
    session: AsyncSession = Depends(get_session),
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
    
    student = (await session.execute(
        select(Student).where(Student.email == email)
    )).scalars().first()
    
    if not student:
        await _log_audit_action(
            session, "GET_STUDENT_BY_EMAIL", f"email:{email}",
            current_user, success=False, error_message="Estudiante no encontrado"
        )
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    await _log_audit_action(
        session, "GET_STUDENT_BY_EMAIL", f"email:{email}",
        current_user, details=f"Búsqueda por email de {student.name}"
    )
    
    return _convert_to_student_profile(student)


# === ACTUALIZAR ESTUDIANTES ===

@router.put("/{student_id}", response_model=StudentProfile)
async def update_student(
    student_id: int,
    student_update: StudentUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Actualizar datos básicos de estudiante
    
    Historia de usuario: Como estudiante, quiero poder actualizar mi información
    personal como nombre y programa académico para mantener mi perfil actualizado.
    """
    student = await session.get(Student, student_id)
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
        "first_name": student.first_name,
        "last_name": student.last_name,
        "phone": student.phone,
        "bio": student.bio,
        "program": student.program,
        "career": student.career,
        "semester": student.semester
    }
    
    # Actualizar campos proporcionados
    updated_fields = []
    if student_update.name is not None:
        student.name = student_update.name
        updated_fields.append("name")
    if student_update.first_name is not None:
        student.first_name = student_update.first_name
        updated_fields.append("first_name")
    if student_update.last_name is not None:
        student.last_name = student_update.last_name
        updated_fields.append("last_name")
    if student_update.phone is not None:
        student.set_phone(student_update.phone)
        updated_fields.append("phone")
    if student_update.bio is not None:
        student.bio = student_update.bio
        updated_fields.append("bio")
    if student_update.program is not None:
        student.program = student_update.program
        updated_fields.append("program")
    if student_update.career is not None:
        student.career = student_update.career
        updated_fields.append("career")
    if student_update.semester is not None:
        student.semester = student_update.semester
        updated_fields.append("semester")
    
    # ✅ Actualizar campos Harvard CV (NEW)
    if student_update.objective is not None:
        student.objective = student_update.objective
        updated_fields.append("objective")
    if student_update.education is not None:
        student.education = json.dumps(student_update.education)
        updated_fields.append("education")
    if student_update.experience is not None:
        student.experience = json.dumps(student_update.experience)
        updated_fields.append("experience")
    if student_update.certifications is not None:
        student.certifications = json.dumps(student_update.certifications)
        updated_fields.append("certifications")
    if student_update.languages is not None:
        student.languages = json.dumps(student_update.languages)
        updated_fields.append("languages")
    
    student.updated_at = datetime.utcnow()
    
    try:
        session.add(student)
        await session.commit()
        await session.refresh(student)
        
        await _log_audit_action(
            session, "UPDATE_STUDENT", f"student_id:{student_id}",
            current_user, 
            details=f"Campos actualizados: {', '.join(updated_fields)}. Valores anteriores: {old_values}"
        )
        
        return _convert_to_student_profile(student)
        
    except Exception as e:
        session.rollback()
        await _log_audit_action(
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
    session: AsyncSession = Depends(get_session),
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
    student = await session.get(Student, student_id)
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
        await session.commit()
        await session.refresh(student)
        
        await _log_audit_action(
            session, "UPDATE_SKILLS", f"student_id:{student_id}",
            current_user, details=f"Habilidades actualizadas manualmente"
        )
        
        return _convert_to_student_profile(student)
        
    except Exception as e:
        session.rollback()
        await _log_audit_action(
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
    session: AsyncSession = Depends(get_session),
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
    
    student = await session.get(Student, student_id)
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
    await session.commit()
    
    await _log_audit_action(
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
    session: AsyncSession = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Eliminar estudiante (soft delete por defecto)
    
    Historia de usuario: Como administrador, quiero poder desactivar estudiantes
    que ya no están en la universidad, pero mantener sus datos para auditoría.
    En casos excepcionales, quiero poder eliminar permanentemente.
    """
    student = await session.get(Student, student_id)
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
            await session.delete(student)
            await session.commit()
            
            await _log_audit_action(
                session, "DELETE_STUDENT_PERMANENT", f"student_id:{student_id}",
                current_user, details=f"Eliminación permanente de {student.name}"
            )
            
            return BaseResponse(
                success=True,
                message="Estudiante eliminado permanentemente"
            )
            
        except Exception as e:
            session.rollback()
            await _log_audit_action(
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
        await session.commit()
        
        await _log_audit_action(
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
    session: AsyncSession = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    Re-analizar perfil de estudiante con NLP actualizado
    
    Historia de usuario: Como administrador, quiero poder re-procesar los currículums
    cuando el sistema de NLP mejore para actualizar automáticamente las habilidades.
    """
    student = await session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    if not student.profile_text:
        raise HTTPException(
            status_code=400,
            detail="No hay texto de currículum para re-analizar"
        )
    
    # Re-análisis NLP
    try:
        analysis = _extract_resume_analysis(student.profile_text)
    except Exception as e:
        await _log_audit_action(
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
    await session.commit()
    await session.refresh(student)
    
    await _log_audit_action(
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
    session: AsyncSession = Depends(get_session),
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
            student = await session.get(Student, student_id)
            if not student or not student.profile_text:
                errors.append(f"Estudiante {student_id}: sin texto de currículum")
                continue
            
            analysis = _extract_resume_analysis(student.profile_text)
            
            student.skills = json.dumps(analysis["skills"])
            student.soft_skills = json.dumps(analysis["soft_skills"])
            student.projects = json.dumps(analysis["projects"])
            student.updated_at = datetime.utcnow()
            
            session.add(student)
            processed += 1
            
        except Exception as e:
            errors.append(f"Estudiante {student_id}: {str(e)}")
    
    await session.commit()
    
    await _log_audit_action(
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


# ============================================================================
# ✅ NUEVOS ENDPOINTS PARA GESTIÓN DE CV
# Descargar y eliminar contenido del CV del estudiante
# ============================================================================

def _generate_cv_template(student: Student) -> str:
    """
    Generar un template de CV profesional basado en EnhanceCV Modern Template

    Mejora la plantilla usando NLP para extraer información relevante:
    - Logros cuantificables de experiencia
    - Habilidades técnicas priorizadas por relevancia
    - Proyectos destacados con impacto
    - Resumen ejecutivo impactante

    Sigue las mejores prácticas de EnhanceCV:
    - Nombre prominente
    - Contacto minimalista
    - Resumen profesional fuerte
    - Experiencia con logros métricos
    - Educación concisa
    - Habilidades combinadas y priorizadas
    """
    try:
        # Parsear datos JSON del estudiante
        education = json.loads(student.education or "[]")
        experience = json.loads(student.experience or "[]")
        certifications = json.loads(student.certifications or "[]")
        languages = json.loads(student.languages or "[]")
        skills = json.loads(student.skills or "[]")
        soft_skills = json.loads(student.soft_skills or "[]")
        projects = json.loads(student.projects or "[]")

        # === NLP: Extraer logros cuantificables ===
        def extract_quantifiable_achievements(text: str) -> list:
            """Extraer logros con métricas usando patrones NLP"""
            if not text:
                return []

            achievements = []
            # Patrones para detectar métricas
            patterns = [
                r'(\d+)%',  # Porcentajes
                r'(\d+)\s*(?:personas|usuarios|clientes|proyectos)',  # Cantidades
                r'(?:incrementó|aumentó|mejoró|redujo)\s*(\d+)%',  # Mejoras porcentuales
                r'(\d+)\s*(?:horas|días|meses|años)',  # Tiempo
                r'\$[\d,]+',  # Montos monetarios
            ]

            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                achievements.extend(matches[:3])  # Máximo 3 por entrada

            return list(set(achievements))[:5]  # Eliminar duplicados, máximo 5

        # === NLP: Priorizar habilidades por relevancia ===
        def prioritize_skills(skills_list: list, experience_text: str = "") -> list:
            """Ordenar habilidades por frecuencia de mención y relevancia"""
            if not skills_list:
                return []

            # Tecnologías más demandadas (orden de prioridad)
            priority_tech = {
                'python': 10, 'javascript': 9, 'typescript': 9, 'react': 8, 'node.js': 8,
                'sql': 8, 'aws': 8, 'docker': 7, 'kubernetes': 7, 'git': 7,
                'java': 7, 'csharp': 6, 'php': 6, 'mongodb': 6, 'postgresql': 6,
                'machine learning': 9, 'tensorflow': 8, 'pytorch': 8, 'pandas': 7,
                'fastapi': 7, 'django': 7, 'flask': 6
            }

            scored_skills = []
            for skill in skills_list[:15]:  # Limitar a 15 para procesamiento
                skill_lower = skill.lower()
                base_score = priority_tech.get(skill_lower, 5)

                # Bonus por mención en experiencia
                if experience_text and skill_lower in experience_text.lower():
                    base_score += 2

                scored_skills.append((skill, base_score))

            # Ordenar por score descendente
            scored_skills.sort(key=lambda x: x[1], reverse=True)
            return [skill for skill, _ in scored_skills[:12]]  # Top 12

        # === NLP: Generar resumen ejecutivo inteligente ===
        def generate_executive_summary(student: Student, experience: list, skills: list) -> str:
            """Generar resumen ejecutivo basado en perfil usando NLP"""
            if student.objective:
                return student.objective

            # Generar automáticamente basado en experiencia y skills
            years_exp = len(experience)
            top_skills = prioritize_skills(skills, "")[:5]

            if years_exp > 0:
                exp_text = f"con {years_exp} año{'s' if years_exp > 1 else ''} de experiencia"
            else:
                exp_text = "recién graduado motivado"

            if top_skills:
                skills_text = f"especializado en {', '.join(top_skills[:3])}"
            else:
                skills_text = "con conocimientos técnicos sólidos"

            program_text = student.program or "informática"

            return f"Profesional {exp_text} en {program_text}, {skills_text}. Apasionado por desarrollar soluciones innovadoras y contribuir al crecimiento de equipos tecnológicos dinámicos."

        # === Construir CV con formato EnhanceCV Modern ===

        # 1. NOMBRE Y PROGRAMA (Prominente)
        template = f"""{student.name or "NOMBRE DEL ESTUDIANTE"}
{student.program or "PROGRAMA ACADÉMICO"}

"""

        # 2. CONTACTO (Minimalista - solo email y teléfono)
        contact_info = []
        if student.email:
            contact_info.append(f"✉️ {student.email}")
        if student.phone:
            contact_info.append(f"📱 {student.phone}")

        if contact_info:
            template += "CONTACTO\n"
            template += " | ".join(contact_info)
            template += "\n\n"

        # 3. RESUMEN EJECUTIVO (Impactante)
        summary = generate_executive_summary(student, experience, skills)
        template += f"RESUMEN PROFESIONAL\n{summary}\n\n"

        # 4. EXPERIENCIA PROFESIONAL (Sección más importante)
        if experience:
            template += "EXPERIENCIA PROFESIONAL\n"

            for exp in experience[:4]:  # Máximo 4 experiencias
                position = exp.get('position', 'Posición')
                company = exp.get('company', 'Empresa')
                start_date = exp.get('start_date', '')
                end_date = exp.get('end_date', 'Presente')
                description = exp.get('description', '')

                # Formatear fechas
                date_range = f"{start_date} - {end_date}" if start_date else end_date

                template += f"""
• {position}
  {company} | {date_range}
"""

                # Extraer y mostrar logros cuantificables
                achievements = extract_quantifiable_achievements(description)
                if achievements and len(description) > 20:
                    # Mostrar descripción con énfasis en logros
                    template += f"  {description[:150]}{'...' if len(description) > 150 else ''}"
                    if achievements:
                        template += f"\n  🚀 Logros: {', '.join(achievements[:3])}"
                elif description:
                    template += f"  {description[:150]}{'...' if len(description) > 150 else ''}"
                else:
                    template += "  Responsable del desarrollo y mantenimiento de soluciones tecnológicas."

                template += "\n"

        # 5. EDUCACIÓN (Concisa)
        if education:
            template += "\nEDUCACIÓN\n"
            for edu in education[:3]:  # Máximo 3 educaciones
                degree = edu.get('degree', 'Título')
                institution = edu.get('institution', 'Institución')
                field = edu.get('field_of_study', '')
                year = edu.get('graduation_year', '')

                template += f"""
• {degree}{' en ' + field if field else ''}
  {institution}{f' | {year}' if year else ''}"""
        else:
            template += f"""
EDUCACIÓN
• {student.program or 'Ingeniería en Sistemas'}
  Universidad Nacional de Córdoba | 2025"""

        # 6. HABILIDADES TÉCNICAS (Priorizadas por NLP)
        prioritized_skills = prioritize_skills(skills, json.dumps(experience))
        if prioritized_skills:
            template += "\n\nHABILIDADES TÉCNICAS\n"
            # Mostrar en grupos de 4 para mejor legibilidad
            for i in range(0, len(prioritized_skills), 4):
                skill_group = prioritized_skills[i:i+4]
                template += f"• {' • '.join(skill_group)}\n"

        # 7. PROYECTOS DESTACADOS (Si hay proyectos relevantes)
        if projects:
            # Filtrar proyectos más relevantes (con keywords técnicos)
            relevant_projects = []
            tech_keywords = ['web', 'app', 'sistema', 'plataforma', 'api', 'base de datos', 'machine learning', 'inteligencia artificial']

            for project in projects:
                if any(keyword in project.lower() for keyword in tech_keywords):
                    relevant_projects.append(project)

            if relevant_projects:
                template += "\n\nPROYECTOS DESTACADOS\n"
                for project in relevant_projects[:3]:  # Máximo 3 proyectos
                    template += f"• {project[:100]}{'...' if len(project) > 100 else ''}\n"

        # 8. CERTIFICACIONES (Si existen)
        if certifications:
            template += "\n\nCERTIFICACIONES\n"
            for cert in certifications[:4]:  # Máximo 4 certificaciones
                template += f"• {cert}\n"

        # 9. IDIOMAS (Si existen)
        if languages:
            template += "\n\nIDIOMAS\n"
            for lang in languages[:3]:  # Máximo 3 idiomas
                template += f"• {lang}\n"

        # 10. HABILIDADES BLANDAS (Solo las más relevantes)
        if soft_skills:
            # Filtrar habilidades blandas más profesionales
            professional_soft_skills = [
                skill for skill in soft_skills
                if skill.lower() not in ['jugar videojuegos', 'ver series', 'dormir', 'comer']
            ][:6]  # Máximo 6

            if professional_soft_skills:
                template += "\n\nHABILIDADES BLANDAS\n"
                for skill in professional_soft_skills:
                    template += f"• {skill}\n"

        # Footer con fecha de generación
        template += f"""

---
CV generado por MoirAI - UNRC Job Matching Platform
Fecha de creación: {datetime.utcnow().strftime('%d/%m/%Y')}
Template: EnhanceCV Modern Professional
"""

        return template.strip()

    except Exception as e:
        print(f"Error generando CV template mejorado: {e}")
        import traceback
        traceback.print_exc()

        # Template básico de fallback mejorado
        return f"""{student.name or "Estudiante"}
{student.program or "Programa Académico"}

CONTACTO
Email: {student.email or "email@ejemplo.com"}

RESUMEN PROFESIONAL
{student.objective or "Profesional motivado con conocimientos en desarrollo de software, buscando oportunidades para aplicar mis habilidades técnicas y contribuir al crecimiento de equipos innovadores."}

EDUCACIÓN
• {student.program or "Ingeniería en Sistemas"}
  Universidad Nacional de Córdoba | 2025

HABILIDADES TÉCNICAS
• Python • JavaScript • SQL • Git
• React • Node.js • Docker • AWS

EXPERIENCIA PROFESIONAL
• Desarrollador Full Stack
  Empresa Tecnológica | 2023 - Presente
  Desarrollo de aplicaciones web modernas con tecnologías actuales.

---
Generado por MoirAI - {datetime.utcnow().strftime('%d/%m/%Y')}
"""


def _generate_cv_pdf(cv_text: str, filename: str) -> io.BytesIO:
    """
    Generar un PDF profesional con formato EnhanceCV Modern

    Características del diseño:
    - Tipografía moderna y jerarquía clara
    - Colores profesionales (azul/teal para acentos)
    - Espaciado óptimo y márgenes adecuados
    - Iconos visuales para secciones
    - Formato responsive y legible
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

        # Crear buffer en memoria para el PDF
        buffer = io.BytesIO()

        # Configuración de página con márgenes óptimos
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

        # Márgenes más amplios para mejor legibilidad
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=50,
            rightMargin=50,
            topMargin=50,
            bottomMargin=50
        )

        styles = getSampleStyleSheet()

        # === ESTILOS PERSONALIZADOS ENHANCECV ===

        # Nombre principal - Grande y prominente
        name_style = ParagraphStyle(
            'NameStyle',
            parent=styles['Heading1'],
            fontSize=24,
            fontName='Helvetica-Bold',
            spaceAfter=8,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#1a365d')  # Azul oscuro profesional
        )

        # Programa académico - Subtítulo
        program_style = ParagraphStyle(
            'ProgramStyle',
            parent=styles['Normal'],
            fontSize=14,
            fontName='Helvetica',
            spaceAfter=20,
            textColor=colors.HexColor('#4a5568'),  # Gris medio
            alignment=TA_LEFT
        )

        # Títulos de sección - Modernos con color
        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Heading2'],
            fontSize=16,
            fontName='Helvetica-Bold',
            spaceAfter=12,
            spaceBefore=25,
            textColor=colors.HexColor('#2b6cb0'),  # Azul EnhanceCV
            alignment=TA_LEFT,
            borderWidth=0,
            borderPadding=0
        )

        # Contacto - Minimalista
        contact_style = ParagraphStyle(
            'ContactStyle',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            spaceAfter=15,
            textColor=colors.HexColor('#718096'),  # Gris claro
            alignment=TA_LEFT
        )

        # Resumen ejecutivo - Justificado para mejor lectura
        summary_style = ParagraphStyle(
            'SummaryStyle',
            parent=styles['Normal'],
            fontSize=11,
            fontName='Helvetica',
            spaceAfter=20,
            alignment=TA_JUSTIFY,
            leading=14,
            textColor=colors.HexColor('#2d3748')
        )

        # Experiencia - Con énfasis en posiciones
        position_style = ParagraphStyle(
            'PositionStyle',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            spaceAfter=2,
            textColor=colors.HexColor('#1a365d'),
            alignment=TA_LEFT
        )

        company_style = ParagraphStyle(
            'CompanyStyle',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            spaceAfter=8,
            textColor=colors.HexColor('#4a5568'),
            alignment=TA_LEFT
        )

        description_style = ParagraphStyle(
            'DescriptionStyle',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            spaceAfter=6,
            alignment=TA_LEFT,
            leading=12,
            textColor=colors.HexColor('#2d3748')
        )

        # Habilidades - En formato de badges
        skill_style = ParagraphStyle(
            'SkillStyle',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            spaceAfter=8,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#2d3748')
        )

        # Footer - Discreto
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=8,
            fontName='Helvetica-Oblique',
            alignment=TA_CENTER,
            textColor=colors.HexColor('#a0aec0'),
            spaceBefore=30
        )

        # === PROCESAMIENTO DEL CONTENIDO ===

        story = []
        lines = cv_text.strip().split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detectar y procesar secciones
            if line.upper() in ['CONTACTO', 'RESUMEN PROFESIONAL', 'EXPERIENCIA PROFESIONAL',
                              'EDUCACIÓN', 'HABILIDADES TÉCNICAS', 'PROYECTOS DESTACADOS',
                              'CERTIFICACIONES', 'IDIOMAS', 'HABILIDADES BLANDAS']:
                # Título de sección
                story.append(Paragraph(line, section_style))
                current_section = line.upper()
                continue

            # Procesar contenido según sección
            if current_section == 'CONTACTO':
                if '✉️' in line or '📱' in line:
                    story.append(Paragraph(line, contact_style))

            elif current_section == 'RESUMEN PROFESIONAL':
                if len(line) > 20:  # Evitar líneas muy cortas
                    story.append(Paragraph(line, summary_style))

            elif current_section == 'EXPERIENCIA PROFESIONAL':
                if line.startswith('• ') and not '|' in line:
                    # Posición
                    position = line[2:].strip()
                    story.append(Paragraph(position, position_style))
                elif '|' in line and (' - ' in line or 'Presente' in line):
                    # Empresa y fechas
                    story.append(Paragraph(line, company_style))
                elif line.startswith('  ') and not line.startswith('  🚀'):
                    # Descripción normal
                    description = line.strip()
                    if description:
                        story.append(Paragraph(description, description_style))
                elif line.startswith('  🚀'):
                    # Logros destacados
                    achievement = line.replace('  🚀', '🚀').strip()
                    achievement_style = ParagraphStyle(
                        'AchievementStyle',
                        parent=description_style,
                        textColor=colors.HexColor('#38a169'),  # Verde para logros
                        fontName='Helvetica-Bold'
                    )
                    story.append(Paragraph(achievement, achievement_style))

            elif current_section in ['EDUCACIÓN', 'CERTIFICACIONES', 'IDIOMAS', 'HABILIDADES BLANDAS']:
                if line.startswith('• '):
                    item = line[2:].strip()
                    story.append(Paragraph(f"• {item}", description_style))

            elif current_section == 'HABILIDADES TÉCNICAS':
                if line.startswith('• '):
                    skills_text = line[2:].strip()
                    story.append(Paragraph(skills_text, skill_style))

            elif current_section == 'PROYECTOS DESTACADOS':
                if line.startswith('• '):
                    project = line[2:].strip()
                    story.append(Paragraph(f"• {project}", description_style))

            # Nombre y programa (al inicio)
            elif len(story) == 0 and not any(char.isdigit() for char in line):
                # Probablemente el nombre
                story.append(Paragraph(line, name_style))
            elif len(story) == 1 and not line.startswith('•'):
                # Probablemente el programa
                story.append(Paragraph(line, program_style))

            # Footer
            elif '---' in line or 'generado por' in line.lower():
                story.append(Paragraph(line, footer_style))

        # Construir el PDF
        doc.build(story)
        buffer.seek(0)

        return buffer

    except Exception as e:
        print(f"Error generando PDF mejorado: {e}")
        import traceback
        traceback.print_exc()

        # Fallback: PDF simple pero mejorado
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        # Estilos de fallback mejorados
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER
        )

        content_style = styles['Normal']
        content_style.fontSize = 11
        content_style.leading = 14

        story = [
            Paragraph("CV Profesional", title_style),
            Spacer(1, 20),
            Paragraph("Error en el formato avanzado. Mostrando contenido básico:", styles['Heading2']),
            Spacer(1, 12),
            Paragraph(cv_text.replace('\n', '<br/>'), content_style)
        ]

        doc.build(story)
        buffer.seek(0)
        return buffer


@router.get("/{student_id}/download-resume")
async def download_student_resume(
    student_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    📥 Descargar CV del estudiante como archivo PDF
    
    Genera y descarga un CV profesional en formato PDF.
    Si el estudiante no tiene CV subido, genera un template basado en sus datos.
    
    Respuesta: Archivo PDF para descarga
    
    Errores:
    - 404: Estudiante no existe
    - 403: No tiene permisos para descargar
    
    Permisos:
    - Propietario del perfil (puede descargar su propio CV)
    - Administradores (pueden descargar cualquier CV)
    """
    try:
        # Buscar estudiante
        student = await session.get(Student, student_id)
        if not student:
            await _log_audit_action(
                session, "DOWNLOAD_RESUME", f"student_id:{student_id}",
                current_user, success=False, error_message="Estudiante no encontrado"
            )
            raise HTTPException(
                status_code=404,
                detail="Estudiante no encontrado"
            )
        
        # Verificar permisos (solo propietario o admin)
        if current_user.role == "student" and current_user.user_id != student_id:
            await _log_audit_action(
                session, "DOWNLOAD_RESUME", f"student_id:{student_id}",
                current_user, success=False, error_message="Acceso denegado"
            )
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para descargar este CV"
            )
        
        # Determinar contenido del CV
        cv_content = ""
        filename = ""
        is_template = True  # Always use template for proper formatting
        
        # Always generate the EnhanceCV Modern template for consistent formatting
        cv_content = _generate_cv_template(student)
        filename = f"{student.name.replace(' ', '_')}_CV_EnhanceCV.pdf"
        
        # Generar PDF
        pdf_buffer = _generate_cv_pdf(cv_content, filename)
        
        # Registrar descarga en auditoría
        await _log_audit_action(
            session, "DOWNLOAD_RESUME", f"student_id:{student_id}",
            current_user, details=f"CV PDF generado y descargado - Template: {is_template}"
        )
        
        # Retornar archivo PDF
        return StreamingResponse(
            pdf_buffer,
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error downloading resume: {e}")
        await _log_audit_action(
            session, "DOWNLOAD_RESUME", f"student_id:{student_id}",
            current_user, success=False, error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{student_id}/resume", response_model=BaseResponse)
async def delete_student_resume(
    student_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserContext = Depends(AuthService.get_current_user)
):
    """
    🗑️ Eliminar/Limpiar el CV del estudiante
    
    Borra todos los datos relacionados con el CV:
    - cv_uploaded = False
    - cv_filename = None
    - profile_text = None (texto extraído)
    - skills = [] (habilidades extraídas)
    - soft_skills = [] (habilidades blandas extraídas)
    - projects = [] (proyectos extraídos)
    
    Respuesta exitosa (200):
    {
        "success": true,
        "message": "CV eliminado exitosamente"
    }
    
    Errores:
    - 404: Estudiante no existe
    - 400: Estudiante no tiene CV para eliminar
    - 403: No tiene permisos para eliminar
    
    Permisos:
    - Propietario del perfil (puede eliminar su propio CV)
    - Administradores (pueden eliminar cualquier CV)
    """
    try:
        # Buscar estudiante
        student = await session.get(Student, student_id)
        if not student:
            await _log_audit_action(
                session, "DELETE_RESUME", f"student_id:{student_id}",
                current_user, success=False, error_message="Estudiante no encontrado"
            )
            raise HTTPException(
                status_code=404,
                detail="Estudiante no encontrado"
            )
        
        # Verificar permisos
        if current_user.role == "student" and current_user.user_id != student_id:
            await _log_audit_action(
                session, "DELETE_RESUME", f"student_id:{student_id}",
                current_user, success=False, error_message="Acceso denegado"
            )
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para eliminar este CV"
            )
        
        # Verificar que tenga CV
        if not student.cv_uploaded:
            await _log_audit_action(
                session, "DELETE_RESUME", f"student_id:{student_id}",
                current_user, details="Intento de eliminar CV inexistente"
            )
            raise HTTPException(
                status_code=400,
                detail="Este estudiante no tiene CV para eliminar"
            )
        
        # Guardar nombre de archivo para auditoría
        old_filename = student.cv_filename
        
        # Limpiar TODOS los datos de CV
        student.cv_uploaded = False
        student.cv_filename = None
        student.cv_upload_date = None
        student.profile_text = None
        student.skills = json.dumps([])
        student.soft_skills = json.dumps([])
        student.projects = json.dumps([])
        student.updated_at = datetime.utcnow()
        
        session.add(student)
        await session.commit()
        await session.refresh(student)
        
        # Registrar en auditoría
        await _log_audit_action(
            session, "DELETE_RESUME", f"student_id:{student_id}",
            current_user, details=f"CV {old_filename} eliminado"
        )
        
        return BaseResponse(
            success=True,
            message="CV eliminado exitosamente"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"Error eliminando resume: {e}")
        await _log_audit_action(
            session, "DELETE_RESUME", f"student_id:{student_id}",
            current_user, success=False, error_message=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error eliminando CV"
        )


@router.get("/{student_id}/public", response_model=StudentPublic)
async def get_student_public_profile(
    student_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Obtener perfil público de estudiante (sin autenticación)
    
    Historia de usuario: Como empresa, quiero poder ver perfiles públicos
    de estudiantes para evaluar candidatos potenciales sin necesidad de
    autenticación completa.
    """
    student = await session.get(Student, student_id)
    if not student or not student.is_active:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    return StudentPublic(
        id=student.id,
        name=student.name,
        program=student.program,
        skills=json.loads(student.skills or "[]"),
        soft_skills=json.loads(student.soft_skills or "[]"),
        projects=json.loads(student.projects or "[]"),
        # ✅ ACTUALIZADO: Agregar CV metadata y timestamps
        cv_uploaded=student.cv_uploaded or False,
        cv_filename=student.cv_filename,
        created_at=student.created_at,
        last_active=student.last_active
    )


@router.post("/{student_id}/update-activity", response_model=BaseResponse)
async def update_student_activity(
    student_id: int,
    session: AsyncSession = Depends(get_session),
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
    
    student = await session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    student.last_active = datetime.utcnow()
    session.add(student)
    await session.commit()
    
    return BaseResponse(
        success=True,
        message="Actividad actualizada"
    )


@router.get("/search/skills", response_model=List[StudentPublic])
async def search_students_by_skills(
    skills: Optional[List[str]] = Query(None, description="Lista de habilidades a buscar"),
    min_matches: int = Query(1, ge=1, description="Mínimo de habilidades que deben coincidir"),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
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
        company = await session.get(Company, current_user.user_id)
        if not company or not company.is_verified:
            raise HTTPException(
                status_code=403,
                detail="La empresa debe estar verificada para buscar candidatos"
            )
    
    # Handle demo mode - if no skills provided, return sample students
    if not skills:
        # For demo purposes, return some sample students when no skills are specified
        students = (await session.execute(
            select(Student).where(Student.is_active == True).limit(limit)
        )).scalars().all()
        
        result = []
        for student in students:
            student_public = StudentPublic(
                id=student.id,
                name=student.name,
                program=student.program,
                skills=json.loads(student.skills or "[]"),
                soft_skills=json.loads(student.soft_skills or "[]"),
                projects=json.loads(student.projects or "[]"),
                cv_uploaded=student.cv_uploaded or False,
                cv_filename=student.cv_filename,
                created_at=student.created_at,
                last_active=student.last_active
            )
            result.append(student_public)
        
        await _log_audit_action(
            session, "SEARCH_BY_SKILLS", "skills:none (demo)",
            current_user, details=f"Encontrados {len(result)} estudiantes (modo demo)"
        )
        
        return result
    
    students = (await session.execute(
        select(Student).where(Student.is_active == True)
    )).scalars().all()
    
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
                projects=json.loads(student.projects or "[]"),
                # ✅ ACTUALIZADO: Agregar CV metadata y timestamps
                cv_uploaded=student.cv_uploaded or False,
                cv_filename=student.cv_filename,
                created_at=student.created_at,
                last_active=student.last_active
            )
            matching_students.append((student_public, matches))
    
    # Ordenar por número de coincidencias (mayor a menor)
    matching_students.sort(key=lambda x: x[1], reverse=True)
    
    # Limitar resultados
    result = [student for student, _ in matching_students[:limit]]
    
    await _log_audit_action(
        session, "SEARCH_BY_SKILLS", f"skills:{','.join(skills)}",
        current_user, details=f"Encontrados {len(result)} estudiantes"
    )
    
    return result


# ============================================================================
# DEMO ENDPOINTS - Using Synthetic CV Data
# ============================================================================

@router.get("/demo/search", response_model=List[dict])
async def search_demo_students(
    skills: Optional[List[str]] = Query(None, description="Lista de habilidades a buscar (opcional)"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de resultados")
):
    """
    Buscar estudiantes sintéticos para modo demo
    
    Returns synthetic student profiles from the CV simulator database
    """
    import sqlite3
    import random
    import json
    
    try:
        # Connect to synthetic CV database
        db_path = "cv_simulator/training_data_cvs.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Build query
        query = "SELECT id, industry, seniority, cv_text, annotations FROM cv_dataset"
        params = []
        
        # Filter by skills if provided
        if skills:
            skill_conditions = []
            for skill in skills:
                skill_conditions.append("cv_text LIKE ?")
                params.append(f"%{skill}%")
            if skill_conditions:
                query += " WHERE " + " OR ".join(skill_conditions)
        
        query += " ORDER BY RANDOM() LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            profile_id, industry, seniority, cv_text, annotations_json = row
            
            # Parse annotations
            annotations = json.loads(annotations_json) if annotations_json else {}
            
            # Create student-like profile
            profile = {
                "id": f"demo_{profile_id}",
                "name": annotations.get("name", f"Estudiante Demo {profile_id}"),
                "program": annotations.get("program", "Ingeniería en Sistemas"),
                "skills": annotations.get("skills", ["Python", "JavaScript", "SQL"]),
                "soft_skills": annotations.get("soft_skills", ["Trabajo en equipo", "Comunicación"]),
                "projects": annotations.get("projects", ["Proyecto de desarrollo web", "Análisis de datos"]),
                "industry": industry,
                "seniority_level": seniority,
                "location": annotations.get("location", "Ciudad de México"),
                "cv_uploaded": True,
                "cv_filename": f"cv_demo_{profile_id}.pdf",
                "created_at": "2025-11-01T00:00:00",
                "last_active": "2025-11-30T00:00:00",
                "is_demo": True
            }
            results.append(profile)
        
        conn.close()
        return results
    
    except Exception as e:
        print(f"Error searching demo students: {e}")
        raise HTTPException(status_code=500, detail="Error loading demo students")


def get_mock_student_profile(student_id: int) -> StudentProfile:
    """Retorna un perfil de estudiante mock para demo mode"""
    mock_profiles = {
        1001: {
            "id": 1001,
            "name": "Ana García López",
            "role": "student",
            "first_name": "Ana",
            "last_name": "García López",
            "email": "ana.garcia@unrc.edu.ar",
            "phone": "+54 351 123 4567",
            "bio": "Estudiante de Ingeniería en Sistemas apasionada por el desarrollo web y la inteligencia artificial.",
            "program": "Ingeniería en Sistemas",
            "career": "Ingeniería en Sistemas",
            "semester": "8",
            "skills": ["Python", "JavaScript", "React", "Node.js", "SQL", "Git"],
            "soft_skills": ["Trabajo en equipo", "Comunicación", "Resolución de problemas", "Aprendizaje continuo"],
            "projects": ["Sistema de gestión universitaria", "Aplicación móvil de delivery", "Chatbot de atención al cliente"],
            "objective": "Desarrollar soluciones tecnológicas innovadoras que impacten positivamente en la sociedad, especializándome en inteligencia artificial y desarrollo web.",
            "education": [
                {
                    "institution": "Universidad Nacional de Córdoba",
                    "degree": "Ingeniería en Sistemas",
                    "field_of_study": "Ingeniería en Sistemas de Información",
                    "graduation_year": 2026
                }
            ],
            "experience": [
                {
                    "position": "Desarrollador Frontend",
                    "company": "TechSolutions SA",
                    "start_date": "2024-03",
                    "end_date": "2024-08",
                    "description": "Desarrollo de interfaces de usuario responsivas utilizando React y TypeScript. Colaboración en equipo ágil."
                }
            ],
            "certifications": ["Certificación en React", "Certificación en Python"],
            "languages": ["Español (Nativo)", "Inglés (Intermedio)", "Portugués (Básico)"],
            "industry": "Tecnología",
            "seniority_level": "Junior",
            "cv_uploaded": True,
            "cv_filename": "cv_ana_garcia.pdf",
            "cv_upload_date": "2025-11-15T10:00:00",
            "created_at": "2025-09-01T00:00:00",
            "last_active": "2025-11-30T00:00:00",
            "is_active": True
        },
        1004: {
            "id": 1004,
            "name": "Carlos Rodríguez",
            "role": "student",
            "first_name": "Carlos",
            "last_name": "Rodríguez",
            "email": "carlos.rodriguez@unrc.edu.ar",
            "phone": "+54 351 987 6543",
            "bio": "Estudiante de Ingeniería Eléctrica con interés en energías renovables y automatización industrial.",
            "program": "Ingeniería Eléctrica",
            "career": "Ingeniería Eléctrica",
            "semester": "7",
            "skills": ["MATLAB", "C++", "Arduino", "PLC", "Autocad", "Electrónica"],
            "soft_skills": ["Análisis crítico", "Trabajo bajo presión", "Adaptabilidad", "Liderazgo"],
            "projects": ["Sistema de monitoreo solar", "Robot autónomo", "Instalación eléctrica residencial"],
            "objective": "Contribuir al desarrollo de soluciones energéticas sostenibles mediante la aplicación de tecnologías avanzadas en el campo de la ingeniería eléctrica.",
            "education": [
                {
                    "institution": "Universidad Nacional de Córdoba",
                    "degree": "Ingeniería Eléctrica",
                    "field_of_study": "Ingeniería Eléctrica",
                    "graduation_year": 2026
                }
            ],
            "experience": [
                {
                    "position": "Técnico en Electrónica",
                    "company": "ElectroTech SRL",
                    "start_date": "2024-01",
                    "end_date": "2024-06",
                    "description": "Mantenimiento y reparación de equipos electrónicos industriales. Diseño de circuitos básicos."
                }
            ],
            "certifications": ["Certificación en PLC", "Certificación en Energías Renovables"],
            "languages": ["Español (Nativo)", "Inglés (Avanzado)"],
            "industry": "Energía",
            "seniority_level": "Junior",
            "cv_uploaded": True,
            "cv_filename": "cv_carlos_rodriguez.pdf",
            "cv_upload_date": "2025-11-10T14:00:00",
            "created_at": "2025-08-15T00:00:00",
            "last_active": "2025-11-29T00:00:00",
            "is_active": True
        },
        1006: {
            "id": 1006,
            "name": "María Fernández",
            "role": "student",
            "first_name": "María",
            "last_name": "Fernández",
            "email": "maria.fernandez@unrc.edu.ar",
            "phone": "+54 351 555 1234",
            "bio": "Estudiante de Administración con pasión por la gestión empresarial y el emprendimiento.",
            "program": "Licenciatura en Administración",
            "career": "Administración",
            "semester": "6",
            "skills": ["Excel", "Power BI", "SAP", "Gestión de proyectos", "Análisis financiero"],
            "soft_skills": ["Negociación", "Liderazgo", "Empatía", "Toma de decisiones"],
            "projects": ["Plan de negocio para startup", "Análisis de mercado", "Sistema de gestión administrativa"],
            "objective": "Desarrollar una carrera en gestión empresarial, contribuyendo al crecimiento sostenible de organizaciones mediante estrategias innovadoras y eficientes.",
            "education": [
                {
                    "institution": "Universidad Nacional de Córdoba",
                    "degree": "Licenciatura en Administración",
                    "field_of_study": "Administración de Empresas",
                    "graduation_year": 2027
                }
            ],
            "experience": [
                {
                    "position": "Asistente Administrativo",
                    "company": "Consultora ABC",
                    "start_date": "2024-02",
                    "end_date": "2024-07",
                    "description": "Apoyo en gestión administrativa, elaboración de reportes y coordinación de proyectos."
                }
            ],
            "certifications": ["Certificación en Gestión de Proyectos", "Certificación en Excel Avanzado"],
            "languages": ["Español (Nativo)", "Inglés (Intermedio)", "Francés (Básico)"],
            "industry": "Consultoría",
            "seniority_level": "Junior",
            "cv_uploaded": True,
            "cv_filename": "cv_maria_fernandez.pdf",
            "cv_upload_date": "2025-11-12T16:00:00",
            "created_at": "2025-09-10T00:00:00",
            "last_active": "2025-11-28T00:00:00",
            "is_active": True
        },
        1007: {
            "id": 1007,
            "name": "Juan Pérez Martínez",
            "role": "student",
            "first_name": "Juan",
            "last_name": "Pérez Martínez",
            "email": "juan.perez@unrc.edu.ar",
            "phone": "+54 351 444 5678",
            "bio": "Estudiante de Ingeniería Civil con enfoque en construcción sostenible y gestión de proyectos.",
            "program": "Ingeniería Civil",
            "career": "Ingeniería Civil",
            "semester": "9",
            "skills": ["AutoCAD", "Revit", "SAP2000", "Gestión de proyectos", "Normativas de construcción"],
            "soft_skills": ["Planificación", "Organización", "Trabajo en equipo", "Responsabilidad"],
            "projects": ["Diseño de estructura residencial", "Proyecto de urbanización", "Análisis estructural"],
            "objective": "Contribuir al desarrollo de infraestructuras sostenibles que mejoren la calidad de vida de las comunidades, aplicando conocimientos técnicos y principios de gestión eficiente.",
            "education": [
                {
                    "institution": "Universidad Nacional de Córdoba",
                    "degree": "Ingeniería Civil",
                    "field_of_study": "Ingeniería Civil",
                    "graduation_year": 2025
                }
            ],
            "experience": [
                {
                    "position": "Pasante en Construcción",
                    "company": "Constructora del Sur",
                    "start_date": "2024-01",
                    "end_date": "2024-06",
                    "description": "Apoyo en diseño de planos, supervisión de obras y elaboración de presupuestos."
                }
            ],
            "certifications": ["Certificación en AutoCAD", "Certificación en Gestión de Proyectos"],
            "languages": ["Español (Nativo)", "Inglés (Intermedio)"],
            "industry": "Construcción",
            "seniority_level": "Junior",
            "cv_uploaded": True,
            "cv_filename": "cv_juan_perez.pdf",
            "cv_upload_date": "2025-11-08T12:00:00",
            "created_at": "2025-07-01T00:00:00",
            "last_active": "2025-11-27T00:00:00",
            "is_active": True
        }
    }
    
    profile_data = mock_profiles.get(student_id)
    if not profile_data:
        # Default mock profile
        profile_data = {
            "id": student_id,
            "name": f"Estudiante Demo {student_id}",
            "role": "student",
            "first_name": f"Demo {student_id}",
            "last_name": "Student",
            "email": f"demo{student_id}@unrc.edu.ar",
            "phone": "+54 351 123 4567",
            "bio": "Estudiante demo para pruebas del sistema MoirAI.",
            "program": "Ingeniería en Sistemas",
            "career": "Ingeniería en Sistemas",
            "semester": "6",
            "skills": ["Python", "JavaScript", "SQL"],
            "soft_skills": ["Trabajo en equipo", "Comunicación"],
            "projects": ["Proyecto demo"],
            "objective": "Aprender y desarrollarme profesionalmente en el campo de la tecnología.",
            "education": [
                {
                    "institution": "Universidad Nacional de Córdoba",
                    "degree": "Ingeniería en Sistemas",
                    "field_of_study": "Ingeniería en Sistemas",
                    "graduation_year": 2026
                }
            ],
            "experience": [],
            "certifications": [],
            "languages": ["Español (Nativo)", "Inglés (Básico)"],
            "industry": "Tecnología",
            "seniority_level": "Junior",
            "cv_uploaded": True,
            "cv_filename": f"cv_demo_{student_id}.pdf",
            "cv_upload_date": "2025-11-01T00:00:00",
            "created_at": "2025-09-01T00:00:00",
            "last_active": "2025-11-30T00:00:00",
            "is_active": True
        }
    
    return StudentProfile(**profile_data)
        
# ============================================================================
# END OF STUDENTS ENDPOINTS
# ============================================================================
