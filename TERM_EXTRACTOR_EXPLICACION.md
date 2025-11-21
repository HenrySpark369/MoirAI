# TermExtractor - Explicación Detallada

## ¿QUÉ ES?

`TermExtractor` es una clase que extrae términos **relevantes** de un texto de forma **inteligente**.

Tiene 2 métodos principales:

---

## 1. `extract_technical_terms(text)` 

### Propósito
Encontrar habilidades técnicas en un CV o texto.

### ¿Cómo funciona?

```
INPUT: "Tengo experiencia con Python y React. Python es mi lenguaje favorito."

PASO 1: Normalizar texto
"tengo experiencia con python y react python es mi lenguaje favorito"

PASO 2: Tokenizar (dividir en palabras)
["tengo", "experiencia", "con", "python", "y", "react", "python", "es", ...]

PASO 3: Buscar términos técnicos
- Compara cada token con TECHNICAL_VOCAB (que tiene "python", "react", etc)
- Si encuentra: "python" ✓ (está en TECHNICAL_VOCAB)
- Si encuentra: "react" ✓ (está en TECHNICAL_VOCAB)

PASO 4: Calcular RELEVANCIA
- Base: relevance = 1.0
- Aumenta por frecuencia: relevance += count(token) * 0.1
  
  Ejemplo:
  - "python" aparece 2 veces → 1.0 + (2 * 0.1) = 1.2
  - "react" aparece 1 vez  → 1.0 + (1 * 0.1) = 1.1

PASO 5: Deduplicar y ordenar
Eliminar duplicados, mantener máxima relevancia, ordenar descendente

OUTPUT: [
    ("python", 1.2),      ← Más relevante (aparece 2 veces)
    ("react", 1.1)        ← Menos relevante (aparece 1 vez)
]
```

### Ventajas vs hardcoded
```
❌ HARDCODED (nlp_service.py):
for skill in ["python", "java", "react", ...]:
    if skill in resume_clean:
        extracted_skills.append(skill)
Problema: Devuelve lista plana sin orden/peso

✅ TERMEXTRACTOR:
technical_terms = extractor.extract_technical_terms(text)
Devuelve: [("python", 1.2), ("react", 1.1), ...]
Ventaja: Ordenado por relevancia (frecuencia), ponderado
```

---

## 2. `extract_keyphrases(text, max_phrase_length=3)`

### Propósito
Encontrar frases clave (multi-palabra) en un texto.
Usado para extraer PROYECTOS y DESCRIPCIONES.

### ¿Cómo funciona?

```
INPUT: "Desarrollé un sistema de gestión de inventarios usando Python. 
        Creé una aplicación web con React."

PASO 1: Normalizar
"desarrolle un sistema de gestion de inventarios usando python creé una 
aplicacion web con react"

PASO 2: Tokenizar
["desarrolle", "un", "sistema", "de", "gestion", "de", "inventarios", 
 "usando", "python", "creé", "una", "aplicacion", "web", "con", "react"]

PASO 3: Generar N-GRAMAS (frases de 2-3 palabras)
Bigramas (2 palabras):
- "desarrolle un"
- "un sistema"
- "sistema de"
- "de gestion"
- "gestion de"
- "de inventarios"
- ... etc

Trigramas (3 palabras):
- "desarrolle un sistema"
- "un sistema de"
- "sistema de gestion"
- "de gestion de"
- ... etc

PASO 4: Contar FRECUENCIA
Si una frase aparece múltiples veces, la frecuencia sube

Ejemplo:
- "sistema de" aparece 1 vez → score = 1.0
- "aplicacion web" aparece 1 vez → score = 1.0

PASO 5: Ordenar por frecuencia descendente

OUTPUT: [
    ("sistema de gestion de inventarios", 0.15),  ← Score normalizado
    ("aplicacion web con react", 0.12),
    ("desarrolle un sistema", 0.10),
    ...
]
```

### Ventajas para extraer PROYECTOS
```
En lugar de solo buscar palabras clave ("proyecto", "sistema", "app"):

nlp_service.py HARDCODED:
if any(kw in sentence for kw in ["proyecto", "sistema", "app"]):
    projects.append(sentence)
Devuelve: Lista sin orden ni pesos

TermExtractor:
keyphrases = extractor.extract_keyphrases(text)
for phrase, score in keyphrases:
    if any(kw in phrase for kw in project_keywords):
        projects.append(phrase)  # ← Ordenado por score
Devuelve: Frases ordenadas por relevancia
```

---

## 3. TECHNICAL_VOCAB - El Diccionario

```python
TECHNICAL_VOCAB = {
    # Lenguajes
    "python", "java", "javascript", "typescript", "go", "rust", ...
    
    # Frameworks
    "react", "vue", "angular", "fastapi", "django", ...
    
    # Bases de datos
    "postgresql", "mongodb", "redis", ...
    
    # Cloud/DevOps
    "aws", "azure", "docker", "kubernetes", ...
}
```

