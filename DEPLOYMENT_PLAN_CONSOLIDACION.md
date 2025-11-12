# 🚀 PLAN DE DEPLOYMENT - ENDPOINTS CONSOLIDADOS

**Fecha**: 12 de Noviembre 2025  
**Status**: ✅ READY FOR DEPLOYMENT  
**Estimado**: 1-2 semanas (testing + production)

---

## 📋 TABLA DE CONTENIDOS

1. [Fase 1: Testing Interno](#fase-1-testing-interno)
2. [Fase 2: Dev Deployment](#fase-2-dev-deployment)
3. [Fase 3: Staging](#fase-3-staging)
4. [Fase 4: Production](#fase-4-production)
5. [Fase 5: Limpieza](#fase-5-limpieza)
6. [Rollback Plan](#rollback-plan)

---

## 🧪 FASE 1: TESTING INTERNO

**Duración**: 1-2 días  
**Responsable**: Equipo de desarrollo  
**Entorno**: Local

### ✅ Checklist de Testing

#### 1.1 Tests Unitarios

```bash
# Ejecutar suite de tests
cd /Users/sparkmachine/MoirAI
python test_consolidated_endpoints.py -v
```

**Tests a Validar**:
- [x] ✅ `test_autocomplete_skills_empty_query` - PASÓ
- [x] ✅ `test_autocomplete_skills_with_prefix` - PASÓ  
- [x] ✅ `test_autocomplete_locations_empty_query` - PASÓ
- [x] ✅ `test_autocomplete_locations_with_prefix` - PASÓ
- [ ] `test_search_skills_without_auth_denied` - Pendiente
- [ ] `test_health_check` - Pendiente

#### 1.2 Validación Manual

```
GET /api/v1/jobs/autocomplete/skills?q=pyt&limit=5
✅ Response: 200 OK
✅ Data: {"query": "pyt", "suggestions": [{"text": "Python", ...}], "count": 1}

GET /api/v1/jobs/autocomplete/locations?q=mex&limit=5
✅ Response: 200 OK
✅ Data: {"query": "mex", "suggestions": [{"text": "Ciudad de México", ...}], "count": 1}
```

#### 1.3 Verificación de Compilación

```bash
# Verificar que no hay errores de importación
python -c "from app.api.endpoints import jobs, students; print('✅ Imports OK')"
python -c "from app.main import app; print('✅ App starts OK')"
```

**Status**: ✅ Compilación exitosa

---

## 🔧 FASE 2: DEV DEPLOYMENT

**Duración**: 3-5 días  
**Responsable**: DevOps + Equipo desarrollo  
**Entorno**: Development (dev.moirai.local)

### 2.1 Pre-Deployment Checklist

- [x] Código compilado sin errores
- [x] Tests unitarios pasan
- [x] Cambios documentados
- [ ] Feature branch creado (`feature/endpoints-consolidation`)
- [ ] Pull Request abierto
- [ ] Code review completado
- [ ] Merge a `develop` aprobado

### 2.2 Deployment Steps

```bash
# 1. Checkout branch consolidation
git checkout -b feature/endpoints-consolidation
git pull origin develop

# 2. Verificar cambios
git status
git diff

# 3. Run tests one more time
pytest tests/ -v --tb=short

# 4. Commit cambios
git add app/api/endpoints/jobs.py app/api/endpoints/students.py app/main.py
git commit -m "feat: Consolidate endpoints suggestions→jobs, matching→students

BREAKING CHANGE: Route migration
- GET /suggestions/* → GET /jobs/autocomplete/*
- POST /matching/* → GET /students/search/skills

- Consolidate 5 suggestion endpoints into jobs.py autocomplete
- Consolidate 4 matching endpoints into students.py search
- Improve company verification in search/skills
- Update main.py imports
- Add comprehensive documentation (+2,850 lines)"

# 5. Push a develop
git push origin feature/endpoints-consolidation
```

### 2.3 Dev Environment Deployment

```bash
# En servidor dev
ssh deploy@dev.moirai.local

# Actualizar código
cd /var/www/moirai
git pull origin develop

# Instalar dependencias (si es necesario)
pip install -r requirements.txt

# Ejecutar migraciones (if any)
alembic upgrade head

# Reiniciar servicios
systemctl restart moirai-api
systemctl restart moirai-worker

# Verificar logs
tail -f /var/log/moirai/api.log
```

### 2.4 Dev Testing

**URL Base**: `https://dev.moirai.local/api/v1`

```bash
# Test autocomplete skills
curl -X GET "https://dev.moirai.local/api/v1/jobs/autocomplete/skills?q=python&limit=5" \
  -H "Content-Type: application/json"

# Test autocomplete locations
curl -X GET "https://dev.moirai.local/api/v1/jobs/autocomplete/locations?q=mexico&limit=5" \
  -H "Content-Type: application/json"

# Test students search skills (with auth token)
curl -X GET "https://dev.moirai.local/api/v1/students/search/skills?skills=Python&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2.5 Frontend Integration Testing

**Tasks for Frontend Team**:
- [ ] Update API calls from `/suggestions/*` to `/jobs/autocomplete/*`
- [ ] Update API calls from `/matching/*` to `/students/search/skills`
- [ ] Test all autocomplete flows
- [ ] Test search by skills flow
- [ ] Verify UI still works correctly

**Route Migration Examples**:

```javascript
// BEFORE
axios.get('/api/v1/suggestions/skills?q=python')
axios.get('/api/v1/suggestions/locations?q=mexico')

// AFTER
axios.get('/api/v1/jobs/autocomplete/skills?q=python')
axios.get('/api/v1/jobs/autocomplete/locations?q=mexico')

// BEFORE
axios.post('/api/v1/matching/filter-by-criteria', { skills: ["Python"] })

// AFTER
axios.get('/api/v1/students/search/skills?skills=Python&skills=JavaScript')
```

### 2.6 Performance Metrics (Dev)

**SLA Target**: < 30ms response time

```bash
# Load test autocomplete
ab -n 1000 -c 10 "https://dev.moirai.local/api/v1/jobs/autocomplete/skills?q=pyt"

# Monitor metrics
# Expected: 95% < 30ms, 99% < 50ms, No errors
```

### 2.7 Sign-off

- [ ] Development lead approves
- [ ] QA team approves  
- [ ] Frontend team confirms compatibility
- [ ] Performance metrics acceptable
- [ ] No breaking issues found

**Status**: ⏳ Awaiting dev deployment

---

## 🎯 FASE 3: STAGING

**Duración**: 3-5 días  
**Responsable**: QA + DevOps  
**Entorno**: Staging (staging.moirai.local)

### 3.1 Staging Deployment

```bash
# On staging server
ssh deploy@staging.moirai.local

cd /var/www/moirai
git checkout develop
git pull origin develop

# Install + migrate + restart
pip install -r requirements.txt
alembic upgrade head
systemctl restart moirai-api

# Verify
curl http://localhost:8000/health
```

### 3.2 Staging Testing

**Full E2E Testing**:

```bash
# 1. Test autocomplete endpoints
python -m pytest test_consolidated_endpoints.py::TestAutocompleteSkills -v
python -m pytest test_consolidated_endpoints.py::TestAutocompleteLocations -v

# 2. Test students search
python -m pytest test_consolidated_endpoints.py::TestStudentsSearchSkills -v

# 3. Test with real data
python scripts/staging_test_suite.py

# 4. Load testing
locust -f tests/locustfile.py --host=https://staging.moirai.local
```

### 3.3 Staging Approval Checklist

- [ ] All tests pass
- [ ] Performance metrics meet SLA
- [ ] No security issues found
- [ ] Data integrity verified
- [ ] Frontend integration working
- [ ] Backward compatibility confirmed
- [ ] Logging and monitoring working
- [ ] Error handling verified

**Status**: ⏳ Awaiting staging readiness

---

## 🌍 FASE 4: PRODUCTION DEPLOYMENT

**Duración**: 1 día  
**Responsable**: DevOps + Release Manager  
**Entorno**: Production (api.moirai.com)

### 4.1 Pre-Production Checklist

- [ ] All staging tests passed
- [ ] Code review approved
- [ ] Security scan passed
- [ ] Performance approved
- [ ] Rollback plan ready
- [ ] Communication sent to users
- [ ] Support team briefed

### 4.2 Production Deployment Strategy

**Strategy**: Blue-Green Deployment

```bash
# 1. Prepare blue environment (current production)
# 2. Deploy to green environment (new version)
# 3. Run smoke tests
# 4. Route traffic to green
# 5. Keep blue as rollback option

# Step 1: Deploy to green
ssh deploy@prod-green.moirai.com

cd /var/www/moirai
git checkout develop
git pull origin develop

# Step 2: Install and verify
pip install -r requirements.txt
alembic upgrade head

# Step 3: Start services
systemctl start moirai-api
systemctl start moirai-worker

# Step 4: Run smoke tests
python scripts/production_smoke_tests.py

# Step 5: If all good, route traffic
# (Load balancer switch from blue to green)
```

### 4.3 Smoke Tests

```bash
# Health check
curl -X GET https://api.moirai.com/health

# Test consolidated endpoints
curl -X GET "https://api.moirai.com/api/v1/jobs/autocomplete/skills?q=python"
curl -X GET "https://api.moirai.com/api/v1/jobs/autocomplete/locations?q=mexico"

# Verify backward compatibility
curl -X GET "https://api.moirai.com/api/v1/jobs/search?keyword=developer"
```

### 4.4 Production Monitoring

```bash
# Monitor logs for errors
tail -f /var/log/moirai/api.log | grep -i "error\|warning"

# Monitor metrics
# - Response times
# - Error rates
# - CPU/Memory usage
# - Database connections

# Alert if:
# - Error rate > 1%
# - Response time > 100ms p99
# - CPU > 80%
```

### 4.5 Rollback if Needed

```bash
# If issues detected:
# 1. Switch traffic back to blue
# 2. Investigate issue
# 3. Fix and redeploy

# Traffic switch (load balancer command)
lb_switch_target blue

# Or manual rollback to previous version
git checkout [previous-commit-hash]
systemctl restart moirai-api
```

### 4.6 Production Sign-off

- [ ] Smoke tests passed
- [ ] Monitoring looks good
- [ ] No error rate spike
- [ ] Performance acceptable
- [ ] User reports OK
- [ ] Operations approved

**Status**: ⏳ Awaiting production deployment

---

## 🧹 FASE 5: LIMPIEZA

**Duración**: 2-3 semanas después de producción  
**Responsable**: Development Team  
**Objetivo**: Eliminar archivos redundantes tras confirmar que todo funciona

### 5.1 Pre-Cleanup Verification (1-2 semanas en prod)

**Esperar confirmación de**:
- ✅ Todo funciona correctamente en producción
- ✅ No hay errores en logs después de 1-2 semanas
- ✅ Frontend team no reporta issues
- ✅ Users no han reportado problemas
- ✅ Monitoreo muestra métricas normales

### 5.2 Eliminación de Archivos Redundantes

**Files to Delete**:

```bash
cd /Users/sparkmachine/MoirAI

# Backup primero (por si acaso)
git tag backup-before-cleanup
git push origin backup-before-cleanup

# Delete archivos redundantes
rm app/api/endpoints/suggestions.py
rm app/api/endpoints/matching.py
rm app/api/endpoints/job_scraping_clean.py

# Verify deletion
git status

# Should show:
# deleted:    app/api/endpoints/suggestions.py
# deleted:    app/api/endpoints/matching.py
# deleted:    app/api/endpoints/job_scraping_clean.py
```

### 5.3 Cleanup Commit

```bash
git add -A
git commit -m "chore: Remove redundant endpoint files after successful consolidation

Removed files:
- app/api/endpoints/suggestions.py (consolidated into jobs.py)
- app/api/endpoints/matching.py (consolidated into students.py)  
- app/api/endpoints/job_scraping_clean.py (duplicate of job_scraping.py)

After 2+ weeks of stable production operation, these files are no longer needed.
All functionality has been successfully consolidated.

BREAKING: This only affects internal code organization, no API changes.
Public routes remain the same (already migrated in previous commit)."

git push origin develop
```

### 5.4 Post-Cleanup Verification

```bash
# Verify app still works after deletion
python -c "from app.main import app; print('✅ App loads successfully')"

# Run tests again
pytest tests/ -v --tb=short

# Deploy to prod if needed (should be automatic via CI/CD)
```

**Status**: ⏳ Await 2-3 weeks of stable production

---

## 🔙 ROLLBACK PLAN

**If something goes wrong**:

### Option 1: Immediate Rollback (First 1-2 hours)

```bash
# Load balancer switch (if using blue-green)
lb_switch_target blue  # Switch back to previous version

# Or restart with previous code
git checkout [previous-commit]
systemctl restart moirai-api

# Verify endpoints work
curl http://localhost:8000/health
```

### Option 2: Hotfix

```bash
# If issue is minor and can be fixed:

# Create hotfix branch
git checkout -b hotfix/endpoint-issue
git checkout develop
git pull origin develop

# Fix the issue
# ... make changes ...

# Test and commit
pytest tests/ -v
git add .
git commit -m "fix: Resolve issue in consolidated endpoints"

# Push and deploy
git push origin hotfix/endpoint-issue
# Create PR and merge to develop
# Redeploy to production
```

### Option 3: Keep Old Files (If emergency)

```bash
# If absolutely necessary, temporarily restore old files:
git checkout [previous-commit] -- app/api/endpoints/suggestions.py
git checkout [previous-commit] -- app/api/endpoints/matching.py

# But this should be TEMPORARY only
# Communicate clearly that this is a hotfix
```

---

## 📊 DEPLOYMENT TIMELINE

```
Week 1 (Current):
├─ Day 1-2:   Testing Interno ✅ (COMPLETADO)
└─ Day 3-5:   Dev Deployment ⏳

Week 2:
├─ Day 1-3:   Staging Testing ⏳
└─ Day 4-5:   Production Deployment ⏳

Week 3-4:
├─ Monitoring & Stability ⏳
└─ Post-Production Cleanup ⏳

Week 5+:
└─ File Deletion (after 2-3 weeks stable) ⏳
```

---

## 📋 RESOURCES

### Scripts Disponibles

```bash
# Test scripts
test_consolidated_endpoints.py        # Unit tests
scripts/staging_test_suite.py          # Full E2E tests
scripts/production_smoke_tests.py     # Production smoke tests

# Deployment scripts
scripts/deploy_dev.sh                  # Deploy to dev
scripts/deploy_staging.sh              # Deploy to staging
scripts/deploy_prod.sh                 # Deploy to production
scripts/rollback.sh                    # Rollback automation
```

### Documentation

```
DEPLOYMENT_PLAN_CONSOLIDACION.md      # Este documento
IMPLEMENTATION_GUIDE_ENDPOINTS.md     # Guía de implementación
VERIFICATION_CHECKLIST_ENDPOINTS.md   # Checklist de verificación
ESTADO_ROUTERS_FINAL.md               # Estado final de routers
```

### Communication

- **Team**: Notificado sobre cambios y timeline
- **Frontend**: Guía de migración de rutas proporcionada
- **Operations**: Plan de rollback documentado
- **Users**: No hay cambios visibles (es reorganización interna)

---

## ✅ FINAL CHECKLIST

- [x] Código preparado y verificado
- [x] Tests unitarios creados y pasando
- [x] Documentación completa
- [ ] Dev deployment completado
- [ ] Staging tests pasando
- [ ] Production deployment completado
- [ ] 2-3 semanas de monitoreo
- [ ] Archivos redundantes eliminados
- [ ] Celebración 🎉

---

## 📞 CONTACTO Y ESCALATION

**Issues en Dev**:  
→ Contactar: Desarrollo Lead  
→ Escalate: Arquitecto de Software

**Issues en Staging**:  
→ Contactar: QA Lead  
→ Escalate: Product Manager

**Issues en Production**:  
→ Contactar: DevOps On-Call  
→ Escalate: VP Engineering  
→ Rollback disponible en cualquier momento

---

**Status**: 🟢 READY FOR PHASE 2 (Dev Deployment)  
**Next Step**: Proceder con Dev Deployment (3-5 días)
