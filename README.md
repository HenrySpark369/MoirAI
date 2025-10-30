# MoirAI — instrucciones de desarrollo y tests

Pequeñas instrucciones para ejecutar los tests y trabajar localmente con el paquete `app`.

Requisitos (macOS): Python 3.9+ y pip. Se recomienda crear un virtualenv.

Instalación rápida (editable):

```zsh
# crear entorno (opcional)
python -m venv .venv
source .venv/bin/activate

# instalar dependencias listadas en requirements.txt
pip install -r requirements.txt

# instalar el paquete en modo editable para que `app` sea importable
pip install -e .
```

Ejecutar tests:

```zsh
# si instalaste el paquete: pytest
pytest -q

# alternativa si no instalaste el paquete (usa PYTHONPATH):
PYTHONPATH=. pytest -q
```

Notas:
- `pyproject.toml` y `setup.cfg` permiten instalar localmente con `pip install -e .`.
- Añade `scikit-learn` y `numpy` en `requirements.txt` para obtener TF-IDF real si lo deseas (ya están incluidos en este repositorio).
# MoirAI - Plataforma de Matching Laboral UNRC

**API RESTful inteligente para conectar estudiantes de la Universidad Nacional Rosario Castellanos con oportunidades laborales mediante análisis NLP y algoritmos de matchmaking.**

## 🎯 Descripción

MoirAI es una plataforma innovadora que utiliza técnicas de procesamiento de lenguaje natural (NLP) y algoritmos de machine learning para:

- **Analizar currículums automáticamente** y extraer habilidades técnicas, blandas y proyectos
- **Scraping inteligente de empleos** desde portales como OCC.com.mx con alertas personalizadas
- **Seguimiento completo de aplicaciones** laborales con estados y estadísticas de éxito
- **Generar recomendaciones personalizadas** de trabajos para estudiantes
- **Facilitar búsqueda avanzada** de candidatos para empresas colaboradoras
- **Sistema de alertas automáticas** para nuevas oportunidades laborales
- **Proporcionar métricas y KPIs** para administradores universitarios
- **Garantizar cumplimiento** de normativas de protección de datos (LFPDPPP)

## 🏗️ Arquitectura

### Stack Tecnológico

- **Backend**: FastAPI + Python 3.11 (recomendado). Compatible con Python 3.9–3.11
- **Base de datos**: SQLModel + PostgreSQL/SQLite
- **NLP**: spaCy + scikit-learn + RapidFuzz
- **Web Scraping**: BeautifulSoup4 + lxml + httpx (async)
- **Autenticación**: OAuth 2.0 / JWT (demo con API keys)
- **Proveedores externos**: OCC.com.mx Scraper, JSearch API, LinkedIn API (futuro)
- **Documentación**: OpenAPI/Swagger automático

### Estructura del Proyecto

```
MoirAI/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicación principal FastAPI
│   ├── core/
│   │   ├── config.py          # Configuración y settings
│   │   └── database.py        # Conexión a base de datos
│   ├── models/
│   │   ├── __init__.py        # Modelos SQLModel (Student, Company, etc.)
│   │   ├── user.py            # Modelo de usuario básico
│   │   └── job_scraping.py    # Modelos para sistema de scraping
│   ├── schemas/
│   │   └── __init__.py        # Esquemas Pydantic para validación
│   ├── api/
│   │   └── endpoints/
│   │       ├── students.py    # Endpoints de estudiantes
│   │       ├── job_scraping.py # ✅ Endpoints de scraping OCC.com.mx
│   │       ├── auth.py        # ✅ Endpoints de autenticación
│   │       ├── jobs.py        # Endpoints de trabajos (futuro)
│   │       ├── companies.py   # Endpoints de empresas (futuro)
│   │       └── admin.py       # Endpoints de administración (futuro)
│   ├── services/
│   │   ├── nlp_service.py     # Servicio de análisis NLP
│   │   ├── matching_service.py # Algoritmos de matchmaking
│   │   ├── occ_scraper_service.py # ✅ Servicio de scraping OCC.com.mx
│   │   ├── job_application_service.py # ✅ Gestión de aplicaciones
│   │   └── api_key_service.py # ✅ Gestión de API keys
│   ├── providers/
│   │   └── __init__.py        # Proveedores de trabajos externos
│   ├── middleware/
│   │   └── auth.py            # Autenticación y autorización
│   └── utils/
│       └── file_processing.py # Procesamiento de archivos
├── tests/
│   ├── unit/                  # Tests unitarios
│   └── integration/           # Tests de integración
├── docs/                      # Documentación adicional
├── requirements.txt           # Dependencias de producción
├── .env.example              # Configuración de ejemplo
└── README.md                 # Este archivo
```

