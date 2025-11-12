#!/bin/bash
# 🚀 FASE 2: DEV DEPLOYMENT - SCRIPT DE INICIO
# Ejecutar: chmod +x inicio_fase2.sh && ./inicio_fase2.sh

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                            ║"
echo "║              🚀 INICIANDO FASE 2: DEV DEPLOYMENT 🚀                       ║"
echo "║                                                                            ║"
echo "║         Consolidación de Endpoints - MoirAI                               ║"
echo "║         Fecha: $(date +'%d de %B de %Y')                                      ║"
echo "║                                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para imprimir pasos
step_print() {
    echo -e "${BLUE}[PASO $1]${NC} $2"
}

# Función para success
success_print() {
    echo -e "${GREEN}✓${NC} $1"
}

# Función para warning
warning_print() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Función para error
error_print() {
    echo -e "${RED}✗${NC} $1"
}

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "                    📋 PRE-DEPLOYMENT VERIFICATION"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Step 1: Verificar que estamos en el repo correcto
step_print "1" "Verificando repositorio..."
if [ ! -d ".git" ]; then
    error_print "No se encontró .git directory"
    echo "Por favor ejecutar este script en la raíz del repositorio MoirAI"
    exit 1
fi
success_print "Repositorio git encontrado"

# Step 2: Verificar status
step_print "2" "Verificando git status..."
if ! git status > /dev/null 2>&1; then
    error_print "Problema con repositorio git"
    exit 1
fi

# Verificar que no hay cambios sin commitear
if [ -n "$(git status --short)" ]; then
    warning_print "Hay cambios sin commitear:"
    git status --short
    echo ""
    read -p "¿Deseas continuar? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        error_print "Abortado por usuario"
        exit 1
    fi
fi
success_print "Git status OK"

# Step 3: Verificar rama actual
step_print "3" "Verificando rama actual..."
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
success_print "Rama actual: $CURRENT_BRANCH"

# Step 4: Verificar archivos modificados
step_print "4" "Verificando cambios en código..."
if git diff --name-only develop 2>/dev/null | grep -q "app/api/endpoints/jobs.py"; then
    success_print "✓ jobs.py: Cambios detectados"
else
    warning_print "jobs.py: Sin cambios detectados"
fi

if git diff --name-only develop 2>/dev/null | grep -q "app/api/endpoints/students.py"; then
    success_print "✓ students.py: Cambios detectados"
else
    warning_print "students.py: Sin cambios detectados"
fi

if git diff --name-only develop 2>/dev/null | grep -q "app/main.py"; then
    success_print "✓ main.py: Cambios detectados"
else
    warning_print "main.py: Sin cambios detectados"
fi

# Step 5: Verificar tests
step_print "5" "Verificando que test file existe..."
if [ -f "test_consolidated_endpoints.py" ]; then
    success_print "Test file encontrado: test_consolidated_endpoints.py"
else
    error_print "Test file no encontrado"
    exit 1
fi

# Step 6: Verificar documentación
step_print "6" "Verificando documentación..."
DOCS_FOUND=0
for doc in QUICK_REFERENCE_CONSOLIDACION.md IMPLEMENTATION_GUIDE_ENDPOINTS.md DEPLOYMENT_PLAN_CONSOLIDACION.md; do
    if [ -f "$doc" ]; then
        success_print "✓ $doc"
        ((DOCS_FOUND++))
    fi
done
echo "   Documentos encontrados: $DOCS_FOUND/3"

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "                        🎯 FASE 2: PRÓXIMOS PASOS"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

echo -e "${BLUE}PASO 1: CREAR FEATURE BRANCH${NC}"
echo "─────────────────────────────────────────────────────────────────────────────"
echo ""
echo "Ejecutar:"
echo "  git checkout develop"
echo "  git pull origin develop"
echo "  git checkout -b feature/endpoints-consolidation"
echo ""
echo "Verificar:"
echo "  git branch -v"
echo ""

