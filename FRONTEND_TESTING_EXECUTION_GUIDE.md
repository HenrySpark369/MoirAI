# 🚀 Frontend MVP - Guía de Ejecución y Testing

**Status**: Ready for Production Testing  
**Branch**: `feature/frontend-mvp`  
**Last Commit**: b31fb3f39df1d97792bd041c519bffb143b21c74  

---

## 🎯 Objetivo

Ejecutar testing completo del frontend integrado con los endpoints del backend para validar:
- ✅ Autenticación (Login/Register)
- ✅ Dashboard con recomendaciones
- ✅ Perfil de usuario con CV upload
- ✅ Validación de formularios
- ✅ Responsividad en todos los dispositivos
- ✅ Seguridad de datos

---

## 📋 Pre-requisitos

### 1. Backend en ejecución
```bash
# Terminal 1: Backend
cd /Users/sparkmachine/MoirAI
python main.py

# Verificar que esté corriendo
curl http://localhost:8000/api/v1/health
# Response: { "status": "ok" }
```

### 2. Frontend en ejecución
```bash
# Terminal 2: Frontend
cd /Users/sparkmachine/MoirAI/app/frontend
python -m http.server 3000

# O con mejor servidor (recomendado)
# Instalar: npm install -g http-server
http-server -p 3000
```

### 3. Navegador
- ✅ Chrome/Chromium 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

---

## 🧪 Testing Manual - Paso a Paso

### FASE 1: AUTENTICACIÓN (30 minutos)

#### Test 1.1: Login Exitoso
**URL**: `http://localhost:3000/login`

1. Abrir página de login
2. Ingresar credenciales:
   - Email: `test@example.com`
   - Password: `TestPass123`
3. Hacer clic en "Iniciar Sesión"

**Resultado Esperado**:
- ✓ Notificación "¡Bienvenido!" aparece
- ✓ Redirección a /dashboard ocurre
- ✓ Dashboard carga con datos del usuario
- ✓ Token guardado en localStorage

**Verificación en Console (F12)**:
```javascript
// Debería mostrar true
console.log(authManager.isAuthenticated())

// Debería mostrar el token
console.log(localStorage.getItem('moirai_token'))

// Debería mostrar datos del usuario
console.log(authManager.getCurrentUser())
```

---

#### Test 1.2: Login Fallido
**URL**: `http://localhost:3000/login`

1. Ingresar email inválido: `wrong@test.com`
2. Ingresar password: `WrongPass123`
3. Click en submit

**Resultado Esperado**:
- ✓ Notificación de error: "Email o contraseña incorrectos"
- ✓ Usuario permanece en /login
- ✓ No hay redirección
- ✓ Token NO se guarda

---

#### Test 1.3: Registro Exitoso
**URL**: `http://localhost:3000/login`

1. Hacer clic en tab "Registrarse"
2. Seleccionar rol: "Estudiante"
3. Ingresar datos:
   - Nombre: `Juan`
   - Apellido: `Pérez`
   - Email: `juan.perez@example.com`
   - Password: `NewPass123`
   - Confirmar: `NewPass123`
4. Aceptar términos
5. Click en "Crear Cuenta"

**Resultado Esperado**:
- ✓ Notificación: "¡Cuenta creada exitosamente!"
- ✓ Auto-login y redirección a /dashboard
- ✓ Datos guardados en backend
- ✓ Sesión iniciada automáticamente

---

#### Test 1.4: Remember Me
**URL**: `http://localhost:3000/login`

1. Marcar checkbox "Recuérdame"
2. Ingresar email: `test@example.com`
3. Ingresar password: `TestPass123`
4. Submit
5. Esperar redirección a dashboard
6. Logout (botón en navbar)
7. Volver a `/login`

**Resultado Esperado**:
- ✓ Email permanece precargado en formulario
- ✓ Checkbox "Recuérdame" está marcado
- ✓ localStorage contiene `moirai_rememberEmail`

---

### FASE 2: DASHBOARD (40 minutos)

#### Test 2.1: Carga de Dashboard
**URL**: `http://localhost:3000/dashboard` (después de login)

1. Abrir DevTools (F12)
2. Ir a tab Network
3. Recargar página (Cmd+R)

**Resultado Esperado**:
- ✓ Página carga en < 2 segundos
- ✓ Notificación "Cargando dashboard..." desaparece
- ✓ Nombre de usuario visible en welcome section
- ✓ 4 stat cards visibles: Applications, Score, Recommendations, CV

**Verificar Network (Tab Network)**:
- [ ] GET /api/v1/auth/me → 200
- [ ] GET /api/v1/applications/my-applications → 200
- [ ] POST /api/v1/matching/recommendations → 200
- [ ] Todos < 1 segundo

