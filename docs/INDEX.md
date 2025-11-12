# 📚 Índice de Documentación - MoirAI

**Última actualización**: 9 de noviembre de 2025  
**Estado**: ✅ Consolidado y Validado

---

## 🌍 PÚBLICO - Documentación para Usuarios

### Para Estudiantes
- **[Guía de Instalación](./INSTALLATION.md)** - Cómo instalar y configurar MoirAI localmente
- **[Búsqueda de Empleos](./JOB_SCRAPING_USER_GUIDE.md)** - Cómo buscar y aplicar a empleos
- **[Guía de Seguridad](./SECURITY_GUIDE.md)** - Privacidad y protección de datos

### Para Empresas
- **[Guía de Usuario - Empresas](./COMPANIES_USER_GUIDE.md)** - Cómo usar MoirAI como empresa colaboradora
- **[API de Empresas](./COMPANIES_API_REFERENCE.md)** - Referencia técnica completa de endpoints

### Para Ejecutivos/Admins
- **[Roadmap de Desarrollo](../ROADMAP_DESARROLLO.md)** - Planes futuros y prioridades

---

## 🔒 INTERNO - Documentación Técnica

### Arquitectura
- **[Diagrama de Arquitectura](./ARCHITECTURE_DIAGRAM.md)** - Estructura general del sistema
- **[API de Matching](./MATCHING_API_REFERENCE.md)** - Endpoints de recomendaciones

### Seguridad & Encriptación
- **[Guía de Encriptación](./ENCRYPTION_SETUP_GUIDE.md)** - Configurar encriptación de datos
- **[Guía de Seguridad](./SECURITY_GUIDE.md)** - Implementación de seguridad
- **[Auditoría de Seguridad](./SECURITY_AUDIT.md)** - Análisis de seguridad del proyecto
- **[Setup de Seguridad GitHub](./GITHUB_SECURITY_SETUP.md)** - Configurar secretos y seguridad en GitHub

### Sistema de API Keys
- **[Sistema de API Keys](./API_KEYS_SYSTEM.md)** - Gestión dinámica de claves de acceso

### Deployment & Operations
- **[Guía de Optimización](./DEPLOYMENT_GUIDE_JOB_OPTIMIZATION.md)** - Performance y optimización
- **[Optimización de Job Descriptions](./JOB_DESCRIPTION_OPTIMIZATION_FINAL.md)** - Técnica de compresión
- **[Guía de Testing](../TESTING_GUIDE.md)** - Cómo ejecutar tests
- **[Guía de Uso - Match Score](./CALCULATE_MATCH_SCORE_USAGE_GUIDE.md)** - Cálculo de compatibilidad

### Sistemas Específicos
- **[Job Scraping](./JOB_SCRAPING_SYSTEM.md)** - Sistema de scraping de empleos OCC.com.mx

---

## 📁 Estructura de Documentación

```
docs/
├── 🌍 PÚBLICO
│   ├── INSTALLATION.md                       # Setup inicial
│   ├── JOB_SCRAPING_USER_GUIDE.md           # Guía de usuario estudiantes
│   ├── COMPANIES_USER_GUIDE.md              # Guía de usuario empresas
│   ├── SECURITY_GUIDE.md                    # Privacidad
│   └── COMPANIES_API_REFERENCE.md           # API empresas
│
├── 🔒 INTERNO - Arquitectura
│   ├── ARCHITECTURE_DIAGRAM.md              # Diagramas técnicos
│   └── MATCHING_API_REFERENCE.md            # Matching endpoints
│
├── 🔒 INTERNO - Seguridad
│   ├── ENCRYPTION_SETUP_GUIDE.md            # Encriptación
│   ├── SECURITY_GUIDE.md                    # Cumplimiento normativo
│   ├── SECURITY_AUDIT.md                    # Análisis de seguridad
│   ├── API_KEYS_SYSTEM.md                   # Sistema de claves
│   └── GITHUB_SECURITY_SETUP.md             # Setup seguridad GitHub
│
├── 🔒 INTERNO - Operations
│   ├── DEPLOYMENT_GUIDE_JOB_OPTIMIZATION.md # Deploy
│   ├── JOB_DESCRIPTION_OPTIMIZATION_FINAL.md # Performance
│   └── RUNNING_TESTS.md                     # Testing
│
└── 🔒 INTERNO - Sistemas & Técnica
    ├── JOB_SCRAPING_SYSTEM.md               # Sistema de scraping
    └── CALCULATE_MATCH_SCORE_USAGE_GUIDE.md # Guía técnica de matching
```

