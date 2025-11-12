# 🛠️ PLAN DE IMPLEMENTACIÓN: OCC Scraper Integration

**Estado:** LISTA PARA EJECUCIÓN  
**Estimado:** 3-4 horas de desarrollo  
**Prioridad:** 🔴 CRÍTICA (Bloqueador para Phase 2A Module 5)

---

## 📋 CHECKLIST DE TAREAS

### PASO 1: Refactorización de Servicios (45 min)

#### 1.1 Consolidar job_scraper_worker.py
- [ ] Expandir `JobScraperWorker` para manejar OCC-específico
- [ ] Agregar método `_build_occ_search_url(keyword, location)`
- [ ] Agregar método `_parse_occ_jobs(html) → List[JobOffer]`
- [ ] Integrar con `HTMLParserService` para extracción de skills
- [ ] Agregar timeout handling y retry logic

**Archivo:** `/app/services/job_scraper_worker.py`

```python
# NUEVO MÉTODO
async def scrape_occ_jobs(
    self,
    keyword: str,
    location: Optional[str] = None,
    limit: int = 20
) -> List[JobOffer]:
    """Scrape jobs desde OCC.com.mx"""
    ...

# NUEVO MÉTODO  
async def enrich_job_with_encryption(
    self,
    job: JobOffer,
    encryption_service: EncryptionService
) → JobPosting:
    """Enriquece job y aplica encriptación LFPDPPP"""
    ...
```

#### 1.2 Refactorizar occ_scraper_service.py
- [ ] **MANTENER:** Métodos de parseo HTML
  - `_parse_job_offer(html) → JobOffer`
  - `_extract_salary_range(text)`
  - `_normalize_location(location)`
  - `_extract_skills(description)`

- [ ] **ELIMINAR:** Métodos replicados
  - `search_jobs()` → Usar `JobScraperWorker.scrape_occ_jobs()`
  - `batch_search()` → Usar `scrape_jobs_batch()`

- [ ] **RENOMBRAR:** 
  - `OCCScraper` → `OCCParser` (es solo parser, no scraper)

**Archivo:** `/app/services/occ_scraper_service.py`

---

### PASO 2: Integración de Encriptación (30 min)

#### 2.1 Crear transformador de datos OCC
- [ ] Crear `/app/services/occ_data_transformer.py`

```python
from app.utils.encryption import EncryptionService
from app.models.job_posting import JobPosting
from app.services.occ_scraper_service import JobOffer

class OCCDataTransformer:
    """Transforma datos OCC → JobPosting con encriptación"""
    
    def __init__(self, encryption_service: EncryptionService):
        self.encryption = encryption_service
    
    def transform(self, job_offer: JobOffer) -> JobPosting:
        """
        Convierte JobOffer a JobPosting con encriptación.
        
        Maneja:
        - Encriptación de email y phone
        - Generación de hashes para índices
        - Normalización de datos
        - Validación LFPDPPP
        """
        # 1. Encriptar datos sensibles
        email_encrypted = self.encryption.encrypt_email(
            job_offer.contact_info.get("email", "")
        )
        email_hash = self.encryption._get_hash_email(
            job_offer.contact_info.get("email", "")
        )
        
        # 2. Crear JobPosting
        job_posting = JobPosting(
            external_job_id=job_offer.job_id,
            title=job_offer.title,
            company=job_offer.company,
            location=self._normalize_location(job_offer.location),
            description=job_offer.description or job_offer.full_description,
            email=email_encrypted,
            email_hash=email_hash,
            phone=self.encryption.encrypt_phone(
                job_offer.contact_info.get("phone", "")
            ) if job_offer.contact_info.get("phone") else None,
            phone_hash=self.encryption._get_hash_phone(
                job_offer.contact_info.get("phone", "")
            ) if job_offer.contact_info.get("phone") else None,
            skills=json.dumps(job_offer.skills),
            work_mode=self._map_work_mode(job_offer.work_mode),
            job_type=self._map_job_type(job_offer.job_type),
            salary_min=job_offer.salary_min if hasattr(job_offer, 'salary_min') else None,
            salary_max=job_offer.salary_max if hasattr(job_offer, 'salary_max') else None,
            published_at=job_offer.publication_date or datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        return job_posting
    
    def _normalize_location(self, location: str) -> str:
        """Normaliza ubicación (e.g., "CDMX" → "Ciudad de México")"""
        mappings = {
            "CDMX": "Ciudad de México",
            "DF": "Ciudad de México",
            "MTY": "Monterrey",
            "GDL": "Guadalajara",
            "Remoto": "Remote",
        }
        return mappings.get(location, location)
    
    def _map_work_mode(self, occ_mode: Optional[str]) -> str:
        """Mapea modalidad OCC a nuestro esquema"""
        if not occ_mode:
            return "hybrid"  # default
        
        mode_lower = occ_mode.lower()
        if "remoto" in mode_lower or "remote" in mode_lower:
            return "remoto"
        elif "híbrido" in mode_lower or "hybrid" in mode_lower:
            return "híbrido"
        elif "presencial" in mode_lower or "onsite" in mode_lower:
            return "presencial"
        
        return "hybrid"
    
    def _map_job_type(self, occ_type: Optional[str]) -> str:
        """Mapea tipo de trabajo OCC a nuestro esquema"""
        if not occ_type:
            return "full-time"  # default
        
        type_lower = occ_type.lower()
        if "completo" in type_lower or "full" in type_lower:
            return "full-time"
        elif "parcial" in type_lower or "part" in type_lower:
            return "part-time"
        elif "temporal" in type_lower or "contract" in type_lower:
            return "temporal"
        elif "freelance" in type_lower or "independiente" in type_lower:
            return "freelance"
        
        return "full-time"
```