---

#### Test 2.2: Estadísticas
1. Observar las 4 tarjetas de stats
2. Verificar cada una:

```
┌─────────────────┬─────────────────┐
│ Applications: X │ Match Score: Y% │
├─────────────────┼─────────────────┤
│ Recommendations │ CV Actualizado  │
│     : Z         │   : Sí/No       │
└─────────────────┴─────────────────┘
```

**Resultado Esperado**:
- ✓ Números coinc iden con datos reales
- ✓ Formato legible
- ✓ Colores consistentes

---

#### Test 2.3: Recomendaciones de Empleos
1. Scrollear hasta "Empleos Recomendados"
2. Verificar grid de tarjetas

Cada tarjeta debe mostrar:
- ✓ Título del empleo
- ✓ Nombre de empresa
- ✓ Ubicación con icono
- ✓ Modalidad (Presencial/Híbrido/Remoto)
- ✓ Match Score (95% Match)
- ✓ Botones: "Ver" y "Aplicar"

3. Hacer clic en botón "Ver"

**Resultado Esperado**:
- ✓ Modal con detalles del empleo abierto
- ✓ Descripción completa visible
- ✓ Requisitos en lista
- ✓ Salario mostrado
- ✓ Scroll de página bloqueado (no se ve scroll bar)

4. Cerrar modal con:
   - Click en X
   - Click fuera del modal
   - Press Escape

**Resultado Esperado**:
- ✓ Modal desaparece
- ✓ Scroll de página restaurado
- ✓ Se puede scrollear normalmente

---

#### Test 2.4: Aplicar a Empleo
1. Abrir modal de un empleo
2. Click en "Aplicar Ahora"

**Resultado Esperado**:
- ✓ Notificación: "Enviando aplicación..."
- ✓ Notificación: "¡Aplicación enviada exitosamente!"
- ✓ Modal se cierra
- ✓ Nueva aplicación aparece en tabla

3. Intentar aplicar de nuevo (test 2.5)

---

#### Test 2.5: Prevención de Aplicaciones Duplicadas
1. Intentar aplicar al MISMO empleo dos veces rápidamente
2. O hacer 4+ aplicaciones en 5 segundos

**Resultado Esperado**:
- ✓ Rate limiter muestra: "Espera un momento antes..."
- ✓ No se envía la solicitud
- ✓ Backend NO recibe petición duplicada

---

#### Test 2.6: Tabla de Aplicaciones
1. Scrollear hasta "Mis Aplicaciones"
2. Verificar tabla:

| Empleo | Empresa | Estado | Fecha | Acciones |
|--------|---------|--------|-------|----------|
| ... | ... | Pendiente | ... | Ver |
| ... | ... | Aceptada | ... | Ver |

**Resultado Esperado**:
- ✓ Estados coloreados:
  - Pendiente = Amarillo
  - Aceptada = Verde
  - Rechazada = Rojo
- ✓ Fechas en formato español (15/11/2025)
- ✓ Click en "Ver" muestra detalles

---

### FASE 3: PERFIL DE USUARIO (45 minutos)

#### Test 3.1: Cargar Perfil
**URL**: `http://localhost:3000/profile`

1. Click en "Perfil" en navbar
2. O navegar directo a /profile

**Resultado Esperado**:
- ✓ Formulario de perfil carga con datos actuales
- ✓ Nombre precargado
- ✓ Email NO editable (gris)
- ✓ Teléfono editable
- ✓ Biografía editable

---

#### Test 3.2: Editar Información Personal
1. Cambiar teléfono: `+56912345678`
2. Cambiar biografía: `Soy un estudiante de Ingeniería en Sistemas`
3. Click en "Guardar Cambios"

**Resultado Esperado**:
- ✓ Notificación: "Perfil actualizado"
- ✓ PUT /api/v1/students/{id} enviado
- ✓ Cambios persisten al refrescar
- ✓ localStorage se actualiza

---

#### Test 3.3: Upload de CV - Arrastra y Suelta
1. Ir a sección "Carga tu CV"
2. Arrastar archivo PDF sobre el área
3. Soltar archivo

**Resultado Esperado**:
- ✓ Área cambia de color (dragover)
- ✓ Loading muestra: "Subiendo CV... 0%"
- ✓ Progress actualiza en real time: 25%, 50%, 75%, 100%
- ✓ Notificación: "CV subido exitosamente"

---

#### Test 3.4: Upload de CV - Click para Seleccionar
1. Click en área de upload
2. Seleccionar archivo DOCX (Word)
3. Confirmar selección

**Resultado Esperado**:
- ✓ Mismo comportamiento que 3.3
- ✓ Progress visible

---

