import openai
import json
import sqlite3
import time
import uuid
import os
import sys

# Configuración para LM Studio Local
API_BASE_URL = "http://127.0.0.1:1234/v1"
API_KEY = "lm-studio" # Clave dummy

client = openai.OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY
)

def get_active_model():
    """Obtiene el modelo cargado actualmente en LM Studio"""
    try:
        models = client.models.list()
        if models.data:
            # Retorna el primer modelo activo (LM Studio suele tener uno cargado)
            model_id = models.data[0].id
            print(f"🔌 Modelo detectado: {model_id}")
            return model_id
        else:
            print("⚠️ No se detectaron modelos cargados en LM Studio.")
            return "local-model" # Fallback genérico
    except Exception as e:
        print(f"⚠️ Error conectando a LM Studio: {e}")
        return "local-model"

# Detectar modelo al inicio
MODEL_ID = get_active_model()

# 1. Preparar Base de Datos
DB_PATH = 'cv_simulator/training_data_cvs.db'
# Asegurar que el directorio existe si se corre desde root
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS cv_dataset (
        id TEXT PRIMARY KEY,
        industry TEXT,
        seniority TEXT,
        cv_text TEXT,
        annotations JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# Configuración de Distribución Uniforme
TARGET_DISTRIBUTION = {
    'industries': {
        'Tecnología': 0.12,
        'Ciencia de Datos': 0.15,
        'Finanzas': 0.12,
        'Salud': 0.12,
        'Biotecnología': 0.10,
        'FinTech': 0.08,
        'Healthcare': 0.08,
        'Marketing': 0.08,
        'Legal': 0.07,
        'Construcción': 0.06,
        'Educación': 0.06,
        'Retail': 0.05,
        'Manufactura': 0.01
    },
    'seniorities': {
        'Junior': 0.20,
        'Mid-Level': 0.35,
        'Senior': 0.30,
        'Lead': 0.10,
        'Manager': 0.03,
        'Director': 0.02
    },
    'genders': {
        'Masculino': 0.50,
        'Femenino': 0.50
    },
    'universities': {
        'UNAM': 0.23,
        'IPN': 0.18,
        'UAM': 0.15,
        'UNRC': 0.14,
        'UACM': 0.07,
        'Otros': 0.16
    }
}

class DistributionTracker:
    """Clase para rastrear y balancear la distribución de categorías"""

    def __init__(self, target_dist):
        self.target = target_dist
        self.current = {cat: {subcat: 0 for subcat in subcats.keys()}
                       for cat, subcats in target_dist.items()}
        self.total_per_category = {cat: 0 for cat in target_dist.keys()}

    def update(self, category, subcategory):
        """Actualizar contador para una categoría"""
        if category in self.current and subcategory in self.current[category]:
            self.current[category][subcategory] += 1
            self.total_per_category[category] += 1

    def get_distribution_weights(self, category):
        """Calcular pesos para favorecer categorías subrepresentadas"""
        if category not in self.current:
            return {}

        total = self.total_per_category[category]
        if total == 0:
            return {subcat: 1.0 for subcat in self.current[category].keys()}

        weights = {}
        for subcat in self.current[category]:
            current_ratio = self.current[category][subcat] / total
            target_ratio = self.target[category].get(subcat, 0.1)

            # Calcular peso: favorecer subrepresentadas
            if current_ratio < target_ratio:
                # Subrepresentada: aumentar peso
                deficit = target_ratio - current_ratio
                weights[subcat] = 1.0 + (deficit * 2.0)  # Multiplicador
            else:
                # Sobre-representada: reducir peso
                excess = current_ratio - target_ratio
                weights[subcat] = max(0.1, 1.0 - (excess * 1.5))  # Mínimo 0.1

        return weights

    def get_weighted_choice(self, category):
        """Seleccionar categoría basada en pesos"""
        weights = self.get_distribution_weights(category)
        if not weights:
            return list(self.current[category].keys())[0]

        # Normalizar pesos
        total_weight = sum(weights.values())
        normalized_weights = {k: v/total_weight for k, v in weights.items()}

        # Selección ponderada
        import random
        rand = random.random()
        cumulative = 0.0

        for subcat, weight in normalized_weights.items():
            cumulative += weight
            if rand <= cumulative:
                return subcat

        return list(weights.keys())[-1]  # Fallback

    def get_stats(self):
        """Obtener estadísticas actuales de distribución"""
        stats = {}
        for category in self.current:
            total = self.total_per_category[category]
            if total > 0:
                stats[category] = {
                    subcat: {
                        'count': count,
                        'percentage': (count / total) * 100,
                        'target': self.target[category].get(subcat, 0) * 100
                    }
                    for subcat, count in self.current[category].items()
                }
        return stats

    def print_balance_report(self):
        """Imprimir reporte de balance de distribución"""
        print("\n📊 REPORTE DE BALANCE DE DISTRIBUCIÓN:")
        print("=" * 50)

        for category, subcats in self.get_stats().items():
            print(f"\n🔹 {category.upper()}:")
            sorted_subcats = sorted(subcats.items(),
                                  key=lambda x: x[1]['count'],
                                  reverse=True)

            for subcat, data in sorted_subcats:
                status = "✅" if abs(data['percentage'] - data['target']) < 5 else "⚠️"
                print(f"  {status} {subcat}: {data['count']} ({data['percentage']:.1f}% | Target: {data['target']:.1f}%)")

# Instancia global del tracker
distribution_tracker = DistributionTracker(TARGET_DISTRIBUTION)

# Configuración global
OBJETIVO = 100

def generate_dynamic_prompt():
    """Generar prompt dinámico basado en distribución actual con COHERENCIA TOTAL"""

    # Obtener categorías favorecidas
    industry_weights = distribution_tracker.get_distribution_weights('industries')
    seniority_weights = distribution_tracker.get_distribution_weights('seniorities')

    # Crear listas ordenadas por peso (descendente)
    favored_industries = sorted(industry_weights.keys(),
                               key=lambda x: industry_weights[x],
                               reverse=True)[:5]  # Top 5

    favored_seniorities = sorted(seniority_weights.keys(),
                                key=lambda x: seniority_weights[x],
                                reverse=True)[:4]  # Top 4

    # Mapas de coherencia por industria
    industry_requirements = {
        'Tecnología': {
            'universities': ['UNAM (Ingeniería en Sistemas)', 'IPN (Ingeniería en Computación)', 'ITESM (Ingeniería en Tecnologías de Información)', 'UAM (Ingeniería en Software)', 'UACM (Ciencia de Datos para Negocios)'],
            'degrees': ['Ingeniería en Sistemas Computacionales', 'Ingeniería en Software', 'Licenciatura en Informática', 'Ingeniería en Tecnologías de la Información', 'Licenciatura en Ciencia de Datos para Negocios'],
            'skills': ['Python', 'JavaScript', 'Java', 'React', 'Node.js', 'SQL', 'AWS', 'Docker', 'Git', 'Machine Learning', 'DevOps', 'R', 'TensorFlow', 'Pandas', 'NumPy', 'Tableau', 'Power BI'],
            'experience_years': {'Junior': '1-3', 'Mid-Level': '3-5', 'Senior': '5-8', 'Lead': '8-12', 'Manager': '10-15', 'Director': '15+'},
            'companies': ['Tech Solutions', 'Digital Innovation', 'Software House', 'Cloud Systems', 'DataTech', 'WebDev Corp', 'Data Analytics Corp', 'Business Intelligence Solutions'],
            'positions': {'Junior': ['Desarrollador Junior', 'Analista de Sistemas', 'Analista de Datos Junior'], 'Mid-Level': ['Desarrollador Senior', 'Ingeniero de Software', 'Científico de Datos'], 'Senior': ['Senior Developer', 'Tech Lead', 'Senior Data Scientist'], 'Lead': ['Lead Developer', 'Arquitecto de Software', 'Lead Data Scientist'], 'Manager': ['Gerente de Desarrollo', 'Scrum Master', 'Gerente de Analytics'], 'Director': ['Director de Tecnología', 'CTO', 'Director de Data Science']}
        },
        'Ciencia de Datos': {
            'universities': ['UACM (Ciencia de Datos para Negocios)', 'UNAM (Matemáticas Aplicadas)', 'IPN (Estadística)', 'ITESM (Tecnologías de Información)', 'UDLAP (Negocios Digitales)'],
            'degrees': ['Licenciatura en Ciencia de Datos para Negocios', 'Licenciatura en Matemáticas Aplicadas', 'Licenciatura en Estadística', 'Ingeniería en Datos', 'Licenciatura en Analytics'],
            'skills': ['Python', 'R', 'SQL', 'Machine Learning', 'Deep Learning', 'Big Data', 'Hadoop', 'Spark', 'TensorFlow', 'Pandas', 'NumPy', 'Scikit-learn', 'Tableau', 'Power BI', 'Excel Avanzado', 'A/B Testing', 'Análisis Predictivo', 'NLP', 'Computer Vision', 'Time Series Analysis'],
            'experience_years': {'Junior': '1-3', 'Mid-Level': '3-5', 'Senior': '5-8', 'Lead': '8-12', 'Manager': '10-15', 'Director': '15+'},
            'companies': ['Data Analytics Corp', 'Business Intelligence Solutions', 'Predictive Analytics Inc', 'Big Data Systems', 'AI Solutions', 'Data-Driven Consulting', 'Analytics Partners'],
            'positions': {'Junior': ['Analista de Datos Junior', 'Data Analyst I', 'Business Analyst'], 'Mid-Level': ['Científico de Datos', 'Data Engineer', 'Analytics Manager'], 'Senior': ['Senior Data Scientist', 'Lead Analyst', 'Data Architect'], 'Lead': ['Principal Data Scientist', 'Head of Analytics', 'Data Science Lead'], 'Manager': ['Gerente de Data Science', 'Director de Analytics', 'Chief Data Officer'], 'Director': ['Director de Data Science', 'VP of Analytics', 'Chief Analytics Officer']}
        },
        'Finanzas': {
            'universities': ['UNAM (Economía)', 'ITESM (Finanzas)', 'UDLAP (Administración)', 'UAM (Contaduría)'],
            'degrees': ['Licenciatura en Economía', 'Licenciatura en Finanzas', 'Contaduría Pública', 'Administración de Empresas'],
            'skills': ['Excel Avanzado', 'SQL', 'Python para Finanzas', 'Power BI', 'SAP', 'Análisis Financiero', 'Modelado Riesgos', 'Banca Digital'],
            'experience_years': {'Junior': '1-3', 'Mid-Level': '3-6', 'Senior': '6-10', 'Lead': '10-15', 'Manager': '12-18', 'Director': '18+'},
            'companies': ['Banco Nacional', 'Finanzas Globales', 'Investment Corp', 'Capital Advisors', 'Asset Management', 'Banca Digital'],
            'positions': {'Junior': ['Analista Financiero Junior', 'Asistente Contable'], 'Mid-Level': ['Analista Senior', 'Contador'], 'Senior': ['Senior Financial Analyst', 'Gerente de Riesgos'], 'Lead': ['Lead Analyst', 'Controller'], 'Manager': ['Gerente Financiero', 'Director de Finanzas'], 'Director': ['Director Financiero', 'CFO']}
        },
        'Salud': {
            'universities': ['UNAM (Medicina)', 'BUAP (Enfermería)', 'UDLAP (Psicología)', 'UASLP (Fisioterapia)'],
            'degrees': ['Medicina', 'Enfermería', 'Psicología', 'Fisioterapia', 'Nutrición', 'Farmacia'],
            'skills': ['Atención al Paciente', 'Diagnóstico Médico', 'Gestión Hospitalaria', 'Sistemas de Salud', 'Epidemiología', 'Telemedicina'],
            'experience_years': {'Junior': '1-3', 'Mid-Level': '3-6', 'Senior': '6-10', 'Lead': '10-15', 'Manager': '12-18', 'Director': '18+'},
            'companies': ['Hospital Central', 'Clínica Universitaria', 'Centro Médico', 'Instituto de Salud', 'Hospital General', 'Clínica Especializada'],
            'positions': {'Junior': ['Enfermero/a', 'Técnico Médico'], 'Mid-Level': ['Enfermero/a Senior', 'Especialista Médico'], 'Senior': ['Supervisor Médico', 'Coordinador de Área'], 'Lead': ['Jefe de Servicio', 'Especialista Senior'], 'Manager': ['Gerente Médico', 'Director de Departamento'], 'Director': ['Director Médico', 'Director General']}
        },
        'Marketing': {
            'universities': ['ITESM (Mercadotecnia)', 'UDLAP (Comunicación)', 'UNAM (Publicidad)', 'UAM (Marketing Digital)'],
            'degrees': ['Licenciatura en Mercadotecnia', 'Comunicación', 'Publicidad', 'Marketing Digital', 'Diseño Gráfico'],
            'skills': ['Google Analytics', 'SEO/SEM', 'Social Media', 'Adobe Creative Suite', 'Content Marketing', 'Brand Management', 'CRM'],
            'experience_years': {'Junior': '1-3', 'Mid-Level': '3-5', 'Senior': '5-8', 'Lead': '8-12', 'Manager': '10-15', 'Director': '15+'},
            'companies': ['Marketing Solutions', 'Brand Agency', 'Digital Media', 'Advertising Corp', 'Content Creators', 'E-commerce Marketing'],
            'positions': {'Junior': ['Ejecutivo de Cuentas', 'Asistente de Marketing'], 'Mid-Level': ['Especialista en Marketing', 'Coordinador Digital'], 'Senior': ['Senior Marketing Manager', 'Brand Manager'], 'Lead': ['Lead Marketing', 'Director de Marca'], 'Manager': ['Gerente de Marketing', 'Director de Campañas'], 'Director': ['Director de Marketing', 'CMO']}
        }
    }

    # Seleccionar seniority e industry específicos para favorecer
    selected_seniority = distribution_tracker.get_weighted_choice('seniorities')
    selected_industry = distribution_tracker.get_weighted_choice('industries')

    # Mapas de experiencia por seniority
    experience_map = {
        'Junior': '2 años',
        'Mid-Level': '4 años', 
        'Senior': '7 años',
        'Lead': '10 años',
        'Manager': '15 años',
        'Director': '20 años'
    }

    # Mapas de skills por industria
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

    # Mapas de carreras por industria
    degree_map = {
        'Tecnología': 'Ingeniería en Sistemas',
        'Ciencia de Datos': 'Licenciatura en Ciencia de Datos para Negocios',
        'Finanzas': 'Licenciatura en Economía',
        'Salud': 'Medicina',
        'Marketing': 'Licenciatura en Mercadotecnia'
    }

    # Prompt Maestro ULTRA-ESPECÍFICO
    prompt = f"""
Genera 1 perfil profesional mexicano en JSON puro.

DATOS ESPECÍFICOS (USA EXACTAMENTE ESTOS VALORES):
- Industria: {selected_industry}
- Seniority: {selected_seniority}
- Experiencia: {experience_map[selected_seniority]}
- Skills: {', '.join(skills_map.get(selected_industry, ['Genéricas'])[:3])}
- Universidad: UNAM
- Carrera: {degree_map.get(selected_industry, 'Profesional')}
- Ubicación: Ciudad de México
- Idiomas: Español, Inglés

INSTRUCCIONES:
- El cv_text DEBE mencionar exactamente "{experience_map[selected_seniority]}" de experiencia
- Los annotations.experience DEBEN tener exactamente {experience_map[selected_seniority].split()[0]} entradas (una por año)
- NO cambies los valores especificados arriba

FORMATO JSON EXACTO:
{{
  "metadata": {{"industry": "{selected_industry}", "seniority": "{selected_seniority}"}},
  "cv_text": "NOMBRE: Juan Pérez\\nEXPERIENCIA: {experience_map[selected_seniority]} en {selected_industry}\\nHABILIDADES: {', '.join(skills_map.get(selected_industry, ['Genéricas'])[:3])}\\n...",
  "annotations": {{
    "name": "Juan Pérez",
    "education": [{{"institution": "UNAM", "degree": "{degree_map.get(selected_industry, 'Profesional')}"}}],
    "experience": [{{"position": "{selected_seniority} {selected_industry}", "company": "Empresa Mexicana"}}],
    "skills": {skills_map.get(selected_industry, ['Genéricas'])[:3]},
    "location": "Ciudad de México",
    "languages": ["Español", "Inglés"]
  }}
}}
"""

    return prompt

def generate_batch_profiles():
    """Generar lote de 5 perfiles usando el Prompt Maestro del otro LLM"""
    try:
        # Obtener todas las industrias y seniorities del target distribution
        all_industries = list(TARGET_DISTRIBUTION['industries'].keys())
        all_seniorities = list(TARGET_DISTRIBUTION['seniorities'].keys())

        # Prompt Maestro del otro LLM (adaptado con TODAS las categorías)
        prompt_maestro = f"""
Genera 5 objetos JSON únicos. Cada objeto debe representar un perfil profesional completamente ficticio y distinto (diferente industria, nivel de seniority, género, nacionalidad y universidad).

Reglas de Estocasticidad (Variabilidad):
1. Industria: Elige aleatoriamente entre {', '.join(all_industries)}.
2. Nivel: Varía entre {', '.join(all_seniorities)}.
3. Estilo: El campo cv_text debe ser un Currículum en "Estilo Harvard" (texto plano, sobrio, orientado a logros, sin columnas, uso de bullet points).
4. Idioma: Español.
5. Especialización: Para Ciencia de Datos, enfatizar habilidades técnicas como Python, R, Machine Learning, análisis predictivo y visualización de datos.

Formato de Salida (JSON Array estricto):
No incluyas texto introductorio ni markdown (```json). Devuelve SOLO la lista de objetos con esta estructura exacta:

[
  {{
    "metadata": {{
      "industry": "Finanzas",
      "seniority": "Senior",
      "profile_id": "uuid_simulado"
    }},
    "cv_text": "NOMBRE: Ana López\\nTELÉFONO: 555-0199\\nEMAIL: ana.lopez@email.com\\n\\nEXPERIENCIA PROFESIONAL\\n\\nCIENTÍFICO DE DATOS SENIOR | PREDICTIVE ANALYTICS INC | 2019 - PRESENTE\\n- Desarrollé modelos de machine learning que aumentaron la precisión predictiva en un 35%.\\n- Implementé pipelines de datos automatizados procesando 10TB de datos diarios.\\n- Lideré equipo de 4 data scientists en proyectos de análisis predictivo.\\n\\nEDUCACIÓN\\n\\nLICENCIATURA EN CIENCIA DE DATOS PARA NEGOCIOS | UACM | 2015 - 2019\\n- Graduada con mención honorífica.\\n- Proyecto final: Sistema de recomendación basado en machine learning.",
    "annotations": {{
      "name": "Ana López",
      "email": "ana.lopez@email.com",
      "current_role": "Científico de Datos Senior",
      "years_experience": 7,
      "degree": "Licenciatura en Ciencia de Datos para Negocios",
      "university": "UACM",
      "skills": ["Python", "Machine Learning", "SQL", "Tableau", "TensorFlow"]
    }}
  }}
]
"""

        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": "Eres un generador de datos sintéticos experto en Recursos Humanos y NLP. Tu tarea es generar datos de entrenamiento de alta variabilidad."},
                {"role": "user", "content": prompt_maestro}
            ],
            temperature=0.9,  # ALTO para máxima creatividad/estocasticidad
            max_tokens=2000,
            timeout=120,
            stream=False
        )

        content = response.choices[0].message.content
        content = content.replace("```json", "").replace("```", "").strip()

        try:
            batch = json.loads(content)
            if isinstance(batch, list):
                return batch
            else:
                return [batch]  # Si devuelve un solo objeto
        except json.JSONDecodeError as e:
            print(f"❌ Error decodificando JSON del lote: {e}")
            print(f"Contenido: {content[:300]}...")
            return []

    except Exception as e:
        print(f"❌ Error generando lote: {e}")
        return []

