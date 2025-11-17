/**
 * Auth Manager - Gestión de autenticación y sesión de usuario
 */

class AuthManager {
  constructor(apiClient) {
    this.api = apiClient
    this.currentUser = null
    this.listeners = []
  }

  /**
   * Registrar un callback que se ejecute cuando cambie el estado de autenticación
   */
  onChange(callback) {
    this.listeners.push(callback)
  }

  /**
   * Notificar cambios a todos los listeners
   */
  notifyListeners() {
    this.listeners.forEach(callback => callback(this.currentUser))
  }

  /**
   * Registro de nuevo usuario
   * ✅ CORRECCIÓN: Mapea correctamente api_key de la respuesta
   */
  async register(userData) {
    try {
      const response = await this.api.post('/auth/register', {
        // ✅ Backend espera estructura correcta
        name: userData.name || `${userData.firstName} ${userData.lastName}`.trim(),
        email: userData.email,
        password: userData.password,
        role: userData.role || userData.userType || 'student',
        program: userData.program,              // Para estudiantes
        industry: userData.industry,            // Para empresas
        company_size: userData.companySize,     // Para empresas
        location: userData.location             // Para empresas
      })

      // ✅ CORRECCIÓN: Mapear api_key correctamente (no token)
      if (response.api_key) {
        this.api.setToken(response.api_key)
      }

      this.currentUser = {
        user_id: response.user_id,
        email: userData.email,
        name: userData.name || `${userData.firstName} ${userData.lastName}`.trim(),
        role: response.role || userData.role || 'student'
      }

      this.notifyListeners()
      return response

    } catch (error) {
      console.error('Error en registro:', error)
      throw {
        message: error.message || 'Error al registrar usuario',
        code: error.status
      }
    }
  }

  /**
   * Login con email y contraseña
   * ✅ CORRECCIÓN: Mapea correctamente api_key de la respuesta
   * ✅ Si no viene api_key, usa la guardada del registro
   */
  async login(email, password) {
    try {
      console.log('📍 Iniciando login...');
      
      const response = await this.api.post('/auth/login', {
        email,
        password
      })

      console.log('📍 Respuesta del login:', {
        user_id: response.user_id,
        email: response.email,
        role: response.role,
        api_key_presente: !!response.api_key,
        api_key_vacio: response.api_key === '',
        api_key_length: response.api_key?.length || 0
      });

      // ✅ CORRECCIÓN: Verificar api_key o usar la del registro
      let apiKey = response.api_key;
      
      // Si no viene api_key en la respuesta, usar la guardada del registro
      if (!apiKey || apiKey === '' || apiKey === undefined) {
        console.log('⚠️ api_key vacío o no presente, buscando en localStorage...');
        apiKey = localStorage.getItem('api_key');
        
        console.log('📍 localStorage api_key:', {
          presente: !!apiKey,
          length: apiKey?.length || 0
        });
        
        // Si tampoco está en localStorage, error
        if (!apiKey) {
          console.error('❌ No se encontró API key en respuesta ni en localStorage');
          throw new Error('No se recibió API key de autenticación. Por favor, vuelve a registrarte.')
        }
      }

      console.log('✅ API key obtenida, usando para autenticación');

      // ✅ CORRECCIÓN: Usar api_key en lugar de token
      this.api.setToken(apiKey)
      
      this.currentUser = {
        user_id: response.user_id,
        email: response.email,
        name: response.name,
        role: response.role
      }

      // ✅ ACTUALIZACIÓN: Guardar en localStorage
      localStorage.setItem('api_key', apiKey)
      localStorage.setItem('user_id', response.user_id.toString())
      localStorage.setItem('user_role', response.role)
      localStorage.setItem('user_email', response.email)

      console.log('✅ Datos guardados en localStorage');

      this.notifyListeners()
      return response

    } catch (error) {
      console.error('❌ Error en login:', error)
      throw {
        message: error.message || 'Error al iniciar sesión',
        code: error.status,
        isAuthError: error.status === 401
      }
    }
  }

  /**
   * Logout
   */
  async logout() {
    try {
      if (this.api.isAuthenticated()) {
        await this.api.post('/auth/logout')
      }
    } catch (error) {
      console.warn('Error en logout:', error)
    }

    this.api.clearToken()
    this.currentUser = null
    this.notifyListeners()
  }

  /**
   * Obtener usuario actual
   */
  async getCurrentUser() {
    try {
      if (!this.api.isAuthenticated()) {
        return null
      }

      if (this.currentUser) {
        return this.currentUser
      }

      const response = await this.api.get('/auth/me')
      this.currentUser = response.user || response

      return this.currentUser

    } catch (error) {
      console.error('Error obtener usuario actual:', error)
      if (error.status === 401) {
        this.api.clearToken()
        this.currentUser = null
      }
      return null
    }
  }

  /**
   * Verificar si el usuario está autenticado
   */
  isAuthenticated() {
    return this.api.isAuthenticated() && !!this.currentUser
  }

  /**
   * Renovar token si es necesario
   */
  async refreshToken() {
    try {
      const response = await this.api.post('/auth/refresh')
      if (response.token) {
        this.api.setToken(response.token)
        return true
      }
      return false
    } catch (error) {
      console.error('Error renovando token:', error)
      return false
    }
  }

  /**
   * Cambiar contraseña
   */
  async changePassword(currentPassword, newPassword) {
    try {
      const response = await this.api.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword
      })
      return response
    } catch (error) {
      console.error('Error cambiando contraseña:', error)
      throw {
        message: error.message || 'Error al cambiar contraseña',
        code: error.status
      }
    }
  }

  /**
   * Solicitar reset de contraseña
   */
  async requestPasswordReset(email) {
    try {
      const response = await this.api.post('/auth/forgot-password', { email })
      return response
    } catch (error) {
      console.error('Error solicitando reset:', error)
      throw {
        message: error.message || 'Error al solicitar reset de contraseña',
        code: error.status
      }
    }
  }

  /**
   * Confirmar reset de contraseña
   */
  async resetPassword(token, newPassword) {
    try {
      const response = await this.api.post('/auth/reset-password', {
        token,
        new_password: newPassword
      })
      return response
    } catch (error) {
      console.error('Error confirmando reset:', error)
      throw {
        message: error.message || 'Error al confirmar reset de contraseña',
        code: error.status
      }
    }
  }

  /**
   * Obtener rol del usuario actual
   */
  getUserRole() {
    if (!this.currentUser) return null
    return this.currentUser.user_type || this.currentUser.role
  }

  /**
   * Verificar si es estudiante
   */
  isStudent() {
    return this.getUserRole() === 'student'
  }

  /**
   * Verificar si es empresa
   */
  isCompany() {
    return this.getUserRole() === 'company'
  }

  /**
   * Verificar si es administrador
   */
  isAdmin() {
    return this.getUserRole() === 'admin'
  }

  /**
   * Obtener información del usuario actual
   */
  getUserInfo() {
    return this.currentUser
  }

  /**
   * Obtener ID del usuario actual
   */
  getUserId() {
    return this.currentUser?.id
  }

  /**
   * Obtener email del usuario actual
   */
  getUserEmail() {
    return this.currentUser?.email
  }
}

// Crear instancia global del AuthManager
const authManager = new AuthManager(apiClient)

// Auto-cargar usuario actual al iniciar
document.addEventListener('DOMContentLoaded', async () => {
  if (apiClient.isAuthenticated()) {
    await authManager.getCurrentUser()
  }
})

// Event listener global para unauthorized
window.addEventListener('unauthorized', () => {
  authManager.currentUser = null
  authManager.notifyListeners()
})
