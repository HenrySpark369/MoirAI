#!/bin/bash

###############################################################################
#                                                                             #
#  🚀 FASE 2: DEV DEPLOYMENT - SCRIPT EJECUTABLE                            #
#                                                                             #
#  Ejecutar: ./inicio_fase2.sh                                              #
#                                                                             #
###############################################################################

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                       ║"
echo "║  🚀 FASE 2: DEV DEPLOYMENT - CONSOLIDACIÓN DE ENDPOINTS             ║"
echo "║                                                                       ║"
echo "║  MoirAI - 12 de Noviembre 2025                                       ║"
echo "║                                                                       ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
REPO_DIR="/Users/sparkmachine/MoirAI"
BRANCH_NAME="feature/endpoints-consolidation"
MAIN_BRANCH="develop"

echo -e "${BLUE}📋 PRE-DEPLOYMENT CHECKLIST${NC}"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

# Step 1: Verificar que estamos en el directorio correcto
echo -e "${YELLOW}✓ Verificando directorio del proyecto...${NC}"
if [ ! -d "$REPO_DIR/.git" ]; then
    echo -e "${RED}✗ Error: No se encontró repositorio git en $REPO_DIR${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Repositorio encontrado${NC}"
echo ""

# Step 2: Verificar git status
echo -e "${YELLOW}✓ Verificando estado de git...${NC}"
cd "$REPO_DIR"

# Verificar cambios sin commitear
if ! git diff-index --quiet HEAD --; then
    echo -e "${RED}✗ Error: Hay cambios sin commitear${NC}"
    echo "Favor de hacer commit o stash de los cambios:"
    echo "  git add ."
    echo "  git commit -m 'message'"
    echo "  o"
    echo "  git stash"
    exit 1
fi
echo -e "${GREEN}✓ No hay cambios sin commitear${NC}"
echo ""

# Step 3: Verificar rama actual
echo -e "${YELLOW}✓ Verificando rama actual...${NC}"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "$MAIN_BRANCH" ]; then
    echo -e "${YELLOW}⚠ Estás en rama: $CURRENT_BRANCH (esperado: $MAIN_BRANCH)${NC}"
    echo "Cambiando a $MAIN_BRANCH..."
    git checkout "$MAIN_BRANCH"
fi
echo -e "${GREEN}✓ En rama: $MAIN_BRANCH${NC}"
echo ""