def load_existing_distribution():
    """Cargar distribución existente desde la base de datos"""
    try:
        cursor.execute("SELECT industry, seniority FROM cv_dataset")
        rows = cursor.fetchall()

        for industry, seniority in rows:
            if industry and industry != 'Unknown':
                distribution_tracker.update('industries', industry)
            if seniority and seniority != 'Unknown':
                distribution_tracker.update('seniorities', seniority)

        print(f"📊 Cargada distribución existente: {len(rows)} registros")
        distribution_tracker.print_balance_report()

    except Exception as e:
        print(f"⚠️ Error cargando distribución existente: {e}")

def generate_profile():
    try:
        # Generar prompt dinámico basado en distribución actual
        current_prompt = generate_dynamic_prompt()

        print(f"⏳ Solicitando perfil al modelo {MODEL_ID}...")
        start_time = time.time()

        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": current_prompt}
            ],
            temperature=0.8,  # Reducido para más consistencia
            max_tokens=1200,  # Reducido para modelo local
            timeout=60,
            stream=False
        )

        duration = time.time() - start_time
        print(f"✅ Respuesta recibida en {duration:.2f}s")

        content = response.choices[0].message.content
        content = content.replace("```json", "").replace("```", "").strip()

        try:
            data = json.loads(content)
            # Si el modelo devuelve lista por error, tomamos el primero
            if isinstance(data, list):
                return data[0] if data else None
            return data
        except json.JSONDecodeError as e:
            print("❌ Error decodificando JSON.")
            print(f"Contenido recibido: {content[:500]}...")  # Mostrar primeros 500 caracteres
            print(f"Error específico: {e}")
            return None

    except Exception as e:
        print(f"❌ Error generando perfil: {e}")
        return None

