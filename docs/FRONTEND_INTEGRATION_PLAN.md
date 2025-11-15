# 📱 Plan de Integración Frontend - MVP MoirAI

**Rama**: `feature/frontend-integration-mvp`  
**Fecha**: 15 de noviembre de 2025  
**Objetivo**: Crear versión MVP funcional con integración completa de endpoints

---

## 🎯 Objetivos de la Integración

- ✅ Conectar frontend con backend API
- ✅ Crear sistema de autenticación y tokens
- ✅ Implementar búsqueda de oportunidades laborales
- ✅ Sistema de notificaciones en tiempo real
- ✅ Gestión de perfil de estudiante
- ✅ Dashboard de estadísticas

---

## 📊 Endpoints API Disponibles

### Autenticación
- `POST /api/v1/auth/register` - Registro de usuario
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Obtener usuario actual

### Estudiantes
- `GET /api/v1/students/{student_id}` - Obtener perfil
- `PUT /api/v1/students/{student_id}` - Actualizar perfil
- `POST /api/v1/students/{student_id}/upload-resume` - Upload CV

### Oportunidades/Jobs
- `GET /api/v1/jobs/search` - Buscar empleos
- `GET /api/v1/jobs/{job_id}` - Obtener detalles
- `POST /api/v1/jobs/scrape` - Iniciar scraping

### Matching
- `POST /api/v1/matching/recommendations` - Recomendaciones
- `POST /api/v1/matching/filter-by-criteria` - Filtrar candidatos
- `GET /api/v1/matching/featured-students` - Estudiantes destacados
- `GET /api/v1/matching/student/{id}/matching-score` - Score de compatibilidad

### Empresas
- `GET /api/v1/companies/{company_id}` - Obtener empresa
- `POST /api/v1/companies/search-students` - Buscar estudiantes

---

## 🏗️ Estructura de Carpetas

```
app/frontend/
├── static/
│   ├── js/
│   │   ├── api-client.js          # Cliente HTTP reutilizable
│   │   ├── auth-manager.js        # Gestión de autenticación
│   │   ├── notification-manager.js# Sistema de notificaciones
│   │   ├── pages/
│   │   │   ├── login.js           # Página de login
│   │   │   ├── dashboard.js       # Dashboard de estudiante
│   │   │   ├── jobs-search.js     # Búsqueda de empleos
│   │   │   └── profile.js         # Perfil de usuario
│   │   └── utils.js               # Funciones útiles
│   ├── css/
│   │   ├── styles.css             # Estilos principales
│   │   ├── notifications.css      # Estilos notificaciones
│   │   └── responsive.css         # Responsivo
│   └── images/                    # Imágenes
└── templates/
    ├── index.html                 # Home
    ├── login.html                 # Login
    ├── dashboard.html             # Dashboard
    ├── jobs.html                  # Búsqueda empleos
    ├── profile.html               # Perfil usuario
    └── admin/                      # Sección admin
```

---

## 🔐 Gestión de Autenticación

### Flujo de Login
```
1. Usuario ingresa email + contraseña
2. Frontend POST /auth/login
3. Backend retorna token JWT
4. Frontend almacena en localStorage
5. Todas las requests llevan Authorization header
```

### Token Management
```javascript
// Guardar token
localStorage.setItem('token', response.token)

// Usar en requests
Authorization: Bearer {token}

// Logout
localStorage.removeItem('token')
```

---

## 🔔 Sistema de Notificaciones

### Tipos de Notificaciones
- ✅ Info (azul)
- ⚠️ Warning (amarillo)
- ❌ Error (rojo)
- ✔️ Success (verde)

### Ejemplo de uso
```javascript
notificationManager.show('Empleos encontrados', 'success', 3000)
notificationManager.show('Error al conectar', 'error', 5000)
```

---

## 📝 Componentes a Implementar

### 1. API Client (`api-client.js`)
```javascript
class ApiClient {
  constructor(baseUrl) { }
  
  async request(method, endpoint, data) { }
  async get(endpoint) { }
  async post(endpoint, data) { }
  async put(endpoint, data) { }
  async delete(endpoint) { }
}
```

### 2. Auth Manager (`auth-manager.js`)
```javascript
class AuthManager {
  async login(email, password) { }
  async register(userData) { }
  async logout() { }
  async getCurrentUser() { }
  isAuthenticated() { }
}
```

### 3. Notification Manager (`notification-manager.js`)
```javascript
class NotificationManager {
  show(message, type, duration) { }
  showLoading(message) { }
  hideLoading() { }
}
```

### 4. Jobs Search (`pages/jobs-search.js`)
```javascript
async function searchJobs(query, location) {
  const results = await apiClient.get(
    `/api/v1/jobs/search?keyword=${query}&location=${location}`
  )
  return results
}
```

---

## 🎨 Interfaz de Usuario

### Página de Login
- Email/contraseña
- Link de recuperación
- Link de registro

### Dashboard
- Resumen de aplicaciones
- Empleos recomendados
- Estadísticas personales

### Búsqueda de Empleos
- Filtros: ubicación, salario, modalidad
- Lista de empleos
- Detalles de empleo
- Botón "Aplicar"

### Perfil de Usuario
- Información personal
- Upload de CV
- Habilidades identificadas
- Historial de aplicaciones

---

## 📋 MVP Checklist

### Frontend
- [ ] Crear `api-client.js` con cliente HTTP
- [ ] Crear `auth-manager.js` para autenticación
- [ ] Crear `notification-manager.js` para notificaciones
- [ ] Página de login funcional
- [ ] Dashboard con datos reales
- [ ] Búsqueda de empleos con filtros
- [ ] Upload de CV
- [ ] Perfil de usuario
- [ ] Historial de aplicaciones

### Backend Integration
- [ ] Conectar todos los endpoints
- [ ] Validación de tokens JWT
- [ ] Manejo de errores
- [ ] CORS correctamente configurado

### Testing
- [ ] Test de autenticación
- [ ] Test de búsqueda
- [ ] Test de notificaciones
- [ ] Test responsivo en mobile

### Deployment
- [ ] Build frontend
- [ ] Configuración de production
- [ ] Deployment a servidor

---

## 🚀 Timeline (2 semanas)

### Semana 1
- Día 1-2: API Client + Auth Manager
- Día 3-4: Notification System + Login Page
- Día 5: Dashboard básico

### Semana 2
- Día 1-2: Búsqueda de empleos
- Día 3: Upload de CV
- Día 4: Perfil de usuario
- Día 5: Testing y pulido

---

## 📚 Documentación Necesaria

- API Documentation (Swagger en `/docs`)
- Frontend Setup Guide
- Deployment Guide
- User Guide para estudiantes

---

**Status**: 🎯 LISTO PARA IMPLEMENTACIÓN

Próximo paso: Crear `api-client.js`