#### 2.2 Actualizar JobPosting model
- [ ] Verificar que `to_dict_public()` NO expone email/phone
- [ ] Agregar validación de PII en `__setattr__`

**Archivo:** `/app/models/job_posting.py`

```python
def to_dict_public(self) -> dict:
    """Retorna datos públicos sin PII"""
    return {
        "id": self.id,
        "external_job_id": self.external_job_id,
        "title": self.title,
        "company": self.company,
        "location": self.location,
        "description": self.description,
        "skills": json.loads(self.skills) if isinstance(self.skills, str) else self.skills,
        "work_mode": self.work_mode,
        "job_type": self.job_type,
        "salary_info": {
            "min": self.salary_min,
            "max": self.salary_max,
            "currency": self.currency
        } if self.salary_min or self.salary_max else None,
        "published_at": self.published_at.isoformat(),
        "source": self.source,
        # NO INCLUIR: email, phone, email_hash, phone_hash
    }
```

---

### PASO 3: Endpoints API Seguros (45 min)

#### 3.1 Crear rutas de scraping
- [ ] Crear `/app/api/routes/jobs.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from app.core.database import get_session
from app.core.auth import verify_admin_key
from app.services.job_scraper_worker import JobScraperWorker, scrape_jobs_batch
from app.services.occ_data_transformer import OCCDataTransformer
from app.utils.encryption import get_encryption_service
from app.models.job_posting import JobPosting

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])

@router.post("/scrape")
async def scrape_jobs(
    keyword: str = Query(..., min_length=2, max_length=50),
    location: Optional[str] = Query(None, max_length=50),
    limit: int = Query(20, ge=1, le=100),
    admin_key: str = Depends(verify_admin_key),
    session: Session = Depends(get_session),
    encryption_service = Depends(get_encryption_service),
):
    """
    Scrape jobs desde OCC.com.mx
    
    ⚠️ **ADMIN ONLY** - Requiere API key de administrador
    
    Flujo:
    1. Busca jobs en OCC
    2. Parsea datos HTML
    3. Extrae skills con NLP
    4. **Encripta PII (email, phone)**
    5. Deduplica
    6. Almacena en BD
    
    Retorna:
    - total_found: Cantidad de jobs encontrados
    - jobs_stored: Cantidad almacenada (después de deduplicación)
    - duplicates: Cantidad rechazada por duplicación
    """
    
    try:
        # 1. Scrape
        worker = JobScraperWorker()
        raw_jobs = await worker.search_jobs(keyword, location, limit)
        
        if not raw_jobs:
            return {
                "total_found": 0,
                "jobs_stored": 0,
                "duplicates": 0,
                "message": f"No jobs found for '{keyword}' in '{location or 'all locations'}'"
            }
        
        # 2. Transform & Encrypt
        transformer = OCCDataTransformer(encryption_service)
        job_postings = [transformer.transform(job) for job in raw_jobs]
        
        # 3. Store
        stored_count = 0
        duplicate_count = 0
        
        for job_posting in job_postings:
            try:
                # Check if already exists
                existing = session.query(JobPosting).filter(
                    JobPosting.external_job_id == job_posting.external_job_id
                ).first()
                
                if existing:
                    duplicate_count += 1
                    # Update if new data
                    existing.updated_at = datetime.utcnow()
                    session.add(existing)
                else:
                    session.add(job_posting)
                    stored_count += 1
                    
            except Exception as e:
                logger.error(f"Error storing job {job_posting.external_job_id}: {e}")
                continue
        
        session.commit()
        
        return {
            "total_found": len(raw_jobs),
            "jobs_stored": stored_count,
            "duplicates": duplicate_count,
            "keyword": keyword,
            "location": location,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Scraping error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Scraping failed")


@router.get("/search")
async def search_jobs(
    keyword: str = Query(..., min_length=2, max_length=50),
    location: Optional[str] = Query(None, max_length=50),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    """
    Buscar jobs ya almacenados (PUBLIC)
    
    ✅ **SIN autenticación requerida**
    ✅ **SIN PII expuesto** - Usa to_dict_public()
    ✅ **CON rate limiting** - 100 req/minuto
    
    Retorna:
    - jobs: Lista de ofertas (sin email/phone)
    - total: Cantidad total encontrada
    - keyword: Búsqueda realizada
    """
    
    try:
        # 1. Búsqueda con índices optimizados
        stmt = select(JobPosting)
        
        if keyword:
            stmt = stmt.where(JobPosting.description.ilike(f"%{keyword}%"))
        
        if location:
            stmt = stmt.where(JobPosting.location.ilike(f"%{location}%"))
        
        stmt = stmt.limit(limit).order_by(JobPosting.published_at.desc())
        
        jobs = session.exec(stmt).all()
        
        # 2. Convertir a público (sin PII)
        jobs_public = [job.to_dict_public() for job in jobs]
        
        return {
            "keyword": keyword,
            "location": location,
            "total": len(jobs_public),
            "jobs": jobs_public,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.get("/{job_id}")
async def get_job_details(
    job_id: int,
    session: Session = Depends(get_session),
):
    """
    Obtener detalles de una oferta (PUBLIC)
    
    ✅ **SIN PII** - Email/phone NO incluidos
    ✅ **Usa to_dict_public()**
    """
    
    job = session.query(JobPosting).filter(
        JobPosting.id == job_id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job.to_dict_public()
```

