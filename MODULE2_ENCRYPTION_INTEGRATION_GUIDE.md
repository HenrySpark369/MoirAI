# Module 2: Encryption Integration - Guía Implementación Rápida

## 📋 Checklist Pre-Implementación

### 1. Revisar Encryption Service Existente
```bash
# ✅ Ya revisado en app/utils/encryption.py
# - EncryptionService class ✅
# - generate_key() ✅
# - encrypt/decrypt methods ✅
# - encrypt_email/decrypt_email ✅
# - encrypt_phone/decrypt_phone ✅
# - _get_hash_email() para búsquedas ✅
# - Tests disponibles: test_encryption_phase*.py ✅
```

### 2. Arquitectura de Integración

```
FastAPI App
    ↓
main.py
    ├─ Import EncryptionService
    ├─ Register dependency: get_encryption_service()
    └─ Create router: POST /api/v1/jobs/parse-and-store
        ↓
    JobPosting Model (SQLModel)
        ├─ Email (encrypted in DB)
        ├─ Email_hash (SHA256 for search)
        ├─ Phone (encrypted in DB)
        ├─ Phone_hash (SHA256 for search)
        └─ set_email(plaintext), get_email() methods
        ↓
    Database (PostgreSQL)
        └─ job_postings table with encrypted fields
```

### 3. Files to Create/Modify

| Archivo | Acción | Prioridad |
|---------|--------|-----------|
| `app/models/job_posting.py` | CREATE | 🔴 ALTA |
| `app/main.py` | MODIFY | 🔴 ALTA |
| `app/core/database.py` | MODIFY | 🟠 MEDIA (setup DB) |
| `tests/unit/test_encryption_integration.py` | CREATE | 🔴 ALTA |
| `tests/integration/test_job_parsing_endpoint.py` | CREATE | 🔴 ALTA |
| `.env` | MODIFY | 🔴 ALTA (DATABASE_URL) |
| `docker-compose.yml` | MODIFY/CREATE | 🔴 ALTA (PostgreSQL) |

---

## 🔧 Step 1: Crear JobPosting Model

**Archivo:** `app/models/job_posting.py`  
**LOC:** ~120 LOC  
**Tiempo:** 30 min

