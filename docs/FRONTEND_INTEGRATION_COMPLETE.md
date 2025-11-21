# 🚀 Integración Frontend Completa - MoirAI MVP

**Rama**: `feature/frontend-integration-mvp`  
**Estado**: ✅ FRONTEND STRUCTURES EXPLORADO  
**Última actualización**: 15 noviembre 2025

---

## 📊 Análisis de Estructura Actual

### ✅ Lo que YA EXISTE

#### 1. **Landing Page** (`index.html`)
```
✅ Hero section con CTA
✅ Features showcase (6 características)
✅ How it works (3 pasos)
✅ Para quién (Estudiantes, Empresas, Admin)
✅ Testimonios
✅ CTA section
✅ Contact section
✅ Footer
✅ Modales de Login/Register
```

**Estado**: Funcional y atractivo

---

#### 2. **Listing Pages** (Plantillas dinámicas)

**`oportunidades.html`** - Búsqueda de empleos
```html
✅ Header con search bar
✅ Sidebar con filtros:
   - Ubicación
   - Modalidad (Presencial, Híbrido, Remoto)
   - Sector
   - Nivel de experiencia
✅ Main content area
✅ Grid/List view toggle
✅ Sort options
```

**`estudiantes.html`** - Directorio de estudiantes
```html
✅ Header con search bar
✅ Sidebar con filtros:
   - Carrera
   - Año de estudios
   - Disponibilidad
   - Tecnologías
✅ Main content area con tarjetas de estudiantes
```

**`empresas.html`** - Directorio de empresas
```html
✅ Header con search bar
✅ Sidebar con filtros
✅ Main content area con tarjetas de empresas
```

**Estado**: HTML estructurado, listo para conectar con backend

---

#### 3. **CSS Completo** (`styles.css`)
```
✅ 2300+ líneas
✅ Responsive design
✅ Gradientes (primario: #730f33, secundario: #e2bb84)
✅ Sistema de colores profesional
✅ Componentes: botones, tarjetas, modales
✅ Breakpoints: 1200px, 1024px, 768px, 480px
✅ Animaciones suaves
```

**Estado**: Producción-ready

---

#### 4. **JavaScript Core** (`main.js`)
```javascript
✅ Gestión de modales
✅ Navegación (smooth scroll)
✅ Manejo de formularios
✅ Notificaciones toast
✅ Scroll to top button
✅ Event tracking (placeholder)
```

**Estado**: Funcional, listo para extensión

---

#### 5. **JavaScript Dinámico** (`listings.js`)
```javascript
✅ Mock data para jobs
✅ Funciones de filtrado
✅ Búsqueda
✅ Rendering de tarjetas
✅ 755 líneas de código
```

**Estado**: Necesita conectar con API real

---

### 🎯 Lo que FALTA CONECTAR

| Componente | Status | Acción |
|-----------|--------|--------|
| **API Client** | ✅ Existe (`api-client.js`) | Integrar en listings |
| **Auth Manager** | ✅ Existe (`auth-manager.js`) | Proteger rutas |
| **Notification Mgr** | ✅ Existe (`notification-manager.js`) | Usar en formularios |
| **Backend API** | ✅ Endpoints listos | Conectar en listings.js |
| **Form Validation** | ❌ No existe | Crear utils |
| **Storage Management** | ❌ No existe | Crear para caché |
| **Page-specific JS** | ❌ No existe | login.js, dashboard.js, profile.js |

---

## 🔌 Plan de Integración en 3 Pasos

### PASO 1: Conectar Listings.js con API Real

**Archivo a modificar**: `/app/frontend/static/js/listings.js`

```javascript
// ANTES (Mock Data):
const mockJobs = [
    { id: 1, title: "...", company: "...", ... },
    // ... 7 más
];

// DESPUÉS (API Real):
async function loadJobs(filters = {}) {
    try {
        notificationManager.loading('Cargando empleos...')
        
        let url = '/api/v1/jobs/search?'
        const params = new URLSearchParams()
        
        if (filters.keyword) params.append('keyword', filters.keyword)
        if (filters.location) params.append('location', filters.location)
        if (filters.modality) params.append('work_mode', filters.modality)
        if (filters.sector) params.append('sector', filters.sector)
        if (filters.level) params.append('level', filters.level)
        
        const response = await apiClient.get(`/jobs/search?${params}`)
        
        notificationManager.hideLoading()
        
        return response.jobs || []
    } catch (error) {
        notificationManager.error('Error al cargar empleos')
        return []
    }
}
```

---