## 🚀 Instalación y Configuración

### ⚠️ IMPORTANTE: Entorno Virtual

**Antes de ejecutar cualquier comando de Python, active el entorno virtual:**
```bash
source .venv/bin/activate  # Linux/macOS
# o
.venv\Scripts\activate     # Windows
```

### Prerrequisitos

- **Python 3.11** (recomendado) - Compatible con Python 3.9–3.11
- PostgreSQL (opcional, se puede usar SQLite para desarrollo)
- Git
- Xcode Command Line Tools (macOS) o build-essential (Linux)

### Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/HenrySpark369/MoirAI.git
cd MoirAI
```

2. **Verificar e instalar Python 3.11**
```bash
# Verificar si Python 3.11 está instalado
python3.11 --version

# Si el comando anterior falla, instalar Python 3.11:

# En macOS con Homebrew
brew install python@3.11

# En macOS con pyenv (alternativa recomendada)
brew install pyenv
pyenv install 3.11.6
pyenv local 3.11.6

# En Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# En CentOS/RHEL/Fedora
sudo dnf install python3.11 python3.11-devel

# Verificar instalación exitosa
python3.11 --version
```

3. **Crear entorno virtual con Python 3.11**
```bash
# Usar Python 3.11 específicamente
python3.11 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Verificar que el entorno virtual usa Python 3.11
python --version  # Debe mostrar Python 3.11.x
```

3. **Instalar dependencias**
```bash
# ⚠️ IMPORTANTE: Asegúrate de tener el entorno virtual activado
source .venv/bin/activate

# Actualizar pip para evitar problemas de compatibilidad
pip install --upgrade pip setuptools wheel

# Instalar dependencias del proyecto (incluye scraping, NLP, validación, bases de datos)
pip install -r requirements.txt

# Descargar modelos pre-entrenados de spaCy para NLP
# Español (recomendado para análisis de currículums en español)
python -m spacy download es_core_news_sm

# Inglés (recomendado para términos técnicos)
python -m spacy download en_core_web_sm
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con sus configuraciones específicas

# IMPORTANTE: Generar SECRET_KEY segura
# Método 1: Usando Python
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Método 2: Usando OpenSSL
openssl rand -base64 32

# Método 3: Usando el script incluido
./setup_secure.sh
```

**⚠️ IMPORTANTE**: Nunca use la SECRET_KEY del archivo `.env.example` en producción.

5. **Inicializar base de datos**
```bash
# La base de datos se crea automáticamente al iniciar la aplicación

# Para inicializar el sistema de scraping de empleos (opcional):
python migrate_job_scraping.py

# Con datos de ejemplo para testing:
python migrate_job_scraping.py --sample-data
```

### 🔐 Configuración de Seguridad

**Para un setup completamente automatizado y seguro:**
```bash
# Ejecutar script de configuración segura
./setup_secure.sh

# Esto generará automáticamente:
# - SECRET_KEY segura (32 bytes)
# - Contraseñas para Docker
# - Archivos .env y .env.docker configurados
```

**Para configuración manual:**
```bash
# ⚠️ IMPORTANTE: Activar entorno virtual primero
source .venv/bin/activate

# 1. Generar SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 2. Copiar resultado al archivo .env
echo 'SECRET_KEY="TU_CLAVE_GENERADA_AQUI"' >> .env

# 3. Configurar otras variables según necesidad
```

**⚠️ IMPORTANTE**: 
- Nunca use las claves del archivo `.env.example` en producción
- Cada instalación debe tener su propia SECRET_KEY única
- Mantenga las claves seguras y no las comparta

### Ejecución

```bash
# Desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Producción
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

La API estará disponible en:
- **Docs interactivos**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

## 📋 Casos de Uso del MVP

### 1. Estudiante UNRC
- ✅ **Subir currículum** y obtener análisis automático de habilidades
- ✅ **Gestionar perfil** académico y profesional completo
- ✅ **Crear perfil manual** sin necesidad de currículum digital
- ✅ **Actualizar habilidades** manualmente según experiencia
- ✅ **Acceder a perfil público** para empresas interesadas
- ✅ **Buscar empleos en OCC.com.mx** con filtros avanzados
- ✅ **Registrar aplicaciones** y seguir estados (aplicado, entrevista, etc.)
- ✅ **Configurar alertas automáticas** para nuevos empleos relevantes
- ✅ **Ver estadísticas personales** de aplicaciones y tasa de éxito
- 🔄 **Recibir recomendaciones** personalizadas de trabajos
- 🔄 **Recibir notificaciones** de oportunidades relevantes

