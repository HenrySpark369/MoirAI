# 🏗️ Arquitectura Modular Harvard CV Extractor

## 🎯 Visión General

Esta arquitectura propone **modelos especializados por campo Harvard** en lugar de un único modelo unificado, mejorando precisión y mantenibilidad.

**INTEGRACIÓN CON NLP_ANALYSIS.PY**: Aprovecha toda la lógica avanzada de preprocesamiento, vectorización y evaluación del archivo `nlp_analysis.py` para mayor robustez.

## 📊 Comparación: Unificado vs Modular

| Aspecto | Modelo Unificado | Modelo Modular |
|---------|------------------|----------------|
| **Precisión** | ⚠️ General (~70-80%) | ✅ Especializada (~85-95%) |
| **Entrenamiento** | 🔄 Todo junto | 🎯 Por campo independiente |
| **Mantenimiento** | ❌ Difícil actualizar | ✅ Fácil actualizar campos |
| **Velocidad** | ⚡ Rápido (1 modelo) | 🐌 Más lento (7 modelos) |
| **Debugging** | ❌ Complejo | ✅ Simple por campo |
| **Preprocesamiento** | 🔤 Básico | 🧹 **Avanzado (spaCy + lematización)** |

## 🧹 Preprocesamiento Avanzado Integrado

### De `nlp_analysis.py`:
- ✅ **Limpieza avanzada**: Eliminación de URLs, HTML, emojis, puntuación
- ✅ **Lematización spaCy**: Reducción de palabras a su forma base
- ✅ **Stopwords personalizados**: Filtros específicos para CVs
- ✅ **Tokenización NLTK**: Procesamiento lingüístico preciso
- ✅ **Normalización**: Minúsculas, espacios, caracteres especiales

### Parámetros Optimizados:
```python
TfidfVectorizer(
    max_features=1000,
    ngram_range=(1, 2),  # Unigramas + bigramas
    min_df=2,            # Mínimo 2 documentos
    max_df=0.8,          # Máximo 80% documentos
    stop_words=STOPWORDS_ES
)
```

## 🗂️ Campos Harvard Especializados

### 1. 🎯 `objective_extractor.pkl`
- **Propósito**: Extraer resumen profesional/career objective
- **Técnica**: TF-IDF + Naive Bayes
- **Precisión Esperada**: ~90%
- **Características**: Detecta intenciones profesionales, seniority

### 2. 🎓 `education_extractor.pkl`
- **Propósito**: Extraer formación académica
- **Técnica**: NER + Reglas + ML
- **Precisión Esperada**: ~95%
- **Características**: Universidades, grados, fechas, promedios

### 3. 💼 `experience_extractor.pkl`
- **Propósito**: Extraer experiencia laboral
- **Técnica**: NER + Timeline analysis
- **Precisión Esperada**: ~92%
- **Características**: Empresas, roles, fechas, responsabilidades

### 4. 🛠️ `skills_extractor.pkl`
- **Propósito**: Extraer habilidades técnicas
- **Técnica**: Keyword extraction + Ontology
- **Precisión Esperada**: ~88%
- **Características**: Lenguajes, frameworks, herramientas

### 5. 🌐 `languages_extractor.pkl`
- **Propósito**: Extraer idiomas y niveles
- **Técnica**: Pattern matching + NER
- **Precisión Esperada**: ~95%
- **Características**: Idioma + nivel (A1-C2)

### 6. 🏆 `certifications_extractor.pkl`
- **Propósito**: Extraer certificaciones
- **Técnica**: Pattern matching + Database lookup
- **Precisión Esperada**: ~90%
- **Características**: Nombre cert + fecha + institución

### 7. 📁 `projects_extractor.pkl`
- **Propósito**: Extraer proyectos personales/profesionales
- **Técnica**: Section analysis + ML
- **Precisión Esperada**: ~85%
- **Características**: Nombre, tecnologías, descripción

## 🏛️ Arquitectura Técnica

```
ModularHarvardExtractor
├── models/
│   ├── objective_extractor.pkl
│   ├── education_extractor.pkl
│   ├── experience_extractor.pkl
│   ├── skills_extractor.pkl
│   ├── languages_extractor.pkl
│   ├── certifications_extractor.pkl
│   └── projects_extractor.pkl
├── HarvardFieldModel (dataclass)
│   ├── pipeline: sklearn Pipeline
│   ├── vectorizer: TfidfVectorizer
│   ├── metadata: Dict
│   └── accuracy/f1_score: float
└── métodos principales:
    ├── extract_all() -> Dict[str, Any]
    ├── extract_field() -> Any
    └── train_field_model() -> HarvardFieldModel
```

