#!/bin/bash

# ============================================================================
# SCRIPT: Stage de Tests Validados
# Propósito: Stagear todos los tests válidos identificados en validación
# ============================================================================

echo ""
echo "🚀 INICIANDO STAGING DE TESTS VALIDADOS"
echo "============================================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

STAGED_COUNT=0
FAILED_COUNT=0

# Función para stagear archivo con verificación
stage_file() {
    local file="$1"
    local description="$2"
    
    if [ -f "$file" ]; then
        git add "$file"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅${NC} STAGED: $file"
            echo "   📝 $description"
            ((STAGED_COUNT++))
        else
            echo -e "${RED}❌${NC} ERROR staging: $file"
            ((FAILED_COUNT++))
        fi
    else
        echo -e "${RED}⚠️ ${NC} FILE NOT FOUND: $file"
        ((FAILED_COUNT++))
    fi
}

echo ""
echo "📋 STAGING TESTS CRÍTICOS (Matching)"
echo "────────────────────────────────────────────────────────────────────────────"
stage_file "tests/unit/test_matching_service.py" "14 tests - Lógica de matching"
stage_file "tests/integration/test_matching_endpoints.py" "E2E - Endpoints de matching"
stage_file "test_phase3_task2_matching_endpoint.py" "10 tests - Email search con hash"
stage_file "test_recommendations_fix.py" "Regression - Feature específica"

echo ""
echo "🔐 STAGING TESTS IMPORTANTES (Encryption)"
echo "────────────────────────────────────────────────────────────────────────────"
stage_file "tests/unit/test_encryption_service.py" "21 tests - Encriptación/Desencriptación"
stage_file "test_encryption_phase1_integration.py" "Phase 1 - Integración en models"
stage_file "test_encryption_phase2_endpoints.py" "Phase 2 - Endpoints encriptados"
stage_file "test_encryption_phase3_advanced_searches.py" "Phase 3 - Búsquedas avanzadas"

echo ""
echo "🔒 STAGING TESTS IMPORTANTES (Rate Limiting)"
echo "────────────────────────────────────────────────────────────────────────────"
stage_file "tests/unit/test_rate_limiting.py" "20+ tests - Middleware rate limiting"

echo ""
echo "📤 STAGING TESTS ADICIONALES (Resume Upload)"
echo "────────────────────────────────────────────────────────────────────────────"
stage_file "tests/integration/test_upload_resume_update.py" "Resume endpoints"

echo ""
echo "============================================================================"
echo ""

# Resumen
echo -e "${GREEN}✅ TESTS STAGED: $STAGED_COUNT${NC}"
if [ $FAILED_COUNT -gt 0 ]; then
    echo -e "${RED}❌ FAILED: $FAILED_COUNT${NC}"
fi

echo ""
echo "📊 STATUS GIT:"
git status --short | grep "^A" | head -15
echo ""

# Mostrar recomendación de commit
echo "═══════════════════════════════════════════════════════════════════════════"
echo "🎯 PRÓXIMO PASO: Crear commit"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "git commit -m \"Add validated unit and integration tests"
echo ""
echo "Tests incluidos:"
echo "- Matching service: 14 tests"
echo "- Matching endpoints: Full e2e"
echo "- Email search (Phase 3 Task 2): 10 tests"
echo "- Encryption service: 21 tests"
echo "- Encryption phases (1-3): Integration + endpoints + advanced searches"
echo "- Rate limiting: 20+ tests"
echo "- Resume upload endpoints: Integration"
echo ""
echo "Coverage: ~150+ tests across 10 files\""
echo ""
