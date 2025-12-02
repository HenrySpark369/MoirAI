# Company Modal Manager - Documentación

## Descripción

`CompanyModalManager` es un gestor centralizado de modales de empresas que proporciona una solución unificada para mostrar detalles de empresas en toda la aplicación MoirAI.

**Ventajas:**
- ✅ Single Source of Truth: Una única implementación del modal
- ✅ Compatible con múltiples formatos de datos
- ✅ Reutilizable en cualquier página (student, company, admin)
- ✅ Funciones globales para compatibilidad con onclick handlers
- ✅ Normalización automática de datos de empresas

## Ubicación

- **Manager:** `/app/frontend/static/js/managers/company-modal-manager.js`
- **Instancia Global:** `companyModalManager`

## Uso Básico

### 1. Cargar el manager en tu template HTML

```html
<!-- Debe cargarse ANTES de scripts específicos de página -->
<script src="/static/js/managers/company-modal-manager.js"></script>
<!-- Luego tus scripts específicos -->
<script src="/static/js/pages/your-page.js"></script>
```

### 2. Mostrar el modal desde un botón

```html
<!-- Opción A: Pasar solo el ID (busca en lista de empresas) -->
<button onclick="openCompanyModal(123)">Ver Detalles</button>

<!-- Opción B: Pasar ID y datos directamente (más rápido) -->
<button onclick="openCompanyModal(123, {...companyData...})">Ver Detalles</button>
```

### 3. Proporcionar lista de empresas al manager

```javascript
// En tu script de página (ej: companies-listing.js, admin-companies.js)
if (typeof companyModalManager !== 'undefined') {
    companyModalManager.setCompanies(allCompanies);
}
```

## Funciones Globales

### `openCompanyModal(companyId, companyData = null)`

Abre el modal con detalles de una empresa.

**Parámetros:**
- `companyId` (number|string): ID de la empresa
- `companyData` (Object, opcional): Datos de la empresa. Si se omite, busca en la lista

**Ejemplo:**
```javascript
openCompanyModal(1);
// o
openCompanyModal(1, {
    id: 1,
    name: 'TechCorp',
    industry: 'Tecnología',
    ...
});
```

### `closeCompanyModal()`

Cierra el modal.

**Ejemplo:**
```javascript
closeCompanyModal();
```

### `switchCompanyTab(tabName)`

Cambia entre pestañas del modal.

**Parámetros:**
- `tabName` (string): Nombre de la pestaña ('overview', 'jobs', 'locations', 'contact')

**Ejemplo:**
```javascript
switchCompanyTab('jobs');
```

## Formato de Datos Soportados

El manager normaliza automáticamente múltiples formatos de datos:

```javascript
// Formato 1: Desde companies-listing.js (students)
{
    id: 1,
    name: 'Company Name',
    industry: 'Tech',
    description: '...',
    logo_url: '...',
    email: '...',
    phone: '...',
    address: '...',
    website: '...',
    is_verified: true,
    size: 'grande',
    open_jobs: 5,
    locations: ['Madrid', 'Barcelona']
}

// Formato 2: Desde admin-companies.js (scraped data)
{
    company_id: 1,
    company_name: 'Company Name',
    industry: 'Tech',
    business_summary: '...',
    email: '...',
    phone: '...',
    locations: '...',
    website: '...',
    is_verified: true,
    company_size: 'grande',
    active_jobs: 5,
    data_source: 'linkedin'
}
```

El manager automáticamente normaliza estos datos a un formato común.

## Integración en Diferentes Contextos

### Para Página de Empresas (`empresas.html`)

```javascript
// En companies-listing.js
await loadCompanies();

// Notificar al manager
companyModalManager.setCompanies(allCompanies);

// Render tarjetas con botón
`<button onclick="openCompanyModal(${company.id}, ${JSON.stringify(company).replace(/"/g, '&quot;')})">
    Detalles
</button>`
```

### Para Admin Dashboard (`admin/dashboard.html`)

```javascript
// En admin-companies.js
this.filteredCompanies = [...companies];

// Notificar al manager
companyModalManager.setCompanies(this.filteredCompanies);

// Render tarjetas con botón
`<button onclick="openCompanyModal('${company.company_id}', ${JSON.stringify(normalizedCompany).replace(/"/g, '&quot;')})">
    Detalles
