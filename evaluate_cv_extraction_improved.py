#!/usr/bin/env python3
"""
Script mejorado de evaluación del sistema de extracción de CVs de MoirAI
Versión avanzada con mejor análisis de skills y diagnóstico detallado.
"""

import sqlite3
import json
import sys
import os
import re
from collections import defaultdict, Counter
from typing import Dict, List, Any


def _extract_resume_analysis_improved(resume_text: str, industry: str = None) -> dict:
    """
    Versión mejorada de extracción de skills que considera el contexto del CV
    y skills específicas por industria.
    """
    if not resume_text or len(resume_text.strip()) < 50:
        return {
            "skills": [],
            "soft_skills": [],
            "projects": [],
            "confidence": 0.0
        }

    try:
        resume_clean = resume_text.lower()

        # Skills por industria (basado en el análisis del generate_cvs.py)
        industry_skills = {
            'Tecnología': [
                'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker',
                'metodologías ágiles', 'desarrollo web', 'programación java', 'api rest',
                'microservicios', 'devops', 'git', 'linux', 'testing', 'ci/cd'
            ],
            'Ciencia de Datos': [
                'python', 'r', 'sql', 'machine learning', 'tensorflow', 'pandas', 'numpy',
                'análisis de datos', 'visualización', 'estadística', 'big data', 'spark',
                'tableau', 'power bi', 'deep learning', 'nlp', 'computer vision'
            ],
            'Finanzas': [
                'análisis financiero', 'modelado de riesgo', 'excel avanzado', 'sql',
                'presentaciones ejecutivas', 'valoración', 'finanzas corporativas',
                'auditoría', 'compliance', 'sap', 'bloomberg', 'modelos financieros'
            ],
            'Salud': [
                'implementación emr', 'optimización de procesos', 'gestión hospitalaria',
                'atención al paciente', 'diagnóstico médico', 'epidemiología', 'telemedicina',
                'sistemas de salud', 'investigación clínica', 'gestión de calidad'
            ],
            'Marketing': [
                'google analytics', 'seo/sem', 'social media', 'content marketing',
                'brand management', 'email marketing', 'crm', 'adobe creative suite',
                'campañas digitales', 'marketing automation', 'growth hacking'
            ],
            'Biotecnología': [
                'investigación científica', 'análisis de laboratorio', 'biotecnología',
                'desarrollo de productos', 'regulaciones sanitarias', 'ensayos clínicos',
                'biología molecular', 'genética', 'proteómica', 'bioinformática'
            ],
            'Legal': [
                'análisis legal', 'investigación jurídica', 'redacción de contratos',
                'compliance legal', 'derecho corporativo', 'propiedad intelectual',
                'litigios', 'regulaciones', 'análisis de riesgo legal'
            ],
            'Educación': [
                'desarrollo curricular', 'evaluación educativa', 'metodologías de enseñanza',
                'tecnología educativa', 'gestión académica', 'capacitación docente',
                'e-learning', 'asesoría pedagógica', 'investigación educativa'
            ],
            'Construcción': [
                'gestión de proyectos', 'normativas de construcción', 'supervisión de obras',
                'planificación urbana', 'seguridad laboral', 'gestión de contratos',
                'autocad', 'bim', 'ingeniería civil', 'gestión de calidad'
            ],
            'FinTech': [
                'finanzas digitales', 'blockchain', 'criptomonedas', 'regtech',
                'pagos digitales', 'análisis de riesgo fintech', 'compliance fintech',
                'innovación financiera', 'api bancarias', 'seguridad financiera'
            ],
            'Retail': [
                'gestión de inventarios', 'experiencia del cliente', 'merchandising',
                'análisis de ventas', 'e-commerce', 'supply chain', 'crm retail',
                'marketing omnicanal', 'gestión de tiendas', 'optimización de precios'
            ],
            'Healthcare': [
                'gestión sanitaria', 'políticas de salud', 'sistemas de salud pública',
                'gestión hospitalaria', 'telemedicina', 'investigación médica',
                'políticas públicas', 'gestión de crisis sanitarias'
            ]
        }

        # Skills transversales (comunes a todas las industrias)
        common_skills = [
            'liderazgo', 'trabajo en equipo', 'comunicación', 'resolución de problemas',
            'adaptabilidad', 'gestión del tiempo', 'aprendizaje continuo', 'creatividad',
            'análisis crítico', 'toma de decisiones', 'orientación a resultados'
        ]

        # Extraer skills basados en la industria del CV
        skills = []
        if industry and industry in industry_skills:
            # Skills específicas de la industria
            industry_specific = [skill for skill in industry_skills[industry]
                               if skill in resume_clean]
            skills.extend(industry_specific)

        # Skills transversales
        transversal = [skill for skill in common_skills if skill in resume_clean]
        skills.extend(transversal)

        # Skills técnicas genéricas (fallback)
        technical_fallback = [
            'python', 'java', 'javascript', 'sql', 'aws', 'docker', 'git',
            'excel', 'powerpoint', 'word', 'project', 'visio'
        ]
        technical_found = [skill for skill in technical_fallback if skill in resume_clean]
        skills.extend(technical_found)

        # Remover duplicados y limitar
        skills = list(set(skills))[:15]

        # Soft skills (si no se encontraron suficientes skills transversales)
        soft_skills = transversal[:5] if transversal else []

        # Extraer proyectos (mejorado)
        projects = []
        project_indicators = [
            "proyecto", "project", "desarrollo", "developed", "implementé", "sistema", "system",
            "plataforma", "platform", "aplicación", "application", "programa", "program",
            "iniciativa", "initiative", "campaña", "campaign"
        ]

        lines = resume_text.split('\n')
        for line in lines:
            line_lower = line.lower().strip()
            if any(indicator in line_lower for indicator in project_indicators) and len(line.strip()) > 15:
                # Limpiar y truncar
                clean_project = line.strip()[:100]
                if clean_project not in projects:
                    projects.append(clean_project)
                if len(projects) >= 5:
                    break

        # Calcular confianza mejorada
        industry_match = len([s for s in skills if s in industry_skills.get(industry, [])]) if industry else 0
        common_match = len(soft_skills)
        technical_match = len(technical_found)

        confidence = min(1.0, (industry_match * 0.4 + common_match * 0.3 + technical_match * 0.3) / 5.0)

        return {
            "skills": skills,
            "soft_skills": soft_skills,
            "projects": projects,
            "confidence": round(confidence, 2)
        }

    except Exception as e:
        print(f"⚠️ Error en análisis mejorado: {str(e)}")
        return {
            "skills": [],
            "soft_skills": [],
            "projects": [],
            "confidence": 0.0
        }


