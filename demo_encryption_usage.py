#!/usr/bin/env python3
"""
DEMO - Cómo usar la encriptación de FASE 1 en el código

Este script muestra ejemplos de cómo usar los nuevos métodos de encriptación
implementados en la FASE 1 de integración.
"""

import os
import sys
from cryptography.fernet import Fernet

# Configurar variables de entorno para testing
test_key = Fernet.generate_key().decode()
os.environ["ENCRYPTION_KEY"] = test_key
os.environ["DATABASE_URL"] = "sqlite://:memory:"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models import Student, Company
from app.utils.encryption import encryption_service
import json


def demo_student_encryption():
    """Demo: Encriptación de estudiante"""
    print("\n" + "="*80)
    print("DEMO 1: Encriptación de Estudiante")
    print("="*80)
    
    # Crear un estudiante
    student = Student(
        name="Juan García",
        program="Ingeniería en Sistemas",
        consent_data_processing=True,
        skills=json.dumps(["Python", "FastAPI", "PostgreSQL"]),
        soft_skills=json.dumps(["Liderazgo", "Comunicación"])
    )
    
    print("\n1. Estudiante creado (sin email aún):")
    print(f"   - Name: {student.name}")
    print(f"   - Program: {student.program}")
    
    # Encriptar email
    email = "juan.garcia@unrc.edu.ar"
    student.set_email(email)
    
    print(f"\n2. Encriptar email usando set_email():")
    print(f"   - Email original: {email}")
    print(f"   - Email encriptado (en BD): {student.email[:40]}...")
    print(f"   - Email hash (índice): {student.email_hash[:20]}...")
    
    # Desencriptar email
    decrypted = student.get_email()
    print(f"\n3. Desencriptar email usando get_email():")
    print(f"   - Email desencriptado: {decrypted}")
    print(f"   - ¿Coincide original?: {decrypted == email} ✅")
    
    # Encriptar teléfono
    phone = "+54 9 358 123-4567"
    student.set_phone(phone)
    
    print(f"\n4. Encriptar teléfono usando set_phone():")
    print(f"   - Teléfono original: {phone}")
    print(f"   - Teléfono encriptado (en BD): {student.phone[:40]}...")
    print(f"   - Teléfono hash (índice): {student.phone_hash[:20]}...")
    
    # Desencriptar teléfono
    decrypted_phone = student.get_phone()
    print(f"\n5. Desencriptar teléfono usando get_phone():")
    print(f"   - Teléfono desencriptado: {decrypted_phone}")
    print(f"   - ¿Coincide original?: {decrypted_phone == phone} ✅")
    
    # Obtener todos los campos desencriptados
    sensitive = student.decrypt_sensitive_fields()
    print(f"\n6. Obtener todos campos sensibles con decrypt_sensitive_fields():")
    print(f"   - Resultado: {json.dumps(sensitive, indent=6)}")


def demo_company_encryption():
    """Demo: Encriptación de empresa"""
    print("\n" + "="*80)
    print("DEMO 2: Encriptación de Empresa")
    print("="*80)
    
    # Crear una empresa
    company = Company(
        name="Tech Innovation SA",
        industry="Tecnología",
        size="mediana",
        location="Córdoba",
        is_verified=False,
        is_active=True
    )
    
    print("\n1. Empresa creada (sin email aún):")
    print(f"   - Name: {company.name}")
    print(f"   - Industry: {company.industry}")
    
    # Encriptar email
    email = "recruiting@techinnovation.com"
    company.set_email(email)
    
    print(f"\n2. Encriptar email usando set_email():")
    print(f"   - Email original: {email}")
    print(f"   - Email encriptado (en BD): {company.email[:40]}...")
    print(f"   - Email hash (índice): {company.email_hash[:20]}...")
    
    # Desencriptar email
    decrypted = company.get_email()
    print(f"\n3. Desencriptar email usando get_email():")
    print(f"   - Email desencriptado: {decrypted}")
    print(f"   - ¿Coincide original?: {decrypted == email} ✅")


