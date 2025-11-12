# 🔧 REFACTORING ACTION PLAN - ARCHIVOS Y TESTS

**Objetivo:** Consolidar y refactorizar código unstaged sin crear commits  
**Scope:** OCC scraper integration + encryption + API endpoints  
**Status:** Ready to execute

---

## 📋 ANÁLISIS DE ARCHIVOS UNSTAGED (14 test files, 114+ MB)

### **TEST FILES STATUS**

| Archivo | Líneas | Estado | Acción |
|---------|--------|--------|--------|
| test_upload_resume_update.py | 8,454 | NEW | ⚠️ REVIEW - Posible duplicate |
| test_database_integration.py | Unknown | STUB | ❌ DELETE - Framework only |
| test_html_parser_integration.py | 7,015 | NEW | ✅ KEEP - Needed for scraper |
| test_job_storage_integration.py | 13,804 | NEW | ✅ KEEP - DB integration tests |
| test_matching_endpoints.py | 11,405 | NEW | ✅ KEEP - Module 5 prep |
| test_rate_limiting_integration.py | 11,191 | NEW | ✅ KEEP - Middleware tests |
| test_database_configuration.py | 10,710 | NEW | ✅ KEEP - Config validation |
| test_encryption_service.py | 7,912 | NEW | ✅ KEEP - Encryption tests |
| test_html_parser_service.py | 14,455 | NEW | ✅ KEEP - Parser validation |
| test_job_posting_model.py | 18,435 | NEW | ✅ KEEP - Model validation |
| test_job_scraper_worker.py | 12,468 | NEW | ⚠️ MODIFY - Update for OCC |
| test_matching_service.py | 9,132 | NEW | ✅ KEEP - Algorithm tests |
| test_rate_limiting.py | 10,087 | NEW | ✅ KEEP - Rate limit tests |
| test_rate_limiting_middleware.py | 18,129 | NEW | ✅ KEEP - Middleware tests |
| test_session_manager.py | 8,236 | NEW | ✅ KEEP - Session tests |
| test_suggestions.py | 14,921 | NEW | ❓ REVIEW - Check content |

**Resumen:**
- ✅ 12 archivos MANTENER (están listos)
- ❌ 1 archivo ELIMINAR (stub)
- ⚠️ 3 archivos REVISAR (revisar duplicados)

---

## 🎯 ARCHIVOS PRINCIPALES A REFACTORIZAR

### **1. app/services/job_scraper_worker.py (324 líneas)**

**Estado Actual:** MVP limpio pero sin métodos OCC  
**Acción:** EXPANDIR con métodos OCC-específicos

**Código a AGREGAR (después de línea 100, dentro de `JobScraperWorker` class):**

