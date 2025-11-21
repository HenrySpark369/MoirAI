# 🚀 Frontend Optimization & Bug Fixes - Phase 2

**Branch**: `feature/frontend-mvp`  
**Status**: Ready for Implementation  
**Priority**: HIGH  

---

## 📋 Índice

1. [Bugs Conocidos a Corregir](#bugs-conocidos)
2. [Optimizaciones de Performance](#optimizaciones)
3. [Mejoras de UX/UI](#mejoras-ux)
4. [Seguridad Adicional](#seguridad)
5. [Accesibilidad](#accesibilidad)
6. [Testing Workflow](#testing-workflow)

---

## 🐛 Bugs Conocidos a Corregir

### 1. Modal - Scroll en background
**Severity**: MEDIUM  
**Description**: Cuando modal abierto, página de fondo puede scrollear

**Fix**:
```javascript
// En dashboard.js al abrir modal
function viewJobDetail(jobId) {
    document.body.style.overflow = 'hidden';
    // ... mostrar modal ...
}

// Al cerrar modal
document.querySelector('.modal .close').addEventListener('click', () => {
    document.body.style.overflow = 'auto';
    // ... cerrar modal ...
});
```

---

### 2. Token Expiration
**Severity**: HIGH  
**Description**: Token expirado no se maneja correctamente, usuario queda sin sesión

**Fix**:
```javascript
// En api-client.js
async function handleUnauthorized() {
    authManager.logout();
    notificationManager.error('Tu sesión expiró. Por favor, inicia sesión nuevamente.');
    window.location.href = '/login';
}

// En cada request
if (response.status === 401) {
    handleUnauthorized();
    return;
}
```

---

### 3. Form submit duplicate
**Severity**: MEDIUM  
**Description**: Al hacer click rápido en submit, se envía el form dos veces

**Fix**:
```javascript
// En login.js
let submitInProgress = false;

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (submitInProgress) return;
    submitInProgress = true;
    
    try {
        // Procesar
    } finally {
        submitInProgress = false;
    }
});
```

---

### 4. Empty state images
**Severity**: LOW  
**Description**: Imágenes en empty states pueden no cargar

**Fix**:
```html
<!-- dashboard.html -->
<div class="empty-state">
    <img src="/static/images/empty-jobs.svg" alt="Sin empleos" onerror="this.style.display='none'">
    <p>No hay empleos disponibles</p>
</div>
```

---

### 5. File upload progress
**Severity**: MEDIUM  
**Description**: No hay feedback visual durante upload de CV

**Fix**:
```javascript
// En profile.js
async function handleCVUpload(file) {
    const progressBar = document.querySelector('.upload-progress');
    const xhr = new XMLHttpRequest();
    
    xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100;
            progressBar.style.width = percentComplete + '%';
        }
    });
    
    // ... upload ...
}
```

---

## ⚡ Optimizaciones de Performance

### 1. Minify CSS y JS
**Impact**: 40-50% reducción de bundle size

```bash
# Instalar herramientas
npm install --save-dev terser clean-css-cli

# Minify JS
terser app/frontend/static/js/**/*.js -o app/frontend/static/js/app.min.js

# Minify CSS
cleancss app/frontend/static/css/**/*.css -o app/frontend/static/css/app.min.css
```

---

### 2. Lazy load recommendations
**Impact**: 30% más rápido en dashboard inicial

```javascript
// dashboard.js
function loadRecommendations() {
    // Load asynchronously after initial dashboard render
    setTimeout(() => {
        // fetch recommendations...
    }, 500);
}
```

---

### 3. Caché de búsquedas
**Impact**: Búsquedas más rápidas en segunda vez

```javascript
// En listings.js
class SearchCache {
    constructor(maxItems = 50) {
        this.cache = new Map();
        this.maxItems = maxItems;
    }
    
    get(query) {
        return this.cache.get(query);
    }
    
    set(query, results) {
        if (this.cache.size >= this.maxItems) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
        this.cache.set(query, results);
    }
}

const searchCache = new SearchCache();
```

---

### 4. Debounce en search
**Impact**: 60% menos requests

```javascript
function debounce(func, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func(...args), delay);
    };
}

const debouncedSearch = debounce((query) => {
    // Ejecutar búsqueda
}, 500);

searchInput.addEventListener('input', (e) => {
    debouncedSearch(e.target.value);
});
```

---

### 5. Throttle en scroll
**Impact**: Mejor performance en scroll

```javascript
function throttle(func, limit) {
    let inThrottle;
    return function (...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

window.addEventListener('scroll', throttle(() => {
    // Ejecutar lógica de scroll
}, 100));
```

---

### 6. Compresión de imágenes
**Impact**: 50% reducción de tamaño

```bash
# Instalar ImageMagick
brew install imagemagick

# Comprimir todas las imágenes
mogrify -strip -quality 85 app/frontend/static/images/*.jpg
```

---

## 🎨 Mejoras de UX/UI

### 1. Loading skeletons
**Description**: En lugar de "Cargando...", mostrar esqueleto del contenido

```html
<!-- dashboard.html -->
<div class="recommendations-section">
    <div id="recommendations-skeleton" class="skeleton-grid">
        <div class="skeleton-card"></div>
        <div class="skeleton-card"></div>
        <div class="skeleton-card"></div>
    </div>
    <div id="recommendations-content" style="display: none;"></div>
</div>
```

```css
/* dashboard.css */
.skeleton-card {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: loading 1.5s infinite;
}

@keyframes loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
```

---

### 2. Toast notifications mejoradas
**Description**: Añadir soporte para diferentes tipos

```javascript
// En notification-manager.js (mejorado)
class NotificationManager {
    show(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        // Icons según tipo
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };
        
        toast.innerHTML = `<span>${icons[type]}</span> ${message}`;
        document.body.appendChild(toast);
        
        setTimeout(() => toast.remove(), duration);
    }
}
```

---

### 3. Breadcrumbs navigation
**Description**: Mostrar ruta actual en perfil y detalles

```html
<!-- profile.html -->
<div class="breadcrumbs">
    <a href="/dashboard">Dashboard</a>
    <span>/</span>
    <a href="/profile" class="active">Perfil</a>
</div>
```

---

### 4. Search suggestions
**Description**: Autocomplete en búsqueda

```javascript
async function getSuggestions(query) {
    const response = await apiClient.get('/jobs/suggestions', {
        q: query,
        limit: 5
    });
    return response.data;
}

searchInput.addEventListener('input', async (e) => {
    const suggestions = await getSuggestions(e.target.value);
    displaySuggestions(suggestions);
});
```

---

### 5. Dark mode support
**Description**: Soporte para preferencia del sistema

```css
/* Agregar a CSS */
@media (prefers-color-scheme: dark) {
    :root {
        --bg-color: #1a1a1a;
        --text-color: #ffffff;
        --card-bg: #2d2d2d;
    }
    
    body {
        background-color: var(--bg-color);
        color: var(--text-color);
    }
}
```

---

## 🔒 Seguridad Adicional

### 1. Rate limiting en cliente
**Description**: Prevenir spam de requests

```javascript
class RateLimiter {
    constructor(maxRequests = 10, windowMs = 60000) {
        this.maxRequests = maxRequests;
        this.windowMs = windowMs;
        this.requests = [];
    }
    
    isAllowed() {
        const now = Date.now();
        this.requests = this.requests.filter(t => now - t < this.windowMs);
        
        if (this.requests.length >= this.maxRequests) {
            return false;
        }
        
        this.requests.push(now);
        return true;
    }
}

const limiter = new RateLimiter(5, 10000); // 5 requests en 10s
```

---

### 2. CSRF token en forms
**Description**: Protección contra CSRF attacks

```html
<!-- En templates -->
<form id="profile-form">
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    <!-- otros campos -->
</form>
```

---

### 3. Input sanitization
**Description**: Limpiar input antes de usar

```javascript
function sanitizeHtml(html) {
    const div = document.createElement('div');
    div.textContent = html;
    return div.innerHTML;
}

// Usar al mostrar datos del usuario
userNameElement.innerHTML = sanitizeHtml(user.name);
```

---

### 4. Secure localStorage
**Description**: Encriptar datos sensibles en localStorage

```javascript
// Usar crypto-js (instalar: npm install crypto-js)
import CryptoJS from 'crypto-js';

const SECRET_KEY = process.env.REACT_APP_ENCRYPTION_KEY;

function secureSet(key, value) {
    const encrypted = CryptoJS.AES.encrypt(
        JSON.stringify(value), 
        SECRET_KEY
    ).toString();
    localStorage.setItem(key, encrypted);
}

function secureGet(key) {
    const encrypted = localStorage.getItem(key);
    if (!encrypted) return null;
    
    const decrypted = CryptoJS.AES.decrypt(encrypted, SECRET_KEY).toString(
        CryptoJS.enc.Utf8
    );
    return JSON.parse(decrypted);
}
```

---

## ♿ Accesibilidad

### 1. ARIA labels en iconos
```html
<!-- Login page -->
<button aria-label="Toggle password visibility" class="eye-toggle">
    <i class="icon-eye"></i>
</button>
```

---

### 2. Keyboard navigation
```javascript
// En cada modal/dropdown
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
    }
    if (e.key === 'ArrowDown') {
        focusNext();
    }
    if (e.key === 'ArrowUp') {
        focusPrev();
    }
});
```

---

### 3. Screen reader support
```html
<!-- Usar semantic HTML -->
<nav aria-label="Main navigation">
    <a href="/dashboard">Dashboard</a>
    <a href="/profile">Perfil</a>
</nav>

<main aria-label="Main content">
    <!-- Contenido principal -->
</main>

<aside aria-label="Sidebar">
    <!-- Sidebar -->
</aside>
```

---

### 4. Focus visible
```css
/* Mejorar visible focus para keyboard users */
button:focus,
input:focus,
a:focus {
    outline: 3px solid #0066cc;
    outline-offset: 2px;
}
```

---

## 🧪 Testing Workflow

### 1. Unit Testing (JavaScript)
```bash
# Instalar Jest
npm install --save-dev jest

# Crear test
cat > test/form-validator.test.js << 'EOF'
describe('FormValidator', () => {
    test('should validate email', () => {
        expect(FormValidator.validate('email', 'test@example.com')).toBe(true);
        expect(FormValidator.validate('email', 'invalid')).toBe(false);
    });
});
EOF

# Ejecutar tests
npm test
```

---

### 2. E2E Testing (Cypress)
```bash
# Instalar Cypress
npm install --save-dev cypress

# Crear test
cat > cypress/e2e/login.cy.js << 'EOF'
describe('Login Flow', () => {
    it('should login successfully', () => {
        cy.visit('/login');
        cy.get('input[type="email"]').type('test@example.com');
        cy.get('input[type="password"]').type('TestPass123');
        cy.get('button[type="submit"]').click();
        cy.url().should('include', '/dashboard');
    });
});
EOF

# Ejecutar
npx cypress run
```

---

### 3. Performance Testing (Lighthouse)
```bash
# Instalar Lighthouse CLI
npm install -g lighthouse

# Analizar performance
lighthouse http://localhost:3000/dashboard --view
```

---

## 📋 Checklist de Implementación

### Bugs fixes (Priority: HIGH)
- [ ] Modal scroll fix (1 hora)
- [ ] Token expiration handler (2 horas)
- [ ] Form duplicate submit (30 min)
- [ ] File upload progress (1 hora)

### Performance (Priority: MEDIUM)
- [ ] Minify CSS/JS (30 min)
- [ ] Lazy load recommendations (1 hora)
- [ ] Search debounce (30 min)
- [ ] Image compression (1 hora)

### UX Improvements (Priority: MEDIUM)
- [ ] Loading skeletons (2 horas)
- [ ] Toast notifications (1 hora)
- [ ] Breadcrumbs (30 min)
- [ ] Dark mode (1 hora)

### Security (Priority: HIGH)
- [ ] Rate limiting (1 hora)
- [ ] Input sanitization (1 hora)
- [ ] CSRF protection (1 hora)

### Accessibility (Priority: MEDIUM)
- [ ] ARIA labels (2 horas)
- [ ] Keyboard navigation (1 hora)
- [ ] Focus management (1 hora)

**Total Estimated Time**: 20-22 horas

---

## 🚀 Roadmap de Implementación

**Week 1: Bug Fixes & Security**
- Lunes-Martes: Token expiration + Modal scroll
- Miércoles: Form duplicate + File upload
- Jueves: Rate limiting + Input sanitization
- Viernes: Testing y verificación

**Week 2: Performance & UX**
- Lunes-Martes: Minify + Image optimization
- Miércoles: Loading skeletons + Toast improvements
- Jueves: Debounce + Search
- Viernes: Dark mode + Breadcrumbs

**Week 3: Testing & Optimization**
- Full test coverage
- Performance benchmarks
- Accessibility audit
- Final optimizations

---

## 📊 Success Metrics

- [ ] Lighthouse score: 90+
- [ ] Page load time: < 2s
- [ ] Accessibility score: 95+
- [ ] Zero console errors
- [ ] 100% test coverage (critical paths)
- [ ] Bundle size: < 150KB (minified)

---

**Generated**: 15 de noviembre de 2025  
**Version**: 2.0  
**Next Review**: Después de implementar bugs fixes
