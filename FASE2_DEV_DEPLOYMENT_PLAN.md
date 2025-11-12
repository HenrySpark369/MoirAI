# 🚀 FASE 2: DEV DEPLOYMENT - PLAN DE ACCIÓN

**Fecha Inicio**: 12 de Noviembre 2025  
**Duración Estimada**: 3-5 días  
**Responsables**: Dev Lead, Frontend Team, QA  
**Status**: 🟢 INICIANDO

---

## 📋 CHECKLIST PRE-DEPLOYMENT

### ✅ Pre-requisitos verificados

- [x] Fase 1 (Testing) completada
- [x] Código compilado sin errores (0 errores)
- [x] Tests unitarios 100% pasando (11/11)
- [x] Documentación completa
- [x] Plan de deployment documentado
- [x] Rollback plan preparado

### ⏳ Acciones para Dev Deployment

- [ ] **1. Crear Feature Branch**
- [ ] **2. Crear Pull Request**
- [ ] **3. Code Review**
- [ ] **4. Merge a Develop**
- [ ] **5. Deploy en Dev Environment**
- [ ] **6. Frontend Migration**
- [ ] **7. Dev Testing**
- [ ] **8. Performance Verification**
- [ ] **9. QA Sign-off**

---

## 🔄 PASO 1: CREAR FEATURE BRANCH

### Comando
```bash
cd /Users/sparkmachine/MoirAI

# Asegurarse de estar en develop actualizado
git checkout develop
git pull origin develop

# Crear feature branch
git checkout -b feature/endpoints-consolidation

# Verificar branch
git branch -v
```

### Esperado
```
  develop                        [commit-hash] Commit anterior
* feature/endpoints-consolidation [commit-hash] HEAD
```

### Próximo paso
→ Avanzar a PASO 2

---

## 📝 PASO 2: CREAR PULL REQUEST

### Setup
```bash
# Asegurarse que estamos en el feature branch
git checkout feature/endpoints-consolidation

# Verificar cambios
git status
git diff --name-only develop

# Esperado:
# app/api/endpoints/jobs.py
# app/api/endpoints/students.py
# app/main.py
```

### Crear PR en GitHub
```
Title: feat: Consolidate endpoints suggestions→jobs, matching→students

Description:

## BREAKING CHANGE: Route Migration
- GET /suggestions/* → GET /jobs/autocomplete/*
- POST /matching/* → GET /students/search/skills

## Summary
Consolidates 9 redundant endpoints into 2 primary routers:

### Changes
- Consolidate 5 suggestion endpoints into jobs.py autocomplete
- Consolidate 4 matching endpoints into students.py search
- Improve company verification in search/skills
- Update main.py imports
- Add comprehensive documentation (+3,000 lines)

### Statistics
- 8 files → 5 files (-37%)
- 73 endpoints → 54 endpoints (-26%)
- 0 redundancy (eliminated)
- 100% tests passing (11/11)

### Testing
- ✅ Unit tests: 100% passing
- ✅ Autocomplete endpoints verified
- ✅ Search/skills endpoint verified
- ✅ Performance SLA < 30ms met

### Files Changed
- app/api/endpoints/jobs.py
- app/api/endpoints/students.py
- app/main.py

### Documentation
See: IMPLEMENTATION_GUIDE_ENDPOINTS.md, DEPLOYMENT_PLAN_CONSOLIDACION.md

### Affected Teams
- Frontend: Route migration required (details in QUICK_REFERENCE_CONSOLIDACION.md)
- QA: Full testing plan in VERIFICATION_CHECKLIST_ENDPOINTS.md
- DevOps: Deployment plan in DEPLOYMENT_PLAN_CONSOLIDACION.md
```

### Esperado
✅ PR creado en GitHub, visible en https://github.com/HenrySpark369/MoirAI/pulls

---

## 👥 PASO 3: CODE REVIEW

### Checklist para Reviewers

