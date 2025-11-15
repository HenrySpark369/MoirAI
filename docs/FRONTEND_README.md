# MoirAI Frontend - Landing Page

## Descripción

Landing page moderna y responsiva para MoirAI, la plataforma de matching laboral inteligente para estudiantes de UNRC. La página está diseñada para ser similar a probecarios.com, con un enfoque en la usabilidad y una experiencia visual atractiva.

## Características

### 📱 Responsive Design
- Diseño completamente adaptativo para dispositivos móviles, tablets y desktop
- Menú hamburguesa para dispositivos móviles
- Navegación fluida y fácil de usar

### 🎨 Secciones Principales

1. **Navegación Sticky** - Barra de navegación persistente con acceso rápido a todas las secciones

2. **Hero Section** - Sección de impacto con:
   - Título principal atractivo
   - Subtítulo descriptivo
   - Botones de CTA (Call To Action)
   - Tarjetas flotantes animadas
   - Estadísticas clave

3. **Características** - Grid de 6 características principales con:
   - Iconos animados
   - Descripciones claras
   - Efecto hover mejorado

4. **Cómo Funciona** - Proceso de 3 pasos:
   - Crear perfil
   - Análisis inteligente
   - Oportunidades personalizadas

5. **Para Quién** - Tres segmentos de usuarios:
   - Estudiantes
   - Empresas (destacado como "Popular")
   - Administradores

6. **Testimonios** - Historias de éxito con:
   - Calificaciones de estrellas
   - Avatares personalizados
   - Rol del testimonialista

7. **CTA Section** - Sección de llamada a la acción prominente

8. **Contacto** - Formulario de contacto + información:
   - Email
   - Teléfono
   - Ubicación
   - Enlaces a redes sociales

9. **Footer** - Pie de página con:
   - Información de la empresa
   - Enlaces de producto
   - Enlaces legales
   - Derechos de autor

### 🎭 Modales Interactivos

- **Modal de Demo** - Video demo de YouTube
- **Modal de Registro** - Formulario con tabs para Estudiante/Empresa
- **Modal de Login** - Formulario de inicio de sesión

### ✨ Animaciones

- Flotación de tarjetas en hero section
- Transiciones suaves en botones
- Animaciones de fade-in en scroll
- Efectos hover mejorados
- Botón "Volver al inicio" flotante

## Estructura de Archivos

```
app/
├── frontend/
│   ├── templates/
│   │   └── index.html          # Página principal
│   └── static/
│       ├── css/
│       │   └── styles.css      # Estilos CSS
│       ├── js/
│       │   └── main.js         # JavaScript interactivo
│       └── images/             # Directorio para imágenes
└── main.py                     # FastAPI app configurado
```

## Configuración en FastAPI

El frontend se sirve automáticamente desde la raíz (`/`) de la aplicación FastAPI:

```python
# Configurar archivos estáticos
static_path = Path(__file__).parent / "frontend" / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Landing page
@app.get("/")
async def landing_page():
    return FileResponse("app/frontend/templates/index.html")
```

## Uso

### Acceder a la Landing Page

Una vez que FastAPI está corriendo:

```bash
# Terminal
uvicorn app.main:app --reload

# Acceder a través del navegador
http://localhost:8000/
```

### Personalización

#### Cambiar Colores
Edita las variables CSS en `static/css/styles.css`:

```css
:root {
    --primary-color: #7c3aed;        /* Color primario */
    --secondary-color: #3b82f6;      /* Color secundario */
    --accent-color: #06b6d4;         /* Color de acento */
    /* ... más variables */
}
```

#### Modificar Contenido
- Textos: Edita directamente en `templates/index.html`
- Estadísticas: Busca la sección "hero-stats"
- Características: Modifica las tarjetas en la sección "features"

#### Agregar Imágenes
Coloca tus imágenes en `static/images/` y referéncialas en el HTML:

```html
<img src="/static/images/tu-imagen.png" alt="Descripción">
```

## Funcionalidades Interactivas

### Formularios
- Contacto
- Registro de usuarios
- Login

Todos los formularios tienen validación básica en el lado del cliente y se conectan con los endpoints de la API (con fallback para desarrollo).

### Navegación
- Scroll suave a secciones
- Menú responsivo
- Botón flotante para volver al inicio

### Modales
- Abre automáticamente al hacer clic en botones
- Se cierra al hacer clic fuera o presionar Escape
- Animaciones suaves

## Compatibilidad

- **Navegadores**: Chrome, Firefox, Safari, Edge (últimas versiones)
- **Dispositivos**: Móviles, tablets, desktop
- **Resoluciones**: Desde 320px hasta 2560px

## Performance

- CSS modular y eficiente
- JavaScript minimalista sin dependencias externas
- Imágenes SVG para iconos (escalables)
- Animaciones con GPU (transform, opacity)

## SEO

- Meta tags apropiadas
- Estructura semántica HTML5
- Textos descriptivos
- Alt text en imágenes

## Seguridad

- No hay información sensible en el cliente
- Formularios con CSRF protection (integración con FastAPI)
- Contraseñas no se guardan localmente
- HTTPS recomendado en producción

## Mejoras Futuras

- [ ] Integración con analytics (Google Analytics, Mixpanel)
- [ ] Soporte para múltiples idiomas (i18n)
- [ ] Modo oscuro
- [ ] Progressive Web App (PWA)
- [ ] Animaciones más avanzadas (GSAP, Framer Motion)
- [ ] Integración de reCAPTCHA en formularios
- [ ] Lazy loading de imágenes
- [ ] Service Worker para offline

## Troubleshooting

### Los estilos no cargan
- Verifica que `static/css/styles.css` exista
- Revisa la consola del navegador para errores CORS
- Asegúrate de que FastAPI está ejecutándose

### Los formularios no envían
- Verifica que los endpoints de API existen
- Revisa la consola para errores de red
- Comprueba que CORS está configurado correctamente

### La landing page no aparece
- Verifica que `templates/index.html` existe
- Revisa los logs de FastAPI
- Comprueba que el path es correcto

## Contacto

Para soporte o sugerencias, contacta a: contacto@moirai.com

---

**Desarrollado con ❤️ por UNRC - Ciencia de Datos para Negocios**