def validate_profile_coherence(profile):
    """Validar que todos los atributos del perfil sean coherentes entre sí"""
    issues = []

    try:
        metadata = profile.get('metadata', {})
        annotations = profile.get('annotations', {})

        # Buscar industry y seniority en metadata primero, luego en annotations (para compatibilidad con perfiles antiguos)
        industry = metadata.get('industry') or annotations.get('industry', '')
        seniority = metadata.get('seniority') or annotations.get('seniority', '')

        if not industry or not seniority:
            issues.append("Faltan industry o seniority en metadata/annotations")
            return issues

        # 1. Validar educación
        education = annotations.get('education', [])
        if education:
            edu = education[0]  # Tomar primera educación
            institution = edu.get('institution', '').lower()
            degree = edu.get('degree', '').lower()

            # Verificar universidades mexicanas
            mexican_universities = ['unam', 'ipn', 'uam', 'itesm', 'udlap', 'buap', 'uaslp', 'udem']
            if not any(uni in institution for uni in mexican_universities):
                issues.append(f"Universidad no mexicana: {institution}")

            # Verificar coherencia carrera-industria
            industry_keywords = {
                'tecnología': ['ingeniería', 'sistemas', 'computación', 'software', 'informática'],
                'ciencia de datos': ['ciencia de datos', 'matemáticas aplicadas', 'estadística', 'analytics', 'datos'],
                'finanzas': ['economía', 'finanzas', 'contaduría', 'administración', 'negocios'],
                'salud': ['medicina', 'enfermería', 'psicología', 'fisioterapia', 'nutrición'],
                'marketing': ['mercadotecnia', 'comunicación', 'publicidad', 'marketing', 'diseño']
            }

            industry_lower = industry.lower()
            if industry_lower in industry_keywords:
                if not any(keyword in degree for keyword in industry_keywords[industry_lower]):
                    issues.append(f"Carrera '{degree}' no coherente con industria '{industry}'")

        # 2. Validar experiencia
        experience = annotations.get('experience', [])
        total_years = len(experience)

        # Para perfiles generados con el nuevo sistema, esperamos experiencia específica
        expected_years = {
            'Junior': 2,
            'Mid-Level': 4,
            'Senior': 7,
            'Lead': 10,
            'Manager': 15,
            'Director': 20
        }

        seniority_lower = seniority.lower()
        if seniority in expected_years:
            expected = expected_years[seniority]
            if total_years != expected:
                issues.append(f"Experiencia ({total_years} años) no coherente con seniority '{seniority}' (esperado: {expected})")
        else:
            # Fallback para seniority no mapeado
            seniority_years = {
                'junior': (0, 3),
                'mid-level': (3, 6),
                'senior': (5, 10),
                'lead': (8, 15),
                'manager': (10, 20),
                'director': (15, 30)
            }
            if seniority_lower in seniority_years:
                min_years, max_years = seniority_years[seniority_lower]
                if total_years < min_years or total_years > max_years:
                    issues.append(f"Experiencia ({total_years} años) no coherente con seniority '{seniority}' (esperado: {min_years}-{max_years})")

        # 3. Validar habilidades técnicas
        skills = annotations.get('skills', [])
        if skills:
            # Verificar que las habilidades sean técnicas y relevantes
            industry_tech_skills = {
                'tecnología': ['python', 'javascript', 'java', 'c++', 'react', 'node.js', 'angular', 'vue.js', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis', 'aws', 'azure', 'google cloud', 'docker', 'kubernetes', 'jenkins', 'git', 'microservicios', 'api rest', 'graphql', 'devops', 'ci/cd', 'linux', 'bash'],
                'ciencia de datos': ['python', 'r', 'sql', 'julia', 'scala', 'sas', 'matlab', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'xgboost', 'lightgbm', 'catboost', 'nltk', 'spacy', 'transformers', 'opencv', 'tableau', 'power bi', 'matplotlib', 'seaborn', 'plotly', 'ggplot2', 'd3.js', 'looker', 'qlik sense', 'microstrategy', 'hadoop', 'spark', 'kafka', 'airflow', 'databricks', 'snowflake', 'redshift', 'postgresql', 'mongodb', 'cassandra', 'elasticsearch', 'redis', 'neo4j', 'aws sagemaker', 'azure ml', 'google ai platform', 'mlflow', 'kubeflow', 'estadística', 'probabilidad', 'machine learning', 'deep learning', 'time series', 'a/b testing', 'análisis predictivo', 'regresión', 'clustering', 'nlp', 'business intelligence', 'data warehousing', 'etl', 'data mining', 'kpi', 'dashboarding', 'storytelling con datos', 'data governance', 'ética en datos'],
                'finanzas': ['excel', 'vba', 'sql', 'python', 'r', 'power bi', 'tableau', 'sap', 'oracle financials', 'quickbooks', 'análisis financiero', 'modelado de riesgos', 'valoración de activos', 'derivados', 'forex', 'banca digital', 'fintech', 'blockchain', 'criptomonedas', 'compliance', 'auditoría', 'contabilidad', 'impuestos', 'mergers & acquisitions'],
                'salud': ['atención al paciente', 'diagnóstico médico', 'gestión hospitalaria', 'sistemas de salud', 'epidemiología', 'telemedicina', 'ehr', 'hl7', 'fhir', 'investigación clínica', 'ensayos clínicos', 'farmacología', 'genética', 'medicina preventiva', 'salud pública', 'bioestadística', 'data analytics en salud'],
                'marketing': ['google analytics', 'google ads', 'facebook ads', 'seo/sem', 'content marketing', 'social media marketing', 'email marketing', 'crm', 'hubspot', 'salesforce', 'adobe creative suite', 'photoshop', 'illustrator', 'brand management', 'customer journey', 'a/b testing', 'conversion optimization', 'growth hacking', 'influencer marketing', 'marketing automation', 'data-driven marketing']
            }

            industry_lower = industry.lower()
            if industry_lower in industry_tech_skills:
                relevant_skills = industry_tech_skills[industry_lower]
                matching_skills = [skill for skill in skills if any(rel_skill.lower() in skill.lower() for rel_skill in relevant_skills)]
                if len(matching_skills) < len(skills) * 0.5:  # Al menos 50% de skills relevantes
                    issues.append(f"Pocas habilidades técnicas relevantes para '{industry}': {matching_skills}")

        # 4. Validar ubicación
        location = annotations.get('location', '').lower()
        mexican_cities = ['ciudad de méxico', 'guadalajara', 'monterrey', 'puebla', 'tijuana', 'mérida', 'león', 'querétaro', 'mexico city']
        if location and not any(city in location for city in mexican_cities):
            issues.append(f"Ubicación no mexicana: {location}")

        # 5. Validar idiomas
        languages = annotations.get('languages', [])
        if languages:
            has_spanish = any('español' in lang.lower() for lang in languages)
            if not has_spanish:
                issues.append("Falta español como idioma nativo")

            # Verificar nivel de inglés según seniority
            has_english = any('inglés' in lang.lower() for lang in languages)
            if seniority_lower in ['senior', 'lead', 'manager', 'director'] and not has_english:
                issues.append(f"Seniority '{seniority}' debería tener inglés")

    except Exception as e:
        issues.append(f"Error en validación: {str(e)}")

    return issues

def main():
    # Bucle infinito (o hasta llegar a N)
    # OBJETIVO definido globalmente

    # Cargar distribución existente
    load_existing_distribution()

    # Verificar cuántos tenemos ya
    cursor.execute("SELECT COUNT(*) FROM cv_dataset")
    total_generados = cursor.fetchone()[0]

    print(f"🚀 Iniciando minería de CVs sintéticos (Modo Balanceado con Validación de Coherencia).")
    print(f"🎯 Objetivo: {OBJETIVO}")
    print(f"📊 Actual: {total_generados}")
    print(f"🤖 Modelo: {MODEL_ID} @ {API_BASE_URL}")
    print("-" * 50)

    report_interval = 25  # Mostrar reporte cada 25 CVs

    while total_generados < OBJETIVO:
        item = generate_profile()

        if not item:
            print("⚠️ Fallo en generación. Reintentando en 2s...")
            time.sleep(2)
            continue

        try:
            unique_id = str(uuid.uuid4())

            # Validar campos mínimos
            if 'cv_text' not in item or 'annotations' not in item:
                print("⚠️ JSON incompleto, saltando...")
                continue

            # VALIDAR COHERENCIA DEL PERFIL
            coherence_issues = validate_profile_coherence(item)
            if coherence_issues:
                print(f"⚠️ Perfil incoherente ({len(coherence_issues)} problemas), reintentando...")
                for issue in coherence_issues[:2]:  # Mostrar máximo 2 problemas
                    print(f"   • {issue}")
                continue  # Reintentar con nuevo perfil

            # Extraer metadata para tracking - CORREGIDO para usar metadata
            industry = item.get('metadata', {}).get('industry', 'Unknown')
            seniority = item.get('metadata', {}).get('seniority', 'Unknown')

            # También actualizar annotations con industry/seniority para consistencia
            if 'annotations' in item:
                item['annotations']['industry'] = industry
                item['annotations']['seniority'] = seniority

            cursor.execute('''
                INSERT INTO cv_dataset (id, industry, seniority, cv_text, annotations)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                unique_id,
                industry,
                seniority,
                item['cv_text'],
                json.dumps(item['annotations'])
            ))

            conn.commit()

            # Actualizar distribución
            distribution_tracker.update('industries', industry)
            distribution_tracker.update('seniorities', seniority)

            total_generados += 1

            # Reporte periódico
            if total_generados % report_interval == 0:
                print(f"\n📊 Progreso: {total_generados}/{OBJETIVO} CVs generados")
                distribution_tracker.print_balance_report()
                print("-" * 50)

            print(f"💾 Guardado 1 CV ({industry}/{seniority}). Progreso total: {total_generados}/{OBJETIVO}")

        except Exception as e:
            print(f"Error insertando item: {e}")

        # Pausa breve para dejar respirar al servidor local
        time.sleep(0.1)

    # Reporte final
    print(f"\n🎉 ¡Entrenamiento completado! Base de datos finalizada con {total_generados} CVs.")
    distribution_tracker.print_balance_report()

    conn.close()

def validate_distribution():
    """Función para validar la distribución actual de la base de datos"""
    try:
        # Cargar datos actuales
        load_existing_distribution()

        # Obtener estadísticas
        stats = distribution_tracker.get_stats()

        print("🔍 VALIDACIÓN DE DISTRIBUCIÓN EN BASE DE DATOS")
        print("=" * 60)

        total_issues = 0

        for category, subcats in stats.items():
            print(f"\n📊 {category.upper()}:")
            issues = 0

            for subcat, data in subcats.items():
                deviation = abs(data['percentage'] - data['target'])
                if deviation > 10:  # Más de 10% de desviación
                    status = "❌ CRÍTICO"
                    issues += 1
                elif deviation > 5:  # Más de 5% de desviación
                    status = "⚠️  ALTO"
                    issues += 1
                else:
                    status = "✅ OK"

                print(f"  {status} {subcat}: {data['count']} ({data['percentage']:.1f}% | Target: {data['target']:.1f}%)")

            if issues > 0:
                print(f"  🔴 {issues} subcategorías con desviaciones significativas")
                total_issues += issues
            else:
                print(f"  ✅ Distribución balanceada")

        print(f"\n" + "=" * 60)
        if total_issues == 0:
            print("🎉 ¡DISTRIBUCIÓN PERFECTA! Dataset listo para entrenamiento.")
        elif total_issues < 5:
            print(f"⚠️  Distribución aceptable con {total_issues} desviaciones menores.")
        else:
            print(f"❌ Distribución requiere rebalanceo. {total_issues} problemas detectados.")
            print("💡 Recomendación: Ejecutar generación adicional con el sistema de balance.")

    except Exception as e:
        print(f"❌ Error en validación: {e}")

def validate_profile_coherence_batch():
    """Validar coherencia de todos los perfiles en la base de datos"""
    try:
        cursor.execute("SELECT industry, seniority, annotations FROM cv_dataset")
        rows = cursor.fetchall()

        print("🔍 VALIDACIÓN DE COHERENCIA DE PERFILES")
        print("=" * 60)

        total_profiles = len(rows)
        profiles_with_issues = 0
        total_issues = 0

        for i, row in enumerate(rows):
            try:
                industry_db, seniority_db, annotations_json = row
                profile = json.loads(annotations_json)
                
                # Reconstruir estructura completa con metadata de DB para perfiles antiguos
                full_profile = {
                    'metadata': {
                        'industry': industry_db,
                        'seniority': seniority_db
                    },
                    'annotations': profile
                }

                issues = validate_profile_coherence(full_profile)
                if issues:
                    profiles_with_issues += 1
                    total_issues += len(issues)
                    if i < 5:  # Mostrar primeros 5 con problemas
                        print(f"\n❌ Perfil {i+1} - {len(issues)} problemas:")
                        for issue in issues[:3]:  # Máximo 3 problemas por perfil
                            print(f"   • {issue}")

            except Exception as e:
                print(f"Error procesando perfil {i+1}: {e}")

        print(f"\n" + "=" * 60)
        print(f"📊 Resumen de Validación:")
        print(f"   • Total de perfiles: {total_profiles}")
        if total_profiles > 0:
            print(f"   • Perfiles con problemas: {profiles_with_issues} ({profiles_with_issues/total_profiles*100:.1f}%)")
        else:
            print(f"   • Perfiles con problemas: {profiles_with_issues} (base de datos vacía)")
        print(f"   • Total de problemas: {total_issues}")

        if profiles_with_issues == 0:
            print("🎉 ¡TODOS los perfiles son coherentes!")
        elif total_profiles > 0 and profiles_with_issues / total_profiles < 0.1:
            print("✅ Coherencia aceptable - pocos perfiles con problemas menores")
        else:
            print("❌ Muchos perfiles con problemas de coherencia - revisar prompt")

    except Exception as e:
        print(f"❌ Error en validación de coherencia: {e}")

def batch_generate_main():
    """Función principal para generar CVs en lotes usando el Prompt Maestro"""
    # Cargar distribución existente
    load_existing_distribution()

    # Verificar cuántos tenemos ya
    cursor.execute("SELECT COUNT(*) FROM cv_dataset")
    total_generados = cursor.fetchone()[0]

    print(f"🚀 Iniciando generación en LOTES (Prompt Maestro Experimental).")
    print(f"🎯 Objetivo: {OBJETIVO}")
    print(f"📊 Actual: {total_generados}")
    print(f"🤖 Modelo: {MODEL_ID} @ {API_BASE_URL}")
    print("-" * 50)

    while total_generados < OBJETIVO:
        batch = generate_batch_profiles()

        if not batch:
            print("⚠️ Fallo en generación del lote. Reintentando en 2s...")
            time.sleep(2)
            continue

        batch_size = len(batch)
        print(f"📦 Procesando lote de {batch_size} CVs...")

        for item in batch:
            if total_generados >= OBJETIVO:
                break

            try:
                unique_id = str(uuid.uuid4())

                # Validar campos mínimos
                if 'cv_text' not in item or 'annotations' not in item or 'metadata' not in item:
                    print("⚠️ JSON incompleto en lote, saltando...")
                    continue

                # Extraer metadata
                industry = item['metadata'].get('industry', 'Unknown')
                seniority = item['metadata'].get('seniority', 'Unknown')

                # Actualizar annotations con industry/seniority para consistencia
                if 'annotations' in item:
                    item['annotations']['industry'] = industry
                    item['annotations']['seniority'] = seniority

                cursor.execute('''
                    INSERT INTO cv_dataset (id, industry, seniority, cv_text, annotations)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    unique_id,
                    industry,
                    seniority,
                    item['cv_text'],
                    json.dumps(item['annotations'])
                ))

                conn.commit()

                # Actualizar distribución
                distribution_tracker.update('industries', industry)
                distribution_tracker.update('seniorities', seniority)

                total_generados += 1

                print(f"💾 Guardado CV {total_generados}/{OBJETIVO} ({industry}/{seniority})")

            except Exception as e:
                print(f"Error insertando item del lote: {e}")

        # Pausa entre lotes
        time.sleep(1)

    # Reporte final
    print(f"\n🎉 ¡Generación en lotes completada! Base de datos finalizada con {total_generados} CVs.")
    distribution_tracker.print_balance_report()

    conn.close()

# Función para ejecutar validación si se llama con --validate
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--validate":
        validate_distribution()
        print("\n" + "="*60)
        validate_profile_coherence_batch()
    elif len(sys.argv) > 1 and sys.argv[1] == "--clean":
        print("🧹 LIMPIANDO BASE DE DATOS...")
        cursor.execute("DELETE FROM cv_dataset")
        conn.commit()
        print("✅ Base de datos limpiada. Todos los registros eliminados.")
        conn.close()
    elif len(sys.argv) > 1 and sys.argv[1] == "--batch":
        print("🔄 GENERANDO CVs EN LOTES (MODO EXPERIMENTAL)")
        batch_generate_main()
    else:
        try:
            main()
        except KeyboardInterrupt:
            print("\n🛑 Detenido por el usuario. Datos guardados.")
            distribution_tracker.print_balance_report()
            conn.close()
        except Exception as e:
            print(f"\n❌ Error fatal: {e}")
            distribution_tracker.print_balance_report()
            conn.close()
            sys.exit(1)