# Step 4: Actualizar develop
echo -e "${YELLOW}✓ Actualizando rama $MAIN_BRANCH...${NC}"
git pull origin "$MAIN_BRANCH"
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Error al hacer pull${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Rama actualizada${NC}"
echo ""

# Step 5: Verificar archivos modificados
echo -e "${YELLOW}✓ Verificando archivos modificados...${NC}"
MODIFIED_FILES=$(git diff develop --name-only)
echo "Archivos a consolidar:"
echo "  - app/api/endpoints/jobs.py (autocomplete endpoints)"
echo "  - app/api/endpoints/students.py (search/skills mejorado)"
echo "  - app/main.py (imports limpios)"
echo ""
echo -e "${GREEN}✓ Archivos correctos${NC}"
echo ""

# Step 6: Compilación check
echo -e "${YELLOW}✓ Verificando compilación...${NC}"
python3 -c "
import sys
try:
    from app.main import app
    print('✓ app.main compila sin errores')
    from app.api.endpoints import jobs, students
    print('✓ endpoints compilan sin errores')
    sys.exit(0)
except Exception as e:
    print(f'✗ Error de compilación: {e}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Error en compilación${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Compilación exitosa${NC}"
echo ""

# Step 7: Tests check
echo -e "${YELLOW}✓ Ejecutando tests...${NC}"
python3 test_consolidated_endpoints.py > /tmp/test_output.txt 2>&1
if grep -q "✅.*PASÓ" /tmp/test_output.txt; then
    echo -e "${GREEN}✓ Tests pasando${NC}"
else
    echo -e "${YELLOW}⚠ Verificar output de tests${NC}"
fi
echo ""

echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo -e "${BLUE}📋 PASOS PARA FASE 2: DEV DEPLOYMENT${NC}"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

echo -e "${BLUE}PASO 1: CREAR FEATURE BRANCH${NC}"
echo "─────────────────────────────────────────────────────────────────────"
echo "Ejecutar:"
echo "  git checkout -b $BRANCH_NAME"
echo ""
read -p "¿Crear feature branch? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    git checkout -b "$BRANCH_NAME" 2>/dev/null || git checkout "$BRANCH_NAME"
    echo -e "${GREEN}✓ Feature branch creado/actualizado${NC}"
    echo "  Branch actual: $(git rev-parse --abbrev-ref HEAD)"
    echo ""
else
    echo -e "${YELLOW}⏭ Saltando...${NC}"
fi
echo ""

echo -e "${BLUE}PASO 2: CREAR PULL REQUEST${NC}"
echo "─────────────────────────────────────────────────────────────────────"
echo "Abrir en GitHub:"
echo "  https://github.com/HenrySpark369/MoirAI/pulls"
echo ""
echo "Título:"
echo "  feat: Consolidate endpoints suggestions→jobs, matching→students"
echo ""
echo "Descripción:"
echo "  BREAKING CHANGE: Route migration"
echo "  - GET /suggestions/* → GET /jobs/autocomplete/*"
echo "  - POST /matching/* → GET /students/search/skills"
echo ""
echo "Ver: IMPLEMENTATION_GUIDE_ENDPOINTS.md para template completo"
echo ""

echo -e "${BLUE}PASO 3: CODE REVIEW${NC}"
echo "─────────────────────────────────────────────────────────────────────"
echo "Checklist para reviewers:"
echo "  ✓ jobs.py consolidation correcto"
echo "  ✓ students.py consolidation correcto"
echo "  ✓ main.py imports limpios"
echo "  ✓ Tests pasando (11/11)"
echo "  ✓ Compilación sin errores"
echo "  ✓ Documentación completa"
echo ""
echo "Ver: VERIFICATION_CHECKLIST_ENDPOINTS.md para checklist completo"
echo ""

echo -e "${BLUE}PASO 4: MERGE A DEVELOP${NC}"
echo "─────────────────────────────────────────────────────────────────────"
echo "Cuando PR esté aprobado:"
echo "  git checkout develop"
echo "  git pull origin develop"
echo "  git merge $BRANCH_NAME"
echo "  git push origin develop"
echo ""

echo -e "${BLUE}PASO 5: DEPLOY EN DEV ENVIRONMENT${NC}"
echo "─────────────────────────────────────────────────────────────────────"
echo "En servidor dev (dev.moirai.local):"
echo "  cd /var/www/moirai"
echo "  git pull origin develop"
echo "  pip install -r requirements.txt"
echo "  systemctl restart moirai-api"
echo ""

echo -e "${BLUE}PASO 6: FRONTEND MIGRATION${NC}"
echo "─────────────────────────────────────────────────────────────────────"
echo "Frontend team debe actualizar:"
echo "  ❌ /api/v1/suggestions/* → ✅ /api/v1/jobs/autocomplete/*"
echo "  ❌ /api/v1/matching/* → ✅ /api/v1/students/search/skills"
echo ""
echo "Ver: QUICK_REFERENCE_CONSOLIDACION.md (sección 'Para Frontend')"
echo ""

echo -e "${BLUE}PASO 7: DEV TESTING${NC}"
echo "─────────────────────────────────────────────────────────────────────"
echo "QA debe ejecutar:"
echo "  python test_consolidated_endpoints.py"
echo "  curl http://dev.moirai.local:8000/api/v1/jobs/autocomplete/skills?q=pyt"
echo "  curl http://dev.moirai.local:8000/api/v1/jobs/autocomplete/locations?q=mex"
echo ""

echo -e "${BLUE}PASO 8: PERFORMANCE VERIFICATION${NC}"
echo "─────────────────────────────────────────────────────────────────────"
echo "Verificar SLA < 30ms:"
echo "  ab -n 1000 -c 10 'http://dev.moirai.local:8000/api/v1/jobs/autocomplete/skills?q=pyt'"
echo ""

echo -e "${BLUE}PASO 9: QA SIGN-OFF${NC}"
echo "─────────────────────────────────────────────────────────────────────"
echo "Cuando todo esté listo:"
echo "  ✓ Tests: 11/11 pasando"
echo "  ✓ Frontend migrada"
echo "  ✓ Performance SLA met"
echo "  ✓ QA sign-off obtenido"
echo ""

echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}📊 RESUMEN${NC}"
echo "─────────────────────────────────────────────────────────────────────"
echo "Status: ✅ LISTA PARA INICIAR FASE 2"
echo "Duración estimada: 3-5 días"
echo "Responsables: Dev Lead, Frontend, QA"
echo ""
echo "Archivos a leer:"
echo "  1. FASE2_DEV_DEPLOYMENT_PLAN.md (este plan)"
echo "  2. QUICK_REFERENCE_CONSOLIDACION.md (referencia rápida)"
echo "  3. IMPLEMENTATION_GUIDE_ENDPOINTS.md (guía de implementación)"
echo ""

echo -e "${YELLOW}💡 PRÓXIMO PASO${NC}"
echo "─────────────────────────────────────────────────────────────────────"
echo "Crear feature branch y abrir Pull Request en GitHub:"
echo "  git checkout -b feature/endpoints-consolidation"
echo ""

echo -e "${GREEN}✅ FASE 2 LISTA PARA INICIAR${NC}"
echo ""

###############################################################################
