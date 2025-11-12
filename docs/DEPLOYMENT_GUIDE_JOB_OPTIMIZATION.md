# 🚀 Guía de Implementación - Optimización de Job Descriptions

**Versión**: 1.0  
**Última actualización**: 6 de noviembre de 2025  
**Estimated time**: 15 minutos

---

## 📋 Quick Start

### Estado Actual
✅ Todo el código ya está implementado y probado.  
⏳ Pendiente: Crear índices en PostgreSQL (1 paso)

---

## Step 1️⃣: Verificar que Todo Está en Lugar

### Verificar cambios en modelos
```bash
grep -n "max_length=500.*index=True" app/models/__init__.py
# Debe mostrar: description: str = Field(max_length=500, index=True, ...)

grep -n "full_description.*Optional" app/models/__init__.py
# Debe mostrar: full_description: Optional[str] = Field(default=None, ...)
```

### Verificar cambios en servicio
```bash
grep -n "description = full_description\[:500\]" app/services/occ_scraper_service.py
# Debe encontrar la línea

grep -n "full_description = full_description$" app/services/occ_scraper_service.py
# Debe mostrar que se guarda la descripción completa
```

### Verificar endpoint
```bash
grep -n "compress.*Query.*True" app/api/endpoints/job_scraping.py
# Debe mostrar el parámetro compress
```

**✅ Resultado esperado**: Todos los grep deben encontrar las líneas

---

## Step 2️⃣: Crear Índices PostgreSQL

### Opción A: Desde Script Python (Recomendado)

```bash
# Ver el SQL que se va a ejecutar
cat migrations_create_indexes.py | tail -50

# Ejecutar el script (solo muestra las instrucciones)
python migrations_create_indexes.py
```

### Opción B: Ejecutar SQL Directamente en psql

```bash
# Conectar a la BD
psql -h localhost -d moirai_db -U postgres

# Ejecutar SQL (copiar desde abajo)
CREATE INDEX IF NOT EXISTS idx_job_description_fulltext 
ON job_positions 
USING GIN (to_tsvector('spanish', COALESCE(description, '')));

CREATE INDEX IF NOT EXISTS idx_job_title_company 
ON job_positions(title, company) 
WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_job_location 
ON job_positions(location) 
WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_job_skills 
ON job_positions(skills) 
WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_job_mode_type 
ON job_positions(work_mode, job_type) 
WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_job_external_id 
ON job_positions(external_job_id, source) 
WHERE is_active = true;

-- Optimizar query planner
ANALYZE job_positions;

-- Verificar índices creados
SELECT indexname FROM pg_indexes 
WHERE tablename = 'job_positions' 
ORDER BY indexname;
```

### Opción C: Usando Alembic (Para CI/CD)

```bash
# Copiar script de migración a directorio Alembic
cp migrations_create_indexes.py alembic/versions/001_fulltext_indexes.py

# Ejecutar migración
alembic upgrade head
```

---

## Step 3️⃣: Verificar Índices Creados

```sql
-- Conectar a la BD
psql -h localhost -d moirai_db -U postgres

-- Listar índices creados
\d job_positions

-- Contar registros (verificar que no hay errores)
SELECT COUNT(*) FROM job_positions;

-- Verificar que la compresión está habilitada
SELECT COUNT(*) FROM job_positions 
WHERE LENGTH(description) > 500;
-- Debe retornar 0 (todas las descripciones <=500 chars)

-- Salir
\q
```

---

## Step 4️⃣: Ejecutar Tests

```bash
# Test de compresión
python test_compression_performance.py

# Test de integración
pytest test_integration_optimization.py -v

# Test del servicio NLP (opcional)
pytest tests/unit/test_nlp_service.py -v
```

**✅ Resultado esperado**:
```
test_compression_performance.py:
  ✅ RÁPIDA: 5.7% reducción
  ✅ MODERADA: 82.8% reducción
  ✅ DETALLADA: 93.3% reducción

test_integration_optimization.py:
  ✅ Test 1: División description/full_description → PASS
  ✅ Test 2: Compresión en tránsito → PASS (56.1% reducción)
  ✅ Test 3: Índices para búsquedas → PASS
  ✅ Test 4: Compatibilidad hacia atrás → PASS
  ✅ Test 5: Parámetro compress → PASS
```

---

## Step 5️⃣: Probar en Local

### Iniciar servidor
```bash
cd /Users/sparkmachine/MoirAI
python -m uvicorn app.main:app --reload --port 8000
```

### Hacer requests de prueba

```bash
# Test 1: Sin compresión
curl "http://localhost:8000/api/v1/job-scraping/search?keyword=Python&compress=false" \
  -H "Content-Type: application/json"

# Test 2: Con compresión (default)
curl "http://localhost:8000/api/v1/job-scraping/search?keyword=Python&compress=true" \
  -H "Content-Type: application/json"

# Test 3: Con full_details (ignora compress)
curl "http://localhost:8000/api/v1/job-scraping/search?keyword=Python&full_details=true" \
  -H "Content-Type: application/json"

# Verificar tamaño de response
curl -I "http://localhost:8000/api/v1/job-scraping/search?keyword=Python&compress=true"
# Ver header: Content-Length
```

---

## Step 6️⃣: Deploy a Producción

### Pre-deploy Checklist

