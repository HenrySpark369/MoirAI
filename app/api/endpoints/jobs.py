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