#### Test 3.5: Validación de Archivo
1. Intentar subir:
   - [ ] Archivo > 5MB → Error: "no debe superar 5MB"
   - [ ] Archivo .jpg → Error: "Solo PDF o DOCX"
   - [ ] Archivo .txt → Error: "Solo PDF o DOCX"

**Resultado Esperado**:
- ✓ Todas las validaciones funcionan
- ✓ Errores claros

---

#### Test 3.6: Estado del CV
Después de upload exitoso, verificar:
- ✓ Sección muestra: "CV cargado: [nombre archivo]"
- ✓ Fecha de carga mostrada
- ✓ Botones "Descargar" y "Eliminar" visibles

---

#### Test 3.7: Habilidades Inferidas
Después de upload de CV:
1. Ir a sección "Habilidades Analizadas"

**Resultado Esperado**:
- ✓ Lista de habilidades extraídas por NLP
- ✓ Cada habilidad muestra: Nombre + Porcentaje (95%)
- ✓ Colores diferentes para técnicas vs blandas
- ✓ Botón X para remover habilidades

---

### FASE 4: VALIDACIÓN DE FORMULARIOS (30 minutos)

#### Test 4.1: Email Validation
1. Ir a Login
2. Probar emails:

| Email | Esperado |
|-------|----------|
| `test@example.com` | ✓ Válido |
| `invalidemail` | ✗ Error |
| `@example.com` | ✗ Error |
| `test@` | ✗ Error |

**Resultado Esperado**:
- ✓ Error message aparece en campo
- ✓ Botón submit deshabilitado si hay error
- ✓ Color rojo en campo con error

---

#### Test 4.2: Contraseña Validation
1. Ir a Register
2. Ingresar password:

| Password | Esperado |
|----------|----------|
| `Test123` | ✗ Error (< 8 chars) |
| `testpass123` | ✗ Error (no mayúscula) |
| `TESTPASS123` | ✗ Error (no minúscula) |
| `Testpass` | ✗ Error (no número) |
| `TestPass123` | ✓ Válido |

**Resultado Esperado**:
- ✓ Requisitos mostrados claramente
- ✓ Validación en tiempo real
- ✓ Confirmación debe coincidir

---

### FASE 5: RESPONSIVIDAD (45 minutos)

#### Test 5.1: Desktop (1200px+)
1. Abrir DevTools
2. Desactivar "Device Toolbar"
3. Maximizar ventana

**Verificar**:
- [ ] Navbar horizontal
- [ ] Todos los elementos visibles
- [ ] Sin scroll horizontal
- [ ] Iconos + texto en botones

---

#### Test 5.2: Tablet (768px - 1200px)
1. DevTools → Device Toolbar
2. Seleccionar "iPad" o "iPad Air"

**Verificar**:
- [ ] Navbar adaptado
- [ ] Una o dos columnas según espacio
- [ ] Elementos redimensionados
- [ ] Clickeable todo

---

#### Test 5.3: Mobile (480px - 768px)
1. Device Toolbar → "Galaxy S5" o similar

**Verificar**:
- [ ] Hamburger menu en navbar
- [ ] Una columna
- [ ] Tablas scrolleables horizontalmente
- [ ] Botones 48px mínimo

---

#### Test 5.4: Small Mobile (<480px)
1. Device Toolbar → "iPhone SE"

**Verificar**:
- [ ] Todo legible
- [ ] Texto no cortado
- [ ] Modales a pantalla completa
- [ ] Elementos no colisionan

---

### FASE 6: SEGURIDAD (30 minutos)

#### Test 6.1: Protección de Rutas
1. Logout
2. Intentar acceder a `/dashboard` directamente
3. Intentar acceder a `/profile`

**Resultado Esperado**:
- ✓ Redirige a `/login?redirect=/dashboard`
- ✓ Después de login, redirige a dashboard

---

#### Test 6.2: Token en Headers
1. Login exitoso
2. Abrir DevTools → Network
3. Ir a Dashboard
4. Buscar request a `/api/v1/`

**Verificar Headers**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Resultado Esperado**:
- ✓ Token presente
- ✓ Formato: "Bearer {token}"

---

#### Test 6.3: Token Expirado (Simulación)
1. Login
2. Abrir console: `localStorage.setItem('moirai_token', 'expired')`
3. Recargar página

**Resultado Esperado**:
- ✓ Notificación: "Tu sesión expiró..."
- ✓ Redirige a `/login?expired=true`

---

### FASE 7: PERFORMANCE (20 minutos)

#### Test 7.1: Lighthouse Audit
1. DevTools → Lighthouse
2. Click en "Analyze page load"

**Mínimos Aceptables**:
- Performance: 70+
- Accessibility: 80+
- Best Practices: 80+
- SEO: 80+