### 2. Empresa Colaboradora
- ✅ **Buscar candidatos** por habilidades y proyectos específicos
- ✅ **Acceder a perfiles públicos** de estudiantes
- ✅ **Filtrar por criterios avanzados** (programa, habilidades, proyectos)
- ✅ **Ver empleos trending** y estadísticas del mercado
- 🔄 **Publicar vacantes** con requisitos detallados
- 🔄 **Acceder a candidatos destacados** con alta compatibilidad
- 🔄 **Utilizar filtros avanzados** para encontrar perfiles ideales

### 3. Administrador UNRC
- ✅ **Visualizar estadísticas** de estudiantes y programas académicos
- ✅ **Gestionar roles y permisos** de usuarios con auditoría completa
- ✅ **Crear y administrar** perfiles de estudiantes
- ✅ **Re-analizar currículums** con modelos NLP actualizados
- ✅ **Operaciones en lote** para procesamiento masivo
- ✅ **Monitorear cumplimiento** de normativas de privacidad
- ✅ **Acceder a logs de auditoría** completos
- ✅ **Procesar alertas de empleo** automáticamente para todos los usuarios
- ✅ **Monitorear sistema de scraping** con logs y métricas
- 🔄 **Visualizar KPIs** de empleabilidad y matching
- 🔄 **Analizar métricas** de inserción laboral

**Leyenda**: ✅ Implementado | 🔄 En desarrollo | ⏳ Planificado

## 🔧 API Endpoints Principales

### Estudiantes ✅ COMPLETAMENTE IMPLEMENTADO
```
# Crear estudiantes
POST   /api/v1/students/                    # Crear estudiante manualmente
POST   /api/v1/students/upload_resume       # Subir y analizar currículum

# Leer estudiantes
GET    /api/v1/students/                    # Listar con filtros y paginación
GET    /api/v1/students/stats               # Estadísticas de estudiantes  
GET    /api/v1/students/{id}                # Obtener perfil completo
GET    /api/v1/students/email/{email}       # Buscar por email (admin)
GET    /api/v1/students/{id}/public         # Perfil público sin autenticación
GET    /api/v1/students/search/skills       # Buscar por habilidades específicas

# Actualizar estudiantes
PUT    /api/v1/students/{id}                # Actualizar datos básicos
PATCH  /api/v1/students/{id}/skills         # Actualizar habilidades manualmente
PATCH  /api/v1/students/{id}/activate       # Reactivar estudiante
POST   /api/v1/students/{id}/update-activity # Actualizar última actividad

# Eliminar estudiantes
DELETE /api/v1/students/{id}                # Eliminación suave o permanente

# Operaciones especiales
POST   /api/v1/students/{id}/reanalyze      # Re-analizar currículum con NLP
POST   /api/v1/students/bulk-reanalyze      # Re-análisis en lote
```

### Scraping de Empleos OCC.com.mx ✅ COMPLETAMENTE IMPLEMENTADO
```
# Búsqueda y gestión de empleos
POST   /job-scraping/search              # Buscar empleos con filtros avanzados
GET    /job-scraping/job/{job_id}        # Detalles de empleo específico
GET    /job-scraping/trending-jobs       # Empleos en tendencia
GET    /job-scraping/search-history      # Historial de búsquedas del usuario

# Gestión de aplicaciones
POST   /job-scraping/apply               # Registrar aplicación a empleo
PUT    /job-scraping/application/{id}/status # Actualizar estado de aplicación
GET    /job-scraping/applications        # Listar aplicaciones del usuario
GET    /job-scraping/applications/stats  # Estadísticas de aplicaciones

# Sistema de alertas
POST   /job-scraping/alerts              # Crear alerta personalizada
GET    /job-scraping/alerts              # Listar alertas del usuario
DELETE /job-scraping/alerts/{id}         # Eliminar alerta

# Administración
POST   /job-scraping/admin/process-alerts # Procesar todas las alertas (admin)
```

### Trabajos (próximamente)
```
GET    /api/v1/jobs/search               # Buscar trabajos
POST   /api/v1/jobs                      # Publicar vacante (empresas)
GET    /api/v1/jobs/{id}                 # Detalles de trabajo específico
```

### Empresas (próximamente)
```
GET    /api/v1/companies/filter_students # Filtrar estudiantes por criterios
GET    /api/v1/companies/featured_candidates # Candidatos destacados
POST   /api/v1/companies                 # Registrar empresa
```

### Administración (próximamente)
```
GET    /api/v1/admin/kpis               # Métricas y KPIs del sistema
GET    /api/v1/admin/audit_logs         # Logs de auditoría
GET    /api/v1/admin/users              # Gestión de usuarios
```

