# 🔍 ANÁLISIS PROFUNDO: Integración del Scraper OCC.com.mx

**Autor:** GitHub Copilot  
**Fecha:** 11 de Noviembre 2025  
**Estado:** En Análisis  
**Commit Base:** bad6bc738a1514c577d9499b61e249bbea6a3cef

---

## 📋 RESUMEN EJECUTIVO

Tu solicitud busca integrar un scraper profesional de OCC.com.mx con análisis de los curl proporcionados. He identificado:

1. **5 tipos de cambios unstaged** necesitados para refactorización
2. **Estructura de datos OCC** completamente mapeada desde los curl
3. **Arquitectura de integración** con tu sistema actual
4. **Eliminación de servicios redundantes** en `/app/services`
5. **Mejoras de seguridad** para no exponer endpoints innecesarios

---

## 🔗 ANÁLISIS DE LOS CURL PROPORCIONADOS

### 1. **Estructura de Solicitudes Identificadas**

```
├── Homepage (GET /)
│   └── Headers: User-Agent, Accept, Cookies CloudFlare
│
├── Búsqueda de Empleos
│   ├── GET /empleos/de-{skill}/en-{location}/
│   │   └── Retorna listado HTML con grid de ofertas
│   │
│   └── POST a collector.occ.com.mx/offer/search (AJAX)
│       ├── Parametro: querystring codificado con búfaer
│       ├── Datos: {keyword, location, page, filters}
│       └── Respuesta: JSON con IDs encriptados
│
├── Detalle de Oferta
│   ├── GET /empleos/de-{skill}/.../{job_id}
│   │   └── Página HTML con detalles
│   │
│   └── POST a collector.occ.com.mx/offer/detail (AJAX)
│       ├── Solicita detalles específicos de oferta
│       └── Respuesta: JSON con datos enriquecidos
│
├── API de Análisis
│   └── POST /ajaxkinesis/basicinfo
│       ├── Headers: X-Requested-With: XMLHttpRequest
│       ├── Cookies CloudFlare (CSRF protection)
│       └── Payload: {oi, icare, icate, iloce, ...}
│
└── Recursos Estáticos
    ├── Fonts: OCCText-*.woff2
    ├── Scripts: jquery.bundle.min.js, site.layout.bundle.min.js
    ├── Stylesheets: modals.min.css
    └── Imágenes: logos de empresas, favicon
```

### 2. **Patrón de Datos de OCC Extraído**

**Estructura de Respuesta (JSON desde collector.occ.com.mx):**

```json
{
  "oi": "external_job_id_hash",
  "icare": "care_code_hash",    // Category
  "icate": "category_hash",      // Subcategory  
  "iloce": "location_hash",      // Location
  "icite": "city_hash",
  "pubdat": "2025-11-06T00:00:00Z",
  "isale": "0",
  "iconttype": "-1",            // Contact type
  "iemptype": "1",              // Employment type
  "dise": "disabled_indicator"
}
```

**Estructura de Datos de Oferta Completa:**

```json
{
  "jobId": "OCC-20834631",
  "title": "Python Developer",
  "company": "Tech Corp",
  "companyVerified": true,
  "location": "Mexico City",
  "salary": {
    "min": 60000,
    "max": 80000,
    "currency": "MXN",
    "period": "monthly"
  },
  "description": "Detailed job description...",
  "requirements": {
    "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
    "experience": "3+ years",
    "education": "Bachelor's degree"
  },
  "workMode": "hybrid",        // remote, hybrid, onsite
  "jobType": "full-time",      // part-time, temporal, freelance
  "publishedAt": "2025-11-06T10:30:00Z",
  "contact": {
    "email": "careers@techcorp.com",
    "phone": "+52 55 1234 5678"
  },
  "benefits": ["Health insurance", "Home office", "Training budget"]
}
```

---

## 🎯 CAMBIOS UNSTAGED RECOMENDADOS

### **1. occ_scraper_service.py** (1372 líneas)
**Estado:** Requiere refactorización  
**Análisis:**
- ✅ HTML parsing funcional
- ✅ Modelos Pydantic correctos
- ❌ Métodos redundantes con job_scraper_worker.py
- ❌ No maneja encriptación de PII
- ❌ Rate limiting básico

**Refactorización Recomendada:**
```python
# MANTENER: Métodos de parseo HTML específicos de OCC
def _parse_job_offer(self, html: str) -> JobOffer
def _extract_salary_range(self, text: str) -> tuple
def _normalize_location(self, location: str) -> str

# ELIMINAR: Duplicados de job_scraper_worker.py
# search_jobs() → usar JobScraperWorker
# batch_search() → usar scrape_jobs_batch()

# INTEGRAR: Encriptación
def _handle_contact_info(self, email: str, phone: str)
  → Retorna {email_encrypted, email_hash, phone_encrypted, phone_hash}
```

