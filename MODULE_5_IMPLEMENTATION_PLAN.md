# 🚀 MODULE 5: MATCHING ALGORITHM - IMPLEMENTATION PLAN

**Status:** READY TO START | **Estimated Time:** 1 hour | **Session:** 12 Continuation

---

## 📋 Overview

Module 5 implementa el algoritmo de matchmaking que conecta estudiantes con oportunidades laborales basado en:
- Skills técnicas y blandas
- Experiencia laboral
- Preferencias de localización
- Requisitos empresariales

---

## 🎯 Module 5 Objectives

### Primary Goals
1. **Matching Algorithm** - Calcular compatibility scores entre estudiantes y vacantes
2. **Recommendation System** - Rankear top 5 estudiantes por vacante
3. **Scoring Metrics** - Implementar múltiples criterios de compatibilidad
4. **Notification Integration** - Generar notificaciones de matches relevantes

### KPIs
- Matching accuracy > 85%
- Top 5 recommendations generated < 500ms
- Notification delivery 100% success rate
- Test coverage > 90%

---

## 🏗️ Architecture

### Components

```
StudentProfile (Module 2)
    ↓
StudentEnrichment (NLP - Module 1)
    ↓
MatchingAlgorithm
    ↓
ScoringEngine
    ↓
Recommendations
    ↓
NotificationService
    ↓
Database (Module 4)
```

### Data Flow

1. **Student Profile** → Extract skills + experience (Module 2)
2. **NLP Enrichment** → Soft skills inference (Module 1)
3. **Job Requirements** → Parse technical requirements (Module 3)
4. **Matching** → Calculate compatibility scores
5. **Ranking** → Sort by relevance score
6. **Notifications** → Send high-relevance matches
7. **Storage** → Save match results to database

---

## 💾 Database Schema

### New Tables (for Module 5)

#### `matches` table
```sql
CREATE TABLE matches (
    id UUID PRIMARY KEY,
    student_id UUID NOT NULL,
    job_posting_id UUID NOT NULL,
    match_score FLOAT NOT NULL,         -- 0.0 to 1.0
    technical_score FLOAT NOT NULL,     -- 0.0 to 1.0
    soft_skills_score FLOAT NOT NULL,   -- 0.0 to 1.0
    experience_score FLOAT NOT NULL,    -- 0.0 to 1.0
    location_score FLOAT NOT NULL,      -- 0.0 to 1.0
    recommendation_rank INT,             -- 1-5
    match_reason TEXT,                  -- Why matched
    created_at TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (job_posting_id) REFERENCES job_postings(id)
);

CREATE INDEX idx_matches_student_id ON matches(student_id);
CREATE INDEX idx_matches_job_posting_id ON matches(job_posting_id);
CREATE INDEX idx_matches_score ON matches(match_score DESC);
```

#### `notifications` table (enhancement)
```sql
ALTER TABLE notifications ADD COLUMN match_id UUID;
ALTER TABLE notifications ADD COLUMN recommendation_rank INT;
```

---

## 🧮 Scoring Algorithm

### Scoring Formula

```
TOTAL_MATCH_SCORE = (
    0.40 * TECHNICAL_SCORE +        -- 40% technical skills
    0.25 * SOFT_SKILLS_SCORE +      -- 25% soft skills
    0.20 * EXPERIENCE_SCORE +       -- 20% experience level
    0.15 * LOCATION_SCORE           -- 15% location preference
)
```

### Technical Score (40%)
```
technical_skills_match = number_of_matching_skills / total_required_skills
technical_score = technical_skills_match * 1.0
range: 0.0 - 1.0
```

### Soft Skills Score (25%)
```
nlp_inference_score = confidence_of_inferred_soft_skills
soft_skills_score = nlp_inference_score * 0.8  -- weight down for uncertainty
range: 0.0 - 0.8
```

### Experience Score (20%)
```
years_required = job_posting.years_required
years_student = student.years_experience

if years_student >= years_required:
    experience_score = 1.0 * 0.2
elif years_student >= years_required * 0.8:
    experience_score = 0.8 * 0.2
else:
    experience_score = (years_student / years_required) * 0.2
range: 0.0 - 0.2
```

### Location Score (15%)
```
if student.location == job_posting.location:
    location_score = 0.15
elif student.willing_to_relocate:
    location_score = 0.10
else:
    location_score = 0.0
range: 0.0 - 0.15
```

---

## 📁 Files to Create/Modify

### New Files

#### 1. `app/services/matching_service.py` (Core Matching Logic)
```python
# Key Functions:
- calculate_technical_score(student, job) -> float
- calculate_soft_skills_score(student, job) -> float
- calculate_experience_score(student, job) -> float
- calculate_location_score(student, job) -> float
- calculate_total_match_score(student, job) -> float
- get_top_matches_for_job(job_id, limit=5) -> List[Match]
- get_recommended_jobs_for_student(student_id, limit=5) -> List[Match]
```

