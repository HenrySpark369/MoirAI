/**
 * MoirAI - Applications Page JavaScript
 * Gestión de solicitudes de empleo del usuario
 */

let applications = [];
let filteredApplications = [];
let currentPage = 1;
const itemsPerPage = 10;
let currentFilter = 'all';

document.addEventListener('DOMContentLoaded', () => {
    initApplicationsPage();
});

/**
 * Inicializar página de aplicaciones
 */
async function initApplicationsPage() {
    // Detectar si estamos en modo demo
    const urlParams = new URLSearchParams(window.location.search);
    const isDemo = urlParams.get('demo') === 'true';
    const userRole = urlParams.get('role') || storageManager.getUserRole();
    
    // Proteger ruta - permitir estudiantes y empresas en demo
    const allowedRoles = isDemo ? ['student', 'company'] : ['student'];
    
    await protectedPageManager.initProtectedPage({
        requiredRoles: allowedRoles,
        redirectOnUnauth: '/login?redirect=/applications',
        redirectOnUnauthorized: '/dashboard',
        loadingMessage: 'Cargando aplicaciones...',
        onInit: async () => {
            await loadApplications();
            setupEventListeners();
        }
    });
}

/**
 * Cargar aplicaciones del usuario
 */
async function loadApplications() {
    try {
        // Detectar modo demo y rol
        const urlParams = new URLSearchParams(window.location.search);
        const isDemo = urlParams.get('demo') === 'true';
        const userRole = urlParams.get('role') || storageManager.getUserRole();
        
        let response;
        
        if (isDemo && userRole === 'company') {
            // Cargar aplicaciones demo para empresas
            response = await apiClient.get('/companies/demo/applications');
            applications = response.applications || [];
            
            // Actualizar título de la página para empresas
            const headerTitle = document.querySelector('.applications-header h1');
            if (headerTitle) {
                headerTitle.innerHTML = '<i class="fas fa-users"></i> Aplicaciones Recibidas';
            }
            const headerDesc = document.querySelector('.applications-header p');
            if (headerDesc) {
                headerDesc.textContent = 'Gestiona las aplicaciones de estudiantes a tus vacantes';
            }
            
        } else {
            // Cargar aplicaciones del estudiante
            if (isDemo) {
                // Usar endpoint demo para estudiantes
                response = await apiClient.get('/students/demo/applications');
            } else {
                // Comportamiento original para estudiantes autenticados
                response = await apiClient.get('/students/my-applications');
            }
            applications = response.applications || response.data || [];
        }

        // Organizar por estado
        applications.forEach(app => {
            // Normalizar fecha
            if (app.created_at) {
                app.created_date = new Date(app.created_at).toLocaleDateString('es-MX');
            }
            if (app.updated_at) {
                app.updated_date = new Date(app.updated_at).toLocaleDateString('es-MX');
            }
        });

        filteredApplications = applications;
        renderApplications();

        // Actualizar estadísticas
        updateStats();

    } catch (error) {
        console.error('Error loading applications:', error);
        throw error;
    }
}

/**
 * Setup de event listeners
 */
function setupEventListeners() {
    // Filtros por estado
    const filterButtons = document.querySelectorAll('.app-filter-btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            filterButtons.forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentFilter = e.target.dataset.filter;
            filterApplicationsByStatus();
        });
    });

    // Búsqueda
    const searchInput = document.getElementById('searchApplications');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterApplicationsBySearch, 300));
    }

    // Ordenamiento
    const sortSelect = document.getElementById('sortApplications');
    if (sortSelect) {
        sortSelect.addEventListener('change', sortApplications);
    }
}

/**
 * Filtrar aplicaciones por estado
 */
function filterApplicationsByStatus() {
    currentPage = 1;

    if (currentFilter === 'all') {
        filteredApplications = applications;
    } else {
        filteredApplications = applications.filter(app =>
            (app.status || 'pending').toLowerCase() === currentFilter.toLowerCase()
        );
    }

    renderApplications();
}