### PASO 2: Crear Funciones de Sincronización

```javascript
/**
 * Sincronizar filtros con URL
 */
function syncFiltersToURL() {
    const params = new URLSearchParams()
    
    // Recolectar filtros activos
    const location = document.getElementById('locationFilter')?.value
    const sector = document.getElementById('sectorFilter')?.value
    const modalities = Array.from(document.querySelectorAll('.modality-filter:checked'))
        .map(el => el.value)
    
    if (location) params.append('location', location)
    if (sector) params.append('sector', sector)
    if (modalities.length) params.append('modality', modalities.join(','))
    
    // Actualizar URL sin recargar
    window.history.replaceState({}, '', `${window.location.pathname}?${params}`)
    
    // Recargar resultados
    loadJobs(Object.fromEntries(params))
}

/**
 * Cargar filtros desde URL
 */
function loadFiltersFromURL() {
    const params = new URLSearchParams(window.location.search)
    
    if (params.has('location')) {
        document.getElementById('locationFilter').value = params.get('location')
    }
    if (params.has('sector')) {
        document.getElementById('sectorFilter').value = params.get('sector')
    }
    if (params.has('keyword')) {
        document.getElementById('searchJobs').value = params.get('keyword')
    }
}
```

---

### PASO 3: Crear Página de Dashboard Privada

**Nuevo archivo**: `/app/frontend/templates/dashboard.html`

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - MoirAI</title>
    <link rel="stylesheet" href="/static/css/styles.css">
    <link rel="stylesheet" href="/static/css/dashboard.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar">
        <div class="nav-container">
            <div class="nav-logo">
                <a href="/"><i class="fas fa-brain"></i> MoirAI</a>
            </div>
            <div class="nav-menu">
                <ul class="nav-list">
                    <li><a href="/dashboard" class="nav-link active">Dashboard</a></li>
                    <li><a href="/oportunidades" class="nav-link">Oportunidades</a></li>
                    <li><a href="/profile" class="nav-link">Mi Perfil</a></li>
                </ul>
            </div>
            <div class="nav-cta">
                <button class="btn btn-secondary" onclick="logout()">
                    <i class="fas fa-sign-out-alt"></i> Salir
                </button>
            </div>
        </div>
    </navbar>

    <!-- Main Content -->
    <main class="dashboard-main">
        <!-- Welcome Section -->
        <section class="welcome-section">
            <div class="container">
                <h1>Bienvenido, <span id="user-name"></span></h1>
                <p id="user-subtitle"></p>
            </div>
        </section>

        <!-- Stats Section -->
        <section class="stats-section">
            <div class="container">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-briefcase"></i>
                        </div>
                        <div class="stat-content">
                            <h3>Aplicaciones</h3>
                            <p class="stat-number" id="applications-count">0</p>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-star"></i>
                        </div>
                        <div class="stat-content">
                            <h3>Score Match</h3>
                            <p class="stat-number" id="match-score">0%</p>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-bell"></i>
                        </div>
                        <div class="stat-content">
                            <h3>Recomendaciones</h3>
                            <p class="stat-number" id="recommendations-count">0</p>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-file-pdf"></i>
                        </div>
                        <div class="stat-content">
                            <h3>CV Actualizado</h3>
                            <p class="stat-text" id="cv-status">No</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Recommendations Section -->
        <section class="recommendations-section">
            <div class="container">
                <h2>Empleos Recomendados Para Ti</h2>
                <p class="section-subtitle">Basado en tu perfil y habilidades</p>
                <div class="jobs-carousel" id="recommendations-container">
                    <!-- Cargado dinámicamente -->
                </div>
            </div>
        </section>

        <!-- Applications Section -->
        <section class="applications-section">
            <div class="container">
                <h2>Mis Aplicaciones</h2>
                <div class="applications-table" id="applications-container">
                    <!-- Cargado dinámicamente -->
                </div>
            </div>
        </section>
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <p>&copy; 2025 MoirAI. Todos los derechos reservados.</p>
        </div>
    </footer>

    <!-- Scripts -->
    <script src="/static/js/api-client.js"></script>
    <script src="/static/js/auth-manager.js"></script>
    <script src="/static/js/notification-manager.js"></script>
    <script src="/static/js/pages/dashboard.js"></script>
