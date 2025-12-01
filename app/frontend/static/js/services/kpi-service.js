/**
 * KPI Service - Servicio centralizado para cálculos de KPIs
 * Garantiza consistencia entre todos los dashboards y roles
 */

class KPIService {
    constructor() {
        this.cache = {};
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutos
    }

    /**
     * Obtener todos los KPIs calculados
     */
    async getAllKPIs() {
        try {
            // Verificar cache
            const now = Date.now();
            if (this.cache.data && (now - this.cache.timestamp) < this.cacheTimeout) {
                console.log('📊 Usando KPIs del cache');
                return this.cache.data;
            }

            console.log('📊 Calculando KPIs...');

            // Calcular KPIs desde múltiples fuentes
            const [userKPIs, jobKPIs, applicationKPIs] = await Promise.all([
                this.calculateUserKPIs(),
                this.calculateJobKPIs(),
                this.calculateApplicationKPIs()
            ]);

            // Combinar todos los KPIs
            const kpis = {
                ...userKPIs,
                ...jobKPIs,
                ...applicationKPIs,

                // KPIs calculados adicionales
                matching_rate: this.calculateMatchingRate(jobKPIs, applicationKPIs),

                // Cambios porcentuales (simulados por ahora)
                student_change: 0,
                company_change: 0,
                job_change: 0,
                app_change: 0,
                matching_rate_change: 0
            };

            // Cachear resultado
            this.cache = {
                data: kpis,
                timestamp: now
            };

            console.log('📊 KPIs calculados:', kpis);
            return kpis;

        } catch (error) {
            console.error('❌ Error calculando KPIs:', error);
            return this.getDefaultKPIs();
        }
    }

    /**
     * Calcular KPIs de usuarios
     */
    async calculateUserKPIs() {
        try {
            // En modo demo, usar datos simulados
            const urlParams = new URLSearchParams(window.location.search);
            const isDemoMode = urlParams.get('demo') === 'true';

            if (isDemoMode) {
                return {
                    total_users: 50,
                    total_students: 45,
                    total_companies: 5,
                    active_users: 48
                };
            }

            // TODO: Implementar llamada a API de usuarios cuando esté disponible
            // Por ahora, datos simulados
            return {
                total_users: 50,
                total_students: 45,
                total_companies: 5,
                active_users: 48
            };

        } catch (error) {
            console.warn('⚠️ Error calculando KPIs de usuarios:', error);
            return {
                total_users: 0,
                total_students: 0,
                total_companies: 0,
                active_users: 0
            };
        }
    }

    /**
     * Calcular KPIs de empleos
     */
    async calculateJobKPIs() {
        try {
            // Asegurar que el cache esté fresco antes de calcular
            await this.ensureCacheFreshness();

            // Obtener datos de empleos desde background-job-search o API directa
            let jobs = [];

            if (window.backgroundJobSearch && window.backgroundJobSearch.getResults) {
                jobs = window.backgroundJobSearch.getResults() || [];
            }

            if (jobs.length === 0) {
                // Intentar búsqueda directa en API
                jobs = await this.searchJobsFromAPI();
            }

            // Usar el método específico para calcular KPIs desde datos de empleos
            return this.calculateKPIsFromJobsData(jobs);

        } catch (error) {
            console.warn('⚠️ Error calculando KPIs de empleos:', error);
            return {
                total_jobs: 0,
                active_jobs: 0
            };
        }
    }

    /**
     * Calcular KPIs de aplicaciones
     */
    async calculateApplicationKPIs() {
        try {
            // En modo demo, usar datos simulados
            const urlParams = new URLSearchParams(window.location.search);
            const isDemoMode = urlParams.get('demo') === 'true';

            if (isDemoMode) {
                return {
                    total_applications: 47
                };
            }

            // TODO: Implementar llamada a API de aplicaciones cuando esté disponible
            return {
                total_applications: 0
            };

        } catch (error) {
            console.warn('⚠️ Error calculando KPIs de aplicaciones:', error);
            return {
                total_applications: 0
            };
        }
    }

    /**
     * Calcular tasa de matching
     */
    calculateMatchingRate(jobKPIs, applicationKPIs) {
        const { active_jobs = 0 } = jobKPIs;
        const { total_applications = 0 } = applicationKPIs;

        if (total_applications === 0) return 0;

        return Math.round((active_jobs / total_applications) * 100);
    }

