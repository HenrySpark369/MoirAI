#!/usr/bin/env python3
"""
🏗️ Arquitectura Modular de Extracción CV Harvard

Esta arquitectura propone modelos especializados por campo Harvard
para mayor precisión y mantenibilidad.

VENTAJAS sobre modelo unificado:
- ✅ Mayor precisión especializada por campo
- ✅ Entrenamiento más eficiente (menos datos por modelo)
- ✅ Mejor debugging y mantenimiento
- ✅ Actualización independiente de campos
- ✅ Modelos más ligeros y rápidos

CAMPOS HARVARD PROPUESTOS:
1. 🎯 objective_extractor.pkl - Resumen/Objective
2. 🎓 education_extractor.pkl - Educación académica
3. 💼 experience_extractor.pkl - Experiencia laboral
4. 🛠️ skills_extractor.pkl - Habilidades técnicas
5. 🌐 languages_extractor.pkl - Idiomas
6. 🏆 certifications_extractor.pkl - Certificaciones
7. 📁 projects_extractor.pkl - Proyectos

ARQUITECTURA PROPUESTA:
- Modelo base: spaCy NER + reglas heurísticas (como actualmente)
- Entrenamiento: Dataset de CVs anotados sintéticos
- Formato: Pickle con modelo + vectorizer + metadata
"""

import os
import pickle
import logging
import re
import json
import string
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.decomposition import LatentDirichletAllocation
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import spacy
import pandas as pd
import numpy as np
from collections import Counter

# Configuración NLTK
STOPWORDS_ES = set(stopwords.words('spanish')) if 'spanish' in stopwords.fileids() else set()

# Descargar recursos NLTK si no existen
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

logger = logging.getLogger(__name__)

@dataclass
class HarvardFieldModel:
    """Modelo especializado para un campo Harvard"""
    field_name: str
    pipeline: Pipeline
    vectorizer: TfidfVectorizer
    metadata: Dict[str, Any]
    accuracy: float = 0.0
    f1_score: float = 0.0

    def save(self, filepath: str):
        """Guarda el modelo en pickle"""
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
        logger.info(f"✅ Modelo {self.field_name} guardado en {filepath}")

    @classmethod
    def load(cls, filepath: str) -> 'HarvardFieldModel':
        """Carga el modelo desde pickle"""
        with open(filepath, 'rb') as f:
            model = pickle.load(f)
        logger.info(f"✅ Modelo {model.field_name} cargado desde {filepath}")
        return model

