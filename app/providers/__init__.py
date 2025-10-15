"""
Proveedores de búsqueda de trabajos externos
Implementa patrón Strategy para diferentes fuentes de trabajos
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import httpx
import asyncio
from app.schemas import JobItem
from app.core.config import settings


class JobProvider(ABC):
    """Interfaz base para proveedores de trabajos"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre del proveedor"""
        pass
    
    @abstractmethod
    async def search(self, query: str, location: Optional[str] = None, 
                    limit: int = 10) -> List[JobItem]:
        """Buscar trabajos"""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Verificar si el proveedor está disponible"""
        pass


class JSearchProvider(JobProvider):
    """
    Proveedor JSearch (RapidAPI)
    Integra con Indeed, LinkedIn y otros sitios de trabajo
    """
    
    def __init__(self, api_key: str, host: str):
        self.api_key = api_key
        self.host = host
        self._timeout = 30
    
    @property
    def name(self) -> str:
        return "jsearch"
    
    async def is_available(self) -> bool:
        """Verificar disponibilidad del servicio"""
        if not self.api_key:
            return False
        
        try:
            headers = {
                "x-rapidapi-key": self.api_key,
                "x-rapidapi-host": self.host,
            }
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(
                    f"https://{self.host}/search",
                    headers=headers,
                    params={"query": "test", "page": 1, "num_pages": 1}
                )
                return response.status_code == 200
        except Exception:
            return False
    
    async def search(self, query: str, location: Optional[str] = None, 
                    limit: int = 10) -> List[JobItem]:
        """Buscar trabajos en JSearch"""
        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.host,
        }
        
        # Construir query con ubicación si se proporciona
        search_query = f"{query} in {location}" if location else query
        
        params = {
            "query": search_query,
            "page": 1,
            "num_pages": 1,
            "date_posted": "month"  # Trabajos del último mes
        }
        
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    f"https://{self.host}/search",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
            
            jobs = []
            for job_data in data.get("data", [])[:limit]:
                job = JobItem(
                    title=job_data.get("job_title", ""),
                    company=job_data.get("employer_name"),
                    location=job_data.get("job_city"),
                    url=job_data.get("job_apply_link") or job_data.get("job_publisher_site"),
                    source="JSearch",
                    description=job_data.get("job_description", "")[:500]  # Limitar descripción
                )
                jobs.append(job)
            
            return jobs
            
        except httpx.TimeoutException:
            raise Exception(f"Timeout al conectar con {self.name}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"Error HTTP {e.response.status_code} en {self.name}")
        except Exception as e:
            raise Exception(f"Error en {self.name}: {str(e)}")


class CompuTrabajoProvider(JobProvider):
    """
    Proveedor para CompuTrabajo (ejemplo de implementación futura)
    Nota: Requeriría integración específica o scraping autorizado
    """
    
    @property
    def name(self) -> str:
        return "computrabajo"
    
    async def is_available(self) -> bool:
        # Implementar verificación específica
        return False
    
    async def search(self, query: str, location: Optional[str] = None, 
                    limit: int = 10) -> List[JobItem]:
        # TODO: Implementar integración con CompuTrabajo
        # Requiere API específica o scraping autorizado
        return []


class LinkedInProvider(JobProvider):
    """
    Proveedor para LinkedIn (ejemplo de implementación futura)
    Nota: Requiere LinkedIn Jobs API o integración empresarial
    """
    
    @property
    def name(self) -> str:
        return "linkedin"
    
    async def is_available(self) -> bool:
        # Implementar verificación específica
        return False
    
    async def search(self, query: str, location: Optional[str] = None, 
                    limit: int = 10) -> List[JobItem]:
        # TODO: Implementar integración con LinkedIn Jobs API
        return []


class MockProvider(JobProvider):
    """
    Proveedor mock para desarrollo y testing
    """
    
    def __init__(self):
        self.mock_jobs = [
            {
                "title": "Data Analyst Intern",
                "company": "TechCorp Argentina",
                "location": "Buenos Aires",
                "description": "Buscamos estudiante de ingeniería para análisis de datos con Python y SQL"
            },
            {
                "title": "Software Developer Trainee",
                "company": "Innovación SA",
                "location": "Córdoba",
                "description": "Desarrollo de aplicaciones web con React y Node.js"
            },
            {
                "title": "Machine Learning Intern",
                "company": "AI Solutions",
                "location": "Rosario",
                "description": "Implementación de modelos de ML con Python, scikit-learn y TensorFlow"
            },
            {
                "title": "Full Stack Developer Jr",
                "company": "StartupTech",
                "location": "Mendoza",
                "description": "Desarrollo full stack con Python/FastAPI backend y React frontend"
            },
            {
                "title": "Data Science Intern",
                "company": "Analytics Pro",
                "location": "Córdoba",
                "description": "Análisis de datos, visualización con Tableau y desarrollo de dashboards"
            }
        ]
    
    @property
    def name(self) -> str:
        return "mock"
    
    async def is_available(self) -> bool:
        return True
    
    async def search(self, query: str, location: Optional[str] = None, 
                    limit: int = 10) -> List[JobItem]:
        """Buscar en trabajos mock"""
        # Simular latencia de red
        await asyncio.sleep(0.1)
        
        query_lower = query.lower()
        filtered_jobs = []
        
        for mock_job in self.mock_jobs:
            # Filtrar por query
            if (query_lower in mock_job["title"].lower() or 
                query_lower in mock_job["description"].lower()):
                
                # Filtrar por ubicación si se especifica
                if location and location.lower() not in mock_job["location"].lower():
                    continue
                
                job = JobItem(
                    title=mock_job["title"],
                    company=mock_job["company"],
                    location=mock_job["location"],
                    url=f"https://example.com/job/{len(filtered_jobs)}",
                    source="Mock",
                    description=mock_job["description"]
                )
                filtered_jobs.append(job)
        
        return filtered_jobs[:limit]


class JobProviderManager:
    """
    Gestor de proveedores de trabajos
    Maneja múltiples proveedores y agregación de resultados
    """
    
    def __init__(self):
        self.providers: List[JobProvider] = []
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Inicializar proveedores disponibles"""
        # JSearch si hay API key
        if settings.JSEARCH_API_KEY:
            jsearch = JSearchProvider(settings.JSEARCH_API_KEY, settings.JSEARCH_HOST)
            self.providers.append(jsearch)
        
        # Siempre incluir mock para desarrollo
        mock = MockProvider()
        self.providers.append(mock)
    
    def add_provider(self, provider: JobProvider):
        """Añadir proveedor personalizado"""
        self.providers.append(provider)
    
    async def get_available_providers(self) -> List[JobProvider]:
        """Obtener lista de proveedores disponibles"""
        available = []
        for provider in self.providers:
            try:
                if await provider.is_available():
                    available.append(provider)
            except Exception:
                # Log error pero continuar con otros proveedores
                continue
        return available
    
    async def search_all_providers(self, query: str, location: Optional[str] = None, 
                                 limit_per_provider: int = 10) -> List[JobItem]:
        """Buscar en todos los proveedores disponibles"""
        available_providers = await self.get_available_providers()
        
        if not available_providers:
            return []
        
        all_jobs = []
        
        # Buscar en paralelo en todos los proveedores
        tasks = []
        for provider in available_providers:
            task = provider.search(query, location, limit_per_provider)
            tasks.append(task)
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Log error pero continuar
                    continue
                elif isinstance(result, list):
                    all_jobs.extend(result)
        
        except Exception:
            # En caso de error general, retornar lo que se pueda
            pass
        
        # Eliminar duplicados por título y empresa
        unique_jobs = []
        seen = set()
        
        for job in all_jobs:
            key = (job.title.lower().strip(), (job.company or "").lower().strip())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs
    
    async def search_best_provider(self, query: str, location: Optional[str] = None, 
                                 limit: int = 10) -> List[JobItem]:
        """Buscar usando el mejor proveedor disponible"""
        available_providers = await self.get_available_providers()
        
        if not available_providers:
            return []
        
        # Priorizar proveedores (JSearch > otros > Mock)
        priority_order = ["jsearch", "linkedin", "computrabajo", "mock"]
        
        sorted_providers = sorted(
            available_providers,
            key=lambda p: priority_order.index(p.name) if p.name in priority_order else 999
        )
        
        # Usar el primer proveedor disponible
        try:
            return await sorted_providers[0].search(query, location, limit)
        except Exception:
            # Si falla, intentar con el siguiente
            if len(sorted_providers) > 1:
                try:
                    return await sorted_providers[1].search(query, location, limit)
                except Exception:
                    return []
            return []


# Instancia global del gestor
job_provider_manager = JobProviderManager()
