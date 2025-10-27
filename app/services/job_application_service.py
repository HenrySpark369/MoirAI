"""
Servicio para gestionar aplicaciones de empleo y seguimiento de solicitudes
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import asyncio
import logging

from sqlmodel import Session, select, func
from ..core.database import get_session
from ..models.job_scraping import (
    JobApplicationDB, 
    SearchQueryDB,
    SearchResultDB,
    UserJobAlertDB,
    ScrapingLogDB
)
from ..models import JobPosition  # Usar modelo unificado
from .occ_scraper_service import OCCScraper, SearchFilters, JobOffer

logger = logging.getLogger(__name__)


class JobApplicationManager:
    """Gestiona las aplicaciones de empleo de los usuarios"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def save_job_offer(self, job_offer: JobOffer) -> JobPosition:
        """Guarda una oferta de trabajo en la base de datos usando el modelo unificado"""
        try:
            # Verificar si la oferta ya existe
            existing_job = self.db_session.exec(
                select(JobPosition).where(JobPosition.external_job_id == job_offer.job_id)
            ).first()
            
            if existing_job:
                # Actualizar oferta existente
                existing_job.title = job_offer.title
                existing_job.company = job_offer.company
                existing_job.location = job_offer.location
                existing_job.salary_range = job_offer.salary
                existing_job.benefits = job_offer.benefits
                existing_job.updated_at = datetime.utcnow()
                
                self.db_session.add(existing_job)
                self.db_session.commit()
                self.db_session.refresh(existing_job)
                return existing_job
            
            # Crear nueva oferta usando modelo unificado
            job_db = JobPosition(
                external_job_id=job_offer.job_id,  # Mapeo correcto
                title=job_offer.title,
                company=job_offer.company,
                location=job_offer.location,
                salary_range=job_offer.salary,  # Mapeo correcto
                description=job_offer.description,
                benefits=job_offer.benefits,
                requirements=job_offer.skills,  # Mapear skills a requirements
                source="occ",  # Identificar origen
                scraped_at=datetime.utcnow(),  # Fecha de scraping
                is_active=True  # Estado inicial
            )
            
            self.db_session.add(job_db)
            self.db_session.commit()
            self.db_session.refresh(job_db)
            return job_db
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error al guardar oferta de trabajo: {e}")
            raise
    
    def create_application(self, user_id: int, job_position_id: int, 
                          external_url: Optional[str] = None,
                          notes: Optional[str] = None) -> JobApplicationDB:
        """Crea una nueva aplicación de empleo"""
        try:
            # Verificar si ya existe una aplicación para este usuario y trabajo
            existing_app = self.db_session.exec(
                select(JobApplicationDB).where(
                    JobApplicationDB.user_id == user_id,
                    JobApplicationDB.job_position_id == job_position_id
                )
            ).first()
            
            if existing_app:
                raise ValueError("Ya existe una aplicación para este empleo")
            
            application = JobApplicationDB(
                user_id=user_id,
                job_position_id=job_position_id,
                status="applied",
                external_application_url=external_url,
                notes=notes
            )
            
            self.db_session.add(application)
            self.db_session.commit()
            self.db_session.refresh(application)
            return application
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error al crear aplicación: {e}")
            raise
    
    def update_application_status(self, application_id: int, 
                                status: str, notes: Optional[str] = None) -> JobApplicationDB:
        """Actualiza el estatus de una aplicación"""
        try:
            application = self.db_session.get(JobApplicationDB, application_id)
            if not application:
                raise ValueError("Aplicación no encontrada")
            
            application.status = status
            application.updated_at = datetime.utcnow()
            if notes:
                application.notes = notes
            
            self.db_session.add(application)
            self.db_session.commit()
            self.db_session.refresh(application)
            return application
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error al actualizar aplicación: {e}")
            raise
    
    def get_user_applications(self, user_id: int, 
                            status: Optional[str] = None) -> List[JobApplicationDB]:
        """Obtiene las aplicaciones de un usuario"""
        try:
            query = select(JobApplicationDB).where(JobApplicationDB.user_id == user_id)
            
            if status:
                query = query.where(JobApplicationDB.status == status)
            
            query = query.order_by(JobApplicationDB.created_at.desc())
            
            return self.db_session.exec(query).all()
            
        except Exception as e:
            logger.error(f"Error al obtener aplicaciones del usuario: {e}")
            raise
    
    def get_application_statistics(self, user_id: int) -> Dict:
        """Obtiene estadísticas de aplicaciones para un usuario"""
        try:
            # Total de aplicaciones
            total_query = select(func.count(JobApplicationDB.id)).where(
                JobApplicationDB.user_id == user_id
            )
            total_applications = self.db_session.exec(total_query).first() or 0
            
            # Aplicaciones por estatus
            status_query = select(
                JobApplicationDB.status,
                func.count(JobApplicationDB.id)
            ).where(
                JobApplicationDB.user_id == user_id
            ).group_by(JobApplicationDB.status)
            
            status_counts = dict(self.db_session.exec(status_query).all())
            
            # Aplicaciones recientes (último mes)
            last_month = datetime.utcnow() - timedelta(days=30)
            recent_query = select(func.count(JobApplicationDB.id)).where(
                JobApplicationDB.user_id == user_id,
                JobApplicationDB.created_at >= last_month
            )
            recent_applications = self.db_session.exec(recent_query).first() or 0
            
            return {
                "total_applications": total_applications,
                "status_breakdown": status_counts,
                "recent_applications": recent_applications,
                "success_rate": round(
                    (status_counts.get("accepted", 0) / max(total_applications, 1)) * 100, 2
                )
            }
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            raise


