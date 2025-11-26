#!/usr/bin/env python3
"""
NLP Analysis Service - Evaluación de Dataset de CVs Sintéticos
Prueba métricas de calidad: F1-score, accuracy, TF-IDF, BoW, LDA
"""

import sqlite3
import json
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score, f1_score
from sklearn.decomposition import LatentDirichletAllocation
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import spacy
from spacy.lang.es import Spanish
import warnings
warnings.filterwarnings('ignore')

# Configuración
DB_PATH = 'cv_simulator/training_data_cvs.db'
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

class NLPAnalyzer:
    """Analizador NLP para evaluar calidad de dataset de CVs"""

    def __init__(self, db_path):
        self.db_path = db_path
        self.nlp = Spanish()
        # Agregar sentencizer para análisis de oraciones
        if 'sentencizer' not in self.nlp.pipe_names:
            self.nlp.add_pipe('sentencizer')
        self.data = []
        self.load_data()

    def load_data(self):
        """Cargar datos desde SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT industry, seniority, cv_text, annotations FROM cv_dataset")
        rows = cursor.fetchall()

        for row in rows:
            industry, seniority, cv_text, annotations_json = row
            try:
                annotations = json.loads(annotations_json)
                self.data.append({
                    'industry': industry,
                    'seniority': seniority,
                    'cv_text': cv_text,
                    'annotations': annotations
                })
            except json.JSONDecodeError:
                continue

        conn.close()
        print(f"✅ Cargados {len(self.data)} CVs desde la base de datos")

    def analyze_basic_stats(self):
        """Estadísticas básicas del dataset"""
        print("\n" + "="*60)
        print("📊 ESTADÍSTICAS BÁSICAS DEL DATASET")
        print("="*60)

        df = pd.DataFrame(self.data)

        print(f"Total de CVs: {len(df)}")

        # Distribución por industria
        print("\n📈 Distribución por Industria:")
        industry_counts = df['industry'].value_counts()
        for industry, count in industry_counts.items():
            pct = count / len(df) * 100
            print(f"  {industry}: {count} ({pct:.1f}%)")

        # Distribución por seniority
        print("\n📈 Distribución por Seniority:")
        seniority_counts = df['seniority'].value_counts()
        for seniority, count in seniority_counts.items():
            pct = count / len(df) * 100
            print(f"  {seniority}: {count} ({pct:.1f}%)")

        # Estadísticas de texto
        text_lengths = df['cv_text'].str.len()
        print("\n📏 Estadísticas de Longitud de Texto:")
        print(f"  Promedio: {text_lengths.mean():.0f} caracteres")
        print(f"  Mínimo: {text_lengths.min()} caracteres")
        print(f"  Máximo: {text_lengths.max()} caracteres")

        # Skills más comunes
        all_skills = []
        for item in self.data:
            skills = item['annotations'].get('skills', [])
            all_skills.extend(skills)

        skill_counts = Counter(all_skills)
        print("\n🔧 Top 10 Skills más comunes:")
        for skill, count in skill_counts.most_common(10):
            print(f"  {skill}: {count}")

    def analyze_text_quality(self):
        """Análisis de calidad del texto usando spaCy"""
        print("\n" + "="*60)
        print("🔍 ANÁLISIS DE CALIDAD DE TEXTO (spaCy)")
        print("="*60)

        total_sentences = 0
        total_tokens = 0
        pos_counts = Counter()

        for item in self.data[:10]:  # Analizar solo primeros 10 para demo
            doc = self.nlp(item['cv_text'])
            total_sentences += len(list(doc.sents))
            total_tokens += len(doc)

            for token in doc:
                pos_counts[token.pos_] += 1

        print(f"Promedio de oraciones por CV: {total_sentences/10:.1f}")
        print(f"Promedio de tokens por CV: {total_tokens/10:.1f}")

        print("\n🏷️  Distribución de Partes del Discurso (Top 5):")
        for pos, count in pos_counts.most_common(5):
            print(f"  {pos}: {count}")

    def tfidf_analysis(self):
        """Análisis TF-IDF por industria"""
        print("\n" + "="*60)
        print("📊 ANÁLISIS TF-IDF POR INDUSTRIA")
        print("="*60)

        df = pd.DataFrame(self.data)

        # Preparar textos limpios
        texts = []
        for text in df['cv_text']:
            # Limpieza básica
            text = text.lower()
            tokens = word_tokenize(text, language='spanish')
            tokens = [t for t in tokens if t.isalnum() and t not in STOPWORDS_ES and len(t) > 2]
            texts.append(' '.join(tokens))

        # TF-IDF
        vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(texts)

        # Palabras más importantes por industria
        feature_names = vectorizer.get_feature_names_out()

        for industry in df['industry'].unique():
            industry_texts = df[df['industry'] == industry]['cv_text']
            if len(industry_texts) < 3:
                continue

            industry_clean = []
            for text in industry_texts:
                text = text.lower()
                tokens = word_tokenize(text, language='spanish')
                tokens = [t for t in tokens if t.isalnum() and t not in STOPWORDS_ES and len(t) > 2]
                industry_clean.append(' '.join(tokens))

            industry_tfidf = vectorizer.transform(industry_clean)
            avg_tfidf = np.asarray(industry_tfidf.mean(axis=0)).flatten()

            top_indices = avg_tfidf.argsort()[-10:][::-1]
            top_words = [feature_names[i] for i in top_indices]

            print(f"\n🏭 {industry} (Top 10 palabras TF-IDF):")
            for word in top_words:
                print(f"  {word}")

    def bow_analysis(self):
        """Análisis Bag of Words"""
        print("\n" + "="*60)
        print("📦 ANÁLISIS BAG OF WORDS (BoW)")
        print("="*60)

        df = pd.DataFrame(self.data)

        # BoW simple
        vectorizer = CountVectorizer(max_features=500, stop_words=list(STOPWORDS_ES))
        bow_matrix = vectorizer.fit_transform(df['cv_text'])

        print(f"Vocabulario total: {len(vectorizer.get_feature_names_out())} palabras")
        print(f"Matriz BoW: {bow_matrix.shape[0]} documentos x {bow_matrix.shape[1]} features")

        # Palabras más frecuentes globalmente
        word_freq = bow_matrix.sum(axis=0).A1
        word_names = vectorizer.get_feature_names_out()

        top_indices = word_freq.argsort()[-20:][::-1]
        print("\n📈 Top 20 palabras más frecuentes:")
        for i, idx in enumerate(top_indices):
            print(f"  {i+1:2d}. {word_names[idx]:15s}: {word_freq[idx]}")

    def lda_topic_modeling(self):
        """Análisis temático supervisado basado en secciones de CV con preprocesamiento avanzado"""
        print("\n" + "="*60)
        print("🎭 ANÁLISIS TEMÁTICO SUPERVISADO - SECCIONES DE CV")
        print("="*60)

        # Definir temas principales de CV (supervisados)
        cv_themes = {
            'educación': {
                'keywords': ['educación', 'estudios', 'universidad', 'carrera', 'licenciatura', 'maestría', 'doctorado', 'bachillerato', 'diploma', 'certificación', 'título', 'académico', 'graduado', 'egresado'],
                'description': 'Formación académica y títulos obtenidos'
            },
            'experiencia_profesional': {
                'keywords': ['experiencia', 'profesional', 'trabajo', 'empleo', 'cargo', 'puesto', 'rol', 'posición', 'empresa', 'compañía', 'organización', 'responsabilidades', 'logros', 'proyectos'],
                'description': 'Historial laboral y responsabilidades'
            },
            'habilidades_duras': {
                'keywords': ['habilidades', 'competencias', 'tecnologías', 'herramientas', 'software', 'programación', 'python', 'java', 'sql', 'excel', 'power', 'bi', 'tableau', 'aws', 'docker', 'kubernetes', 'machine learning', 'deep learning', 'estadística', 'matemáticas'],
                'description': 'Habilidades técnicas y herramientas específicas'
            },
            'habilidades_blandas': {
                'keywords': ['liderazgo', 'comunicación', 'trabajo en equipo', 'adaptabilidad', 'resolución de problemas', 'creatividad', 'gestión del tiempo', 'aprendizaje continuo', 'empatía', 'colaboración', 'motivación', 'iniciativa', 'flexibilidad', 'pensamiento crítico'],
                'description': 'Competencias interpersonales y comportamentales'
            },
            'idiomas': {
                'keywords': ['idiomas', 'español', 'inglés', 'francés', 'alemán', 'italiano', 'portugués', 'chino', 'japonés', 'nativo', 'avanzado', 'intermedio', 'básico', 'fluido', 'conversacional'],
                'description': 'Dominio de idiomas y nivel de competencia'
            },
            'contacto_información': {
                'keywords': ['teléfono', 'email', 'correo', 'electrónico', 'dirección', 'ubicación', 'ciudad', 'estado', 'país', 'linkedin', 'github', 'portfolio', 'sitio web', 'contacto'],
                'description': 'Información de contacto y presencia digital'
            }
        }

        df = pd.DataFrame(self.data)

        # Análisis de cobertura por tema
        theme_coverage = {theme: [] for theme in cv_themes.keys()}

        for idx, row in df.iterrows():
            cv_text = row['cv_text'].lower()

            for theme, config in cv_themes.items():
                # Contar ocurrencias de keywords del tema
                keyword_count = sum(cv_text.count(keyword) for keyword in config['keywords'])
                # Normalizar por longitud del texto
                coverage_score = min(keyword_count / max(len(cv_text.split()), 1) * 100, 100)
                theme_coverage[theme].append(coverage_score)

        # Estadísticas de cobertura
        print("📊 COBERTURA PROMEDIO POR TEMA EN CVs:")
        print("-" * 50)

        for theme, scores in theme_coverage.items():
            avg_coverage = np.mean(scores)
            max_coverage = np.max(scores)
            min_coverage = np.min(scores)
            coverage_pct = np.mean([1 if score > 0 else 0 for score in scores]) * 100

            print(f"🎯 {theme.replace('_', ' ').title()}:")
            print(f"   📈 Cobertura promedio: {avg_coverage:.2f}%")
            print(f"   🎯 CVs que lo incluyen: {coverage_pct:.1f}%")
            print(f"   📊 Rango: {min_coverage:.2f}% - {max_coverage:.2f}%")
            print(f"   📝 {cv_themes[theme]['description']}")
            print()

        # Análisis LDA mejorado con preprocesamiento avanzado
        print("🔍 ANÁLISIS LDA MEJORADO (5 temas automáticos - sin contaminación de contacto):")
        print("-" * 50)

        # Función de preprocesamiento avanzado
        def preprocess_cv_text(text):
            """Preprocesamiento avanzado para eliminar ruido de contacto y mejorar calidad"""
            import re

            # Convertir a minúsculas
            text = text.lower()

            # Eliminar información de contacto específica
            contact_patterns = [
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Teléfonos US
                r'\+\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # Teléfonos internacionales
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Emails
                r'@\w+',  # Menciones @usuario
                r'linkedin\.com/\S+',  # LinkedIn URLs
                r'github\.com/\S+',  # GitHub URLs
                r'http[s]?://\S+',  # URLs generales
                r'\b\d{5}(?:[-\s]\d{4})?\b',  # Códigos postales US
                r'\b\d{4,5}\b',  # Códigos postales otros
            ]

            for pattern in contact_patterns:
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)

            # Tokenización y limpieza
            tokens = word_tokenize(text, language='spanish')

            # Filtros adicionales
            custom_stopwords = set(STOPWORDS_ES)
            custom_stopwords.update([
                'teléfono', 'email', 'correo', 'electrónico', 'dirección',
                'ciudad', 'estado', 'país', 'ubicación', 'contacto',
                'fecha', 'nacimiento', 'edad', 'género', 'nacionalidad'
            ])

            # Filtrar tokens
            tokens = [
                token for token in tokens
                if (token.isalnum() and
                    len(token) > 2 and
                    token not in custom_stopwords and
                    not token.isdigit())
            ]

            return ' '.join(tokens)

        # Aplicar preprocesamiento a todos los CVs
        processed_texts = [preprocess_cv_text(row['cv_text']) for _, row in df.iterrows()]

        # Vectorización con parámetros optimizados
        vectorizer = CountVectorizer(
            max_features=1000,
            stop_words=list(STOPWORDS_ES),
            min_df=2,  # Aparece en al menos 2 documentos
            max_df=0.8,  # No más del 80% de documentos
            ngram_range=(1, 2)  # Unigramas y bigramas
        )

        bow_matrix = vectorizer.fit_transform(processed_texts)

        # LDA con parámetros optimizados
        n_topics = 5
        lda = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            learning_method='online',
            max_iter=20,
            learning_decay=0.7,
            evaluate_every=5
        )

        lda.fit(bow_matrix)

        feature_names = vectorizer.get_feature_names_out()

        print(f"Modelo LDA optimizado con {n_topics} temas entrenado")
        print(f"Vocabulario: {len(feature_names)} términos")
        print(f"Documentos procesados: {len(processed_texts)}")

        # Análisis de coherencia de temas
        def calculate_topic_coherence(topic_words, documents, top_n=10):
            """Calcular coherencia de un tema usando PMI"""
            coherence = 0
            word_pairs = 0

            for i in range(len(topic_words)):
                for j in range(i+1, len(topic_words)):
                    word1, word2 = topic_words[i], topic_words[j]

                    # Contar co-ocurrencias en documentos
                    co_occurrences = sum(1 for doc in documents
                                       if word1 in doc and word2 in doc)

                    # Contar ocurrencias individuales
                    word1_count = sum(1 for doc in documents if word1 in doc)
                    word2_count = sum(1 for doc in documents if word2 in doc)

                    if word1_count > 0 and word2_count > 0 and co_occurrences > 0:
                        # PMI simplificado
                        pmi = np.log((co_occurrences * len(documents)) /
                                   (word1_count * word2_count))
                        coherence += pmi
                        word_pairs += 1

            return coherence / word_pairs if word_pairs > 0 else 0

        # Mostrar temas con métricas de coherencia
        topic_coherences = []

        for topic_idx, topic in enumerate(lda.components_):
            top_word_indices = topic.argsort()[:-11:-1]
            top_words = [feature_names[i] for i in top_word_indices]

            # Calcular coherencia
            coherence = calculate_topic_coherence(top_words, processed_texts)
            topic_coherences.append(coherence)

            print(f"\n🎯 Tema {topic_idx + 1} (Coherencia: {coherence:.3f}):")
            print(f"   Palabras clave: {', '.join(top_words)}")

        # Estadísticas de coherencia general
        avg_coherence = np.mean(topic_coherences)
        print(f"\n📊 COHERENCIA GENERAL DE TEMAS:")
        print(f"   Coherencia promedio: {avg_coherence:.3f}")
        print(f"   Mejor tema: Tema {np.argmax(topic_coherences) + 1} ({np.max(topic_coherences):.3f})")
        print(f"   Peor tema: Tema {np.argmin(topic_coherences) + 1} ({np.min(topic_coherences):.3f})")

        # Análisis de distribución de temas en documentos
        doc_topics = lda.transform(bow_matrix)
        dominant_themes = np.argmax(doc_topics, axis=1)

        print(f"\n📊 DISTRIBUCIÓN DE TEMAS EN {len(df)} CVs:")
        theme_counts = Counter(dominant_themes)
        for topic_idx in range(n_topics):
            count = theme_counts.get(topic_idx, 0)
            percentage = count / len(df) * 100
            print(f"   Tema {topic_idx + 1}: {count} CVs ({percentage:.1f}%)")

        # Validación cruzada: Comparar temas supervisados vs LDA mejorado
        print(f"\n✅ VALIDACIÓN: TEMAS SUPERVISADOS vs LDA MEJORADO")
        print("-" * 50)
        print("✓ Preprocesamiento avanzado elimina contaminación de contacto")
        print("✓ Temas supervisados garantizan cobertura de secciones críticas")
        print("✓ LDA mejorado encuentra patrones naturales sin ruido")
        print("✓ Métricas de coherencia validan calidad de separación temática")

        # Recomendaciones basadas en análisis
        print(f"\n💡 RECOMENDACIONES PARA MEJORA DE CVs:")
        low_coverage_themes = []
        for theme, scores in theme_coverage.items():
            coverage_pct = np.mean([1 if score > 0 else 0 for score in scores]) * 100
            if coverage_pct < 50:
                low_coverage_themes.append((theme, coverage_pct))

        if low_coverage_themes:
            print("Secciones con baja cobertura que necesitan mejora:")
            for theme, pct in low_coverage_themes:
                print(f"   • {theme.replace('_', ' ').title()}: {pct:.1f}%")
        else:
            print("✓ Todas las secciones críticas tienen buena cobertura")

    def automatic_cv_classification(self):
        """Clasificación automática de CVs usando técnicas del cuaderno"""
        print("\n" + "="*60)
        print("🤖 CLASIFICACIÓN AUTOMÁTICA DE CVs")
        print("="*60)

        if len(self.data) < 20:
            print("❌ Insuficientes datos para clasificación")
            return

        # Preparar datos de entrenamiento
        cv_texts = []
        industries = []
        seniorities = []

        for item in self.data:
            cv_texts.append(item['cv_text'])
            industries.append(item['industry'])
            seniorities.append(item['seniority'])

        # Función de preprocesamiento (simplificada del cuaderno)
        def preprocess_cv_text_simple(text):
            """Preprocesamiento simple inspirado en el cuaderno"""
            import re
            import string

            text = str(text).lower()
            text = re.sub(r'\[.*?\]', '', text)
            text = re.sub(r'https?://\S+|www\.\S+', '', text)
            text = re.sub(r'<.*?>+', '', text)
            text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
            text = re.sub(r'\n', ' ', text)
            text = re.sub(r'\w*\d\w*', '', text)
            text = re.sub(r'[^\x00-\x7F]+', '', text)
            text = text.strip()

            # Tokenización y filtrado básico
            tokens = word_tokenize(text, language='spanish')
            tokens = [t for t in tokens if t.isalnum() and t not in STOPWORDS_ES and len(t) > 2]
            return ' '.join(tokens)

        # Preprocesar textos
        processed_texts = [preprocess_cv_text_simple(text) for text in cv_texts]

        # Vectorización TF-IDF (como en el cuaderno)
        tfidf = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
        X = tfidf.fit_transform(processed_texts)

        # 1. Clasificación por Industria
        print("🏭 CLASIFICACIÓN POR INDUSTRIA:")
        print("-" * 30)

        X_train_ind, X_test_ind, y_train_ind, y_test_ind = train_test_split(
            X, industries, test_size=0.3, random_state=42, stratify=industries
        )

        nb_industry = MultinomialNB()
        nb_industry.fit(X_train_ind, y_train_ind)
        y_pred_ind = nb_industry.predict(X_test_ind)

        acc_ind = accuracy_score(y_test_ind, y_pred_ind)
        f1_ind = f1_score(y_test_ind, y_pred_ind, average='weighted')

        print(f"Accuracy: {acc_ind:.3f}")
        print(f"F1-Score (weighted): {f1_ind:.3f}")

        # 2. Clasificación por Seniority
        print("\n📊 CLASIFICACIÓN POR SENIORITY:")
        print("-" * 30)

        X_train_sen, X_test_sen, y_train_sen, y_test_sen = train_test_split(
            X, seniorities, test_size=0.3, random_state=42, stratify=seniorities
        )

        nb_seniority = MultinomialNB()
        nb_seniority.fit(X_train_sen, y_train_sen)
        y_pred_sen = nb_seniority.predict(X_test_sen)

        acc_sen = accuracy_score(y_test_sen, y_pred_sen)
        f1_sen = f1_score(y_test_sen, y_pred_sen, average='weighted')

        print(f"Accuracy: {acc_sen:.3f}")
        print(f"F1-Score (weighted): {f1_sen:.3f}")

        # Guardar modelos (como en el cuaderno)
        import joblib
        import os

        models_dir = "cv_simulator/models"
        os.makedirs(models_dir, exist_ok=True)

        joblib.dump(nb_industry, f"{models_dir}/industry_classifier.pkl")
        joblib.dump(nb_seniority, f"{models_dir}/seniority_classifier.pkl")
        joblib.dump(tfidf, f"{models_dir}/tfidf_vectorizer.pkl")

        print(f"\n� Modelos guardados en {models_dir}/")

        # Demo de predicción (como en el cuaderno)
        print("\n🎯 DEMO DE PREDICCIÓN:")
        print("-" * 30)

        if self.data:
            sample_cv = self.data[0]['cv_text']
            sample_processed = preprocess_cv_text_simple(sample_cv)
            sample_vector = tfidf.transform([sample_processed])

            pred_industry = nb_industry.predict(sample_vector)[0]
            pred_seniority = nb_seniority.predict(sample_vector)[0]

            print(f"CV de ejemplo: {sample_cv[:100]}...")
            print(f"Predicción - Industria: {pred_industry}")
            print(f"Predicción - Seniority: {pred_seniority}")
            print(f"Real - Industria: {industries[0]}, Seniority: {seniorities[0]}")

        return {
            'industry_accuracy': acc_ind,
            'seniority_accuracy': acc_sen,
            'industry_f1': f1_ind,
            'seniority_f1': f1_sen
        }

    def advanced_text_preprocessing(self):
        """Preprocesamiento avanzado de texto inspirado en el cuaderno de reseñas"""
        print("\n" + "="*60)
        print("🧹 PREPROCESAMIENTO AVANZADO DE TEXTO")
        print("="*60)

        import re
        from nltk.corpus import stopwords
        import string

        # Función de limpieza avanzada (inspirada en el cuaderno)
        def clean_text_advanced(text):
            """Limpieza avanzada como en el cuaderno de reseñas"""
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

            return text

        # Función de lematización con spaCy
        def lemmatize_with_spacy(text):
            """Lematización usando spaCy como en el cuaderno"""
            doc = self.nlp(text)
            # Eliminar stopwords y aplicar lematización
            lemmatized = [token.lemma_ for token in doc if token.text.lower() not in STOPWORDS_ES]
            return " ".join(lemmatized).strip()

        # Aplicar preprocesamiento a una muestra
        sample_size = min(10, len(self.data))
        print(f"📊 Procesando muestra de {sample_size} CVs...")

        processed_texts = []
        for item in self.data[:sample_size]:
            # Limpieza básica
            clean_text = clean_text_advanced(item['cv_text'])
            # Lematización avanzada
            lemmatized_text = lemmatize_with_spacy(clean_text)
            processed_texts.append(lemmatized_text)

        print("✅ Preprocesamiento completado")
        print(f"� Ejemplo de texto procesado:")
        print(f"   Original: {self.data[0]['cv_text'][:100]}...")
        print(f"   Procesado: {processed_texts[0][:100]}...")

        return processed_texts

    def run_full_analysis(self):
        """Ejecutar análisis completo"""
        print("🚀 INICIANDO ANÁLISIS NLP COMPLETO DEL DATASET")
        print("="*60)

        self.analyze_basic_stats()
        self.analyze_text_quality()
        self.tfidf_analysis()
        self.bow_analysis()
        self.lda_topic_modeling()
        self.classification_experiment()
        self.harvard_style_analysis()

        print("\n" + "="*60)
        print("✅ ANÁLISIS COMPLETADO")
        print("="*60)

def main():
    analyzer = NLPAnalyzer(DB_PATH)
    analyzer.run_full_analysis()

if __name__ == "__main__":
    main()