- [ ] Backup de BD
  ```bash
  pg_dump -h prod-db.example.com -d moirai_db > backup_$(date +%Y%m%d_%H%M%S).sql
  ```

- [ ] Revisar cambios
  ```bash
  git diff main origin/main | head -100
  ```

- [ ] Crear feature branch
  ```bash
  git checkout -b feature/job-description-optimization
  git add -A
  git commit -m "feat: optimize job descriptions with split fields and compression"
  ```

- [ ] Push y crear PR
  ```bash
  git push origin feature/job-description-optimization
  # Crear PR en GitHub
  ```

- [ ] Merge after approval
  ```bash
  git checkout main
  git pull origin main
  git merge --ff-only feature/job-description-optimization
  git push origin main
  ```

### Deploy en Staging

```bash
# Stash cambios no comiteados
git stash

# Actualizar código
git pull origin main

# Reinstalar dependencias (por si acaso)
pip install -r requirements.txt

# Crear índices en BD de staging
psql -h staging-db.example.com -d moirai_db -U postgres < <(
  cat migrations_create_indexes.py | grep -A 1000 "CREATE INDEX"
)

# Reiniciar aplicación
systemctl restart moirai-api

# Verificar logs
tail -f /var/log/moirai/api.log
```

### Deploy en Producción

```bash
# Verificar health check
curl https://api.example.com/health
# Debe retornar 200 OK

# Crear índices en prod (durante maintenance window)
psql -h prod-db.example.com -d moirai_db -U postgres < <(
  cat migrations_create_indexes.py | grep -A 1000 "CREATE INDEX"
)

# Monitorear indexación
psql -h prod-db.example.com -d moirai_db -c \
  "SELECT indexname, idx_size FROM pg_indexes WHERE tablename='job_positions'"

# Reiniciar API gradualmente (blue-green)
# 1. Drain connections from 50% of instances
# 2. Deploy new code
# 3. Wait for health checks
# 4. Repeat for remaining instances
```

---

## 🔍 Monitoreo Post-Deploy

### Métricas a Verificar

```bash
# 1. Response time
curl -w "@curl-format.txt" -o /dev/null -s "http://api.example.com/jobs/search?keyword=Python"

# 2. Payload size (con y sin compresión)
curl -I "http://api.example.com/jobs/search?keyword=Python&compress=true" \
  | grep "Content-Length"

curl -I "http://api.example.com/jobs/search?keyword=Python&compress=false" \
  | grep "Content-Length"

# 3. Error rate
grep "ERROR.*job" /var/log/moirai/api.log | wc -l

# 4. Index usage
psql -h prod-db.example.com -d moirai_db -c \
  "SELECT schemaname, tablename, indexname, idx_scan FROM pg_stat_user_indexes WHERE tablename='job_positions';"
```

### Alertas (para configurar en Datadog/CloudWatch)

```yaml
alerts:
  - name: "High compression ratio anomaly"
    condition: "compression_ratio < 70%"
    action: "warn"
  
  - name: "DB index creation failed"
    condition: "index_count != 6"
    action: "critical"
  
  - name: "Job search latency spike"
    condition: "p95_latency > 1000ms"
    action: "warn"
  
  - name: "Truncated descriptions detected"
    condition: "truncated_descriptions > 0"
    action: "critical"
```

---

## ❌ Troubleshooting

### Problema: Index ya existe
```
ERROR: relation "idx_job_description_fulltext" already exists
```
**Solución**: El SQL usa `IF NOT EXISTS`, esto es normal en re-runs. Ignorar.

### Problema: Full text search no funciona
```
ERROR: text search configuration "spanish" does not exist
```
**Solución**: Instalar idioma español en PostgreSQL:
```bash
psql -d moirai_db -c "CREATE TEXT SEARCH DICTIONARY spanish_stem (TEMPLATE=snowball, LANGUAGE=spanish);"
```

### Problema: Compression no reduce tamaño
**Solución**: Verificar que descripciones son >200 chars:
```sql
SELECT COUNT(*) FROM job_positions 
WHERE LENGTH(description) > 200 AND LENGTH(description) < 300;
-- Si es 0, las descripciones son pequeñas
```

### Problema: API retorna error 500 en /search
**Solución**: Verificar que `full_description` column existe:
```sql
SELECT column_name FROM information_schema.columns 
WHERE table_name='job_positions' AND column_name='full_description';
-- Debe retornar una fila
```

---

## 📚 Documentación Completa

Para detalles técnicos, ver:
- **Architectural Overview**: `docs/ARCHITECTURE_DIAGRAM.md`
- **API Reference**: `docs/MATCHING_API_REFERENCE.md`
- **Optimization Details**: `docs/JOB_DESCRIPTION_OPTIMIZATION_FINAL.md`
- **Test Results**: `OPTIMIZATION_SUMMARY.md`

---

## ✅ Checklist Final

- [ ] Código verificado en git
- [ ] Tests pasando (5/5 ✅)
- [ ] Índices creados en PostgreSQL
- [ ] Verificado en staging
- [ ] Monitores configurados
- [ ] Runbook documentado
- [ ] Team notificado
- [ ] Rollback plan comunicado

---

**¿Preguntas?** Revisar los documentos relacionados o contactar al equipo de desarrollo.

**Status**: 🟢 LISTO PARA PRODUCCIÓN
