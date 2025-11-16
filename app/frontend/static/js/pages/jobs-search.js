/**
 * MoirAI - Jobs Search Page JavaScript
 * Búsqueda y filtrado de empleos con matchmaking inteligente
 */

// Estado global
let currentJobs = [];
let allJobsData = [];
let currentPage = 1;
const itemsPerPage = 12;
let totalJobs = 0;
let isSearchInProgress = false;

// Rate limiter para búsquedas
class SearchRateLimiter {
    constructor(maxRequests = 3, windowMs = 5000) {
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

const searchLimiter = new SearchRateLimiter(3, 5000);

// Inicializar página
document.addEventListener('DOMContentLoaded', () => {
    initJobsSearchPage();
});

/**
 * Inicializar página de búsqueda de empleos
 */
async function initJobsSearchPage() {
    // Proteger ruta - estudiantes y empresas pueden acceder
    if (!authManager.isAuthenticated()) {
        window.location.href = '/login?redirect=/oportunidades';
        return;
    }

    try {
        setupEventListeners();
        await loadInitialJobs();
    } catch (error) {
        notificationManager.error('Error al cargar la página de empleos');
        console.error(error);
    }
}

/**
 * Setup de event listeners
 */
function setupEventListeners() {
    // Búsqueda por texto
    const searchInput = document.getElementById('searchJobs');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 500));
    }

    // Filtros
    const filterElements = document.querySelectorAll(
        '.location-filter, .modality-filter, .level-filter, .skill-filter, ' +
        '#sectorFilter, #sortFilter, #locationFilter'
    );

    filterElements.forEach(element => {
        element.addEventListener('change', handleFilterChange);
    });

    // Botón de filtros avanzados
    const advancedFilterBtn = document.getElementById('advancedFilterBtn');
    if (advancedFilterBtn) {
        advancedFilterBtn.addEventListener('click', toggleAdvancedFilters);
    }

    // Botón de limpiar filtros
    const clearFiltersBtn = document.getElementById('clearFiltersBtn');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', clearAllFilters);
    }

    // Cambio de vista
    const viewModeButtons = document.querySelectorAll('.view-mode-btn');
    viewModeButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            viewModeButtons.forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            const mode = e.target.dataset.mode;
            setViewMode(mode);
        });
    });
}

/**
 * Cargar empleos iniciales
 */
async function loadInitialJobs() {
    notificationManager.loading('Cargando empleos disponibles...');

    try {
        // Obtener empleos destacados o trending
        const response = await apiClient.get('/jobs/trending-jobs?limit=50');
        allJobsData = response.jobs || response.data || [];
        currentJobs = allJobsData;
        totalJobs = allJobsData.length;

        notificationManager.hideLoading();
        renderJobs();

    } catch (error) {
        notificationManager.hideLoading();
        
        // Si no hay endpoint de trending, cargar desde búsqueda general
        try {
            await handleSearch();
        } catch (err) {
            notificationManager.error('Error al cargar empleos');
            console.error(err);
        }
    }
}

/**
 * Realizar búsqueda
 */
async function handleSearch() {
    // Rate limiting
    if (!searchLimiter.isAllowed()) {
        notificationManager.warning('Por favor espera antes de hacer otra búsqueda');
        return;
    }

    if (isSearchInProgress) return;
    isSearchInProgress = true;

    try {
        const keyword = document.getElementById('searchJobs')?.value || '';
        const location = document.getElementById('locationFilter')?.value || '';

        if (!keyword.trim()) {
            notificationManager.warning('Por favor ingresa un término de búsqueda');
            isSearchInProgress = false;
            return;
        }

        notificationManager.loading('Buscando empleos...');

        // Construir query
        let url = `/jobs/search?keyword=${encodeURIComponent(keyword)}&detailed=true`;
        if (location) {
            url += `&location=${encodeURIComponent(location)}`;
        }

        const response = await apiClient.get(url);
        
        allJobsData = response.jobs || response.data || [];
        currentJobs = allJobsData;
        totalJobs = allJobsData.length;
        currentPage = 1;

        notificationManager.hideLoading();

        if (allJobsData.length === 0) {
            notificationManager.info(`No se encontraron empleos para "${keyword}"`);
        } else {
            notificationManager.success(`Se encontraron ${allJobsData.length} empleos`);
        }

        renderJobs();

    } catch (error) {
        notificationManager.hideLoading();
        notificationManager.error(error.message || 'Error al buscar empleos');
        console.error(error);
    } finally {
        isSearchInProgress = false;
    }
}

/**
 * Manejar cambio de filtro
 */
async function handleFilterChange() {
    currentPage = 1; // Resetear a página 1
    await applyFilters();
}

/**
 * Aplicar filtros
 */
