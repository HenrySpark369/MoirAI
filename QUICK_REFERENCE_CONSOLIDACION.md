# ⚡ QUICK REFERENCE: CONSOLIDACIÓN DE ENDPOINTS

**Para**: Developers, QA, DevOps  
**Última actualización**: 12 Nov 2025  
**Leer en**: 5 minutos ⏱️

---

## 🎯 TL;DR (Too Long; Didn't Read)

### Qué Pasó
- 8 files → 5 files (-37%)
- 73 endpoints → 54 endpoints (-26%)
- suggestions.py + job_scraping_clean.py + matching.py = CONSOLIDADOS

### URLs que Cambian (IMPORTANTE PARA FRONTEND)

```
Antes                                    Ahora
────────────────────────────────────────────────────────
GET /suggestions/skills                  GET /jobs/autocomplete/skills
GET /suggestions/locations               GET /jobs/autocomplete/locations
POST /matching/filter-by-criteria        GET /students/search/skills
```

### Timeline
- Week 1: Testing ✅ (DONE)
- Week 2: Dev deployment
- Week 3: Staging
- Week 4: Production
- Week 5-6: Cleanup (eliminar archivos)

---

## 📊 ARCHIVOS MODIFICADOS

### 1️⃣ jobs.py (+2 endpoints)
```python
# NUEVOS ENDPOINTS:
GET /jobs/autocomplete/skills?q=pyt&limit=10
GET /jobs/autocomplete/locations?q=mex&limit=10

# Status: ✅ WORKING
```

### 2️⃣ students.py (1 endpoint mejorado)
```python
# MEJORADO:
GET /students/search/skills?skills=Python&min_matches=1&limit=20
# Ahora valida: company.is_verified == True

# Status: ✅ WORKING
```

### 3️⃣ main.py (imports limpios)
```python
# REMOVIDO:
from app.api.endpoints import suggestions  # ← ELIMINADO
app.include_router(suggestions.router)     # ← ELIMINADO

# Status: ✅ WORKING
```

---

## 🧪 TESTING RÁPIDO

### Verificar que funciona

```bash
# Test 1: Autocomplete Skills
curl -X GET "http://localhost:8000/api/v1/jobs/autocomplete/skills?q=pyt"
# Esperado: { "query": "pyt", "suggestions": [{"text": "Python", ...}] }

# Test 2: Autocomplete Locations
curl -X GET "http://localhost:8000/api/v1/jobs/autocomplete/locations?q=mex"
# Esperado: { "query": "mex", "suggestions": [{"text": "Ciudad de México", ...}] }

# Test 3: Health Check
curl -X GET "http://localhost:8000/health"
# Esperado: { "status": "healthy" }
```

### Run Unit Tests

```bash
python test_consolidated_endpoints.py
# Esperado: ✅ All tests pass
```

---

## 🚀 PARA DEVELOPERS

### Código que cambió

```python
# En jobs.py:
@router.get("/autocomplete/skills")
async def get_skill_suggestions(q: str = Query(""), limit: int = Query(10)):
    # Retorna sugerencias de habilidades
    # Data: COMMON_SKILLS hardcodeada (conectar BD en fase 2)

@router.get("/autocomplete/locations")
async def get_location_suggestions(q: str = Query(""), limit: int = Query(10)):
    # Retorna sugerencias de ubicaciones
    # Data: COMMON_LOCATIONS hardcodeada

# En students.py:
@router.get("/search/skills")
async def search_by_skills(...):
    # MEJORADO: Ahora valida company.is_verified
    # Parámetros: skills (list), min_matches (int), limit (int)
```

### Imports Actualizados

```python
# Viejo (REMOVIDO):
from app.api.endpoints import suggestions
app.include_router(suggestions.router, prefix=settings.API_V1_STR)

# Nuevo (MANTENER):
from app.api.endpoints import jobs
app.include_router(jobs.router, prefix=settings.API_V1_STR)
```

---

## 🎨 PARA FRONTEND

### URLs a Actualizar

```javascript
// ANTES (❌ Ya no funciona)
const skillSuggestions = await axios.get('/api/v1/suggestions/skills', 
  { params: { q: searchTerm, limit: 10 } }
);

// DESPUÉS (✅ Nuevo)
const skillSuggestions = await axios.get('/api/v1/jobs/autocomplete/skills',
  { params: { q: searchTerm, limit: 10 } }
);
```

```javascript
// ANTES (❌ Ya no funciona)
const locations = await axios.get('/api/v1/suggestions/locations',
  { params: { q: searchTerm, limit: 10 } }
);

// DESPUÉS (✅ Nuevo)
const locations = await axios.get('/api/v1/jobs/autocomplete/locations',
  { params: { q: searchTerm, limit: 10 } }
);
```

```javascript
// ANTES (❌ Ya no funciona - POST)
const students = await axios.post('/api/v1/matching/filter-by-criteria',
  { skills: ['Python', 'JavaScript'] }
);

// DESPUÉS (✅ Nuevo - GET con query params)
const students = await axios.get('/api/v1/students/search/skills',
  { params: { 
      skills: ['Python', 'JavaScript'],
      min_matches: 1,
      limit: 20
    }
  }
);
```

### Response Formats