class JobSearchManager:
    """Gestiona búsquedas de empleo y resultados"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.app_manager = JobApplicationManager(db_session)
    
    async def perform_search_and_save(self, user_id: Optional[int], 
                                    filters: SearchFilters) -> Tuple[List[JobOffer], int]:
        """Realiza una búsqueda y guarda los resultados en la base de datos"""
        try:
            # Realizar búsqueda
            async with OCCScraper() as scraper:
                jobs, total_results = await scraper.search_jobs(filters)
            
            # Guardar consulta de búsqueda
            search_query = SearchQueryDB(
                user_id=user_id,
                keyword=filters.keyword,
                location=filters.location,
                filters=filters.dict(exclude={'keyword', 'location'}),
                total_results=total_results
            )
            
            self.db_session.add(search_query)
            self.db_session.commit()
            self.db_session.refresh(search_query)
            
            # Guardar ofertas de trabajo y resultados
            for position, job in enumerate(jobs, 1):
                # Guardar oferta
                job_db = self.app_manager.save_job_offer(job)
                
                # Crear vinculación de resultado
                search_result = SearchResultDB(
                    search_query_id=search_query.id,
                    job_position_id=job_db.id,
                    position_in_results=position
                )
                
                self.db_session.add(search_result)
            
            self.db_session.commit()
            
            # Log de la operación
            self._log_scraping_operation(
                operation_type="search",
                search_keyword=filters.keyword,
                results_count=len(jobs),
                success=True
            )
            
            return jobs, total_results
            
        except Exception as e:
            self.db_session.rollback()
            self._log_scraping_operation(
                operation_type="search",
                search_keyword=filters.keyword,
                results_count=0,
                success=False,
                error_message=str(e)
            )
            logger.error(f"Error en búsqueda y guardado: {e}")
            raise
    
    def get_search_history(self, user_id: int, limit: int = 10) -> List[SearchQueryDB]:
        """Obtiene el historial de búsquedas de un usuario"""
        try:
            query = select(SearchQueryDB).where(
                SearchQueryDB.user_id == user_id
            ).order_by(SearchQueryDB.created_at.desc()).limit(limit)
            
            return self.db_session.exec(query).all()
            
        except Exception as e:
            logger.error(f"Error al obtener historial de búsquedas: {e}")
            raise
    
    def get_popular_searches(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Obtiene las búsquedas más populares en los últimos días"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            query = select(
                SearchQueryDB.keyword,
                func.count(SearchQueryDB.id).label("search_count")
            ).where(
                SearchQueryDB.created_at >= start_date
            ).group_by(SearchQueryDB.keyword).order_by(
                func.count(SearchQueryDB.id).desc()
            ).limit(limit)
            
            results = self.db_session.exec(query).all()
            
            return [
                {"keyword": keyword, "search_count": count}
                for keyword, count in results
            ]
            
        except Exception as e:
            logger.error(f"Error al obtener búsquedas populares: {e}")
            raise
    
    def _log_scraping_operation(self, operation_type: str, 
                               search_keyword: Optional[str] = None,
                               results_count: int = 0,
                               success: bool = True,
                               error_message: Optional[str] = None):
        """Registra operaciones de scraping en el log"""
        try:
            log_entry = ScrapingLogDB(
                operation_type=operation_type,
                search_keyword=search_keyword,
                results_count=results_count,
                success=success,
                error_message=error_message
            )
            
            self.db_session.add(log_entry)
            self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Error al registrar log: {e}")


class JobAlertManager:
    """Gestiona alertas de empleo personalizadas"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.search_manager = JobSearchManager(db_session)
    
    def create_job_alert(self, user_id: int, keywords: List[str],
                        location: Optional[str] = None,
                        salary_min: Optional[int] = None,
                        work_mode: Optional[str] = None,
                        frequency: str = "daily") -> UserJobAlertDB:
        """Crea una nueva alerta de empleo"""
        try:
            alert = UserJobAlertDB(
                user_id=user_id,
                keywords=keywords,
                location=location,
                salary_min=salary_min,
                work_mode=work_mode,
                frequency=frequency
            )
            
            self.db_session.add(alert)
            self.db_session.commit()
            self.db_session.refresh(alert)
            return alert
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error al crear alerta: {e}")
            raise
    
    async def check_alerts_and_notify(self) -> Dict[str, int]:
        """Verifica todas las alertas activas y genera notificaciones"""
        try:
            # Obtener alertas que necesitan verificación
            alerts = self._get_alerts_to_check()
            
            notifications_sent = 0
            errors = 0
            
            for alert in alerts:
                try:
                    await self._process_single_alert(alert)
                    notifications_sent += 1
                except Exception as e:
                    logger.error(f"Error procesando alerta {alert.id}: {e}")
                    errors += 1
            
            return {
                "alerts_processed": len(alerts),
                "notifications_sent": notifications_sent,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Error en verificación de alertas: {e}")
            raise
    
    def _get_alerts_to_check(self) -> List[UserJobAlertDB]:
        """Obtiene alertas que necesitan ser verificadas"""
        now = datetime.utcnow()
        
        # Calcular tiempo mínimo desde última notificación según frecuencia
        daily_cutoff = now - timedelta(hours=24)
        weekly_cutoff = now - timedelta(days=7)
        
        query = select(UserJobAlertDB).where(
            UserJobAlertDB.is_active == True,
            (
                # Alertas diarias que no se han verificado en 24h
                (UserJobAlertDB.frequency == "daily") & 
                ((UserJobAlertDB.last_notification == None) | 
                 (UserJobAlertDB.last_notification <= daily_cutoff)) |
                
                # Alertas semanales que no se han verificado en 7 días
                (UserJobAlertDB.frequency == "weekly") & 
                ((UserJobAlertDB.last_notification == None) | 
                 (UserJobAlertDB.last_notification <= weekly_cutoff))
            )
        )
        
        return self.db_session.exec(query).all()
    
    async def _process_single_alert(self, alert: UserJobAlertDB):
        """Procesa una alerta individual"""
        try:
            new_jobs = []
            
            # Buscar empleos para cada keyword
            for keyword in alert.keywords:
                filters = SearchFilters(
                    keyword=keyword,
                    location=alert.location,
                    work_mode=alert.work_mode,
                    sort_by="date",
                    page=1
                )
                
                jobs, _ = await self.search_manager.perform_search_and_save(
                    alert.user_id, filters
                )
                
                # Filtrar solo empleos nuevos (últimas 24h)
                recent_jobs = [
                    job for job in jobs 
                    if any(term in job.publication_date.lower() 
                          for term in ["hoy", "ayer"])
                ]
                
                new_jobs.extend(recent_jobs)
                
                # Delay para no sobrecargar el servidor
                await asyncio.sleep(2)
            
            # Actualizar última notificación
            alert.last_notification = datetime.utcnow()
            self.db_session.add(alert)
            self.db_session.commit()
            
            # Aquí podrías enviar notificación por email/push
            if new_jobs:
                logger.info(f"Enviando notificación a usuario {alert.user_id} con {len(new_jobs)} nuevos empleos")
            
        except Exception as e:
            logger.error(f"Error procesando alerta {alert.id}: {e}")
            raise