```python
# ============================================
# OCC-SPECIFIC SCRAPING METHODS
# ============================================

async def scrape_occ_jobs_by_skill(
    self,
    skill: str,
    location: str,
    page: int = 1,
    limit: int = 20,
) -> List[JobPostingMinimal]:
    """
    Scrapes OCC jobs for specific skill/location combination.
    
    Args:
        skill: "python", "javascript", etc.
        location: "ciudad-de-mexico", "remote", etc.
        page: Page number (1-indexed)
        limit: Jobs per page (20-100)
    
    Returns:
        List of JobPostingMinimal objects
    """
    try:
        # Use OCCScraper to fetch offers
        offers = await self._occ_scraper.search_offers(
            keyword=skill,
            location=location,
            page=page,
            limit=limit,
        )
        
        # Transform to JobPostingMinimal
        results = []
        for offer in offers:
            minimal = JobPostingMinimal(
                external_job_id=offer.job_id,
                title=offer.title,
                company=offer.company,
                location=offer.location,
                description=offer.description,
                skills=offer.skills,
                work_mode=offer.work_mode,
                job_type=offer.job_type,
                published_at=offer.published_at,
            )
            results.append(minimal)
        
        return results
        
    except Exception as e:
        self.logger.error(f"Error scraping OCC jobs: {e}")
        return []

async def scrape_occ_job_detail(
    self,
    job_id: str,
) -> Optional[JobPostingMinimal]:
    """
    Fetches detailed information for specific OCC job.
    
    Args:
        job_id: OCC job ID
    
    Returns:
        JobPostingMinimal or None if not found
    """
    try:
        offer = await self._occ_scraper.fetch_job_detail(job_id)
        
        if not offer:
            return None
        
        return JobPostingMinimal(
            external_job_id=offer.job_id,
            title=offer.title,
            company=offer.company,
            location=offer.location,
            description=offer.description,
            skills=offer.skills,
            work_mode=offer.work_mode,
            job_type=offer.job_type,
            published_at=offer.published_at,
        )
        
    except Exception as e:
        self.logger.error(f"Error fetching OCC job detail: {e}")
        return None

async def scrape_occ_batch(
    self,
    skill_location_pairs: List[Tuple[str, str]],
    limit_per_pair: int = 20,
) -> JobScraperResult:
    """
    Batch scrapes multiple skill/location combinations.
    Useful for initial load or full catalog updates.
    
    Args:
        skill_location_pairs: [("python", "mexico-city"), ("javascript", "remote"), ...]
        limit_per_pair: Jobs to fetch per combination
    
    Returns:
        JobScraperResult with aggregated results
    """
    start_time = time.time()
    all_jobs = []
    duplicate_count = 0
    
    for skill, location in skill_location_pairs:
        try:
            jobs = await self.scrape_occ_jobs_by_skill(
                skill=skill,
                location=location,
                limit=limit_per_pair,
            )
            
            # Deduplicate and add
            unique_jobs, dupes = await self.deduplicate_jobs(jobs)
            all_jobs.extend(unique_jobs)
            duplicate_count += dupes
            
        except Exception as e:
            self.logger.warning(f"Error in batch for {skill}/{location}: {e}")
            continue
    
    execution_time = time.time() - start_time
    
    return JobScraperResult(
        query=JobSearchQuery(keyword="batch_occ_scrape"),
        total_found=len(all_jobs) + duplicate_count,
        jobs=all_jobs,
        duplicates_removed=duplicate_count,
        execution_time_ms=int(execution_time * 1000),
    )
```

**Cambios necesarios en INIT:**
```python
def __init__(self, session_manager: SessionManager):
    self.session_manager = session_manager
    self.logger = logging.getLogger(__name__)
    self._seen_job_ids = set()
    # ADD THIS:
    self._occ_scraper = OCCScraper()  # Initialize OCC scraper
```

---

### **2. app/services/occ_scraper_service.py (1372 líneas)**

**Estado Actual:** Bien estructurado pero tiene métodos duplicate de job_scraper_worker.py  
**Acción:** REFACTORIZAR - Eliminar métodos de búsqueda, mantener solo parsing HTML

**Código a ELIMINAR:**
- Lines with `search_jobs()` method (duplicate)
- Lines with `get_by_id()` generic method (duplicate)
- Any generic search logic (duplicado en JobScraperWorker)

**Código a MANTENER/MEJORAR:**
```python
# Keep these:
class OCCScraper:
    # Initialization
    def __init__(self)
    
    # HTML Parsing specialization
    async def fetch_job_detail(self, job_id: str) -> Optional[JobOffer]
    async def parse_job_html(self, html: str) -> JobOffer
    async def extract_salary_range(self, html: str) -> Tuple[Optional[float], Optional[float]]
    async def extract_skills(self, html: str) -> List[str]
    async def extract_job_type(self, html: str) -> str
    async def extract_work_mode(self, html: str) -> str
    
    # Only internal/private methods for scraping
    async def _search_offers(self, ...) -> List[JobOffer]  # PRIVATE
    async def _build_search_url(self, ...)  # PRIVATE
```

**Nueva estructura (refactorizada):**
```python
# 1. Remove generic search (goes to JobScraperWorker)
# 2. Keep HTML parsing (specialized knowledge)
# 3. Add method to transform JobOffer → JobPostingMinimal
# 4. Remove any PII handling (handled in transformer)

class OCCScraper:
    """Specialized OCC.com.mx HTML parser and data extractor."""
    
    async def fetch_and_parse_detail(self, job_id: str) -> Optional[JobOffer]:
        """Fetch and parse single job from OCC."""
        # Implementation stays same
    
    async def parse_job_html(self, html: str) -> JobOffer:
        """Parse HTML into JobOffer model."""
        # Implementation stays same
    
    # All extraction methods (salary, skills, job_type, etc)
    # These stay as-is
```