async function applyFilters() {
    try {
        const modalities = Array.from(
            document.querySelectorAll('.modality-filter:checked')
        ).map(el => el.value);

        const levels = Array.from(
            document.querySelectorAll('.level-filter:checked')
        ).map(el => el.value);

        const skills = Array.from(
            document.querySelectorAll('.skill-filter:checked')
        ).map(el => el.value);

        const sector = document.getElementById('sectorFilter')?.value || '';
        const sortBy = document.getElementById('sortFilter')?.value || 'recent';

        // Filtrar datos
        let filtered = [...allJobsData];

        // Filtro por modalidad
        if (modalities.length > 0) {
            filtered = filtered.filter(job =>
                modalities.includes(job.work_mode?.toLowerCase())
            );
        }

        // Filtro por nivel
        if (levels.length > 0) {
            filtered = filtered.filter(job =>
                levels.includes(job.level?.toLowerCase())
            );
        }

        // Filtro por habilidades (al menos una coincidencia)
        if (skills.length > 0) {
            filtered = filtered.filter(job => {
                const jobSkills = (job.skills || []).map(s => s.toLowerCase());
                return skills.some(skill =>
                    jobSkills.some(js => js.includes(skill.toLowerCase()))
                );
            });
        }

        // Filtro por sector
        if (sector) {
            filtered = filtered.filter(job =>
                job.sector?.toLowerCase() === sector.toLowerCase()
            );
        }

        // Ordenar
        switch (sortBy) {
            case 'match':
                filtered.sort((a, b) => (b.match_score || 0) - (a.match_score || 0));
                break;
            case 'salary-high':
                filtered.sort((a, b) => {
                    const aSalary = parseInt(b.salary_max || 0);
                    const bSalary = parseInt(a.salary_max || 0);
                    return aSalary - bSalary;
                });
                break;
            case 'salary-low':
                filtered.sort((a, b) => {
                    const aSalary = parseInt(a.salary_min || 0);
                    const bSalary = parseInt(b.salary_min || 0);
                    return aSalary - bSalary;
                });
                break;
            case 'recent':
            default:
                filtered.sort((a, b) =>
                    new Date(b.published_at || 0) - new Date(a.published_at || 0)
                );
        }

        currentJobs = filtered;
        currentPage = 1;
        renderJobs();

    } catch (error) {
        notificationManager.error('Error al aplicar filtros');
        console.error(error);
    }
}

/**
 * Renderizar lista de empleos
 */
