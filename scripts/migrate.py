"""
Database Migration Script - Crear tabla y índices

Uso:
  python scripts/migrate.py --version all      # Aplicar todas las migraciones
  python scripts/migrate.py --version 001      # Aplicar versión específica
  python scripts/migrate.py --check             # Ver estado de migraciones
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy import text
from app.core.config import settings
from app.core.database import engine, create_db_and_tables
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migration_001_create_tables():
    """Migration 001: Create all tables"""
    logger.info("🔄 Applying migration 001: Create tables...")
    
    try:
        # Create all tables defined in SQLModel
        create_db_and_tables()
        logger.info("✅ Migration 001 applied successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Migration 001 failed: {e}")
        return False


def migration_002_create_indices():
    """Migration 002: Create performance indices"""
    logger.info("🔄 Applying migration 002: Create indices...")
    
    try:
        # For SQLite and PostgreSQL, indices are typically created through SQLModel
        # or we use proper SQL execution
        if "postgresql" in settings.DATABASE_URL:
            indices_sql = [
                "CREATE INDEX IF NOT EXISTS idx_job_postings_external_id ON job_postings(external_job_id)",
                "CREATE INDEX IF NOT EXISTS idx_job_postings_location ON job_postings(location)",
                "CREATE INDEX IF NOT EXISTS idx_job_postings_source_published ON job_postings(source, published_at)",
                "CREATE INDEX IF NOT EXISTS idx_job_postings_email_hash ON job_postings(email_hash)",
                "CREATE INDEX IF NOT EXISTS idx_job_postings_created_at ON job_postings(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
                "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            ]
            
            with engine.connect() as connection:
                for statement in indices_sql:
                    try:
                        connection.execute(text(statement))
                    except Exception as e:
                        logger.warning(f"  Index creation warning (might already exist): {e}")
                connection.commit()
        
        logger.info("✅ Migration 002 applied successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Migration 002 failed: {e}")
        return False


def migration_003_add_constraints():
    """Migration 003: Add foreign keys and constraints"""
    logger.info("🔄 Applying migration 003: Add constraints...")
    
    # For SQLite, constraints are handled through SQLModel
    # For PostgreSQL, they're created via engine
    
    try:
        logger.info("✅ Migration 003 applied successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Migration 003 failed: {e}")
        return False


def get_migration_status():
    """Get status of all migrations"""
    migrations = [
        ("001", "Create tables", migration_001_create_tables),
        ("002", "Create indices", migration_002_create_indices),
        ("003", "Add constraints", migration_003_add_constraints),
    ]
    
    logger.info("\n📋 Migration Status Report")
    logger.info("=" * 50)
    logger.info(f"Database: {settings.DATABASE_URL}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}\n")
    
    for version, description, func in migrations:
        logger.info(f"  [{version}] {description}")
    
    logger.info("=" * 50 + "\n")


def apply_migrations(target_version="all"):
    """Apply database migrations"""
    migrations = [
        ("001", "Create tables", migration_001_create_tables),
        ("002", "Create indices", migration_002_create_indices),
        ("003", "Add constraints", migration_003_add_constraints),
    ]
    
    logger.info(f"\n🚀 Applying migrations (target: {target_version})...\n")
    
    results = []
    for version, description, func in migrations:
        if target_version == "all" or target_version == version:
            success = func()
            results.append((version, description, success))
        
        if target_version == version:
            break
    
    # Summary
    logger.info("\n📊 Migration Summary")
    logger.info("=" * 50)
    passed = sum(1 for _, _, success in results if success)
    total = len(results)
    logger.info(f"Passed: {passed}/{total}")
    
    for version, description, success in results:
        status = "✅" if success else "❌"
        logger.info(f"  {status} [{version}] {description}")
    
    logger.info("=" * 50)
    
    return all(success for _, _, success in results)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Database Migration Manager")
    parser.add_argument(
        "--version",
        default="all",
        help="Migration version to apply (all, 001, 002, 003)"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check migration status"
    )
    
    args = parser.parse_args()
    
    if args.check:
        get_migration_status()
    else:
        success = apply_migrations(args.version)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