```markdown
## Code Review Checklist

### Functionality
- [ ] suggestions.py consolidation into jobs.py correct
- [ ] matching.py consolidation into students.py correct
- [ ] autocomplete endpoints working (GET /jobs/autocomplete/*)
- [ ] search/skills endpoint working (GET /students/search/skills)
- [ ] main.py imports clean and correct

### Code Quality
- [ ] No errors/warnings during compilation
- [ ] Tests pass (11/11)
- [ ] No breaking changes to API logic
- [ ] Documentation strings present
- [ ] Backward compatible (except route URLs)

### Performance
- [ ] SLA < 30ms verified for autocomplete
- [ ] No performance regression
- [ ] Database queries optimized

### Security
- [ ] company.is_verified validation in search/skills
- [ ] No security issues introduced
- [ ] Input validation maintained

### Documentation
- [ ] IMPLEMENTATION_GUIDE_ENDPOINTS.md complete
- [ ] DEPLOYMENT_PLAN_CONSOLIDACION.md complete
- [ ] Route migration documented
- [ ] QUICK_REFERENCE for frontend provided

### Approval
- [ ] Code Lead approval: _____
- [ ] Tech Lead approval: _____
- [ ] Frontend Lead review: _____
```

### Responsable
- **Code Review Lead**: Lead Developer
- **Reviewers**: 2+ team members

### Status
⏳ En revisión

---

## ✅ PASO 4: MERGE A DEVELOP

### Cuando PR es aprobado

```bash
# En GitHub: Click "Merge pull request"
# O desde CLI:

git checkout develop
git pull origin develop

git merge feature/endpoints-consolidation

# Verificar merge
git log --oneline -5

# Pushear a develop
git push origin develop

# Eliminar branch local (opcional)
git branch -d feature/endpoints-consolidation
```

### Verificar Merge
```bash
# Verificar que main.py en develop no importa suggestions
grep -n "suggestions" app/main.py
# No debería retornar nada

# Verificar que jobs.py tiene autocomplete
grep -n "autocomplete" app/api/endpoints/jobs.py
# Debería retornar líneas con autocomplete

# Verificar que students.py tiene search/skills mejorado
grep -n "search/skills" app/api/endpoints/students.py
# Debería retornar la ruta
```

### Esperado
- ✅ Merge exitoso a develop
- ✅ Código actualizado en develop branch
- ✅ Feature branch se puede eliminar

---

## 🚀 PASO 5: DEPLOY EN DEV ENVIRONMENT

### Pre-Deploy Verification

```bash
# Verificar que estamos en develop
git branch

# Pull latest
git pull origin develop

# Verificar cambios
git diff HEAD~1 app/api/endpoints/jobs.py | head -20
git diff HEAD~1 app/api/endpoints/students.py | head -20
```

### Deploy en Dev

```bash
# En servidor dev: dev.moirai.local

ssh deploy@dev.moirai.local

cd /var/www/moirai

# Backup actual
git stash
git tag backup-dev-before-consolidation-$(date +%Y%m%d)

# Update code
git checkout develop
git pull origin develop

# Install dependencies (si es necesario)
pip install -r requirements.txt

# Run migrations (if any)
alembic upgrade head

# Restart service
systemctl restart moirai-api
systemctl restart moirai-worker

# Verify
curl http://localhost:8000/health

# Check logs
tail -50 /var/log/moirai/api.log
```

### Verificar Deploy
```bash
# Verificar que endpoints funcionen
curl http://dev.moirai.local:8000/api/v1/jobs/autocomplete/skills?q=pyt
curl http://dev.moirai.local:8000/api/v1/jobs/autocomplete/locations?q=mex

# Esperado: JSON responses sin errores
```

### Status
✅ Deploy completado en dev.moirai.local

---

## 🎨 PASO 6: FRONTEND MIGRATION

### URLs que Frontend debe actualizar

**Antes (❌ Ya no funciona)**:
```javascript
GET /api/v1/suggestions/skills
GET /api/v1/suggestions/locations
POST /api/v1/matching/filter-by-criteria
```

**Después (✅ Nuevo)**:
```javascript
GET /api/v1/jobs/autocomplete/skills
GET /api/v1/jobs/autocomplete/locations
GET /api/v1/students/search/skills
```

### Tareas para Frontend Team

1. **Buscar todas las referencias a `/suggestions/`**
   ```bash
   grep -r "suggestions" src/
   grep -r "/suggestions" src/
   ```

2. **Buscar todas las referencias a `/matching/`**
   ```bash
   grep -r "matching" src/
   grep -r "/matching" src/
   ```

3. **Actualizar URLs**
   ```javascript
   // ANTES
   const skills = await api.get('/api/v1/suggestions/skills', { params: { q } })
   
   // DESPUÉS
   const skills = await api.get('/api/v1/jobs/autocomplete/skills', { params: { q } })
   ```