    /**
     * Buscar empleos desde API directa
     */
    async searchJobsFromAPI() {
        try {
            const keywords = ['python', 'javascript', 'desarrollador', 'ingeniero'];
            let allJobs = [];

            for (const keyword of keywords) {
                try {
                    const response = await fetch(`${window.API_BASE_URL}/jobs/search?keyword=${encodeURIComponent(keyword)}&limit=10`);

                    if (response.ok) {
                        const data = await response.json();
                        if (data.items && Array.isArray(data.items)) {
                            allJobs = allJobs.concat(data.items);
                        }
                    }
                } catch (error) {
                    console.warn(`⚠️ Error buscando ${keyword}:`, error.message);
                }
            }

            // Remover duplicados
            const uniqueJobs = allJobs.filter((job, index, self) =>
                index === self.findIndex(j => j.external_job_id === job.external_job_id || j.id === job.id)
            );

            return uniqueJobs;

        } catch (error) {
            console.warn('⚠️ Error en búsqueda directa de empleos:', error.message);
            return [];
        }
    }

    /**
     * KPIs por defecto en caso de error
     */
    getDefaultKPIs() {
        return {
            total_users: 0,
            total_students: 0,
            total_companies: 0,
            active_users: 0,
            total_jobs: 0,
            active_jobs: 0,
            total_applications: 0,
            success_rate: 0,
            matching_rate: 0,
            student_change: 0,
            company_change: 0,
            job_change: 0,
            app_change: 0,
            matching_rate_change: 0
        };
    }

    /**
     * Limpiar cache
     */
    clearCache() {
        this.cache = {};
        console.log('🧹 Cache de KPIs limpiado');
    }

    /**
     * Forzar recálculo de KPIs
     */
    async refreshKPIs() {
        this.clearCache();
        return await this.getAllKPIs();
    }

    /**
     * Calcular KPIs directamente desde datos de empleos
     * Método específico para usar con cache de background-job-search
     */
    calculateKPIsFromJobsData(jobsData) {
        if (!jobsData || !Array.isArray(jobsData)) {
            return {
                total_jobs: 0,
                active_jobs: 0,
                matching_rate: 0
            };
        }

        const total_jobs = jobsData.length;
        const active_jobs = jobsData.filter(job => job.is_active !== false).length;

        // Calcular matching rate basado en empleos activos vs total
        const matching_rate = total_jobs > 0 ? Math.round((active_jobs / total_jobs) * 100) : 0;

        return {
            total_jobs,
            active_jobs,
            matching_rate
        };
    }

    /**
     * Verificar la frescura del cache (4 horas máximo)
     */
    getCacheFreshness() {
        try {
            // Intentar obtener datos del background-job-search service
            if (window.backgroundJobSearch && window.backgroundJobSearch.getResults) {
                const jobs = window.backgroundJobSearch.getResults();
                if (jobs && jobs.length > 0) {
                    // Verificar si hay timestamp en los datos
                    const firstJob = jobs[0];
                    if (firstJob.created_at || firstJob.timestamp) {
                        const jobTime = new Date(firstJob.created_at || firstJob.timestamp).getTime();
                        const now = Date.now();
                        const ageHours = (now - jobTime) / (1000 * 60 * 60);

                        return {
                            isFresh: ageHours <= 4,
                            ageHours: Math.round(ageHours * 10) / 10,
                            lastUpdate: new Date(jobTime).toLocaleString()
                        };
                    }
                }
            }

            return {
                isFresh: false,
                ageHours: null,
                lastUpdate: null
            };

        } catch (error) {
            console.warn('⚠️ Error verificando frescura del cache:', error.message);
            return {
                isFresh: false,
                ageHours: null,
                lastUpdate: null
            };
        }
    }

    /**
     * Asegurar que el cache esté fresco (máximo 4 horas)
     * Si no está fresco, intenta refrescar desde API
     */
    async ensureCacheFreshness() {
        const freshness = this.getCacheFreshness();

        if (freshness.isFresh) {
            console.log(`✅ Cache fresco: ${freshness.ageHours}h desde última actualización`);
            return true;
        }

        console.log(`⚠️ Cache obsoleto: ${freshness.ageHours || 'desconocido'}h desde última actualización`);

        // Intentar refrescar el cache iniciando background search si no está corriendo
        if (window.backgroundJobSearch && !window.backgroundJobSearch.isRunning) {
            console.log('🔄 Iniciando refresco de cache...');
            window.backgroundJobSearch.start();

            // Esperar un poco para que cargue datos iniciales
            await new Promise(resolve => setTimeout(resolve, 2000));

            // Verificar si ahora tenemos datos frescos
            const newFreshness = this.getCacheFreshness();
            if (newFreshness.isFresh) {
                console.log('✅ Cache refrescado exitosamente');
                return true;
            }
        }

        console.log('⚠️ No se pudo refrescar el cache automáticamente');
        return false;
    }
}

// Instancia global
const kpiService = new KPIService();
window.kpiService = kpiService;