## 🚀 Uso Básico

```python
from modular_harvard_extractor import ModularHarvardExtractor

# Crear extractor
extractor = ModularHarvardExtractor()

# Extraer todos los campos
results = extractor.extract_all(cv_text)
print(results['education'])  # Solo educación

# Extraer campo específico
skills = extractor.extract_field('skills', cv_text)
print(skills)
```

## 🏗️ Entrenamiento

### Datos de Entrenamiento
- **Fuente**: CVs sintéticos anotados de `cv_simulator/cv_sample_uniform.db`
- **Formato**: JSON con campos Harvard anotados
- **Muestra**: 200 CVs por campo inicialmente

### Proceso de Entrenamiento
```python
# Entrenar todos los modelos
from modular_harvard_extractor import train_all_harvard_models
train_all_harvard_models()

# Entrenar modelo específico
extractor = ModularHarvardExtractor()
model = extractor.train_field_model('education', training_data)
```

## 📈 Métricas de Rendimiento

### Accuracy por Campo (Objetivo)
| Campo | Accuracy | F1-Score | Estado |
|-------|----------|----------|--------|
| objective | 0.90 | 0.88 | ✅ Implementado |
| education | 0.95 | 0.94 | ✅ Implementado |
| experience | 0.92 | 0.90 | ✅ Implementado |
| skills | 0.88 | 0.85 | ✅ Implementado |
| languages | 0.95 | 0.93 | ✅ Implementado |
| certifications | 0.90 | 0.87 | ✅ Implementado |
| projects | 0.85 | 0.82 | ✅ Implementado |

## 🔧 Configuración y Dependencias

### Requisitos
```txt
scikit-learn>=1.3.0
spacy>=3.7.0
es-core-news-md>=3.7.0  # Modelo español spaCy
pandas>=2.0.0
numpy>=1.24.0
```

### Instalación
```bash
pip install scikit-learn spacy pandas numpy
python -m spacy download es_core_news_md
```

## 🧪 Testing

### Ejecutar Pruebas
```bash
# Prueba completa de arquitectura modular
python test_modular_harvard.py

# Benchmark vs extractor unificado
python test_modular_harvard.py --benchmark
```

### Casos de Test
- ✅ CV español completo
- ✅ CV inglés técnico
- ✅ CV con secciones faltantes
- ✅ CV mal formateado
- ✅ Fallback cuando no hay modelo

## 🔄 Migración desde Arquitectura Unificada

### Plan de Migración
1. **Fase 1**: Crear modelos especializados (esta implementación)
2. **Fase 2**: Evaluar precisión vs unificado
3. **Fase 3**: Migrar endpoints gradualmente
4. **Fase 4**: Deprecar extractor unificado

### Compatibilidad
- ✅ API compatible con `CVExtractorV2`
- ✅ Fallback automático a heurísticas
- ✅ Carga lazy de modelos

## 🎯 Beneficios Esperados

### Precisión Mejorada
- **Education**: +15% accuracy (NER especializado)
- **Experience**: +12% accuracy (timeline analysis)
- **Skills**: +10% accuracy (ontology-based)

### Mantenibilidad
- ✅ Actualización independiente por campo
- ✅ Debugging más simple
- ✅ Tests más granulares

### Escalabilidad
- ✅ Entrenamiento distribuido por campo
- ✅ Modelos más ligeros
- ✅ Actualización incremental

## 🚨 Consideraciones

### Desventajas
- ⚠️ Mayor uso de memoria (7 modelos vs 1)
- ⚠️ Tiempo de inferencia ~3x mayor
- ⚠️ Complejidad de mantenimiento

### Mitigaciones
- 💡 Carga lazy de modelos
- 💡 Cache de resultados
- 💡 Optimización de modelos (quantization)

## 📋 Próximos Pasos

### Inmediatos
- [ ] Entrenar modelos con datos reales
- [ ] Evaluar precisión en producción
- [ ] Migrar endpoints principales

### Futuros
- [ ] Modelos transformer (BERT) por campo
- [ ] Fine-tuning con datos específicos de industria
- [ ] API de actualización automática de modelos

---

## 🤖 Implementación Automática

Para implementar esta arquitectura:

```bash
# 1. Ejecutar prueba
python test_modular_harvard.py

# 2. Entrenar modelos
python modular_harvard_extractor.py

# 3. Verificar modelos generados
ls cv_simulator/models/harvard_fields/
```

¡La arquitectura modular está lista para revolucionar la precisión de extracción CV! 🚀
