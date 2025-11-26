#!/usr/bin/env python3
"""
Script simple para crear un usuario admin de prueba
"""
import sys
import asyncio
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.database import async_engine
from app.services.auth_service import auth_service
from app.services.api_key_service import api_key_service
from app.schemas import ApiKeyCreate
from sqlalchemy.ext.asyncio import AsyncSession

async def get_or_create_test_admin():
    """Obtener o crear admin de prueba"""
    async with AsyncSession(async_engine) as session:
        try:
            # Buscar usuario existente
            user, user_type = await auth_service.find_user_by_email(session, "admin@test.com")

            if user:
                print("✅ Admin de prueba encontrado!")
                # Buscar API key existente
                from app.models import ApiKey
                from sqlmodel import select

                result = await session.execute(
                    select(ApiKey).where(
                        (ApiKey.user_id == user.id) &
                        (ApiKey.user_type == user_type) &
                        (ApiKey.is_active == True)
                    ).order_by(ApiKey.created_at.desc())
                )
                api_key_record = result.scalars().first()

                if api_key_record:
                    print(f"🔑 API Key existente encontrada:")
                    print(f"   Key ID:   {api_key_record.key_id}")
                    print(f"   Prefijo:  {api_key_record.key_prefix}")
                    print(f"   Expira:   {api_key_record.expires_at}")
                    # La API key completa sería key_id + "_" + secret, pero el secret está hasheado
                    # Necesito crear una nueva
                    print("   Creando nueva API key...")

            # Crear nueva API key si no existe o queremos una nueva
            api_key_data = ApiKeyCreate(
                name="Clave de prueba - Test Admin",
                description="API key para pruebas de integración",
                expires_days=365
            )

            api_key_response = await api_key_service.create_api_key(
                session=session,
                user_id=user.id if user else None,
                user_type=user_type if user else "admin",
                user_email="admin@test.com",
                key_data=api_key_data
            )

            print("✅ API Key creada exitosamente!")
            print(f"📋 Datos de acceso:")
            print(f"   Email:    admin@test.com")
            print(f"   Password: TestPass123!")
            print(f"   Rol:      admin")
            print(f"\n🔑 API Key:")
            print(f"   Key ID:   {api_key_response.key_info.key_id}")
            print(f"   Prefijo:  {api_key_response.key_info.key_prefix}")
            print(f"   Expira:   {api_key_response.key_info.expires_at}")
            print(f"   API Key completa: {api_key_response.api_key}")

            return api_key_response.api_key

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return None

if __name__ == "__main__":
    api_key = asyncio.run(get_or_create_test_admin())
    if api_key:
        print(f"\n🔑 API Key completa para usar en pruebas: {api_key}")
    else:
        print("\n❌ No se pudo obtener la API key del admin de prueba")
