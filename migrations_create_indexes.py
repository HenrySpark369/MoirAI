"""
Script para crear índices FULL TEXT en PostgreSQL
Ejecutar con: psql -d moirai_db -f create_indexes.sql
O desde Python:
    python -m alembic upgrade head
"""

# Alembic migration para indices FULL TEXT
migration_content = """
\"\"\"Create FULL TEXT indexes for job descriptions

Revision ID: 001_fulltext_indexes
Revises: 
Create Date: 2025-11-06

\"\"\"
from alembic import op
import sqlalchemy as sa


revision = '001_fulltext_indexes'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Crear índice FULL TEXT para descripción en español
    op.execute('''
        CREATE INDEX IF NOT EXISTS idx_job_description_fulltext 
        ON job_positions 
        USING GIN (to_tsvector('spanish', COALESCE(description, '')));
    ''')
    
    # Crear índices para campos de búsqueda común
    op.execute('''
        CREATE INDEX IF NOT EXISTS idx_job_title_company 
        ON job_positions(title, company) 
        WHERE is_active = true;
    ''')
    
    # Crear índice en location
    op.execute('''
        CREATE INDEX IF NOT EXISTS idx_job_location 
        ON job_positions(location) 
        WHERE is_active = true;
    ''')
    
    # Crear índice en skills (para matchmaking)
    op.execute('''
        CREATE INDEX IF NOT EXISTS idx_job_skills 
        ON job_positions(skills) 
        WHERE is_active = true;
    ''')
    
    # Crear índice en work_mode y job_type
    op.execute('''
        CREATE INDEX IF NOT EXISTS idx_job_mode_type 
        ON job_positions(work_mode, job_type) 
        WHERE is_active = true;
    ''')
    
    # Crear índice en external_job_id para scraping
    op.execute('''
        CREATE INDEX IF NOT EXISTS idx_job_external_id 
        ON job_positions(external_job_id, source) 
        WHERE is_active = true;
    ''')


def downgrade():
    # Remover índices
    op.execute('DROP INDEX IF EXISTS idx_job_description_fulltext;')
    op.execute('DROP INDEX IF EXISTS idx_job_title_company;')
    op.execute('DROP INDEX IF EXISTS idx_job_location;')
    op.execute('DROP INDEX IF EXISTS idx_job_skills;')
    op.execute('DROP INDEX IF EXISTS idx_job_mode_type;')
    op.execute('DROP INDEX IF EXISTS idx_job_external_id;')
"""

# SQL directo para ejecutar en psql
sql_direct = """
-- Crear índice FULL TEXT para búsquedas de descripción (español)
CREATE INDEX IF NOT EXISTS idx_job_description_fulltext 
ON job_positions 
USING GIN (to_tsvector('spanish', COALESCE(description, '')));

-- Crear índices para búsquedas comunes
CREATE INDEX IF NOT EXISTS idx_job_title_company 
ON job_positions(title, company) 
WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_job_location 
ON job_positions(location) 
WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_job_skills 
ON job_positions(skills) 
WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_job_mode_type 
ON job_positions(work_mode, job_type) 
WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_job_external_id 
ON job_positions(external_job_id, source) 
WHERE is_active = true;

-- Analizar tabla para optimizar query planner
ANALYZE job_positions;

-- Verificar que los índices fueron creados
SELECT indexname FROM pg_indexes 
WHERE tablename = 'job_positions' 
ORDER BY indexname;
"""

if __name__ == "__main__":
    print("="*70)
    print("📝 SQL para crear índices FULL TEXT en PostgreSQL")
    print("="*70)
    print(sql_direct)
    print("\n" + "="*70)
    print("✅ Copia y ejecuta el SQL anterior en psql")
    print("="*70)
