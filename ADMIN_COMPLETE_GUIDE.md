# 🔐 Guía Completa de Administrador MoirAI

> **Documento Master**: Consolida Quick Start + Setup Guide + Security Architecture
> 
> Última actualización: 17 de noviembre de 2025

---

## 📑 Tabla de Contenidos

1. [⚡ Quick Start](#quick-start) - Empieza aquí (5 min)
2. [🏗️ Arquitectura de Seguridad](#arquitectura-de-seguridad) - Cómo funciona internamente
3. [🚀 Configuración Completa](#configuración-completa) - Guía paso a paso
4. [🔒 Mejores Prácticas](#mejores-prácticas) - Seguridad en desarrollo y producción
5. [🚨 Troubleshooting](#troubleshooting) - Resolver problemas
6. [❓ FAQ](#faq) - Preguntas frecuentes

---

## Quick Start

### ⚡ Opción 1: Inicialización Automática (Recomendado - 3 minutos)

La forma más rápida y segura de crear un admin.

#### Paso 1: Editar `.env`

```bash
# En la raíz del proyecto, editar o crear .env
INIT_DEFAULT_ADMIN=true
ADMIN_DEFAULT_NAME="Admin Sistema"
ADMIN_DEFAULT_EMAIL="admin@moirai.local"
ADMIN_DEFAULT_PASSWORD="AdminPassword123!"
```

#### Paso 2: Iniciar la aplicación

```bash
python main.py
# O con uvicorn:
uvicorn app.main:app --reload
```

**Esperado en logs**:
```
✅ Admin creado exitosamente:
   Email: admin@moirai.local
   API Key prefix: adm_...
```

#### Paso 3: Desabilitar para siguiente reinicio

```bash
# IMPORTANTE: Cambiar en .env
INIT_DEFAULT_ADMIN=false
```

#### Paso 4: Login como admin

```
URL: http://localhost:8000/login
Email: admin@moirai.local
Password: AdminPassword123!
```

#### Paso 5: Acceder al dashboard

```
http://localhost:8000/admin/dashboard
```

---

### 🛠️ Opción 2: Crear Admin Manualmente (Script CLI - 1 minuto)

Para crear admins adicionales o en producción.

```bash
# Crear nuevo admin
python3 manage_admin.py --create "Admin Dev" "admin@dev.local" "DevPass123!"

# Output esperado:
# ✅ Admin creado exitosamente!
# 📋 Email: admin@dev.local
# 🔑 API Key: adm_xyz789... (guardar!)
```

---

### 📋 Gestión de Admins (Comandos disponibles)

```bash
# Listar todos los admins
python3 manage_admin.py --list

# Cambiar contraseña
python3 manage_admin.py --change-password "admin@moirai.local" "NewPassword456!"

# Inicializar desde .env explícitamente
python3 manage_admin.py --init-from-env
```

---

## Arquitectura de Seguridad

### 🏗️ Capas Implementadas

El sistema de admin seguro funciona en **6 capas**:

#### Capa 1: Auth Service Mejorado
**Archivo**: `app/services/auth_service.py`

**Cambios**:
- `find_user_by_email()` detecta admins por `program="Administration"`
- `create_user()` soporta `role="admin"`

```python
# El sistema ahora entiende 3 roles:
- "student": Usuario estudiante
- "company": Empresa colaboradora  
- "admin": Administrador del sistema
```

#### Capa 2: Configuración Centralizada
**Archivo**: `app/core/config.py`

```python
# SIN VALORES HARDCODED - Todo desde .env
INIT_DEFAULT_ADMIN: bool = Field(default=False)
ADMIN_DEFAULT_NAME: Optional[str] = Field(default=None)
ADMIN_DEFAULT_EMAIL: Optional[str] = Field(default=None)
ADMIN_DEFAULT_PASSWORD: Optional[str] = Field(default=None)
```

**Ventaja**: Credenciales NO en el código

#### Capa 3: Módulo de Inicialización
**Archivo**: `app/core/admin_init.py`

Funciones clave:
- `init_default_admin(session)` → Crea admin al startup
  - ✅ Idempotente (no recrea si existe)
  - ✅ Valida todas las variables
  - ✅ Genera API key automáticamente
  - ✅ Registra en auditoría

- `verify_admin_access_configured()` → Verifica acceso

#### Capa 4: Integración en Startup
**Archivo**: `app/main.py`

```python
@app.on_event("startup")
async def startup_event():
    create_db_and_tables()
    
    # Admin initialization from .env
    with Session(engine) as session:
        admin_id = init_default_admin(session)
        verify_admin_access_configured()
```

#### Capa 5: Script de Gestión Manual
**Archivo**: `manage_admin.py`

CLI para gestionar admins sin reiniciar la app:
- Crear admins adicionales
- Listar admins existentes
- Cambiar contraseñas
- Inicializar desde .env

#### Capa 6: Variables de Entorno
**Archivos**: `.env` y `.env.example`

```env
# .env (local, NO en git - en .gitignore ✅)
INIT_DEFAULT_ADMIN=true|false
ADMIN_DEFAULT_NAME="tu nombre"
ADMIN_DEFAULT_EMAIL="tu@email.com"
ADMIN_DEFAULT_PASSWORD="tu contraseña"
```

```env
# .env.example (SÍ en git - template)
INIT_DEFAULT_ADMIN=false
ADMIN_DEFAULT_NAME="Admin Sistema"
ADMIN_DEFAULT_EMAIL="admin@moirai.local"
ADMIN_DEFAULT_PASSWORD="ChangeMeInProduction!"
```

---

### ✅ Validaciones de Seguridad Implementadas

| Validación | Descripción | Estado |
|-----------|-------------|--------|
| **Idempotencia** | No recrea admin si existe | ✅ |
| **Encriptación** | Password: SHA256, Email: Fernet | ✅ |
| **Variables nulas** | Desactiva si están vacías | ✅ |
| **Email único** | Valida contra BD | ✅ |
| **API key auto** | Genera con secrets module | ✅ |
| **Auditoría** | Registra en logs | ✅ |
| **Sin hardcoding** | Todo desde .env, NO código | ✅ |

---

### 🔒 Comparativa: Antes vs Después

#### ❌ Antes (Inseguro)
```bash
python3 create_admin.py "Admin" "admin@ex.com" "Pass"
# ↓ Problema: 
#   - Credenciales en línea de comando
#   - Visible en historial de shell
#   - Expone en procesos
```

#### ✅ Después (Seguro)
```bash
# Opción 1: Desde .env (recomendado)
INIT_DEFAULT_ADMIN=true
python main.py
# ↓ Ventajas:
#   - .env NO se commitea (en .gitignore)
#   - Credenciales NO en historial
#   - Autocreación transparente
#   - Idempotente

# Opción 2: Desde script
python3 manage_admin.py --init-from-env
# ↓ Lee variables de .env, no pide en CLI
```

---

## Configuración Completa

### 🚀 Opción 1: Inicialización desde .env (Recomendado)

#### Paso 1: Configurar .env

Edita el archivo `.env` en la raíz:

```env
# ⚠️ IMPORTANTE: Cambiar estos valores en producción

# Habilitar inicialización automática
INIT_DEFAULT_ADMIN=true

# Datos del admin a crear
ADMIN_DEFAULT_NAME="Admin Sistema"
ADMIN_DEFAULT_EMAIL="admin@moirai.local"
ADMIN_DEFAULT_PASSWORD="ChangeMeInProduction!"
```

#### Paso 2: Ejecutar la aplicación

```bash
cd /Users/sparkmachine/MoirAI

# Opción A: Con Python directo
python main.py

# Opción B: Con Uvicorn
uvicorn app.main:app --reload
```

#### Paso 3: Verificar creación

En los logs de startup, deberías ver:

```
✅ Admin creado exitosamente:
   Email: admin@moirai.local
   API Key prefix: adm_...
   ⚠️  CAMBIAR CONTRASEÑA EN PRODUCCIÓN
```

#### Paso 4: Desabilitar para siguiente reinicio

**IMPORTANTE**: Cambiar en `.env` después de crear:

```env
INIT_DEFAULT_ADMIN=false
```

Esto evita intentos repetidos de creación en cada startup.

#### Paso 5: Acceder como admin

1. Navega a: http://localhost:8000/login
2. Email: `admin@moirai.local` (o la configurada)
3. Password: La configurada en `.env`
4. Dashboard: http://localhost:8000/admin/dashboard

---

### 🔧 Opción 2: Crear admin manualmente con Script

#### Crear nuevo admin

```bash
python3 manage_admin.py --create "Admin Nombre" "admin@example.com" "Password123!"
```

**Output esperado**:
```
✅ Admin creado exitosamente!

📋 Datos de acceso:
   ID:       1
   Nombre:   Admin Nombre
   Email:    admin@example.com
   Rol:      admin

🔑 API Key (guardar en lugar seguro):
   Prefijo:  adm_abc123...
   Key ID:   key_xyz789...
```

#### Listar admins existentes

```bash
python3 manage_admin.py --list
```

**Output**:
```
📋 Admins registrados:

  ID: 1
  Nombre: Admin Sistema
  Email: admin@moirai.local
  Creado: 2025-11-17 10:30:45
```

#### Cambiar contraseña

```bash
python3 manage_admin.py --change-password "admin@moirai.local" "NuevaContraseña123!"
```

**Output**:
```
✅ Contraseña actualizada exitosamente!
```

---

### 🔑 Variables de Entorno Explicadas

| Variable | Descripción | Ejemplo | Requerida |
|----------|-------------|---------|-----------|
| `INIT_DEFAULT_ADMIN` | Habilitar creación auto | `true` o `false` | Sí |
| `ADMIN_DEFAULT_NAME` | Nombre del admin | `"Admin Sistema"` | Si INIT=true |
| `ADMIN_DEFAULT_EMAIL` | Email único | `"admin@moirai.local"` | Si INIT=true |
| `ADMIN_DEFAULT_PASSWORD` | Contraseña inicial | `"Contraseña123!"` | Si INIT=true |

---

## Mejores Prácticas

### 🔒 En Desarrollo

```env
# ✅ RECOMENDADO para testing
INIT_DEFAULT_ADMIN=true
ADMIN_DEFAULT_NAME="Admin Dev"
ADMIN_DEFAULT_EMAIL="admin@localhost"
ADMIN_DEFAULT_PASSWORD="Admin123!"
```

**Ventajas**:
- Fácil recordar credenciales
- Admin se crea automáticamente
- Ideal para testing local

---

### 🔒 En Producción

```env
# ❌ NUNCA hacer esto:
INIT_DEFAULT_ADMIN=true              # ← Podría recrear admin
ADMIN_DEFAULT_PASSWORD="simple123"   # ← Contraseña débil

# ✅ CONFIGURACIÓN RECOMENDADA:
INIT_DEFAULT_ADMIN=false             # ← Admin creado UNA SOLA VEZ
ADMIN_DEFAULT_EMAIL="admin.prod@company.com"
ADMIN_DEFAULT_PASSWORD="RandomStrongPassword123!@#$%"
```

**Checklist de Seguridad**:
- [ ] `INIT_DEFAULT_ADMIN=false` (nunca true)
- [ ] Contraseña fuerte (20+ caracteres, números, símbolos)
- [ ] Email único y verificable
- [ ] `.env` NO comiteable (en `.gitignore`)
- [ ] `.env.example` SÍ comiteable (sin valores)
- [ ] Admin cambia contraseña en primer login
- [ ] API key guardada en lugar seguro
- [ ] Auditoría habilitada

---

### 📋 Puntos Críticos

#### 1. No Commitear `.env`

Verificar que está en `.gitignore`:

```bash
cat .gitignore | grep .env
# Debe mostrar: .env
```

Si NO está, añadirlo:

```bash
echo ".env" >> .gitignore
```

#### 2. Usar `.env.example`

Crear template sin valores sensibles:

```env
# .env.example (COMMITEAR ESTO)
INIT_DEFAULT_ADMIN=false
ADMIN_DEFAULT_NAME="Admin Sistema"
ADMIN_DEFAULT_EMAIL="admin@moirai.local"
ADMIN_DEFAULT_PASSWORD="ChangeMeInProduction!"
```

#### 3. Cambiar Contraseña en Primer Login

El admin debe cambiar su contraseña inicial:

1. Login con contraseña inicial
2. Ir a Perfil
3. Cambiar contraseña
4. Guardar

#### 4. Guardar API Key Segura

Si se genera una API key:

```json
{
  "api_key": "adm_xyz789_secret_part",
  "key_id": "xyz789",
  "expires_at": "2026-11-17T10:30:45",
  "scopes": ["read:all", "write:all", "admin:all"]
}
```

**Guardar en**:
- 1Password, LastPass, o vault equivalente
- NO en archivos de código
- NO en email sin encriptar

---

## Troubleshooting

### 🚨 Error: "Admin ya existe"

```
⚠️ Admin ya existe: admin@moirai.local
   (cambiar INIT_DEFAULT_ADMIN=false en .env para evitar intentos repetidos)
```

**Soluciones**:

**Opción 1**: Cambiar `INIT_DEFAULT_ADMIN=false`
```env
INIT_DEFAULT_ADMIN=false
```

**Opción 2**: Cambiar email si necesitas otro admin
```env
ADMIN_DEFAULT_EMAIL="admin2@moirai.local"
```

---

### 🚨 Error: "Email inválido"

```
❌ Error: Email inválido
```

**Solución**: Verificar formato de email:

```env
ADMIN_DEFAULT_EMAIL="admin@company.com"  # ✅ Correcto
ADMIN_DEFAULT_EMAIL="admin"              # ❌ Incorrecto
ADMIN_DEFAULT_EMAIL="admin@"             # ❌ Incorrecto
```

---

### 🚨 Error: "Contraseña muy corta"

```
❌ Error: Contraseña debe tener al menos 6 caracteres
```

**Solución**: Usar contraseña más larga:

```env
ADMIN_DEFAULT_PASSWORD="A123"         # ❌ Solo 4 caracteres
ADMIN_DEFAULT_PASSWORD="Admin123!"    # ✅ 12 caracteres
```

---

### 🚨 Error: "Variables en blanco"

```
⚠️ INIT_DEFAULT_ADMIN=true pero valores en blanco en .env
```

**Solución**: Completar todas las variables:

```env
INIT_DEFAULT_ADMIN=true
ADMIN_DEFAULT_NAME="Admin"
ADMIN_DEFAULT_EMAIL="admin@example.com"
ADMIN_DEFAULT_PASSWORD="Password123!"
```

---

### 🚨 Error: "500 Internal Server Error" en `/admin/users`

Ver documentación separada: `ADMIN_USERS_ENDPOINT_FIX.md`

---

### 🧪 Debug: Verificar Admin en Base de Datos

```bash
sqlite3 moirai.db "SELECT id, name, email, program FROM student LIMIT 5;"
```

**Esperado**:
```
1|Admin Sistema|admin@moirai.local|Administration
```

---

### 🧪 Debug: Verificar Encryption Service

```bash
python -c "from app.utils.encryption import EncryptionService; service = EncryptionService(); print('✅ Encryption OK')"
```

---

### 🧪 Debug: Probar Endpoint Directamente

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/admin/users 2>/dev/null | python -m json.tool
```

---

## FAQ

### ¿Dónde se almacena la contraseña?

En la tabla `student` (no hay tabla Admin separada):
- **Campo**: `student.hashed_password`
- **Encriptación**: SHA256 (no reversible)
- **Identificación**: `student.program = "Administration"`

---

### ¿Cómo se identifica un admin?

Por el campo `program`:

```python
# En la base de datos:
student.program = "Administration"  # ← Identifica como admin

# En la lógica de negocio:
if student.program == "Administration":
    role = "admin"  # ← Se asigna rol admin
```

---

### ¿Se puede cambiar el rol post-creación?

Sí, modificando el campo `program`:

```bash
# En BD SQLite
sqlite3 moirai.db "UPDATE student SET program = 'Administration' WHERE email = 'admin@ex.com';"

# En Python (en app)
student.program = "Administration"  # → Se convierte en admin
student.program = "Ingeniería"      # → Se convierte en student
session.commit()
```

---

### ¿Qué pasa si dejo `INIT_DEFAULT_ADMIN=true`?

- Cada startup intenta crear el admin
- Si ya existe, solo imprime log (idempotente)
- **No causa duplicados**
- **Pero NO es recomendado** en producción

**Recomendación**: Cambiar a `false` después de crear

---

### ¿Cómo creo múltiples admins?

#### Opción 1: Usar script varias veces

```bash
python3 manage_admin.py --create "Admin 1" "admin1@company.com" "Pass123!"
python3 manage_admin.py --create "Admin 2" "admin2@company.com" "Pass456!"
python3 manage_admin.py --create "Admin 3" "admin3@company.com" "Pass789!"
```

#### Opción 2: Crear primero uno, luego cambiar email en .env

```env
# Primera vez:
INIT_DEFAULT_ADMIN=true
ADMIN_DEFAULT_EMAIL="admin1@company.com"

# Luego cambiar:
INIT_DEFAULT_ADMIN=true
ADMIN_DEFAULT_EMAIL="admin2@company.com"
```

---

### ¿Se puede usar sin .env?

No. El sistema requiere `.env` para:
- `INIT_DEFAULT_ADMIN`: Habilitar/deshabilitar
- Variables de admin si está habilitado

**Fallback**: El código proporciona defaults seguros (None/False)

---

### ¿Qué pasa si pierdo la contraseña del admin?

#### Opción 1: Cambiar directamente en BD (dev only)

```bash
# Generar nuevo hash
python -c "from app.services.auth_service import AuthenticationService; print(AuthenticationService.hash_password('NewPassword123!'))"

# Actualizar en BD
sqlite3 moirai.db "UPDATE student SET hashed_password = 'nuevo_hash' WHERE email = 'admin@ex.com';"
```

#### Opción 2: Crear nuevo admin

```bash
python3 manage_admin.py --create "New Admin" "newadmin@ex.com" "Password123!"
```

---

### ¿Cómo exporto/importo configuración de admin?

Actualmente no hay herramienta automática. Opciones:

#### Opción 1: Usar .env.example como template

```bash
cp .env.example .env
# Editar con nuevos valores
```

#### Opción 2: Exportar desde BD

```bash
sqlite3 moirai.db ".dump student" > backup.sql
```

---

### ¿Puedo usar OAuth/2FA con admin?

**Actual**: No, solo email + password

**Roadmap Phase 2**:
- [ ] OAuth 2.0 integration
- [ ] 2FA (TOTP)
- [ ] MFA policies

---

## Archivos Relacionados

| Archivo | Propósito |
|---------|-----------|
| `app/core/admin_init.py` | Módulo de inicialización |
| `manage_admin.py` | Script CLI para gestión |
| `app/services/auth_service.py` | Servicios de autenticación |
| `app/core/config.py` | Configuración centralizada |
| `.env` | Variables de entorno (NO commitear) |
| `.env.example` | Template de ejemplo (SÍ commitear) |
| `app/main.py` | Entrada de la app (integración startup) |
| `ADMIN_USERS_ENDPOINT_FIX.md` | Documentación del fix 500 error |
| `ADMIN_USERS_ENDPOINT_FIX.md` | Documentación del fix 500 error |

---

## Estadísticas

| Métrica | Valor |
|---------|-------|
| **Archivos modificados** | 5 |
| **Archivos creados** | 3 |
| **Funciones nuevas** | 5+ |
| **Líneas de documentación** | 600+ |
| **Validaciones implementadas** | 7 |
| **Roles soportados** | 3 (student, company, admin) |
| **Scripts CLI disponibles** | 4 comandos |

---

## Resumen

### ✅ Lo que logramos

✓ **Seguridad**: Credenciales NO en código  
✓ **Automatización**: Admin creado en startup  
✓ **Idempotencia**: No causa errores si se reinicia  
✓ **Flexibilidad**: Múltiples formas de crear  
✓ **Auditoría**: Registro en logs  
✓ **Production-ready**: Diferentes configs por ambiente  

### 🚀 Próximas Mejoras (Opcional - Phase 2)

- [ ] 2FA para admin
- [ ] OAuth 2.0
- [ ] Password strength validator mejorado
- [ ] Admin audit dashboard
- [ ] Role-based permissions granulares

---

**Creado**: 17 de noviembre de 2025  
**Versión**: 1.0  
**Status**: ✅ LISTO PARA PRODUCCIÓN
