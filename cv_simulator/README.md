# CV Simulator Service

Servicio independiente para generar datos sintéticos de CVs usando LLMs locales (LM Studio).
Diseñado para crear datasets de entrenamiento para modelos NLP propios.

## Requisitos

1.  **LM Studio** corriendo localmente.
2.  Modelo cargado: `mistralai/magistral-small` (o `qwen/qwen3-4b-thinking`).
3.  Servidor iniciado en `http://localhost:1234`.

## Instalación

```bash
pip install -r cv_simulator/requirements.txt
```

## Uso

### 1. Generar Datos
Ejecuta el script para comenzar a "minar" CVs. El script se conectará a tu LM Studio local.

```bash
python cv_simulator/generate_cvs.py
```

- Los datos se guardan en `cv_simulator/training_data_cvs.db` (SQLite).
- Puedes detener el script con `Ctrl+C` y reanudarlo después; no se perderán datos.

### 2. Verificar Calidad
Compara los datos generados contra los extractores actuales de MoirAI.

```bash
python cv_simulator/test_generated_cvs.py
```

## Estrategia de NLP (Siguientes Pasos)

Una vez acumulados suficientes datos (e.g., 1,000+ CVs):

1.  **Exportar & Alinear**:
    - Usar los JSONs de `annotations` como "Ground Truth".
    - Alinear las entidades (Skills, Experiencia, Educación) con el texto crudo (`cv_text`) para obtener índices de caracteres `(start, end, label)`.

2.  **Entrenar Modelo NER (spaCy)**:
    - Entrenar un modelo `es_core_news_lg` personalizado.
    - Esto reemplazará las listas hardcodeadas con predicciones basadas en contexto.

3.  **Mejoras de Limpieza**:
    - Implementar **Lemmatización** (`developed` -> `develop`).
    - Usar **Embeddings** para matching semántico en lugar de exacto.