```python
from sqlmodel import SQLModel, Field, Column, String, DateTime, Float, Index, UniqueConstraint
from datetime import datetime
from typing import Optional, List
import json
from app.utils.encryption import get_encryption_service

class JobPosting(SQLModel, table=True):
    """
    Modelo de Job Posting con encriptación integrada
    
    Campos encriptados (Fernet AES-128):
    - email: Almacenado encriptado en BD
    - phone: Almacenado encriptado en BD
    
    Campos hash (búsquedas sin desencriptar):
    - email_hash: SHA256 del email original
    - phone_hash: SHA256 del teléfono original
    
    Cumplimiento LFPDPPP ✅
    """
    __tablename__ = "job_postings"
    
    # IDs
    id: Optional[int] = Field(default=None, primary_key=True)
    external_job_id: str = Field(
        unique=True,
        index=True,
        description="ID único de fuente (OCC.com.mx)"
    )
    
    # Campos básicos
    title: str = Field(index=True, description="Título del puesto")
    company: str = Field(description="Nombre de empresa")
    location: str = Field(index=True, description="Ubicación")
    description: str = Field(description="Descripción completa")
    
    # Campos encriptados (LFPDPPP)
    email: str = Field(description="Email ENCRIPTADO en BD")
    email_hash: str = Field(
        unique=True,
        index=True,
        description="Hash SHA256 para búsquedas sin desencriptar"
    )
    phone: Optional[str] = Field(default=None, description="Teléfono ENCRIPTADO en BD")
    phone_hash: Optional[str] = Field(default=None, index=True, description="Hash SHA256")
    
    # Datos parsed (del HTML Parser)
    skills: str = Field(
        default="[]",
        description="JSON array de skills extraídas"
    )
    work_mode: str = Field(
        default="hybrid",
        description="presencial | remoto | híbrido"
    )
    job_type: str = Field(
        default="full-time",
        description="full-time | part-time | temporal | freelance"
    )
    salary_min: Optional[float] = Field(default=None)
    salary_max: Optional[float] = Field(default=None)
    currency: str = Field(default="MXN")
    
    # Metadata
    published_at: datetime = Field(description="Fecha publicación original")
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    source: str = Field(default="occ.com.mx", description="Fuente de datos")
    
    # Índices compuestos
    __table_args__ = (
        Index('idx_location_skills', 'location', 'skills'),
        Index('idx_source_published', 'source', 'published_at'),
    )
    
    # Métodos de encriptación
    def set_email(self, plaintext: str) -> None:
        """Encriptar y guardar email"""
        encryption = get_encryption_service()
        self.email = encryption.encrypt_email(plaintext)
        self.email_hash = encryption._get_hash_email(plaintext)
    
    def get_email(self) -> str:
        """Desencriptar email"""
        encryption = get_encryption_service()
        return encryption.decrypt_email(self.email)
    
    def set_phone(self, plaintext: Optional[str]) -> None:
        """Encriptar y guardar teléfono"""
        if not plaintext:
            self.phone = None
            self.phone_hash = None
            return
        
        encryption = get_encryption_service()
        self.phone = encryption.encrypt_phone(plaintext)
        self.phone_hash = encryption._get_hash_email(plaintext)
    
    def get_phone(self) -> Optional[str]:
        """Desencriptar teléfono"""
        if not self.phone:
            return None
        
        encryption = get_encryption_service()
        return encryption.decrypt_phone(self.phone)
    
    def get_skills(self) -> List[str]:
        """Parsear skills JSON"""
        return json.loads(self.skills or "[]")
    
    def set_skills(self, skills: List[str]) -> None:
        """Serializar skills a JSON"""
        self.skills = json.dumps(skills)
    
    @classmethod
    def from_job_item(cls, job_item, encryption_service=None):
        """Crear JobPosting desde JobItem (del parser HTML)"""
        if not encryption_service:
            encryption_service = get_encryption_service()
        
        posting = cls(
            external_job_id=job_item.external_job_id,
            title=job_item.title,
            company=job_item.company,
            location=job_item.location,
            description=job_item.description,
            work_mode=job_item.work_mode or "hybrid",
            job_type=job_item.job_type or "full-time",
            salary_min=job_item.salary_min,
            salary_max=job_item.salary_max,
            published_at=job_item.published_at,
            source=job_item.source
        )
        
        # Encriptar email
        if job_item.email:
            posting.set_email(job_item.email)
        
        # Encriptar phone
        if job_item.phone:
            posting.set_phone(job_item.phone)
        
        # Skills
        posting.set_skills(job_item.skills)
        
        return posting
```

---

## 🔌 Step 2: Registrar en main.py

**Modificaciones a hacer:**

```python
# En app/main.py - IMPORTS
from app.models.job_posting import JobPosting
from app.utils.encryption import get_encryption_service
from app.services.html_parser_service import get_html_parser
from app.core.database import get_session

# En app/main.py - DEPENDENCIES
@app.get("/health/encryption")
async def health_encryption():
    """Verificar que encriptación está disponible"""
    try:
        encryption = get_encryption_service()
        test_key = encryption.generate_key()
        return {"status": "ok", "encryption": "enabled"}
    except Exception as e:
        return {"status": "error", "encryption": "failed", "error": str(e)}, 500

# En app/main.py - NEW ROUTER
@app.post("/api/v1/jobs/parse-and-store")
async def parse_and_store_job(
    html: str,
    external_job_id: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """
    Parsear HTML job listing y almacenar en BD con encriptación
    
    Flow:
    1. Parsear HTML con HTMLParserService
    2. Validar JobItem
    3. Convertir a JobPosting con encriptación
    4. Almacenar en BD
    5. Retornar ID del job
    """
    try:
        parser = get_html_parser()
        job_item = parser.parse_job_listing(html, external_job_id)
        
        # Validar
        if not parser.validate_job_item(job_item):
            return {"error": "Job item validation failed"}, 422
        
        # Crear JobPosting con encriptación
        posting = JobPosting.from_job_item(job_item)
        
        # Guardar en BD
        session.add(posting)
        session.commit()
        session.refresh(posting)
        
        return {
            "id": posting.id,
            "external_job_id": posting.external_job_id,
            "title": posting.title,
            "company": posting.company,
            "location": posting.location,
            "status": "stored_encrypted"
        }
    
    except ValueError as e:
        return {"error": str(e)}, 422
    except Exception as e:
        logger.error(f"Error storing job: {e}")
        return {"error": "Internal server error"}, 500
```

---