function renderJobs() {
    const container = document.getElementById('jobsContainer');
    if (!container) {
        console.warn('Container #jobsContainer no encontrado');
        return;
    }

    // Actualizar contador
    const countElement = document.getElementById('resultsCount');
    if (countElement) {
        countElement.textContent = currentJobs.length;
    }

    // Paginación
    const start = (currentPage - 1) * itemsPerPage;
    const paginatedJobs = currentJobs.slice(start, start + itemsPerPage);

    if (paginatedJobs.length === 0) {
        container.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 3rem 1rem;">
                <i class="fas fa-briefcase" style="font-size: 3rem; color: var(--text-tertiary); margin-bottom: 1rem;"></i>
                <p style="color: var(--text-secondary);">No hay empleos que coincidan con tus filtros</p>
            </div>
        `;
        updatePagination(currentJobs.length);
        return;
    }

    // Renderizar jobs
    container.innerHTML = paginatedJobs.map(job => {
        const matchScore = job.match_score || job.match || 0;
        const matchClass = matchScore >= 75 ? 'high' : matchScore >= 50 ? 'medium' : 'low';

        return `
            <div class="job-card" data-job-id="${job.id || job.job_id}">
                <div class="job-header">
                    <div class="job-info">
                        <h3 class="job-title">${escapeHtml(job.title || 'Sin título')}</h3>
                        <p class="job-company">
                            <i class="fas fa-building"></i>
                            ${escapeHtml(job.company || 'Empresa no disponible')}
                        </p>
                    </div>
                    <span class="job-match match-${matchClass}">
                        ${Math.round(matchScore)}% Match
                    </span>
                </div>

                <div class="job-meta">
                    <div class="job-meta-item">
                        <i class="fas fa-map-marker-alt"></i>
                        ${escapeHtml(job.location || 'Ubicación no especificada')}
                    </div>
                    ${job.work_mode ? `
                        <span class="job-modality ${job.work_mode.toLowerCase()}">
                            ${capitalizeFirst(job.work_mode)}
                        </span>
                    ` : ''}
                    ${job.level ? `
                        <span class="job-level">${capitalizeFirst(job.level)}</span>
                    ` : ''}
                </div>

                ${job.salary_min && job.salary_max ? `
                    <div class="job-salary">
                        <i class="fas fa-money-bill-wave"></i>
                        $${formatNumber(job.salary_min)} - $${formatNumber(job.salary_max)}
                        ${job.currency || 'MXN'}
                    </div>
                ` : ''}

                <p class="job-description">
                    ${escapeHtml((job.description || '').substring(0, 150))}...
                </p>

                ${job.skills && job.skills.length > 0 ? `
                    <div class="job-skills">
                        ${job.skills.slice(0, 3).map(skill => `
                            <span class="skill-tag">${escapeHtml(skill)}</span>
                        `).join('')}
                        ${job.skills.length > 3 ? `
                            <span class="skill-tag">+${job.skills.length - 3} más</span>
                        ` : ''}
                    </div>
                ` : ''}

                <div class="job-actions">
                    <button class="btn btn-secondary" onclick="viewJobDetail('${job.id || job.job_id}')">
                        <i class="fas fa-eye"></i> Ver Detalles
                    </button>
                    <button class="btn btn-primary" onclick="applyForJob('${job.id || job.job_id}')">
                        <i class="fas fa-paper-plane"></i> Aplicar
                    </button>
                </div>
            </div>
        `;
    }).join('');

    updatePagination(currentJobs.length);
}

/**
 * Ver detalles de un empleo
 */
async function viewJobDetail(jobId) {
    try {
        // Buscar en datos locales primero
        let job = allJobsData.find(j => j.id === jobId || j.job_id === jobId);

        if (!job) {
            notificationManager.loading('Cargando detalles del empleo...');

            // Obtener del API si no está en local
            const response = await apiClient.get(`/jobs/${jobId}`);
            job = response.job || response.data;

            notificationManager.hideLoading();
        }

        // Abrir modal con detalles
        openJobDetailsModal(job);

    } catch (error) {
        notificationManager.hideLoading();
        notificationManager.error('Error al cargar los detalles del empleo');
        console.error(error);
    }
}

/**
 * Abrir modal con detalles del empleo
 */
function openJobDetailsModal(job) {
    const modal = document.createElement('div');
    modal.className = 'modal modal-job-details';
    modal.id = 'jobDetailsModal';

    const matchScore = job.match_score || job.match || 0;
    const matchClass = matchScore >= 75 ? 'high' : matchScore >= 50 ? 'medium' : 'low';

    modal.innerHTML = `
        <div class="modal-content">
            <span class="close-modal" onclick="document.getElementById('jobDetailsModal')?.remove()">&times;</span>

            <div class="modal-header-job">
                <div class="job-title-section">
                    <h1>${escapeHtml(job.title)}</h1>
                    <p class="job-company-modal">
                        <i class="fas fa-building"></i> ${escapeHtml(job.company)}
                    </p>
                </div>
                <span class="job-match-modal match-${matchClass}">
                    ${Math.round(matchScore)}% Match
                </span>
            </div>

            <div class="modal-body-job">
                <div class="job-details-grid">
                    <div class="detail-section">
                        <h3>Información General</h3>
                        <div class="detail-item">
                            <strong>Ubicación:</strong>
                            <span><i class="fas fa-map-marker-alt"></i> ${escapeHtml(job.location)}</span>
                        </div>
                        <div class="detail-item">
                            <strong>Modalidad:</strong>
                            <span class="job-modality ${job.work_mode?.toLowerCase()}">
                                ${capitalizeFirst(job.work_mode)}
                            </span>
                        </div>
                        <div class="detail-item">
                            <strong>Nivel:</strong>
                            <span>${capitalizeFirst(job.level || 'No especificado')}</span>
                        </div>
                        <div class="detail-item">
                            <strong>Tipo de Contrato:</strong>
                            <span>${capitalizeFirst(job.job_type || 'No especificado')}</span>
                        </div>
                    </div>

                    <div class="detail-section">
                        <h3>Compensación</h3>
                        ${job.salary_min && job.salary_max ? `
                            <div class="detail-item">
                                <strong>Rango Salarial:</strong>
                                <span>$${formatNumber(job.salary_min)} - $${formatNumber(job.salary_max)} ${job.currency || 'MXN'}</span>
                            </div>
                        ` : '<p>No especificado</p>'}
                    </div>

                    ${job.benefits && job.benefits.length > 0 ? `
                        <div class="detail-section">
                            <h3>Beneficios</h3>
                            <ul class="benefits-list">
                                ${job.benefits.slice(0, 5).map(benefit => `
                                    <li><i class="fas fa-check"></i> ${escapeHtml(benefit)}</li>
                                `).join('')}
                            </ul>
                        </div>
                    ` : ''}

                    ${job.skills && job.skills.length > 0 ? `
                        <div class="detail-section">
                            <h3>Habilidades Requeridas</h3>
                            <div class="skills-grid">
                                ${job.skills.map(skill => `
                                    <span class="skill-tag">${escapeHtml(skill)}</span>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>

                <div class="detail-section full-width">
                    <h3>Descripción del Puesto</h3>
                    <div class="job-description-full">
                        ${escapeHtml(job.description || 'No disponible')}
                    </div>
                </div>

                ${job.requirements ? `
                    <div class="detail-section full-width">
                        <h3>Requisitos</h3>
                        <div class="job-requirements">
                            ${escapeHtml(job.requirements)}
                        </div>
                    </div>
                ` : ''}
            </div>

            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="document.getElementById('jobDetailsModal')?.remove()">
                    Cerrar
                </button>
                <button class="btn btn-primary" onclick="applyForJob('${job.id || job.job_id}')">
                    <i class="fas fa-paper-plane"></i> Solicitar Empleo
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    modal.style.display = 'flex';
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

/**
 * Aplicar a un empleo
 */
async function applyForJob(jobId) {
    try {
        // Verificar autenticación
        if (!authManager.isAuthenticated()) {
            window.location.href = '/login?redirect=/oportunidades';
            return;
        }

        const userId = authManager.getUserId();
        if (!userId) {
            notificationManager.error('No se pudo identificar tu usuario');
            return;
        }

        notificationManager.loading('Procesando solicitud...');

        // Crear aplicación
        const response = await apiClient.post('/applications', {
            student_id: userId,
            job_position_id: jobId
        });

        notificationManager.hideLoading();
        notificationManager.success('¡Solicitud enviada exitosamente!');

        // Cerrar modal si está abierto
        const modal = document.getElementById('jobDetailsModal');
        if (modal) modal.remove();

        // Cambiar estado del botón
        const applyBtn = document.querySelector(`button[onclick="applyForJob('${jobId}')"]`);
        if (applyBtn) {
            applyBtn.disabled = true;
            applyBtn.textContent = '✓ Solicitado';
            applyBtn.classList.add('applied');
        }

    } catch (error) {
        notificationManager.hideLoading();

        if (error.status === 409) {
            notificationManager.warning('Ya has solicitado este empleo');
        } else if (error.status === 401) {
            window.location.href = '/login?redirect=/oportunidades';
        } else {
            notificationManager.error(error.message || 'Error al enviar solicitud');
        }

        console.error(error);
    }
}

/**
 * Alternar filtros avanzados
 */
function toggleAdvancedFilters() {
    const filtersSection = document.querySelector('.advanced-filters');
    if (filtersSection) {
        filtersSection.classList.toggle('visible');
    }
}

/**
 * Limpiar todos los filtros
 */
function clearAllFilters() {
    // Limpiar inputs
    document.getElementById('searchJobs').value = '';
    document.getElementById('locationFilter').value = '';
    document.getElementById('sectorFilter').value = '';
    document.getElementById('sortFilter').value = 'recent';

    // Desmarcar checkboxes
    document.querySelectorAll(
        '.modality-filter, .level-filter, .skill-filter'
    ).forEach(checkbox => {
        checkbox.checked = false;
    });

    // Resetear datos
    currentJobs = allJobsData;
    currentPage = 1;

    renderJobs();
    notificationManager.info('Filtros limpios');
}

/**
 * Cambiar modo de vista
 */
function setViewMode(mode) {
    const container = document.getElementById('jobsContainer');
    if (container) {
        container.className = 'jobs-container';
        container.classList.add(`view-${mode}`);
    }
}

/**
 * Actualizar paginación
 */
function updatePagination(totalItems) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const pageInfo = document.getElementById('pageInfo');

    if (pageInfo) {
        if (totalPages === 0) {
            pageInfo.textContent = 'Sin resultados';
        } else {
            pageInfo.textContent = `Página ${currentPage} de ${totalPages}`;
        }
    }

    // Botones de navegación
    const prevBtn = document.getElementById('prevPageBtn');
    const nextBtn = document.getElementById('nextPageBtn');

    if (prevBtn) prevBtn.disabled = currentPage === 1;
    if (nextBtn) nextBtn.disabled = currentPage === totalPages || totalPages === 0;
}

/**
 * Página anterior
 */
function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        renderJobs();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

/**
 * Página siguiente
 */
function nextPage() {
    const totalPages = Math.ceil(currentJobs.length / itemsPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        renderJobs();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

/**
 * Debounce para búsqueda
 */
function debounce(func, delay) {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func(...args), delay);
    };
}

/**
 * Utilidades
 */
function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function capitalizeFirst(text) {
    if (!text) return '';
    return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
}

function formatNumber(num) {
    if (!num) return '0';
    return parseInt(num).toLocaleString('es-MX');
}
