/**
 * MoirAI - Companies Listing Page
 * Gestiona el listado de empresas y modal de detalles
 */

// Estado global
let allCompanies = [];
let filteredCompanies = [];
let currentPage = 1;
const itemsPerPage = 9;
let totalCompanies = 0;
let selectedCompany = null;
let isDemoMode = false;

// Inicializar página
document.addEventListener('DOMContentLoaded', () => {
    console.log('🏢 Companies Listing: DOMContentLoaded triggered');
    initCompaniesPage();
});

/**
 * Inicializar página
 */
async function initCompaniesPage() {
    try {
        // Detectar modo demo
        const urlParams = new URLSearchParams(window.location.search);
        isDemoMode = urlParams.get('demo') === 'true';

        console.log('🏢 Inicializando página de empresas...');
        console.log('📍 URL:', window.location.href);
        console.log('🎭 Modo demo:', isDemoMode);

        // Esperar a que apiClient esté disponible
        await waitForApiClient();

        // Cargar empresas
        await loadCompanies();

        // Configurar manejadores de eventos
        setupEventHandlers();

        console.log('✅ Página de empresas inicializada correctamente');

    } catch (error) {
        console.error('❌ Error inicializando página de empresas:', error);
    }
}

/**
 * Esperar a que apiClient esté disponible
 */
async function waitForApiClient() {
    return new Promise((resolve) => {
        let attempts = 0;
        const maxAttempts = 50; // 5 segundos máximo

        const checkApiClient = setInterval(() => {
            if (typeof apiClient !== 'undefined') {
                clearInterval(checkApiClient);
                console.log('✅ apiClient disponible');
                resolve();
            } else {
                attempts++;
                if (attempts >= maxAttempts) {
                    clearInterval(checkApiClient);
                    console.warn('⚠️ apiClient no disponible después de 5s, continuando de todas formas');
                    resolve();
                }
            }
        }, 100);
    });
}

/**
 * Cargar empresas desde la API
 */
async function loadCompanies() {
    try {
        console.log('📥 Cargando empresas desde la API...');

        // Usar datos mock por defecto (fallback)
        allCompanies = getMockCompanies();
        totalCompanies = allCompanies.length;

        // Intentar desde endpoint /admin/companies si apiClient está disponible
        if (typeof apiClient !== 'undefined') {
            try {
                console.log('🔍 Intentando cargar desde API...');
                const response = await apiClient.get('/admin/companies');
                if (response && response.companies && response.companies.length > 0) {
                    allCompanies = response.companies;
                    totalCompanies = allCompanies.length;
                    console.log(`✅ ${totalCompanies} empresas cargadas desde API`);
                } else {
                    console.log('⚠️ API retornó datos vacíos, usando mock');
                }
            } catch (apiError) {
                console.warn('⚠️ Error cargando desde API, usando datos mock:', apiError.message);
            }
        } else {
            console.log('⚠️ apiClient no disponible, usando datos mock');
        }

        console.log(`✅ Total empresas disponibles: ${totalCompanies}`);

        // Renderizar primera página
        renderCompaniesGrid();

    } catch (error) {
        console.error('❌ Error cargando empresas:', error);
        allCompanies = getMockCompanies();
        totalCompanies = allCompanies.length;
        renderCompaniesGrid();
    }
}

/**
 * Obtener datos mock de empresas (fallback)
 */