## 🤖 Características de NLP y Web Scraping

### Extracción Automática de Currículums
- **Habilidades técnicas**: Python, SQL, React, Machine Learning, etc.
- **Habilidades blandas**: Liderazgo, comunicación, trabajo en equipo, etc.
- **Proyectos**: Descripciones y tecnologías utilizadas
- **Experiencia**: Análisis de roles y responsabilidades

### Sistema de Scraping OCC.com.mx ✅
- **Búsqueda automatizada** con filtros por ubicación, salario, modalidad
- **Extracción estructurada** de ofertas de trabajo con NLP
- **Rate limiting inteligente** para evitar bloqueos
- **Headers anti-detección** y manejo de errores robusto
- **Seguimiento de aplicaciones** con estados y notas
- **Sistema de alertas** personalizadas con notificaciones automáticas
- **Analytics y trending** de empleos más buscados

### Algoritmos de Matching
- **Puntuación de compatibilidad** entre perfil y vacante
- **Factores de boost** por ubicación, actividad reciente, etc.
- **Ranking inteligente** de candidatos y oportunidades
- **Filtrado avanzado** con múltiples criterios

## 🔒 Seguridad y Privacidad

### Configuración Inicial Segura

**🚨 ANTES DE USAR EN PRODUCCIÓN:**

1. **Generar SECRET_KEY única:**
```bash
# ⚠️ Activar entorno virtual primero
source .venv/bin/activate

# Método recomendado
python -c "import secrets; print('SECRET_KEY=\"' + secrets.token_urlsafe(32) + '\"')"

# Alternativa con OpenSSL (sin entorno virtual)
openssl rand -base64 32
```

2. **Usar script de configuración segura:**
```bash
# Configura automáticamente todas las claves
./setup_secure.sh
```

3. **Verificar configuración antes de deploy:**
```bash
# Ejecutar verificación de seguridad
./security_check.sh
```

### Cumplimiento Normativo
- ✅ **LFPDPPP**: Ley Federal de Protección de Datos Personales
- ✅ **ISO/IEC 27001**: Gestión de Seguridad de la Información
- ✅ **Privacy by Design**: Privacidad desde el diseño
- ✅ **Auditoría completa**: Logging de todas las actividades

### Medidas de Seguridad Implementadas
- ✅ **Autenticación robusta** con API keys (OAuth 2.0/JWT en producción)
- ✅ **Autorización por roles** (estudiante, empresa, admin, anónimo)
- ✅ **Control de acceso granular** por endpoint y recurso
- ✅ **Logs de auditoría** para todas las operaciones sensibles
- ✅ **Soft delete por defecto** para protección de datos
- ✅ **Validación de entrada** y sanitización de datos
- ✅ **Verificación de permisos** en cada operación
- 🔒 **Cifrado en tránsito** (TLS 1.3 en producción)
- ⏰ **Retención de datos** configurable con anonimización automática

### Sistema de Auditoría
- ✅ **Actor tracking**: Quién realizó cada acción
- ✅ **Timestamp precisos**: Cuándo ocurrió cada evento
- ✅ **Detalles completos**: Qué se modificó y valores anteriores
- ✅ **Registro de errores**: Fallos y intentos no autorizados
- ✅ **IP tracking**: Dirección IP de cada solicitud

## 🧪 Testing

```bash
# Activar entorno virtual
source .venv/bin/activate

# Ejecutar tests unitarios
pytest tests/unit/

# Ejecutar tests de integración
pytest tests/integration/

# Tests con cobertura
pytest --cov=app tests/

# Tests específicos de endpoints de estudiantes
pytest tests/unit/test_students_endpoints.py -v

# Tests específicos de NLP
pytest tests/unit/test_nlp_service.py -v

# Tests de autenticación y autorización
pytest tests/unit/test_auth_middleware.py -v
```

### Tests de API en vivo

```bash
# Verificar que la API esté funcionando
curl -X GET "http://localhost:8000/health"

# Probar endpoint de estudiantes (requiere API key)
curl -H "X-API-Key: YOUR_ADMIN_KEY" "http://localhost:8000/api/v1/students/stats"

# Verificar documentación interactiva
open http://localhost:8000/docs
```

## 📈 Monitoreo y Métricas

### KPIs Implementados ✅
- ✅ **Estudiantes registrados** y activos por programa
- ✅ **Registros recientes** en los últimos 30 días
- ✅ **Distribución por programas** académicos
- ✅ **Estados de activación** (activos vs inactivos)
- 🔄 **Empresas colaboradoras** verificadas
- 🔄 **Matches generados** en período
- 🔄 **Tasa de colocación** laboral
- 🔄 **Tiempo promedio** de respuesta de la API