---

### PASO 4: Testing (1 hora)

#### 4.1 Tests de integración
- [ ] Crear `/tests/integration/test_occ_scraper_integration.py`

```python
import pytest
from app.services.occ_scraper_service import OCCParser, JobOffer
from app.services.occ_data_transformer import OCCDataTransformer
from app.utils.encryption import EncryptionService
from app.models.job_posting import JobPosting

@pytest.mark.asyncio
async def test_occ_parsing_complete():
    """Test parseo completo de datos OCC"""
    parser = OCCParser()
    
    # HTML real de OCC
    html = load_fixture("occ_job_listing.html")
    
    # Parse
    job_offer = parser._parse_job_offer(html)
    
    # Validar
    assert job_offer.job_id
    assert job_offer.title
    assert job_offer.company
    assert job_offer.description
    assert len(job_offer.skills) > 0

@pytest.mark.asyncio
async def test_encryption_integration():
    """Test que encriptación funciona end-to-end"""
    
    # 1. Crear JobOffer con datos PII
    job_offer = JobOffer(
        job_id="OCC-123",
        title="Python Dev",
        company="TechCorp",
        location="Remote",
        description="Build stuff",
        contact_info={
            "email": "careers@techcorp.com",
            "phone": "+52 55 1234 5678"
        }
    )
    
    # 2. Transform con encriptación
    encryption_service = EncryptionService()
    transformer = OCCDataTransformer(encryption_service)
    job_posting = transformer.transform(job_offer)
    
    # 3. Validar encriptación
    assert job_posting.email.startswith("gAAAAAB")  # Fernet encrypted
    assert job_posting.email_hash  # SHA-256 hash
    assert job_posting.phone.startswith("gAAAAAB")
    assert job_posting.phone_hash
    
    # 4. Validar to_dict_public() NO expone
    public_dict = job_posting.to_dict_public()
    assert "email" not in public_dict
    assert "phone" not in public_dict
    assert "email_hash" not in public_dict
```

