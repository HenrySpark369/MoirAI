import sqlite3
import json
import sys
import os

# Agregar root al path para importar servicios de la app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.unsupervised_cv_extractor import UnsupervisedCVExtractor
from app.services.cv_extractor_v2_spacy import CVExtractorV2

def test_extraction():
    DB_PATH = 'cv_simulator/training_data_cvs.db'
    
    if not os.path.exists(DB_PATH):
        print(f"❌ No se encontró la base de datos en {DB_PATH}")
        print("Ejecuta primero generate_cvs.py para crear datos.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Obtener 3 CVs de muestra
    cursor.execute("SELECT id, cv_text, annotations FROM cv_dataset ORDER BY RANDOM() LIMIT 3")
    rows = cursor.fetchall()
    
    if not rows:
        print("⚠️ La base de datos está vacía.")
        return

    # Inicializar extractores
    print("🔧 Inicializando extractores...")
    extractor_v1 = UnsupervisedCVExtractor()
    extractor_v2 = CVExtractorV2()
    
    print("\n" + "="*60)
    print("🧪 TEST DE EXTRACCIÓN: SINTÉTICO vs EXTRACTORES")
    print("="*60)

    for row in rows:
        cv_id, cv_text, annotations_json = row
        ground_truth = json.loads(annotations_json)
        
        print(f"\n📄 CV ID: {cv_id}")
        print(f"👤 Perfil Esperado: {ground_truth.get('name', 'N/A')} - {ground_truth.get('current_role', 'N/A')}")
        
        # Extracción V1
        result_v1 = extractor_v1.extract(cv_text)
        
        # Extracción V2
        result_v2 = extractor_v2.extract_to_dict(cv_text)
        
        # Comparación Simple (Skills)
        gt_skills = set(ground_truth.get('skills', []))
        v1_skills = set(result_v1.skills or [])
        v2_skills = set(result_v2.get('skills', []) or [])
        
        print(f"\n--- Comparativa de Skills ---")
        print(f"✅ Ground Truth ({len(gt_skills)}): {', '.join(list(gt_skills)[:5])}...")
        print(f"1️⃣ V1 Unsupervised ({len(v1_skills)}): {', '.join(list(v1_skills)[:5])}...")
        print(f"2️⃣ V2 SpaCy ({len(v2_skills)}): {', '.join(list(v2_skills)[:5])}...")
        
        # Calcular intersección (Recall simple)
        if gt_skills:
            recall_v1 = len(gt_skills.intersection(v1_skills)) / len(gt_skills) * 100
            recall_v2 = len(gt_skills.intersection(v2_skills)) / len(gt_skills) * 100
            print(f"📊 Recall V1: {recall_v1:.1f}% | Recall V2: {recall_v2:.1f}%")
        
        print("-" * 30)

    conn.close()

if __name__ == "__main__":
    test_extraction()