/**
 * Filtrar por búsqueda
 */
function filterApplicationsBySearch() {
    const searchTerm = document.getElementById('searchApplications')?.value.toLowerCase() || '';
    currentPage = 1;

    if (!searchTerm) {
        filterApplicationsByStatus();
        return;
    }

    const basedApps = currentFilter === 'all' ? applications : applications.filter(app =>
        (app.status || 'pending').toLowerCase() === currentFilter.toLowerCase()
    );

    filteredApplications = basedApps.filter(app =>
        (app.job_title || '').toLowerCase().includes(searchTerm) ||
        (app.company || '').toLowerCase().includes(searchTerm)
    );

    renderApplications();
}

/**
 * Ordenar aplicaciones
 */
function sortApplications() {
    const sortBy = document.getElementById('sortApplications')?.value || 'recent';

    switch (sortBy) {
        case 'recent':
            filteredApplications.sort((a, b) =>
                new Date(b.created_at || 0) - new Date(a.created_at || 0)
            );
            break;
        case 'oldest':
            filteredApplications.sort((a, b) =>
                new Date(a.created_at || 0) - new Date(b.created_at || 0)
            );
            break;
        case 'updated':
            filteredApplications.sort((a, b) =>
                new Date(b.updated_at || 0) - new Date(a.updated_at || 0)
            );
            break;
    }

    currentPage = 1;
    renderApplications();
}

/**
 * Renderizar lista de aplicaciones
 */