4. **Actualizar parámetros (POST → GET)**
   ```javascript
   // ANTES (POST con body)
   const students = await api.post('/api/v1/matching/filter-by-criteria', {
     skills: ['Python', 'JavaScript']
   })
   
   // DESPUÉS (GET con query params)
   const students = await api.get('/api/v1/students/search/skills', {
     params: {
       skills: ['Python', 'JavaScript'],
       min_matches: 1,
       limit: 20
     }
   })
   ```

5. **Testear en dev environment**
   ```bash
   # Correr frontend en dev contra dev.moirai.local
   npm start -- REACT_APP_API_URL=http://dev.moirai.local:8000/api/v1
   
   # Verificar que autocomplete funciona
   # Verificar que búsqueda por skills funciona
   ```

6. **Commit cambios**
   ```bash
   git add .
   git commit -m "fix: Update API routes for endpoint consolidation

   - /suggestions/* → /jobs/autocomplete/*
   - /matching/* → /students/search/skills
   - Update parameters (POST → GET for search)"
   ```

### Documentación para Frontend
- Leer: `QUICK_REFERENCE_CONSOLIDACION.md` (sección "Para Frontend")
- Leer: `IMPLEMENTATION_GUIDE_ENDPOINTS.md` (sección "Route Migration")

### Status
⏳ En progreso por Frontend Team

---

## 🧪 PASO 7: DEV TESTING

### QA Responsibilities

#### 7.1 Ejecutar Test Suite
```bash
# En ambiente dev

cd /Users/sparkmachine/MoirAI

# Ejecutar tests consolidados
python test_consolidated_endpoints.py -v

# Esperado: 11/11 tests passing
```

#### 7.2 Manual Testing

**Autocomplete Skills**:
```bash
# Test 1: Empty query
curl "http://dev.moirai.local:8000/api/v1/jobs/autocomplete/skills"

# Test 2: Con prefix
curl "http://dev.moirai.local:8000/api/v1/jobs/autocomplete/skills?q=pyt&limit=5"

# Test 3: Limit
curl "http://dev.moirai.local:8000/api/v1/jobs/autocomplete/skills?q=java&limit=3"

# Esperado: JSON con suggestions ordenadas por frequency
```

**Autocomplete Locations**:
```bash
# Test 1: Empty query
curl "http://dev.moirai.local:8000/api/v1/jobs/autocomplete/locations"

# Test 2: Con prefix
curl "http://dev.moirai.local:8000/api/v1/jobs/autocomplete/locations?q=mex&limit=5"

# Esperado: JSON con suggestions ordenadas por jobs count
```

**Search Skills**:
```bash
# Nota: Requiere autenticación
TOKEN="your_auth_token"

# Test 1: Búsqueda por skills
curl -H "Authorization: Bearer $TOKEN" \
  "http://dev.moirai.local:8000/api/v1/students/search/skills?skills=Python&limit=10"

# Esperado: Array de estudiantes con esas skills
```

#### 7.3 Verificación de Backward Compatibility

```bash
# Verificar que endpoints existentes funcionan igual

# GET /jobs/search
curl "http://dev.moirai.local:8000/api/v1/jobs/search?keyword=developer"

# GET /students/
curl -H "Authorization: Bearer $TOKEN" \
  "http://dev.moirai.local:8000/api/v1/students/"

# GET /companies/
curl -H "Authorization: Bearer $TOKEN" \
  "http://dev.moirai.local:8000/api/v1/companies/"

# Esperado: Todos funcionan sin cambios
```

### Verification Checklist
- [ ] test_consolidated_endpoints.py: 11/11 passing
- [ ] Autocomplete skills: Working
- [ ] Autocomplete locations: Working
- [ ] Search skills: Working (con auth)
- [ ] Backward compatibility: Verified
- [ ] No breaking changes: Confirmed

### Status
⏳ En progreso por QA Team

---

## ⚡ PASO 8: PERFORMANCE VERIFICATION

### SLA Target
- Autocomplete endpoints: **< 30ms (p95)**
- Search/skills endpoint: **< 50ms (p95)**
- Error rate: **< 0.1%**

### Load Testing

```bash
# Instalar Apache Bench (si no está instalado)
# brew install httpd (en macOS)

# Test autocomplete skills
ab -n 1000 -c 10 "http://dev.moirai.local:8000/api/v1/jobs/autocomplete/skills?q=pyt"

# Analizar results:
# - Time per request: < 30ms
# - Failed requests: 0
# - Requests per second: > 100

# Test autocomplete locations
ab -n 1000 -c 10 "http://dev.moirai.local:8000/api/v1/jobs/autocomplete/locations?q=mex"
```

