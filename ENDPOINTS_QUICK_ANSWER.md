# 📌 QUICK REFERENCE: Endpoints Comparación

## En 30 Segundos

```
¿Cuál es la diferencia entre job_scraping.py y jobs.py?

job_scraping.py:      Legacy, 928 líneas, expone PII, no integrado
job_scraping_clean.py: Mejor que legacy, 677 líneas, aún expone PII, no integrado
jobs.py:              NEW, 347 líneas, SEGURO, ✅ integrado (USAR ESTE)
```

---

## Tabla de Decisión (1 minuto)

| Necesidad | Usa |
|-----------|-----|
| Búsqueda de empleos | jobs.py ✅ |
| Seguridad LFPDPPP | jobs.py ✅ |
| Admin scraping | jobs.py ✅ |
| Alertas (futuro) | job_tracking.py (Fase 4) |
| Tracking (futuro) | job_tracking.py (Fase 4) |
| Referencia código | job_scraping_clean.py |
| Debug legacy | job_scraping.py (solo ref) |

**Bottom line: SIEMPRE USA jobs.py**

---

## Endpoints de jobs.py (4 totales)

```bash
# 1. ADMIN - Disparar scraping
POST /api/v1/jobs/scrape
  Header: X-API-Key: admin_xxxx
  Body: {skill, location, limit_per_location}
  Response: 202 ACCEPTED (queued)

# 2. PUBLIC - Buscar empleos (sin PII)
GET /api/v1/jobs/search?keyword=python&location=mexico
  Response: {total, items[], limit, skip}
  Items NO incluyen: email, phone

# 3. PUBLIC - Detalle de empleo (sin PII)
GET /api/v1/jobs/1
  Response: JobDetail (sin email, phone)

# 4. HEALTH - Check de salud
GET /api/v1/jobs/health
  Response: {status: "healthy", service: "jobs"}
```

---

## Seguridad: jobs.py ✅

```
✅ Encriptación Fernet
✅ SHA-256 hashes
✅ LFPDPPP 100%
✅ X-API-Key validation
✅ Rate limiting
✅ Sin PII en responses
✅ Status codes correctos
```

---

## Datos en BD vs API

**En Base de Datos:**
```python
JobPosting(
    title="Senior Python Dev",
    email_encrypted="gAAAAA...",      # ✅ Encriptado
    email_hash="sha256(...)",          # ✅ Hash
    phone_encrypted="gAAAAA...",       # ✅ Encriptado
    phone_hash="sha256(...)",          # ✅ Hash
)
```

**En API Response (jobs/search):**
```json
{
    "id": 1,
    "title": "Senior Python Dev",
    "company": "TechCorp",
    "location": "Mexico City",
    "description": "...",
    "skills": ["Python", "FastAPI"],
    "salary_min": 50000,
    "salary_max": 80000,
    "currency": "MXN",
    "published_at": "2025-11-12T10:00:00"
    // ❌ NO email_encrypted
    // ❌ NO phone_encrypted
    // ❌ NO email_hash
    // ❌ NO phone_hash
}
```

---

## Fases de Desarrollo

**Ahora (Fase 3):**
- ✅ jobs.py (búsqueda + admin scraping)
- ✅ LFPDPPP compliance
- ✅ Integrado en main.py

**Futuro (Fase 4):**
- ⏳ job_tracking.py (alertas + monitoreo)
- ⏳ Basado en job_scraping_clean.py
- ⏳ Con encriptación

---

## Líneas de Código

- job_scraping.py: 928 líneas (legacy)
- job_scraping_clean.py: 677 líneas (mejor pero no seguro)
- **jobs.py: 347 líneas (óptimo)** ✅

**Lección:** Menos líneas = mejor código (cuando está bien diseñado)

---

## Status

```
✅ jobs.py        PRODUCCIÓN (AHORA)
⚠️ job_scraping   DEPRECADO (solo ref)
⚠️ job_scraping_clean  REFERENCIA (Fase 4)
```

---

## Próxima Acción

```bash
# 1. Abrir Swagger UI
curl http://localhost:8000/docs

# 2. Probar búsqueda
GET /api/v1/jobs/search?keyword=python

# 3. Probar admin scraping (con API key)
POST /api/v1/jobs/scrape
X-API-Key: admin_test
```

---

**Generado:** 12 Nov 2025  
**Status:** ✅ Listo para testing