function renderApplications() {
    const container = document.getElementById('applicationsContainer');
    if (!container) return;

    // Detectar modo demo y rol
    const urlParams = new URLSearchParams(window.location.search);
    const isDemo = urlParams.get('demo') === 'true';
    const userRole = urlParams.get('role') || storageManager.getUserRole();
    const isCompanyView = isDemo && userRole === 'company';

    // Actualizar contador
    const countElement = document.getElementById('applicationsCount');
    if (countElement) {
        countElement.textContent = filteredApplications.length;
    }

    // Paginación
    const start = (currentPage - 1) * itemsPerPage;
    const paginatedApps = filteredApplications.slice(start, start + itemsPerPage);

    if (paginatedApps.length === 0) {
        const emptyMessage = isCompanyView 
            ? 'Aún no has recibido aplicaciones. <a href="/buscar-candidatos">Busca candidatos aquí</a>'
            : 'Aún no has enviado solicitudes. <a href="/oportunidades">Busca empleos aquí</a>';
            
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <h3>Sin aplicaciones</h3>
                <p>${currentFilter !== 'all' ? 'Cambia los filtros para ver más.' : emptyMessage}</p>
            </div>
        `;
        updatePagination(0);
        return;
    }

    container.innerHTML = paginatedApps.map((app, idx) => {
        const statusConfig = getStatusConfig(app.status || 'pending');
        const isExpired = app.expires_at && new Date(app.expires_at) < new Date();

        if (isCompanyView) {
            // Render para empresas: mostrar aplicaciones de estudiantes
            return `
                <div class="application-card" data-app-id="${app.application_id}">
                    <div class="app-header">
                        <div class="app-title-section">
                            <h3>${escapeHtml(app.name || 'Candidato sin nombre')}</h3>
                            <p class="app-company">${escapeHtml(app.program || 'Programa no disponible')} • ${escapeHtml(app.job_title || 'Vacante')}</p>
                        </div>
                        <span class="app-status status-${statusConfig.class}">
                            <i class="${statusConfig.icon}"></i> ${statusConfig.label}
                        </span>
                    </div>

                    <div class="app-meta">
                        <div class="meta-item">
                            <strong>Match Score:</strong>
                            <span>${app.match_score || 0}%</span>
                        </div>
                        <div class="meta-item">
                            <strong>Aplicado:</strong>
                            <span>${new Date(app.applied_date).toLocaleDateString('es-MX')}</span>
                        </div>
                        <div class="meta-item">
                            <strong>Email:</strong>
                            <span>${escapeHtml(app.email || 'N/A')}</span>
                        </div>
                    </div>

                    ${app.skills && app.skills.length > 0 ? `
                        <div class="app-skills">
                            <strong>Habilidades:</strong>
                            <div class="skills-list">
                                ${app.skills.slice(0, 5).map(skill => `<span class="skill-tag">${escapeHtml(skill)}</span>`).join('')}
                                ${app.skills.length > 5 ? `<span class="skill-tag">+${app.skills.length - 5} más</span>` : ''}
                            </div>
                        </div>
                    ` : ''}

                    <div class="app-actions">
                        <button class="btn btn-secondary" onclick="viewStudentProfile(${app.student_id})">
                            <i class="fas fa-user"></i> Ver Perfil
                        </button>
                        <button class="btn btn-primary" onclick="updateApplicationStatus(${app.application_id}, 'accepted')">
                            <i class="fas fa-check"></i> Aceptar
                        </button>
                        <button class="btn btn-danger" onclick="updateApplicationStatus(${app.application_id}, 'rejected')">
                            <i class="fas fa-times"></i> Rechazar
                        </button>
                    </div>
                </div>
            `;
        } else {
            // Render original para estudiantes: mostrar aplicaciones enviadas
            return `
                <div class="application-card" data-app-id="${app.id}">
                    <div class="app-header">
                        <div class="app-title-section">
                            <h3>${escapeHtml(app.job_title || 'Empleo sin título')}</h3>
                            <p class="app-company">${escapeHtml(app.company || 'Empresa no disponible')}</p>
                        </div>
                        <span class="app-status status-${statusConfig.class}">
                            <i class="${statusConfig.icon}"></i> ${statusConfig.label}
                        </span>
                    </div>

                    <div class="app-meta">
                        <div class="meta-item">
                            <strong>Solicitado:</strong>
                            <span>${app.created_date || 'N/A'}</span>
                        </div>
                        <div class="meta-item">
                            <strong>Actualizado:</strong>
                            <span>${app.updated_date || app.created_date || 'N/A'}</span>
                        </div>
                        ${app.location ? `
                            <div class="meta-item">
                                <i class="fas fa-map-marker-alt"></i>
                                <span>${escapeHtml(app.location)}</span>
                            </div>
                        ` : ''}
                    </div>

                    ${isExpired ? `
                        <div class="app-warning">
                            <i class="fas fa-exclamation-triangle"></i>
                            <span>Esta oferta ha expirado</span>
                        </div>
                    ` : ''}

                    ${app.notes ? `
                        <div class="app-notes">
                            <strong>Notas:</strong>
                            <p>${escapeHtml(app.notes)}</p>
                        </div>
                    ` : ''}

                    ${app.feedback ? `
                        <div class="app-feedback">
                            <strong>Retroalimentación:</strong>
                            <p>${escapeHtml(app.feedback)}</p>
                        </div>
                    ` : ''}

                    <div class="app-actions">
                        <button class="btn btn-secondary" onclick="viewApplicationDetail('${app.id}')">
                            <i class="fas fa-eye"></i> Ver Detalles
                        </button>
                        ${['pending', 'pending_review'].includes((app.status || 'pending').toLowerCase()) ? `
                            <button class="btn btn-danger" onclick="withdrawApplication('${app.id}')">
                                <i class="fas fa-times"></i> Retirar
                            </button>
                        ` : ''}
                    </div>
                </div>
            `;
        }
    }).join('');

    updatePagination(filteredApplications.length);
}/**
 * Ver perfil de estudiante (para empresas)
 */
async function viewStudentProfile(studentId) {
    try {
        notificationManager.info('Funcionalidad de ver perfil próximamente disponible');
        // TODO: Implementar vista de perfil de estudiante
        console.log('Ver perfil de estudiante:', studentId);
    } catch (error) {
        console.error('Error al ver perfil:', error);
        notificationManager.error('Error al cargar perfil del estudiante');
    }
}

/**
 * Actualizar estado de aplicación (para empresas)
 */
async function updateApplicationStatus(applicationId, newStatus) {
    try {
        notificationManager.loading('Actualizando estado...');
        
        // TODO: Implementar endpoint para actualizar estado
        // await apiClient.put(`/companies/applications/${applicationId}/status`, { status: newStatus });
        
        // Simular actualización por ahora
        setTimeout(() => {
            notificationManager.hideLoading();
            notificationManager.success(`Aplicación ${newStatus === 'accepted' ? 'aceptada' : 'rechazada'} exitosamente`);
            
            // Actualizar estado localmente
            const app = applications.find(a => a.application_id === applicationId);
            if (app) {
                app.status = newStatus;
                filterApplicationsByStatus(); // Re-filtrar para actualizar vista
            }
        }, 1000);
        
    } catch (error) {
        console.error('Error al actualizar estado:', error);
        notificationManager.hideLoading();
        notificationManager.error('Error al actualizar estado de la aplicación');
    }
}

/**
 * Ver detalles de una aplicación
 */
async function viewApplicationDetail(appId) {
    try {
        const app = applications.find(a => a.id === appId);
        if (!app) {
            notificationManager.error('Aplicación no encontrada');
            return;
        }

        // Obtener detalles completos del empleo
        let jobDetails = null;
        if (app.job_id) {
            try {
                const jobResponse = await apiClient.get(`/jobs/${app.job_id}`);
                jobDetails = jobResponse;
            } catch (error) {
                console.warn('No se pudieron obtener detalles adicionales del empleo:', error);
                // Continuar con la información básica disponible
            }
        }

        const statusConfig = getStatusConfig(app.status || 'pending');

        const modal = document.createElement('div');
        modal.className = 'modal modal-app-details';
        modal.id = `appDetailsModal-${appId}`;

        // Usar detalles del empleo si están disponibles, sino usar datos básicos
        const jobTitle = jobDetails?.title || app.job_title || 'Empleo sin título';
        const jobCompany = jobDetails?.company || app.company || 'Empresa';
        const jobLocation = jobDetails?.location || app.location || 'Ubicación no especificada';
        const jobDescription = jobDetails?.description || 'Descripción no disponible';
        const jobSkills = jobDetails?.skills || [];
        const jobWorkMode = jobDetails?.work_mode || 'No especificado';
        const jobType = jobDetails?.job_type || 'No especificado';
        const jobSalaryMin = jobDetails?.salary_min || app.salary_min;
        const jobSalaryMax = jobDetails?.salary_max || app.salary_max;
        const jobCurrency = jobDetails?.currency || app.currency || 'MXN';

        modal.innerHTML = `
            <div class="modal-content">
                <span class="close-modal" onclick="document.getElementById('appDetailsModal-${appId}')?.remove()">&times;</span>

                <div class="modal-header-app">
                    <div>
                        <h1>${escapeHtml(jobTitle)}</h1>
                        <p class="app-company-modal">${escapeHtml(jobCompany)}</p>
                    </div>
                    <span class="app-status status-${statusConfig.class} status-large">
                        ${statusConfig.label}
                    </span>
                </div>

                <div class="modal-body-app">
                    <div class="app-info-grid">
                        <div class="info-section">
                            <h3>Información de la Solicitud</h3>
                            <div class="info-item">
                                <strong>Estado:</strong>
                                <span>${statusConfig.label}</span>
                            </div>
                            <div class="info-item">
                                <strong>Fecha de Solicitud:</strong>
                                <span>${app.applied_date ? new Date(app.applied_date).toLocaleDateString('es-MX') : 'N/A'}</span>
                            </div>
                            <div class="info-item">
                                <strong>Última Actualización:</strong>
                                <span>${app.updated_date ? new Date(app.updated_date).toLocaleDateString('es-MX') : (app.applied_date ? new Date(app.applied_date).toLocaleDateString('es-MX') : 'N/A')}</span>
                            </div>
                            ${app.match_score ? `
                                <div class="info-item">
                                    <strong>Compatibilidad:</strong>
                                    <span class="match-score-display">${app.match_score}%</span>
                                </div>
                            ` : ''}
                        </div>

                        <div class="info-section">
                            <h3>Detalles del Empleo</h3>
                            <div class="info-item">
                                <i class="fas fa-map-marker-alt"></i>
                                <span>${escapeHtml(jobLocation)}</span>
                            </div>
                            <div class="info-item">
                                <i class="fas fa-briefcase"></i>
                                <span>${escapeHtml(jobType)}</span>
                            </div>
                            <div class="info-item">
                                <i class="fas fa-building"></i>
                                <span>${escapeHtml(jobWorkMode)}</span>
                            </div>
                            ${jobSalaryMin ? `
                                <div class="info-item">
                                    <i class="fas fa-dollar-sign"></i>
                                    <span>$${jobSalaryMin.toLocaleString()} - $${jobSalaryMax.toLocaleString()} ${jobCurrency}</span>
                                </div>
                            ` : ''}
                        </div>
                    </div>

                    ${jobDescription && jobDescription !== 'Descripción no disponible' ? `
                        <div class="app-section">
                            <h3>Descripción del Empleo</h3>
                            <div class="job-description">
                                ${jobDescription.split('\n').map(line => `<p>${escapeHtml(line)}</p>`).join('')}
                            </div>
                        </div>
                    ` : ''}

                    ${jobSkills && jobSkills.length > 0 ? `
                        <div class="app-section">
                            <h3>Habilidades Requeridas</h3>
                            <div class="skills-list">
                                ${jobSkills.map(skill => `<span class="skill-tag">${escapeHtml(skill)}</span>`).join('')}
                            </div>
                        </div>
                    ` : ''}

                    ${app.notes ? `
                        <div class="app-section">
                            <h3>Mis Notas</h3>
                            <p>${escapeHtml(app.notes)}</p>
                        </div>
                    ` : ''}

                    ${app.feedback ? `
                        <div class="app-section feedback">
                            <h3>Retroalimentación de la Empresa</h3>
                            <p>${escapeHtml(app.feedback)}</p>
                        </div>
                    ` : ''}

                    ${app.job_description ? `
                        <div class="app-section">
                            <h3>Descripción del Puesto</h3>
                            <div class="job-desc-text">
                                ${escapeHtml(app.job_description)}
                            </div>
                        </div>
                    ` : ''}
                </div>

                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="document.getElementById('appDetailsModal-${appId}')?.remove()">
                        Cerrar
                    </button>
                    ${['pending', 'pending_review'].includes((app.status || 'pending').toLowerCase()) ? `
                        <button class="btn btn-outline" onclick="editApplicationNotes(${appId})">
                            <i class="fas fa-edit"></i> Editar Notas
                        </button>
                        <button class="btn btn-danger" onclick="withdrawApplication(${appId})">
                            <i class="fas fa-times"></i> Retirar Solicitud
                        </button>
                    ` : ''}
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        modal.style.display = 'flex';
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });

    } catch (error) {
        notificationManager.error('Error al cargar detalles');
        console.error(error);
    }
}