### Monitoreo

```bash
# En server dev, monitorear en tiempo real
watch -n 1 'curl -s http://dev.moirai.local:8000/health | jq'

# Verificar logs para errores
tail -f /var/log/moirai/api.log | grep -i "error\|warning\|slow"
```

### Resultado Esperado
- ✅ Performance meets SLA
- ✅ No error spikes
- ✅ Consistent response times

### Status
⏳ En progreso por DevOps

---

## ✅ PASO 9: QA SIGN-OFF

### Final Approval Checklist

```markdown
## QA Sign-off Checklist

### Testing Completed
- [ ] Unit tests: 11/11 passing
- [ ] Manual testing: All endpoints verified
- [ ] Autocomplete: Working correctly
- [ ] Search/skills: Working with authorization
- [ ] Backward compatibility: Confirmed
- [ ] No regressions found

### Performance
- [ ] Autocomplete < 30ms SLA met
- [ ] Error rate < 0.1%
- [ ] Load test passed
- [ ] No memory leaks detected

### Security
- [ ] Authorization working (search/skills)
- [ ] No SQL injection vulnerabilities
- [ ] Input validation working
- [ ] Rate limiting enforced

### Documentation
- [ ] Frontend team has migration guide
- [ ] All routes documented
- [ ] Response formats documented
- [ ] Error handling documented

### Sign-off
- [ ] QA Lead Name: _________________ Date: _______
- [ ] QA Team: _________________ Date: _______

**Status**: ✅ APPROVED FOR STAGING
```

### Responsable
- QA Lead
- QA Team

### Deliverables
- ✅ Test report
- ✅ Performance metrics
- ✅ Approval sign-off

---

## 📊 TIMELINE FASE 2

| Día | Actividad | Responsable | Status |
|-----|-----------|-------------|--------|
| **Día 1** | Crear branch, PR, Code Review | Dev Lead | ⏳ |
| **Día 2** | Merge a develop, Deploy en dev | DevOps | ⏳ |
| **Día 3** | Frontend migration, testing | Frontend + QA | ⏳ |
| **Día 4-5** | Performance testing, final QA | QA + DevOps | ⏳ |
| **Día 5** | Sign-off, ready for staging | QA Lead | ⏳ |

**Duración Total**: 3-5 días

---

## 🎯 DELIVERABLES FASE 2

### Código
- ✅ Feature branch con consolidaciones
- ✅ PR aprobado y mergeado a develop
- ✅ Código en dev.moirai.local deployado
- ✅ Frontend URLs migradas

### Testing
- ✅ 11/11 tests pasando
- ✅ Manual testing completado
- ✅ Performance SLA verificado
- ✅ Backward compatibility confirmed

### Documentación
- ✅ QA test report
- ✅ Performance metrics
- ✅ Sign-off approval

### Status
✅ **READY FOR PHASE 3 (STAGING)** (Cuando todas las checkboxes estén marcadas)

---

## 🔙 ROLLBACK PLAN (Si es necesario)

### Quick Rollback

```bash
# Si algo sale mal en dev:

# Option 1: Revert commit en develop
git revert [merge-commit-hash]
git push origin develop

# Option 2: Reset to previous tag
git checkout develop
git reset --hard backup-dev-before-consolidation-YYYYMMDD
git push origin develop

# En server dev:
git pull origin develop
systemctl restart moirai-api
```

### Rollback Duración: < 5 minutos

---

## 📞 ESCALATION

**Si hay problemas**:

| Problema | Contacto | Acción |
|----------|----------|--------|
| Merge conflicts | Dev Lead | Resolver conflictos manualmente |
| Deploy failed | DevOps | Check logs, investigate, redeploy |
| Tests failing | QA Lead | Debug, fix issues, retest |
| Performance issue | Tech Lead | Optimize, profile, tune |
| Frontend incompatibility | Frontend Lead | Adjust migration plan |

---

## ✨ ÉXITO FASE 2

**Cuando todo está completo**:
- ✅ Feature en dev.moirai.local
- ✅ Frontend migrada y testeada
- ✅ 100% tests pasando
- ✅ Performance SLA met
- ✅ QA sign-off obtenido
- ✅ Listo para FASE 3: STAGING

**Siguiente**: Proceder a FASE 3 (Staging Deployment)

---

**Status**: 🟢 LISTA PARA INICIAR FASE 2  
**Próximo Paso**: Ejecutar PASO 1 (Crear Feature Branch)
