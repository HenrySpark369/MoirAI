/**
 * MoirAI - Admin Analytics Module
 * Gestiona la analítica del panel de administración (standalone o integrada)
 * Incluye KPIs, gráficos, tablas y filtros dinámicos
 * 
 * Uso:
 * 1. Standalone (analytics.html): Auto-inicializa
 * 2. Integrado (dashboard.html): Inicializar manualmente en DashboardRoleAdapter
 */

class AdminAnalyticsPage {
    constructor(containerSelector = null) {
        this.API_BASE = 'http://localhost:8000/api/v1';
        this.charts = {};
        this.initialized = false;
        // Para uso integrado, especificar selector del contenedor
        this.containerSelector = containerSelector;
    }

    /**
     * Inicializar la página de analítica
     * @param {boolean} isIntegrated - Si es true, busca elementos dentro del contenedor
     */
    async initialize(isIntegrated = false) {
        try {
            this.validateElements(isIntegrated);
            this.setupEventListeners(isIntegrated);
            this.initDateRange(isIntegrated);
            await this.loadAnalytics(isIntegrated);
            this.initialized = true;
        } catch (error) {
            console.error('Error inicializando analytics:', error);
            this.showError('Error al inicializar la página de analítica', isIntegrated);
        }
    }

    /**
     * Validar que existan los elementos necesarios en el DOM
     * @param {boolean} isIntegrated - Si es true, busca dentro del contenedor
     */
    validateElements(isIntegrated = false) {
        const requiredElements = [
            'error-message',
            'start-date',
            'end-date',
            'kpi-grid'
        ];

        // Para standalone, requerir más elementos
        if (!isIntegrated) {
            requiredElements.push('loading-state', 'analytics-content', 'charts-section', 'tables-section');
        }

        requiredElements.forEach(id => {
            const selector = isIntegrated && this.containerSelector 
                ? `${this.containerSelector} #${id}` 
                : `#${id}`;
            
            if (!document.querySelector(selector)) {
                console.warn(`Elemento no encontrado: ${selector}`);
                // No throw para integrated mode
                if (!isIntegrated) {
                    throw new Error(`Elemento requerido no encontrado: #${id}`);
                }
            }
        });
    }

