/**
 * API Client - Cliente HTTP para todas las llamadas a la API
 * Maneja tokens, headers, errores y reintentos
 */

class ApiClient {
  constructor(baseUrl = 'http://localhost:8000/api/v1') {
    this.baseUrl = baseUrl
    this.token = null
    this.loadToken()
  }

  /**
   * Cargar token del localStorage si existe
   * ✅ CORRECCIÓN: Ahora busca en 'api_key' en lugar de 'auth_token'
   */
  loadToken() {
    const token = localStorage.getItem('api_key')
    if (token) {
      this.setToken(token)
    }
  }

  /**
   * Guardar y usar un nuevo token (API key)
   * ✅ CORRECCIÓN: Almacena en 'api_key'
   */
  setToken(token) {
    this.token = token
    if (token) {
      localStorage.setItem('api_key', token)
    } else {
      localStorage.removeItem('api_key')
    }
  }

  /**
   * Construir headers con API key
   * ✅ CORRECCIÓN: Usa X-API-Key header en lugar de Bearer token
   */
  getHeaders(additionalHeaders = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...additionalHeaders
    }

    if (this.token) {
      // ✅ Backend espera X-API-Key header, no Authorization Bearer
      headers['X-API-Key'] = this.token
    }

    return headers
  }

  /**
   * Realizar request genérico
   */
  async request(method, endpoint, data = null, options = {}) {
    const url = `${this.baseUrl}${endpoint}`
    
    const fetchOptions = {
      method,
      headers: this.getHeaders(options.headers),
      ...options
    }

    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
      fetchOptions.body = JSON.stringify(data)
    }

    try {
      const response = await fetch(url, fetchOptions)

      // Handle 401 Unauthorized
      if (response.status === 401) {
        this.setToken(null)
        window.dispatchEvent(new CustomEvent('unauthorized'))
        throw new Error('No autorizado')
      }

      // Parsear respuesta
      const contentType = response.headers.get('content-type')
      let responseData = null

      if (contentType && contentType.includes('application/json')) {
        responseData = await response.json()
      } else {
        responseData = await response.text()
      }

      // Check if response is ok
      if (!response.ok) {
        const error = new Error(
          responseData?.detail || 
          responseData?.message || 
          `HTTP Error: ${response.status}`
        )
        error.status = response.status
        error.data = responseData
        throw error
      }

      return responseData

    } catch (error) {
      console.error(`API Error [${method} ${endpoint}]:`, error)
      throw error
    }
  }

  /**
   * GET request
   */
  async get(endpoint, options = {}) {
    return this.request('GET', endpoint, null, options)
  }

  /**
   * POST request
   */
  async post(endpoint, data = null, options = {}) {
    return this.request('POST', endpoint, data, options)
  }

  /**
   * PUT request
   */
  async put(endpoint, data = null, options = {}) {
    return this.request('PUT', endpoint, data, options)
  }

  /**
   * PATCH request
   */
  async patch(endpoint, data = null, options = {}) {
    return this.request('PATCH', endpoint, data, options)
  }

  /**
   * DELETE request
   */
  async delete(endpoint, options = {}) {
    return this.request('DELETE', endpoint, null, options)
  }

  /**
   * Upload file (para CV, imagen, etc)
   * ✅ CORRECCIÓN: Usa X-API-Key header
   */
  async uploadFile(endpoint, file, additionalData = {}) {
    const formData = new FormData()
    formData.append('file', file)
    
    Object.keys(additionalData).forEach(key => {
      formData.append(key, additionalData[key])
    })

    const url = `${this.baseUrl}${endpoint}`
    const headers = {}

    if (this.token) {
      // ✅ Usar X-API-Key header en file uploads también
      headers['X-API-Key'] = this.token
    }

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: formData
      })

      if (response.status === 401) {
        this.setToken(null)
        window.dispatchEvent(new CustomEvent('unauthorized'))
        throw new Error('No autorizado')
      }

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || error.message)
      }

      return await response.json()

    } catch (error) {
      console.error(`File Upload Error [${endpoint}]:`, error)
      throw error
    }
  }

  /**
   * Obtener URL completa de un endpoint
   */
  getUrl(endpoint) {
    return `${this.baseUrl}${endpoint}`
  }

  /**
   * Limpiar token (logout)
   */
  clearToken() {
    this.setToken(null)
  }

  /**
   * Verificar si tiene token válido
   */
  isAuthenticated() {
    return !!this.token
  }
}

// Crear instancia global del cliente
const apiClient = new ApiClient(
  window.API_BASE_URL || 'http://localhost:8000/api/v1'
)

// Event listener para re-autenticación
window.addEventListener('unauthorized', () => {
  console.warn('Sesión expirada, redirigiendo a login')
  window.location.href = '/login'
})
