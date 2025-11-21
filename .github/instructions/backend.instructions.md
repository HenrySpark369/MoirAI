---
applyTo: "**/*.py"
---
# Estándares de Backend (Python Agent)

## Stack Tecnológico
- Lenguaje: Python 3.11 (Uso estricto de Type Hints).
- Framework: FastAPI (Arquitectura "Thin Router", lógica en Services).
- DB: SQLAlchemy 2.0+, PostgresSQL & Pydantic V2.

## Reglas de Implementación
1. **Ubicación:**
   - Endpoints -> `app/api/`
   - Lógica NLP/Match -> `app/services/`
   - Modelos DB -> `app/models/`
2. **Seguridad:**
   - Nunca uses `print()`, usa `logging`.
   - Nunca loggees PII (Emails, Teléfonos).
   - Sanitiza inputs en los Schemas de Pydantic.
3. **Testing:**
   - Usa `pytest`.
   - Crea los tests en `tests/unit` o `tests/integration`.
   - Usa `conftest.py` para fixtures.

## Comportamiento Específico (NLP)
- Al trabajar con `app/services/nlp_service.py`, prioriza librerías ligeras (scikit-learn) sobre modelos pesados si es posible.
- Evita bloquear el Event Loop principal con cálculos de CPU intensivos.