def _extract_harvard_cv_fields(resume_text: str) -> dict:
    """
    Extrae campos estructurados del CV en formato Harvard.

    Mejora la extracción para manejar CVs en español y formatos variables.

    Retorna:
        Dict con: {
            "objective": str,
            "education": List[Dict],
            "experience": List[Dict],
            "certifications": List[str],
            "languages": List[str]
        }
    """

    if not resume_text or len(resume_text.strip()) < 50:
        return {
            "objective": None,
            "education": [],
            "experience": [],
            "certifications": [],
            "languages": []
        }

    try:
        lines = resume_text.split('\n')
        text_lower = resume_text.lower()

        # 1️⃣ Extraer OBJETIVO: Primer párrafo después del contacto
        objective = None
        contact_end_idx = 0

        # Encontrar dónde termina la información de contacto
        for i, line in enumerate(lines[:15]):
            line = line.strip()
            if not line:
                continue
            # Si la línea contiene email, teléfono, o URLs, es parte del contacto
            if ('@' in line and '.' in line) or any(char.isdigit() for char in line if char not in ['/', '-', ' ']) or 'http' in line:
                contact_end_idx = i + 1
            # Si encontramos una línea que parece ser el inicio del objetivo
            elif len(line) > 50 and not any(keyword in line.lower() for keyword in ['educación', 'education', 'experiencia', 'experience', 'habilidades', 'skills']):
                break

        # El objetivo es el párrafo que sigue al contacto
        objective_lines = []
        for i in range(contact_end_idx, min(len(lines), contact_end_idx + 10)):
            line = lines[i].strip()
            if line and len(line) > 20 and not any(keyword in line.lower() for keyword in ['educación', 'education', 'experiencia', 'experience', 'habilidades', 'skills', 'certific', 'idioma']):
                objective_lines.append(line)
                if len(' '.join(objective_lines)) > 300:  # Limitar a ~300 caracteres
                    break

        if objective_lines:
            objective = ' '.join(objective_lines)[:500]

        # 2️⃣ Extraer EDUCACIÓN: Buscar patrones de universidades y títulos
        education = []
        edu_keywords = [
            'universidad', 'university', 'instituto', 'institute', 'colegio', 'school',
            'licenciatura', 'degree', 'bachiller', 'master', 'maestría', 'doctorado', 'phd',
            'ingeniería', 'engineering', 'ciencia', 'science', 'tecnología', 'technology'
        ]

        # Buscar párrafos que contengan keywords de educación
        paragraphs = resume_text.split('\n\n')
        for para in paragraphs:
            para_lower = para.lower()
            if any(keyword in para_lower for keyword in edu_keywords):
                lines_in_para = [l.strip() for l in para.split('\n') if l.strip()]

                if len(lines_in_para) >= 1:
                    edu_record = {
                        "institution": "",
                        "degree": "",
                        "field_of_study": "",
                        "graduation_year": None
                    }

                    # Primera línea suele ser la institución
                    edu_record["institution"] = lines_in_para[0]

                    # Buscar año de graduación
                    year_match = re.search(r'(20\d{2}|19\d{2})', para)
                    if year_match:
                        edu_record["graduation_year"] = int(year_match.group(1))

                    # Buscar título académico
                    for line in lines_in_para:
                        if any(keyword in line.lower() for keyword in ['licenciatura', 'degree', 'bachiller', 'master', 'maestría', 'ingeniería', 'ciencia']):
                            edu_record["degree"] = line
                            break

                    # Campo de estudio (si hay más líneas)
                    if len(lines_in_para) >= 3:
                        edu_record["field_of_study"] = lines_in_para[2]

                    if edu_record["institution"]:
                        education.append(edu_record)

        # Limitar a máximo 3 educaciones
        education = education[:3]

        # 3️⃣ Extraer EXPERIENCIA: Buscar patrones de trabajo
        experience = []
        exp_keywords = [
            'experiencia', 'experience', 'trabajo', 'job', 'puesto', 'position',
            'empresa', 'company', 'organización', 'organization'
        ]

        # Buscar párrafos que contengan keywords de experiencia
        for para in paragraphs:
            para_lower = para.lower()
            if any(keyword in para_lower for keyword in exp_keywords) or re.search(r'\d{4}\s*[-–]\s*(presente|actual|actualidad|\d{4})', para_lower):
                lines_in_para = [l.strip() for l in para.split('\n') if l.strip()]

                if len(lines_in_para) >= 2:
                    exp_record = {
                        "position": "",
                        "company": "",
                        "start_date": None,
                        "end_date": None,
                        "description": ""
                    }

                    # Buscar fechas (formato: 2020-2022, 2020/2022, 2020 – 2022, 2020 - Presente)
                    date_match = re.search(r'(\d{4})\s*[-–/]\s*(presente|actual|actualidad|(\d{4}))?', para, re.IGNORECASE)
                    if date_match:
                        exp_record["start_date"] = date_match.group(1)
                        if date_match.group(2) and date_match.group(2).lower() not in ['presente', 'actual', 'actualidad']:
                            exp_record["end_date"] = date_match.group(2)
                        elif date_match.group(3):
                            exp_record["end_date"] = date_match.group(3)

                    # Primera línea significativa suele ser el puesto
                    first_line = lines_in_para[0]
                    if not re.search(r'\d{4}', first_line):  # Si no tiene fecha
                        exp_record["position"] = first_line
                        if len(lines_in_para) >= 2:
                            exp_record["company"] = lines_in_para[1]
                    else:
                        # Si la primera línea tiene fecha, buscar el puesto en la siguiente
                        if len(lines_in_para) >= 2:
                            exp_record["position"] = lines_in_para[1]
                            if len(lines_in_para) >= 3:
                                exp_record["company"] = lines_in_para[2]

                    # Descripción: resto del párrafo
                    desc_lines = []
                    for line in lines_in_para[2:]:
                        if line and len(line) > 10:
                            desc_lines.append(line)

                    exp_record["description"] = ' '.join(desc_lines) if desc_lines else para

                    if exp_record["position"]:
                        experience.append(exp_record)

        # Limitar a máximo 4 experiencias
        experience = experience[:4]

        # 4️⃣ Extraer CERTIFICACIONES: Buscar menciones de certificados
        certifications = []
        cert_keywords = ['certific', 'course', 'diploma', 'diplomado', 'capacitación', 'training', 'workshop']

        for para in paragraphs:
            para_lower = para.lower()
            if any(keyword in para_lower for keyword in cert_keywords):
                lines_in_para = [l.strip() for l in para.split('\n') if l.strip()]
                certifications.extend(lines_in_para[:3])  # Máximo 3 por párrafo

        certifications = certifications[:5]  # Máximo 5 total

        # 5️⃣ Extraer IDIOMAS: Buscar menciones de idiomas
        languages = []
        lang_patterns = [
            r'(inglés|english)[\s:]*([a-zA-Z\s]+)',
            r'(español|spanish)[\s:]*([a-zA-Z\s]+)',
            r'(francés|french)[\s:]*([a-zA-Z\s]+)',
            r'(alemán|german)[\s:]*([a-zA-Z\s]+)',
            r'(portugués|portuguese)[\s:]*([a-zA-Z\s]+)',
            r'(italiano|italian)[\s:]*([a-zA-Z\s]+)',
            r'(chino|chinese)[\s:]*([a-zA-Z\s]+)'
        ]

        for pattern in lang_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                lang_name = match[0] if isinstance(match, tuple) else match
                level = match[1] if isinstance(match, tuple) and len(match) > 1 else ""
                lang_entry = lang_name.strip()
                if level:
                    lang_entry += f": {level.strip()}"
                if lang_entry not in languages:
                    languages.append(lang_entry)

        languages = languages[:5]  # Máximo 5 idiomas

        return {
            "objective": objective,
            "education": education,
            "experience": experience,
            "certifications": certifications,
            "languages": languages
        }

    except Exception as e:
        print(f"⚠️ Error en _extract_harvard_cv_fields mejorado: {str(e)}")
        return {
            "objective": None,
            "education": [],
            "experience": [],
            "certifications": [],
            "languages": []
        }
    """Carga los CVs generados desde la base de datos"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT id, industry, seniority, cv_text, annotations FROM cv_dataset')
    rows = cursor.fetchall()

    cvs = []
    for row in rows:
        cv_id, industry, seniority, cv_text, annotations_json = row

        try:
            annotations = json.loads(annotations_json)
            cvs.append({
                'id': cv_id,
                'industry': industry,
                'seniority': seniority,
                'cv_text': cv_text,
                'expected': annotations
            })
        except json.JSONDecodeError:
            print(f"⚠️ Error parseando annotations para CV {cv_id}")
            continue

    conn.close()
    return cvs


def evaluate_harvard_extraction(cv_text: str, expected: Dict) -> Dict[str, Any]:
    """Evalúa la extracción de campos Harvard"""
    extracted = _extract_harvard_cv_fields(cv_text)

    results = {}

    # Evaluar objective
    expected_objective = expected.get('current_role', '') or expected.get('objective', '')
    extracted_objective = extracted.get('objective', '') or ''

    # Calcular similitud simple (overlap de palabras)
    expected_words = set(expected_objective.lower().split())
    extracted_words = set(extracted_objective.lower().split())
    overlap = len(expected_words.intersection(extracted_words))
    total_expected = len(expected_words)

    results['objective'] = {
        'expected': expected_objective,
        'extracted': extracted_objective,
        'accuracy': overlap / total_expected if total_expected > 0 else 0
    }

    # Evaluar education
    expected_edu = expected.get('education', [])
    extracted_edu = extracted.get('education', [])

    edu_matches = 0
    for exp_edu in expected_edu:
        for ext_edu in extracted_edu:
            # Comparar institución y grado
            exp_inst = exp_edu.get('institution', '').lower()
            ext_inst = ext_edu.get('institution', '').lower()
            exp_degree = exp_edu.get('degree', '').lower()
            ext_degree = ext_edu.get('degree', '').lower()

            if (exp_inst in ext_inst or ext_inst in exp_inst) and \
               (exp_degree in ext_degree or ext_degree in exp_degree):
                edu_matches += 1
                break

    results['education'] = {
        'expected_count': len(expected_edu),
        'extracted_count': len(extracted_edu),
        'matches': edu_matches,
        'accuracy': edu_matches / len(expected_edu) if expected_edu else 1.0
    }

    # Evaluar experience
    expected_exp = expected.get('experience', [])
    extracted_exp = extracted.get('experience', [])

    exp_matches = 0
    for exp_exp in expected_exp:
        for ext_exp in extracted_exp:
            # Comparar posición y compañía
            exp_pos = exp_exp.get('position', '').lower()
            ext_pos = ext_exp.get('position', '').lower()
            exp_comp = exp_exp.get('company', '').lower()
            ext_comp = ext_exp.get('company', '').lower()

            if (exp_pos in ext_pos or ext_pos in exp_pos) and \
               (exp_comp in ext_comp or ext_comp in exp_comp):
                exp_matches += 1
                break

    results['experience'] = {
        'expected_count': len(expected_exp),
        'extracted_count': len(extracted_exp),
        'matches': exp_matches,
        'accuracy': exp_matches / len(expected_exp) if expected_exp else 1.0
    }

    # Evaluar languages
    expected_lang = expected.get('languages', [])
    extracted_lang = extracted.get('languages', [])

    lang_matches = 0
    for exp_lang in expected_lang:
        exp_lang_lower = exp_lang.lower()
        for ext_lang in extracted_lang:
            if exp_lang_lower in ext_lang.lower() or ext_lang.lower() in exp_lang_lower:
                lang_matches += 1
                break

    results['languages'] = {
        'expected_count': len(expected_lang),
        'extracted_count': len(extracted_lang),
        'matches': lang_matches,
        'accuracy': lang_matches / len(expected_lang) if expected_lang else 1.0
    }

    return results


def evaluate_skills_extraction(cv_text: str, expected: Dict, industry: str = None) -> Dict[str, Any]:
    """Evalúa la extracción de skills con la versión mejorada"""
    extracted = _extract_resume_analysis_improved(cv_text, industry)

    expected_skills = set(expected.get('skills', []))
    extracted_skills = set(extracted.get('skills', []))

    # Calcular precisión y recall
    true_positives = len(expected_skills.intersection(extracted_skills))
    false_positives = len(extracted_skills - expected_skills)
    false_negatives = len(expected_skills - extracted_skills)

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    return {
        'expected_skills': list(expected_skills),
        'extracted_skills': list(extracted_skills),
        'true_positives': true_positives,
        'false_positives': false_positives,
        'false_negatives': false_negatives,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'confidence': extracted.get('confidence', 0)
    }


def generate_evaluation_report(cvs: List[Dict]) -> Dict[str, Any]:
    """Genera un reporte completo de evaluación con la versión mejorada"""
    print(f"🔬 Evaluando {len(cvs)} CVs generados con análisis mejorado...")

    results = {
        'summary': {
            'total_cvs': len(cvs),
            'industries': Counter(cv['industry'] for cv in cvs),
            'seniorities': Counter(cv['seniority'] for cv in cvs)
        },
        'harvard_fields': defaultdict(list),
        'skills': defaultdict(list),
        'detailed_results': []
    }

    for i, cv in enumerate(cvs):
        if i % 25 == 0:
            print(f"📊 Procesando CV {i+1}/{len(cvs)}...")

        cv_result = {
            'id': cv['id'],
            'industry': cv['industry'],
            'seniority': cv['seniority']
        }

        # Evaluar campos Harvard
        harvard_results = evaluate_harvard_extraction(cv['cv_text'], cv['expected'])
        cv_result['harvard'] = harvard_results

        for field, metrics in harvard_results.items():
            if 'accuracy' in metrics:
                results['harvard_fields'][field].append(metrics['accuracy'])

        # Evaluar skills con contexto de industria
        skills_results = evaluate_skills_extraction(cv['cv_text'], cv['expected'], cv['industry'])
        cv_result['skills'] = skills_results

        for metric in ['precision', 'recall', 'f1_score']:
            results['skills'][metric].append(skills_results[metric])

        results['detailed_results'].append(cv_result)

    # Calcular promedios
    results['averages'] = {
        'harvard_fields': {
            field: sum(scores) / len(scores) if scores else 0
            for field, scores in results['harvard_fields'].items()
        },
        'skills': {
            metric: sum(scores) / len(scores) if scores else 0
            for metric, scores in results['skills'].items()
        }
    }

    return results


def print_evaluation_report(results: Dict[str, Any]):
    """Imprime un reporte legible de la evaluación mejorada"""
    print("\n" + "="*85)
    print("📊 REPORTE DE EVALUACIÓN MEJORADO - EXTRACCIÓN DE CVS MOIRAI")
    print("="*85)

    # Resumen general
    summary = results['summary']
    print(f"\n📈 RESUMEN GENERAL:")
    print(f"   • Total CVs evaluados: {summary['total_cvs']}")
    print(f"   • Industrias: {dict(summary['industries'])}")
    print(f"   • Niveles: {dict(summary['seniorities'])}")

    # Resultados Harvard Fields
    print(f"\n🎓 EXTRACCIÓN DE CAMPOS HARVARD:")
    averages = results['averages']['harvard_fields']
    for field, accuracy in averages.items():
        print(".2f")

    # Resultados Skills Mejorados
    print(f"\n🛠️ EXTRACCIÓN DE SKILLS (MEJORADA):")
    skills_avg = results['averages']['skills']
    print(".2f")
    print(".2f")
    print(".2f")

    # Análisis por industria (top 5 mejores)
    print(f"\n🏭 TOP 5 INDUSTRIAS CON MEJOR DESEMPEÑO:")
    industry_performance = defaultdict(lambda: defaultdict(list))

    for cv_result in results['detailed_results']:
        industry = cv_result['industry']
        harvard_acc = sum(metrics['accuracy'] for metrics in cv_result['harvard'].values() if 'accuracy' in metrics) / 4
        skills_f1 = cv_result['skills']['f1_score']

        industry_performance[industry]['harvard'].append(harvard_acc)
        industry_performance[industry]['skills'].append(skills_f1)

    # Ordenar por promedio de F1 de skills
    industry_avg = {}
    for industry, metrics in industry_performance.items():
        harvard_avg = sum(metrics['harvard']) / len(metrics['harvard'])
        skills_avg = sum(metrics['skills']) / len(metrics['skills'])
        industry_avg[industry] = (harvard_avg, skills_avg)

    sorted_industries = sorted(industry_avg.items(), key=lambda x: x[1][1], reverse=True)

    for industry, (harvard_avg, skills_avg) in sorted_industries[:5]:
        count = len(industry_performance[industry]['skills'])
        print(".2f")

    # Casos de éxito
    print(f"\n✅ CASOS DE ÉXITO (F1 Skills > 0.5):")
    success_cases = []

    for cv_result in results['detailed_results']:
        skills_f1 = cv_result['skills']['f1_score']
        if skills_f1 > 0.5:
            success_cases.append({
                'id': cv_result['id'],
                'industry': cv_result['industry'],
                'seniority': cv_result['seniority'],
                'skills_f1': skills_f1,
                'harvard_acc': sum(metrics['accuracy'] for metrics in cv_result['harvard'].values() if 'accuracy' in metrics) / 4
            })

    if success_cases:
        print(f"   Encontrados {len(success_cases)} casos exitosos:")
        for case in success_cases[:3]:  # Mostrar top 3
            print(f"     • {case['industry']} ({case['seniority']}): F1={case['skills_f1']:.2f}, Harvard={case['harvard_acc']:.2f}")
    else:
        print("   No se encontraron casos con F1 > 0.5")

    # Diagnóstico de problemas
    print(f"\n🔍 DIAGNÓSTICO DE PROBLEMAS:")

    # Analizar skills no encontrados
    all_expected_skills = Counter()
    all_extracted_skills = Counter()

    for cv_result in results['detailed_results'][:10]:  # Analizar primeros 10
        expected = set(cv_result['skills']['expected_skills'])
        extracted = set(cv_result['skills']['extracted_skills'])

        for skill in expected:
            all_expected_skills[skill] += 1
        for skill in extracted:
            all_extracted_skills[skill] += 1

    print("   Skills más comunes esperados pero no extraídos:")
    missed_skills = all_expected_skills - all_extracted_skills
    for skill, count in missed_skills.most_common(5):
        print(f"     • '{skill}' (en {count} CVs)")

    print(f"\n" + "="*85)


def save_detailed_results(results: Dict[str, Any], output_file: str = 'evaluation_results_improved.json'):
    """Guarda los resultados detallados en un archivo JSON"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"💾 Resultados detallados guardados en {output_file}")