/**
 * Editar notas de la aplicación
 */
async function editApplicationNotes(appId) {
    const app = applications.find(a => a.id === appId);
    if (!app) return;

    const newNotes = prompt('Editar notas:', app.notes || '');
    if (newNotes === null) return; // Cancelado

    try {
        notificationManager.loading('Guardando notas...');

        await apiClient.put(`/applications/${appId}`, {
            notes: newNotes
        });

        app.notes = newNotes;
        notificationManager.hideLoading();
        notificationManager.success('Notas actualizadas');

        // Cerrar modal y actualizar
        const modal = document.getElementById(`appDetailsModal-${appId}`);
        if (modal) modal.remove();
        renderApplications();

    } catch (error) {
        notificationManager.hideLoading();
        notificationManager.error('Error al guardar notas');
        console.error(error);
    }
}

/**
 * Retirar una aplicación
 */
async function withdrawApplication(appId) {
    if (!confirm('¿Está seguro de que desea retirar esta solicitud?')) {
        return;
    }

    try {
        notificationManager.loading('Retirando solicitud...');

        await apiClient.delete(`/students/applications/${appId}`);

        applications = applications.filter(a => a.id !== appId);
        filteredApplications = filteredApplications.filter(a => a.id !== appId);

        notificationManager.hideLoading();
        notificationManager.success('Solicitud retirada');

        // Cerrar modal si está abierto
        const modal = document.getElementById(`appDetailsModal-${appId}`);
        if (modal) modal.remove();

        renderApplications();
        updateStats();

    } catch (error) {
        notificationManager.hideLoading();
        notificationManager.error('Error al retirar solicitud');
        console.error(error);
    }
}

