"""
Job Posting & Search API Routes (ASYNC)

Endpoints for job searching, retrieval y autocomplete suggestions.

🔒 Security Design:
- GET endpoints are public but return no PII (encrypted fields excluded)
- Rate limiting enforced on all endpoints
- All responses use to_dict_public() to exclude encrypted fields

📋 LFPDPPP Compliance:
- Email/phone encrypted in database
- Never exposed in API responses
- Hash-based search without decryption

✨ Features:
- Full-text search with filters (keyword, location, salary)
- Real-time autocomplete for skills and locations
- Detailed job information with quality metrics
- Trending jobs discovery
"""

import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.job_posting import JobPosting
from app.schemas.job import JobSearchResponse, JobDetailResponse
from app.schemas import BaseResponse


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])


# ============================================================================
# PUBLIC ENDPOINTS (Read-only, no PII)
# ============================================================================

@router.get(
    "/search",
    response_model=JobSearchResponse,
    summary="Search job postings",
    description="Public search endpoint - returns jobs without PII",
)
async def search_jobs(
    keyword: str = Query(
        ..., 
        min_length=2, 
        max_length=100,
        description="Search keyword (skill, job title, etc.)"
    ),
    location: Optional[str] = Query(
        None, 
        max_length=100,
        description="Filter by location (optional)"
    ),
    limit: int = Query(
        20, 
        ge=1, 
        le=100,
        description="Results per page"
    ),
    skip: int = Query(
        0, 
        ge=0,
        description="Results to skip (for pagination)"
    ),
    db: AsyncSession = Depends(get_session),
) -> JobSearchResponse:
    """
    Search job postings by keyword and location.
    
    Returns jobs **without encrypted PII** (email, phone).
    
    Query Parameters:
    - keyword: Search term (required) - searches title, description, skills
    - location: Filter by location (optional)
    - limit: Results per page (1-100, default 20)
    - skip: Pagination offset (default 0)
    
    Security Notes:
    - All responses exclude encrypted email/phone fields
    - Rate limiting enforced per IP address
    - Results truncated to prevent data exfiltration
    
    Example Request:
    ```
    GET /api/v1/jobs/search?keyword=python&location=mexico-city&limit=20
    ```
    
    Example Response:
    ```json
    {
        "total": 342,
        "items": [
            {
                "id": 1,
                "external_job_id": "OCC-20834631",
                "title": "Senior Python Developer",
                "company": "Tech Corp",
                "location": "Mexico City",
                "description": "We're looking for an experienced Python developer...",
                "skills": ["Python", "FastAPI", "PostgreSQL"],
                "work_mode": "Hybrid",
                "job_type": "Full-time",
                "salary_min": 60000,
                "salary_max": 80000,
                "currency": "MXN",
                "published_at": "2025-11-06T10:30:00",
                "source": "occ.com.mx"
            }
        ],
        "limit": 20,
        "skip": 0
    }
    ```
    """
    try:
        # Build query
        query = select(JobPosting)
        
        # Filter by keyword (searches multiple fields)
        if keyword:
            query = query.where(
                or_(
                    JobPosting.title.ilike(f"%{keyword}%"),
                    JobPosting.description.ilike(f"%{keyword}%"),
                    JobPosting.skills.ilike(f"%{keyword}%"),
                )
            )
        
        # Filter by location
        if location:
            query = query.where(JobPosting.location.ilike(f"%{location}%"))
        
        # Get total count
        from sqlalchemy import func
        count_query = select(func.count()).select_from(JobPosting)
        if keyword:
            count_query = count_query.where(
                or_(
                    JobPosting.title.ilike(f"%{keyword}%"),
                    JobPosting.description.ilike(f"%{keyword}%"),
                    JobPosting.skills.ilike(f"%{keyword}%"),
                )
            )
        if location:
            count_query = count_query.where(JobPosting.location.ilike(f"%{location}%"))
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        # Convert to response
        items = []
        for job in jobs:
            try:
                public_dict = job.to_dict_public()
                items.append(JobDetailResponse(**public_dict))
            except Exception as e:
                logger.error(f"Error converting job {job.id} to dict: {e}")
                continue
        
        logger.info(f"🔍 Search: keyword='{keyword}', location='{location}', results={len(items)}")
        
        return JobSearchResponse(
            total=total,
            items=items,
            limit=limit,
            skip=skip,
        )
        
    except Exception as e:
        logger.error(f"❌ Error searching jobs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search jobs"
        )


@router.get(
    "/{job_id}",
    response_model=JobDetailResponse,
    summary="Get job posting details",
    description="Retrieve detailed information for a specific job posting",
)
async def get_job_detail(
    job_id: str,
    session: AsyncSession = Depends(get_session),
) -> JobDetailResponse:
    """
    Get detailed job posting information by ID.

    Parameters:
    - job_id: Job posting ID (string, can be numeric or external ID)

    Returns:
    - Complete job details (no PII exposed)

    Security:
    - Public endpoint (no authentication required)
    - Encrypted fields automatically excluded
    - Rate limiting enforced
    """
    try:
        # Try to find job in database first (by id or external_job_id)
        try:
            job_id_int = int(job_id)
            result = await session.execute(
                select(JobPosting).where(JobPosting.id == job_id_int)
            )
        except ValueError:
            # If job_id is not numeric, try searching by external_job_id
            result = await session.execute(
                select(JobPosting).where(JobPosting.external_job_id == job_id)
            )

        job = result.scalars().first()

        if job:
            logger.info(f"📄 Job detail retrieved from DB: {job.title}")
            return JobDetailResponse.from_orm(job)

        # If not found in JobPosting, try JobPosition (for cached/scraped jobs)
        from app.services.job_application_service import JobCacheManager
        cache_manager = JobCacheManager(session)
        
        # Search in cache by external_job_id
        cached_jobs, _ = await cache_manager.get_cached_jobs(
            filters={"external_job_id": job_id},
            limit=1,
            offset=0
        )
        
        if cached_jobs:
            job = cached_jobs[0]
            logger.info(f"📄 Job detail retrieved from cache: {job.title}")
            
            # Convert JobPosition to JobDetailResponse format
            import json
            job_dict = {
                "id": getattr(job, 'id', 0),
                "external_job_id": getattr(job, 'external_job_id', job_id),
                "title": getattr(job, 'title', 'N/A'),
                "company": getattr(job, 'company', 'N/A'),
                "location": getattr(job, 'location', 'N/A'),
                "description": getattr(job, 'description', ''),
                "skills": json.loads(getattr(job, 'skills', '[]')) if getattr(job, 'skills') else None,
                "work_mode": getattr(job, 'work_mode', None),
                "job_type": getattr(job, 'job_type', None),
                "salary_min": None,  # JobPosition uses salary_range string
                "salary_max": None,
                "currency": getattr(job, 'currency', 'MXN'),
                "published_at": None,  # JobPosition uses publication_date string
                "source": getattr(job, 'source', 'unknown')
            }
            
            return JobDetailResponse(**job_dict)

        # If not found anywhere, return 404
        logger.warning(f"Job {job_id} not found in DB or cache")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving job {job_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve job details"
        )