---

### **3. NEW FILE: app/services/occ_data_transformer.py (150 líneas)**

**Purpose:** Transform JobOffer → encrypted JobPosting  
**Create NEW file:**

```python
"""
OCC Data Transformer Service

Transforms OCC JobOffer models into encrypted JobPosting models
with proper PII handling and validation.
"""

import logging
from typing import Optional
from datetime import datetime

from sqlmodel import Session
from pydantic import ValidationError

from app.models.job_posting import JobPosting
from app.services.encryption_service import EncryptionService
from app.services.occ_scraper_service import JobOffer


logger = logging.getLogger(__name__)


class OCCDataTransformer:
    """
    Transforms OCC JobOffer data into secure JobPosting records.
    
    Responsibilities:
    1. Validate OCC data
    2. Normalize fields
    3. Extract and enrich data (skills via NLP)
    4. Encrypt PII (email, phone)
    5. Prepare for storage
    """
    
    def __init__(self, encryption_service: EncryptionService):
        self.encryption_service = encryption_service
        self.logger = logging.getLogger(__name__)
    
    async def transform(
        self,
        offer: JobOffer,
        db: Session,
    ) -> Optional[JobPosting]:
        """
        Transform JobOffer → JobPosting with encryption.
        
        Args:
            offer: OCC JobOffer data
            db: Database session
        
        Returns:
            JobPosting model ready for storage, or None if validation fails
        """
        try:
            # Validate required fields
            self._validate_offer(offer)
            
            # Check for duplicates
            existing = db.query(JobPosting).filter(
                JobPosting.external_job_id == offer.job_id
            ).first()
            
            if existing:
                self.logger.info(f"Job {offer.job_id} already in DB, updating...")
                return await self._update_existing(existing, offer)
            
            # Encrypt PII
            encrypted_email = None
            email_hash = None
            if offer.contact_email:
                encrypted_email = self.encryption_service.encrypt(offer.contact_email)
                email_hash = self.encryption_service.hash(offer.contact_email)
            
            encrypted_phone = None
            phone_hash = None
            if offer.contact_phone:
                encrypted_phone = self.encryption_service.encrypt(offer.contact_phone)
                phone_hash = self.encryption_service.hash(offer.contact_phone)
            
            # Create JobPosting
            job_posting = JobPosting(
                external_job_id=offer.job_id,
                title=offer.title,
                company=offer.company,
                location=offer.location,
                description=offer.description,
                
                # Encrypted PII
                email=encrypted_email,
                email_hash=email_hash,
                phone=encrypted_phone,
                phone_hash=phone_hash,
                
                # Job metadata
                skills=offer.skills,  # JSON list
                work_mode=offer.work_mode,
                job_type=offer.job_type,
                salary_min=offer.salary_min,
                salary_max=offer.salary_max,
                currency=offer.currency or "MXN",
                
                # Timestamps
                published_at=offer.published_at,
                
                # Source tracking
                source="occ.com.mx",
            )
            
            return job_posting
            
        except ValidationError as e:
            self.logger.error(f"Validation error for job {offer.job_id}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error transforming job {offer.job_id}: {e}")
            return None
    
    def _validate_offer(self, offer: JobOffer) -> None:
        """Validate required fields in JobOffer."""
        if not offer.job_id or not offer.job_id.strip():
            raise ValueError("job_id is required")
        if not offer.title or len(offer.title.strip()) < 4:
            raise ValueError("title must be at least 4 characters")
        if not offer.company or not offer.company.strip():
            raise ValueError("company is required")
        if not offer.location or not offer.location.strip():
            raise ValueError("location is required")
        if not offer.description or len(offer.description.strip()) < 10:
            raise ValueError("description must be at least 10 characters")
        if not (offer.contact_email or offer.contact_phone):
            raise ValueError("At least email or phone must be provided")
    
    async def _update_existing(
        self,
        existing: JobPosting,
        offer: JobOffer,
    ) -> JobPosting:
        """Update existing job posting with new data."""
        # Update fields that might have changed
        existing.title = offer.title
        existing.description = offer.description
        existing.skills = offer.skills
        existing.salary_min = offer.salary_min
        existing.salary_max = offer.salary_max
        existing.updated_at = datetime.utcnow()
        
        return existing
```