function getMockCompanies() {
    return [
        {
            id: 1,
            name: 'TechCorp Solutions',
            industry: 'Tecnología',
            size: 'grande',
            description: 'Empresa líder en soluciones tecnológicas e innovación digital',
            logo_url: 'https://via.placeholder.com/200?text=TechCorp',
            website: 'https://techcorp.com',
            email: 'careers@techcorp.com',
            phone: '+34 915 234 567',
            address: 'Calle Principal 123, Madrid',
            is_verified: true,
            open_jobs: 12,
            founded_year: 2010,
            employees_count: 500,
            locations: ['Madrid', 'Barcelona', 'Valencia']
        },
        {
            id: 2,
            name: 'DataInc Analytics',
            industry: 'Data Science',
            size: 'pyme',
            description: 'Especialistas en análisis de datos y business intelligence',
            logo_url: 'https://via.placeholder.com/200?text=DataInc',
            website: 'https://datainc.com',
            email: 'info@datainc.com',
            phone: '+34 912 345 678',
            address: 'Avenida Secundaria 456, Barcelona',
            is_verified: true,
            open_jobs: 5,
            founded_year: 2015,
            employees_count: 150,
            locations: ['Barcelona', 'Madrid']
        },
        {
            id: 3,
            name: 'InnovateLab',
            industry: 'Startups',
            size: 'startup',
            description: 'Incubadora de startups y proyectos innovadores',
            logo_url: 'https://via.placeholder.com/200?text=InnovateLab',
            website: 'https://innovatelab.com',
            email: 'hello@innovatelab.com',
            phone: '+34 913 456 789',
            address: 'Plaza Mayor 789, Valencia',
            is_verified: false,
            open_jobs: 8,
            founded_year: 2020,
            employees_count: 80,
            locations: ['Valencia']
        },
        {
            id: 4,
            name: 'ConsultaPro Consulting',
            industry: 'Consultoría',
            size: 'grande',
            description: 'Consultoría empresarial y asesoramiento estratégico',
            logo_url: 'https://via.placeholder.com/200?text=ConsultaPro',
            website: 'https://consultapro.com',
            email: 'contact@consultapro.com',
            phone: '+34 914 567 890',
            address: 'Torre Azul, Madrid',
            is_verified: true,
            open_jobs: 15,
            founded_year: 2000,
            employees_count: 1200,
            locations: ['Madrid', 'Barcelona', 'Valencia', 'Bilbao']
        }
    ];
}

/**
 * Renderizar grid de empresas
 */
function renderCompaniesGrid() {
    const container = document.getElementById('companiesContainer');
    if (!container) {
        console.warn('⚠️ Container #companiesContainer no encontrado');
        return;
    }

    console.log(`🎨 Renderizando empresas: total=${allCompanies.length}, página=${currentPage}`);

    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageCompanies = allCompanies.slice(start, end);

    container.innerHTML = pageCompanies.map(company => `
        <div class="company-card" data-company-id="${company.id}">
            <div class="company-header">
                <div class="company-logo">
                    <img src="${company.logo_url || 'https://via.placeholder.com/100'}" 
                         alt="${company.name}" 
                         onerror="this.src='https://via.placeholder.com/100'">
                </div>
                <div class="company-badges">
                    ${company.is_verified ? '<span class="badge badge-verified"><i class="fas fa-check-circle"></i></span>' : ''}
                </div>
            </div>

            <div class="company-info">
                <h3 class="company-title">${company.name}</h3>
                <p class="company-industry">${company.industry}</p>
                <p class="company-description">${company.description || 'Sin descripción'}</p>

                <div class="company-meta">
                    <span class="meta-item">
                        <i class="fas fa-briefcase"></i> ${company.open_jobs || 0} empleos
                    </span>
                    <span class="meta-item">
                        <i class="fas fa-users"></i> ${getSizeLabel(company.size)}
                    </span>
                </div>
            </div>

            <div class="company-actions">
                <button class="btn btn-small btn-secondary" type="button" onclick="event.preventDefault(); viewCompanyDetails(${company.id}); return false;">
                    <i class="fas fa-eye"></i> Ver Perfil
                </button>
                <button class="btn btn-small btn-primary" type="button" onclick="event.preventDefault(); openCompanyModal(${company.id}); return false;">
                    <i class="fas fa-info-circle"></i> Detalles
                </button>
            </div>
        </div>
    `).join('');

    // Actualizar contador
    const countElement = document.getElementById('companyCount');
    if (countElement) {
        countElement.textContent = totalCompanies;
    }

    console.log(`✅ Renderizado ${pageCompanies.length} empresas en la página ${currentPage}`);
}