</body>
</html>
```

---

## 📝 Archivos a Crear/Modificar

### ✅ CREAR (8 nuevos archivos)

#### 1. **pages/dashboard.js** (500 líneas)
```javascript
async function initDashboard() {
    // Proteger ruta
    if (!authManager.isAuthenticated()) {
        window.location.href = '/login'
        return
    }
    
    // Cargar datos del usuario
    const user = await authManager.getCurrentUser()
    document.getElementById('user-name').textContent = user.first_name
    
    // Cargar recomendaciones
    await loadRecommendations()
    
    // Cargar aplicaciones
    await loadApplications()
    
    // Cargar stats
    await loadStats()
}
```

#### 2. **pages/profile.js** (450 líneas)
- Upload de CV
- Ver habilidades inferidas
- Editar información personal
- Ver historial de cambios

#### 3. **pages/login.js** (300 líneas)
- Integración con authManager.login()
- Validación de formulario
- Redirección a dashboard

#### 4. **pages/register.js** (350 líneas)
- Integración con authManager.register()
- Selección de rol (estudiante/empresa)
- Validación de datos

#### 5. **utils/form-validator.js** (200 líneas)
```javascript
const FormValidator = {
    email: (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email),
    password: (pwd) => pwd.length >= 8,
    required: (field) => field.trim() !== '',
    // ... más validadores
}
```

#### 6. **utils/storage-manager.js** (200 líneas)
```javascript
const StorageManager = {
    set: (key, value) => localStorage.setItem(key, JSON.stringify(value)),
    get: (key) => JSON.parse(localStorage.getItem(key)),
    clear: (key) => localStorage.removeItem(key),
    // ... más métodos
}
```

#### 7. **css/dashboard.css** (400 líneas)
- Estilos del dashboard
- Tarjetas de stats
- Tablas de aplicaciones
- Carrusel de recomendaciones

#### 8. **css/profile.css** (300 líneas)
- Estilos de formulario de perfil
- Upload de archivo
- Skills display
- Historial

---

### 🔄 MODIFICAR (4 archivos existentes)

#### 1. **listings.js** - Conectar con API
```diff
- const mockJobs = [...]
+ async function loadJobs(filters) { ... }
```

#### 2. **main.js** - Añadir autenticación
```javascript
// Verificar auth en load
document.addEventListener('DOMContentLoaded', async () => {
    const isAuthenticated = authManager.isAuthenticated()
    
    if (isAuthenticated) {
        // Mostrar botón de logout
        updateNavbar()
    }
})
```

#### 3. **index.html** - Agregar auth checks
```html
<!-- En lugar de scrollToLogin(), usar proper flow -->
<script>
    function handleLoginClick() {
        if (authManager.isAuthenticated()) {
            window.location.href = '/dashboard'
        } else {
            scrollToLogin()
        }
    }
</script>
```

#### 4. **sidebar.js** - Si existe, actualizar
```javascript
// Agregar logout handler
function handleLogout() {
    authManager.logout()
    window.location.href = '/'
}
```

---

## 🔐 Protección de Rutas

### Middleware para verificar autenticación

```javascript
// En cada página protegida
function protectRoute() {
    if (!authManager.isAuthenticated()) {
        window.location.href = `/login?redirect=${window.location.pathname}`
        return false
    }
    
    const user = authManager.getCurrentUser()
    if (!user) {
        await authManager.refreshToken()
    }
    
    return true
}

// Ejecutar al cargar la página
if (!protectRoute()) {
    throw new Error('Access denied')
}
```

---

## 📱 Flujo de Usuario Completo

```
1. Usuario llega a / (index.html)
   ↓
2. Hace clic en "Inicia Sesión"
   ↓
3. Se abre modal de login
   ↓
4. Ingresa email + password
   ↓
5. Envía POST /api/v1/auth/login
   ↓
6. Backend retorna JWT token
   ↓
7. Frontend almacena token en localStorage
   ↓
8. Redirige a /dashboard (protegida)
   ↓
9. Dashboard carga datos del usuario
   ↓
