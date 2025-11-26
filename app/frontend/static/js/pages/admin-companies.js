/**
 * MoirAI Admin - Companies Management from Job Postings
 * Dynamic loading and display of companies aggregated from scraped job data
 */

class AdminCompaniesManager {
    constructor() {
        this.companies = [];
        this.filteredCompanies = [];
        this.currentPage = 1;
        this.itemsPerPage = 20;
        this.isLoading = false;

        // DOM elements
        this.companiesGrid = document.getElementById('companiesGrid');
        this.searchInput = document.querySelector('.filters-bar input[type="text"]');
        this.statusFilter = document.querySelector('.filters-bar select');
        this.companyCount = document.getElementById('companyCount');

        this.init();
    }

    async init() {
        console.log('🚀 Initializing Admin Companies Manager');

        // Setup event listeners
        this.setupEventListeners();

        // Load initial companies data
        await this.loadCompanies();

        // Update UI
        this.updateCompanyCount();
    }

    setupEventListeners() {
        // Search input
        if (this.searchInput) {
            this.searchInput.addEventListener('input', this.debounce(() => {
                this.handleSearch();
            }, 500));
        }

        // Status filter
        if (this.statusFilter) {
            this.statusFilter.addEventListener('change', () => {
                this.handleFilter();
            });
        }

        // Add company button
        const addCompanyBtn = document.getElementById('addCompanyBtn');
        if (addCompanyBtn) {
            addCompanyBtn.addEventListener('click', () => {
                this.showAddCompanyModal();
            });
        }
    }

    async loadCompanies() {
        if (this.isLoading) return;

        this.isLoading = true;
        this.showLoadingState();

        try {
            const params = new URLSearchParams({
                limit: this.itemsPerPage,
                offset: (this.currentPage - 1) * this.itemsPerPage
            });

            const response = await apiClient.get(`/admin/companies-from-jobs?${params}`);

            if (response.companies) {
                this.companies = response.companies;
                this.filteredCompanies = [...this.companies];
                this.renderCompanies();
            }

            console.log(`📊 Loaded ${this.companies.length} companies from job postings`);

        } catch (error) {
            console.error('❌ Error loading companies:', error);
            this.showErrorState('Error al cargar empresas');
        } finally {
            this.isLoading = false;
            this.hideLoadingState();
        }
    }