/**
 * Obtener etiqueta de tamaño
 */
function getSizeLabel(size) {
    const sizes = {
        'startup': 'Startup',
        'pyme': 'PyME',
        'grande': 'Empresa Grande'
    };
    return sizes[size] || size;
}

/**
 * Abrir modal de detalles de empresa
 */
async function openCompanyModal(companyId) {
    try {
        console.log(`🔓 Intentando abrir modal para empresa ID: ${companyId}`);
        console.log(`📊 Total empresas en lista: ${allCompanies.length}`);
        console.log(`📋 Empresas cargadas:`, allCompanies.map(c => ({ id: c.id, name: c.name })));

        // Encontrar empresa en la lista
        selectedCompany = allCompanies.find(c => c.id === companyId);

        if (!selectedCompany) {
            console.error(`❌ Empresa ${companyId} no encontrada en la lista`);
            alert('Empresa no encontrada');
            return;
        }

        console.log(`📂 Abriendo detalles de empresa: ${selectedCompany.name}`);

        // Llenar modal con datos
        populateCompanyModal(selectedCompany);

        // Mostrar modal
        const modal = document.getElementById('companyModal');
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            console.log('✅ Modal visible');
        } else {
            console.error('❌ Modal no encontrado en el DOM');
        }

    } catch (error) {
        console.error('❌ Error abriendo modal de empresa:', error);
        alert('Error al abrir el modal: ' + error.message);
    }
}

/**
 * Llenar modal con datos de empresa
 */
function populateCompanyModal(company) {
    // Header
    document.getElementById('modalCompanyName').textContent = company.name;
    document.getElementById('modalCompanyIndustry').textContent = company.industry;
    document.getElementById('modalCompanyDescription').textContent = company.description || 'Sin descripción disponible';
    document.getElementById('modalCompanyLogo').src = company.logo_url || 'https://via.placeholder.com/200';

    // Badges
    const verifiedBadge = document.getElementById('modalCompanyVerified');
    if (company.is_verified) {
        verifiedBadge.style.display = 'inline-block';
    } else {
        verifiedBadge.style.display = 'none';
    }

    document.getElementById('modalCompanySize').textContent = getSizeLabel(company.size);

    // Información General
    document.getElementById('infoIndustry').textContent = company.industry;
    document.getElementById('infoSize').textContent = getSizeLabel(company.size);
    document.getElementById('infoEmployees').textContent = (company.employees_count || 'N/A') + ' empleados';
    document.getElementById('infoFounded').textContent = company.founded_year || 'N/A';

    // Website
    const websiteLink = document.getElementById('infoWebsite');
    if (company.website) {
        websiteLink.href = company.website;
        websiteLink.textContent = company.website.replace('https://', '').replace('http://', '');
    } else {
        websiteLink.textContent = 'No disponible';
        websiteLink.href = '#';
    }

    // Estadísticas
    document.getElementById('statOpenJobs').textContent = company.open_jobs || 0;
    document.getElementById('statRegistered').textContent = company.founded_year || '--';
    document.getElementById('statProfile').textContent = '85%'; // Placeholder

    // Contacto
    document.getElementById('modalContactEmail').textContent = company.email || 'No disponible';
    document.getElementById('modalContactPhone').textContent = company.phone || 'No disponible';
    document.getElementById('modalContactAddress').textContent = company.address || 'No disponible';

    // Ubicaciones
    populateLocationsList(company.locations || []);

    // Empleos
    populateJobsList(company.id);

    // Reset a primer tab
    switchCompanyTab('overview');
}

/**
 * Llenar lista de ubicaciones
 */