---

### **4. NEW FILE: app/api/routes/jobs.py (250 líneas)**

**Purpose:** API endpoints for job scraping (3 total - minimal, secure)  
**Create NEW file:**

```python
"""
Job Posting API Routes

Endpoints for scraping, searching, and retrieving job postings.
Only 3 endpoints:
1. POST /api/v1/jobs/scrape - Admin only, triggers scraping
2. GET /api/v1/jobs/search - Public search (no PII)
3. GET /api/v1/jobs/{id} - Public detail (no PII)
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.api_key_service import verify_api_key
from app.models.job_posting import JobPosting
from app.schemas.job import JobSearchResponse, JobDetailResponse
from app.services.job_scraper_worker import JobScraperWorker, JobSearchQuery
from app.core.session_manager import SessionManager


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


# ============================================
# ADMIN ENDPOINTS
# ============================================

@router.post(
    "/scrape",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger OCC scraping",
    description="Admin-only endpoint to start background scraping job",
)
async def trigger_occ_scraping(
    skill: str = Query(..., min_length=2, max_length=50),
    location: str = Query("remote", min_length=2, max_length=100),
    api_key: str = Depends(verify_api_key),
):
    """
    Trigger scraping for specific skill/location.
    
    Requires valid API key with admin role.
    Returns immediately - scraping happens in background.
    """
    # Verify API key has admin role
    if not api_key.startswith("admin_"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin API key required"
        )
    
    try:
        logger.info(f"Scraping triggered: {skill} in {location}")
        
        # Start background task
        # (Implementation depends on job queue - Celery, APScheduler, etc)
        
        return {
            "status": "queued",
            "skill": skill,
            "location": location,
            "message": "Scraping job queued. Check status later.",
        }
    except Exception as e:
        logger.error(f"Error triggering scrape: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue scraping job"
        )


# ============================================
# PUBLIC ENDPOINTS (Read-only, no PII)
# ============================================

@router.get(
    "/search",
    response_model=JobSearchResponse,
    summary="Search job postings",
    description="Public search endpoint - returns jobs without PII",
)
async def search_jobs(
    keyword: str = Query(..., min_length=2, max_length=100),
    location: Optional[str] = Query(None, max_length=100),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_session),
    session_manager: SessionManager = Depends(),
):
    """
    Search jobs by keyword and location.
    
    Query Parameters:
    - keyword: Search term (required)
    - location: Filter by location (optional)
    - limit: Results per page (1-100, default 20)
    - skip: Pagination offset
    
    Returns: Jobs WITHOUT email/phone (encrypted)
    """
    try:
        # Check rate limit
        await session_manager.check_rate_limit()
        
        # Build query
        query = select(JobPosting)
        
        if keyword:
            query = query.where(
                JobPosting.title.ilike(f"%{keyword}%") |
                JobPosting.description.ilike(f"%{keyword}%") |
                JobPosting.skills.astext.ilike(f"%{keyword}%")
            )
        
        if location:
            query = query.where(JobPosting.location.ilike(f"%{location}%"))
        
        query = query.offset(skip).limit(limit)
        
        jobs = db.exec(query).all()
        total = db.exec(select(JobPosting)).count() if skip == 0 else None
        
        return JobSearchResponse(
            total=total,
            items=jobs,  # to_dict_public() applied automatically via schema
            limit=limit,
            skip=skip,
        )
        
    except Exception as e:
        logger.error(f"Error searching jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search jobs"
        )


@router.get(
    "/{job_id}",
    response_model=JobDetailResponse,
    summary="Get job posting detail",
    description="Get detailed information about a job (no PII)",
)
async def get_job_detail(
    job_id: int,
    db: Session = Depends(get_session),
    session_manager: SessionManager = Depends(),
):
    """
    Retrieve detailed job posting.
    
    Returns: Full job info but with email/phone excluded (encrypted fields)
    """
    try:
        # Check rate limit
        await session_manager.check_rate_limit()
        
        job = db.exec(
            select(JobPosting).where(JobPosting.id == job_id)
        ).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )
        
        return JobDetailResponse(
            **job.to_dict_public()  # Excludes email/phone
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch job"
        )


# ============================================
# HEALTH CHECK
# ============================================

@router.get(
    "/health",
    tags=["health"],
    summary="Health check",
)
async def health_check():
    """Check if jobs service is healthy."""
    return {"status": "healthy"}
```

