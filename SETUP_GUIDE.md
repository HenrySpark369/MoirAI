# 🚀 Guía de Instalación MoirAI

## Instalación Rápida (La forma amena)

### Opción 1: Setup Automático (Recomendado)

```bash
# Solo ejecute este comando desde la raíz del proyecto
chmod +x setup_secure.sh
./setup_secure.sh
```

El script automáticamente:
- ✅ Crea/verifica entorno virtual Python
- ✅ Instala todas las dependencias
- ✅ Descarga modelos spaCy para NLP
- ✅ Genera claves de seguridad
- ✅ Configura variables de entorno

**Tiempo estimado:** 3-5 minutos

---

## Instalación Manual (Paso a Paso)

Si prefieres hacer todo manualmente:

### 1. Entorno Virtual
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# o en Windows:
# .venv\Scripts\activate
```

### 2. Dependencias
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 3. Modelos spaCy (Importante para NLP)
```bash
# Para procesar CV en Español
python -m spacy download es_core_news_md

# O para Inglés (alternativa)
python -m spacy download en_core_web_md
```

### 4. Variables de Entorno
```bash
# Copiar plantilla
cp .env.example .env

# Generar claves seguras (modificar estos comandos en .env)
python -c "import secrets; print(secrets.token_urlsafe(32))"  # SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"  # ENCRYPTION_KEY
```

---

## ✅ Verificación de Instalación

### Test 1: Python y Dependencias
```bash
python -c "import fastapi, spacy, pandas; print('✅ Básicos OK')"
```

### Test 2: Modelos spaCy
```bash
python -c "import spacy; nlp = spacy.load('es_core_news_md'); print('✅ spaCy OK')"
```

### Test 3: Sistema NLP Completo
```bash
python demo_spacy_vs_current_extraction.py
```

Si ves `🏆 Ganador:` al final, ¡todo está funcionando! 🎉

---

## 🔧 Configuración de .env

Variables principales que debes revisar:

```env
# Desarrollo
DEBUG=True
ENVIRONMENT=development

# Database (necesaria para producción)
DATABASE_URL=postgresql://user:password@localhost:5432/moirai_db

# Seguridad (ya auto-generadas)
SECRET_KEY=<generada automáticamente>
ENCRYPTION_KEY=<generada automáticamente>

# NLP
SPACY_LANGUAGE=es  # o 'en' para inglés
```

---

## 🚀 Iniciar el Servidor

```bash
# Modo desarrollo (con auto-reload)
python -m uvicorn app.main:app --reload

# El servidor estará en: http://localhost:8000
```

---

## 🧪 Ejecutar Tests

```bash
# Todos los tests
pytest

# Solo tests de NLP
pytest -k nlp

# Con salida verbose
pytest -v
```

---

## 🐳 Con Docker (Opcional)

```bash
# Verificar que tienes docker-compose
docker-compose --version

# Iniciar servicios
docker-compose --env-file .env.docker up -d

# Ver logs
docker-compose logs -f
```

---

## ⚠️ Problemas Comunes

### ❌ "spaCy model not found"
```bash
# Solución
python -m spacy download es_core_news_md
```

### ❌ "ModuleNotFoundError: No module named 'app'"
```bash
# Solución - Asegúrate de estar en la raíz del proyecto
cd /path/to/MoirAI
source .venv/bin/activate
```

### ❌ "psycopg2 not found" (en macOS)
```bash
# Solución
pip install psycopg2-binary
```

### ❌ "Permission denied" (setup_secure.sh)
```bash
# Solución
chmod +x setup_secure.sh
```

---

## 🔒 Seguridad

**IMPORTANTE:** 
- ❌ Nunca commites `.env` al repositorio
- ❌ Nunca compartas tu `ENCRYPTION_KEY`
- ✅ La `ENCRYPTION_KEY` encripta emails, teléfonos, etc.
- ✅ Si la pierdes, no podrás desencriptar datos existentes

---

## 📚 Más Información

- Arquitectura: Ver `ARCHITECTURE.md`
- API Docs: http://localhost:8000/docs (cuando el servidor esté corriendo)
- Tests: Ver archivos en `tests/` y `test_*.py`

---

## 🎯 Próximos Pasos

1. ✅ Ejecuta `./setup_secure.sh`
2. ✅ Revisa `.env`
3. ✅ Corre `python demo_spacy_vs_current_extraction.py`
4. ✅ Inicia el servidor: `python -m uvicorn app.main:app --reload`
5. ✅ Abre http://localhost:8000/docs

¡Listo para desarrollar! 🚀