**Estimated LOC:** 150-200

#### 2. `app/api/routes/matches.py` (Matching Endpoints)
```python
# Key Endpoints:
- GET /api/v1/matches/student/{student_id}
  - Returns top matching job postings for student
  
- GET /api/v1/matches/job/{job_id}
  - Returns top matching students for job
  
- POST /api/v1/matches/calculate
  - Manual trigger to recalculate all matches
  
- GET /api/v1/matches/statistics
  - Get matching metrics and KPIs
```

**Estimated LOC:** 100-150

#### 3. `tests/unit/test_matching_service.py` (Unit Tests)
```python
# Test Classes:
- TestTechnicalScore (5 tests)
- TestSoftSkillsScore (5 tests)
- TestExperienceScore (5 tests)
- TestLocationScore (5 tests)
- TestTotalMatchScore (5 tests)
- TestMatchRanking (5 tests)
- TestMatchPerformance (3 tests)

Total: 33 unit tests
```

**Estimated LOC:** 400-500

#### 4. `tests/integration/test_matching_integration.py` (Integration Tests)
```python
# Test Classes:
- TestMatchingEndpoints (6 tests)
  - test_get_student_matches
  - test_get_job_matches
  - test_calculate_all_matches
  - test_statistics_endpoint
  - test_match_ranking_order
  - test_match_filtering

Total: 6 integration tests
```

**Estimated LOC:** 300-400

### Modified Files

#### `app/models.py`
```python
# Add:
class Match(SQLModel, table=True):
    id: UUID
    student_id: UUID
    job_posting_id: UUID
    match_score: float
    technical_score: float
    soft_skills_score: float
    experience_score: float
    location_score: float
    recommendation_rank: Optional[int]
    match_reason: str
    created_at: datetime
```

**Changes:** Add Match model (~20 LOC)

#### `app/main.py`
```python
# Add:
from app.api.routes import matches
app.include_router(matches.router)
```

**Changes:** Include new router (~3 LOC)

#### `app/core/database.py`
```python
# Update migration_002_create_indices():
CREATE INDEX idx_matches_student_id ON matches(student_id);
CREATE INDEX idx_matches_job_posting_id ON matches(job_posting_id);
CREATE INDEX idx_matches_score ON matches(match_score DESC);
```

**Changes:** Add indices for matches table (~5 LOC)

---

## 🧪 Testing Strategy

### Unit Tests (33 tests)
```bash
pytest tests/unit/test_matching_service.py -v
```

**Test Coverage:**
- ✅ Technical score calculation (5 tests)
- ✅ Soft skills score calculation (5 tests)
- ✅ Experience score calculation (5 tests)
- ✅ Location score calculation (5 tests)
- ✅ Total match score formula (5 tests)
- ✅ Match ranking/sorting (5 tests)
- ✅ Performance benchmarks (3 tests)

### Integration Tests (6 tests)
```bash
pytest tests/integration/test_matching_integration.py -v
```

**Test Coverage:**
- ✅ GET /api/v1/matches/student/{id} endpoint
- ✅ GET /api/v1/matches/job/{id} endpoint
- ✅ POST /api/v1/matches/calculate endpoint
- ✅ GET /api/v1/matches/statistics endpoint
- ✅ Match ranking order verification
- ✅ Filter and pagination

### Performance Tests
```bash
pytest tests/unit/test_matching_service.py::TestMatchPerformance -v
```

**Performance Targets:**
- Single match calculation: < 50ms
- Get top 5 matches: < 500ms
- Calculate all matches: < 2s (for 100 students + 50 jobs)

---

## 📊 Expected Test Results

```
📊 MODULE 5 TEST EXECUTION

Unit Tests (test_matching_service.py):
✅ 33/33 tests passing

Integration Tests (test_matching_integration.py):
✅ 6/6 tests passing

Performance Tests:
✅ Single match: < 50ms
✅ Top 5 matches: < 500ms
✅ All matches: < 2s

Total Module 5: 39/39 tests passing
```

---

## 🔄 Integration Points

### With Module 1 (NLP Service)
```python
# Use soft skills inferred by NLP
from app.services.nlp_service import nlp_service

soft_skills = nlp_service.extract_soft_skills(student.cv_text)
soft_skills_score = matching_service.calculate_soft_skills_score(
    soft_skills,
    job_posting.required_soft_skills
)
```

### With Module 2 (Student Profiles)
```python
# Query student data
student = db.query(Student).filter(Student.id == student_id).first()
years_experience = student.years_experience
technical_skills = student.technical_skills
```