**Autocomplete Skills**:
```json
{
  "query": "pyt",
  "suggestions": [
    {
      "text": "Python",
      "category": "programming",
      "frequency": 450
    }
  ],
  "count": 1
}
```

**Autocomplete Locations**:
```json
{
  "query": "mex",
  "suggestions": [
    {
      "text": "Ciudad de México",
      "normalized": "Mexico City",
      "jobs": 1200
    }
  ],
  "count": 1
}
```

**Students Search/Skills**:
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "skills": ["Python", "JavaScript"],
    "projects": [...],
    "is_active": true
  }
]
```

---

## 🔒 PARA OPS/DEVOPS

### Deployment Commands

```bash
# Dev
git checkout feature/endpoints-consolidation
git pull origin develop
pip install -r requirements.txt
pytest tests/ -v
git push origin feature/endpoints-consolidation
# (create PR, review, merge to develop)

# Staging
ssh deploy@staging.moirai.local
cd /var/www/moirai
git checkout develop && git pull
systemctl restart moirai-api
curl http://localhost:8000/health

# Production
# (same as staging, but with blue-green strategy)
```

### Monitoring

**SLA Target**: 
- Response time: < 30ms (autocomplete), < 50ms (search)
- Error rate: < 0.1%
- Uptime: 99.9%

**Alertas**:
```
IF response_time > 100ms for autocomplete THEN alert
IF error_rate > 1% THEN alert
IF status != healthy THEN alert
```

### Rollback

```bash
# Si algo sale mal:
git revert [commit-hash]
git push origin develop
systemctl restart moirai-api

# O manualmente:
git checkout [previous-working-commit]
systemctl restart moirai-api
```

---

## 🗑️ ARCHIVOS A ELIMINAR (Esperar 2-3 semanas)

```bash
# ⏳ NO ELIMINAR AÚN - Esperar production stable

rm app/api/endpoints/suggestions.py         # After 2-3 weeks
rm app/api/endpoints/matching.py            # After 2-3 weeks
rm app/api/endpoints/job_scraping_clean.py  # After 2-3 weeks

# Guardar backup
git tag backup-before-cleanup
git push origin backup-before-cleanup
```

---

## 🆘 TROUBLESHOOTING

### Problema: "No se encuentra /api/v1/suggestions/skills"
**Solución**: Migrar a `/api/v1/jobs/autocomplete/skills`

### Problema: "Search students no retorna resultados"
**Solución**: Verificar que la empresa sea verified (`company.is_verified == True`)

### Problema: "Autocomplete es muy lento"
**Solución**: Datos en memoria. Conectar con BD en siguiente fase (optimization)

### Problema: "¿Dónde está matching.py?"
**Solución**: Consolidado en `students.py`, usar `/api/v1/students/search/skills`

---

## 📚 LEER MÁS

Documentos completos (si necesitas detalles):

| Necesito | Lee esto |
|----------|----------|
| Implementar | `IMPLEMENTATION_GUIDE_ENDPOINTS.md` |
| Verificar | `VERIFICATION_CHECKLIST_ENDPOINTS.md` |
| Entender todo | `ENDPOINTS_CONSOLIDATION_SUMMARY.md` |
| Referenciar routers | `ESTADO_ROUTERS_FINAL.md` |
| Deploy plan | `DEPLOYMENT_PLAN_CONSOLIDACION.md` |
| Eliminar archivos | `PLAN_ELIMINACION_ARCHIVOS_REDUNDANTES.md` |

---

## ✅ CHECKLIST RÁPIDO

### Developer
- [ ] Leer esta guía ⬅️ YOU ARE HERE
- [ ] Revisar cambios en jobs.py y students.py
- [ ] Ejecutar tests: `python test_consolidated_endpoints.py`
- [ ] Verificar que tu parte compila sin errores

### Frontend Developer
- [ ] Migrar URLs de /suggestions/* a /jobs/autocomplete/*
- [ ] Migrar POST /matching/* a GET /students/search/skills
- [ ] Testear que autocomplete funciona
- [ ] Testear que búsqueda funciona

### QA
- [ ] Ejecutar test_consolidated_endpoints.py
- [ ] Verificar SLA: < 30ms response time
- [ ] Validar autorización en search/skills
- [ ] Aprobar para dev deployment

### DevOps
- [ ] Preparar dev environment
- [ ] Preparar staging environment
- [ ] Preparar rollback procedure
- [ ] Configurar monitoring

---

## 🎯 TIMELINE ACTUAL

```
TODAY (12 Nov)        ✅ Phase 1 Testing - DONE
Next Week (15-19 Nov) ⏳ Phase 2 Dev Deploy
Week After (22 Nov)   ⏳ Phase 3 Staging
Another Week (25 Nov) ⏳ Phase 4 Production
Week 5-6 (>1 Dec)     ⏳ Phase 5 Cleanup
```

---

## 🚀 VAMOS A EMPEZAR

**Próximo paso**: Dev deployment (Phase 2)

1. **Para Developers**: Review de código y testing
2. **Para Frontend**: Migración de rutas
3. **Para QA**: Full testing suite
4. **Para DevOps**: Deployment preparation

**Let's go!** 🎉

---

**Preguntas?** Consultar documentación completa o contactar al team lead.
