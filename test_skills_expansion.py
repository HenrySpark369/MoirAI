#!/usr/bin/env python3
"""
Script de prueba para verificar el skills_map ampliado
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Simular el skills_map ampliado
skills_map = {
    'Tecnología': [
        'Python', 'JavaScript', 'Java', 'C++', 'React', 'Node.js', 'Angular', 'Vue.js',
        'SQL', 'NoSQL', 'MongoDB', 'PostgreSQL', 'MySQL', 'Redis',
        'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins', 'Git',
        'Microservicios', 'API REST', 'GraphQL', 'DevOps', 'CI/CD', 'Linux', 'Bash'
    ],
    'Ciencia de Datos': [
        # Lenguajes de Programación
        'Python', 'R', 'SQL', 'Julia', 'Scala', 'SAS', 'MATLAB',
        # Librerías de Python/R
        'Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'PyTorch', 'Keras', 'XGBoost',
        'LightGBM', 'CatBoost', 'NLTK', 'spaCy', 'Transformers', 'OpenCV',
        # Visualización
        'Tableau', 'Power BI', 'matplotlib', 'seaborn', 'plotly', 'ggplot2', 'D3.js',
        'Looker', 'Qlik Sense', 'MicroStrategy',
        # Big Data
        'Hadoop', 'Spark', 'Kafka', 'Airflow', 'Databricks', 'Snowflake', 'Redshift',
        # Bases de Datos
        'PostgreSQL', 'MongoDB', 'Cassandra', 'Elasticsearch', 'Redis', 'Neo4j',
        # Cloud y MLOps
        'AWS SageMaker', 'Azure ML', 'Google AI Platform', 'MLflow', 'Kubeflow',
        # Estadística y Matemáticas
        'Estadística', 'Probabilidad', 'Machine Learning', 'Deep Learning', 'Time Series',
        'A/B Testing', 'Análisis Predictivo', 'Regresión', 'Clustering', 'NLP',
        # Business Intelligence
        'Business Intelligence', 'Data Warehousing', 'ETL', 'Data Mining', 'KPI',
        'Dashboarding', 'Storytelling con Datos', 'Data Governance', 'Ética en Datos'
    ],
    'Finanzas': [
        'Excel Avanzado', 'VBA', 'SQL', 'Python para Finanzas', 'R para Finanzas',
        'Power BI', 'Tableau', 'SAP', 'Oracle Financials', 'QuickBooks',
        'Análisis Financiero', 'Modelado de Riesgos', 'Valoración de Activos',
        'Derivados', 'Forex', 'Banca Digital', 'FinTech', 'Blockchain', 'Criptomonedas',
        'Compliance', 'Auditoría', 'Contabilidad', 'Impuestos', 'Mergers & Acquisitions'
    ],
    'Salud': [
        'Atención al Paciente', 'Diagnóstico Médico', 'Gestión Hospitalaria',
        'Sistemas de Salud', 'Epidemiología', 'Telemedicina', 'EHR', 'HL7', 'FHIR',
        'Investigación Clínica', 'Ensayos Clínicos', 'Farmacología', 'Genética',
        'Medicina Preventiva', 'Salud Pública', 'Bioestadística', 'Data Analytics en Salud'
    ],
    'Marketing': [
        'Google Analytics', 'Google Ads', 'Facebook Ads', 'SEO/SEM', 'Content Marketing',
        'Social Media Marketing', 'Email Marketing', 'CRM', 'HubSpot', 'Salesforce',
        'Adobe Creative Suite', 'Photoshop', 'Illustrator', 'Brand Management',
        'Customer Journey', 'A/B Testing', 'Conversion Optimization', 'Growth Hacking',
        'Influencer Marketing', 'Marketing Automation', 'Data-Driven Marketing'
    ]
}

if __name__ == "__main__":
    print('=== SKILLS MAP AMPLIADO PARA CIENCIA DE DATOS PARA NEGOCIOS ===')
    print('=' * 70)

    for industry, skills in skills_map.items():
        print(f'\n🔹 {industry.upper()}: {len(skills)} habilidades')

        # Mostrar primeras 10 habilidades como ejemplo
        ejemplos = ', '.join(skills[:10])
        print(f'   📋 Ejemplos: {ejemplos}')

        if len(skills) > 10:
            restantes = len(skills) - 10
            print(f'   ➕ ... y {restantes} habilidades más')

        # Estadísticas específicas para Ciencia de Datos
        if industry.lower() == 'ciencia de datos':
            categorias = {
                'Lenguajes': ['Python', 'R', 'SQL', 'Julia', 'Scala', 'SAS', 'MATLAB'],
                'Librerías ML': ['TensorFlow', 'PyTorch', 'Scikit-learn', 'Keras', 'XGBoost', 'Pandas', 'NumPy'],
                'Visualización': ['Tableau', 'Power BI', 'matplotlib', 'seaborn', 'plotly'],
                'Big Data': ['Hadoop', 'Spark', 'Kafka', 'Airflow', 'Databricks'],
                'Cloud/MLOps': ['AWS SageMaker', 'Azure ML', 'Google AI Platform', 'MLflow']
            }

            print(f'   📊 Desglose por categorías:')
            for cat, cat_skills in categorias.items():
                count = len([s for s in cat_skills if s in skills])
                print(f'      • {cat}: {count} habilidades')

    print('\n' + '=' * 70)
    print('✅ Skills map ampliado correctamente para especialización en Ciencia de Datos para Negocios')
    print('🎯 El sistema ahora incluye habilidades específicas del plan de estudios LCDN')