    /**
     * Configurar event listeners
     * @param {boolean} isIntegrated - Si es true, busca dentro del contenedor
     */
    setupEventListeners(isIntegrated = false) {
        // Selector base
        const selector = isIntegrated && this.containerSelector ? this.containerSelector : '';
        
        // Botón de actualizar
        const updateBtn = selector 
            ? document.querySelector(`${selector} .date-range button`)
            : document.querySelector('.date-range button');
        if (updateBtn) {
            updateBtn.addEventListener('click', () => this.loadAnalytics(isIntegrated));
        }

        // Enter en campos de fecha
        const startDate = selector
            ? document.querySelector(`${selector} #start-date`)
            : document.getElementById('start-date');
        const endDate = selector
            ? document.querySelector(`${selector} #end-date`)
            : document.getElementById('end-date');
        
        if (startDate) startDate.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.loadAnalytics(isIntegrated);
        });
        
        if (endDate) endDate.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.loadAnalytics(isIntegrated);
        });
    }

    /**
     * Obtener API key desde localStorage
     */
    getApiKey() {
        const key = localStorage.getItem('api_key');
        if (!key) {
            this.showError('Sin sesión activa');
            setTimeout(() => window.location.href = '/login', 2000);
            throw new Error('No API key found');
        }
        return key;
    }

    /**
     * Mostrar error
     * @param {string} msg - Mensaje de error
     * @param {boolean} isIntegrated - Si es true, busca dentro del contenedor
     */
    showError(msg, isIntegrated = false) {
        const selector = isIntegrated && this.containerSelector ? this.containerSelector : '';
        const el = selector
            ? document.querySelector(`${selector} #error-message`)
            : document.getElementById('error-message');
        if (el) {
            el.textContent = msg;
            el.style.display = 'block';
        }
    }

    /**
     * Ocultar error
     * @param {boolean} isIntegrated - Si es true, busca dentro del contenedor
     */
    hideError(isIntegrated = false) {
        const selector = isIntegrated && this.containerSelector ? this.containerSelector : '';
        const el = selector
            ? document.querySelector(`${selector} #error-message`)
            : document.getElementById('error-message');
        if (el) {
            el.style.display = 'none';
        }
    }

    /**
     * Mostrar estado de carga
     * @param {boolean} isIntegrated - Si es true, busca dentro del contenedor
     */
    showLoading(isIntegrated = false) {
        const selector = isIntegrated && this.containerSelector ? this.containerSelector : '';
        
        const loading = selector
            ? document.querySelector(`${selector} #loading-state`)
            : document.getElementById('loading-state');
        const content = selector
            ? document.querySelector(`${selector} #analytics-content`)
            : document.getElementById('analytics-content');
        
        if (loading) loading.style.display = 'block';
        if (content) content.style.display = 'none';
    }

    /**
     * Ocultar estado de carga
     * @param {boolean} isIntegrated - Si es true, busca dentro del contenedor
     */
    hideLoading(isIntegrated = false) {
        const selector = isIntegrated && this.containerSelector ? this.containerSelector : '';
        
        const loading = selector
            ? document.querySelector(`${selector} #loading-state`)
            : document.getElementById('loading-state');
        const content = selector
            ? document.querySelector(`${selector} #analytics-content`)
            : document.getElementById('analytics-content');
        
        if (loading) loading.style.display = 'none';
        if (content) content.style.display = 'block';
    }

    /**
     * Inicializar rango de fechas (últimos 30 días)
     * @param {boolean} isIntegrated - Si es true, busca dentro del contenedor
     */
    initDateRange(isIntegrated = false) {
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(endDate.getDate() - 30);

        const selector = isIntegrated && this.containerSelector ? this.containerSelector : '';
        
        const startInput = selector
            ? document.querySelector(`${selector} #start-date`)
            : document.getElementById('start-date');
        const endInput = selector
            ? document.querySelector(`${selector} #end-date`)
            : document.getElementById('end-date');

        if (startInput) startInput.valueAsDate = startDate;
        if (endInput) endInput.valueAsDate = endDate;
    }

    /**
     * Cargar datos de analítica desde API
     * @param {boolean} isIntegrated - Si es true, busca dentro del contenedor
     */
    async loadAnalytics(isIntegrated = false) {
        try {
            this.showLoading(isIntegrated);
            this.hideError(isIntegrated);

            const selector = isIntegrated && this.containerSelector ? this.containerSelector : '';
            
            // Obtener rangos de fecha
            const startDateEl = selector
                ? document.querySelector(`${selector} #start-date`)
                : document.getElementById('start-date');
            const endDateEl = selector
                ? document.querySelector(`${selector} #end-date`)
                : document.getElementById('end-date');
            
            const startDate = startDateEl?.value || '';
            const endDate = endDateEl?.value || '';

            // Construir URL con parámetros
            const params = new URLSearchParams();
            if (startDate) params.append('start_date', startDate);
            if (endDate) params.append('end_date', endDate);

            const url = `${this.API_BASE}/admin/analytics/kpis${params.toString() ? '?' + params.toString() : ''}`;

            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'X-API-Key': this.getApiKey(),
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            // Actualizar UI con datos
            this.updateKPIs(data, isIntegrated);
            this.populateTables(data, isIntegrated);
            this.initializeCharts(data, isIntegrated);

            this.hideLoading(isIntegrated);

        } catch (error) {
            console.error('Analytics loading error:', error);
            this.hideLoading(isIntegrated);
            this.showError(`Error al cargar analítica: ${error.message}`, isIntegrated);
        }
    }

    /**
     * Actualizar KPIs con datos dinámicos
     * @param {object} data - Datos de la API
     * @param {boolean} isIntegrated - Si es true, busca dentro del contenedor
     */
    updateKPIs(data, isIntegrated = false) {
        const selector = isIntegrated && this.containerSelector ? this.containerSelector : '';
        const querySelector = (id) => selector
            ? document.querySelector(`${selector} #${id}`)
            : document.getElementById(id);

        const kpiMappings = [
            { key: 'total_students', elementId: 'kpi-students', changeId: 'kpi-students-change', changeKey: 'student_change' },
            { key: 'total_companies', elementId: 'kpi-companies', changeId: 'kpi-companies-change', changeKey: 'company_change' },
            { key: 'total_jobs', elementId: 'kpi-jobs', changeId: 'kpi-jobs-change', changeKey: 'job_change' },
            { key: 'total_applications', elementId: 'kpi-applications', changeId: 'kpi-applications-change', changeKey: 'app_change' },
            { key: 'matching_rate', elementId: 'kpi-matching-rate', changeId: 'kpi-matching-change', changeKey: 'matching_rate_change' }
        ];

        kpiMappings.forEach(mapping => {
            // Actualizar valor
            const valueEl = querySelector(mapping.elementId);
            if (valueEl && data[mapping.key] !== undefined) {
                // Para matching_rate, agregar símbolo %
                if (mapping.key === 'matching_rate') {
                    valueEl.textContent = (data[mapping.key] || 0).toLocaleString() + '%';
                } else {
                    valueEl.textContent = (data[mapping.key] || 0).toLocaleString();
                }
            }

            // Actualizar cambio porcentual
            const changeEl = querySelector(mapping.changeId);
            if (changeEl && data[mapping.changeKey] !== undefined) {
                const changeValue = Math.abs(data[mapping.changeKey]);
                changeEl.textContent = changeValue + '%';
                
                // Cambiar color según si es positivo o negativo
                const changeDiv = changeEl.closest('.kpi-change');
                if (changeDiv) {
                    changeDiv.classList.remove('positive', 'negative');
                    changeDiv.classList.add(data[mapping.changeKey] >= 0 ? 'positive' : 'negative');
                }
            }
        });
    }

    /**
     * Llenar tablas con datos
     * @param {object} data - Datos de la API
     * @param {boolean} isIntegrated - Si es true, busca dentro del contenedor
     */
    populateTables(data, isIntegrated = false) {
        this.populateTable('top-companies', data.top_companies, 
            (item, i) => `<tr><td class="rank">#${i + 1}</td><td>${item.name || 'Sin datos'}</td><td>${(item.jobs_count || 0).toLocaleString()}</td></tr>`,
            isIntegrated
        );

        this.populateTable('top-skills', data.top_skills,
            (item, i) => `<tr><td class="rank">#${i + 1}</td><td>${item.name || 'Sin datos'}</td><td>${(item.demand || 0).toLocaleString()}</td></tr>`,
            isIntegrated
        );

        this.populateTable('top-locations', data.top_locations,
            (item, i) => `<tr><td class="rank">#${i + 1}</td><td>${item.name || 'Sin datos'}</td><td>${(item.jobs_count || 0).toLocaleString()}</td></tr>`,
            isIntegrated
        );
    }

    /**
     * Helper para llenar tabla individual
     * @param {string} tableId - ID de la tabla (tbody)
     * @param {array} items - Elementos a mostrar
     * @param {function} renderFn - Función para renderizar cada fila
     * @param {boolean} isIntegrated - Si es true, busca dentro del contenedor
     */
    populateTable(tableId, items, renderFn, isIntegrated = false) {
        const selector = isIntegrated && this.containerSelector ? this.containerSelector : '';
        const tbody = selector
            ? document.querySelector(`${selector} #${tableId}`)
            : document.getElementById(tableId);
        
        if (!tbody) return;

        if (!items || items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: #999;">Sin datos disponibles</td></tr>';
            return;
        }

        tbody.innerHTML = items.slice(0, 5).map((item, i) => renderFn(item, i)).join('');
    }

    /**
     * Inicializar gráficos con Chart.js
     * @param {object} data - Datos de la API
     * @param {boolean} isIntegrated - Si es true, busca dentro del contenedor
     */
    initializeCharts(data, isIntegrated = false) {
        // Destruir gráficos existentes
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};

        const selector = isIntegrated && this.containerSelector ? this.containerSelector : '';
        const querySelector = (id) => selector
            ? document.querySelector(`${selector} #${id}`)
            : document.getElementById(id);

        // Obtener datos de tendencias
        const trends = data.trends || {};
        const dates = trends.dates || ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'];

        // Configuración común para gráficos de línea
        const lineConfig = {
            borderColor: '#730f33',
            backgroundColor: 'rgba(115, 15, 51, 0.1)',
            tension: 0.4,
            fill: true,
            borderWidth: 2
        };

        // Gráfico 1: Registros de Estudiantes
        const studentsCanvas = querySelector('students-chart');
        if (studentsCanvas) {
            this.charts.students = new Chart(studentsCanvas, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: 'Estudiantes',
                        data: trends.student_values || [45, 52, 48, 61],
                        ...lineConfig
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: { mode: 'index', intersect: false }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        }

        // Gráfico 2: Vacantes Publicadas
        const jobsCanvas = querySelector('jobs-chart');
        if (jobsCanvas) {
            this.charts.jobs = new Chart(jobsCanvas, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: 'Vacantes',
                        data: trends.job_values || [12, 19, 16, 24],
                        ...lineConfig
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: { mode: 'index', intersect: false }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        }

        // Gráfico 3: Aplicaciones
        const appsCanvas = querySelector('applications-chart');
        if (appsCanvas) {
            this.charts.applications = new Chart(appsCanvas, {
                type: 'bar',
                data: {
                    labels: dates,
                    datasets: [{
                        label: 'Aplicaciones',
                        data: trends.app_values || [89, 134, 118, 156],
                        backgroundColor: '#730f33',
                        borderColor: '#5a0a27',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        }

        // Gráfico 4: Tasa de Éxito
        const rateCanvas = querySelector('success-rate-chart');
        if (rateCanvas) {
            this.charts.successRate = new Chart(rateCanvas, {
                type: 'doughnut',
                data: {
                    labels: ['Exitosas', 'Pendientes'],
                    datasets: [{
                        data: trends.success_rate || [73, 27],
                        backgroundColor: ['#730f33', '#e5e7eb'],
                        borderColor: ['#5a0a27', '#d1d5db'],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { padding: 15 }
                        }
                    }
                }
            });
        }
    }

    /**
     * Limpiar recursos (para cuando se salga de la página)
     */
    destroy() {
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};
        this.initialized = false;
    }

    /**
     * Exportar datos (para descargar como CSV, etc)
     */
    async exportData() {
        try {
            // Aquí iría la lógica de exportación
            console.log('Exporting analytics data...');
        } catch (error) {
            console.error('Export error:', error);
            this.showError('Error al exportar datos');
        }
    }
}

// Instancia global
let adminAnalyticsPage = null;

// Inicializar cuando el DOM esté listo (solo para standalone)
// Para modo integrado, usar: 
//   const analytics = new AdminAnalyticsPage('#analytics');
//   analytics.initialize(true);

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Solo inicializar automáticamente si NO está en dashboard
        const isInDashboard = document.querySelector('main.main-content') && 
                             document.querySelector('#analytics.content-section');
        
        if (!isInDashboard || window.location.pathname === '/admin/analytics') {
            adminAnalyticsPage = new AdminAnalyticsPage();
            adminAnalyticsPage.initialize(false).catch(error => {
                console.error('Error en admin analytics:', error);
            });
        }
    });
} else {
    // Solo inicializar automáticamente si NO está en dashboard
    const isInDashboard = document.querySelector('main.main-content') && 
                         document.querySelector('#analytics.content-section');
    
    if (!isInDashboard || window.location.pathname === '/admin/analytics') {
        adminAnalyticsPage = new AdminAnalyticsPage();
        adminAnalyticsPage.initialize(false).catch(error => {
            console.error('Error en admin analytics:', error);
        });
    }
}

// Limpiar al salir
window.addEventListener('beforeunload', () => {
    if (adminAnalyticsPage) {
        adminAnalyticsPage.destroy();
    }
});