### Logging y Auditoría ✅
- ✅ **Acceso a la API** con detalles de usuario y rol
- ✅ **Operaciones CRUD** en datos sensibles con valores anteriores
- ✅ **Autenticación y autorización** con tracking de IPs
- ✅ **Errores y excepciones** con contexto completo
- ✅ **Operaciones masivas** (bulk operations) con contadores
- ✅ **Búsquedas y filtros** con criterios utilizados
- 🔄 **Métricas de rendimiento** de algoritmos NLP

### Dashboard de Estadísticas
El endpoint `/api/v1/students/stats` proporciona:
```json
{
  "total_students": 150,
  "active_students": 142,
  "inactive_students": 8,
  "students_by_program": {
    "Ingeniería en Sistemas": 45,
    "Ingeniería Industrial": 32,
    "Ingeniería Civil": 28,
    "Licenciatura en Informática": 37
  },
  "recent_registrations_30d": 12,
  "generated_at": "2025-10-15T10:30:00Z"
}
```

## 🔮 Roadmap

### Fase 1 - MVP (Octubre 2025) ✅ COMPLETADO
- ✅ **CRUD completo de estudiantes** con 15 endpoints
- ✅ **Análisis automático de currículums** con NLP
- ✅ **Sistema de autenticación** y autorización por roles
- ✅ **Auditoría completa** de todas las operaciones
- ✅ **Búsqueda avanzada** por habilidades y criterios
- ✅ **Estadísticas y métricas** en tiempo real
- ✅ **Operaciones administrativas** (bulk, reactivación, etc.)
- ✅ **Sistema completo de scraping OCC.com.mx** con 12 endpoints
- ✅ **Seguimiento de aplicaciones** laborales con estados
- ✅ **Sistema de alertas personalizadas** con notificaciones automáticas
- ✅ **Analytics de empleos** y estadísticas de éxito

### Fase 2 - Expansión (Noviembre 2025)
- 🔄 **API de empresas** completa con gestión de vacantes
- 🔄 **Sistema de matching** inteligente estudiante-trabajo
- 🔄 **Recomendaciones personalizadas** para estudiantes
- 🔄 **Notificaciones push/email** en tiempo real
- 🔄 **Panel web** para administradores
- 🔄 **Integración con proveedores** externos (JSearch, LinkedIn)

### Fase 3 - Integración (Diciembre 2025)
- ⏳ **Integración con sistemas UNRC** existentes
- ⏳ **Dashboard empresarial** avanzado
- ⏳ **App móvil** para estudiantes
- ⏳ **Algoritmos ML** avanzados para predicciones
- ⏳ **API de métricas** y reportes automáticos

### Fase 4 - Optimización (2026)
- ⏳ **Análisis predictivo** de empleabilidad
- ⏳ **Machine Learning** para mejora continua
- ⏳ **Integración con redes sociales** profesionales
- ⏳ **Sistema de recomendaciones** bidireccional

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para su feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit sus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

### Estándares de Código
- **Formato**: Black para Python
- **Imports**: isort para organización
- **Linting**: flake8 para análisis estático
- **Tipos**: mypy para type checking
- **Tests**: pytest con coverage > 80%

## ❓ Preguntas Frecuentes (FAQ)

### Configuración y Seguridad

**P: ¿Cómo genero una SECRET_KEY segura?**
```bash
# ⚠️ IMPORTANTE: Activar entorno virtual primero
source .venv/bin/activate

# Método más seguro (recomendado)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Con OpenSSL (sin entorno virtual)
openssl rand -base64 32

# Script automatizado (maneja entorno virtual automáticamente)
./setup_secure.sh
```

**P: ¿Puedo usar la SECRET_KEY del archivo .env.example?**
❌ **NO.** Nunca use valores de ejemplo en producción. Cada instalación debe tener una clave única.

**P: ¿Qué pasa si pierdo mi SECRET_KEY?**
⚠️ Si cambia la SECRET_KEY, todas las sesiones activas se invalidarán. Guarde su clave de forma segura.

**P: ¿Con qué frecuencia debo cambiar la SECRET_KEY?**
🔄 Se recomienda rotarla anualmente o si se sospecha compromiso de seguridad.

### Desarrollo y Uso

**P: ¿Cómo empiezo a usar la API?**
1. Ejecute `./setup_secure.sh` para configuración inicial segura
2. Ejecute `pip install -r requirements.txt` para instalar todas las dependencias (incluye scraping, NLP y validación)
3. Descargue los modelos de spaCy: `python -m spacy download es_core_news_sm`
4. Configure la base de datos de scraping: `python migrate_job_scraping.py`
5. Inicie con `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
6. Vaya a `http://localhost:8000/docs` para documentación interactiva Swagger

