# 🔐 Guía de Configuración de Encriptación

**Fecha**: 5 de noviembre de 2025  
**Versión**: 1.0.0  
**Estado**: IMPLEMENTADO ✅

---

## 📋 Tabla de Contenidos
1. [Generación de Clave](#generación-de-clave)
2. [Configuración del Entorno](#configuración-del-entorno)
3. [Uso del Servicio](#uso-del-servicio)
4. [Campos a Encriptar](#campos-a-encriptar)
5. [Seguridad](#seguridad)

---

## 🔑 Generación de Clave

### Opción 1: Generar Nueva Clave (Recomendado)

```bash
# En Python interactivo
python -c "
from app.utils.encryption import EncryptionService
key = EncryptionService.generate_key()
print(f'ENCRYPTION_KEY={key}')
"
```

**Salida esperada:**
```
ENCRYPTION_KEY=r2_dGKkRrBvn6B2_efZOqAQhd6SmeWKIAVgJ8sPAYTY=
```

### Opción 2: Generar desde Contraseña

```bash
python -c "
from app.utils.encryption import EncryptionService
key, salt = EncryptionService.generate_key_from_password('mi_contraseña_segura')
print(f'ENCRYPTION_KEY={key}')
print(f'ENCRYPTION_SALT={salt}')
"
```

**Nota**: Si usas contraseña, guardar también el SALT para poder regenerar la clave.

---

## 🌍 Configuración del Entorno

### Opción 1: Variable de Entorno (RECOMENDADO)

#### En macOS/Linux (.env):
```bash
# .env (en raíz del proyecto)
ENCRYPTION_KEY=r2_dGKkRrBvn6B2_efZOqAQhd6SmeWKIAVgJ8sPAYTY=
```

#### En shell (.zshrc o .bash_profile):
```bash
export ENCRYPTION_KEY="r2_dGKkRrBvn6B2_efZOqAQhd6SmeWKIAVgJ8sPAYTY="
```

#### En Docker (docker-compose.yml):
```yaml
services:
  moirai:
    environment:
      - ENCRYPTION_KEY=r2_dGKkRrBvn6B2_efZOqAQhd6SmeWKIAVgJ8sPAYTY=
```

#### En Producción (AWS/GCP/Azure):
```bash
# AWS Secrets Manager
aws secretsmanager create-secret \
  --name moirai/encryption-key \
  --secret-string r2_dGKkRrBvn6B2_efZOqAQhd6SmeWKIAVgJ8sPAYTY=

# Luego configurar en el código:
import boto3
client = boto3.client('secretsmanager')
response = client.get_secret_value(SecretId='moirai/encryption-key')
encryption_key = response['SecretString']
```

### Opción 2: Variables de Configuración

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENCRYPTION_KEY: str = Field(
        ...,
        description="Clave para encriptar campos sensibles"
    )
    
    class Config:
        env_file = ".env"
```

---

## 🔒 Uso del Servicio

### Encriptación Básica

```python
from app.utils.encryption import encryption_service

# Encriptar
plaintext = "información sensible"
encrypted = encryption_service.encrypt(plaintext)
# encrypted: 'gAAAAABl...' (string encriptado)

# Desencriptar
decrypted = encryption_service.decrypt(encrypted)
# decrypted: 'información sensible'
```

### Encriptación de Email

```python
# Encriptar email
encrypted_email = encryption_service.encrypt_email("user@example.com")

# Desencriptar email
email = encryption_service.decrypt_email(encrypted_email)
# email: 'user@example.com'
```

### Encriptación de Teléfono

```python
# Encriptar teléfono
encrypted_phone = encryption_service.encrypt_phone("+1 (555) 123-4567")

# Desencriptar teléfono
phone = encryption_service.decrypt_phone(encrypted_phone)
# phone: '+1 (555) 123-4567'
```

### Encriptación de Diccionarios

```python
student_data = {
    "id": 1,
    "name": "Juan",
    "email": "juan@example.com",
    "phone": "555-1234"
}

# Encriptar campos específicos
encrypted_data = encryption_service.encrypt_dict(
    student_data,
    fields_to_encrypt=["email", "phone"]
)
# encrypted_data['email'] y encrypted_data['phone'] estarán encriptados

# Desencriptar
decrypted_data = encryption_service.decrypt_dict(
    encrypted_data,
    fields_to_decrypt=["email", "phone"]
)
# Vuelve al estado original
```

### Encriptación Opcional (con None)

```python
# Encriptar valor que puede ser None
optional_value = None
encrypted = encryption_service.encrypt_optional(optional_value)
# encrypted: None (sin error)

encrypted_phone = encryption_service.encrypt_optional("+1-555-1234")
# encrypted_phone: 'gAAAAABl...'
```

---

## 📋 Campos a Encriptar

### Campos Críticos (DEBE hacerse):
- ✅ **Emails** - Información de identificación
- ✅ **Teléfonos** - Información personal
- ✅ **Direcciones** - Información personal
- ✅ **Documentos de Identidad** - PII crítica

### Campos Recomendados (DEBERÍA hacerse):
- 🟡 **Nombres Completos** - PII
- 🟡 **Notas Personales** - Pueden contener PII
- 🟡 **Histórico de Aplicaciones** - Contiene datos personales

### Implementación en Modelos

```python
# app/models/user.py
from app.utils.encryption import encryption_service

class Student(SQLModel, table=True):
    id: Optional[int] = None
    name: str
    email: str  # Encriptado en BD
    phone: Optional[str] = None  # Encriptado en BD
    
    def __init__(self, **data):
        super().__init__(**data)
        # Auto-encriptar en inserción
        self.email = encryption_service.encrypt(self.email)
        if self.phone:
            self.phone = encryption_service.encrypt(self.phone)
    
    def get_email(self):
        """Obtener email desencriptado"""
        return encryption_service.decrypt(self.email)
    
    def get_phone(self):
        """Obtener teléfono desencriptado"""
        return encryption_service.decrypt_optional(self.phone)
```

---

## 🔐 Seguridad

### Clave Segura
- **Longitud**: 44 caracteres base64
- **Algoritmo**: Fernet (AES-128)
- **Generación**: Criptográficamente segura

### Buenas Prácticas
1. **Nunca** hardcodear la clave en el código
2. **Siempre** usar variable de entorno
3. **En Producción**: Usar Secret Manager (AWS, GCP, Azure)
4. **Backups**: Guardar clave de forma segura y separada
5. **Rotación**: Plan de rotación de claves cada 6-12 meses

### Auditoría
```python
# Registrar acceso a datos sensibles
import logging

logger = logging.getLogger(__name__)

def log_access(field_name, user_id):
    logger.info(f"Acceso a campo {field_name} por usuario {user_id}")
    # Enviar a sistema de auditoría
```

### Validación
```python
# Verificar integridad de datos
try:
    decrypted = encryption_service.decrypt(encrypted_value)
except Exception as e:
    logger.error(f"Error desencriptando: {e}")
    # Posible corrupción de datos
```

---

## 🧪 Testing

```python
# tests/test_encryption_config.py
import pytest
from app.utils.encryption import encryption_service

def test_encryption_configured():
    """Verificar que la encriptación está configurada"""
    # Intentar encriptar/desencriptar
    test_data = "test@example.com"
    encrypted = encryption_service.encrypt(test_data)
    decrypted = encryption_service.decrypt(encrypted)
    assert decrypted == test_data

def test_production_key_set():
    """Verificar que la clave está en entorno"""
    import os
    assert os.getenv("ENCRYPTION_KEY") is not None
```

---

## 🚀 Implementación Paso a Paso

### 1. Generar Clave
```bash
python -c "from app.utils.encryption import EncryptionService; print('ENCRYPTION_KEY=' + EncryptionService.generate_key())"
```

### 2. Guardar en .env
```bash
echo "ENCRYPTION_KEY=<clave_generada>" >> .env
```

### 3. Verificar Configuración
```bash
python -c "from app.utils.encryption import encryption_service; print('✅ Encriptación lista')"
```

### 4. Actualizar Modelos
```python
# En cada modelo que use datos sensibles
def before_save(self):
    self.email = encryption_service.encrypt(self.email)
```

### 5. Actualizar Consultas
```python
# Cuando recuperes datos encriptados
def get_user(user_id):
    user = db.query(User).get(user_id)
    user.email = encryption_service.decrypt(user.email)
    return user
```

### 6. Tests
```bash
pytest tests/unit/test_encryption_service.py -v
```

---

## ⚠️ Errores Comunes

### Error: "ENCRYPTION_KEY no configurada"
```
⚠️ ENCRYPTION_KEY no configurada. Generando clave temporal (NO usar en producción)
```
**Solución**: Configurar `ENCRYPTION_KEY` en `.env` o variable de entorno

### Error: "Clave de encriptación inválida"
```
ValueError: Clave de encriptación inválida
```
**Solución**: Verificar que la clave es válida (base64)

### Error: "Invalid token"
```
cryptography.fernet.InvalidToken
```
**Solución**: La clave no es la misma que se usó para encriptar

---

## 📞 Soporte

Para preguntas o problemas:
1. Revisar documentación en docstrings
2. Ejecutar tests: `pytest tests/unit/test_encryption_service.py`
3. Contactar equipo de desarrollo

---

**Última Actualización**: 5 de noviembre de 2025  
**Versión**: 1.0.0  
**Status**: ✅ COMPLETO