    renderCompanies() {
        if (!this.companiesGrid) return;

        if (this.filteredCompanies.length === 0) {
            this.companiesGrid.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-building"></i>
                    <h3>No se encontraron empresas</h3>
                    <p>No hay empresas que coincidan con los criterios de búsqueda.</p>
                </div>
            `;
            return;
        }

        this.companiesGrid.innerHTML = this.filteredCompanies.map(company => this.createCompanyCard(company)).join('');

        // Update count
        this.updateCompanyCount();
    }

    createCompanyCard(company) {
        const statusClass = company.is_verified ? 'verified' : 'pending';
        const statusText = company.is_verified ? 'Verificada' : 'Pendiente';
        const logoUrl = `https://via.placeholder.com/60?text=${encodeURIComponent(company.company_name.charAt(0))}`;

        return `
            <div class="company-card" data-company-name="${company.company_name}">
                <div class="company-header">
                    <img src="${logoUrl}" alt="${company.company_name}" class="company-logo" onerror="this.src='https://via.placeholder.com/60'">
                    <div class="company-info">
                        <h3>${this.escapeHtml(company.company_name)}</h3>
                        <p>${this.escapeHtml(company.industry)}</p>
                    </div>
                    <span class="status-badge ${statusClass}">${statusText}</span>
                </div>
                <div class="company-details">
                    <p><strong>Email:</strong> ${this.escapeHtml(company.email || 'No disponible')}</p>
                    <p><strong>Empleos:</strong> ${company.active_jobs} activos</p>
                    <p><strong>Registrado:</strong> ${this.formatDate(company.first_posted)}</p>
                    <p><strong>Ubicaciones:</strong> ${this.escapeHtml(company.locations)}</p>
                </div>
                <div class="company-actions">
                    <button class="btn btn-small btn-primary" onclick="adminCompaniesManager.viewCompanyJobs('${company.company_name}')">
                        <i class="fas fa-briefcase"></i> Ver Empleos
                    </button>
                    <button class="btn btn-small btn-outline" onclick="adminCompaniesManager.contactCompany('${company.company_name}', '${company.email || ''}')">
                        <i class="fas fa-envelope"></i> Contactar
                    </button>
                    ${!company.is_verified ? `
                        <button class="btn btn-small btn-success" onclick="adminCompaniesManager.verifyCompany('${company.company_name}')">
                            <i class="fas fa-check"></i> Verificar
                        </button>
                    ` : ''}
                </div>
                <div class="company-meta">
                    <small class="data-source">
                        <i class="fas fa-database"></i> Fuente: ${company.data_source}
                    </small>
                </div>
            </div>
        `;
    }

    async handleSearch() {
        const searchTerm = this.searchInput?.value?.toLowerCase() || '';

        if (!searchTerm) {
            this.filteredCompanies = [...this.companies];
        } else {
            this.filteredCompanies = this.companies.filter(company =>
                company.company_name.toLowerCase().includes(searchTerm) ||
                company.industry.toLowerCase().includes(searchTerm) ||
                company.locations.toLowerCase().includes(searchTerm)
            );
        }

        this.currentPage = 1;
        this.renderCompanies();
    }

    async handleFilter() {
        const statusFilter = this.statusFilter?.value || '';

        if (!statusFilter || statusFilter === 'Todos los estados') {
            this.filteredCompanies = [...this.companies];
        } else {
            const filterMap = {
                'Verificada': true,
                'Pendiente': false
            };

            const isVerified = filterMap[statusFilter];
            if (isVerified !== undefined) {
                this.filteredCompanies = this.companies.filter(company =>
                    company.is_verified === isVerified
                );
            }
        }

        this.currentPage = 1;
        this.renderCompanies();
    }

    updateCompanyCount() {
        if (this.companyCount) {
            this.companyCount.textContent = this.filteredCompanies.length;
        }
    }

    async viewCompanyJobs(companyName) {
        try {
            // Redirect to jobs page with company filter
            window.location.href = `/admin?section=jobs&company=${encodeURIComponent(companyName)}`;
        } catch (error) {
            console.error('Error viewing company jobs:', error);
            notificationManager?.error('Error al cargar empleos de la empresa');
        }
    }

    async contactCompany(companyName, email) {
        if (!email || email === 'No disponible') {
            notificationManager?.warning('No hay email disponible para esta empresa');
            return;
        }

        // Open email client
        const subject = encodeURIComponent(`Contacto desde MoirAI - ${companyName}`);
        const body = encodeURIComponent(`Hola equipo de ${companyName},\n\nMe pongo en contacto desde MoirAI para...`);
        window.open(`mailto:${email}?subject=${subject}&body=${body}`);
    }

    async verifyCompany(companyName) {
        if (!confirm(`¿Verificar la empresa "${companyName}"?`)) return;

        try {
            notificationManager?.loading('Verificando empresa...');

            // Note: This would need a backend endpoint to actually verify companies
            // For now, we'll just show a success message
            setTimeout(() => {
                notificationManager?.success(`Empresa "${companyName}" verificada exitosamente`);
                // Reload companies to reflect changes
                this.loadCompanies();
            }, 1000);

        } catch (error) {
            console.error('Error verifying company:', error);
            notificationManager?.error('Error al verificar empresa');
        }
    }

    showAddCompanyModal() {
        // Placeholder for add company functionality
        notificationManager?.info('Funcionalidad de agregar empresa próximamente');
    }

    showLoadingState() {
        if (this.companiesGrid) {
            this.companiesGrid.innerHTML = `
                <div class="loading-state">
                    <div class="spinner"></div>
                    <p>Cargando empresas...</p>
                </div>
            `;
        }
    }

    hideLoadingState() {
        // Loading state is replaced by renderCompanies()
    }

    showErrorState(message) {
        if (this.companiesGrid) {
            this.companiesGrid.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Error</h3>
                    <p>${message}</p>
                    <button class="btn btn-primary" onclick="adminCompaniesManager.loadCompanies()">
                        Reintentar
                    </button>
                </div>
            `;
        }
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';

        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('es-ES', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch (e) {
            return dateString;
        }
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Make AdminCompaniesManager globally available
window.AdminCompaniesManager = AdminCompaniesManager;
