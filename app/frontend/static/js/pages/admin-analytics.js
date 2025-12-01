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
        // Elementos siempre requeridos (deben existir en ambas versiones)
        const criticalElements = ['error-message'];
        
        // Elementos opcionales para standalone
        const standaloneElements = [
            'start-date',
            'end-date',
            'kpi-grid',
            'loading-state', 
            'analytics-content', 
            'charts-section', 
            'tables-section'
        ];
        
        // Para integrated mode, no validamos elementos del DOM
        // porque podrían estar en diferentes contenedores o estructuras
        if (isIntegrated) {
            console.log('📌 Modo integrado: validación flexible de elementos');
            return;
        }

        // Para standalone, validar elementos críticos y advertir sobre los faltantes
        criticalElements.forEach(id => {
            const selector = `#${id}`;
            if (!document.querySelector(selector)) {
                console.warn(`⚠️ Elemento no encontrado: ${selector}`);
            }
        });

        // Para standalone, advertir pero no fallar si faltan elementos no críticos
        standaloneElements.forEach(id => {
            const selector = `#${id}`;
            if (!document.querySelector(selector)) {
                console.warn(`⚠️ Elemento no encontrado: ${selector} (no crítico)`);
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
        
        // Botón de actualizar (opcional, puede no existir en integrated mode)
        const updateBtn = selector 
            ? document.querySelector(`${selector} .date-range button`)
            : document.querySelector('.date-range button');
        if (updateBtn) {
            updateBtn.addEventListener('click', () => this.loadAnalytics(isIntegrated));
        } else {
            console.debug('💡 Botón de actualizar no encontrado (opcional)');
        }

        // Enter en campos de fecha (opcional)
        const startDate = selector
            ? document.querySelector(`${selector} #start-date`)
            : document.getElementById('start-date');
        const endDate = selector
            ? document.querySelector(`${selector} #end-date`)
            : document.getElementById('end-date');
        
        if (startDate) {
            startDate.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.loadAnalytics(isIntegrated);
            });
        }
        
        if (endDate) {
            endDate.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.loadAnalytics(isIntegrated);
            });
        }
    }

    /**
     * Obtener API key desde localStorage
     */
    getApiKey() {
        // Check for demo mode
        const urlParams = new URLSearchParams(window.location.search);
        const isDemoMode = urlParams.get('demo') === 'true';
        
        if (isDemoMode) {
            return 'demo-key'; // Dummy key for demo mode
        }

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
        
        if (loading) {
            loading.style.display = 'block';
        }
        if (content) {
            content.style.display = 'none';
        }
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
        
        if (loading) {
            loading.style.display = 'none';
        }
        if (content) {
            content.style.display = 'block';
        }
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

        // Solo asignar valores si los elementos existen
        if (startInput) startInput.valueAsDate = startDate;
        if (endInput) endInput.valueAsDate = endDate;
        
        // Log para debugging
        if (!startInput || !endInput) {
            console.debug('💡 Campos de fecha no encontrados (opcional)');
        }
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

            // Check for demo mode
            const urlParams = new URLSearchParams(window.location.search);
            const isDemoMode = urlParams.get('demo') === 'true';

            const headers = {
                'X-API-Key': this.getApiKey(),
                'Content-Type': 'application/json'
            };

            if (isDemoMode) {
                headers['X-Demo-Mode'] = 'true';
            }

            const response = await fetch(url, {
                method: 'GET',
                headers: headers
            });

            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            // Actualizar UI con datos
            this.updateKPIs(data, isIntegrated);
            this.populateTables(data, isIntegrated);
            await this.initializeCharts(data, isIntegrated);
            
            // Asegurar dimensiones correctas de gráficos después de inicialización
            this.ensureChartDimensions();
            
            // Agregar listener para redimensionamiento de ventana
            window.addEventListener('resize', this.handleResize);

            // Forzar dimensiones finales después de un breve delay
            setTimeout(() => {
                this.forceChartDimensions();
            }, 300);

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
    async initializeCharts(data, isIntegrated = false) {
        // Destruir gráficos existentes
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};

        const selector = isIntegrated && this.containerSelector ? this.containerSelector : '';
        const querySelector = (id) => {
            // En modo integrado, usar getElementById directamente ya que los IDs deberían ser únicos
            if (isIntegrated) {
                return document.getElementById(id);
            }
            return selector
                ? document.querySelector(`${selector} #${id}`)
                : document.getElementById(id);
        };

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

        // Función helper para crear gráficos con dimensiones forzadas
        const createChartWithFixedDimensions = (canvasId, config) => {
            const canvas = querySelector(canvasId);
            if (!canvas) {
                console.warn(`Canvas ${canvasId} not found`);
                return null;
            }

            // Forzar dimensiones del contenedor padre
            const wrapper = canvas.parentElement;
            if (wrapper) {
                wrapper.style.height = '300px !important';
                wrapper.style.width = '100% !important';
                wrapper.style.overflow = 'visible !important';
            }

            // Forzar dimensiones del canvas - consistentes
            canvas.style.height = '300px !important';
            canvas.style.width = '100% !important';
            canvas.style.maxHeight = '300px !important';
            canvas.style.maxWidth = '100% !important';
            canvas.height = 300;
            canvas.width = 400; // Ancho fijo para consistencia

            // Usar requestAnimationFrame para asegurar que el DOM esté actualizado
            return new Promise((resolve) => {
                requestAnimationFrame(() => {
                    try {
                        // Crear gráfico con configuración restrictiva
                        const chart = new Chart(canvas, {
                            ...config,
                            options: {
                                ...config.options,
                                responsive: false, // Deshabilitar responsive para control total
                                maintainAspectRatio: false,
                                animation: false, // Deshabilitar animaciones que pueden causar problemas
                                plugins: {
                                    ...config.options.plugins,
                                    legend: { display: false }
                                }
                            }
                        });

                        // Re-afirmar dimensiones finales después de crear el gráfico
                        setTimeout(() => {
                            canvas.style.height = '300px !important';
                            canvas.style.width = '100% !important';
                            canvas.height = 300;
                            canvas.width = 400;
                            // Forzar un update del gráfico para asegurar que se renderice
                            chart.update();
                        }, 50);

                        resolve(chart);
                    } catch (error) {
                        console.error(`Error creating chart ${canvasId}:`, error);
                        resolve(null);
                    }
                });
            });
        };

        // Crear gráficos de manera asíncrona para asegurar que se rendericen correctamente
        const createChartsAsync = async () => {
            // Gráfico 1: Registros de Estudiantes
            this.charts.students = await createChartWithFixedDimensions('students-chart', {
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
                    plugins: {
                        legend: { display: false },
                        tooltip: { mode: 'index', intersect: false }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });

            // Gráfico 2: Vacantes Publicadas
            this.charts.jobs = await createChartWithFixedDimensions('jobs-chart', {
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
                    plugins: {
                        legend: { display: false },
                        tooltip: { mode: 'index', intersect: false }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });

            // Gráfico 3: Aplicaciones
            this.charts.applications = await createChartWithFixedDimensions('applications-chart', {
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
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });

            // Gráfico 4: Tasa de Éxito
            this.charts.successRate = await createChartWithFixedDimensions('success-rate-chart', {
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
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { padding: 15 }
                        }
                    }
                }
            });
        };

        // Ejecutar la creación de gráficos de manera asíncrona
        await createChartsAsync();
    }

    /**
     * Limpiar recursos (para cuando se salga de la página)
     */
    destroy() {
        // Remover event listener de resize
        window.removeEventListener('resize', this.handleResize);
        
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};
        this.initialized = false;
    }

    /**
     * Manejar redimensionamiento de ventana para ajustar gráficos
     */
    handleResize = () => {
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.resize === 'function') {
                chart.resize();
            }
        });
    }

    /**
     * Asegurar que todos los gráficos tengan dimensiones correctas
     */
    ensureChartDimensions() {
        const chartIds = ['students-chart', 'jobs-chart', 'applications-chart', 'success-rate-chart'];
        chartIds.forEach(id => {
            const canvas = document.getElementById(id);
            if (canvas) {
                canvas.style.height = '300px';
                canvas.style.width = '100%';
                canvas.height = 300;
                canvas.width = 400;
            }
        });
    }

    /**
     * Forzar dimensiones de gráficos de manera agresiva
     */
    forceChartDimensions() {
        const chartIds = ['students-chart', 'jobs-chart', 'applications-chart', 'success-rate-chart'];
        chartIds.forEach(id => {
            const canvas = document.getElementById(id);
            if (canvas) {
                // Forzar dimensiones del canvas - consistentes
                canvas.style.height = '300px !important';
                canvas.style.width = '100% !important';
                canvas.style.maxHeight = '300px !important';
                canvas.style.maxWidth = '100% !important';
                canvas.height = 300;
                canvas.width = 400;

                // Forzar dimensiones del wrapper
                const wrapper = canvas.parentElement;
                if (wrapper) {
                    wrapper.style.height = '300px !important';
                    wrapper.style.width = '100% !important';
                    wrapper.style.overflow = 'visible !important';
                }
            }
        });
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

function initializeAnalyticsPage() {
    try {
        // Detectar si estamos en página standalone o integrada
        const analyticsHtml = document.querySelector('[data-page="analytics"]');
        const isDedicatedPage = window.location.pathname === '/admin/analytics';
        const hasStandaloneStructure = document.querySelector('.content-section.active #analytics-content');
        
        // Solo inicializar automáticamente en página standalone
        if (isDedicatedPage || hasStandaloneStructure) {
            console.log('📊 Inicializando Analytics en modo STANDALONE');
            adminAnalyticsPage = new AdminAnalyticsPage();
            adminAnalyticsPage.initialize(false).catch(error => {
                console.error('❌ Error en analytics standalone:', error);
            });
        } else {
            console.log('📊 Modo integrado detectado - Analytics no se inicializa automáticamente');
        }
    } catch (error) {
        console.error('❌ Error al detectar modo de analytics:', error);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAnalyticsPage);
} else {
    initializeAnalyticsPage();
}

// Limpiar al salir
window.addEventListener('beforeunload', () => {
    if (adminAnalyticsPage) {
        adminAnalyticsPage.destroy();
    }
});

// Exportar función global para HTML onclick
window.updateAnalytics = function() {
    if (adminAnalyticsPage && adminAnalyticsPage.initialized) {
        adminAnalyticsPage.loadAnalytics(false);
    } else if (adminAnalyticsPage) {
        console.warn('Analytics not initialized yet');
    } else {
        console.error('AdminAnalyticsPage instance not found');
    }
};
