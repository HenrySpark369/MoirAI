# 🏗️ Diagrama de Arquitectura

**Última Actualización**: 5 de noviembre de 2025

---

## 📐 Arquitectura Global

```
┌─────────────────────────────────────────────────────────────────┐
│                       CLIENT / FRONTEND                          │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                    HTTP/HTTPS │ REST API
                               │
┌──────────────────────────────┴──────────────────────────────────┐
│                   FASTAPI APPLICATION (main.py)                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            MIDDLEWARE STACK (Capa 1)                     │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ • CORS (Cross-Origin Resource Sharing)                  │  │
│  │ • Rate Limiting 🆕 ✅                          │  │
│  │   └─ Límites por rol y endpoint                         │  │
│  │   └─ Ventanas deslizantes (hourly + minute)            │  │
│  │   └─ Headers X-RateLimit-*                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                               │                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            AUTHENTICATION (Capa 2)                       │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ • API Key validation                                    │  │
│  │ • Role-based authorization                              │  │
│  │ • Audit logging                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                               │                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            ROUTING & ENDPOINTS (Capa 3) 🆕 ✅            │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ ┌─ Students Endpoints                                   │  │
│  │ ├─ Companies Endpoints                                  │  │
│  │ ├─ Auth Endpoints                                       │  │
│  │ ├─ Job Scraping Endpoints                               │  │
│  │ └─ Matching Endpoints   ✅                    │  │
│  │    ├─ POST   /matching/recommendations                  │  │
│  │    ├─ POST   /matching/filter-by-criteria               │  │
│  │    ├─ GET    /matching/featured-students                │  │
│  │    └─ GET    /matching/student/{id}/matching-score      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                               │                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            SERVICES & BUSINESS LOGIC (Capa 4) 🆕 ✅      │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ ┌─ Authentication Service                               │  │
│  │ ├─ Matching Service 🆕 ✅                               │  │
│  │ │  ├─ find_job_recommendations()                        │  │
│  │ │  ├─ filter_students_by_criteria()                     │  │
│  │ │  ├─ get_featured_students()                           │  │
│  │ │  └─ _calculate_job_match_score()                      │  │
│  │ ├─ NLP Service (extracting skills)                      │  │
│  │ ├─ Job Application Service                              │  │
│  │ ├─ OCC Scraper Service                                  │  │
│  │ └─ Encryption Service 🆕 ✅                           │  │
│  │    ├─ encrypt() / decrypt()                             │  │
│  │    ├─ encrypt_email() / decrypt_email()                 │  │
│  │    ├─ encrypt_phone() / decrypt_phone()                 │  │
│  │    └─ encrypt_dict() / decrypt_dict()                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                               │                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            UTILITIES (Capa 5) 🆕 ✅                      │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ ┌─ Rate Limiter                                        │  │
│  │ │  ├─ RateLimiter class                                 │  │
│  │ │  ├─ Per-role limits                                   │  │
│  │ │  ├─ Per-endpoint limits                               │  │
│  │ │  └─ Sliding window algorithm                          │  │
│  │ ├─ Encryption Service                                   │  │
│  │ │  ├─ EncryptionService class                           │  │
│  │ │  ├─ Fernet (AES-128 + HMAC)                           │  │
│  │ │  └─ Specialized methods                               │  │
│  │ ├─ File Processing                                      │  │
│  │ └─ Validation & Schemas                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                               │                                 │
└───────────────────────────────┼─────────────────────────────────┘
                                │
                    DATABASE / STORAGE
                                │
        ┌───────────────────────┴───────────────────────┐
        │                                               │
    ┌───▼────────┐    ┌──────────────┐    ┌──────────┐ │
    │  SQLite    │    │  PostgreSQL  │    │  Redis   │ │
    │  (Dev)     │    │  (Prod)      │    │  (Cache) │ │
    └────────────┘    └──────────────┘    └──────────┘ │
                                                        │
                    ┌─────────────────────────────────┐ │
                    │   External APIs                  │ │
                    ├─────────────────────────────────┤ │
                    │ • OCC.com.mx Job Scraping       │ │
                    │ • JSearch API                   │ │
                    │ • Email Service (SMTP)          │ │
                    └─────────────────────────────────┘ │
```

