/**
 * MoirAI - Global Company Modal Manager
 * Gestiona el modal de detalles de empresas de manera centralizada
 * Reutilizable en todas las páginas que muestren empresas
 */

class CompanyModalManager {
    constructor() {
        this.modalId = 'companyModal';
        this.selectedCompany = null;
        this.allCompanies = [];
        this.modal = null;
        
        // Inicializar cuando el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    /**
     * Inicializar el manager
     */
    init() {
        console.log('🎯 Inicializando Company Modal Manager');
        
        // Buscar modal en el DOM
        this.modal = document.getElementById(this.modalId);
        
        if (!this.modal) {
            console.warn('⚠️ Modal companyModal no encontrado en el DOM');
            return;
        }

        // Setup event listeners
        this.setupEventListeners();
        console.log('✅ Company Modal Manager inicializado');
    }

    /**
     * Setup de event listeners del modal
     */
    setupEventListeners() {
        // Cerrar modal cuando se hace clic fuera
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });

        // Cerrar con tecla ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('active')) {
                this.close();
            }
        });
    }

    /**
     * Establecer lista de empresas disponibles
     * @param {Array} companies - Lista de empresas
     */
    setCompanies(companies) {
        this.allCompanies = companies || [];
        console.log(`📊 ${this.allCompanies.length} empresas cargadas en Company Modal Manager`);
    }

    /**
     * Abrir modal con detalles de una empresa
     * @param {number|string} companyId - ID de la empresa
     * @param {Object} companyData - Datos de la empresa (opcional, para búsqueda rápida)
     */
    open(companyId, companyData = null) {
        try {
            console.log(`🔓 Abriendo modal para empresa ID: ${companyId}`);

            // Si se proporciona datos directos, usarlos
            let company = companyData;

            // Si no, buscar en la lista
            if (!company && this.allCompanies.length > 0) {
                company = this.allCompanies.find(c => 
                    c.id === companyId || 
                    c.company_id === companyId ||
                    c.company_name === companyId
                );
            }

            if (!company) {
                console.error(`❌ Empresa ${companyId} no encontrada`);
                alert('Empresa no encontrada');
                return;
            }

            this.selectedCompany = company;
            console.log(`📂 Abriendo detalles: ${company.name || company.company_name}`);

            // Llenar modal con datos
            this.populate(company);

            // Mostrar modal
            this.modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            console.log('✅ Modal visible');

        } catch (error) {
            console.error('❌ Error abriendo modal:', error);
            alert('Error al abrir el modal: ' + error.message);
        }
    }

    /**
     * Llenar el modal con datos de la empresa
     * @param {Object} company - Datos de la empresa
     */
    populate(company) {
        // Normalizar datos (soportar múltiples formatos)
        const name = company.name || company.company_name || 'Sin nombre';
        const industry = company.industry || company.sector || 'Sin especificar';
        const description = company.description || company.business_summary || '';
        const logo = company.logo_url || company.logo || 'https://via.placeholder.com/200';
        const verified = company.is_verified || company.verified || false;
        const size = company.size || company.company_size || 'Sin especificar';
        const email = company.email || company.contact_email || '';
        const phone = company.phone || company.contact_phone || '';
        const address = company.address || company.location || '';
        const website = company.website || company.web || '';
        const foundedYear = company.founded_year || company.year_founded || '--';
        const employees = company.employees_count || company.employee_count || '--';
        const jobsCount = company.open_jobs || company.active_jobs || 0;
        const locations = company.locations || [];

        // Rellenar header
        const logoElem = document.getElementById('modalCompanyLogo');
        const nameElem = document.getElementById('modalCompanyName');
        const industryElem = document.getElementById('modalCompanyIndustry');
        const verifiedBadge = document.getElementById('modalCompanyVerified');
        const sizeBadge = document.getElementById('modalCompanySize');

        if (logoElem) logoElem.src = logo;
        if (nameElem) nameElem.textContent = name;
        if (industryElem) industryElem.textContent = industry;
        if (verifiedBadge) verifiedBadge.style.display = verified ? 'inline-block' : 'none';
        if (sizeBadge) {
            sizeBadge.textContent = this.getSizeLabel(size);
            sizeBadge.className = `badge badge-size badge-${this.getSizeCssClass(size)}`;
        }

        // Tab: Overview - Información General
        const descElem = document.getElementById('modalCompanyDescription');
        const infoIndustry = document.getElementById('infoIndustry');
        const infoSize = document.getElementById('infoSize');
        const infoEmployees = document.getElementById('infoEmployees');
        const infoFounded = document.getElementById('infoFounded');
        const infoWebsite = document.getElementById('infoWebsite');

        if (descElem) descElem.textContent = description || 'Sin descripción disponible';
        if (infoIndustry) infoIndustry.textContent = industry;
        if (infoSize) infoSize.textContent = this.getSizeLabel(size);
        if (infoEmployees) infoEmployees.textContent = employees;
        if (infoFounded) infoFounded.textContent = foundedYear;
        if (infoWebsite) {
            if (website) {
                infoWebsite.href = website.startsWith('http') ? website : `https://${website}`;
                infoWebsite.textContent = website;
                infoWebsite.style.display = 'block';
            } else {
                infoWebsite.style.display = 'none';
            }
        }

        // Tab: Overview - Estadísticas
        const statJobs = document.getElementById('statOpenJobs');
        const statRegister = document.getElementById('statRegistered');
        const statProfile = document.getElementById('statProfile');

        if (statJobs) statJobs.textContent = jobsCount;
        if (statRegister) statRegister.textContent = new Date().toLocaleDateString('es-ES');
        if (statProfile) statProfile.textContent = '85%'; // Placeholder

        // Tab: Jobs
        const jobsList = document.getElementById('modalJobsList');
        if (jobsList) {
            if (company.jobs && Array.isArray(company.jobs) && company.jobs.length > 0) {
                jobsList.innerHTML = company.jobs.map(job => `
                    <div class="job-item">
                        <div class="job-title">${this.escapeHtml(job.title || job.position || 'Sin título')}</div>
                        <div class="job-meta">
                            <span><i class="fas fa-map-marker-alt"></i> ${this.escapeHtml(job.location || 'Ubicación no especificada')}</span>
                            ${job.salary ? `<span><i class="fas fa-dollar-sign"></i> ${this.escapeHtml(job.salary)}</span>` : ''}
                        </div>
                    </div>
                `).join('');
            } else {
                jobsList.innerHTML = `
                    <div class="empty-jobs">
                        <i class="fas fa-briefcase"></i>
                        <p>No hay empleos publicados actualmente</p>
                    </div>
                `;
            }
        }

        // Tab: Locations
        const locationsList = document.getElementById('modalLocationsList');
        if (locationsList) {
            if (Array.isArray(locations) && locations.length > 0) {
                locationsList.innerHTML = locations.map(loc => `
                    <div class="location-item">
                        <i class="fas fa-map-pin"></i>
                        <span>${this.escapeHtml(loc)}</span>
                    </div>
                `).join('');
            } else if (address) {
                locationsList.innerHTML = `
                    <div class="location-item">
                        <i class="fas fa-map-pin"></i>
                        <span>${this.escapeHtml(address)}</span>
                    </div>
                `;
            } else {
                locationsList.innerHTML = `
                    <div class="empty-state">
                        <p>Sin información de ubicaciones</p>
                    </div>
                `;
            }
        }

        // Tab: Contact
        const contactEmail = document.getElementById('modalContactEmail');
        const contactPhone = document.getElementById('modalContactPhone');
        const contactAddress = document.getElementById('modalContactAddress');

        if (contactEmail) contactEmail.textContent = email || 'No disponible';
        if (contactPhone) contactPhone.textContent = phone || 'No disponible';
        if (contactAddress) contactAddress.textContent = address || 'No disponible';

        console.log('✅ Modal poblado con datos de empresa');
    }

    /**
     * Cambiar a una pestaña específica
     * @param {string} tabName - Nombre de la pestaña (overview, jobs, locations, contact)
     */
    switchTab(tabName) {
        console.log(`📑 Cambiando a pestaña: ${tabName}`);

        // Desactivar todos los tabs
        const tabs = this.modal.querySelectorAll('.tab-content');
        const buttons = this.modal.querySelectorAll('.tab-btn');

        tabs.forEach(tab => tab.classList.remove('active'));
        buttons.forEach(btn => btn.classList.remove('active'));

        // Activar tab seleccionado
        const selectedTab = document.getElementById(`tab-${tabName}`);
        const selectedBtn = Array.from(buttons).find(btn =>
            btn.textContent.toLowerCase().includes(tabName.toLowerCase()) ||
            btn.onclick?.toString().includes(tabName)
        );

        if (selectedTab) selectedTab.classList.add('active');
        if (selectedBtn) selectedBtn.classList.add('active');
    }

    /**
     * Cerrar modal
     */
    close() {
        console.log('🔒 Cerrando modal de empresa');
        this.modal.classList.remove('active');
        document.body.style.overflow = '';
        this.selectedCompany = null;
    }

    /**
     * Obtener etiqueta de tamaño
     * @param {string} size - Código de tamaño
     * @returns {string} Etiqueta legible
     */
    getSizeLabel(size) {
        const sizes = {
            'startup': 'Startup',
            'pyme': 'PyME',
            'grande': 'Empresa Grande',
            'multinational': 'Multinacional',
            'micro': 'Micro Empresa',
            '1-10': '1-10 empleados',
            '11-50': '11-50 empleados',
            '51-200': '51-200 empleados',
            '200+': '200+ empleados'
        };
        return sizes[size?.toLowerCase()] || size || 'Sin especificar';
    }

    /**
     * Obtener clase CSS para el badge de tamaño
     * @param {string} size - Código de tamaño
     * @returns {string} Clase CSS
     */
    getSizeCssClass(size) {
        const sizeClass = (size?.toLowerCase() || '').replace(/\s+/g, '-');
        return sizeClass || 'unknown';
    }

    /**
     * Escapar HTML para seguridad
     * @param {string} text - Texto a escapar
     * @returns {string} Texto escapado
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Crear instancia global
const companyModalManager = new CompanyModalManager();

// Funciones globales para compatibilidad con onclick handlers
function openCompanyModal(companyId, companyData = null) {
    companyModalManager.open(companyId, companyData);
}

function closeCompanyModal() {
    companyModalManager.close();
}

function switchCompanyTab(tabName) {
    companyModalManager.switchTab(tabName);
}

console.log('✅ Company Modal Manager cargado y disponible globalmente');
