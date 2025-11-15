/**
 * MoirAI - Dashboard Page JavaScript
 * Página de inicio de usuarios autenticados
 */

let currentUser = null;
let dashboardData = {
    applications: [],
    recommendations: [],
    stats: {}
};

document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
});

/**
 * Inicializar dashboard
 */
async function initDashboard() {
    // Proteger ruta
    if (!authManager.isAuthenticated()) {
        window.location.href = '/login?redirect=/dashboard';
        return;
    }

    // Cargar datos del usuario
    notificationManager.loading('Cargando dashboard...');

    try {
        await Promise.all([
            loadUserData(),
            loadApplications(),
            loadRecommendations(),
            loadStats()
        ]);

        notificationManager.hideLoading();
        setupEventHandlers();

    } catch (error) {
        notificationManager.hideLoading();
        notificationManager.error('Error al cargar el dashboard');
        console.error(error);
    }
}

/**
 * Cargar datos del usuario actual
 */
async function loadUserData() {
    try {
        currentUser = await authManager.getCurrentUser();

        if (!currentUser) {
            throw new Error('No se pudo obtener datos del usuario');
        }

        // Actualizar elementos del usuario
        document.getElementById('user-name').textContent = currentUser.first_name || 'Usuario';
        document.getElementById('user-email').textContent = currentUser.email;

        // Actualizar según el rol
        const role = authManager.getUserRole();
        if (role === 'student') {
            document.getElementById('user-subtitle').textContent = 'Estudiante de UNRC - Busca tu próxima oportunidad';
        } else if (role === 'company') {
            document.getElementById('user-subtitle').textContent = 'Empresa Colaboradora - Encuentra el talento que necesitas';
        }

        return currentUser;

    } catch (error) {
        notificationManager.error('Error al cargar datos del usuario');
        console.error(error);
        throw error;
    }
}

/**
 * Cargar aplicaciones del usuario
 */
async function loadApplications() {
    try {
        const response = await apiClient.get('/applications/my-applications');

        dashboardData.applications = response.applications || [];

        // Renderizar tabla
        renderApplicationsTable();

    } catch (error) {
        notificationManager.warning('No se pudieron cargar las aplicaciones');
        console.error(error);
    }
}

/**
 * Cargar recomendaciones de empleos
 */
async function loadRecommendations() {
    try {
        const userId = currentUser.id;

        const response = await apiClient.post('/matching/recommendations', {
            student_id: userId,
            limit: 5
        });

        dashboardData.recommendations = response.jobs || [];

        // Renderizar carrusel
        renderRecommendations();

    } catch (error) {
        notificationManager.warning('No se pudieron cargar recomendaciones');
        console.error(error);
    }
}

/**
 * Cargar estadísticas
 */
async function loadStats() {
    try {
        // Calcular stats locales
        dashboardData.stats = {
            applications_count: dashboardData.applications.length,
            applications_pending: dashboardData.applications.filter(a => a.status === 'pending').length,
            applications_accepted: dashboardData.applications.filter(a => a.status === 'accepted').length,
            recommendations_count: dashboardData.recommendations.length,
        };

        // Intentar obtener score si existe endpoint
        try {
            const scoreResponse = await apiClient.get(`/matching/student/${currentUser.id}/matching-score`);
            dashboardData.stats.avg_match_score = scoreResponse.avg_score || 0;
        } catch (e) {
            dashboardData.stats.avg_match_score = 0;
        }

        // Renderizar cards de stats
        renderStats();

    } catch (error) {
        console.error('Error calculando stats:', error);
    }
}

/**
 * Renderizar tabla de aplicaciones
 */
