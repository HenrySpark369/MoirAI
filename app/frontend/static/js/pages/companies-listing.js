/**
 * MoirAI - Companies Listing Page
 * Gestiona el listado de empresas usando el modal centralizado (companyModalManager)
 */

// Estado global
let allCompanies = [];
let filteredCompanies = [];
let currentPage = 1;
const itemsPerPage = 9;
let totalCompanies = 0;
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
                        <i class="fas fa-users"></i> ${companyModalManager.getSizeLabel(company.size)}
                    </span>
                </div>
            </div>

            <div class="company-actions">
                <button class="btn btn-small btn-primary" type="button" onclick="openCompanyModal(${company.id}, ${JSON.stringify(company).replace(/"/g, '&quot;')})">
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

    // Notificar al manager de las empresas disponibles
    if (typeof companyModalManager !== 'undefined') {
        companyModalManager.setCompanies(allCompanies);
    }

    console.log(`✅ Renderizado ${pageCompanies.length} empresas en la página ${currentPage}`);
}

/**
 * Ver todos los empleos de la empresa
 */
function viewCompanyAllJobs() {
    if (!companyModalManager.selectedCompany) return;

    companyModalManager.close();
    window.location.href = `/oportunidades?company=${companyModalManager.selectedCompany.id}`;
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