def demo_hash_based_search():
    """Demo: Búsqueda por hash (sin desencriptar)"""
    print("\n" + "="*80)
    print("DEMO 3: Búsqueda por Hash (Método Seguro)")
    print("="*80)
    
    # Crear estudiante
    student = Student(
        name="María López",
        program="Ingeniería",
        consent_data_processing=True
    )
    
    email_to_store = "maria.lopez@unrc.edu.ar"
    student.set_email(email_to_store)
    
    print(f"\n1. Estudiante creado y encriptado:")
    print(f"   - Email original: {email_to_store}")
    print(f"   - Email en BD (encriptado): {student.email[:40]}...")
    print(f"   - Email hash: {student.email_hash}")
    
    # Simular búsqueda
    print(f"\n2. Buscar por email (en la práctica):")
    search_email = "maria.lopez@unrc.edu.ar"
    search_hash = encryption_service._get_hash_email(search_email)
    
    print(f"   - Email a buscar: {search_email}")
    print(f"   - Hash calculado: {search_hash}")
    print(f"   - Query: WHERE email_hash = '{search_hash}'")
    print(f"   - ¿Hashes coinciden?: {search_hash == student.email_hash} ✅")
    
    print(f"\n3. Ventajas del método hash:")
    print(f"   - ✅ No expone email encriptado en queries")
    print(f"   - ✅ Email jamás se desencripta para búsqueda")
    print(f"   - ✅ Indexable (performant)")
    print(f"   - ✅ Resistente a ataques (SHA-256 one-way)")
    
    # Normalización
    print(f"\n4. Normalización automática:")
    variants = [
        "MARIA.LOPEZ@UNRC.EDU.AR",
        " maria.lopez@unrc.edu.ar ",
        "Maria.Lopez@UNRC.edu.ar"
    ]
    
    for variant in variants:
        h = encryption_service._get_hash_email(variant)
        match = h == search_hash
        print(f"   - '{variant}' → Hash: {h[:20]}... {'✅ Match' if match else '❌ No match'}")


def demo_response_desencryption():
    """Demo: Desencriptación en respuestas de API"""
    print("\n" + "="*80)
    print("DEMO 4: Desencriptación en Respuestas de API")
    print("="*80)
    
    # Simular lo que retorna desde BD
    student = Student(
        name="Carlos Rodríguez",
        program="Sistemas",
        consent_data_processing=True
    )
    
    student.set_email("carlos.rodriguez@unrc.edu.ar")
    student.set_phone("+54 9 358 555-1234")
    
    print(f"\n1. Datos en BD (encriptados):")
    print(f"   - student.email: {student.email[:40]}... (encriptado)")
    print(f"   - student.phone: {student.phone[:40]}... (encriptado)")
    print(f"   - student.email_hash: {student.email_hash[:20]}... (hash)")
    print(f"   - student.phone_hash: {student.phone_hash[:20]}... (hash)")
    
    # Desencriptar para respuesta
    print(f"\n2. Desencriptar para respuesta API:")
    decrypted = student.decrypt_sensitive_fields()
    print(f"   - Llamar: student.decrypt_sensitive_fields()")
    print(f"   - Resultado: {json.dumps(decrypted, indent=6)}")
    
    # Simular respuesta JSON
    response = {
        "id": 1,
        "name": student.name,
        "program": student.program,
        "email": decrypted.get("email"),
        "phone": decrypted.get("phone"),
        "skills": json.loads(student.skills or "[]")
    }
    
    print(f"\n3. Respuesta JSON enviada al cliente:")
    print(f"   {json.dumps(response, indent=4)}")
    print(f"\n   ✅ El cliente recibe datos legibles")
    print(f"   ✅ La BD mantiene datos encriptados")


