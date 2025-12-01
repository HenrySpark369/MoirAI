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
     * Cargar datos de analítica desde API o cache
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

            // Obtener KPIs del servicio centralizado
            const centralizedKPIs = await window.kpiService.getAllKPIs();
            console.log('📊 KPIs centralizados:', centralizedKPIs);

            // Intentar obtener datos del cache de empleos
            let jobsData = null;
            try {
                jobsData = await this.loadJobsFromCache();
                console.log(`📊 Datos de empleos del cache: ${jobsData ? jobsData.length : 0} empleos`);
            } catch (error) {
                console.warn('⚠️ Error cargando cache de empleos:', error.message);
            }

            // Combinar KPIs centralizados con datos adicionales
            const combinedData = {
                ...centralizedKPIs,
                // Mantener datos específicos de analytics si existen
                top_companies: centralizedKPIs.top_companies || [],
                top_skills: centralizedKPIs.top_skills || [],
                top_locations: centralizedKPIs.top_locations || []
            };

            // Poblar tabla de empleos con datos del cache
            this.populateJobsTable(jobsData, isIntegrated);

            // Actualizar UI con datos combinados
            this.updateKPIs(combinedData, isIntegrated);
            this.populateTables(combinedData, isIntegrated);
            await this.initializeCharts(combinedData, isIntegrated);
            
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
            { key: 'total_jobs', elementId: 'total-jobs', changeId: null, changeKey: null },
            { key: 'active_jobs', elementId: 'active-jobs', changeId: null, changeKey: null },
            { key: 'total_applications', elementId: 'total-applications', changeId: null, changeKey: null },
            { key: 'success_rate', elementId: 'success-rate', changeId: null, changeKey: null },
            // Mantener compatibilidad con KPIs existentes
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
                // Para porcentajes, agregar símbolo %
                if (mapping.key === 'matching_rate' || mapping.key === 'success_rate') {
                    valueEl.textContent = (data[mapping.key] || 0).toLocaleString() + '%';
                } else {
                    valueEl.textContent = (data[mapping.key] || 0).toLocaleString();
                }
            }

            // Actualizar cambio porcentual (solo si existe changeId)
            if (mapping.changeId) {
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

            // Limpiar cualquier dimensión previa del canvas
            canvas.removeAttribute('height');
            canvas.removeAttribute('width');
            canvas.style.removeProperty('height');
            canvas.style.removeProperty('width');

            // Forzar dimensiones del contenedor padre
            const wrapper = canvas.parentElement;
            if (wrapper) {
                wrapper.style.height = '300px';
                wrapper.style.width = '100%';
                wrapper.style.overflow = 'visible';
                wrapper.style.position = 'relative';
            }

            // Esperar a que el DOM esté completamente listo antes de crear el gráfico
            return new Promise((resolve) => {
                setTimeout(() => {
                    try {
                        // Verificar que el canvas esté realmente en el DOM y visible
                        if (!canvas.isConnected) {
                            console.warn(`Canvas ${canvasId} is not connected to DOM`);
                            resolve(null);
                            return;
                        }

                        // Crear gráfico con configuración optimizada para renderizado inmediato
                        const chart = new Chart(canvas, {
                            ...config,
                            options: {
                                ...config.options,
                                responsive: true,
                                maintainAspectRatio: false,
                                animation: {
                                    duration: 0 // Sin animaciones para renderizado inmediato
                                },
                                plugins: {
                                    ...config.options.plugins,
                                    legend: { display: false }
                                }
                            }
                        });

                        // Forzar múltiples actualizaciones para asegurar renderizado
                        setTimeout(() => {
                            chart.resize();
                            chart.update('none');
                            // Segunda actualización después de un breve delay
                            setTimeout(() => {
                                chart.resize();
                                chart.update('none');
                                // Tercera actualización para asegurar renderizado completo
                                setTimeout(() => {
                                    chart.resize();
                                    chart.update('none');
                                }, 100);
                            }, 50);
                        }, 10);

                        resolve(chart);
                    } catch (error) {
                        console.error(`Error creating chart ${canvasId}:`, error);
                        resolve(null);
                    }
                }, 100); // Delay mayor para asegurar que el DOM esté listo
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

        // Forzar renderizado final después de crear todos los gráficos
        setTimeout(() => {
            this.forceChartDimensions();
            // Segunda verificación después de un delay adicional
            setTimeout(() => {
                this.forceChartDimensions();
            }, 200);
        }, 150);
    }

    /**
     * Cargar empleos desde el cache del background job search
     */
    async loadJobsFromCache() {
        try {
            // Verificar si el servicio está disponible
            if (!window.backgroundJobSearch) {
                console.warn('⚠️ BackgroundJobSearch service not available');
                return [];
            }

            // Si el servicio no está ejecutándose, iniciarlo
            if (!window.backgroundJobSearch.isRunning) {
                console.log('🔄 Iniciando background job search para obtener datos...');
                window.backgroundJobSearch.start();
                
                // Esperar un poco para que cargue datos iniciales
                await new Promise(resolve => setTimeout(resolve, 2000));
            }

            // Intentar obtener resultados del servicio
            const cachedJobs = window.backgroundJobSearch.getResults();
            if (cachedJobs && cachedJobs.length > 0) {
                console.log(`📦 Usando cache del servicio: ${cachedJobs.length} empleos`);
                return cachedJobs;
            }

            // Si no hay datos locales, intentar cargar desde API directamente
            console.log('📡 Cargando datos desde API de cache...');
            const response = await fetch(`${this.API_BASE}/job-scraping/cache/list?limit=1000&offset=0`, {
                method: 'GET',
                headers: {
                    'X-API-Key': this.getApiKey(),
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Error cargando cache: ${response.status}`);
            }

            const data = await response.json();
            return data.jobs || [];

        } catch (error) {
            console.warn('⚠️ Error cargando cache de empleos:', error.message);
            return [];
        }
    }

    /**
     * Combinar datos de la API con datos del cache de empleos
     */
    combineDataWithJobsCache(apiData, jobsCache) {
        const combined = { ...apiData };

        if (jobsCache && Array.isArray(jobsCache)) {
            // Calcular métricas basadas en el cache de empleos
            const totalJobs = jobsCache.length;
            
            // Empleos activos: empleos marcados como activos en la BD
            const activeJobs = jobsCache.filter(job => job.is_active === true).length;

            // Actualizar métricas de empleos
            combined.total_jobs = totalJobs;
            combined.active_jobs = activeJobs;

            // Si no hay datos de aplicaciones en la API, usar datos calculados
            if (!combined.total_applications || combined.total_applications === 0) {
                // Estimar aplicaciones basado en empleos activos (promedio de 5-10 aplicaciones por empleo)
                combined.total_applications = Math.floor(activeJobs * 7);
            }

            // Calcular tasa de éxito si no está disponible
            if (!combined.success_rate || combined.success_rate === 0) {
                // Estimar tasa de éxito (5-15% típico)
                combined.success_rate = Math.floor(Math.random() * 10) + 5;
            }

            console.log(`📊 KPIs actualizados con cache: ${totalJobs} empleos totales, ${activeJobs} activos`);
        }

        return combined;
    }

    /**
     * Cargar empleos desde el cache del background job search
     */
    async loadJobsFromCache() {
        try {
            // Verificar si el servicio está disponible
            if (!window.backgroundJobSearch) {
                console.warn('⚠️ BackgroundJobSearch service not available');
                return [];
            }

            // Si el servicio no está ejecutándose, iniciarlo
            if (!window.backgroundJobSearch.isRunning) {
                console.log('🔄 Iniciando background job search para obtener datos...');
                window.backgroundJobSearch.start();
                
                // Esperar un poco para que cargue datos iniciales
                await new Promise(resolve => setTimeout(resolve, 2000));
            }

            // Intentar obtener resultados del servicio
            const cachedJobs = window.backgroundJobSearch.getResults();
            if (cachedJobs && cachedJobs.length > 0) {
                console.log(`📦 Usando cache del servicio: ${cachedJobs.length} empleos`);
                return cachedJobs;
            }

            // Si no hay datos locales, intentar cargar desde API directamente
            console.log('📡 Cargando datos desde API de cache...');
            const response = await fetch(`${this.API_BASE}/job-scraping/cache/list?limit=1000&offset=0`, {
                method: 'GET',
                headers: {
                    'X-API-Key': this.getApiKey(),
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Error cargando cache: ${response.status}`);
            }

            const data = await response.json();
            return data.jobs || [];

        } catch (error) {
            console.warn('⚠️ Error cargando cache de empleos:', error.message);
            return [];
        }
    }

    /**
     * Poblar tabla de empleos con datos del cache
     * @param {array} jobsData - Datos de empleos del cache
     * @param {boolean} isIntegrated - Si es true, busca dentro del contenedor
     */
    populateJobsTable(jobsData, isIntegrated = false) {
        const selector = isIntegrated && this.containerSelector ? this.containerSelector : '';
        const tbody = selector
            ? document.querySelector(`${selector} #jobs-tbody`)
            : document.getElementById('jobs-tbody');

        if (!tbody) {
            console.warn('Tabla de empleos no encontrada');
            return;
        }

        if (!jobsData || jobsData.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #999;">No hay empleos disponibles</td></tr>';
            return;
        }

        // Tomar los primeros 10 empleos para mostrar
        const jobsToShow = jobsData.slice(0, 10);

        tbody.innerHTML = jobsToShow.map((job, index) => {
            const statusBadge = job.is_active
                ? '<span class="badge active">Publicado</span>'
                : '<span class="badge inactive">Inactivo</span>';

            const formattedDate = job.scraped_at
                ? new Date(job.scraped_at).toLocaleDateString('es-ES')
                : 'Sin fecha';

            return `
                <tr>
                    <td><strong>${job.title || 'Sin título'}</strong></td>
                    <td>${job.company || 'Empresa no especificada'}</td>
                    <td>${job.location || 'Ubicación no especificada'}</td>
                    <td>${statusBadge}</td>
                    <td><small>${formattedDate}</small></td>
                    <td>
                        <div class="actions">
                            <button class="btn-sm btn-info" onclick="viewJob('${job.external_job_id || job.id}')">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn-sm btn-warning" onclick="editJob('${job.external_job_id || job.id}')">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn-sm btn-danger" onclick="deleteJob('${job.external_job_id || job.id}', '${job.title || 'Sin título'}')">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
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
        chartIds.forEach((id, index) => {
            const canvas = document.getElementById(id);
            if (canvas) {
                // Limpiar dimensiones previas
                canvas.removeAttribute('height');
                canvas.removeAttribute('width');
                canvas.style.removeProperty('height');
                canvas.style.removeProperty('width');

                // Asegurar que el contenedor tenga dimensiones correctas
                const wrapper = canvas.parentElement;
                if (wrapper) {
                    wrapper.style.height = '300px';
                    wrapper.style.width = '100%';
                    wrapper.style.overflow = 'visible';
                }
            }
            // Actualizar el gráfico correspondiente si existe
            const chartKeys = ['students', 'jobs', 'applications', 'successRate'];
            const chart = this.charts[chartKeys[index]];
            if (chart && typeof chart.resize === 'function') {
                chart.resize();
                chart.update('none');
            }
        });
    }

    /**
     * Forzar dimensiones de gráficos de manera agresiva
     */
    forceChartDimensions() {
        const chartIds = ['students-chart', 'jobs-chart', 'applications-chart', 'success-rate-chart'];
        chartIds.forEach((id, index) => {
            const canvas = document.getElementById(id);
            if (canvas) {
                // Limpiar cualquier dimensión previa del canvas
                canvas.removeAttribute('height');
                canvas.removeAttribute('width');
                canvas.style.removeProperty('height');
                canvas.style.removeProperty('width');

                // Forzar dimensiones del wrapper
                const wrapper = canvas.parentElement;
                if (wrapper) {
                    wrapper.style.height = '300px';
                    wrapper.style.width = '100%';
                    wrapper.style.overflow = 'visible';
                    wrapper.style.position = 'relative';
                }
            }
            // Actualizar el gráfico correspondiente si existe
            const chartKeys = ['students', 'jobs', 'applications', 'successRate'];
            const chart = this.charts[chartKeys[index]];
            if (chart && typeof chart.resize === 'function') {
                chart.resize();
                chart.update('none');
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