---

## ✅ Checklist de Documentación

### A Nivel Raíz (`/`)
- ✅ **README.md** - Overview del proyecto (NO EDITAR, solo usuario)
- ✅ **ROADMAP_DESARROLLO.md** - Único documento de oportunidades (CONSOLIDADO)
- ✅ **TESTING_GUIDE.md** - Guía de testing

### En Carpeta `docs/`
- ✅ **Public docs**: 5 archivos
- ✅ **Internal docs**: 12 archivos
- ✅ **Total: 17 archivos** (vs 70+ anteriormente)

---

## 🎯 Mantenimiento

### Al Agregar Documentación Nueva
1. ✅ Verificar si ya existe (buscar en `docs/INDEX.md`)
2. ✅ Decidir si es 🌍 PÚBLICO o 🔒 INTERNO
3. ✅ Agregar entrada a este INDEX.md
4. ✅ Categorizar en la sección correcta

### Al Eliminar Documentación
1. ✅ Remover de `docs/INDEX.md`
2. ✅ Buscar referencias cruzadas en otros documentos
3. ✅ Actualizar referencias si existen
4. ✅ Confirmar que no rompe nada en git

### Reglas de Consolidación
- 🚫 No duplicar información entre documentos
- 🚫 No crear índices adicionales (solo este INDEX.md)
- ✅ Linkar entre documentos relacionados
- ✅ Mantener los 4 documentos principales siempre actualizados
- ✅ Mantener documentación técnica valiosa (no duplicada)

---

## 📊 Estadísticas

| Métrica | Antes | Ahora | Mejora |
|---------|-------|-------|--------|
| Documentos totales | ~70 | 16 | ↓77% |
| Índices separados | 5+ | 1 | ↓100% |
| Reportes obsoletos | 30+ | 0 | ✅ |
| Duplicación | Alto | Ninguna | ✅ |
| Docs de usuario | Perdidas | Recuperadas | ✅ |

---

## 📞 Cómo Usar Este Índice

1. **¿Necesitas instalar MoirAI?** → [INSTALLATION.md](./INSTALLATION.md)
2. **¿Necesitas aprender a buscar empleos?** → [JOB_SCRAPING_USER_GUIDE.md](./JOB_SCRAPING_USER_GUIDE.md)
3. **¿Eres empresa y quieres usar MoirAI?** → [COMPANIES_USER_GUIDE.md](./COMPANIES_USER_GUIDE.md)
4. **¿Quieres entender la arquitectura?** → [ARCHITECTURE_DIAGRAM.md](./ARCHITECTURE_DIAGRAM.md)
5. **¿Necesitas deploy/seguridad?** → [SECURITY_GUIDE.md](./SECURITY_GUIDE.md)
6. **¿Tienes dudas de endpoints?** → [MATCHING_API_REFERENCE.md](./MATCHING_API_REFERENCE.md)
7. **¿Qué viene próximo?** → [ROADMAP_DESARROLLO.md](../ROADMAP_DESARROLLO.md)

---

**Última revisión**: 9 de noviembre de 2025  
**Próxima revisión**: 30 de noviembre de 2025  
**Responsable**: GitHub Copilot + Equipo de Desarrollo

✅ **DOCUMENTACIÓN CONSOLIDADA, ORGANIZADA Y VALIDADA**