**P: ¿Necesito instalar dependencias adicionales después de pip install -r requirements.txt?**
❌ **NO.** El archivo `requirements.txt` incluye TODAS las dependencias necesarias:
- ✅ Scraping: BeautifulSoup4, lxml, httpx
- ✅ NLP: spaCy, scikit-learn, pandas, numpy
- ✅ Validación: pydantic, email-validator
- ✅ Base de datos: sqlmodel, psycopg2, alembic

Solo necesita descargar los **modelos pre-entrenados de spaCy** por separado (ver paso 3 arriba).

**P: ¿Cómo funciona el sistema de scraping de empleos?**
El sistema permite buscar empleos en OCC.com.mx, registrar aplicaciones y configurar alertas automáticas. Incluye:
- Rate limiting inteligente para evitar bloqueos
- Headers anti-detección
- Manejo robusto de errores
- Seguimiento completo de aplicaciones con estados

**P: ¿Cómo obtengo una API key?**
- Para desarrollo: Use las claves en su archivo `.env`
- Para producción: Implemente sistema OAuth2/JWT según su infraestructura

**P: ¿La API funciona sin base de datos externa?**
✅ Sí, usa SQLite por defecto. Para producción recomendamos PostgreSQL.

## 📞 Soporte

- **Documentación**: Consulte este README o el archivo `/docs/` para información detallada
- **Issues y Bugs**: Reporte problemas en https://github.com/HenrySpark369/MoirAI/issues
- **Discusiones**: Participe en las discusiones del repositorio

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia Apache 2.0 - vea el archivo [LICENSE](LICENSE) para detalles.

## 🙏 Agradecimientos

- **Universidad Nacional Rosario Castellanos** - Por la iniciativa de conectar estudiantes con oportunidades laborales - Lic. en Ciencia de Datos para Negocios MAC-801
- **Comunidad open source** de FastAPI, spaCy, SQLAlchemy y scikit-learn
- **Todos los contribuyentes** que ayudan a mejorar la plataforma

---

**Desarrollado con ❤️ para la comunidad UNRC**

## Documentación de Diseño

### Arquitectura

La aplicación sigue una arquitectura limpia y modular, diseñada para ser escalable y fácil de mantener.

- **API Layer (FastAPI)**: Expone los endpoints de la API RESTful. Se encarga de la validación de solicitudes, serialización de respuestas y enrutamiento.
- **Lógica de Negocio**: Contiene la lógica central de la aplicación.
- **Capa de Acceso a Datos (asyncpg)**: Gestiona la comunicación con la base de datos PostgreSQL. El uso de `asyncpg` permite interacciones no bloqueantes con la base de datos.

### Esquema de la Base de Datos

*(Esta sección se llenará a medida que se defina el esquema)*

Aquí se describirán las tablas, relaciones y restricciones de la base de datos PostgreSQL.

## Documentación Técnica

### Stack Tecnológico

