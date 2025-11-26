#!/usr/bin/env python3
"""
Script para crear una muestra uniforme y balanceada de la base de datos de CVs
"""
import sqlite3
import json
import os
import random
from collections import defaultdict

def create_uniform_sample():
    """Crear una muestra uniforme de la base de datos actual"""

    # Conectar a la base de datos
    db_path = 'cv_simulator/training_data_cvs.db'
    if not os.path.exists(db_path):
        print("❌ Base de datos no encontrada")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Obtener todos los registros
    cursor.execute("SELECT id, industry, seniority, cv_text, annotations FROM cv_dataset")
    rows = cursor.fetchall()

    print(f"📊 Base de datos actual: {len(rows)} registros")

    # Organizar por industria y seniority
    organized = defaultdict(lambda: defaultdict(list))
    for row in rows:
        cv_id, industry, seniority, cv_text, annotations = row
        organized[industry][seniority].append({
            'id': cv_id,
            'cv_text': cv_text,
            'annotations': annotations
        })

    # Definir tamaños objetivo para muestra uniforme
    target_sizes = {
        'industries': {
            'Tecnología': 40,
            'Ciencia de Datos': 35,
            'Finanzas': 30,
            'Salud': 25,
            'Marketing': 20,
            'Biotecnología': 15,
            'FinTech': 15,
            'Legal': 10,
            'Construcción': 10,
            'Educación': 10,
            'Retail': 5,
            'Healthcare': 5
        },
        'seniorities': {
            'Junior': 30,
            'Mid-Level': 40,
            'Senior': 50,
            'Lead': 30,
            'Manager': 20,
            'Director': 10
        }
    }

    # Crear nueva base de datos para la muestra
    sample_db = 'cv_simulator/cv_sample_uniform.db'
    if os.path.exists(sample_db):
        os.remove(sample_db)

    sample_conn = sqlite3.connect(sample_db)
    sample_cursor = sample_conn.cursor()

    sample_cursor.execute('''
        CREATE TABLE cv_dataset (
            id TEXT PRIMARY KEY,
            industry TEXT,
            seniority TEXT,
            cv_text TEXT,
            annotations JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    selected_cvs = []
    total_selected = 0

    # Seleccionar CVs de manera uniforme
    for industry, seniority_dict in organized.items():
        target_industry = target_sizes['industries'].get(industry, 5)  # Default 5 si no está en target

        industry_cvs = []
        for seniority, cvs in seniority_dict.items():
            # Mezclar aleatoriamente
            random.shuffle(cvs)
            industry_cvs.extend(cvs)

        # Tomar muestra de esta industria
        sample_size = min(target_industry, len(industry_cvs))
        selected_from_industry = industry_cvs[:sample_size]

        for cv in selected_from_industry:
            selected_cvs.append({
                'id': cv['id'],
                'industry': industry,
                'seniority': 'Unknown',  # Lo determinaremos del contenido
                'cv_text': cv['cv_text'],
                'annotations': cv['annotations']
            })

        total_selected += len(selected_from_industry)
        print(f"✅ {industry}: {len(selected_from_industry)} CVs seleccionados")

    # Balancear por seniority también
    seniority_counts = defaultdict(int)
    for cv in selected_cvs:
        try:
            annotations = json.loads(cv['annotations'])
            seniority = annotations.get('seniority', 'Unknown')
            seniority_counts[seniority] += 1
        except:
            seniority_counts['Unknown'] += 1

    print(f"\n📊 Distribución por seniority en muestra:")
    for seniority, count in seniority_counts.items():
        print(f"  {seniority}: {count}")

    # Insertar en base de datos de muestra
    for cv in selected_cvs:
        try:
            sample_cursor.execute('''
                INSERT INTO cv_dataset (id, industry, seniority, cv_text, annotations)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                cv['id'],
                cv['industry'],
                cv['seniority'],
                cv['cv_text'],
                cv['annotations']
            ))
        except Exception as e:
            print(f"Error insertando CV {cv['id']}: {e}")

    sample_conn.commit()

    # Verificar distribución final
    sample_cursor.execute("SELECT industry, COUNT(*) FROM cv_dataset GROUP BY industry ORDER BY COUNT(*) DESC")
    industry_dist = sample_cursor.fetchall()

    sample_cursor.execute("SELECT seniority, COUNT(*) FROM cv_dataset GROUP BY seniority ORDER BY COUNT(*) DESC")
    seniority_dist = sample_cursor.fetchall()

    print(f"\n🎯 MUESTRA UNIFORME CREADA: {len(selected_cvs)} CVs")
    print("=" * 50)
    print("📊 DISTRIBUCIÓN POR INDUSTRIA:")
    for industry, count in industry_dist:
        print(f"  {industry}: {count}")

    print("\n📊 DISTRIBUCIÓN POR SENIORITY:")
    for seniority, count in seniority_dist:
        print(f"  {seniority}: {count}")

    # Cerrar conexiones
    conn.close()
    sample_conn.close()

    print(f"\n✅ Muestra uniforme guardada en: {sample_db}")

if __name__ == "__main__":
    create_uniform_sample()