Se usa en `extract_technical_terms()` para filtrar tokens válidos.

---

## COMPARACIÓN: NLPSERVICE vs TERMEXTRACTOR

### nlp_service.analyze_resume()
```python
# Método: Búsqueda exacta (HARDCODED)
technical_skills = {
    "python", "java", "react", ...  # ← Lista fija
}

for skill in technical_skills:
    if skill in resume_clean:
        extracted_skills.append(skill)

# Resultado: ["python", "react", "java", ...]
# Problema: SIN ORDEN, SIN PESO, SIN CONTEXTO
```

### TermExtractor.extract_technical_terms()
```python
# Método: Búsqueda INTELIGENTE con ponderación
technical_terms = []
for token in tokens:
    if token in TECHNICAL_VOCAB:
        relevance = 1.0 + (count(token) * 0.1)
        technical_terms.append((token, relevance))

# Resultado: [("python", 1.2), ("react", 1.1), ...]
# Ventaja: ORDENADO POR RELEVANCIA, ponderado por frecuencia
```

---

## CASO DE USO: Extraer Skills + Projects

### ❌ VIEJO (nlp_service):
```python
# Skills: hardcoded keywords
technical_skills = {"python", "java", ...}
for skill in technical_skills:
    if skill in resume:
        skills.append(skill)

# Projects: sentencias que contienen palabras clave
project_keywords = {"proyecto", "sistema", ...}
for sentence in resume.split('. '):
    if any(kw in sentence for kw in project_keywords):
        projects.append(sentence)

# Resultado: Sin orden, sin peso
```

### ✅ NUEVO (TermExtractor + analyze_document):
```python
# 1. Obtener todo del documento
doc_analysis = text_vectorization_service.analyze_document(resume)

# 2. Extraer skills (con ponderación)
technical_terms = doc_analysis["technical_terms"]
# Resultado: [("python", 1.2), ("react", 1.1), ...]
skills = [term[0] for term in technical_terms]

# 3. Extraer projects (frases relevantes)
keyphrases = doc_analysis["keyphrases"]
# Resultado: [("desarrolle sistema gestión", 0.9), ...]
projects = []
for phrase, score in keyphrases:
    if any(kw in phrase for kw in project_keywords):
        projects.append(phrase)

# Resultado: Ordenado, ponderado, contextualizado ✓
```

---

## VENTAJAS DE TERMEXTRACTOR

1. **Inteligente**: No es búsqueda simple, es análisis de texto
2. **Ponderado**: Términos más frecuentes = más relevancia
3. **Flexible**: Se reutiliza para múltiples casos
4. **Escalable**: Fácil agregar new VOCAB (soft_skills, etc)
5. **Sin hardcoding**: Se basa en diccionarios centralizados

---

## CÓMO AGREGAR SOFT_SKILLS

Si decidimos que SI queremos soft_skills inteligente:

### Opción A: Extender TECHNICAL_VOCAB
```python
TECHNICAL_VOCAB = {...}  # Ya existe

SOFT_SKILLS_VOCAB = {
    "comunicación", "liderazgo", "teamwork",
    "problem solving", "creativity", ...
}
```

### Opción B: Agregar método a TermExtractor
```python
class TermExtractor:
    def extract_soft_skills(self, text: str) -> List[Tuple[str, float]]:
        """
        Igual que extract_technical_terms pero usa SOFT_SKILLS_VOCAB
        """
        normalized = normalize_text(text, NormalizationType.TECHNICAL)
        tokens = normalized.split()
        
        soft_skills = []
        for token in tokens:
            if token in SOFT_SKILLS_VOCAB:
                relevance = 1.0 + (tokens.count(token) * 0.1)
                soft_skills.append((token, relevance))
        
        unique_skills = {}
        for skill, rel in soft_skills:
            unique_skills[skill] = max(unique_skills.get(skill, 0), rel)
        
        return sorted(unique_skills.items(), key=lambda x: x[1], reverse=True)
```

### Opción C: Reutilizar en analyze_document
```python
def analyze_document(self, text: str) -> Dict:
    technical_terms = self.term_extractor.extract_technical_terms(text)
    soft_skills = self.term_extractor.extract_soft_skills(text)  # ← NUEVO
    keyphrases = self.term_extractor.extract_keyphrases(text)
    
    return {
        "technical_terms": technical_terms,
        "soft_skills": soft_skills,       # ← NUEVO
        "keyphrases": keyphrases,
        ...
    }
```

---

## CONCLUSIÓN

**TermExtractor es superior porque:**

✅ Extrae de forma **inteligente** (no hardcoded)
✅ Pondera por **frecuencia** (más apariciones = más relevante)
✅ Retorna **tuplas** (term, score) para poder filtrar/ordenar
✅ Reutilizable para **múltiples vocabularios**
✅ Escalable: agregar soft_skills = 15 líneas

**vs nlp_service que:**

❌ Búsqueda simple en texto
❌ Sin ponderación
❌ Hardcoded en múltiples lugares
❌ Difícil de mantener/extender