function populateLocationsList(locations) {
    const container = document.getElementById('modalLocationsList');
    if (!locations || locations.length === 0) {
        container.innerHTML = '<p class="empty-message">No hay ubicaciones registradas</p>';
        return;
    }

    container.innerHTML = locations.map(location => `
        <div class="location-item">
            <i class="fas fa-map-pin"></i>
            <span>${location}</span>
        </div>
    `).join('');
}

/**
 * Llenar lista de empleos
 */
async function populateJobsList(companyId) {
    const container = document.getElementById('modalJobsList');

    try {
        // Intentar cargar empleos de la API
        const response = await apiClient.get(`/companies/${companyId}/jobs`);
        const jobs = response.jobs || [];

        if (jobs.length === 0) {
            container.innerHTML = '<p class="empty-message">Esta empresa no tiene empleos publicados actualmente</p>';
            return;
        }

        container.innerHTML = jobs.slice(0, 5).map(job => `
            <div class="job-item">
                <h4>${job.title}</h4>
                <p class="job-location">
                    <i class="fas fa-map-marker-alt"></i> ${job.location || 'Ubicación no especificada'}
                </p>
                <p class="job-description">${job.description || 'Sin descripción'}</p>
                <div class="job-meta">
                    <span class="job-type">${job.job_type || 'Tiempo Completo'}</span>
                    <span class="job-mode">${job.work_mode || 'Presencial'}</span>
                </div>
            </div>
        `).join('');

    } catch (error) {
        console.warn('⚠️ Error cargando empleos de la empresa:', error);
        container.innerHTML = '<p class="empty-message">No se pudieron cargar los empleos</p>';
    }
}

/**
 * Cambiar tab en el modal
 */
function switchCompanyTab(tabName) {
    // Desactivar todos los tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Activar tab seleccionado
    const tabElement = document.getElementById(`tab-${tabName}`);
    if (tabElement) {
        tabElement.classList.add('active');
    }

    // Marcar botón como activo
    event.target.classList.add('active');

    console.log(`📑 Tab cambiado a: ${tabName}`);
}

/**
 * Cerrar modal de empresa
 */
function closeCompanyModal() {
    const modal = document.getElementById('companyModal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }

    selectedCompany = null;
    console.log('✅ Modal cerrado');
}

/**
 * Ver todos los empleos de la empresa
 */
function viewCompanyAllJobs() {
    if (!selectedCompany) return;

    closeCompanyModal();
    window.location.href = `/oportunidades?company=${selectedCompany.id}`;
}

/**
 * Ver perfil completo de empresa
 */
function viewCompanyDetails(companyId) {
    openCompanyModal(companyId);
}

/**
 * Configurar manejadores de eventos
 */
function setupEventHandlers() {
    // Cerrar modal al hacer clic fuera
    const modal = document.getElementById('companyModal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeCompanyModal();
            }
        });
    }

    // Tecla ESC para cerrar modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeCompanyModal();
        }
    });

    console.log('✅ Event handlers configurados');
}

/**
 * Cambiar vista (grid/list)
 */
function setViewMode(mode) {
    const container = document.getElementById('companiesContainer');
    if (!container) return;

    container.classList.remove('grid-view', 'list-view');
    container.classList.add(`${mode}-view`);

    // Actualizar botones activos
    document.getElementById('gridViewBtn').classList.toggle('active', mode === 'grid');
    document.getElementById('listViewBtn').classList.toggle('active', mode === 'list');

    console.log(`👁️ Vista cambiada a: ${mode}`);
}

/**
 * Navegar a página anterior
 */
function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        renderCompaniesGrid();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

/**
 * Navegar a página siguiente
 */
function nextPage() {
    const totalPages = Math.ceil(totalCompanies / itemsPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        renderCompaniesGrid();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

/**
 * Ir a página específica
 */
function goToPage(page) {
    const totalPages = Math.ceil(totalCompanies / itemsPerPage);
    if (page >= 1 && page <= totalPages) {
        currentPage = page;
        renderCompaniesGrid();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}