---

### **5. UPDATE: app/models/job_posting.py**

**Action:** Ensure methods `to_dict_public()` exists and excludes PII

**Verify/Add method:**
```python
def to_dict_public(self) -> dict:
    """
    Convert to dictionary, excluding encrypted PII fields.
    Safe to return in API responses.
    """
    data = self.dict()
    # Remove encrypted fields
    data.pop("email", None)
    data.pop("phone", None)
    # Keep hashes for verification if needed
    # data.pop("email_hash", None)
    # data.pop("phone_hash", None)
    return data
```

---

### **6. CREATE SCHEMA: app/schemas/job.py (80 líneas)**

**Purpose:** Pydantic response schemas for API  
**Create NEW file:**

```python
"""Job API Response Schemas"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class JobDetailResponse(BaseModel):
    """Job posting detail response (no PII)."""
    id: int
    title: str
    company: str
    location: str
    description: str
    skills: Optional[List[str]] = None
    work_mode: Optional[str] = None
    job_type: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: str
    published_at: Optional[datetime] = None
    source: str
    
    class Config:
        from_attributes = True


class JobSearchResponse(BaseModel):
    """Search results response."""
    total: Optional[int] = None
    items: List[JobDetailResponse]
    limit: int
    skip: int
    
    class Config:
        from_attributes = True
```

---

## ✅ TEST FILES ACTION MATRIX

| File | Action | Reason | Priority |
|------|--------|--------|----------|
| test_html_parser_integration.py | KEEP | Validates OCC HTML parsing | HIGH |
| test_job_storage_integration.py | KEEP | Validates DB encryption | HIGH |
| test_matching_endpoints.py | KEEP | Module 5 prerequisite | HIGH |
| test_rate_limiting_integration.py | KEEP | Validates rate limiting | MEDIUM |
| test_database_configuration.py | KEEP | Config validation | MEDIUM |
| test_encryption_service.py | KEEP | Encryption validation | MEDIUM |
| test_html_parser_service.py | KEEP | Parser unit tests | MEDIUM |
| test_job_posting_model.py | KEEP | Model validation | MEDIUM |
| test_job_scraper_worker.py | MODIFY | Add OCC methods tests | HIGH |
| test_matching_service.py | KEEP | Algorithm tests | MEDIUM |
| test_rate_limiting.py | KEEP | Rate limit unit tests | MEDIUM |
| test_rate_limiting_middleware.py | KEEP | Middleware tests | MEDIUM |
| test_session_manager.py | KEEP | Session tests | MEDIUM |
| test_suggestions.py | REVIEW | Check content first | LOW |
| test_upload_resume_update.py | REVIEW | Possible duplicate | LOW |
| test_database_integration.py | DELETE | Framework only, no tests | - |

---

## 🔄 IMPLEMENTATION ORDER

```
1. REFACTOR occ_scraper_service.py
   ├─ Remove generic search methods
   ├─ Keep HTML parsing
   ├─ Verify data extraction accuracy

2. EXPAND job_scraper_worker.py
   ├─ Add OCC-specific methods
   ├─ Test with JobScraperWorker

3. CREATE occ_data_transformer.py
   ├─ Transform + encrypt PII
   ├─ Test encryption end-to-end

4. CREATE app/api/routes/jobs.py
   ├─ 3 endpoints: scrape, search, detail
   ├─ Rate limiting middleware

5. CREATE app/schemas/job.py
   ├─ Response models
   ├─ PII exclusion validation

6. UPDATE app/models/job_posting.py
   ├─ Verify to_dict_public()
   ├─ Test PII exclusion

7. MODIFY test files
   ├─ Update test_job_scraper_worker.py
   ├─ Consolidate as needed
   ├─ Delete test_database_integration.py (stub)

8. RUN TESTS
   ├─ Ensure 274 existing tests pass
   ├─ Run new scraper tests
   ├─ Verify encryption works

9. GIT COMMIT
   ├─ Message: "feat: OCC scraper integration with encryption"
```

---

**END OF REFACTORING ACTION PLAN** 🔧