echo -e "${BLUE}PASO 2: CREAR PULL REQUEST${NC}"
echo "─────────────────────────────────────────────────────────────────────────────"
echo ""
echo "Ir a: https://github.com/HenrySpark369/MoirAI/pulls"
echo "Crear PR con:"
echo "  Título: feat: Consolidate endpoints suggestions→jobs, matching→students"
echo "  Ver: FASE2_DEV_DEPLOYMENT_PLAN.md (sección PASO 2) para descripción completa"
echo ""

echo -e "${BLUE}PASO 3: CODE REVIEW${NC}"
echo "─────────────────────────────────────────────────────────────────────────────"
echo ""
echo "Esperando review de:"
echo "  • Code Lead"
echo "  • 2+ team members"
echo "  • Tech Lead"
echo ""
echo "Ver: FASE2_DEV_DEPLOYMENT_PLAN.md (sección PASO 3) para checklist"
echo ""

echo -e "${BLUE}PASO 4: MERGE A DEVELOP${NC}"
echo "─────────────────────────────────────────────────────────────────────────────"
echo ""
echo "Cuando PR esté aprobado:"
echo "  git checkout develop"
echo "  git pull origin develop"
echo "  git merge feature/endpoints-consolidation"
echo "  git push origin develop"
echo ""

echo -e "${BLUE}PASO 5: DEPLOY EN DEV${NC}"
echo "─────────────────────────────────────────────────────────────────────────────"
echo ""
echo "En servidor dev (dev.moirai.local):"
echo "  ssh deploy@dev.moirai.local"
echo "  cd /var/www/moirai"
echo "  git checkout develop && git pull"
echo "  systemctl restart moirai-api"
echo ""

echo -e "${BLUE}PASO 6: FRONTEND MIGRATION${NC}"
echo "─────────────────────────────────────────────────────────────────────────────"
echo ""
echo "Frontend team debe:"
echo "  1. Leer: QUICK_REFERENCE_CONSOLIDACION.md (sección 'Para Frontend')"
echo "  2. Buscar todas las referencias a /suggestions/ y /matching/"
echo "  3. Actualizar URLs según: IMPLEMENTATION_GUIDE_ENDPOINTS.md"
echo "  4. Testear en dev environment"
echo ""

echo -e "${BLUE}PASO 7-9: TESTING Y SIGN-OFF${NC}"
echo "─────────────────────────────────────────────────────────────────────────────"
echo ""
echo "QA Team debe:"
echo "  1. Ejecutar: python test_consolidated_endpoints.py -v"
echo "  2. Testear endpoints manualmente (ver FASE2_DEV_DEPLOYMENT_PLAN.md)"
echo "  3. Verificar performance SLA < 30ms"
echo "  4. Dar sign-off para Staging"
echo ""

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "                         📚 DOCUMENTOS DE REFERENCIA"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

echo "Para Dev Lead:"
echo "  📄 FASE2_DEV_DEPLOYMENT_PLAN.md - Plan completo de Fase 2"
echo ""

echo "Para Frontend Team:"
echo "  📄 QUICK_REFERENCE_CONSOLIDACION.md - Cheat sheet de URLs"
echo "  📄 IMPLEMENTATION_GUIDE_ENDPOINTS.md - Guía de implementación"
echo ""

echo "Para QA Team:"
echo "  📄 VERIFICATION_CHECKLIST_ENDPOINTS.md - Checklist de testing"
echo "  📄 test_consolidated_endpoints.py - Unit tests"
echo ""

echo "Para DevOps:"
echo "  📄 DEPLOYMENT_PLAN_CONSOLIDACION.md - Plan de deployment"
echo ""

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "                          ✅ VERIFICACIÓN COMPLETADA"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

echo -e "${GREEN}✓ Sistema listo para FASE 2: DEV DEPLOYMENT${NC}"
echo ""
echo "Próximos pasos:"
echo "  1. Crear feature branch (git checkout -b feature/endpoints-consolidation)"
echo "  2. Crear Pull Request en GitHub"
echo "  3. Ejecutar code review"
echo "  4. Merge a develop"
echo "  5. Deploy en dev environment"
echo "  6. Frontend migration"
echo "  7. Testing y QA sign-off"
echo ""
echo "Duración estimada: 3-5 días"
echo ""
echo "Para más detalles, leer: FASE2_DEV_DEPLOYMENT_PLAN.md"
echo ""
