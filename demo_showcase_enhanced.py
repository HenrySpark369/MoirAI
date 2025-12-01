#!/usr/bin/env python3
"""
MoirAI Demo Mode Visual Demonstration - Navegación Completa
Script automatizado que demuestra visualmente la navegación completa del navbar
y funcionalidades específicas para cada rol en modo demo.
"""

import time
import json
import requests
import subprocess
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class MoirAIDemoShowcase:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.roles = ['student', 'company', 'admin']
        self.demo_data = {}
        self.driver = None
        self.wait = None
        
        # Verificar conectividad al backend primero
        self._verify_backend_connectivity()
        
        # Luego inicializar ChromeDriver
        self._initialize_chromedriver()

    def _verify_backend_connectivity(self):
        """Verificar que el backend esté disponible antes de inicializar Selenium"""
        print("🔍 Verificando conectividad al backend...")
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = requests.get(f"{self.base_url}/", timeout=5)
                if response.status_code == 200:
                    print("✅ Backend disponible en http://127.0.0.1:8000")
                    return
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"   ⏳ Intento {attempt + 1}/{max_retries} fallido. Reintentando en {retry_delay}s...")
                    time.sleep(retry_delay)
        
        raise ConnectionError(
            "❌ No se puede conectar al backend en http://127.0.0.1:8000\n"
            "   Por favor, asegúrate de ejecutar: uvicorn app.main:app --reload"
        )

    def _initialize_chromedriver(self):
        """Inicializar ChromeDriver usando solo el del sistema (sin descargas de internet)"""
        print("🚀 Inicializando ChromeDriver...")
        
        try:
            # Configurar Chrome en modo visual (no headless para demostración)
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--enable-automation")
            
            print("   🔗 Buscando ChromeDriver en el sistema...")
            
            # Buscar chromedriver en el PATH del sistema
            chromedriver_path = shutil.which('chromedriver')
            
            if chromedriver_path:
                print(f"   ✅ ChromeDriver encontrado: {chromedriver_path}")
                service = Service(chromedriver_path)
                self.driver = webdriver.Chrome(
                    service=service,
                    options=chrome_options
                )
            else:
                print("   ⚠️  ChromeDriver no encontrado en PATH, intentando con webdriver automático...")
                # Fallback: dejar que Selenium lo busque en el PATH
                self.driver = webdriver.Chrome(options=chrome_options)
            
            self.wait = WebDriverWait(self.driver, 15)
            print("✅ ChromeDriver inicializado correctamente")
            
        except Exception as e:
            raise RuntimeError(
                f"❌ Error inicializando ChromeDriver: {str(e)}\n"
                f"   Asegúrate de tener ChromeDriver instalado:\n"
                f"   - brew install --cask chromedriver\n"
                f"   - O instala Chrome: brew install --cask google-chrome"
            )

    def showcase_role(self, role):
        """Demostración visual completa de un rol específico"""
        print(f"\n🎭 === DEMOSTRACIÓN VISUAL: {role.upper()} ===")

        try:
            # 1. Navegar a perfil en modo demo
            self.navigate_to_role_profile(role)

            # 2. Mostrar información del rol
            self.display_role_info(role)

            # Demostrar funcionalidades del dashboard inicial
            self.demonstrate_dashboard_features(role)

            # 4. Demostrar navegación completa del navbar
            self.showcase_navbar_navigation(role)

            # 5. Capturar estado final
            self.capture_final_state(role)

            return {"success": True, "message": f"Demostración de {role} completada"}

        except Exception as e:
            print(f"❌ Error en demostración de {role}: {str(e)}")
            return {"success": False, "error": str(e)}

    def navigate_to_role_profile(self, role):
        """Navegar al DASHBOARD del rol en modo demo para flujo más lineal"""
        # Para estudiantes: primero explorar la raíz por 2.5 minutos antes de ir al dashboard
        if role == 'student':
            self.navigate_root_sections()
            print(f"\n✅ Exploración de raíz completada (2.5 minutos)")
            print(f"🌐 Ahora navegando al dashboard de {role}...")

        url = f"{self.base_url}/dashboard?demo=true&role={role}"
        print(f"🌐 Navegando a dashboard de {role}: {url}")

        self.driver.get(url)
        time.sleep(6)  # Tiempo para carga completa (era 5, ahora 6)

        # Verificar que estamos en modo demo
        try:
            demo_indicator = self.driver.find_element(By.CSS_SELECTOR, "[class*='demo'], .demo-badge, #demo-badge")
            print("✅ Modo demo activado")
        except:
            print("⚠️  Modo demo no detectado visualmente")

    def navigate_root_sections(self):
        """Navegar por secciones de la raíz durante 2.08 minutos antes de ir al dashboard del estudiante"""
        print(f"\n🏠 === EXPLORACIÓN DE LA RAÍZ - 2.08 MINUTOS ===")
        print("📖 Navegando por secciones principales antes de acceder al dashboard")

        # Ir a la página raíz
        root_url = f"{self.base_url}/"
        print(f"🌐 Iniciando exploración en: {root_url}")
        self.driver.get(root_url)
        time.sleep(3)  # Tiempo inicial para carga

        # Definir secciones de la raíz y su tiempo de exploración
        # Total: 150 segundos (2.5 minutos) dividido en 5 secciones = 30 segundos cada una
        root_sections = {
            'hero': {
                'name': '🎯 Hero Section - Presentación Principal',
                'selector': 'section.hero',
                'description': 'Sección principal con título, descripción y estadísticas de MoirAI',
                'time_seconds': 30.0
            },
            'features': {
                'name': '⚡ Características Poderosas - Funcionalidades',
                'selector': 'section.features',
                'description': 'Grid de características principales de la plataforma',
                'time_seconds': 30.0
            },
            'how-it-works': {
                'name': '🔄 Cómo Funciona - Proceso de Matching',
                'selector': 'section.how-it-works',
                'description': 'Pasos del proceso de matching inteligente',
                'time_seconds': 30.0
            },
            'audience': {
                'name': '👥 Para Quién es MoirAI - Usuarios Objetivo',
                'selector': 'section.for-who',
                'description': 'Información para estudiantes, empresas y administradores',
                'time_seconds': 30.0
            },
            'testimonials': {
                'name': '💬 Historias de Éxito - Testimonios',
                'selector': 'section.testimonials',
                'description': 'Testimonios de usuarios y empresas colaboradoras',
                'time_seconds': 30.0
            }
        }

        total_time = 0
        for section_key, section_info in root_sections.items():
            section_start_time = time.time()

            print(f"\n   📑 Explorando: {section_info['name']}")
            print(f"      {section_info['description']}")
            print(f"      ⏱️  Tiempo asignado: {section_info['time_seconds']} segundos")

            # Primero, hacer scroll a la sección específica para posicionarla correctamente
            self._scroll_to_section(section_key, section_info['selector'])

            # Demostrar elementos encontrados en la sección (sin exploración gradual)
            self.demonstrate_root_section_features(section_key, section_info)

            # Esperar el tiempo completo asignado para esta sección (30 segundos)
            print(f"         ⏳ Esperando {section_info['time_seconds']} segundos en la sección posicionada...")
            time.sleep(section_info['time_seconds'])
            print("         ✅ Tiempo de espera completado")

            total_time += section_info['time_seconds']
            print(f"      ✅ Sección {section_key} completada ({total_time}s total)")

        print(f"\n🏁 Exploración de raíz completada: {total_time} segundos (2.5 minutos)")
        print("   ✅ Todas las secciones principales han sido exploradas")

    def perform_gradual_scroll_exploration(self, duration_seconds, section_key=None):
        """Realizar exploración gradual con scrolls naturales según la sección actual"""
        start_time = time.time()
        scroll_count = 0

        # Obtener altura total de la página
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        current_position = self.driver.execute_script("return window.pageYOffset")
        window_height = self.driver.execute_script("return window.innerHeight")

        print(f"         📏 Página total: {total_height}px, Posición actual: {current_position}px")

        # Si es la última sección (testimonials), buscar específicamente testimonios
        if section_key == 'testimonials':
            return self._scroll_to_testimonials(duration_seconds)
        else:
            # Para las primeras secciones, hacer scroll gradual normal
            return self._scroll_gradual_normal(duration_seconds)



    def _scroll_gradual_normal(self, duration_seconds):
        """Realizar scroll gradual normal dentro de la sección actual"""
        start_time = time.time()
        scroll_count = 0

        # Obtener posición inicial de la sección
        initial_position = self.driver.execute_script("return window.pageYOffset")
        window_height = self.driver.execute_script("return window.innerHeight")

        print(f"         🔍 Debug: Posición inicial={initial_position}px, Altura ventana={window_height}px")

        # Definir rango de exploración: desde la posición inicial hasta un máximo de 2 alturas de ventana
        max_exploration_height = initial_position + (window_height * 2)
        total_height = self.driver.execute_script("return document.body.scrollHeight")

        # Calcular intervalos de scroll (cada 2.5 segundos)
        scroll_interval = 2.5
        max_scrolls = int(duration_seconds / scroll_interval)

        for i in range(max_scrolls):
            if time.time() - start_time >= duration_seconds:
                break

            # Calcular nueva posición (scroll pequeño y gradual, máximo 200px)
            scroll_increment = min(200, max_exploration_height - initial_position - window_height)

            if scroll_increment <= 0:
                print(f"         🛑 Fin del rango de exploración alcanzado en scroll #{scroll_count}")
                break

            new_position = initial_position + scroll_increment

            # No exceder el rango máximo de exploración
            if new_position > max_exploration_height:
                new_position = max_exploration_height

            # Ejecutar scroll
            self.driver.execute_script(f"window.scrollTo({{top: {new_position}, behavior: 'smooth'}});")
            scroll_count += 1
            print(f"         📜 Scroll #{scroll_count}: posición {initial_position}px → {new_position}px (rango: {initial_position}-{max_exploration_height}px)")

            # Actualizar posición inicial para el siguiente scroll
            initial_position = new_position

            # Pausa entre scrolls
            time.sleep(scroll_interval)

        # Si terminó temprano, completar el tiempo restante
        elapsed = time.time() - start_time
        if elapsed < duration_seconds:
            remaining = duration_seconds - elapsed
            print(f"         ⏳ Completando tiempo restante: {remaining:.1f} segundos")
            time.sleep(remaining)

        print(f"         📜 Total scrolls realizados: {scroll_count} en {elapsed:.1f}s")

    def _scroll_to_testimonials(self, duration_seconds):
        """Buscar y hacer scroll específicamente hacia testimonios"""
        start_time = time.time()
        scroll_count = 0

        # Obtener altura total de la página
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        window_height = self.driver.execute_script("return window.innerHeight")

        print(f"         🔍 Debug testimonios: Altura total={total_height}px, Altura ventana={window_height}px")

        # Buscar elementos de testimonios
        testimonial_selectors = [
            ".testimonial", ".testimonials", "[class*='testimonial']",
            ".success-story", ".review", ".feedback",
            "[id*='testimonial']", "[class*='review']"
        ]

        testimonials_found = []
        for selector in testimonial_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    testimonials_found.extend(elements)
            except:
                pass

        if testimonials_found:
            print(f"         💬 {len(testimonials_found)} elementos de testimonios encontrados")

            # Hacer scroll hacia el primer testimonio encontrado
            first_testimonial = testimonials_found[0]
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", first_testimonial)
            scroll_count += 1
            print(f"         📜 Scroll #{scroll_count}: hacia primer testimonio")

            # Pausa para que se vea el scroll
            time.sleep(2)

            # Hacer algunos scrolls adicionales alrededor de los testimonios
            remaining_time = duration_seconds - (time.time() - start_time)
            if remaining_time > 0:
                scroll_interval = 3
                max_additional_scrolls = int(remaining_time / scroll_interval)

                for i in range(min(max_additional_scrolls, 3)):  # Máximo 3 scrolls adicionales
                    if time.time() - start_time >= duration_seconds:
                        break

                    # Scroll suave hacia abajo para mostrar más testimonios
                    self.driver.execute_script("window.scrollBy({top: 300, behavior: 'smooth'});")
                    scroll_count += 1
                    print(f"         📜 Scroll adicional #{scroll_count}: +300px")
                    time.sleep(scroll_interval)
        else:
            print("         ⚠️  No se encontraron testimonios específicos, haciendo scroll gradual normal")
            # Si no hay testimonios, hacer scroll gradual normal pero sin llegar al final
            scroll_interval = 2.5
            max_scrolls = int(duration_seconds / scroll_interval)

            for i in range(max_scrolls):
                if time.time() - start_time >= duration_seconds:
                    break

                # Scroll moderado, evitando el final de la página
                current_position = self.driver.execute_script("return window.pageYOffset")
                scroll_increment = min(400, total_height - current_position - window_height)

                if scroll_increment <= 0:
                    print(f"         🛑 Fin de página alcanzado en scroll gradual #{scroll_count}")
                    break

                # No llegar al final
                if current_position + scroll_increment >= total_height - window_height * 1.5:
                    break

                self.driver.execute_script(f"window.scrollBy({{top: {scroll_increment}, behavior: 'smooth'}});")
                scroll_count += 1
                print(f"         📜 Scroll gradual #{scroll_count}: +{scroll_increment}px")
                time.sleep(scroll_interval)

        # Completar tiempo restante si es necesario
        elapsed = time.time() - start_time
        if elapsed < duration_seconds:
            remaining = duration_seconds - elapsed
            print(f"         ⏳ Completando tiempo restante: {remaining:.1f} segundos")
            time.sleep(remaining)

        print(f"         📜 Total scrolls hacia testimonios: {scroll_count} en {elapsed:.1f}s")

    def demonstrate_root_section_features(self, section_key, section_info):
        """Demostrar funcionalidades específicas de cada sección de la raíz"""
        print(f"         🔍 Explorando contenido de la sección:")

        try:
            if section_key == 'hero':
                self.demonstrate_hero_section()
            elif section_key == 'features':
                self.demonstrate_features_section()
            elif section_key == 'how-it-works':
                self.demonstrate_how_it_works_section()
            elif section_key == 'audience':
                self.demonstrate_audience_section()
            elif section_key == 'testimonials':
                self.demonstrate_testimonials_section()
        except Exception as e:
            print(f"            ⚠️  Error demostrando funcionalidades: {str(e)}")

    def demonstrate_hero_section(self):
        """Demostrar funcionalidades de la sección Hero"""
        print("            🎯 Explorando sección principal:")

        # Verificar elementos del hero
        hero_titles = self.driver.find_elements(By.CSS_SELECTOR, ".hero-title, h1")
        if hero_titles:
            print(f"               📋 {len(hero_titles)} títulos principales encontrados")

        # Verificar subtítulos
        hero_subtitles = self.driver.find_elements(By.CSS_SELECTOR, ".hero-subtitle, .hero-text p")
        if hero_subtitles:
            print(f"               � {len(hero_subtitles)} subtítulos encontrados")

        # Verificar botones de acción principales
        hero_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".hero-buttons .btn, .btn-primary, .btn-outline")
        if hero_buttons:
            print(f"               🎯 {len(hero_buttons)} botones de acción principales")

        # Verificar estadísticas
        hero_stats = self.driver.find_elements(By.CSS_SELECTOR, ".hero-stats .stat, .stat")
        if hero_stats:
            print(f"               � {len(hero_stats)} estadísticas mostradas")

        # Verificar navegación
        nav_elements = self.driver.find_elements(By.CSS_SELECTOR, "nav, .navbar, .navigation")
        if nav_elements:
            print("               🧭 Elementos de navegación presentes")


    def demonstrate_how_it_works_section(self):
        """Demostrar funcionalidades de la sección Cómo Funciona"""
        print("            🔄 Explorando proceso de funcionamiento:")

        # Verificar pasos del proceso
        steps = self.driver.find_elements(By.CSS_SELECTOR, ".step")
        if steps:
            print(f"               🔢 {len(steps)} pasos del proceso identificados")

        # Verificar números de pasos
        step_numbers = self.driver.find_elements(By.CSS_SELECTOR, ".step-number")
        if step_numbers:
            print(f"               🔢 {len(step_numbers)} números de pasos")

        # Verificar iconos de pasos
        step_icons = self.driver.find_elements(By.CSS_SELECTOR, ".step-icon, .step i")
        if step_icons:
            print(f"               🎯 {len(step_icons)} iconos de pasos")

        # Verificar títulos de pasos
        step_titles = self.driver.find_elements(By.CSS_SELECTOR, ".step h3")
        if step_titles:
            print(f"               📋 {len(step_titles)} títulos de pasos")

        # Verificar descripciones de pasos
        step_descriptions = self.driver.find_elements(By.CSS_SELECTOR, ".step p")
        if step_descriptions:
            print(f"               � {len(step_descriptions)} descripciones de pasos")

        # Verificar divisores entre pasos
        step_dividers = self.driver.find_elements(By.CSS_SELECTOR, ".step-divider")
        if step_dividers:
            print(f"               ➡️  {len(step_dividers)} divisores entre pasos")

    def demonstrate_features_section(self):
        """Demostrar funcionalidades de la sección Características"""
        print("            ⚡ Explorando características poderosas:")

        # Verificar tarjetas de características
        feature_cards = self.driver.find_elements(By.CSS_SELECTOR, ".feature-card")
        if feature_cards:
            print(f"               📋 {len(feature_cards)} características principales")

        # Verificar iconos de características
        feature_icons = self.driver.find_elements(By.CSS_SELECTOR, ".feature-icon, .feature-card i")
        if feature_icons:
            print(f"               🎯 {len(feature_icons)} iconos de características")

        # Verificar títulos de características
        feature_titles = self.driver.find_elements(By.CSS_SELECTOR, ".feature-card h3")
        if feature_titles:
            print(f"               📋 {len(feature_titles)} títulos de características")

        # Verificar descripciones de características
        feature_descriptions = self.driver.find_elements(By.CSS_SELECTOR, ".feature-card p")
        if feature_descriptions:
            print(f"               � {len(feature_descriptions)} descripciones de características")

    def demonstrate_audience_section(self):
        """Demostrar funcionalidades de la sección Para Quién es MoirAI"""
        print("            👥 Explorando usuarios objetivo:")

        # Verificar tarjetas de audiencia
        audience_cards = self.driver.find_elements(By.CSS_SELECTOR, ".audience-card")
        if audience_cards:
            print(f"               📋 {len(audience_cards)} tipos de usuarios objetivo")

        # Verificar iconos de audiencia
        audience_icons = self.driver.find_elements(By.CSS_SELECTOR, ".audience-icon, .audience-card i")
        if audience_icons:
            print(f"               🎯 {len(audience_icons)} iconos de usuarios")

        # Verificar títulos de audiencia
        audience_titles = self.driver.find_elements(By.CSS_SELECTOR, ".audience-card h3")
        if audience_titles:
            print(f"               📋 {len(audience_titles)} títulos de usuarios")

        # Verificar descripciones de audiencia
        audience_descriptions = self.driver.find_elements(By.CSS_SELECTOR, ".audience-card p")
        if audience_descriptions:
            print(f"               � {len(audience_descriptions)} descripciones de usuarios")

        # Verificar listas de beneficios
        benefits_lists = self.driver.find_elements(By.CSS_SELECTOR, ".benefits-list")
        if benefits_lists:
            print(f"               ✅ {len(benefits_lists)} listas de beneficios")

        # Verificar elementos de beneficios
        benefit_items = self.driver.find_elements(By.CSS_SELECTOR, ".benefits-list li")
        if benefit_items:
            print(f"               ✅ {len(benefit_items)} beneficios específicos")

    def demonstrate_testimonials_section(self):
        """Demostrar funcionalidades de la sección Historias de Éxito"""
        print("            💬 Explorando historias de éxito:")

        # Verificar tarjetas de testimonios
        testimonial_cards = self.driver.find_elements(By.CSS_SELECTOR, ".testimonial-card")
        if testimonial_cards:
            print(f"               📋 {len(testimonial_cards)} testimonios de usuarios")

        # Verificar estrellas de calificación
        stars = self.driver.find_elements(By.CSS_SELECTOR, ".stars, .testimonial-card .fa-star")
        if stars:
            print(f"               ⭐ {len(stars)} elementos de calificación")

        # Verificar textos de testimonios
        testimonial_texts = self.driver.find_elements(By.CSS_SELECTOR, ".testimonial-card p")
        if testimonial_texts:
            print(f"               � {len(testimonial_texts)} textos de testimonios")

        # Verificar autores de testimonios
        testimonial_authors = self.driver.find_elements(By.CSS_SELECTOR, ".testimonial-author")
        if testimonial_authors:
            print(f"               👤 {len(testimonial_authors)} autores de testimonios")

        # Verificar avatares de autores
        author_avatars = self.driver.find_elements(By.CSS_SELECTOR, ".author-avatar, .testimonial-author div:first-child")
        if author_avatars:
            print(f"               🖼️  {len(author_avatars)} avatares de autores")

        # Verificar nombres de autores
        author_names = self.driver.find_elements(By.CSS_SELECTOR, ".testimonial-author h4")
        if author_names:
            print(f"               📝 {len(author_names)} nombres de autores")

    def display_role_info(self, role):
        """Mostrar información específica del rol"""
        print(f"📋 Información del rol {role}:")

        role_info = {
            'student': {
                'title': '👨‍🎓 Estudiante UNRC',
                'description': 'Usuario principal - Gestiona su perfil académico y busca oportunidades',
                'permissions': ['Ver/editar perfil', 'Subir CV', 'Ver ofertas laborales', 'Aplicar a vacantes'],
                'mvp_features': ['CV Harvard', 'Habilidades inferidas', 'Sistema de matching'],
                'navbar_sections': ['Dashboard → Oportunidades → Mis Aplicaciones']
            },
            'company': {
                'title': '🏢 Empresa Colaboradora',
                'description': 'Reclutador - Busca talento y publica ofertas de trabajo',
                'permissions': ['Buscar candidatos', 'Ver perfiles anónimos', 'Publicar vacantes', 'Ver métricas'],
                'mvp_features': ['Búsqueda por habilidades', 'Dashboard KPIs', 'Sistema de matching'],
                'navbar_sections': ['Dashboard → Buscar Candidatos → Mis Vacantes']
            },
            'admin': {
                'title': '👨‍💼 Administrador UNRC',
                'description': 'Supervisor - Gestiona la plataforma y supervisa métricas',
                'permissions': ['Ver todos los usuarios', 'Gestionar roles', 'Ver analytics', 'Configurar sistema'],
                'mvp_features': ['Dashboard analytics', 'Gestión de usuarios', 'Métricas de colocación'],
                'navbar_sections': ['Dashboard → Usuarios → Analítica → Configuración']
            }
        }

        info = role_info.get(role, {})
        print(f"   {info.get('title', 'Rol desconocido')}")
        print(f"   {info.get('description', '')}")
        print(f"   Permisos: {', '.join(info.get('permissions', []))}")
        print(f"   Funcionalidades MVP: {', '.join(info.get('mvp_features', []))}")
        print(f"   Secciones del Navbar: {', '.join(info.get('navbar_sections', []))}")

    def demonstrate_dashboard_features(self, role):
        """Demostrar las funcionalidades del dashboard inicial para cada rol"""
        print(f"\n🚀 Demostrando funcionalidades del Dashboard para {role}:")

        if role == 'student':
            self.demonstrate_student_dashboard()
        elif role == 'company':
            self.demonstrate_company_dashboard()
        elif role == 'admin':
            self.demonstrate_admin_dashboard()

    def demonstrate_student_dashboard(self):
        """Demostrar funcionalidades del dashboard para estudiantes"""
        print("   � 1. Dashboard Personalizado")

        # Verificar KPIs del estudiante
        kpi_cards = self.driver.find_elements(By.CLASS_NAME, "kpi-card")
        if kpi_cards:
            print(f"      ✅ {len(kpi_cards)} métricas personales encontradas")
        else:
            print("      ⚠️  KPIs no visibles (puede ser normal en demo)")

        print("   🎯 2. Acceso Rápido a Oportunidades")
        # Verificar acceso rápido a funcionalidades
        quick_actions = self.driver.find_elements(By.CSS_SELECTOR, "[class*='quick'], [class*='action'], button")
        if quick_actions:
            print(f"      ✅ {len(quick_actions)} acciones rápidas disponibles")
        else:
            print("      ⚠️  Acciones rápidas no encontradas")

        print("   � 3. Progreso de Aplicaciones")
        # Verificar métricas de progreso
        progress_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='progress'], [class*='chart'], .metric")
        if progress_elements:
            print(f"      ✅ {len(progress_elements)} elementos de progreso")
        else:
            print("      ⚠️  Elementos de progreso no visibles")

    def demonstrate_company_dashboard(self):
        """Demostrar funcionalidades del dashboard para empresas"""
        print("   � 1. KPIs de Vinculación Laboral")

        # Verificar métricas de empresa
        kpi_cards = self.driver.find_elements(By.CLASS_NAME, "kpi-card")
        metric_elements = self.driver.find_elements(By.CLASS_NAME, "metric")

        if kpi_cards or metric_elements:
            print(f"      ✅ {len(kpi_cards)} KPIs y {len(metric_elements)} métricas de empresa")
        else:
            print("      ⚠️  KPIs no visibles (puede ser normal en demo)")

        print("   🎯 2. Candidatos Potenciales")
        # Verificar candidatos destacados
        candidate_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='candidate'], [class*='match']")
        if candidate_elements:
            print(f"      ✅ {len(candidate_elements)} candidatos potenciales mostrados")
        else:
            print("      ⚠️  Candidatos no visibles en dashboard")

        print("   💼 3. Gestión de Vacantes Activas")
        # Verificar gestión de vacantes
        vacancy_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='vacancy'], [class*='job']")
        if vacancy_elements:
            print(f"      ✅ {len(vacancy_elements)} vacantes activas")
        else:
            print("      ⚠️  Vacantes no visibles en dashboard")

    def demonstrate_admin_dashboard(self):
        """Demostrar funcionalidades del dashboard para administradores"""
        print("   📈 1. Métricas Globales del Sistema")

        # Verificar métricas administrativas
        kpi_cards = self.driver.find_elements(By.CLASS_NAME, "kpi-card")
        system_metrics = self.driver.find_elements(By.CSS_SELECTOR, "[class*='system'], [class*='metric']")

        if kpi_cards or system_metrics:
            print(f"      ✅ {len(kpi_cards)} KPIs administrativos y {len(system_metrics)} métricas del sistema")
        else:
            print("      ⚠️  Métricas del sistema no visibles")

        print("   👥 2. Resumen de Usuarios Activos")
        # Verificar información de usuarios
        user_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='user'], [class*='active']")
        if user_elements:
            print(f"      ✅ {len(user_elements)} indicadores de usuarios activos")
        else:
            print("      ⚠️  Información de usuarios no visible")

        print("   ⚙️  3. Estado de Configuración del Sistema")
        # Verificar estado del sistema
        status_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='status'], [class*='health'], [class*='config']")
        if status_elements:
            print(f"      ✅ {len(status_elements)} indicadores de estado del sistema")
        else:
            print("      ⚠️  Estado del sistema no visible")

        print("   🧭 4. Navegación por Sidebar del Dashboard")
        self.navigate_admin_sidebar()

    def showcase_navbar_navigation(self, role):
        """Demostrar navegación completa del navbar para cada rol"""
        print(f"\n🧭 === NAVEGACIÓN COMPLETA DEL NAVBAR PARA {role.upper()} ===")

        try:
            # Obtener todos los enlaces del navbar
            nav_links = self.driver.find_elements(By.CLASS_NAME, "nav-link")

            if len(nav_links) == 0:
                print("   ⚠️  No se encontraron enlaces de navegación")
                return

            print(f"   📍 {len(nav_links)} enlaces de navegación encontrados")

            # Definir navegación específica por rol
            navigation_paths = self.get_navigation_paths_by_role(role)

            # Navegar por cada enlace relevante
            for path_name, path_config in navigation_paths.items():
                print(f"\n   🔗 Navegando a: {path_name}")
                self.navigate_to_navbar_section(path_config, role)

            print(f"\n   ✅ Navegación completa del navbar para {role} finalizada")

        except Exception as e:
            print(f"   ❌ Error en navegación del navbar: {str(e)}")

    def get_navigation_paths_by_role(self, role):
        """Definir rutas de navegación lineal específicas por rol (excluyendo dashboard donde empezamos)"""
        base_paths = {
            'student': {
                # Empezamos en Dashboard, navegamos linealmente: Oportunidades → Mi Perfil → Mis Aplicaciones
                'Oportunidades': {'href_contains': 'oportunidades', 'expected_elements': ['job-listing', 'filter-section']},
                'Mi Perfil': {'href_contains': 'profile', 'expected_elements': ['harvard-cv-container', 'cv-upload-area']},
                'Mis Aplicaciones': {'href_contains': 'applications', 'expected_elements': ['application-list', 'application-status']}
            },
            'company': {
                # Empezamos en Dashboard, navegamos linealmente: Buscar Candidatos → Mis Vacantes
                'Buscar Candidatos': {'href_contains': 'buscar-candidatos', 'expected_elements': ['search-filters', 'candidate-list']},
                'Mis Vacantes': {'href_contains': 'mis-vacantes', 'expected_elements': ['vacancy-list', 'create-vacancy-btn']}
            },
            'admin': {
                # Para admin, la navegación se hace dentro del dashboard via sidebar
                # Ya se exploró completamente en demonstrate_admin_dashboard()
                # No navegamos a URLs externas adicionales
                'Dashboard Completado': {'href_contains': 'dashboard', 'expected_elements': ['kpi-grid', 'charts-grid']}
            }
        }

        return base_paths.get(role, {})

    def navigate_to_navbar_section(self, path_config, role):
        """Navegar a una sección específica del navbar SIN volver atrás (flujo lineal)"""
        try:
            href_contains = path_config['href_contains']
            expected_elements = path_config['expected_elements']

            # Para admin, si ya exploramos la sidebar, solo confirmar
            if role == 'admin' and 'Dashboard Completado' in str(path_config):
                print(f"      ✅ Dashboard ya explorado completamente via sidebar")
                print(f"         📊 Secciones exploradas: Estudiantes, Empresas, Empleos, API, Aplicaciones, CV Monitor, Analytics, Configuración")
                return

            # Buscar el enlace correspondiente
            nav_links = self.driver.find_elements(By.CSS_SELECTOR, f"a[href*='{href_contains}']")

            if not nav_links:
                print(f"      ⚠️  Enlace '{href_contains}' no encontrado")
                return

            # Hacer clic en el enlace
            link = nav_links[0]
            link_text = link.text.strip()
            print(f"      🖱️  Clic en: {link_text}")

            # Scroll para asegurar visibilidad
            self.driver.execute_script("arguments[0].scrollIntoView();", link)
            time.sleep(1)

            link.click()
            time.sleep(5)  # Tiempo para carga completa (era 4, ahora 5)

            # Verificar que llegamos a la página correcta
            current_url = self.driver.current_url
            if href_contains in current_url:
                print(f"      ✅ Navegación exitosa a: {current_url}")
            else:
                print(f"      ⚠️  Navegación completada: {current_url}")

            # Demostrar funcionalidades específicas de la página
            self.demonstrate_page_functionality(role, href_contains, expected_elements)

            # NO volver al perfil - mantener flujo lineal

        except Exception as e:
            print(f"      ❌ Error navegando a sección: {str(e)}")

    def demonstrate_page_functionality(self, role, section, expected_elements):
        """Demostrar funcionalidades específicas de cada página"""
        print(f"      🔧 Demostrando funcionalidades de {section}:")

        # Verificar elementos esperados
        found_elements = []
        for element_id in expected_elements:
            if self.check_element_exists(By.ID, element_id) or self.check_element_exists(By.CLASS_NAME, element_id):
                found_elements.append(element_id)

        if found_elements:
            print(f"         ✅ Elementos encontrados: {', '.join(found_elements)}")
        else:
            print(f"         ⚠️  No se encontraron elementos esperados (puede ser normal en demo)")

        # Funcionalidades específicas por rol y sección
        if role == 'student':
            self.demonstrate_student_functionality(section)
        elif role == 'company':
            self.demonstrate_company_functionality(section)
        elif role == 'admin':
            self.demonstrate_admin_functionality(section)

    def navigate_admin_sidebar(self):
        """Navegar por todos los elementos de la sidebar del admin dashboard"""
        print("      🔍 Explorando secciones del admin dashboard:")

        # Definir las secciones de la sidebar y sus elementos característicos
        sidebar_sections = {
            'students': {
                'name': '👨‍🎓 Estudiantes',
                'selector': '.nav-item[data-section="students"]',
                'expected_elements': ['.kpi-card', '.data-table', '#users-tbody'],
                'description': 'Gestión completa de estudiantes registrados'
            },
            'companies': {
                'name': '🏢 Empresas',
                'selector': '.nav-item[data-section="companies"]',
                'expected_elements': ['.companies-grid', '.company-card', '#addCompanyBtn'],
                'description': 'Administrar empresas y reclutadores'
            },
            'jobs': {
                'name': '💼 Empleos',
                'selector': '.nav-item[data-section="jobs"]',
                'expected_elements': ['.data-table', '.filter-select', '.job-listing'],
                'description': 'Revisar y moderar ofertas de empleo'
            },
            'api': {
                'name': '🔌 API Endpoints',
                'selector': '.nav-item[data-section="api"]',
                'expected_elements': ['.api-endpoints', '.endpoint-card', '.system-status'],
                'description': 'Monitorear endpoints y documentación API'
            },
            'applications': {
                'name': '📄 Aplicaciones',
                'selector': '.nav-item[data-section="applications"]',
                'expected_elements': ['.data-table', '.status-badge', '.application-list'],
                'description': 'Seguimiento de postulaciones y matching'
            },
            'cv-monitor': {
                'name': '🤖 CV Monitor',
                'selector': '.nav-item[data-section="cv-monitor"]',
                'expected_elements': ['.progress-card', '.industry-stats', '.seniority-stats'],
                'description': 'Monitoreo de procesamiento de CVs'
            },
            'analytics': {
                'name': '📊 Analytics',
                'selector': '.nav-item[data-section="analytics"]',
                'expected_elements': ['.charts-section', '.kpi-grid', '.date-range'],
                'description': 'Análisis avanzado y reportes detallados'
            },
            'settings': {
                'name': '⚙️ Configuración',
                'selector': '.nav-item[data-section="settings"]',
                'expected_elements': ['.settings-group', '.setting-item', '.btn-primary'],
                'description': 'Configuración del sistema y preferencias'
            }
        }

        # Navegar por cada sección de la sidebar
        for section_key, section_info in sidebar_sections.items():
            try:
                print(f"         {section_info['name']}: {section_info['description']}")

                # Buscar el elemento de navegación
                nav_item = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, section_info['selector']))
                )

                # Hacer clic en el elemento
                nav_item.click()
                time.sleep(4)  # Esperar carga de la sección (era 3, ahora 4)

                # Verificar elementos característicos de la sección
                found_elements = 0
                for element_selector in section_info['expected_elements']:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, element_selector)
                        if elements:
                            found_elements += len(elements)
                    except:
                        pass

                if found_elements > 0:
                    print(f"            ✅ {found_elements} elementos encontrados")
                else:
                    print("            ⚠️  Sección cargada (elementos no visibles en demo)")

                # Demostrar funcionalidades específicas de cada sección
                self.demonstrate_admin_section_features(section_key)

                time.sleep(3)  # Pausa entre secciones (era 2, ahora 3)

            except Exception as e:
                print(f"            ❌ Error navegando a {section_info['name']}: {str(e)}")

        # Volver al dashboard principal
        try:
            dashboard_nav = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.nav-item[data-section="dashboard"]'))
            )
            dashboard_nav.click()
            time.sleep(3)  # Pausa después de regresar (era 2, ahora 3)
            print("         🔄 Regresando al dashboard principal")
        except Exception as e:
            print(f"         ⚠️  Error regresando al dashboard: {str(e)}")

    def demonstrate_student_functionality(self, section):
        """Demostrar funcionalidades específicas para estudiantes"""
        if 'profile' in section:
            print("         📄 Gestionando perfil y CV...")
            # Verificar elementos de CV
            cv_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='cv'], [class*='upload'], #cv-upload-area")
            if cv_elements:
                print(f"         📎 {len(cv_elements)} elementos de CV disponibles")
            # Verificar Harvard CV container
            harvard_elements = self.driver.find_elements(By.ID, "harvard-cv-container")
            if harvard_elements:
                print(f"         🎓 Harvard CV container encontrado")
        elif 'oportunidades' in section:
            print("         🎯 Probando filtros de oportunidades...")
            # Intentar interactuar con filtros si existen
            filter_buttons = self.driver.find_elements(By.CLASS_NAME, "filter-btn")
            if filter_buttons:
                print(f"         📊 {len(filter_buttons)} filtros disponibles")
        elif 'applications' in section:
            print("         📄 Revisando estado de aplicaciones...")
            # Verificar estados de aplicaciones
            status_badges = self.driver.find_elements(By.CLASS_NAME, "status-badge")
            if status_badges:
                print(f"         📊 {len(status_badges)} aplicaciones encontradas")

    def demonstrate_company_functionality(self, section):
        """Demostrar funcionalidades específicas para empresas"""
        if 'buscar-candidatos' in section:
            print("         🔍 Probando búsqueda de candidatos...")
            # Intentar usar filtros de búsqueda
            search_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='buscar'], input[type='search']")
            if search_inputs:
                print(f"         🔎 {len(search_inputs)} campos de búsqueda disponibles")
        elif 'mis-vacantes' in section:
            print("         💼 Gestionando vacantes...")
            # Verificar botones de gestión
            action_buttons = self.driver.find_elements(By.CLASS_NAME, "action-btn")
            if action_buttons:
                print(f"         ⚙️  {len(action_buttons)} acciones disponibles")

    def demonstrate_admin_section_features(self, section_key):
        """Demostrar funcionalidades específicas de cada sección del admin dashboard"""
        try:
            if section_key == 'students':
                self.demonstrate_admin_students_section()
            elif section_key == 'companies':
                self.demonstrate_admin_companies_section()
            elif section_key == 'jobs':
                self.demonstrate_admin_jobs_section()
            elif section_key == 'api':
                self.demonstrate_admin_api_section()
            elif section_key == 'applications':
                self.demonstrate_admin_applications_section()
            elif section_key == 'cv-monitor':
                self.demonstrate_admin_cv_monitor_section()
            elif section_key == 'analytics':
                self.demonstrate_admin_analytics_section()
            elif section_key == 'settings':
                self.demonstrate_admin_settings_section()
        except Exception as e:
            print(f"            ⚠️  Error demostrando funcionalidades: {str(e)}")

    def demonstrate_admin_students_section(self):
        """Demostrar funcionalidades de la sección de estudiantes"""
        print("            �‍🎓 Gestionando estudiantes:")
        # Verificar KPIs de estudiantes
        kpi_cards = self.driver.find_elements(By.CLASS_NAME, "kpi-card")
        if kpi_cards:
            print(f"               📊 {len(kpi_cards)} métricas de estudiantes")
        # Verificar tabla de usuarios
        user_rows = self.driver.find_elements(By.CSS_SELECTOR, "#users-tbody tr")
        if user_rows:
            print(f"               👥 {len(user_rows)} estudiantes listados")
        # Verificar filtros
        filters = self.driver.find_elements(By.CSS_SELECTOR, "#role-filter, #status-filter, #search-input")
        if filters:
            print(f"               🔍 {len(filters)} opciones de filtrado")

    def demonstrate_admin_companies_section(self):
        """Demostrar funcionalidades de la sección de empresas"""
        print("            🏢 Gestionando empresas:")
        # Verificar grid de empresas
        company_cards = self.driver.find_elements(By.CLASS_NAME, "company-card")
        if company_cards:
            print(f"               🏢 {len(company_cards)} empresas listadas")
        # Verificar botón de agregar empresa
        add_btn = self.driver.find_elements(By.ID, "addCompanyBtn")
        if add_btn:
            print("               ➕ Opción para agregar nuevas empresas")
        # Verificar filtros
        filters = self.driver.find_elements(By.CLASS_NAME, "filter-select")
        if filters:
            print(f"               � {len(filters)} filtros disponibles")

    def demonstrate_admin_jobs_section(self):
        """Demostrar funcionalidades de la sección de empleos"""
        print("            💼 Gestionando empleos:")
        # Verificar tabla de empleos
        job_rows = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if job_rows:
            print(f"               💼 {len(job_rows)} empleos listados")
        # Verificar badges de estado
        status_badges = self.driver.find_elements(By.CLASS_NAME, "status-badge")
        if status_badges:
            print(f"               📊 {len(status_badges)} estados de empleos")
        # Verificar filtros
        filters = self.driver.find_elements(By.CLASS_NAME, "filter-select")
        if filters:
            print("               🔍 Filtros por estado disponibles")

    def demonstrate_admin_api_section(self):
        """Demostrar funcionalidades de la sección API"""
        print("            🔌 Monitoreando APIs:")
        # Verificar endpoints
        endpoints = self.driver.find_elements(By.CLASS_NAME, "endpoint-card")
        if endpoints:
            print(f"               � {len(endpoints)} endpoints monitoreados")
        # Verificar estado del sistema
        status_items = self.driver.find_elements(By.CLASS_NAME, "status-item")
        if status_items:
            print(f"               ⚙️  {len(status_items)} servicios del sistema")
        # Verificar pestañas
        tabs = self.driver.find_elements(By.CLASS_NAME, "tab-btn")
        if tabs:
            print(f"               📑 {len(tabs)} secciones de monitoreo")

    def demonstrate_admin_applications_section(self):
        """Demostrar funcionalidades de la sección de aplicaciones"""
        print("            📄 Gestionando aplicaciones:")
        # Verificar tabla de aplicaciones
        app_rows = self.driver.find_elements(By.CSS_SELECTOR, ".data-table tbody tr")
        if app_rows:
            print(f"               📄 {len(app_rows)} aplicaciones registradas")
        # Verificar estados
        status_badges = self.driver.find_elements(By.CLASS_NAME, "status-badge")
        if status_badges:
            print(f"               📊 {len(status_badges)} estados de aplicación")
        # Verificar filtros
        filters = self.driver.find_elements(By.CLASS_NAME, "filter-select")
        if filters:
            print("               🔍 Filtros por estado disponibles")

    def demonstrate_admin_cv_monitor_section(self):
        """Demostrar funcionalidades de la sección CV Monitor"""
        print("            🤖 Monitoreando CVs:")
        # Verificar progreso
        progress_bars = self.driver.find_elements(By.CLASS_NAME, "progress-bar")
        if progress_bars:
            print(f"               📈 {len(progress_bars)} barras de progreso")
        # Verificar estadísticas por industria
        industry_stats = self.driver.find_elements(By.CLASS_NAME, "industry-stats")
        if industry_stats:
            print("               🏭 Estadísticas por industria disponibles")
        # Verificar estadísticas por seniority
        seniority_stats = self.driver.find_elements(By.CLASS_NAME, "seniority-stats")
        if seniority_stats:
            print("               📊 Estadísticas por seniority disponibles")

    def demonstrate_admin_analytics_section(self):
        """Demostrar funcionalidades de la sección Analytics"""
        print("            📊 Analizando datos:")
        # Verificar gráficos
        charts = self.driver.find_elements(By.CSS_SELECTOR, ".chart-card, canvas")
        if charts:
            print(f"               📈 {len(charts)} gráficos analíticos")
        # Verificar KPIs
        kpi_cards = self.driver.find_elements(By.CLASS_NAME, "kpi-card")
        if kpi_cards:
            print(f"               📊 {len(kpi_cards)} métricas principales")
        # Verificar selectores de fecha
        date_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='date']")
        if date_inputs:
            print("               📅 Filtros de fecha disponibles")

    def demonstrate_admin_settings_section(self):
        """Demostrar funcionalidades de la sección de configuración"""
        print("            ⚙️ Configurando sistema:")
        # Verificar grupos de configuración
        settings_groups = self.driver.find_elements(By.CLASS_NAME, "settings-group")
        if settings_groups:
            print(f"               ⚙️  {len(settings_groups)} grupos de configuración")
        # Verificar items de configuración
        setting_items = self.driver.find_elements(By.CLASS_NAME, "setting-item")
        if setting_items:
            print(f"               🔧 {len(setting_items)} opciones configurables")
        # Verificar botones de acción
        action_btns = self.driver.find_elements(By.CSS_SELECTOR, ".btn-primary, .btn-outline")
        if action_btns:
            print(f"               💾 {len(action_btns)} acciones disponibles")

    def capture_final_state(self, role):
        """Capturar el estado final de la demostración"""
        print(f"\n📸 Estado final de la demostración para {role}:")

        # Recopilar información del estado actual
        state_info = {
            'url': self.driver.current_url,
            'title': self.driver.title,
            'role': role,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        # Verificar elementos clave presentes
        key_elements = {
            'navbar': self.check_element_exists(By.ID, "navbar-container"),
            'profile_form': self.check_element_exists(By.ID, "profile-form"),
            'harvard_cv': self.check_element_exists(By.ID, "harvard-cv-container"),
            'cv_upload': self.check_element_exists(By.ID, "cv-upload-card")
        }

        state_info['elements_present'] = key_elements

        self.demo_data[role] = state_info

        print(f"   ✅ URL final: {state_info['url']}")
        print(f"   ✅ Título: {state_info['title']}")
        print(f"   ✅ Elementos presentes: {sum(key_elements.values())}/{len(key_elements)}")

    def run_complete_showcase(self):
        """Ejecutar demostración completa de todos los roles"""
        print("🎬 === MOIRAI MVP DEMO SHOWCASE ===")
        print("=" * 60)
        print("🚀 Demostrando EXPLORACIÓN COMPLETA: raíz + navegación lineal + funcionalidades")
        print("📱 Navegación visual - Flujo continuo sin repeticiones")
        print("=" * 60)

        results = {}

        for role in self.roles:
            result = self.showcase_role(role)
            results[role] = result

            if result["success"]:
                print(f"✅ {role.upper()}: DEMOSTRACIÓN COMPLETADA")
            else:
                print(f"❌ {role.upper()}: ERROR - {result.get('error', 'Error desconocido')}")

            # Pausa entre roles para observación
            if role != self.roles[-1]:  # No pausar después del último
                print(f"\n⏳ Preparando siguiente rol... ({6} segundos)")
                time.sleep(6)

        print("\n" + "=" * 60)
        print("📊 RESULTADOS DE LA DEMOSTRACIÓN:")

        successful = sum(1 for r in results.values() if r["success"])
        total = len(results)

        print(f"✅ Demostraciones exitosas: {successful}/{total}")

        if successful == total:
            print("🎉 ¡Demostración MVP completada exitosamente!")
            print("✅ Navegación completa del navbar y funcionalidades demostradas")
        else:
            print("⚠️  Algunas demostraciones tuvieron problemas")

        return results

    def check_element_exists(self, by, value):
        """Verificar si un elemento existe"""
        try:
            self.driver.find_element(by, value)
            return True
        except NoSuchElementException:
            return False

    def cleanup(self):
        """Limpiar recursos"""
        if self.driver:
            self.driver.quit()

    def _scroll_to_section(self, section_key, selector):
        """Hacer scroll a la sección específica para posicionarla correctamente en pantalla"""
        try:
            print(f"         🎯 Posicionando sección {section_key}...")

            # Buscar elementos de la sección
            section_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

            if section_elements:
                # Hacer scroll al primer elemento encontrado
                first_element = section_elements[0]
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'start'});", first_element)
                time.sleep(2)  # Tiempo para que el scroll se complete
                print(f"         ✅ Sección {section_key} posicionada correctamente")
            else:
                print(f"         ⚠️  No se encontraron elementos para la sección {section_key}, comenzando desde posición actual")

        except Exception as e:
            print(f"         ⚠️  Error posicionando sección {section_key}: {str(e)}, continuando desde posición actual")