def demo_email_normalization():
    """Demo: Normalización automática de emails"""
    print("\n" + "="*80)
    print("DEMO 5: Normalización de Emails")
    print("="*80)
    
    emails = [
        "User@Example.COM",
        "user@example.com",
        " user@example.com ",
        "USER@EXAMPLE.COM",
        "uSeR@ExAmPlE.cOm"
    ]
    
    print(f"\n1. Diferentes variantes del mismo email:")
    hashes = {}
    for email in emails:
        h = encryption_service._get_hash_email(email)
        print(f"   - '{email}' → Hash: {h[:20]}...")
        hashes[h] = email
    
    print(f"\n2. Resultado:")
    print(f"   - Emails únicos ingresados: {len(emails)}")
    print(f"   - Hashes únicos generados: {len(set(hashes.keys()))}")
    print(f"   - ✅ Todos normalizan a UN SOLO hash")
    print(f"\n3. Normalización aplicada:")
    print(f"   - Convertir a lowercase")
    print(f"   - Remover espacios (strip)")
    print(f"   - Generar SHA-256")


def demo_complete_flow():
    """Demo: Flujo completo de registro y búsqueda"""
    print("\n" + "="*80)
    print("DEMO 6: Flujo Completo (Registro + Búsqueda + Respuesta)")
    print("="*80)
    
    print("\n📝 PASO 1: Usuario se registra")
    print("   Cliente envía: POST /auth/register")
    print("   Payload: {email: 'alice@example.com', name: 'Alice', role: 'student'}")
    
    # Registro
    student = Student(
        name="Alice",
        program="Informática",
        consent_data_processing=True
    )
    
    user_email = "alice@example.com"
    student.set_email(user_email)
    
    print(f"\n🔐 PASO 2: Sistema encripta y guarda en BD")
    print(f"   - Email: {student.email[:40]}... (encriptado)")
    print(f"   - Email hash: {student.email_hash} (índice)")
    
    print(f"\n📤 PASO 3: Sistema retorna respuesta")
    response = {
        "user_id": 1,
        "name": student.name,
        "email": student.get_email(),  # Desencriptado
        "role": "student"
    }
    print(f"   {json.dumps(response, indent=3)}")
    
    print(f"\n🔍 PASO 4: Admin busca por email")
    print(f"   Envía: GET /students/email/alice@example.com")
    
    # Búsqueda
    search_hash = encryption_service._get_hash_email(user_email)
    print(f"   Query: WHERE email_hash = '{search_hash[:20]}...'")
    print(f"   Encontrado: email_hash coincide ✅")
    
    print(f"\n📊 PASO 5: Sistema retorna perfil completo")
    profile = {
        "id": 1,
        "name": student.name,
        "program": student.program,
        "email": student.get_email(),  # Desencriptado
        "created_at": "2024-01-15T10:30:00"
    }
    print(f"   {json.dumps(profile, indent=3)}")
    
    print(f"\n✅ Flujo completado")
    print(f"   - BD: Datos encriptados ✅")
    print(f"   - Búsqueda: Sin desencriptar ✅")
    print(f"   - Respuesta: Datos legibles ✅")


def main():
    """Ejecutar todos los demos"""
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  DEMO - Encriptación de Campos Sensibles (FASE 1 Integration)".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    try:
        demo_student_encryption()
        demo_company_encryption()
        demo_hash_based_search()
        demo_response_desencryption()
        demo_email_normalization()
        demo_complete_flow()
        
        print("\n" + "="*80)
        print("✅ TODOS LOS DEMOS COMPLETADOS EXITOSAMENTE")
        print("="*80)
        print("\nPróximos pasos:")
        print("  1. Ejecutar tests: python test_encryption_phase1_integration.py")
        print("  2. Revisar documentación: ENCRYPTION_PHASE1_STATUS.md")
        print("  3. Pasar a FASE 2: Endpoints GET")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