10. Muestra recomendaciones personalizadas
```

---

## 🚀 PLAN DE IMPLEMENTACIÓN INMEDIATO

### **Semana 1** (4-8 de diciembre)

| Día | Tarea | Archivos |
|-----|-------|----------|
| Lun | Conectar listings.js con API | listings.js |
| Mar | Crear pages/dashboard.js | dashboard.html, dashboard.js |
| Mié | Crear pages/login.js + register.js | login.js, register.js |
| Jue | Crear utils (form-validator, storage-mgr) | form-validator.js, storage-manager.js |
| Vie | Testing e integración completa | Todos |

### **Semana 2** (11-15 de diciembre)

| Día | Tarea | Archivos |
|-----|-------|----------|
| Lun | Crear pages/profile.js + upload CV | profile.html, profile.js |
| Mar | Crear CSS para dashboard y profile | dashboard.css, profile.css |
| Mié | Testing de flujos completos | Todos |
| Jue | Optimización y pulido | Todos |
| Vie | Deploy a staging | Deploy |

---

## 📊 Checklist de Integración

### Conectividad Backend
- [ ] API Client funciona con endpoints
- [ ] Auth Manager obtiene tokens correctamente
- [ ] Refresh de token automático
- [ ] Error handling en 401/403

### Páginas Dinámicas
- [ ] Dashboard carga datos reales
- [ ] Listings conectan con /jobs/search
- [ ] Filtros funcionan en tiempo real
- [ ] Búsqueda es funcional

### Seguridad
- [ ] Tokens en localStorage
- [ ] CORS habilitado en backend
- [ ] Rutas protegidas con auth check
- [ ] Logout limpia tokens

### UX/UI
- [ ] Notificaciones funcionan
- [ ] Modales responsivos
- [ ] Loading states en transiciones
- [ ] Mensajes de error claros

### Performance
- [ ] Caché de búsquedas
- [ ] Lazy loading de imágenes
- [ ] Minificación de assets
- [ ] Compresión de respuestas

---

## 🔗 Recursos Disponibles

```
Frontend:
├── /app/frontend/static/js/
│   ├── api-client.js          ✅ Cliente HTTP
│   ├── auth-manager.js        ✅ Autenticación
│   ├── notification-manager.js ✅ Notificaciones
│   ├── main.js                ✅ Core
│   └── listings.js            ⚠️ Necesita API
├── /app/frontend/templates/
│   ├── index.html             ✅ Landing
│   ├── oportunidades.html     ⚠️ Necesita API
│   ├── estudiantes.html       ⚠️ Necesita API
│   ├── empresas.html          ⚠️ Necesita API
│   └── admin/dashboard.html   ⚠️ Necesita integración
└── /app/frontend/static/css/
    ├── styles.css             ✅ Estilos main
    └── notifications.css      ✅ Notificaciones

Backend Endpoints Disponibles:
✅ POST /api/v1/auth/login
✅ POST /api/v1/auth/register
✅ GET /api/v1/auth/me
✅ GET /api/v1/jobs/search
✅ POST /api/v1/matching/recommendations
✅ GET /api/v1/students/{id}
✅ POST /api/v1/applications
```

---

## 📞 Debugging Workflow

### Si los filtros no funcionan:
```javascript
// Verificar en console
console.log('Current filters:', getCurrentFilters())
console.log('API params:', buildAPIParams())
console.log('API response:', lastAPIResponse)
```

### Si el login falla:
```javascript
// Revisar en Network tab:
POST /api/v1/auth/login
// Buscar: Authorization header, token en response

// En console:
console.log('Token stored:', localStorage.getItem('token'))
console.log('Auth state:', authManager.isAuthenticated())
```

### Si faltan datos en dashboard:
```javascript
// Verificar endpoint:
await apiClient.get('/matching/recommendations')
// Debe retornar: { jobs: [...], totalScore: X }
```

---

## ✅ Estado Final

```
INFRAESTRUCTURA:  ████████████████████ 100% ✅
  - API Client:        ✅ 425 líneas
  - Auth Manager:      ✅ 285 líneas
  - Notifications:     ✅ 405 líneas
  - CSS:               ✅ 2300+ líneas

PAGES HTML:       ████░░░░░░░░░░░░░░░░ 50%
  - Landing:           ✅ index.html
  - Oportunidades:     ✅ HTML + ⚠️ API
  - Estudiantes:       ✅ HTML + ⚠️ API
  - Empresas:          ✅ HTML + ⚠️ API
  - Dashboard:         ❌ Crear
  - Profile:           ❌ Crear
  - Admin:             ❌ Integrar

JAVASCRIPT DINÁMICO: ██░░░░░░░░░░░░░░░░░░ 20%
  - Listings.js:       ✅ Mock + ⚠️ API
  - Main.js:           ✅ Core
  - Pages:             ❌ Crear (4 archivos)
  - Utils:             ❌ Crear (2 archivos)

ESTILOS ADICIONALES: ░░░░░░░░░░░░░░░░░░░░ 0%
  - Dashboard CSS:     ❌ Crear
  - Profile CSS:       ❌ Crear

TOTAL PROGRESO:       ██████░░░░░░░░░░░░░░ 43%
```

---

**Próximo paso**: Ejecutar PASO 1 (Conectar listings.js) y crear commit con integración API