### **2. job_scraper_worker.py** (324 líneas)
**Estado:** Requiere expansión  
**Análisis:**
- ✅ Modelo MVP funcional
- ✅ SessionManager integrado
- ✅ Deduplicación implementada
- ❌ Falta parseo específico OCC
- ❌ Sin manejo de encriptación

**Mejoras Necesarias:**
```python
# AGREGAR: Métodos OCC-específicos
async def scrape_occ_jobs(keyword: str) → List[JobOffer]
async def get_job_details(job_id: str) → JobOfferFull

# INTEGRAR: Encriptación automática
async def enrich_and_encrypt(job: JobOffer) → JobPosting
```

### **3. html_parser_service.py**
**Estado:** Puede reutilizarse  
**Análisis:**
- ✅ Extracción de skills funcional
- ✅ Parseo de salarios
- ✅ Detección de modalidad
- ❌ No optimizado para HTML de OCC

### **4. Nuevos Servicios Necesarios**

**A. OCC_BUSINESS_LOGIC.py** - Lógica de negocio de OCC
```python
class OCCDataTransformer:
    """Convierte datos OCC → modelo JobPosting con seguridad"""
    
    def transform_to_job_posting(
        self, 
        raw_occ_data: dict,
        encryption_service: EncryptionService
    ) -> JobPosting:
        # Valida, enriquece y encripta
        pass
    
    def map_work_mode(self, occ_mode: str) -> str:
        # OCC usa códigos, nosotros usamos strings
        pass
    
    def map_job_type(self, occ_type: int) -> str:
        pass
```

**B. OCC_ERROR_HANDLING.py** - Gestión de errores
```python
class OCCScraperException(Exception):
    """Base para excepciones del scraper"""

class OCCRateLimitedException(OCCScraperException):
    """Cuando OCC rechaza por rate limit"""

class OCCDataValidationError(OCCScraperException):
    """Cuando datos no cumplen validaciones"""
```

---

## 📊 MAPA ARQUITECTÓNICO PROPUESTO

```
┌─────────────────────────────────────────────────────────┐
│           API REST - FastAPI Endpoints                   │
│  POST /api/v1/jobs/scrape          (Admin only)         │
│  GET  /api/v1/jobs/search          (Public - Rate Ltd)  │
│  GET  /api/v1/jobs/{id}            (Public - No PII)    │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
┌──────────────────┐   ┌─────────────────────┐
│ JobScraperWorker │   │ MatchingService     │
│ (Orchestration)  │   │ (Busca compatibles) │
└────────┬─────────┘   └─────────────────────┘
         │
    ┌────┴─────────────┐
    ▼                  ▼
┌─────────────┐  ┌──────────────────┐
│ OCCScraper  │  │ HTMLParserService│
│ (HTML/AJAX) │  │ (Extracción)     │
└────────┬────┘  └────────┬─────────┘
         │                │
    ┌────┴────────────────┴──────┐
    ▼                            ▼
┌──────────────────┐  ┌──────────────────────────┐
│ SessionManager   │  │ EncryptionService        │
│ (Rate Limiting)  │  │ (Fernet AES-128)         │
└──────────────────┘  └──────────────────────────┘
         │                      │
         ▼                      ▼
    ┌──────────────────────────────────┐
    │     SQLModel + PostgreSQL        │
    │  - JobPosting (con índices)      │
    │  - Datos encriptados             │
    │  - Hashes para búsqueda          │
    └──────────────────────────────────┘
```

---

## 🔐 CUMPLIMIENTO LFPDPPP (DATOS PERSONALES)

**PII Identificado en OCC:**
1. ✅ Email de contacto
2. ✅ Teléfono de contacto  
3. ⚠️ Nombre de HR/Recruiter (si está visible)
4. ⚠️ Información de empresa que revela ubicación exacta

**Estrategia de Encriptación:**
```python
# ANTES (inseguro)
job_posting.email = "careers@company.com"  # Texto plano ❌

# DESPUÉS (seguro)
job_posting.email = "gAAAAABl...encrypted...dJzQ"  # Fernet ✅
job_posting.email_hash = "9f86d081..."  # SHA-256 para búsqueda ✅

# Búsqueda sin desencriptar
jobs = db.query(JobPosting).filter(
    JobPosting.email_hash == "9f86d081..."
)  # Eficiente y seguro ✅
```