---

#### Test 7.2: Page Load Time
1. DevTools → Network
2. Recargar página (Cmd+R)
3. Revisar Finish time

**Mínimos Aceptables**:
- Home: < 1.5s
- Login: < 1.5s
- Dashboard: < 2s
- Profile: < 2s

---

## 📊 Test Results Template

Crear archivo: `/Users/sparkmachine/MoirAI/TEST_RESULTS_MANUAL.md`

```markdown
# Manual Testing Results

**Date**: [FECHA]
**Tester**: [NOMBRE]
**Browser**: [NAVEGADOR + VERSION]
**OS**: [macOS/Windows/Linux]

## Phase 1: Authentication
- [ ] 1.1 Login Exitoso: PASS/FAIL
- [ ] 1.2 Login Fallido: PASS/FAIL
- [ ] 1.3 Registro Exitoso: PASS/FAIL
- [ ] 1.4 Remember Me: PASS/FAIL

## Phase 2: Dashboard
- [ ] 2.1 Carga: PASS/FAIL
- [ ] 2.2 Estadísticas: PASS/FAIL
- [ ] 2.3 Recomendaciones: PASS/FAIL
- [ ] 2.4 Aplicar: PASS/FAIL
- [ ] 2.5 Rate Limiting: PASS/FAIL
- [ ] 2.6 Tabla: PASS/FAIL

## Phase 3: Profile
- [ ] 3.1 Cargar: PASS/FAIL
- [ ] 3.2 Editar: PASS/FAIL
- [ ] 3.3 Upload Drag: PASS/FAIL
- [ ] 3.4 Upload Click: PASS/FAIL
- [ ] 3.5 Validación: PASS/FAIL
- [ ] 3.6 CV Status: PASS/FAIL
- [ ] 3.7 Habilidades: PASS/FAIL

## Phase 4: Validación
- [ ] 4.1 Email: PASS/FAIL
- [ ] 4.2 Password: PASS/FAIL

## Phase 5: Responsividad
- [ ] 5.1 Desktop: PASS/FAIL
- [ ] 5.2 Tablet: PASS/FAIL
- [ ] 5.3 Mobile: PASS/FAIL
- [ ] 5.4 Small Mobile: PASS/FAIL

## Phase 6: Seguridad
- [ ] 6.1 Protección rutas: PASS/FAIL
- [ ] 6.2 Token headers: PASS/FAIL
- [ ] 6.3 Token expirado: PASS/FAIL

## Phase 7: Performance
- [ ] 7.1 Lighthouse: PASS/FAIL (Score: __)
- [ ] 7.2 Page speed: PASS/FAIL

## Issues Found
1. [Describir]
2. [Describir]

## Overall Result
- **PASS**: Todo funciona ✓
- **PASS WITH ISSUES**: Funciona pero con problemas
- **FAIL**: No funciona

**Notes**:
[Notas generales]
```

---

## 🐛 Debugging Tips

### Si algo no funciona...

**1. Limpiar localStorage**
```javascript
// En console (F12)
localStorage.clear()
location.reload()
```

**2. Ver estado actual**
```javascript
console.log(authManager.isAuthenticated())
console.log(authManager.getCurrentUser())
console.log(StorageManager.getAll())
```

**3. Ver requests fallidos**
- DevTools → Network
- Buscar request rojo (error)
- Click para ver detalles
- Response tab muestra error

**4. Ver console errors**
- DevTools → Console
- Los errores aparecer en rojo
- Click para obtener stack trace

---

## ✅ Checklist Final

Antes de marcar como "TESTING COMPLETE":

- [ ] Todas las fases pasadas
- [ ] No hay console errors (rojo)
- [ ] No hay console warnings (amarillo) críticos
- [ ] Performance >= 70 (Lighthouse)
- [ ] Funciona en 3+ navegadores
- [ ] Responsividad funciona en 4 breakpoints
- [ ] Seguridad validada
- [ ] TEST_RESULTS_MANUAL.md completado

---

## 📞 Next Steps

Si todos los tests PASS:

1. **Commit cambios**
```bash
git add .
git commit -m "Testing completed: All phases passed"
git push origin feature/frontend-mvp
```

2. **Create Pull Request**
```
Title: "Frontend MVP - Complete implementation with fixes"
Description: "Integrates frontend with all endpoints, includes 5 critical fixes"
Base: main
Compare: feature/frontend-mvp
```

3. **Deploy a Staging**
```bash
# Preparar para deployment
npm run build
npm run deploy:staging
```

4. **QA Testing en Staging**
5. **Deploy a Production**

---

**Generated**: 15 de noviembre de 2025  
**Version**: 3.0  
**Time to Complete**: ~3 horas en total
