#!/usr/bin/env python3
"""
Demo de Clasificación Automática de CVs
Usa los modelos entrenados para clasificar nuevos CVs
"""

import joblib
import os
import sys
import re
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Configuración
STOPWORDS_ES = set(stopwords.words('spanish')) if 'spanish' in stopwords.fileids() else set()
MODELS_DIR = "cv_simulator/models"

def load_models():
    """Cargar modelos entrenados"""
    try:
        industry_clf = joblib.load(f"{MODELS_DIR}/industry_classifier.pkl")
        seniority_clf = joblib.load(f"{MODELS_DIR}/seniority_classifier.pkl")
        vectorizer = joblib.load(f"{MODELS_DIR}/tfidf_vectorizer.pkl")
        print("✅ Modelos cargados exitosamente")
        return industry_clf, seniority_clf, vectorizer
    except FileNotFoundError:
        print("❌ Modelos no encontrados. Ejecuta primero nlp_analysis.py")
        return None, None, None

def preprocess_cv_text_simple(text):
    """Preprocesamiento simple (igual que en el entrenamiento)"""
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

def classify_cv(cv_text, industry_clf, seniority_clf, vectorizer):
    """Clasificar un CV usando los modelos entrenados"""
    # Preprocesar
    processed_text = preprocess_cv_text_simple(cv_text)

    # Vectorizar
    vector = vectorizer.transform([processed_text])

    # Predecir
    pred_industry = industry_clf.predict(vector)[0]
    pred_seniority = seniority_clf.predict(vector)[0]

    # Probabilidades
    prob_industry = industry_clf.predict_proba(vector)[0]
    prob_seniority = seniority_clf.predict_proba(vector)[0]

    industry_classes = industry_clf.classes_
    seniority_classes = seniority_clf.classes_

    return {
        'industry': pred_industry,
        'seniority': pred_seniority,
        'industry_probs': dict(zip(industry_classes, prob_industry)),
        'seniority_probs': dict(zip(seniority_classes, prob_seniority))
    }

def demo_classification():
    """Demo de clasificación con ejemplos"""
    print("🎯 DEMO DE CLASIFICACIÓN AUTOMÁTICA DE CVs")
    print("="*60)

    # Cargar modelos
    industry_clf, seniority_clf, vectorizer = load_models()
    if not industry_clf:
        return

    # Ejemplos de CVs
    cv_examples = [
        {
            'title': 'CV de Data Scientist Senior',
            'text': '''
NOMBRE: Ana López
EXPERIENCIA PROFESIONAL
DATA SCIENTIST SENIOR | TECH CORP | 2019 - PRESENTE
- Desarrollo modelos de machine learning con Python y TensorFlow
- Análisis de datos masivos con Spark y Hadoop
- Implementación de pipelines de datos automatizados

EDUCACIÓN
LICENCIATURA EN CIENCIA DE DATOS PARA NEGOCIOS | UACM | 2015 - 2019

HABILIDADES
Python, R, SQL, Machine Learning, TensorFlow, Pandas, Scikit-learn
            '''
        },
        {
            'title': 'CV de Ingeniero de Software Junior',
            'text': '''
NOMBRE: Carlos Ruiz
EXPERIENCIA PROFESIONAL
DESARROLLADOR JUNIOR | STARTUP TECH | 2022 - PRESENTE
- Desarrollo de aplicaciones web con React y Node.js
- Implementación de APIs REST
- Trabajo con bases de datos SQL

EDUCACIÓN
INGENIERÍA EN SISTEMAS COMPUTACIONALES | UNAM | 2018 - 2022

HABILIDADES
JavaScript, React, Node.js, SQL, Git, Docker
            '''
        },
        {
            'title': 'CV de Gerente de Marketing',
            'text': '''
NOMBRE: María González
EXPERIENCIA PROFESIONAL
GERENTE DE MARKETING | AGENCIA DIGITAL | 2015 - PRESENTE
- Dirección de campañas de marketing digital
- Gestión de equipos creativos
- Análisis de ROI y métricas de performance

EDUCACIÓN
LICENCIATURA EN MERCADOTECNIA | ITESM | 2010 - 2014

HABILIDADES
Google Analytics, SEO/SEM, Social Media, Content Marketing, Adobe Suite
            '''
        }
    ]

    for i, example in enumerate(cv_examples, 1):
        print(f"\n📄 EJEMPLO {i}: {example['title']}")
        print("-" * 40)

        # Clasificar
        result = classify_cv(example['text'], industry_clf, seniority_clf, vectorizer)

        print(f"🏭 Industria predicha: {result['industry']}")
        print(f"📊 Seniority predicho: {result['seniority']}")

        print("\n🎯 Probabilidades de Industria:")
        for industry, prob in sorted(result['industry_probs'].items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"  {industry}: {prob:.3f}")

        print("\n📈 Probabilidades de Seniority:")
        for seniority, prob in sorted(result['seniority_probs'].items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"  {seniority}: {prob:.3f}")
        print("-" * 40)

def interactive_classification():
    """Clasificación interactiva de CVs"""
    print("💬 CLASIFICACIÓN INTERACTIVA DE CVs")
    print("="*60)
    print("Ingresa el texto de un CV (o 'salir' para terminar):")
    print()

    # Cargar modelos
    industry_clf, seniority_clf, vectorizer = load_models()
    if not industry_clf:
        return

    while True:
        cv_text = input("CV > ")
        if cv_text.lower() in ['salir', 'exit', 'quit']:
            break

        if len(cv_text.strip()) < 50:
            print("⚠️ El texto es muy corto. Ingresa al menos 50 caracteres.")
            continue

        # Clasificar
        result = classify_cv(cv_text, industry_clf, seniority_clf, vectorizer)

        print("\n🔍 RESULTADO:")
        print(f"🏭 Industria: {result['industry']}")
        print(f"📊 Seniority: {result['seniority']}")
        print()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_classification()
    else:
        demo_classification()