---

## 📝 PLAN DE REFACTORIZACIÓN (PASO A PASO)

### **FASE 1: Análisis y Preparación** (30 min)
- [ ] Crear archivo de análisis (este documento)
- [ ] Revisar todos los unstaged files
- [ ] Documentar decisiones de arquitectura

### **FASE 2: Consolidación de Servicios** (45 min)
- [ ] Integrar occ_scraper_service.py con job_scraper_worker.py
- [ ] Crear OCCDataTransformer para mapeo de datos
- [ ] Implementar manejo de errores OCC-específicos

### **FASE 3: Encriptación de PII** (30 min)
- [ ] Integrar EncryptionService en OCCScraper
- [ ] Actualizar JobPosting storage para datos encriptados
- [ ] Crear índices en email_hash y phone_hash

### **FASE 4: Endpoints API** (45 min)
- [ ] Crear POST /api/v1/jobs/scrape (admin)
- [ ] Crear GET /api/v1/jobs/search (público, sin PII)
- [ ] Implementar rate limiting per-endpoint
- [ ] Crear respuestas API seguras (to_dict_public)

### **FASE 5: Testing e Integración** (1 hora)
- [ ] Tests unitarios de parseo OCC
- [ ] Tests de encriptación
- [ ] Tests de endpoints
- [ ] Validación contra módulo de matching

---

## 🚨 PROBLEMAS IDENTIFICADOS EN CÓDIGO UNSTAGED

### **Problema 1: Duplicación de Lógica**
```python
# occ_scraper_service.py (línea ~150)
async def search_jobs(keyword, limit) → List[JobOffer]

# job_scraper_worker.py (línea ~90)  
async def search_jobs(keyword, limit) → List[JobPostingMinimal]

# SOLUCIÓN: Consolidar en JobScraperWorker con OCCScraper como helper
```

### **Problema 2: Sin Encriptación de Email**
```python
# occ_scraper_service.py - JobOffer
contact_info: Dict = Field(default_factory=dict)
# ❌ Almacena email/phone en texto plano

# SOLUCIÓN: 
contact_info: Dict = Field(default_factory=dict)  # Solo en transit
# DB: usar email_encrypted, email_hash, etc.
```

### **Problema 3: Tests sin Casos de Encriptación**
- test_job_posting_model.py ✅ Tiene tests
- test_html_parser_service.py ✅ Tiene tests  
- test_job_scraper_worker.py ✅ Tiene tests básicos
- ❌ **Falta: test_occ_scraper_integration.py**

---

## ✅ RECOMENDACIONES FINALES

1. **NO crear nuevos endpoints** innecesarios
   - ✅ POST /api/v1/jobs/scrape (admin, programado)
   - ✅ GET /api/v1/jobs/search (público)
   - ❌ NO: GET /api/v1/jobs/raw (expone datos sin encriptar)
   - ❌ NO: POST /api/v1/scrape/manual (poco profesional)

2. **Consolidar servicios:**
   - ✅ Mantener: occ_scraper_service.py (parseo HTML específico)
   - ✅ Mejorar: job_scraper_worker.py (orquestación)
   - ✅ Reutilizar: html_parser_service.py (extracción genérica)
   - ❌ Eliminar: cualquier lógica duplicada

3. **Cumplimiento LFPDPPP:**
   - ✅ Email/phone encriptados en BD
   - ✅ Hashes para búsqueda
   - ✅ No exponer PII en API responses
   - ✅ Audit logging de accesos

4. **Performance:**
   - ✅ SessionManager con rate limiting
   - ✅ Deduplicación en memoria
   - ✅ Índices compuestos en DB
   - ✅ Caché de búsquedas frecuentes

5. **Seguridad:**
   - ✅ Validación de entrada (Pydantic)
   - ✅ User-Agent rotation (SessionManager)
   - ✅ Backoff exponencial en rate limit
   - ✅ Logging de errores sin exponer datos

---

## 📚 DOCUMENTACIÓN RECOMENDADA

Guardar en repositorio:
1. `SCRAPER_INTEGRATION_ANALYSIS.md` ← **ESTE DOCUMENTO**
2. `OCC_SCRAPER_API_REFERENCE.md` ← Especificación de datos
3. `OCC_SCRAPER_IMPLEMENTATION_CHECKLIST.md` ← Tareas
4. `OCC_DATA_ENCRYPTION_GUIDE.md` ← Guía de seguridad

---

**FIN DEL ANÁLISIS**  
Próximo paso: Implementar refactorización siguiendo el plan