</button>`
```

### Para Dashboard de Estudiante (`dashboard.html`)

```javascript
// En cualquier script que muestre empresas
if (typeof companyModalManager !== 'undefined') {
    companyModalManager.setCompanies(companies);
}

// Botón
`<button onclick="openCompanyModal(${id})">Ver Empresa</button>`
```

## Modal HTML Requerido

El modal debe estar presente en la página:

```html
<div id="companyModal" class="modal">
    <div class="modal-content company-modal-content">
        <button class="modal-close" onclick="closeCompanyModal()">
            <i class="fas fa-times"></i>
        </button>

        <div class="modal-body">
            <!-- Header -->
            <div class="company-modal-header">
                <div class="company-modal-logo">
                    <img id="modalCompanyLogo" src="" alt="Logo">
                </div>
                <div class="company-modal-title">
                    <h1 id="modalCompanyName"></h1>
                    <p id="modalCompanyIndustry"></p>
                    <div class="company-badges">
                        <span id="modalCompanyVerified" class="badge badge-verified">
                            <i class="fas fa-check-circle"></i> Verificada
                        </span>
                        <span id="modalCompanySize" class="badge badge-size"></span>
                    </div>
                </div>
            </div>

            <!-- Tabs -->
            <div class="company-modal-tabs">
                <button class="tab-btn active" onclick="switchCompanyTab('overview')">
                    <i class="fas fa-info-circle"></i> Información
                </button>
                <button class="tab-btn" onclick="switchCompanyTab('jobs')">
                    <i class="fas fa-briefcase"></i> Empleos
                </button>
                <button class="tab-btn" onclick="switchCompanyTab('locations')">
                    <i class="fas fa-map-marker-alt"></i> Ubicaciones
                </button>
                <button class="tab-btn" onclick="switchCompanyTab('contact')">
                    <i class="fas fa-envelope"></i> Contacto
                </button>
            </div>

            <!-- Tab Content -->
            <div class="company-modal-tabs-content">
                <!-- Tabs filled by manager -->
            </div>

            <!-- Footer -->
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeCompanyModal()">Cerrar</button>
            </div>
        </div>
    </div>
</div>
```

## CSS Requerido

El modal requiere los siguientes estilos en `styles.css`:

- `.modal` y `.modal.active`
- `.modal-content`
- `.company-modal-*` clases
- `.tab-btn`, `.tab-content`
- `.info-grid`, `.stat-card`
- Y más (ver `styles.css`)

## Checklist de Integración

Para integrar el modal en una nueva página:

- [ ] Cargar script `company-modal-manager.js` ANTES del script de página
- [ ] Incluir modal HTML en la template
- [ ] Incluir CSS modal en `<head>`
- [ ] Llamar `companyModalManager.setCompanies(companies)` cuando se carguen empresas
- [ ] Agregar botón "Detalles" en tarjetas que abre el modal
- [ ] Usar `openCompanyModal(id, data)` en botones

## Resolución de Problemas

### Modal no aparece
1. Verificar que `company-modal-manager.js` se cargó (console: `✅ Company Modal Manager cargado`)
2. Verificar que el modal HTML con `id="companyModal"` existe en la página
3. Verificar que CSS modal tiene `.modal.active { display: flex }`

### Datos no se muestran correctamente
1. Verificar formato de datos en la consola
2. Verificar que `setCompanies()` fue llamado
3. Comprobar normalizador de datos en el manager

### Botones no responden
1. Verificar que funciones globales `openCompanyModal()`, `closeCompanyModal()`, `switchCompanyTab()` estén disponibles (definidas en manager)
2. Verificar que onclick handlers tengan sintaxis correcta: `onclick="openCompanyModal(${id})"`
3. Verificar que no haya errores en consola

## Mejoras Futuras

- [ ] Soporte para carga de empleos desde API
- [ ] Caché de datos de empresas
- [ ] Animaciones mejoradas
- [ ] Soporte para múltiples modales simultáneos
- [ ] Historial de empresas vistas

---

**Última actualización:** Diciembre 2025
**Autor:** GitHub Copilot
**Estado:** ✅ Producción