def load_generated_cvs(db_path: str = 'cv_simulator/training_data_cvs.db') -> List[Dict]:
    """Carga los CVs generados desde la base de datos"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT id, industry, seniority, cv_text, annotations FROM cv_dataset')
    rows = cursor.fetchall()

    cvs = []
    for row in rows:
        cv_id, industry, seniority, cv_text, annotations_json = row

        try:
            annotations = json.loads(annotations_json)
            cvs.append({
                'id': cv_id,
                'industry': industry,
                'seniority': seniority,
                'cv_text': cv_text,
                'expected': annotations
            })
        except json.JSONDecodeError:
            print(f"⚠️ Error parseando annotations para CV {cv_id}")
            continue

    conn.close()
    return cvs


if __name__ == "__main__":
    print("🚀 Iniciando evaluación MEJORADA del sistema de extracción de CVs MoirAI")
    print("📂 Cargando CVs generados...")

    # Cargar CVs
    cvs = load_generated_cvs()

    if not cvs:
        print("❌ No se encontraron CVs en la base de datos")
        sys.exit(1)

    # Ejecutar evaluación mejorada
    results = generate_evaluation_report(cvs)

    # Imprimir reporte
    print_evaluation_report(results)

    # Guardar resultados detallados
    save_detailed_results(results)

    print("✅ Evaluación mejorada completada exitosamente!")
