/**
 * Background Job Search Service
 * Realiza búsquedas automáticas en segundo plano con amplia cobertura de palabras clave
 * Se integra con jobs-search.js para alimentar el catálogo de oportunidades
 */

class BackgroundJobSearchService {
    constructor() {
        this.isRunning = false;
        this.isSearching = false;
        this.currentBatchIndex = 0;
        this.allResults = [];
        this.searchBatches = [
            // Batch 1: Tecnología
            ['python', 'javascript', 'react', 'sql', 'nodejs', 'typescript', 'angular'],
            // Batch 2: Backend & Cloud
            ['backend', 'api', 'aws', 'docker', 'kubernetes', 'microservices'],
            // Batch 3: Frontend & UI
            ['frontend', 'html', 'css', 'vue', 'webdesign', 'ui', 'ux'],
            // Batch 4: Data & AI
            ['data', 'machine learning', 'analytics', 'big data', 'sql', 'python'],
            // Batch 5: Devops & Infrastructure
            ['devops', 'linux', 'networking', 'infrastructure', 'ci/cd'],
            // Batch 6: Mobile
            ['mobile', 'android', 'ios', 'flutter', 'react native'],
            // Batch 7: QA & Testing
            ['testing', 'qa', 'automation', 'selenium', 'quality assurance'],
            // Batch 8: Empleos generales
            ['empleo', 'trabajo', 'vacante', 'junior', 'senior'],
            // Batch 9: Habilidades blandas
            ['liderazgo', 'comunicación', 'gestión de proyectos', 'análisis'],
            // Batch 10: Sectores
            ['finanzas', 'marketing', 'recursos humanos', 'administración']
        ];
        this.batchDelay = 3000; // 3 segundos entre batches
        this.maxResultsPerBatch = 20;
    }

    /**
     * Iniciar búsqueda en segundo plano
     */
    async start() {
        if (this.isRunning) {
            console.log('⏸️ Búsqueda en segundo plano ya está activa');
            return;
        }

        this.isRunning = true;
        this.currentBatchIndex = 0;
        this.allResults = [];

        console.log('🔍 Iniciando búsqueda automática en segundo plano...');
        console.log(`📊 Total de batches: ${this.searchBatches.length}`);

        // ✨ NUEVO: Cargar cache existente ANTES de buscar
        try {
            const cachedJobs = await this.loadFromCache();
            if (cachedJobs && cachedJobs.length > 0) {
                this.allResults = cachedJobs;
                console.log(`✅ Cache cargado: ${cachedJobs.length} empleos disponibles`);
                
                // Disparar evento para mostrar datos inmediatamente
                window.dispatchEvent(new CustomEvent('cacheLoaded', {
                    detail: { jobs: cachedJobs, count: cachedJobs.length }
                }));
            } else {
                console.log('📦 No hay cache disponible, comenzando búsqueda...');
            }
        } catch (error) {
            console.warn('⚠️ Error al cargar cache:', error.message);
            // Continuar sin cache
        }

        // Ejecutar búsquedas en segundo plano
        this.executeNextBatch();
    }

    /**
     * Detener búsqueda en segundo plano
     */
    stop() {
        this.isRunning = false;
        this.isSearching = false;
        console.log('⏹️ Búsqueda en segundo plano detenida');
    }

    /**
     * Ejecutar siguiente batch de búsqueda
     */
    async executeNextBatch() {
        if (!this.isRunning || this.currentBatchIndex >= this.searchBatches.length) {
            if (this.currentBatchIndex >= this.searchBatches.length) {
                console.log('✅ Búsqueda en segundo plano completada');
                console.log(`📊 Total de empleos encontrados: ${this.allResults.length}`);
                
                // Notificar que data está lista
                window.dispatchEvent(new CustomEvent('backgroundJobsReady', {
                    detail: { jobs: this.allResults, count: this.allResults.length }
                }));
            }
            this.isRunning = false;
            return;
        }

        const keywords = this.searchBatches[this.currentBatchIndex];
        const batchNumber = this.currentBatchIndex + 1;

        console.log(`📦 Batch ${batchNumber}/${this.searchBatches.length}: ${keywords.join(', ')}`);

        try {
            // Búsqueda para cada keyword del batch
            for (const keyword of keywords) {
                if (!this.isRunning) break;

                await this.searchKeyword(keyword);
                
                // Pequeño delay entre keywords para no sobrecargar
                await this.delay(500);
            }

            // Incrementar índice y agendar siguiente batch
            this.currentBatchIndex++;

            if (this.isRunning) {
                // Esperar antes del siguiente batch
                console.log(`⏳ Esperando ${this.batchDelay}ms antes del siguiente batch...`);
                setTimeout(() => this.executeNextBatch(), this.batchDelay);
            }

        } catch (error) {
            console.error(`❌ Error en batch ${batchNumber}:`, error);
            
            // Continuar con siguiente batch a pesar del error
            this.currentBatchIndex++;
            setTimeout(() => this.executeNextBatch(), this.batchDelay);
        }
    }