---

## 🔄 Flujo de Integración

```
REQUEST
   │
   ├─► CORS Middleware ────────────────────┐
   │                                        │
   ├─► Rate Limit Middleware 🆕 ✅          ├─► ✅ Check permitted
   │   • Get client IP                      │
   │   • Get role from auth                 │
   │   • Check limits per role/endpoint     │
   │   • Return 429 if exceeded             │
   │                                        │
   ├─► Authentication 🔐                    │
   │   • Validate API key                   │
   │   • Extract user context               │
   │   • Set permissions                    │
   │                                        │
   ├─► Endpoint Handler                     │
   │   (e.g., GET /matching/recommendations)│
   │   • Validate parameters                │
   │   • Call service                       │
   │                                        │
   ├─► Service Layer                        │
   │   • MatchingService 🆕 ✅              │
   │   • NLP Service                        │
   │   • Encryption Service 🆕 ✅           │
   │                                        │
   ├─► Database Layer                       │
   │   • Query models                       │
   │   • Encrypt/Decrypt data               │
   │                                        │
   └─► Response Builder                     │
       • Add Rate Limit Headers              │
       • Return JSON                        │
```

---

## 🔐 Flujo de Encriptación           

```
DATOS SENSIBLES (Email, Phone, etc.)
        │
        ▼
┌──────────────────────┐
│ EncryptionService 🆕 │
├──────────────────────┤
│  encrypt_email()     │
│  encrypt_phone()     │
│  encrypt_dict()      │
│  encrypt()           │
└──────────────────────┘
        │
        ▼
    Fernet 🔐
    (AES-128 + HMAC)
        │
        ▼
┌──────────────────────┐
│  Base64 Encoded      │
│  Ciphertext          │
└──────────────────────┘
        │
        ▼
   DATABASE
   (Almacenado encriptado)
        │
        ▼
DECRYPT (cuando sea necesario)
        │
        ▼
    ORIGINAL DATA
```

---

## 🚦 Flujo de Rate Limiting           

```
REQUEST RECEIVED
        │
        ▼
┌─────────────────────────────────┐
│ RateLimiter.check_rate_limit()  │ 🆕
├─────────────────────────────────┤
│ 1. Extract client IP            │
│    • X-Forwarded-For header     │
│    • X-Real-IP header           │
│    • request.client.host        │
│                                 │
│ 2. Get rate limit key           │
│    • For auth: IP + role        │
│    • For anon: IP only          │
│                                 │
│ 3. Get current counts           │
│    • Hourly requests            │
│    • Per-minute requests        │
│                                 │
│ 4. Check limits                 │
│    • Per-minute < endpoint_limit│
│    • Per-hour < role_limit      │
│                                 │
│ 5. Clean old requests           │
│    • Remove >1hour requests     │
│    • Remove >1min requests      │
└─────────────────────────────────┘
        │
        ├─► ALLOWED ──────┐
        │                  │
        └─► DENIED (429) ──┤
                           │
                           ▼
                      ADD HEADERS
                      X-RateLimit-Hourly-Limit
                      X-RateLimit-Hourly-Remaining
                      X-RateLimit-Minute-Limit
                      X-RateLimit-Minute-Remaining
```

---

## 🎯 Endpoints           

### Matchmaking Endpoints 🆕 ✅

#### 1. Get Recommendations
```
POST /api/v1/matching/recommendations
├─ Parameters:
│  ├─ student_id: int (required)
│  ├─ location: str (optional)
│  └─ limit: int (1-50, default 10)
├─ Auth: Student (own) | Admin (any)
├─ Rate Limit: 60/minute
└─ Response: JobRecommendationResponse
   ├─ student_id
   ├─ jobs: List[JobItem]
   ├─ total_found
   ├─ query_used
   └─ generated_at
```