function renderApplicationsTable() {
    const container = document.getElementById('applications-container');

    if (!container) return;

    if (dashboardData.applications.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <h3>Sin aplicaciones</h3>
                <p>Aún no has aplicado a ningún empleo</p>
                <a href="/oportunidades" class="btn btn-primary">Buscar empleos</a>
            </div>
        `;
        return;
    }

    let html = `
        <table class="applications-table">
            <thead>
                <tr>
                    <th>Empleo</th>
                    <th>Empresa</th>
                    <th>Estado</th>
                    <th>Fecha</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
    `;

    dashboardData.applications.forEach(app => {
        const statusColor = {
            'pending': 'pending',
            'accepted': 'success',
            'rejected': 'error',
            'interview': 'warning'
        }[app.status] || 'info';

        const statusLabel = {
            'pending': 'Pendiente',
            'accepted': 'Aceptada',
            'rejected': 'Rechazada',
            'interview': 'Entrevista'
        }[app.status] || app.status;

        const date = new Date(app.applied_at).toLocaleDateString('es-ES');

        html += `
            <tr>
                <td><strong>${app.job?.title || 'Empleo'}</strong></td>
                <td>${app.job?.company || 'Empresa'}</td>
                <td>
                    <span class="status-badge status-${statusColor}">
                        ${statusLabel}
                    </span>
                </td>
                <td>${date}</td>
                <td>
                    <button class="btn-small" onclick="viewJobDetail(${app.job?.id})">
                        <i class="fas fa-eye"></i> Ver
                    </button>
                </td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    container.innerHTML = html;
}

/**
 * Renderizar recomendaciones
 */
function renderRecommendations() {
    const container = document.getElementById('recommendations-container');

    if (!container) return;

    if (dashboardData.recommendations.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-star"></i>
                <h3>Sin recomendaciones</h3>
                <p>Completá tu perfil para recibir recomendaciones personalizadas</p>
                <a href="/profile" class="btn btn-primary">Completar perfil</a>
            </div>
        `;
        return;
    }

    let html = '<div class="jobs-grid">';

    dashboardData.recommendations.forEach(job => {
        const matchScore = Math.round(job.matching_score * 100);

        html += `
            <div class="job-card-simple">
                <div class="job-card-header">
                    <h4>${job.title}</h4>
                    <span class="match-badge">${matchScore}% Match</span>
                </div>
                <p class="job-company">${job.company}</p>
                <p class="job-location">
                    <i class="fas fa-map-marker-alt"></i> ${job.location || 'Ubicación no especificada'}
                </p>
                <p class="job-modality">
                    <i class="fas fa-briefcase"></i> ${job.work_mode || 'Modalidad no especificada'}
                </p>
                <div class="job-card-footer">
                    <button class="btn-small btn-secondary" onclick="viewJobDetail(${job.id})">
                        <i class="fas fa-eye"></i> Ver
                    </button>
                    <button class="btn-small btn-primary" onclick="applyToJob(${job.id})">
                        <i class="fas fa-check"></i> Aplicar
                    </button>
                </div>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}

/**
 * Renderizar cards de estadísticas
 */
function renderStats() {
    const stats = dashboardData.stats;

    const statsElements = {
        'applications-count': stats.applications_count || 0,
        'match-score': stats.avg_match_score ? Math.round(stats.avg_match_score) + '%' : '0%',
        'recommendations-count': stats.recommendations_count || 0,
        'cv-status': currentUser.cv_uploaded ? 'Sí ✓' : 'No'
    };

    Object.keys(statsElements).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = statsElements[id];
        }
    });
}

/**
 * Ver detalles de un empleo
 */
async function viewJobDetail(jobId) {
    try {
        const job = await apiClient.get(`/jobs/${jobId}`);

        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content job-modal">
                <span class="close-modal" onclick="this.closest('.modal').remove()">&times;</span>
                <h2>${job.title}</h2>
                <p class="job-company"><strong>${job.company}</strong></p>
                <p class="job-meta">
                    <i class="fas fa-map-marker-alt"></i> ${job.location}
                    | <i class="fas fa-briefcase"></i> ${job.work_mode}
                </p>
                <h4>Descripción</h4>
                <p>${job.description}</p>
                <h4>Salario</h4>
                <p>$${job.salary_min} - $${job.salary_max} ${job.currency}</p>
                <h4>Requisitos</h4>
                <ul>
                    ${job.requirements?.map(req => `<li>${req}</li>`).join('') || '<li>No especificado</li>'}
                </ul>
                <div class="modal-footer">
                    <button class="btn btn-primary" onclick="applyToJob(${jobId}); this.closest('.modal').remove()">
                        <i class="fas fa-paper-plane"></i> Aplicar Ahora
                    </button>
                    <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">
                        Cerrar
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        modal.style.display = 'flex';

        // Cerrar al hacer clic fuera
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });

    } catch (error) {
        notificationManager.error('Error al cargar detalles del empleo');
        console.error(error);
    }
}

/**
 * Aplicar a un empleo
 */
async function applyToJob(jobId) {
    try {
        const userId = currentUser.id;

        notificationManager.loading('Enviando aplicación...');

        const response = await apiClient.post('/applications', {
            student_id: userId,
            job_id: jobId
        });

        notificationManager.hideLoading();
        notificationManager.success('¡Aplicación enviada exitosamente!');

        // Recargar aplicaciones
        await loadApplications();

    } catch (error) {
        notificationManager.hideLoading();

        if (error.message?.includes('already applied')) {
            notificationManager.warning('Ya has aplicado a este empleo');
        } else {
            notificationManager.error('Error al enviar aplicación');
        }

        console.error(error);
    }
}

/**
 * Setup de event handlers
 */
function setupEventHandlers() {
    // Botón de logout
    const logoutBtn = document.querySelector('[onclick="logout()"]');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            await logout();
        });
    }

    // Event listeners para notificaciones en tiempo real (WebSocket en futuro)
    authManager.onChange((user) => {
        currentUser = user;
        document.getElementById('user-name').textContent = user.first_name || 'Usuario';
    });
}

/**
 * Logout
 */
async function logout() {
    try {
        await authManager.logout();
        notificationManager.success('Hasta luego');
        setTimeout(() => {
            window.location.href = '/';
        }, 1000);
    } catch (error) {
        notificationManager.error('Error al cerrar sesión');
    }
}

/**
 * Refrescar dashboard
 */
async function refreshDashboard() {
    notificationManager.loading('Actualizando...');
    try {
        await Promise.all([
            loadApplications(),
            loadRecommendations(),
            loadStats()
        ]);
        notificationManager.hideLoading();
        notificationManager.success('Dashboard actualizado');
    } catch (error) {
        notificationManager.hideLoading();
        notificationManager.error('Error al actualizar');
    }
}