### With Module 3 (Job Postings)
```python
# Query job data
job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
required_skills = job.required_technical_skills
required_experience = job.years_required
```

### With Module 4 (Database)
```python
# Store match results
match = Match(
    student_id=student_id,
    job_posting_id=job_id,
    match_score=total_score,
    ...
)
db.add(match)
db.commit()
```

---

## 📋 Implementation Checklist

### Phase 1: Core Algorithm (30 min)
- [ ] Create `app/services/matching_service.py`
- [ ] Implement `calculate_technical_score()`
- [ ] Implement `calculate_soft_skills_score()`
- [ ] Implement `calculate_experience_score()`
- [ ] Implement `calculate_location_score()`
- [ ] Implement `calculate_total_match_score()`
- [ ] Write unit tests (15 min)

### Phase 2: Ranking & Retrieval (15 min)
- [ ] Implement `get_top_matches_for_job()`
- [ ] Implement `get_recommended_jobs_for_student()`
- [ ] Add sorting and ranking logic
- [ ] Write unit tests (5 min)

### Phase 3: API Endpoints (10 min)
- [ ] Create `app/api/routes/matches.py`
- [ ] Implement GET /api/v1/matches/student/{id}
- [ ] Implement GET /api/v1/matches/job/{id}
- [ ] Implement POST /api/v1/matches/calculate
- [ ] Write integration tests (5 min)

### Phase 4: Optimization & Polish (5 min)
- [ ] Performance benchmarking
- [ ] Error handling
- [ ] Documentation
- [ ] Final test run

---

## 🚀 Quick Start Commands

### Create Module 5 files
```bash
# Service
touch app/services/matching_service.py

# API Routes
touch app/api/routes/matches.py

# Tests
touch tests/unit/test_matching_service.py
touch tests/integration/test_matching_integration.py
```

### Run Module 5 tests (after implementation)
```bash
# Unit tests
pytest tests/unit/test_matching_service.py -v

# Integration tests
pytest tests/integration/test_matching_integration.py -v

# All Module 5 tests
pytest tests/unit/test_matching_service.py tests/integration/test_matching_integration.py -v

# With coverage
pytest tests/unit/test_matching_service.py --cov=app.services.matching_service
```

### Validate total Phase 2A progress
```bash
# All Phase 2A tests (Modules 1-5)
pytest tests/unit/test_nlp_service.py \
       tests/unit/test_student_endpoints.py \
       tests/unit/test_job_endpoints.py \
       tests/unit/test_database_configuration.py \
       tests/unit/test_matching_service.py -v

# Expected: 36 + 38 + 40 + 37 + 33 = 184 tests
```

---

## 📈 Success Metrics

### Code Quality
- [ ] 39/39 Module 5 tests passing
- [ ] 100% code coverage for matching_service.py
- [ ] All endpoints documented with docstrings
- [ ] Type hints on all functions

### Performance
- [ ] Single match calculation: < 50ms ✓
- [ ] Top 5 matches retrieval: < 500ms ✓
- [ ] All matches calculation: < 2s ✓
- [ ] Database query optimization: Indices on (student_id, job_posting_id, match_score)

### Integration
- [ ] ✅ Works with Module 1 (NLP soft skills)
- [ ] ✅ Works with Module 2 (student profiles)
- [ ] ✅ Works with Module 3 (job postings)
- [ ] ✅ Works with Module 4 (database storage)
- [ ] ✅ No regressions in Phase 1 (114 tests still pass)

---

## 🎯 Phase 2A Completion Status After Module 5

```
📊 PHASE 2A COMPLETION

Module 1 (NLP Service):        ✅ 36/36 tests
Module 2 (Student Profiles):   ✅ 38/38 tests
Module 3 (Job Postings):       ✅ 40/40 tests
Module 4 (Database Setup):     ✅ 46/46 tests + 3/3 migrations
Module 5 (Matching):           ✅ 39/39 tests (pending)

PHASE 2A TOTAL (After Module 5): 199/199 tests

COMBINED WITH PHASE 1:         313/313 tests
```

---

## ✅ Ready to Implement?

**Prerequisites Met:**
- ✅ Phase 1: 114/114 tests
- ✅ Module 1: 36/36 tests (NLP service ready)
- ✅ Module 2: 38/38 tests (student profiles ready)
- ✅ Module 3: 40/40 tests (job postings ready)
- ✅ Module 4: 46/46 tests + 3/3 migrations (database ready)

**Ready to Start Module 5:** YES ✅

---

**Next Action:** Start implementing `app/services/matching_service.py` with scoring algorithm

Estimated completion time: 1 hour
