#!/usr/bin/env python3
"""
Script para evaluar la extracción de CVs usando la muestra uniforme
"""
import sqlite3
import json
import sys
import os

# Agregar el directorio raíz al path para importar módulos de la app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def evaluate_uniform_sample():
    """Evaluar la extracción de CVs usando la muestra uniforme"""

    # Conectar a la base de datos de muestra
    sample_db = 'cv_simulator/cv_sample_uniform.db'
    if not os.path.exists(sample_db):
        print("❌ Base de datos de muestra no encontrada")
        return

    conn = sqlite3.connect(sample_db)
    cursor = conn.cursor()

    # Obtener muestra aleatoria de CVs
    cursor.execute("SELECT id, industry, cv_text, annotations FROM cv_dataset ORDER BY RANDOM() LIMIT 50")  # Muestra aleatoria
    rows = cursor.fetchall()

    print(f"🎯 Evaluando {len(rows)} CVs de la muestra uniforme")
    print("=" * 60)

    # Aquí iría el código para probar los extractores
    # Por ahora solo mostrar estadísticas básicas

    industries = {}
    for row in rows:
        cv_id, industry, cv_text, annotations = row
        industries[industry] = industries.get(industry, 0) + 1

    print("📊 COMPOSICIÓN DE LA MUESTRA:")
    for industry, count in sorted(industries.items(), key=lambda x: x[1], reverse=True):
        print(f"  {industry}: {count} CVs")

    print(f"\n✅ Muestra uniforme lista para evaluación")
    print(f"📁 Ubicación: {sample_db}")
    print(f"📊 Total CVs: {len(rows)}")

    conn.close()

if __name__ == "__main__":
    evaluate_uniform_sample()