def main():
    print("🎬 === MOIRAI MVP DEMO SHOWCASE - MODO CONTINUO ===")
    print("=" * 60)
    print("🚀 Demostración automática en bucle continuo")
    print("📱 Navegación visual - Se repite automáticamente")
    print("⏹️  Presiona Ctrl+C para detener")
    print("=" * 60)

    cycle_count = 0

    try:
        while True:
            cycle_count += 1
            print(f"\n🔄 === CICLO #{cycle_count} ===")
            print(f"⏰ Iniciado: {time.strftime('%H:%M:%S')}")

            showcase = None
            try:
                # Crear nueva instancia para cada ciclo (con manejo de errores)
                print("🔧 Inicializando demostración...")
                showcase = MoirAIDemoShowcase()
                
                print("🎬 Iniciando Demo Showcase de MoirAI MVP...")
                print("💡 Esta demostración mostrará EXPLORACIÓN COMPLETA:")
                print("   🏠 2.5 minutos explorando la raíz por secciones principales")
                print("   🧭 Navegación LINEAL del navbar desde Dashboard hasta la última sección")
                print("   👥 Demostración de funcionalidades para todos los roles")

                results = showcase.run_complete_showcase()

                # Guardar resultados
                with open('/Users/sparkmachine/MoirAI/demo_showcase_results.json', 'w') as f:
                    json.dump({
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'cycle': cycle_count,
                        'results': results,
                        'demo_data': showcase.demo_data
                    }, f, indent=2, ensure_ascii=False)

                print("\n💾 Resultados guardados en: demo_showcase_results.json")

                print("\n🎯 RESUMEN DE FUNCIONALIDADES DEMOSTRADAS:")
                print("🏠 RAÍZ: Exploración completa de 5 secciones principales (Hero, Características, Cómo Funciona, Para Quién es MoirAI, Historias de Éxito) - 2.5 minutos")
                print("👨‍🎓 ESTUDIANTES: Dashboard personal → Oportunidades → Mi Perfil (CV) → Aplicaciones")
                print("🏢 EMPRESAS: Dashboard KPIs → Búsqueda candidatos → Gestión vacantes")
                print("👨‍💼 ADMINS: Dashboard sistema → Exploración completa de sidebar (Estudiantes, Empresas, Empleos, API, Aplicaciones, CV Monitor, Analytics, Configuración)")

                successful = sum(1 for r in results.values() if r["success"])
                total = len(results)

                if successful == total:
                    print(f"\n🎉 ¡Ciclo #{cycle_count} completado exitosamente!")
                    print("✅ Navegación completa del navbar y funcionalidades demostradas")
                else:
                    print(f"\n⚠️  Ciclo #{cycle_count} completado con algunos problemas")

            except ConnectionError as e:
                print(f"\n❌ Error de conectividad: {str(e)}")
                print("\n📋 INSTRUCCIONES:")
                print("   1. Abre una nueva terminal")
                print("   2. Ejecuta: uvicorn app.main:app --reload")
                print("   3. Espera hasta que veas: 'Application startup complete.'")
                print("   4. Vuelve aquí y reinicia este script")
                raise
                
            except Exception as e:
                print(f"\n❌ Error inicializando demostración: {str(e)}")
                import traceback
                traceback.print_exc()
                print("\n📋 AYUDA DE DIAGNÓSTICO:")
                print("   - ¿El backend está corriendo? (uvicorn app.main:app --reload)")
                print("   - ¿Chrome está instalado? (brew install --cask google-chrome)")
                print("   - ¿Puedes acceder a http://127.0.0.1:8000?")
                
            finally:
                if showcase:
                    showcase.cleanup()

            # Pausa entre ciclos
            print(f"\n⏳ Esperando 10 segundos antes del siguiente ciclo...")
            print("   Presiona Ctrl+C para detener la demostración")
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n⏹️  Demostración detenida por el usuario")
        print(f"✅ Total de ciclos completados: {cycle_count}")
    except Exception as e:
        print(f"\n❌ Error fatal: {str(e)}")
        print(f"✅ Ciclos completados antes del error: {cycle_count}")


if __name__ == "__main__":
    main()
