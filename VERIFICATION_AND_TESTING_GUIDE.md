# 🧪 GUÍA DE VERIFICACIÓN Y TESTING

**Documento:** Testing & Verification Guide  
**Fecha:** 2025-11-18  
**Status:** Ready for Verification

---

## 📋 TABLA DE CONTENIDOS

1. [Verificación Automática](#verificación-automática)
2. [Testing Manual por Rol](#testing-manual-por-rol)
3. [Verificación de Cambios](#verificación-de-cambios)
4. [Validación de Seguridad](#validación-de-seguridad)
5. [Checklist Final](#checklist-final)

---

## 🤖 VERIFICACIÓN AUTOMÁTICA

### Script de Verificación de Frontend

```bash
# Ejecutar verificación de cambios
python3 verify_frontend_adaptation.py

# Salida esperada:
# ✅ VERIFICACIÓN EXITOSA - Frontend adaptado correctamente
# Cambios realizados: 17 | Advertencias: 0
```

**Qué verifica:**
- ✅ Endpoints corregidos en cada archivo
- ✅ Métodos deshabilitados implementados
- ✅ Alternativas correctas implementadas
- ✅ Ningún endpoint antiguo sin cambios

---

### Verificación de Estado Git

```bash
# Verificar estado de cambios
git status

# Cambios esperados en staging:
# Modified: app/frontend/static/js/auth-manager.js
# Modified: app/frontend/static/js/pages/applications.js
# Modified: app/frontend/static/js/pages/dashboard.js
# Modified: app/frontend/static/js/pages/jobs-search.js
# Modified: app/frontend/static/js/pages/company-search.js
# Modified: app/frontend/static/js/pages/login.js
# New files: verify_frontend_adaptation.py, ...

# Backend DEBE estar intacto:
git diff app/main.py
git diff app/api/endpoints/admin.py
git diff app/api/endpoints/auth.py
# Salida esperada: (empty)
```

---

## 👤 TESTING MANUAL POR ROL

### 1. Testing Estudiante

**Prerequisitos:**
- [ ] Aplicación ejecutándose en http://localhost:8000
- [ ] Base de datos inicializada
- [ ] Usuario estudiante de prueba creado

**Flujo de Testing:**

```bash
# Paso 1: Login
1. Ir a http://localhost:8000/login
2. Ingresar credentials de estudiante
3. Clickear "Login"
   ✅ Esperado: Dashboard carga sin errores 404

# Paso 2: Ver Aplicaciones
1. Clickear "Mis Aplicaciones"
2. Esperar a que cargue la lista
   ✅ Esperado: GET /students/my-applications (NO /applications)
   ✅ Esperado: Lista de aplicaciones se muestra

# Paso 3: Ver Recomendaciones
1. En dashboard, buscar sección "Recomendaciones"
2. Verificar que cargue la lista
   ✅ Esperado: GET /students/recommendations (NO /matching/student/...)
   ✅ Esperado: Empleos recomendados se muestran

# Paso 4: Buscar Empleos
1. Clickear "Buscar Empleos"
2. Ingresar criterio de búsqueda
3. Clickear "Buscar"
   ✅ Esperado: GET /job-scraping/trending-jobs (NO /jobs/trending-jobs)
   ✅ Esperado: Resultados se cargan

# Paso 5: Ver Trending Jobs
1. En la sección inicial, verificar "Trending"
   ✅ Esperado: GET /job-scraping/trending-jobs carga
   ✅ Esperado: Top jobs se muestran

# Verificar Consola del Navegador
1. Abrir DevTools (F12)
2. Ir a pestaña "Console"
3. Buscar errores 404
   ✅ Esperado: CERO errores 404 relacionados a endpoints
   ✅ Esperado: Pueden haber warnings de endpoints deshabilitados (es normal)
```

**Resultados Esperados:**
- ✅ Dashboard carga sin errores
- ✅ Todas las secciones cargan datos
- ✅ NO hay errores 404 en endpoints principales
- ✅ Console muestra warnings de endpoints deshabilitados (normal)

---

### 2. Testing Empresa

**Prerequisitos:**
- [ ] Empresa de prueba creada
- [ ] Empresa verificada en admin

**Flujo de Testing:**

```bash
# Paso 1: Login
1. Ir a http://localhost:8000/login
2. Ingresar credentials de empresa
3. Clickear "Login"
   ✅ Esperado: Dashboard carga sin errores 404

# Paso 2: Buscar Candidatos
1. Clickear "Buscar Candidatos"
2. Esperar a que cargue lista inicial
   ✅ Esperado: GET /students/search/skills (NO /matching/featured-students)
   ✅ Esperado: Lista de estudiantes se muestra

# Paso 3: Filtrar por Skills
1. Ingresar skill (ej: "Python")
2. Clickear buscar
   ✅ Esperado: GET /companies/{company_id}/search-students
   ✅ Esperado: Resultados filtrados se muestran

# Paso 4: Ver KPIs
1. En dashboard, buscar sección "KPIs"
2. Verificar métricas
   ✅ Esperado: GET /admin/analytics/kpis cargue (si empresa es admin)
   ✅ Esperado: Métricas se muestren

# Verificar Consola del Navegador
1. Abrir DevTools (F12)
2. Ir a pestaña "Console"
   ✅ Esperado: CERO errores 404
   ✅ Esperado: Warnings de endpoints deshabilitados (normal)
```

**Resultados Esperados:**
- ✅ Dashboard carga sin errores
- ✅ Búsqueda de candidatos funciona
- ✅ Filtros funcionan
- ✅ NO hay errores 404 en endpoints principales

---

### 3. Testing Admin

**Prerequisitos:**
- [ ] Usuario admin creado
- [ ] Acceso a dashboard admin

**Flujo de Testing:**

```bash
# Paso 1: Login
1. Ir a http://localhost:8000/login
2. Ingresar credentials de admin
3. Clickear "Login"
   ✅ Esperado: Dashboard admin carga sin errores 404

# Paso 2: Ver KPIs
1. En dashboard admin, buscar "KPIs"
2. Verificar métricas
   ✅ Esperado: GET /admin/analytics/kpis (NO /admin/kpis)
   ✅ Esperado: Métricas se muestran

# Paso 3: Ver Auditoría
1. Clickear "Auditoría" o "Activity Log"
2. Esperar a que cargue logs
   ✅ Esperado: GET /admin/audit-log (NO /admin/activity-log)
   ✅ Esperado: Logs se muestran

# Paso 4: Gestionar Usuarios
1. Ir a sección "Usuarios"
2. Ver lista de usuarios
   ✅ Esperado: GET /admin/users carga
   ✅ Esperado: Lista de usuarios se muestra

# Verificar Consola del Navegador
1. Abrir DevTools (F12)
2. Ir a pestaña "Console"
   ✅ Esperado: CERO errores 404
   ✅ Esperado: Warnings de endpoints deshabilitados (normal)
```

**Resultados Esperados:**
- ✅ Dashboard admin carga sin errores
- ✅ KPIs se cargan correctamente
- ✅ Auditoría se carga correctamente
- ✅ Usuarios se gestionen
- ✅ NO hay errores 404 en endpoints principales

---

## 📝 VERIFICACIÓN DE CAMBIOS

### Verificar cada archivo modificado

```bash
# auth-manager.js
git diff app/frontend/static/js/auth-manager.js | grep -A 5 "refreshToken\|changePassword\|requestPasswordReset\|resetPassword"
# ✅ Esperado: Todos deshabilitados con DESHABILITADO en comentario

# applications.js
git diff app/frontend/static/js/pages/applications.js | grep "students/my-applications"
# ✅ Esperado: Cambio de /applications a /students/my-applications

# jobs-search.js
git diff app/frontend/static/js/pages/jobs-search.js | grep "job-scraping"
# ✅ Esperado: Cambio de /jobs/trending-jobs a /job-scraping/trending-jobs

# dashboard.js
git diff app/frontend/static/js/pages/dashboard.js | grep -E "students/recommendations|students/my-applications|admin/analytics/kpis|admin/audit-log|DESHABILITADO"
# ✅ Esperado: 4 cambios de ruta + 3 deshabilitaciones

# company-search.js
git diff app/frontend/static/js/pages/company-search.js | grep -E "students/search|companies/.*search-students|DESHABILITADO"
# ✅ Esperado: 2 cambios + 1 deshabilitación

# login.js
git diff app/frontend/static/js/pages/login.js | grep -E "forgot-password|DESHABILITADO"
# ✅ Esperado: 1 deshabilitación
```

### Verificar Backend Intacto

```bash
# Confirmar que backend NO tiene cambios
git status app/main.py
# ✅ Esperado: sin cambios o solo en staging (por revert)

git status app/api/endpoints/admin.py
# ✅ Esperado: sin cambios

git status app/api/endpoints/auth.py
# ✅ Esperado: sin cambios

# Ver diff de archivos backend
git diff HEAD -- app/main.py
git diff HEAD -- app/api/endpoints/admin.py
# ✅ Esperado: (empty)
```

---

## 🔐 VALIDACIÓN DE SEGURIDAD

### Verificar Encriptación

```bash
# En Python, ejecutar:
from app.utils.encryption import EncryptionService

service = EncryptionService()

# Test 1: Encriptar email
email = "test@example.com"
encrypted = service.encrypt(email)
decrypted = service.decrypt(encrypted)

assert decrypted == email
print("✅ Encriptación funcionando")

# Test 2: Verificar que emails no están en texto plano
import sqlite3
conn = sqlite3.connect('moirai.db')
cursor = conn.cursor()
cursor.execute("SELECT email FROM students LIMIT 1")
row = cursor.fetchone()
assert row[0] != "test@example.com"  # No debe ser texto plano
print("✅ Emails encriptados en BD")
```

### Verificar Esquemas Públicos

```bash
# En Python, ejecutar:
from app.schemas import StudentPublic, StudentProfile

# Test 1: StudentPublic no tiene email
student_public = StudentPublic(
    id=1, name="Test", program="CS", skills=[], soft_skills=[], projects=[]
)
assert not hasattr(student_public, 'email')
print("✅ StudentPublic no expone email")

# Test 2: StudentProfile sí tiene email (privado)
student_profile = StudentProfile(
    id=1, name="Test", email="test@example.com", 
    program="CS", skills=[], soft_skills=[], projects=[]
)
assert hasattr(student_profile, 'email')
print("✅ StudentProfile es privado")
```

### Verificar Control de Acceso

```bash
# Abrir DevTools y verificar headers de autorización
1. En pestaña "Network" de DevTools
2. Buscar peticiones GET /students/my-applications
3. Verificar header: Authorization: Bearer <api_key>
   ✅ Esperado: Header presente

# Verificar que endpoints sin auth fallan
1. En consola del navegador, ejecutar:
fetch('/admin/users', { method: 'GET' })
   ✅ Esperado: 401 Unauthorized (sin token)

2. Con token:
fetch('/admin/users', { 
    method: 'GET',
    headers: { 'Authorization': 'Bearer <token>' }
})
   ✅ Esperado: 200 OK (con token correcto)
```

---

## ✅ CHECKLIST FINAL

### Verificación Técnica
- [ ] `python verify_frontend_adaptation.py` ejecuta sin errores
- [ ] 17 cambios verificados correctamente
- [ ] Backend intacto (git diff vacío)
- [ ] No hay cambios en main.py, admin.py, auth.py

### Testing Estudiante
- [ ] Login funciona
- [ ] Dashboard carga sin 404s
- [ ] Mis aplicaciones carga
- [ ] Recomendaciones cargan
- [ ] Búsqueda de empleos funciona
- [ ] Console tiene 0 errores 404

### Testing Empresa
- [ ] Login funciona
- [ ] Dashboard carga sin 404s
- [ ] Búsqueda de candidatos funciona
- [ ] Filtros funcionan
- [ ] Console tiene 0 errores 404

### Testing Admin
- [ ] Login funciona
- [ ] Dashboard carga sin 404s
- [ ] KPIs cargan correctamente
- [ ] Auditoría carga correctamente
- [ ] Usuarios se muestran
- [ ] Console tiene 0 errores 404

### Validación de Seguridad
- [ ] Emails encriptados en BD
- [ ] StudentPublic no expone emails
- [ ] Control de acceso funciona
- [ ] Authorization headers presentes
- [ ] Endpoints sin auth devuelven 401

### Documentación
- [ ] FRONTEND_COMPATIBILITY_MAPPING.md revisado
- [ ] FRONTEND_ADAPTATION_FINAL_REPORT.md revisado
- [ ] VALIDATION_FINAL_COMPLETE.md revisado
- [ ] EXECUTIVE_SUMMARY_FINAL.md revisado
- [ ] BACKEND_SECURITY_AUDIT_COMPLETE.md revisado

### Cambios Git
- [ ] 7 archivos frontend modificados
- [ ] 0 archivos backend modificados
- [ ] Documentación actualizada
- [ ] Scripts de verificación agregados

---

## 🚀 PRÓXIMOS PASOS DESPUÉS DE VERIFICACIÓN

### Si TODO está ✅

```bash
# 1. Hacer commit
git add .
git commit -m "feat(frontend-adaptation): complete frontend compatibility (91%) without backend changes"

# 2. Mergear a main
git checkout main
git merge feature/frontend-mvp

# 3. Deploy a staging
git push origin main
# Trigger deploy pipeline

# 4. Testing en staging
# - Repetir testing manual en ambiente staging
# - Verificar performance
# - Verificar logs

# 5. Deploy a producción
# Si todo está bien en staging
git tag -a v1.0.0-frontend-adaptation -m "Frontend adaptation complete"
git push origin v1.0.0-frontend-adaptation
# Trigger production deploy
```

### Si hay ❌ Problemas

```bash
# 1. Identificar el problema
# Mirar console del navegador para errores específicos

# 2. Revisar logs
tail -f server.log

# 3. Revisar cambios realizados
git diff HEAD

# 4. Si es necesario, revertir y ajustar
git reset --hard HEAD~1

# 5. Hacer los ajustes necesarios
# Editar archivos problemáticos

# 6. Re-ejecutar verificación
python verify_frontend_adaptation.py
```

---

## 📞 SOPORTE Y DEBUGGING

### Errores Comunes y Soluciones

**Error: 404 en /students/my-applications**
```
Causa: Endpoint no fue actualizado o backend no registró el router
Solución: Verificar que students.py está cargado en main.py
```

**Error: Métodos deshabilitados lanzan excepción**
```
Causa: Esperado - endpoints no existen en MVP
Solución: Mostrar UI message "Disponible en futuras versiones"
```

**Error: Console muestra warnings de endpoints deshabilitados**
```
Causa: Esperado - métodos llaman console.warn()
Solución: Es normal, indica endpoints no disponibles
```

**Error: Backend cambió (main.py tiene modificaciones)**
```
Causa: Cambios no deseados fueron staged
Solución: git checkout HEAD -- app/main.py
         Revertir y mantener backend limpio
```

---

**Guía de Verificación Completada**  
**Próximo paso:** Ejecutar `python verify_frontend_adaptation.py` para validación automática
