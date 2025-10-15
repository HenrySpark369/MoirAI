"""
Servicios de matchmaking entre estudiantes y oportunidades laborales
Algoritmos de compatibilidad y recomendación
"""
from typing import List, Dict, Tuple, Optional
import json
from datetime import datetime, timedelta
from sqlmodel import Session, select

from app.models import Student, JobMatchEvent
from app.schemas import JobItem, MatchResult, StudentPublic, MatchingCriteria
from app.services.nlp_service import nlp_service
from app.providers import job_provider_manager
from app.core.database import engine


class MatchingService:
    """Servicio principal de matching y recomendaciones"""
    
    def __init__(self):
        self.min_match_score = 0.1  # Puntuación mínima para considerar match
        self.boost_factors = {
            "location": 0.1,      # Boost por coincidencia de ubicación
            "recent_activity": 0.05,  # Boost por actividad reciente del estudiante
            "project_relevance": 0.15,  # Boost por relevancia de proyectos
            "skill_diversity": 0.1     # Boost por diversidad de habilidades
        }
    
    def build_student_query(self, student: Student) -> str:
        """Construir query de búsqueda basada en el perfil del estudiante"""
        skills = json.loads(student.skills or "[]")
        projects = json.loads(student.projects or "[]")
        
        # Seleccionar las mejores habilidades y proyectos para la query
        top_skills = skills[:5]  # Top 5 habilidades
        top_projects = projects[:3]  # Top 3 proyectos
        
        # Construir query combinando habilidades y proyectos
        query_parts = []
        
        if top_skills:
            query_parts.extend(top_skills)
        
        if top_projects:
            # Extraer palabras clave de proyectos
            for project in top_projects:
                project_keywords = self._extract_keywords_from_project(project)
                query_parts.extend(project_keywords[:2])  # Max 2 keywords por proyecto
        
        # Añadir términos genéricos si no hay suficiente información
        if not query_parts:
            if student.program:
                query_parts.append(student.program.lower())
            query_parts.extend(["intern", "junior", "trainee"])
        
        return " ".join(query_parts[:8])  # Limitar a 8 términos max
    
    def _extract_keywords_from_project(self, project_description: str) -> List[str]:
        """Extraer palabras clave relevantes de la descripción de un proyecto"""
        # Palabras clave técnicas comunes en proyectos
        tech_keywords = {
            "web", "mobile", "app", "api", "database", "dashboard", "machine learning",
            "data analysis", "visualization", "backend", "frontend", "fullstack",
            "automation", "algorithm", "prediction", "classification", "regression"
        }
        
        project_lower = project_description.lower()
        found_keywords = []
        
        for keyword in tech_keywords:
            if keyword in project_lower:
                found_keywords.append(keyword)
        
        return found_keywords[:3]  # Max 3 keywords
    
    async def find_job_recommendations(self, student_id: int, 
                                     location: Optional[str] = None,
                                     limit: int = 10) -> Dict[str, any]:
        """Encontrar recomendaciones de trabajos para un estudiante"""
        with Session(engine) as session:
            student = session.get(Student, student_id)
            if not student:
                raise ValueError(f"Estudiante con ID {student_id} no encontrado")
            
            # Construir query de búsqueda
            search_query = self.build_student_query(student)
            
            # Buscar trabajos usando los proveedores
            raw_jobs = await job_provider_manager.search_all_providers(
                query=search_query,
                location=location,
                limit_per_provider=limit
            )
            
            # Calcular scores de matching
            scored_jobs = []
            for job in raw_jobs:
                score, details = self._calculate_job_match_score(student, job)
                if score >= self.min_match_score:
                    job.match_score = round(score, 3)
                    scored_jobs.append((job, score, details))
            
            # Ordenar por score descendente
            scored_jobs.sort(key=lambda x: x[1], reverse=True)
            
            # Tomar los mejores matches
            best_jobs = [job for job, score, details in scored_jobs[:limit]]
            
            # Registrar evento de matching
            match_event = JobMatchEvent(
                student_id=student_id,
                query=search_query,
                num_results=len(best_jobs),
                source="internal_matching"
            )
            session.add(match_event)
            session.commit()
            
            return {
                "student_id": student_id,
                "jobs": best_jobs,
                "total_found": len(raw_jobs),
                "matches_found": len(best_jobs),
                "query_used": search_query,
                "generated_at": datetime.utcnow()
            }
    
    def _calculate_job_match_score(self, student: Student, job: JobItem) -> Tuple[float, Dict]:
        """Calcular score de compatibilidad entre estudiante y trabajo"""
        student_skills = json.loads(student.skills or "[]")
        student_projects = json.loads(student.projects or "[]")
        
        # Usar el servicio NLP para calcular score base
        job_description = f"{job.title} {job.description or ''}"
        base_score, match_details = nlp_service.calculate_match_score(
            student_skills, student_projects, job_description
        )
        
        # Aplicar factores de boost
        total_boost = 0.0
        boost_details = {}
        
        # Boost por ubicación
        if (job.location and student.program and 
            any(city in job.location.lower() for city in ["córdoba", "cordoba"])):
            location_boost = self.boost_factors["location"]
            total_boost += location_boost
            boost_details["location"] = location_boost
        
        # Boost por actividad reciente
        if student.last_active:
            days_since_active = (datetime.utcnow() - student.last_active).days
            if days_since_active <= 7:  # Activo en los últimos 7 días
                activity_boost = self.boost_factors["recent_activity"]
                total_boost += activity_boost
                boost_details["recent_activity"] = activity_boost
        
        # Boost por relevancia de proyectos
        if len(match_details.get("matching_projects", [])) >= 2:
            project_boost = self.boost_factors["project_relevance"]
            total_boost += project_boost
            boost_details["project_relevance"] = project_boost
        
        # Boost por diversidad de habilidades
        if len(student_skills) >= 8:
            diversity_boost = self.boost_factors["skill_diversity"]
            total_boost += diversity_boost
            boost_details["skill_diversity"] = diversity_boost
        
        final_score = min(base_score + total_boost, 1.0)
        
        return final_score, {
            **match_details,
            "base_score": base_score,
            "boost_applied": total_boost,
            "boost_details": boost_details,
            "final_score": final_score
        }
    
    def filter_students_by_criteria(self, criteria: MatchingCriteria) -> List[MatchResult]:
        """Filtrar estudiantes basado en criterios específicos"""
        with Session(engine) as session:
            # Obtener todos los estudiantes activos
            students = session.exec(
                select(Student).where(Student.is_active == True)
            ).all()
            
            matched_students = []
            
            for student in students:
                student_skills = json.loads(student.skills or "[]")
                student_projects = json.loads(student.projects or "[]")
                
                # Verificar criterios de skills
                if criteria.skills:
                    required_skills = [s.lower() for s in criteria.skills]
                    student_skills_lower = [s.lower() for s in student_skills]
                    
                    matching_skills = [
                        skill for skill in required_skills
                        if any(req_skill in skill for req_skill in student_skills_lower)
                    ]
                    
                    if len(matching_skills) < len(required_skills) * 0.5:  # Al menos 50% match
                        continue
                else:
                    matching_skills = []
                
                # Verificar criterios de proyectos
                if criteria.projects:
                    required_projects = [p.lower() for p in criteria.projects]
                    student_projects_lower = [p.lower() for p in student_projects]
                    
                    matching_projects = []
                    for req_proj in required_projects:
                        for stud_proj in student_projects_lower:
                            if req_proj in stud_proj:
                                matching_projects.append(stud_proj)
                                break
                    
                    if len(matching_projects) == 0:
                        continue
                else:
                    matching_projects = []
                
                # Calcular score basado en matches
                skill_score = len(matching_skills) / max(len(criteria.skills or []), 1)
                project_score = len(matching_projects) / max(len(criteria.projects or []), 1)
                final_score = (skill_score * 0.7) + (project_score * 0.3)
                
                # Crear resultado de match
                student_public = StudentPublic(
                    id=student.id,
                    name=student.name,
                    program=student.program,
                    skills=student_skills,
                    soft_skills=json.loads(student.soft_skills or "[]"),
                    projects=student_projects
                )
                
                match_result = MatchResult(
                    student=student_public,
                    score=round(final_score, 3),
                    matching_skills=matching_skills,
                    matching_projects=matching_projects
                )
                
                matched_students.append(match_result)
            
            # Ordenar por score descendente
            matched_students.sort(key=lambda x: x.score, reverse=True)
            
            return matched_students
    
    def get_featured_students(self, limit: int = 10) -> List[StudentPublic]:
        """Obtener estudiantes destacados basado en métricas de calidad"""
        with Session(engine) as session:
            students = session.exec(
                select(Student).where(Student.is_active == True)
            ).all()
            
            scored_students = []
            
            for student in students:
                score = self._calculate_student_featured_score(student)
                scored_students.append((student, score))
            
            # Ordenar por score y tomar los mejores
            scored_students.sort(key=lambda x: x[1], reverse=True)
            
            featured = []
            for student, score in scored_students[:limit]:
                student_public = StudentPublic(
                    id=student.id,
                    name=student.name,
                    program=student.program,
                    skills=json.loads(student.skills or "[]"),
                    soft_skills=json.loads(student.soft_skills or "[]"),
                    projects=json.loads(student.projects or "[]")
                )
                featured.append(student_public)
            
            return featured
    
    def _calculate_student_featured_score(self, student: Student) -> float:
        """Calcular score para estudiante destacado"""
        skills = json.loads(student.skills or "[]")
        soft_skills = json.loads(student.soft_skills or "[]")
        projects = json.loads(student.projects or "[]")
        
        # Factores de scoring
        skill_score = min(len(skills) / 10.0, 1.0)  # Normalizado a 10 habilidades
        soft_skill_score = min(len(soft_skills) / 5.0, 1.0)  # Normalizado a 5 habilidades
        project_score = min(len(projects) / 3.0, 1.0)  # Normalizado a 3 proyectos
        
        # Bonus por actividad reciente
        activity_bonus = 0.0
        if student.last_active:
            days_since_active = (datetime.utcnow() - student.last_active).days
            if days_since_active <= 30:
                activity_bonus = 0.2 * (30 - days_since_active) / 30
        
        # Score final ponderado
        final_score = (
            skill_score * 0.4 +
            project_score * 0.3 +
            soft_skill_score * 0.2 +
            activity_bonus * 0.1
        )
        
        return min(final_score, 1.0)


# Instancia global del servicio
matching_service = MatchingService()