class ModularHarvardExtractor:
    """
    Extractor modular con modelos especializados por campo Harvard

    Usa lógica avanzada de preprocesamiento de nlp_analysis.py
    para mayor precisión y robustez.

    Uso:
    ----
    extractor = ModularHarvardExtractor()
    results = extractor.extract_all(cv_text)
    print(results['education'])  # Solo educación
    """

    def __init__(self, models_dir: str = "cv_simulator/models/harvard_fields"):
        self.models_dir = models_dir
        self.models: Dict[str, HarvardFieldModel] = {}
        self.nlp = spacy.load("es_core_news_md")  # Modelo base spaCy

        # Agregar sentencizer para análisis de oraciones
        if 'sentencizer' not in self.nlp.pipe_names:
            self.nlp.add_pipe('sentencizer')

        # Campos Harvard a extraer
        self.harvard_fields = [
            "objective",
            "education",
            "experience",
            "skills",
            "languages",
            "certifications",
            "projects"
        ]

        # Cargar modelos existentes
        self._load_models()

    def preprocess_cv_text_simple(self, text: str) -> str:
        """
        Preprocesamiento simple inspirado en nlp_analysis.py
        Función clean_text_advanced del análisis NLP
        """
        # Convertir a minúsculas
        text = str(text).lower()

        # Eliminar textos entre corchetes (ej.: etiquetas)
        text = re.sub(r'\[.*?\]', '', text)

        # Eliminar URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)

        # Eliminar etiquetas HTML
        text = re.sub(r'<.*?>+', '', text)

        # Eliminar signos de puntuación
        text = re.sub('[%s]' % re.escape(string.punctuation), '', text)

        # Eliminar saltos de línea
        text = re.sub(r'\n', ' ', text)

        # Eliminar palabras que contienen números
        text = re.sub(r'\w*\d\w*', '', text)

        # Eliminar emojis y caracteres especiales (no ASCII)
        text = re.sub(r'[^\x00-\x7F]+', '', text)

        # Eliminar espacios extras
        text = text.strip()

        # Tokenización y filtrado básico
        tokens = word_tokenize(text, language='spanish')
        tokens = [t for t in tokens if t.isalnum() and t not in STOPWORDS_ES and len(t) > 2]
        return ' '.join(tokens)

    def lemmatize_with_spacy(self, text: str) -> str:
        """
        Lematización usando spaCy como en nlp_analysis.py
        """
        doc = self.nlp(text)
        # Eliminar stopwords y aplicar lematización
        lemmatized = [token.lemma_ for token in doc if token.text.lower() not in STOPWORDS_ES]
        return " ".join(lemmatized).strip()

    def preprocess_cv_text_advanced(self, text: str) -> str:
        """
        Preprocesamiento avanzado completo:
        1. Limpieza básica
        2. Lematización con spaCy
        3. Filtros adicionales
        """
        # Limpieza básica
        clean_text = self.preprocess_cv_text_simple(text)

        # Lematización avanzada
        lemmatized_text = self.lemmatize_with_spacy(clean_text)

        return lemmatized_text

    def _load_models(self):
        """Carga todos los modelos disponibles"""
        os.makedirs(self.models_dir, exist_ok=True)

        for field in self.harvard_fields:
            model_path = os.path.join(self.models_dir, f"{field}_extractor.pkl")
            if os.path.exists(model_path):
                try:
                    self.models[field] = HarvardFieldModel.load(model_path)
                    logger.info(f"✅ Modelo {field} cargado")
                except Exception as e:
                    logger.warning(f"❌ Error cargando modelo {field}: {e}")
            else:
                logger.info(f"⚠️ Modelo {field} no encontrado, usando fallback")

    def extract_all(self, cv_text: str) -> Dict[str, Any]:
        """
        Extrae todos los campos Harvard usando modelos especializados

        Usa preprocesamiento avanzado para mayor precisión.

        Args:
            cv_text: Texto completo del CV

        Returns:
            Dict con todos los campos extraídos
        """
        results = {}

        # Preprocesar texto una vez para todos los modelos
        processed_text = self.preprocess_cv_text_advanced(cv_text)

        # Extraer cada campo con su modelo especializado
        for field in self.harvard_fields:
            if field in self.models:
                # Usar modelo entrenado con texto preprocesado
                results[field] = self.models[field].pipeline.predict([processed_text])[0]
            else:
                # Fallback a extracción heurística
                results[field] = self._extract_field_fallback(field, cv_text, {}, {})

        return results

    def extract_field(self, field_name: str, cv_text: str) -> Any:
        """
        Extrae un campo específico usando su modelo especializado

        Usa preprocesamiento avanzado para consistencia con extract_all.

        Args:
            field_name: Nombre del campo Harvard ('education', 'experience', etc.)
            cv_text: Texto del CV

        Returns:
            Contenido extraído del campo
        """
        if field_name not in self.harvard_fields:
            raise ValueError(f"Campo {field_name} no válido. Campos disponibles: {self.harvard_fields}")

        if field_name in self.models:
            # Usar modelo entrenado con preprocesamiento avanzado
            processed_text = self.preprocess_cv_text_advanced(cv_text)
            return self.models[field_name].pipeline.predict([processed_text])[0]
        else:
            # Fallback heurístico
            sections = self._split_sections(cv_text)
            analysis = self._analyze_with_spacy(cv_text)
            return self._extract_field_fallback(field_name, cv_text, sections, analysis)

    def train_field_model(self, field_name: str, training_data: List[Dict[str, Any]],
                         save: bool = True) -> HarvardFieldModel:
        """
        Entrena un modelo especializado para un campo Harvard

        Usa preprocesamiento avanzado de nlp_analysis.py
        para mayor calidad de datos de entrenamiento.

        Args:
            field_name: Campo a entrenar ('education', 'experience', etc.)
            training_data: Lista de dicts con 'cv_text' y campo anotado
            save: Si guardar el modelo entrenado

        Returns:
            Modelo entrenado
        """
        logger.info(f"🏗️ Entrenando modelo para campo: {field_name}")

        # Preprocesar textos con lógica avanzada de nlp_analysis.py
        texts = []
        labels = []

        for item in training_data:
            cv_text = item['cv_text']
            field_value = item.get(field_name, '')

            if field_value:  # Solo incluir ejemplos con datos
                # Usar preprocesamiento avanzado
                processed_text = self.preprocess_cv_text_advanced(cv_text)
                texts.append(processed_text)
                labels.append(str(field_value))  # Convertir a string

        if len(texts) < 10:
            logger.warning(f"⚠️ Pocos datos de entrenamiento para {field_name}: {len(texts)} ejemplos")
            return None

        # Crear pipeline con parámetros optimizados de nlp_analysis.py
        pipeline = Pipeline([
            ('vectorizer', TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),  # Unigramas y bigramas
                min_df=2,  # Aparece en al menos 2 documentos
                max_df=0.8,  # No más del 80% de documentos
                stop_words=list(STOPWORDS_ES)
            )),
            ('classifier', MultinomialNB())
        ])

        # Entrenar con validación cruzada
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                texts, labels, test_size=0.3, random_state=42, stratify=labels
            )
        except ValueError:
            # Fallback si no se puede estratificar
            X_train, X_test, y_train, y_test = train_test_split(
                texts, labels, test_size=0.3, random_state=42
            )

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        # Calcular métricas como en nlp_analysis.py
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')

        # Crear modelo
        model = HarvardFieldModel(
            field_name=field_name,
            pipeline=pipeline,
            vectorizer=pipeline.named_steps['vectorizer'],
            metadata={
                'training_samples': len(texts),
                'field_type': field_name,
                'model_type': 'naive_bayes_tfidf_advanced',
                'preprocessing': 'advanced_spacy_lemmatization',
                'vectorizer_params': {
                    'max_features': 1000,
                    'ngram_range': (1, 2),
                    'min_df': 2,
                    'max_df': 0.8
                }
            },
            accuracy=accuracy,
            f1_score=f1
        )

        logger.info(f"✅ Modelo {field_name} entrenado - Accuracy: {accuracy:.3f}, F1: {f1:.3f}")

        # Guardar
        if save:
            model_path = os.path.join(self.models_dir, f"{field_name}_extractor.pkl")
            model.save(model_path)
            self.models[field_name] = model

        return model

    def _split_sections(self, text: str) -> Dict[str, str]:
        """Divide CV en secciones (método auxiliar)"""
        # Implementación simplificada - usar la del extractor actual
        sections = {}

        header_patterns = [
            (r'(OBJECTIVE|CAREER SUMMARY)', "objective"),
            (r'(EDUCATION|EDUCACIÓN)', "education"),
            (r'(EXPERIENCE|EXPERIENCIA)', "experience"),
            (r'(SKILLS|HABILIDADES)', "skills"),
            (r'(LANGUAGE|IDIOMAS)', "languages"),
            (r'(CERTIFICATIONS?|CERTIFICACIONES?)', "certifications"),
            (r'(PROJECTS?|PROYECTOS?)', "projects"),
        ]

        lines = text.split('\n')
        current_section = None
        current_content = []

        for line in lines:
            line_upper = line.upper().strip()

            found_header = False
            for pattern, section_name in header_patterns:
                if re.search(pattern, line_upper):
                    if current_section:
                        sections[current_section] = '\n'.join(current_content)
                    current_section = section_name
                    current_content = []
                    found_header = True
                    break

            if not found_header and current_section:
                current_content.append(line)

        if current_section:
            sections[current_section] = '\n'.join(current_content)

        return sections

    def _analyze_with_spacy(self, text: str) -> Dict[str, Any]:
        """Análisis básico con spaCy"""
        doc = self.nlp(text)
        return {
            'organizations': [ent.text for ent in doc.ents if ent.label_ == 'ORG'],
            'persons': [ent.text for ent in doc.ents if ent.label_ == 'PERSON'],
            'dates': [ent.text for ent in doc.ents if ent.label_ == 'DATE'],
            'tokens': len(doc)
        }

    def _extract_field_fallback(self, field_name: str, cv_text: str,
                               sections: Dict[str, str], analysis: Dict[str, Any]) -> Any:
        """Extracción fallback heurística cuando no hay modelo entrenado"""
        # Implementación simplificada - usar lógica del extractor actual
        if field_name == "objective":
            return sections.get("objective", "").strip()[:200]
        elif field_name == "education":
            return sections.get("education", "").strip()
        elif field_name == "experience":
            return sections.get("experience", "").strip()
        elif field_name == "skills":
            return sections.get("skills", "").strip().split('\n')
        elif field_name == "languages":
            return sections.get("languages", "").strip()
        elif field_name == "certifications":
            return sections.get("certifications", "").strip().split('\n')
        elif field_name == "projects":
            return sections.get("projects", "").strip().split('\n')
        else:
            return ""

    def get_model_status(self) -> Dict[str, Dict[str, Any]]:
        """Retorna estado de todos los modelos"""
        status = {}
        for field in self.harvard_fields:
            if field in self.models:
                model = self.models[field]
                status[field] = {
                    'trained': True,
                    'accuracy': model.accuracy,
                    'f1_score': model.f1_score,
                    'model_type': model.metadata.get('model_type', 'unknown')
                }
            else:
                status[field] = {
                    'trained': False,
                    'accuracy': 0.0,
                    'f1_score': 0.0,
                    'model_type': 'fallback'
                }
        return status

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def create_training_data_from_synthetic_cvs(db_path: str = "cv_simulator/cv_sample_uniform.db") -> List[Dict[str, Any]]:
    """
    Crea datos de entrenamiento desde CVs sintéticos anotados

    Returns:
        Lista de dicts con cv_text y campos Harvard anotados
    """
    import sqlite3

    training_data = []

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT cv_text, annotations FROM cv_dataset LIMIT 200")  # Usar muestra

        for row in cursor.fetchall():
            cv_text, annotations_json = row
            try:
                annotations = json.loads(annotations_json)

                # Convertir a formato de entrenamiento
                training_item = {
                    'cv_text': cv_text,
                    'objective': annotations.get('current_role', ''),
                    'education': json.dumps(annotations.get('education', [])),
                    'experience': json.dumps(annotations.get('experience', [])),
                    'skills': ', '.join(annotations.get('skills', [])),
                    'languages': json.dumps(annotations.get('languages', {})),
                    'certifications': '',  # No tenemos certificaciones en datos sintéticos
                    'projects': ''  # No tenemos proyectos en datos sintéticos
                }

                training_data.append(training_item)

            except json.JSONDecodeError:
                continue

        conn.close()

    except Exception as e:
        logger.error(f"Error creando datos de entrenamiento: {e}")

    logger.info(f"✅ Creados {len(training_data)} ejemplos de entrenamiento")
    return training_data

def train_all_harvard_models():
    """Entrena todos los modelos Harvard y los guarda"""
    logger.info("🚀 Iniciando entrenamiento de todos los modelos Harvard")

    # Crear datos de entrenamiento
    training_data = create_training_data_from_synthetic_cvs()

    if not training_data:
        logger.error("❌ No hay datos de entrenamiento disponibles")
        return

    # Crear extractor modular
    extractor = ModularHarvardExtractor()

    # Entrenar cada modelo
    for field in extractor.harvard_fields:
        try:
            model = extractor.train_field_model(field, training_data)
            logger.info(f"✅ Modelo {field} entrenado - Acc: {model.accuracy:.3f}")
        except Exception as e:
            logger.error(f"❌ Error entrenando modelo {field}: {e}")

    # Mostrar estado final
    status = extractor.get_model_status()
    logger.info("📊 ESTADO FINAL DE MODELOS:")
    for field, info in status.items():
        trained = "✅" if info['trained'] else "❌"
        acc = info['accuracy']
        logger.info(f"  {trained} {field}: {acc:.3f} accuracy")

if __name__ == "__main__":
    # Entrenar todos los modelos
    train_all_harvard_models()