#### 4.2 Tests de endpoints
- [ ] Crear `/tests/integration/test_jobs_api_endpoints.py`

```python
@pytest.mark.asyncio
async def test_scrape_jobs_endpoint_requires_admin():
    """POST /api/v1/jobs/scrape requiere admin"""
    
    response = client.post(
        "/api/v1/jobs/scrape?keyword=Python&limit=5",
        headers={"x-api-key": "invalid_key"}
    )
    
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_search_jobs_public_no_pii():
    """GET /api/v1/jobs/search retorna sin PII"""
    
    response = client.get(
        "/api/v1/jobs/search?keyword=Python&limit=5"
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Validar NO PII
    for job in data["jobs"]:
        assert "email" not in job
        assert "phone" not in job
        assert "email_hash" not in job
        assert "phone_hash" not in job
```

---

### PASO 5: Limpieza de Servicios (15 min)

#### 5.1 Revisar y eliminar redundancias
- [ ] Revisar `/app/services/job_application_service.py`
- [ ] Revisar `/app/services/job_background_enrichment.py`
- [ ] ✅ MANTENER: `nlp_service.py` (usado por extracción de skills)
- [ ] ✅ MANTENER: `html_parser_service.py` (usado por muchos)
- [ ] ✅ MANTENER: `matching_service.py` (matchmaking)

#### 5.2 Actualizar imports en main.py
- [ ] Agregar rutas a `app/main.py`

```python
from app.api.routes import jobs  # NUEVO

app.include_router(jobs.router)  # NUEVO
```

---

## 🔍 ARCHIVOS A MODIFICAR

| Archivo | Acción | Líneas | Complejidad |
|---------|--------|--------|------------|
| `job_scraper_worker.py` | Expandir | +150 | Media |
| `occ_scraper_service.py` | Refactor | -200 | Alta |
| `occ_data_transformer.py` | **CREAR** | 150 | Media |
| `job_posting.py` | Validar | +20 | Baja |
| `jobs.py` (rutas) | **CREAR** | 200 | Alta |
| `main.py` | Actualizar | +3 | Baja |
| Tests | **CREAR** | 300+ | Media |

---

## ✅ VALIDACIONES PRE-COMMIT

```bash
# 1. Tests
pytest tests/unit/test_job_scraper_worker.py -v
pytest tests/unit/test_occ_scraper_service.py -v
pytest tests/integration/test_occ_scraper_integration.py -v
pytest tests/integration/test_jobs_api_endpoints.py -v

# 2. Seguridad
grep -r "\.email\s*=" app/  # ¿Email sin encriptar?
grep -r "\.phone\s*=" app/  # ¿Phone sin encriptar?

# 3. Imports
python -m py_compile app/services/*.py
python -m py_compile app/api/routes/*.py

# 4. Lint
pylint app/services/occ_*.py --disable=all --enable=W,E
```

---

## 📊 MÉTRICAS DE ÉXITO

✅ **Completado cuando:**
1. [ ] 39+ tests en test_matching_service.py PASAN (Module 5 compatible)
2. [ ] 0 exposiciones de PII en API responses
3. [ ] Email/phone almacenados encriptados en BD
4. [ ] Scraperintegrado en <500ms por oferta
5. [ ] Rate limiting funcional (SessionManager)
6. [ ] Deduplicación working (< 2% jobs duplicados)
7. [ ] Documentación actualizada
8. [ ] No hay servicios redundantes en `/app/services`

---

**LISTO PARA COMENZAR IMPLEMENTACIÓN** ✅
