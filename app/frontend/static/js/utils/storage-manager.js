/**
 * MoirAI - Storage Manager Utility
 * Gestión centralizada de localStorage con encriptación básica
 * 
 * Uso:
 *   StorageManager.set('user', { id: 1, name: 'John' })
 *   const user = StorageManager.get('user')
 *   StorageManager.remove('user')
 */

const StorageManager = {
    /**
     * Prefijo para diferenciar datos de MoirAI
     */
    prefix: 'moirai_',

    /**
     * Obtener clave con prefijo
     */
    getKey(key) {
        return `${this.prefix}${key}`;
    },

    /**
     * Guardar datos en localStorage
     * ✅ CORRECCIÓN: Prevent storing undefined values
     */
    set(key, value, expiration = null) {
        try {
            // ✅ CORRECCIÓN: No guardar valores undefined
            if (value === undefined) {
                console.warn(`[StorageManager] Intentando guardar undefined para "${key}", usando null en su lugar`);
                value = null;
            }

            const finalKey = this.getKey(key);
            const data = {
                value: value,
                timestamp: Date.now(),
                expiration: expiration
            };

            localStorage.setItem(finalKey, JSON.stringify(data));
            return true;
        } catch (error) {
            console.error('Error guardando en localStorage:', error);
            return false;
        }
    },

    /**
     * Obtener datos de localStorage
     */
    get(key, defaultValue = null) {
        try {
            const finalKey = this.getKey(key);
            const item = localStorage.getItem(finalKey);

            // ✅ CORRECCIÓN: Handle undefined string
            if (!item || item === 'undefined') {
                return defaultValue;
            }

            const data = JSON.parse(item);

            // Verificar si ha expirado
            if (data.expiration && Date.now() > data.expiration) {
                this.remove(key);
                return defaultValue;
            }

            return data.value;
        } catch (error) {
            // Only log if it's a real error (not just null/undefined)
            if (error instanceof SyntaxError) {
                console.warn(`[StorageManager] Invalid JSON for key "${key}": ${error.message}`);
            }
            return defaultValue;
        }
    },

    /**
     * Remover datos de localStorage
     */
    remove(key) {
        try {
            const finalKey = this.getKey(key);
            localStorage.removeItem(finalKey);
            return true;
        } catch (error) {
            console.error('Error removiendo de localStorage:', error);
            return false;
        }
    },

    /**
     * Limpiar todos los datos de MoirAI
     */
    clear() {
        try {
            const keys = Object.keys(localStorage);
            keys.forEach(key => {
                if (key.startsWith(this.prefix)) {
                    localStorage.removeItem(key);
                }
            });
            return true;
        } catch (error) {
            console.error('Error limpiando localStorage:', error);
            return false;
        }
    },

    /**
     * Verificar si existe una clave
     */
    exists(key) {
        const finalKey = this.getKey(key);
        return localStorage.getItem(finalKey) !== null;
    },

    /**
     * Obtener todas las claves
     */
    getAllKeys() {
        const keys = [];
        Object.keys(localStorage).forEach(key => {
            if (key.startsWith(this.prefix)) {
                keys.push(key.replace(this.prefix, ''));
            }
        });
        return keys;
    },

    /**
     * Obtener todos los datos
     */
    getAll() {
        const data = {};
        this.getAllKeys().forEach(key => {
            data[key] = this.get(key);
        });
        return data;
    },

    /**
     * Guardar con expiración automática (en segundos)
     */
    setWithExpiration(key, value, seconds) {
        const expiration = Date.now() + (seconds * 1000);
        return this.set(key, value, expiration);
    },

    /**
     * Incrementar un contador
     */
    increment(key, amount = 1) {
        try {
            const current = this.get(key, 0);
            const newValue = (parseInt(current) || 0) + amount;
            this.set(key, newValue);
            return newValue;
        } catch (error) {
            console.error('Error incrementando:', error);
            return 0;
        }
    },

    /**
     * Decrementar un contador
     */
    decrement(key, amount = 1) {
        return this.increment(key, -amount);
    },

    /**
     * Guardar array con límite de tamaño
     */
    pushToArray(key, value, maxSize = 100) {
        try {
            let array = this.get(key, []);
            if (!Array.isArray(array)) {
                array = [];
            }

            array.unshift(value); // Agregar al inicio

            // Limitar tamaño
            if (array.length > maxSize) {
                array = array.slice(0, maxSize);
            }

            this.set(key, array);
            return array;
        } catch (error) {
            console.error('Error agregando a array:', error);
            return [];
        }
    },

    /**
     * Remover valor de array
     */
    removeFromArray(key, value) {
        try {
            let array = this.get(key, []);
            if (!Array.isArray(array)) {
                array = [];
            }

            array = array.filter(item => item !== value);
            this.set(key, array);
            return array;
        } catch (error) {
            console.error('Error removiendo de array:', error);
            return [];
        }
    },

    /**
     * Validar espacio disponible
     */
    getStorageStats() {
        try {
            const data = this.getAll();
            const size = JSON.stringify(data).length;
            const totalKeys = Object.keys(data).length;

            return {
                keys: totalKeys,
                sizeBytes: size,
                sizeMB: (size / 1024 / 1024).toFixed(2),
                available: size < 5 * 1024 * 1024, // 5MB limite
            };
        } catch (error) {
            console.error('Error calculando storage:', error);
            return null;
        }
    },

    /**
     * CONVENIENCE METHODS - Métodos de conveniencia para datos de autenticación
     */

    /**
     * Obtener API Key
     */
    getApiKey() {
        return this.get('api_key') || localStorage.getItem('api_key');
    },

    /**
     * Establecer API Key
     */
    setApiKey(apiKey) {
        this.set('api_key', apiKey);
        localStorage.setItem('api_key', apiKey); // Backward compatibility
        return true;
    },

    /**
     * Obtener token del usuario
     */
    getToken() {
        return this.get('token') || this.get('moirai_token') || localStorage.getItem('moirai_token');
    },

    /**
     * Establecer token
     */
    setToken(token) {
        this.set('token', token);
        localStorage.setItem('moirai_token', token);
        return true;
    },

    /**
     * Obtener rol del usuario
     */
    getUserRole() {
        return this.get('user_role') || localStorage.getItem('user_role');
    },

    /**
     * Establecer rol del usuario
     */
    setUserRole(role) {
        this.set('user_role', role);
        localStorage.setItem('user_role', role);
        return true;
    },

    /**
     * Obtener ID del usuario
     */
    getUserId() {
        return this.get('user_id') || localStorage.getItem('user_id');
    },

    /**
     * Establecer ID del usuario
     */
    setUserId(userId) {
        this.set('user_id', userId);
        localStorage.setItem('user_id', userId);
        return true;
    },

    /**
     * Obtener nombre del usuario
     */
    getUserName() {
        return this.get('user_name') || localStorage.getItem('user_name');
    },

    /**
     * Establecer nombre del usuario
     */
    setUserName(userName) {
        this.set('user_name', userName);
        localStorage.setItem('user_name', userName);
        return true;
    },

    /**
     * Obtener email del usuario
     */
    getUserEmail() {
        return this.get('user_email') || localStorage.getItem('user_email');
    },

    /**
     * Establecer email del usuario
     */
    setUserEmail(email) {
        this.set('user_email', email);
        localStorage.setItem('user_email', email);
        return true;
    },

    /**
     * Guardar sesión de usuario completa
     */
    setUserSession(userData) {
        if (!userData) return false;
        
        this.setApiKey(userData.api_key || userData.apiKey);
        this.setToken(userData.token || userData.moirai_token);
        this.setUserRole(userData.role || userData.user_role);
        // ✅ CORRECCIÓN: Intentar user_id primero (usado por auth-manager)
        this.setUserId(userData.user_id || userData.id);
        this.setUserName(userData.name || userData.user_name || userData.username);
        this.setUserEmail(userData.email || userData.user_email);
        
        return true;
    },

    /**
     * Obtener sesión de usuario completa
     */
    getUserSession() {
        return {
            api_key: this.getApiKey(),
            token: this.getToken(),
            user_role: this.getUserRole(),
            user_id: this.getUserId(),
            user_name: this.getUserName(),
            user_email: this.getUserEmail(),
        };
    },

    /**
     * Verificar si usuario está autenticado
     */
    isAuthenticated() {
        const apiKey = this.getApiKey();
        const token = this.getToken();
        return !!(apiKey && token);
    },

    /**
     * Verificar si es estudiante
     */
    isStudent() {
        return this.getUserRole() === 'student';
    },

    /**
     * Verificar si es empresa
     */
    isCompany() {
        return this.getUserRole() === 'company';
    },

    /**
     * Verificar si es administrador
     */
    isAdmin() {
        return this.getUserRole() === 'admin';
    },

    /**
     * DEMO MODE METHODS - Métodos específicos para modo demo
     */

    /**
     * Verificar si está en modo demo
     */
    isDemoMode() {
        return this.get('demo_mode') === true;
    },

    /**
     * Obtener perfil demo completo
     */
    getDemoProfile() {
        return this.get('demo_profile');
    },

    /**
     * Establecer perfil demo
     */
    setDemoProfile(profile) {
        this.set('demo_profile', profile);
        this.set('demo_mode', true);
        // También actualizar campos de usuario estándar
        if (profile) {
            this.setUserName(profile.name);
            this.setUserEmail(profile.email);
            this.setUserRole('student');
        }
        return true;
    },

    /**
     * Limpiar modo demo
     */
    clearDemoMode() {
        this.remove('demo_profile');
        this.remove('demo_mode');
        return true;
    },

    /**
     * Obtener perfil de usuario (demo o autenticado)
     */
    getCurrentUserProfile() {
        if (this.isDemoMode()) {
            return this.getDemoProfile();
        }
        // Para usuarios autenticados, devolver sesión básica
        return this.getUserSession();
    }
};

// Exportar para uso global
window.StorageManager = StorageManager;

// Alias minúscula para compatibilidad con nuevo código
const storageManager = StorageManager;