    /**
     * Buscar por una palabra clave específica
     * ✨ MEJORADO: Usa más parámetros para búsquedas más relevantes
     */
    async searchKeyword(keyword) {
        if (this.isSearching) {
            // Si ya hay una búsqueda en progreso, esperar
            await this.waitForSearchComplete();
        }

        this.isSearching = true;

        try {
            // ✨ Usar el endpoint de scraping que retorna JobOffer con job_id
            const params = new URLSearchParams({
                keyword: keyword,
                detailed: 'true',
                full_details: 'false',
                limit: this.maxResultsPerBatch.toString()
            });

            const response = await apiClient.post('/job-scraping/search', {
                keyword: keyword,
                location: null,
                category: null,
                limit: this.maxResultsPerBatch
            });

            if (response.jobs && Array.isArray(response.jobs)) {
                // Filtrar duplicados por job_id
                const newJobs = response.jobs.slice(0, this.maxResultsPerBatch);
                const filteredJobs = newJobs.filter(job => 
                    !this.allResults.some(existing => existing.id === job.id || existing.job_id === job.job_id)
                );

                if (filteredJobs.length > 0) {
                    this.allResults.push(...filteredJobs);
                    
                    // ✨ NUEVO: Guardar en cache (no-blocking)
                    this.saveToCache(filteredJobs, keyword).catch(err => 
                        console.warn('⚠️ Error guardando cache:', err.message)
                    );
                    
                    console.log(`✅ "${keyword}": ${filteredJobs.length} empleos agregados (total: ${this.allResults.length})`);
                    
                    // Disparar evento para actualización en tiempo real
                    window.dispatchEvent(new CustomEvent('jobsUpdated', {
                        detail: { 
                            keyword: keyword,
                            newJobs: filteredJobs,
                            totalJobs: this.allResults.length
                        }
                    }));
                } else {
                    console.log(`⚪ "${keyword}": Sin empleos nuevos`);
                }
            }

        } catch (error) {
            console.warn(`⚠️ Error buscando "${keyword}":`, error.message);
            // No lanzar error, solo registrar y continuar
        } finally {
            this.isSearching = false;
        }
    }

    /**
     * Esperar a que se complete la búsqueda actual
     */
    async waitForSearchComplete() {
        return new Promise(resolve => {
            const checkInterval = setInterval(() => {
                if (!this.isSearching) {
                    clearInterval(checkInterval);
                    resolve();
                }
            }, 100);
            
            // Timeout de 10 segundos
            setTimeout(() => {
                clearInterval(checkInterval);
                resolve();
            }, 10000);
        });
    }

    /**
     * Helper: Delay
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Obtener resultados actuales
     */
    getResults() {
        return this.allResults;
    }

    /**
     * Obtener progreso
     */
    getProgress() {
        return {
            currentBatch: this.currentBatchIndex,
            totalBatches: this.searchBatches.length,
            percentage: Math.round((this.currentBatchIndex / this.searchBatches.length) * 100),
            totalJobs: this.allResults.length,
            isRunning: this.isRunning,
            isSearching: this.isSearching
        };
    }

    /**
     * Limpiar resultados
     */
    clear() {
        this.allResults = [];
        this.currentBatchIndex = 0;
        console.log('🧹 Resultados limpios');
    }

    /**
     * ✨ Cargar empleos del cache persistente (BD)
     */
    async loadFromCache() {
        try {
            console.log('📦 Cargando empleos desde cache API...');

            const response = await fetch(`${window.API_BASE_URL}/job-scraping/cache/list?limit=200&offset=0`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data && data.jobs && Array.isArray(data.jobs)) {
                console.log(`📦 Cache cargado: ${data.jobs.length} de ${data.total} empleos disponibles`);

                // ✨ Mapear IDs para consistencia con getDemoJobs()
                const mappedJobs = data.jobs.map(job => ({
                    ...job,
                    id: job.external_job_id || job.id,  // Use external_job_id as id for compatibility
                    job_id: job.external_job_id || job.id,
                    skills: Array.isArray(job.skills) ? job.skills : (job.skills ? JSON.parse(job.skills) : [])
                }));

                return mappedJobs;
            }

            console.log('📦 Cache vacío o sin datos');
            return [];

        } catch (error) {
            console.warn('⚠️ Error cargando cache:', error.message);
            return [];
        }
    }

    /**
     * ✨ Guardar empleos en cache persistente (BD) después de cada búsqueda
     */
    async saveToCache(jobs, keyword) {
        try {
            // Validación de entrada
            if (!jobs || jobs.length === 0) {
                console.warn('Sin empleos para guardar en cache');
                return 0;
            }

            console.log(`Guardando ${jobs.length} empleos en cache (keyword: "${keyword}")`);

            const response = await fetch(`${window.API_BASE_URL}/job-scraping/cache/store`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    jobs: jobs,
                    keyword: keyword,
                    source: 'occ'
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.saved_count && data.saved_count > 0) {
                console.log(`Cache: ${data.saved_count} empleos guardados`);
                if (data.total_cached) {
                    console.log(`Total en cache: ${data.total_cached} empleos`);
                }
                return data.saved_count;
            }

            console.log('No se guardaron empleos en cache');
            return 0;

        } catch (error) {
            console.warn('Error guardando en cache:', error.message);
            return 0;
        }
    }
}

// Instancia global
const backgroundJobSearch = new BackgroundJobSearchService();

// Exponer globalmente para acceso desde otros módulos
window.backgroundJobSearch = backgroundJobSearch;