- **Framework de Backend**: [FastAPI](https://fastapi.tiangolo.com/)
- **Servidor ASGI**: [Uvicorn](https://www.uvicorn.org/)
- **Validación de Datos**: [Pydantic](https://pydantic-docs.helpmanual.io/)
- **Driver de Base de Datos**: [asyncpg](https://magicstack.github.io/asyncpg/current/)
- **Lenguaje**: Python 3.9+

### Endpoints de la API

#### Estudiantes (15 endpoints implementados)

| Método | Ruta | Descripción | Autenticación |
|--------|------|-------------|---------------|
| POST | `/api/v1/students/` | Crear estudiante manualmente | Student/Admin |
| POST | `/api/v1/students/upload_resume` | Subir y analizar currículum | Student/Admin |
| GET | `/api/v1/students/` | Listar con filtros y paginación | Student/Admin/Company |
| GET | `/api/v1/students/stats` | Estadísticas de estudiantes | Admin |
| GET | `/api/v1/students/{id}` | Obtener perfil completo | Student/Admin/Company |
| GET | `/api/v1/students/email/{email}` | Buscar por email | Admin |
| GET | `/api/v1/students/{id}/public` | Perfil público | Ninguna |
| GET | `/api/v1/students/search/skills` | Buscar por habilidades | Student/Admin/Company |
| PUT | `/api/v1/students/{id}` | Actualizar datos básicos | Student/Admin |
| PATCH | `/api/v1/students/{id}/skills` | Actualizar habilidades | Student/Admin |
| PATCH | `/api/v1/students/{id}/activate` | Reactivar estudiante | Admin |
| POST | `/api/v1/students/{id}/update-activity` | Actualizar actividad | Student/Admin |
| DELETE | `/api/v1/students/{id}` | Eliminar (soft/permanente) | Student/Admin |
| POST | `/api/v1/students/{id}/reanalyze` | Re-analizar currículum | Student/Admin |
| POST | `/api/v1/students/bulk-reanalyze` | Re-análisis en lote | Admin |

#### Próximos endpoints
- **Trabajos**: Búsqueda, publicación y gestión de vacantes
- **Empresas**: Registro, gestión de perfiles y búsqueda de candidatos
- **Administración**: KPIs, logs de auditoría y gestión de usuarios

### Configuración e Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone <URL-DEL-REPOSITORIO>
    cd MoirAI
    ```

2.  **Crear un entorno virtual:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar variables de entorno:**
    Crea un archivo `.env` y añade las configuraciones necesarias (ej. credenciales de la base de datos).
    ```
    DATABASE_URL="postgresql://user:password@host:port/database"
    ```

### Cómo ejecutar el proyecto

Para iniciar el servidor de desarrollo localmente:

```bash
# Activar entorno virtual
source .venv/bin/activate

# Iniciar servidor de desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Para producción:

```bash
# Con múltiples workers
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

El servidor estará disponible en:
- **API Base**: `http://localhost:8000/api/v1/`
- **Documentación interactiva**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health check**: `http://localhost:8000/health`

### Estado Actual del Desarrollo

✅ **COMPLETADO (Octubre 2025)**
- CRUD completo de estudiantes (15 endpoints)
- Análisis NLP de currículums
- Sistema de autenticación por API keys
- Auditoría completa de operaciones
- Búsqueda avanzada por habilidades
- Estadísticas y métricas en tiempo real
- Operaciones administrativas avanzadas

## 📚 Documentación Completa

### Autenticación

La API utiliza autenticación basada en API keys mediante el header `X-API-Key`:

```bash
# Ejemplo con curl
curl -H "X-API-Key: YOUR_API_KEY" "http://localhost:8000/api/v1/students/"
```

**Tipos de API Keys y Permisos por Rol:**
- **Admin**: Acceso completo a todos los endpoints y funcionalidades
- **Student**: Acceso a endpoints de estudiantes (consulta y modificación del propio perfil)
- **Company**: Acceso a búsqueda de estudiantes y gestión de perfiles públicos
- **Anonymous**: Acceso limitado a endpoints públicos (consulta de perfiles públicos sin autenticación)

### 🔑 Gestión de API Keys

#### Crear una nueva API Key
```bash
curl -X POST "http://localhost:8000/api/v1/auth/api-keys" \
  -H "X-API-Key: YOUR_CURRENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Clave para aplicación móvil",
    "description": "API key para la app móvil del estudiante",
    "expires_days": 90,
    "rate_limit": 500
  }'
```

#### Listar mis API Keys
```bash
curl -X GET "http://localhost:8000/api/v1/auth/api-keys" \
  -H "X-API-Key: YOUR_API_KEY"
```

#### Revocar una API Key
```bash
curl -X DELETE "http://localhost:8000/api/v1/auth/api-keys/{key_id}" \
  -H "X-API-Key: YOUR_API_KEY"
```

#### Ver mi información y permisos
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "X-API-Key: YOUR_API_KEY"
```

**Respuesta esperada:**
```json
{
  "user_id": 123,
  "name": "María García",
  "email": "maria.garcia@estudiantes.unrc.edu.mx",
  "role": "student",
  "api_key": "stu_p6iaDFfLV_dNswLfYN_cyA_vDA_7mo2kL-ngCQm6XmXHrVKpF7Q6tv_fGdcgI1P-XQ",
  "key_id": "p6iaDFfLV_dNswLfYN_cyA",
  "expires_at": "2026-10-15T10:30:00Z",
  "scopes": ["read:own_profile", "write:own_profile", "read:jobs"]
}
```

### Configuración Técnica (Sección Técnica)

Para desarrolladores que necesiten entender la arquitectura en profundidad, consulte la sección **"Documentación Técnica"** que se encuentra más adelante en este documento.

### Ejemplos de Uso Prácticos

#### 1. Crear un estudiante manualmente

```bash
curl -X POST "http://localhost:8000/api/v1/students/" \
  -H "X-API-Key: ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan Pérez",
    "email": "juan.perez@estudiantes.unrc.edu.mx",
    "program": "Ingeniería en Sistemas",
    "consent_data_processing": true
  }'
```

#### 2. Subir y analizar currículum

```bash
curl -X POST "http://localhost:8000/api/v1/students/upload_resume" \
  -H "X-API-Key: STUDENT_KEY" \
  -F 'meta={"name":"María García","email":"maria.garcia@estudiantes.unrc.edu.mx","program":"Licenciatura en Informática"}' \
  -F 'file=@curriculum.pdf'
```

#### 3. Buscar estudiantes por habilidades

```bash
curl -X GET "http://localhost:8000/api/v1/students/search/skills?skills=Python&skills=Machine%20Learning&min_matches=1&limit=10" \
  -H "X-API-Key: COMPANY_KEY"
```

#### 4. Obtener estadísticas (solo admin)

```bash
curl -X GET "http://localhost:8000/api/v1/students/stats" \
  -H "X-API-Key: ADMIN_KEY"
```

#### 5. Actualizar habilidades de un estudiante

```bash
curl -X PATCH "http://localhost:8000/api/v1/students/123/skills" \
  -H "X-API-Key: ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skills": ["Python", "FastAPI", "PostgreSQL", "Machine Learning"],
    "soft_skills": ["Trabajo en equipo", "Liderazgo", "Comunicación"],
    "projects": ["Sistema de gestión estudiantil", "App móvil de delivery"]
  }'
```

#### 6. Buscar empleos en OCC.com.mx

```bash
curl -X POST "http://localhost:8000/job-scraping/search" \
  -H "X-API-Key: STUDENT_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "Python Developer",
    "location": "Córdoba",
    "salary_min": 80000,
    "work_mode": "remoto",
    "job_type": "tiempo-completo",
    "experience_level": "semi-senior",
    "sort_by": "date",
    "page": 1
  }'
```

**Parámetros de búsqueda de empleos:**

| Parámetro | Tipo | Requerido | Valores | Descripción |
|-----------|------|-----------|---------|-------------|
| `keyword` | string | ✅ Sí | Cualquier texto | Palabra clave de búsqueda (ej: "Python", "Developer", etc.) |
| `location` | string | ❌ No | Ciudad/región | Ubicación geográfica para filtrar empleos |
| `salary_min` | integer | ❌ No | Número | Salario mínimo esperado en pesos |
| `work_mode` | string | ❌ No | `presencial`, `remoto`, `hibrido` | Modalidad de trabajo |
| `job_type` | string | ❌ No | `tiempo-completo`, `medio-tiempo`, `freelance` | Tipo de contrato/jornada |
| `experience_level` | string | ❌ No | `junior`, `semi-senior`, `senior` | Nivel de experiencia requerida |
| `sort_by` | string | ❌ No | `relevance`, `date`, `salary` | Ordenamiento de resultados (defecto: `relevance`) |
| `page` | integer | ❌ No | Número ≥ 1 | Número de página (defecto: 1) |

### Respuestas de la API

**Estructura estándar de respuesta exitosa:**
```json
{
  "id": 123,
  "name": "Juan Pérez",
  "email": "juan.perez@estudiantes.unrc.edu.mx",
  "program": "Ingeniería en Sistemas",
  "skills": ["Python", "JavaScript", "SQL"],
  "soft_skills": ["Trabajo en equipo", "Liderazgo"],
  "projects": ["Sistema web", "App móvil"],
  "created_at": "2025-10-15T10:30:00Z",
  "last_active": "2025-10-15T14:20:00Z",
  "is_active": true
}
```

**Estructura de respuesta de error:**
```json
{
  "detail": "Descripción del error",
  "status_code": 400
}
```

### Paginación y Filtros

Los endpoints de listado soportan paginación y filtros:

```bash
# Listar estudiantes con paginación y filtros
curl -X GET "http://localhost:8000/api/v1/students/?skip=0&limit=20&program=Ingeniería&search=juan&active_only=true" \
  -H "X-API-Key: ADMIN_KEY"
```

**Parámetros disponibles:**
- `skip`: Número de registros a omitir (default: 0)
- `limit`: Número máximo de registros (default: 20, max: 100)
- `program`: Filtrar por programa académico
- `search`: Buscar en nombre o email
- `active_only`: Solo estudiantes activos (default: true)

## Contribuciones

Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

1.  Haz un fork del repositorio.
2.  Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3.  Realiza tus cambios y haz commit (`git commit -am 'Añade nueva funcionalidad'`).
4.  Haz push a la rama (`git push origin feature/nueva-funcionalidad`).
5.  Crea un nuevo Pull Request.

## Licencia

Este proyecto está bajo la Licencia Apache 2.0. Consulta el archivo `LICENSE` para más detalles.