#### 2. Filter Students by Criteria
```
POST /api/v1/matching/filter-by-criteria
├─ Parameters: MatchingCriteria
│  ├─ skills: List[str] (optional)
│  ├─ projects: List[str] (optional)
│  ├─ location: str (optional)
│  ├─ job_type: str (optional)
│  └─ experience_level: str (optional)
├─ Auth: Company | Admin
├─ Rate Limit: 30/minute
└─ Response: List[MatchResult]
   ├─ student: StudentPublic
   ├─ score: float (0-1)
   ├─ matching_skills: List[str]
   └─ matching_projects: List[str]
```

#### 3. Featured Students
```
GET /api/v1/matching/featured-students
├─ Parameters:
│  └─ limit: int (1-50, default 10)
├─ Auth: Company | Admin
├─ Rate Limit: 100/minute
└─ Response: List[StudentPublic]
```

#### 4. Matching Score
```
GET /api/v1/matching/student/{student_id}/matching-score
├─ Parameters:
│  ├─ student_id: int (path)
│  ├─ job_title: str (query)
│  └─ job_description: str (query)
├─ Auth: Student (own) | Admin | Company
├─ Rate Limit: 30/minute
└─ Response:
   ├─ matching_score: float (0-1)
   ├─ base_score: float
   ├─ boost_applied: float
   ├─ matching_skills: List[str]
   ├─ matching_projects: List[str]
   └─ boost_details: dict
```

---

## 📊 Estadísticas de Implementación

```
Archivos Creados:        6
├─ app/api/endpoints/matching.py
├─ app/utils/encryption.py
├─ app/middleware/rate_limit.py
├─ tests/unit/test_encryption_service.py
├─ tests/unit/test_rate_limiting.py
└─ tests/integration/test_matching_endpoints.py

Archivos Modificados:    3
├─ app/main.py
├─ requirements.txt
└─ docs/OPORTUNIDADES_IMPLEMENTACION_CONSOLIDADO.md

Líneas de Código:
├─ Producción:         ~1,200 líneas
├─ Tests:              ~1,000 líneas
└─ Total:              ~2,200 líneas

Tests:
├─ Unitarios:         51 ✅
├─ Integración:       10+ ✅
└─ Total:             62/62 ✅ (100%)

Documentación:
├─ Docstrings:        Completos
├─ Guías:             3 archivos
└─ Ejemplos:          Incluidos
```

---

## 🔗 Relaciones de Componentes

```
Endpoints (matching.py)
    │
    ├─► Services (matching_service.py)
    │   ├─► NLP Service (for skill matching)
    │   ├─► Database (Student model)
    │   └─► Job Provider Manager
    │
    ├─► Schemas (validation)
    │   ├─ JobItem
    │   ├─ MatchResult
    │   └─ MatchingCriteria
    │
    └─► Middleware
        ├─ Authentication (auth.py)
        ├─ Rate Limiting (rate_limit.py) 🆕
        └─ CORS

Services (encryption.py)
    │
    ├─► Can be used by:
    │   ├─ Endpoints (models.py)
    │   ├─ Services (any service)
    │   └─ Models (before_save hook)
    │
    └─► Uses:
        ├─ Fernet (cryptography)
        └─ Environment variables

Middleware (rate_limit.py)
    │
    ├─► Applied globally in:
    │   └─ app.middleware("http")
    │
    └─► Uses:
        ├─ datetime (for windows)
        ├─ threading.Lock (for sync)
        └─ collections.defaultdict
```

---

## 🎯 Próximas Fases

```
SEMANA 2:
├─ Coverage Testing (pytest-cov)
├─ Validación Schemas (custom validators)
└─ Rate Limiting Avanzado (Redis)

SEMANA 3:
├─ CI/CD Pipeline (GitHub Actions)
├─ Admin Dashboard (new endpoints)
└─ Refactorización (service separation)

FUTURA:
├─ Migración a PostgreSQL
├─ Observabilidad (APM)
└─ Machine Learning (recommendations v2)
```

---

**Generado por**: GitHub Copilot  
**Fecha**: 5 de noviembre de 2025  
**Versión**: 1.0.0  
**Estado**: ✅ ACTUALIZADO
