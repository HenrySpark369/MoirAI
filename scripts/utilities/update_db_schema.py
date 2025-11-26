#!/usr/bin/env python3
"""
Script para actualizar el esquema de la base de datos
Agrega los nuevos campos industry y seniority_level a la tabla students
"""

import asyncio
import logging
from sqlalchemy import text
from app.core.database import async_engine
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def update_database_schema():
    """Actualizar esquema de BD para agregar nuevos campos"""

    async with async_engine.begin() as conn:
        try:
            # Verificar si las columnas ya existen
            if "sqlite" in settings.DATABASE_URL:
                # SQLite: verificar columnas
                result = await conn.execute(text("""
                    PRAGMA table_info(student)
                """))
                columns_info = result.fetchall()
                columns = [row[1] for row in columns_info]
                column_constraints = {row[1]: row for row in columns_info}  # name -> full row

                # Verificar hashed_password - SQLite no soporta ALTER COLUMN fácilmente
                # Para este caso, asumimos que si existe la columna, está bien
                if "hashed_password" in columns:
                    logger.info("✅ Columna 'hashed_password' existe (SQLite)")
                
                if "industry" not in columns:
                    logger.info("➕ Agregando columna 'industry' a tabla student...")
                    await conn.execute(text("""
                        ALTER TABLE student ADD COLUMN industry VARCHAR(50)
                    """))

                if "seniority_level" not in columns:
                    logger.info("➕ Agregando columna 'seniority_level' a tabla student...")
                    await conn.execute(text("""
                        ALTER TABLE student ADD COLUMN seniority_level VARCHAR(20)
                    """))

            elif "postgresql" in settings.DATABASE_URL:
                # PostgreSQL: verificar y agregar columnas
                # Verificar y actualizar hashed_password para permitir NULL
                result = await conn.execute(text("""
                    SELECT column_name, is_nullable FROM information_schema.columns
                    WHERE table_name = 'student' AND column_name = 'hashed_password'
                """))
                row = result.fetchone()
                if row and row[1] == 'NO':  # is_nullable = 'NO' significa NOT NULL
                    logger.info("🔄 Cambiando columna 'hashed_password' para permitir NULL...")
                    await conn.execute(text("""
                        ALTER TABLE student ALTER COLUMN hashed_password DROP NOT NULL
                    """))
                
                # Verificar industry
                result = await conn.execute(text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'student' AND column_name = 'industry'
                """))
                if not result.fetchone():
                    logger.info("➕ Agregando columna 'industry' a tabla student...")
                    await conn.execute(text("""
                        ALTER TABLE student ADD COLUMN industry VARCHAR(50)
                    """))

                # Verificar seniority_level
                result = await conn.execute(text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'student' AND column_name = 'seniority_level'
                """))
                if not result.fetchone():
                    logger.info("➕ Agregando columna 'seniority_level' a tabla student...")
                    await conn.execute(text("""
                        ALTER TABLE student ADD COLUMN seniority_level VARCHAR(20)
                    """))

            await conn.commit()
            logger.info("✅ Esquema de base de datos actualizado exitosamente")

        except Exception as e:
            logger.error(f"❌ Error actualizando esquema: {e}")
            await conn.rollback()
            raise


async def main():
    """Función principal"""
    logger.info("🚀 Iniciando actualización del esquema de base de datos...")

    try:
        await update_database_schema()
        logger.info("✅ Actualización completada exitosamente")
    except Exception as e:
        logger.error(f"❌ Error en actualización: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
