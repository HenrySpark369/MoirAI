# Guía de Seguridad para Despliegue en Producción

## 🔐 CHECKLIST DE SEGURIDAD PARA PRODUCCIÓN

### 1. Variables de Entorno y Secretos
- [ ] Generar SECRET_KEY único y fuerte (mínimo 32 caracteres)
- [ ] Configurar contraseñas de base de datos seguras
- [ ] Usar variables de entorno para todas las credenciales
- [ ] Nunca hardcodear secretos en el código
- [ ] Usar servicios de gestión de secretos (AWS Secrets Manager, HashiCorp Vault)

### 2. Base de Datos
- [ ] Configurar PostgreSQL en lugar de SQLite
- [ ] Habilitar SSL/TLS para conexiones de BD
- [ ] Configurar backup automático
- [ ] Limitar acceso de red a la BD
- [ ] Usar usuarios de BD con privilegios mínimos

### 3. Configuración del Servidor
- [ ] Deshabilitar modo debug/desarrollo
- [ ] Configurar HTTPS con certificados válidos
- [ ] Configurar CORS apropiadamente
- [ ] Implementar rate limiting
- [ ] Configurar logs de seguridad

### 4. Autenticación y Autorización
- [ ] Implementar OAuth2/JWT en lugar de API keys estáticas
- [ ] Configurar expiración de tokens
- [ ] Implementar refresh tokens
- [ ] Habilitar autenticación de dos factores
- [ ] Audit logs de accesos

### 5. Configuración de Red
- [ ] Configurar firewall (solo puertos necesarios)
- [ ] Usar reverse proxy (nginx/Apache)
- [ ] Configurar DDoS protection
- [ ] Implementar WAF (Web Application Firewall)

### 6. Monitoreo y Logging
- [ ] Configurar logs centralizados
- [ ] Monitoreo de recursos del sistema
- [ ] Alertas de seguridad
- [ ] Backup y recovery plan

## 🚀 CONFIGURACIÓN PARA DIFERENTES ENTORNOS

### Desarrollo Local
```bash
# Usar SQLite para simplicidad
DATABASE_URL="sqlite:///./moirai.db"
DEBUG=true
LOG_LEVEL="DEBUG"
```

### Staging
```bash
# PostgreSQL con datos de prueba
DATABASE_URL="postgresql://user:pass@staging-db:5432/moirai_staging"
DEBUG=false
LOG_LEVEL="INFO"
```

### Producción
```bash
# PostgreSQL con alta disponibilidad
DATABASE_URL="postgresql://user:pass@prod-db:5432/moirai_prod"
DEBUG=false
LOG_LEVEL="WARNING"
ENABLE_AUDIT_LOGGING=true
```

## 🛡️ CONFIGURACIONES ESPECÍFICAS DE FASTAPI

### Configuración Segura
```python
# app/core/config.py
class Settings(BaseSettings):
    # Seguridad
    SECRET_KEY: str = Field(..., min_length=32)
    DEBUG: bool = False
    ALLOWED_HOSTS: List[str] = ["your-domain.com"]
    
    # HTTPS
    FORCE_HTTPS: bool = True
    SECURE_COOKIES: bool = True
    
    # Headers de seguridad
    SECURITY_HEADERS: bool = True
```

### Middleware de Seguridad
```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["your-domain.com", "*.your-domain.com"]
)
```

## 📊 MÉTRICAS Y MONITOREO

### Health Checks
- Endpoint `/health` para verificar estado
- Verificación de conectividad de BD
- Verificación de servicios externos

### Logs de Auditoría
- Accesos a la API
- Cambios en datos sensibles
- Intentos de autenticación fallidos
- Operaciones administrativas

## 🔧 HERRAMIENTAS RECOMENDADAS

### Desarrollo
- `bandit` - Análisis de seguridad de código Python
- `safety` - Verificación de vulnerabilidades en dependencias
- `semgrep` - Análisis estático de código

### Producción
- `fail2ban` - Protección contra ataques de fuerza bruta
- `certbot` - Gestión automática de certificados SSL
- `prometheus` + `grafana` - Monitoreo y métricas
- `elk stack` - Logs centralizados