/**
 * Actualizar estadísticas
 */
function updateStats() {
    const stats = {
        total: applications.length,
        pending: applications.filter(a => ['pending', 'pending_review'].includes((a.status || 'pending').toLowerCase())).length,
        accepted: applications.filter(a => (a.status || '').toLowerCase() === 'accepted').length,
        rejected: applications.filter(a => (a.status || '').toLowerCase() === 'rejected').length
    };

    document.getElementById('totalApplications').textContent = stats.total;
    document.getElementById('pendingApplications').textContent = stats.pending;
    document.getElementById('acceptedApplications').textContent = stats.accepted;
    document.getElementById('rejectedApplications').textContent = stats.rejected;
}

/**
 * Actualizar paginación
 */
function updatePagination(totalItems) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const pageInfo = document.getElementById('pageInfoApp');

    if (pageInfo) {
        if (totalPages === 0) {
            pageInfo.textContent = 'Sin resultados';
        } else {
            pageInfo.textContent = `Página ${currentPage} de ${totalPages}`;
        }
    }

    const prevBtn = document.getElementById('prevPageAppBtn');
    const nextBtn = document.getElementById('nextPageAppBtn');

    if (prevBtn) prevBtn.disabled = currentPage === 1;
    if (nextBtn) nextBtn.disabled = currentPage === totalPages || totalPages === 0;
}

/**
 * Página anterior
 */
function previousPageApp() {
    if (currentPage > 1) {
        currentPage--;
        renderApplications();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

/**
 * Página siguiente
 */
function nextPageApp() {
    const totalPages = Math.ceil(filteredApplications.length / itemsPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        renderApplications();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

/**
 * Obtener configuración del estado
 */
function getStatusConfig(status) {
    const statusMap = {
        'pending': {
            label: 'Pendiente',
            class: 'pending',
            icon: 'fas fa-clock'
        },
        'pending_review': {
            label: 'En Revisión',
            class: 'review',
            icon: 'fas fa-eye'
        },
        'accepted': {
            label: 'Aceptada',
            class: 'accepted',
            icon: 'fas fa-check'
        },
        'rejected': {
            label: 'Rechazada',
            class: 'rejected',
            icon: 'fas fa-times'
        },
        'withdrawn': {
            label: 'Retirada',
            class: 'withdrawn',
            icon: 'fas fa-ban'
        }
    };

    return statusMap[status?.toLowerCase()] || statusMap['pending'];
}

/**
 * Utilidades
 */
function debounce(func, delay) {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func(...args), delay);
    };
}

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
