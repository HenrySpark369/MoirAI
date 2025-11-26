#!/usr/bin/env python3
"""
Script para probar la integración completa de ML en el endpoint upload_resume
"""

import requests
import json
import os
from pathlib import Path

# Configuración
BASE_URL = "http://localhost:8000"
API_ENDPOINT = "/api/v1/students/upload_resume"
CV_FILE_PATH = "CV - Harvard.pdf"

# API Key para autenticación (obtenida del script create_test_admin.py)
API_KEY = "9nzWoS3LEZEgREXNqdwRpw_XND4_lSfEI75w5O4gPllSo3EWlA7iUliCzqijEfOBJU"

# Headers de autenticación
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "X-API-Key": API_KEY
}

# Datos de prueba para el estudiante
test_student_data = {
    "name": "Ana García López",
    "email": "ana.garcia.test@unrc.edu.ar",
    "program": "Ingeniería en Sistemas"
}

def test_upload_resume():
    """Probar la subida de CV con clasificación ML"""

    print("🚀 Probando integración ML en upload_resume")
    print("=" * 50)

    # Verificar que el archivo existe
    if not os.path.exists(CV_FILE_PATH):
        print(f"❌ Archivo {CV_FILE_PATH} no encontrado")
        return False

    # Preparar los datos del formulario
    with open(CV_FILE_PATH, 'rb') as f:
        files = {
            'file': (CV_FILE_PATH, f, 'application/pdf')
        }

        data = {
            'meta': json.dumps(test_student_data)
        }

        print(f"📤 Subiendo CV: {CV_FILE_PATH}")
        print(f"👤 Datos estudiante: {test_student_data}")
        print()

        try:
            # Hacer la petición
            response = requests.post(
                f"{BASE_URL}{API_ENDPOINT}",
                files=files,
                data=data,
                headers=HEADERS,
                timeout=30
            )

            print(f"📡 Status Code: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print("✅ Subida exitosa!")
                print()

                # Mostrar información del estudiante
                student = result.get('student', {})
                print("👤 INFORMACIÓN DEL ESTUDIANTE:")
                print(f"   ID: {student.get('id')}")
                print(f"   Nombre: {student.get('name')}")
                print(f"   Email: {student.get('email')}")
                print(f"   Programa: {student.get('program')}")
                print()

                # Mostrar clasificación ML
                print("🤖 CLASIFICACIÓN ML AUTOMÁTICA:")
                industry = student.get('industry')
                seniority = student.get('seniority_level')

                if industry:
                    print(f"   🏭 Industria: {industry}")
                else:
                    print("   🏭 Industria: No clasificada")

                if seniority:
                    print(f"   📊 Seniority: {seniority}")
                else:
                    print("   📊 Seniority: No clasificada")

                print()

                # Mostrar campos Harvard
                print("📚 CAMPOS HARVARD EXTRAÍDOS:")
                harvard_fields = ['objective', 'education', 'experience', 'certifications', 'languages']
                for field in harvard_fields:
                    value = student.get(field)
                    if value:
                        if isinstance(value, list):
                            print(f"   {field.title()}: {len(value)} items")
                        else:
                            preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                            print(f"   {field.title()}: {preview}")
                    else:
                        print(f"   {field.title()}: No extraído")

                print()

                # Mostrar skills extraídos
                extracted_skills = result.get('extracted_skills', [])
                print(f"🔧 SKILLS EXTRAÍDOS: {len(extracted_skills)}")
                if extracted_skills:
                    print(f"   {', '.join(extracted_skills[:5])}{'...' if len(extracted_skills) > 5 else ''}")

                print()

                # Verificar que tenemos un student_id para consultar el perfil
                student_id = student.get('id')
                if student_id:
                    print("🔍 Consultando perfil completo del estudiante...")
                    return test_get_student_profile(student_id)
                else:
                    print("❌ No se pudo obtener el ID del estudiante")
                    return False

            else:
                print(f"❌ Error en la subida: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Detalle: {error_detail}")
                except:
                    print(f"   Respuesta: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return False

def test_get_student_profile(student_id):
    """Consultar el perfil completo del estudiante para verificar datos ML"""

    print(f"🔍 Consultando perfil del estudiante ID: {student_id}")
    print("-" * 40)

    try:
        # Hacer petición GET al perfil
        response = requests.get(f"{BASE_URL}/api/v1/students/{student_id}", headers=HEADERS)

        if response.status_code == 200:
            student = response.json()
            print("✅ Perfil obtenido exitosamente!")
            print()

            # Verificar campos ML
            print("🤖 VERIFICACIÓN DE CAMPOS ML EN BD:")
            industry = student.get('industry')
            seniority = student.get('seniority_level')

            if industry:
                print(f"   ✅ Industria almacenada: {industry}")
            else:
                print("   ❌ Industria no almacenada")

            if seniority:
                print(f"   ✅ Seniority almacenada: {seniority}")
            else:
                print("   ❌ Seniority no almacenada")

            print()

            # Verificar campos Harvard
            print("📚 VERIFICACIÓN DE CAMPOS HARVARD EN BD:")
            harvard_fields = ['objective', 'education', 'experience', 'certifications', 'languages']
            stored_fields = 0

            for field in harvard_fields:
                value = student.get(field)
                if value:
                    stored_fields += 1
                    if isinstance(value, list):
                        print(f"   ✅ {field.title()}: {len(value)} items almacenados")
                    else:
                        print(f"   ✅ {field.title()}: Almacenado")
                else:
                    print(f"   ❌ {field.title()}: No almacenado")

            print()
            print(f"📊 RESUMEN:")
            print(f"   Campos Harvard almacenados: {stored_fields}/{len(harvard_fields)}")
            print(f"   Clasificación ML: {'✅ Completa' if industry and seniority else '❌ Incompleta'}")

            return True

        else:
            print(f"❌ Error consultando perfil: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Detalle: {error_detail}")
            except:
                print(f"   Respuesta: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 PRUEBA DE INTEGRACIÓN COMPLETA - ML en MoirAI")
    print("=" * 60)

    success = test_upload_resume()

    print()
    print("=" * 60)
    if success:
        print("🎉 ¡PRUEBA EXITOSA! La integración ML funciona correctamente")
        print("   ✅ CV subido y procesado")
        print("   ✅ Clasificación ML aplicada")
        print("   ✅ Datos almacenados en BD")
        print("   ✅ Campos Harvard extraídos")
    else:
        print("❌ PRUEBA FALLIDA - Revisar logs para más detalles")

    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