## 📦 Step 3: Setup Database

**Archivo:** `.env` (MODIFICAR)
```
DATABASE_URL=postgresql://postgres:moirai_dev@localhost:5432/moirai_db
```

**Archivo:** `docker-compose.yml` (CREAR/MODIFICAR)
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16
    container_name: moirai-db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: moirai_dev
      POSTGRES_DB: moirai_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

**Comando para iniciar:**
```bash
docker-compose up -d
```

---

## ✅ Step 4: Unit Tests (8 tests)

**Archivo:** `tests/unit/test_job_posting_model.py`

```python
import pytest
from app.models.job_posting import JobPosting
from app.utils.encryption import get_encryption_service
from app.services.html_parser_service import JobItem

def test_job_posting_encryption_email():
    """Test que email se encripta correctamente"""
    posting = JobPosting(
        external_job_id="test_001",
        title="Test Job",
        company="Test Corp",
        location="Test City",
        description="Test description here",
        email="test@example.com"
    )
    
    posting.set_email("user@example.com")
    
    # Verificar que está encriptado
    assert posting.email != "user@example.com"
    assert posting.email_hash is not None
    
    # Verificar que se puede desencriptar
    decrypted = posting.get_email()
    assert decrypted == "user@example.com"

def test_job_posting_encryption_phone():
    """Test que teléfono se encripta correctamente"""
    posting = JobPosting(...)
    posting.set_phone("+52 55 1234 5678")
    
    assert posting.phone != "+52 55 1234 5678"
    assert posting.phone_hash is not None
    
    decrypted = posting.get_phone()
    assert "1234" in decrypted

def test_job_posting_from_job_item():
    """Test conversión de JobItem a JobPosting"""
    job_item = JobItem(
        external_job_id="item_001",
        title="Developer",
        company="Tech",
        location="Remote",
        description="Looking for developers",
        email="jobs@tech.com",
        skills=["Python", "JavaScript"]
    )
    
    posting = JobPosting.from_job_item(job_item)
    
    assert posting.external_job_id == "item_001"
    assert posting.title == "Developer"
    assert posting.email != "jobs@tech.com"  # Encrypted
    assert posting.get_skills() == ["Python", "JavaScript"]

# + 5 más tests
```

---

## 🧪 Step 5: Integration Tests (4 tests)

**Archivo:** `tests/integration/test_job_storage_endpoint.py`

```python
@pytest.mark.asyncio
async def test_parse_and_store_endpoint():
    """Test endpoint POST /api/v1/jobs/parse-and-store"""
    
    html = "<h1>Software Developer</h1>..."
    
    response = client.post(
        "/api/v1/jobs/parse-and-store",
        json={"html": html, "external_job_id": "test_001"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "stored_encrypted"
    
    # Verificar que se guardó en BD
    session = SessionLocal()
    stored = session.query(JobPosting).filter_by(
        external_job_id="test_001"
    ).first()
    
    assert stored is not None
    assert stored.email != "..."  # Encrypted

# + 3 más tests
```

---

## 🎯 Implementation Order

1. **Crear JobPosting model** (30 min)
   - Importar EncryptionService
   - Definir campos
   - Métodos de encriptación

2. **Registrar en main.py** (20 min)
   - Import JobPosting
   - Endpoint: POST /jobs/parse-and-store

3. **Tests** (40 min)
   - 8 unit tests
   - 4 integration tests

4. **Verificación** (10 min)
   - Todos los tests pasen
   - Endpoints respondan

---

## ⏱️ Timeline Estimada

| Paso | Tiempo |
|------|--------|
| JobPosting model | 30 min |
| main.py integration | 20 min |
| Unit tests | 20 min |
| Integration tests | 20 min |
| Debug + Buffer | 20 min |
| **TOTAL** | **~2 horas** |

---

## ✅ Success Criteria

- [ ] JobPosting model funciona
- [ ] Email/phone se encriptan correctamente
- [ ] Se pueden desencriptar
- [ ] Email hash se puede usar para búsquedas
- [ ] 12 tests pasen (8 unit + 4 integration)
- [ ] Endpoint POST /jobs/parse-and-store funciona
- [ ] Datos se almacenan en PostgreSQL encriptados

---

**Status:** Listo para comenzar  
**Archivos Base:** ✅ encryption.py existe y funciona  
**Próximo Paso:** Crear `app/models/job_posting.py`
