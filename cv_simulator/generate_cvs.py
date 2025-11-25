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

# El Prompt Maestro (Optimizado para 1 CV a la vez)
PROMPT_MAESTRO = """
**System Role:**
Eres un generador de datos sintéticos experto en Recursos Humanos y NLP.

**Instrucción:**
Genera **UN (1)** perfil profesional ficticio en formato JSON que se ajuste al esquema `StudentProfile` de MoirAI.
Variabilidad requerida: Industria, Seniority, Universidad, Género.

**Formato de Salida (JSON Puro):**
Devuelve SOLO el objeto JSON (sin markdown, sin lista).

```json
{
  "metadata": {
    "industry": "Tecnología",
    "seniority": "Senior",
    "profile_id": "uuid_simulado"
  },
  "cv_text": "NOMBRE: Juan Pérez\\n...",
  "annotations": {
    "name": "Juan Pérez",
    "email": "juan.perez@email.com",
    "phone": "555-0123",
    "location": "Ciudad de México",
    "bio": "Ingeniero...",
    "objective": "...",
    "education": [{"institution": "UNAM", "degree": "Ingeniería", "start_date": "2010", "end_date": "2015"}],
    "experience": [{"company": "Tech", "position": "Dev", "start_date": "2018", "end_date": "Presente", "description": "..."}],
    "skills": ["Python", "React"],
    "soft_skills": ["Liderazgo"],
    "languages": ["Español"],
    "projects": ["App"]
  }
}
```
"""

def generate_profile():
    try:
        print(f"⏳ Solicitando perfil al modelo {MODEL_ID}...")
        start_time = time.time()
        
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": PROMPT_MAESTRO}
            ],
            temperature=0.9,
            max_tokens=2000, # Límite de seguridad
            timeout=60,      # Timeout para evitar bloqueos
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
        except json.JSONDecodeError:
            print("❌ Error decodificando JSON.")
            return None
            
    except Exception as e:
        print(f"❌ Error generando perfil: {e}")
        return None

def main():
    # Bucle infinito (o hasta llegar a N)
    OBJETIVO = 1000
    
    # Verificar cuántos tenemos ya
    cursor.execute("SELECT COUNT(*) FROM cv_dataset")
    total_generados = cursor.fetchone()[0]
    
    print(f"🚀 Iniciando minería de CVs sintéticos (Modo Estable: 1 a la vez).")
    print(f"🎯 Objetivo: {OBJETIVO}")
    print(f"📊 Actual: {total_generados}")
    print(f"🤖 Modelo: {MODEL_ID} @ {API_BASE_URL}")
    print("-" * 50)

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
                
            cursor.execute('''
                INSERT INTO cv_dataset (id, industry, seniority, cv_text, annotations)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                unique_id, 
                item.get('metadata', {}).get('industry', 'Unknown'), 
                item.get('metadata', {}).get('seniority', 'Unknown'), 
                item['cv_text'], 
                json.dumps(item['annotations']) 
            ))
            
            conn.commit()
            total_generados += 1
            print(f"💾 Guardado 1 CV. Progreso total: {total_generados}/{OBJETIVO}")
            
        except Exception as e:
            print(f"Error insertando item: {e}")
        
        # Pausa breve para dejar respirar al servidor local
        time.sleep(0.2)

    conn.close()
    print("🎉 ¡Entrenamiento listo! Base de datos completada.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Detenido por el usuario. Datos guardados.")
        conn.close()
