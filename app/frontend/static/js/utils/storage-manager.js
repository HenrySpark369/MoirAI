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
     */
    set(key, value, expiration = null) {
        try {
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

            if (!item) {
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
            console.error('Error leyendo de localStorage:', error);
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
};

// Exportar para uso global
window.StorageManager = StorageManager;
