#!/usr/bin/env python3
"""
MoirAI Demo Mode Visual Demonstration - Navegación Completa
Script automatizado que demuestra visualmente la navegación completa del navbar
y funcionalidades específicas para cada rol en modo demo.
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class MoirAIDemoShowcase:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.roles = ['student', 'company', 'admin']
        self.demo_data = {}

        # Configurar Chrome en modo visual (no headless para demostración)
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        # Inicializar el driver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

        self.wait = WebDriverWait(self.driver, 15)

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
        """Navegar por secciones de la raíz durante 2.5 minutos antes de ir al dashboard del estudiante"""
        print(f"\n🏠 === EXPLORACIÓN DE LA RAÍZ - 2.5 MINUTOS ===")
        print("📖 Navegando por secciones principales antes de acceder al dashboard")

        # Ir a la página raíz
        root_url = f"{self.base_url}/"
        print(f"🌐 Iniciando exploración en: {root_url}")
        self.driver.get(root_url)
        time.sleep(3)  # Tiempo inicial para carga

        # Definir secciones de la raíz y su tiempo de exploración
        # Total: 150 segundos (2.5 minutos) dividido en 4 secciones = 37.5 segundos cada una
        root_sections = {
            'hero-about': {
                'name': '🎯 Hero/About - Presentación de MoirAI',
                'selector': '[id*="hero"], [class*="hero"], [id*="about"], [class*="about"], header, .hero-section',
                'description': 'Sección principal con presentación de la plataforma',
                'time_seconds': 37.5
            },
            'for-students': {
                'name': '👨‍🎓 For Students - Información para estudiantes',
                'selector': '[id*="student"], [class*="student"], [href*="student"], #students-section',
                'description': 'Información específica para estudiantes de UNRC',
                'time_seconds': 37.5
            },
            'for-companies': {
                'name': '🏢 For Companies - Información para empresas',
                'selector': '[id*="company"], [class*="company"], [href*="company"], #companies-section',
                'description': 'Información para empresas colaboradoras',
                'time_seconds': 37.5
            },
            'how-it-works': {
                'name': '⚙️ How it Works - Cómo funciona la plataforma',
                'selector': '[id*="how"], [class*="how"], [id*="work"], [class*="work"], #how-it-works',
                'description': 'Explicación del funcionamiento del sistema de matching',
                'time_seconds': 37.5
            }
        }

        total_time = 0
        for section_key, section_info in root_sections.items():
            section_start_time = time.time()

            print(f"\n   📑 Explorando: {section_info['name']}")
            print(f"      {section_info['description']}")
            print(f"      ⏱️  Tiempo asignado: {section_info['time_seconds']} segundos")

            # Scroll gradual y natural para simular exploración de usuario
            print("         📜 Iniciando exploración gradual...")
            self.perform_gradual_scroll_exploration(section_info['time_seconds'])
            print("         ✅ Exploración gradual completada")

            # Intentar navegar a la sección específica (sin scroll agresivo)
            section_found = False
            try:
                # Buscar elementos de navegación a esta sección
                nav_elements = self.driver.find_elements(By.CSS_SELECTOR, f"a[href*='{section_key}'], button[class*='{section_key}'], .{section_key}-nav")

                if nav_elements:
                    # Hacer clic en el primer elemento encontrado (sin scroll adicional)
                    nav_elements[0].click()
                    time.sleep(2)  # Tiempo para carga
                    section_found = True
                    print("         ✅ Navegación directa encontrada y ejecutada")
                else:
                    # Solo verificar si existen elementos de la sección (sin scroll)
                    section_elements = self.driver.find_elements(By.CSS_SELECTOR, section_info['selector'])
                    if section_elements:
                        section_found = True
                        print("         ✅ Elementos de sección encontrados (exploración continua)")
                    else:
                        print("         📝 Sección no localizada específicamente (exploración general)")
                        section_found = True  # Continuar de todas formas
            except Exception as e:
                print(f"         ⚠️  Error en navegación: {str(e)} (continuando con exploración)")
                section_found = True  # No fallar por esto

            # Demostrar elementos encontrados en la sección
            self.demonstrate_root_section_features(section_key, section_info)

            # Esperar el tiempo asignado para esta sección (el scroll gradual continúa)
            elapsed = time.time() - section_start_time
            remaining_time = max(0, section_info['time_seconds'] - elapsed)

            if remaining_time > 0:
                print(f"         ⏳ Completando exploración gradual: {remaining_time:.1f} segundos restantes...")
                # El scroll gradual continúa automáticamente en perform_gradual_scroll_exploration
                time.sleep(remaining_time)

            total_time += section_info['time_seconds']
            print(f"      ✅ Sección {section_key} completada ({total_time}s total)")

        print(f"\n🏁 Exploración de raíz completada: {total_time} segundos (2.5 minutos)")
        print("   ✅ Todas las secciones principales han sido exploradas")

    def perform_gradual_scroll_exploration(self, duration_seconds):
        """Realizar exploración gradual con scrolls naturales hasta la sección de Historias de Éxito"""
        start_time = time.time()
        scroll_count = 0

        # Obtener altura total de la página
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        current_position = self.driver.execute_script("return window.pageYOffset")
        window_height = self.driver.execute_script("return window.innerHeight")

        print(f"         📏 Página total: {total_height}px, Posición actual: {current_position}px")

        # Buscar la sección de Historias de Éxito
        testimonials_section = None
        testimonial_selectors = [
            "[class*='testimonials']",
            "[id*='testimonials']",
            "[class*='historias']",
            "[id*='historias']",
            "[class*='success-stories']",
            "[id*='success-stories']",
            ".testimonial-section",
            "#testimonial-section",
            "[data-section*='testimonials']",
            "[data-section*='historias']"
        ]

        for selector in testimonial_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    testimonials_section = elements[0]
                    print(f"         🎯 Sección de Historias de Éxito encontrada con selector: {selector}")
                    break
            except:
                continue

        # Si no encontramos la sección por selectores, buscar por texto
        if not testimonials_section:
            try:
                elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Historias de Éxito') or contains(text(), 'Testimonios') or contains(text(), 'Casos de Éxito')]")
                if elements:
                    testimonials_section = elements[0]
                    print("         🎯 Sección de Historias de Éxito encontrada por texto")
            except:
                pass

        # Buscar testimonios específicos
        testimonial_found = False
        specific_testimonials = [
            "Ana Carrillo",
            "Jorge Rodríguez",
            "María Bernal"
        ]

        for name in specific_testimonials:
            try:
                elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{name}')]")
                if elements:
                    testimonial_found = True
                    print(f"         👤 Testimonio encontrado: {name}")
                    if not testimonials_section:
                        testimonials_section = elements[0]
            except:
                continue

        if testimonial_found:
            print("         ✅ Testimonios específicos localizados")
        else:
            print("         ⚠️  Testimonios específicos no encontrados (puede ser normal)")

        # Si encontramos la sección, hacer scroll hasta ella
        if testimonials_section:
            try:
                # Obtener posición de la sección
                section_position = self.driver.execute_script("""
                    var element = arguments[0];
                    var rect = element.getBoundingClientRect();
                    return rect.top + window.pageYOffset;
                """, testimonials_section)

                target_position = section_position - (window_height * 0.3)  # Posicionar con margen superior
                max_scroll_position = total_height - window_height * 0.8  # No llegar al 100% de la página

                # Asegurar que no se pase del límite
                target_position = min(target_position, max_scroll_position)

                print(f"         📍 Desplazándose a posición: {int(target_position)}px (sección testimonios)")

                # Scroll gradual hasta la sección
                steps = 20  # Más pasos para scroll más suave
                step_duration = duration_seconds / steps

                for step in range(steps):
                    elapsed = time.time() - start_time
                    if elapsed >= duration_seconds:
                        break

                    progress = step / (steps - 1)
                    current_target = current_position + (target_position - current_position) * progress

                    self.driver.execute_script(f"window.scrollTo({{top: {current_target}, behavior: 'smooth'}});")
                    scroll_count += 1

                    time.sleep(step_duration)

                    # Verificar si ya estamos cerca de la posición objetivo
                    current_pos = self.driver.execute_script("return window.pageYOffset")
                    if abs(current_pos - target_position) < 50:  # Margen de 50px
                        print(f"         ✅ Posición objetivo alcanzada en paso {step + 1}")
                        break

                print(f"         🎯 Exploración completada: {scroll_count} scrolls realizados hasta testimonios")

            except Exception as e:
                print(f"         ⚠️  Error en scroll inteligente: {str(e)}")
                # Fallback a scroll gradual normal
                self._fallback_gradual_scroll(duration_seconds)
        else:
            print("         ⚠️  Sección de testimonios no encontrada, realizando scroll gradual normal")
            self._fallback_gradual_scroll(duration_seconds)

    def _fallback_gradual_scroll(self, duration_seconds):
        """Método de respaldo para scroll gradual normal"""
        start_time = time.time()
        scroll_count = 0

        total_height = self.driver.execute_script("return document.body.scrollHeight")
        current_position = self.driver.execute_script("return window.pageYOffset")
        window_height = self.driver.execute_script("return window.innerHeight")

        max_scroll_position = total_height - window_height * 0.8  # No llegar al 100%

        while (time.time() - start_time) < duration_seconds:
            elapsed = time.time() - start_time
            remaining = duration_seconds - elapsed

            progress = elapsed / duration_seconds

            if current_position < max_scroll_position:
                scroll_amount = 100 + (progress * 50)

                new_position = min(current_position + scroll_amount, max_scroll_position)

                self.driver.execute_script(f"window.scrollTo({{top: {new_position}, behavior: 'smooth'}});")
                scroll_count += 1

                time.sleep(1.2)

                current_position = new_position

                if scroll_count % 5 == 0:
                    progress_pct = int(progress * 100)
                    print(f"         � Scroll {scroll_count} - Progreso: {progress_pct}% ({int(elapsed)}s/{duration_seconds}s)")
            else:
                print("         🔄 Manteniendo posición (límite alcanzado)")
                time.sleep(min(remaining, 2))

        print(f"         ✅ Scroll gradual completado: {scroll_count} scrolls realizados")

    def demonstrate_root_section_features(self, section_key, section_info):
        """Demostrar funcionalidades específicas de cada sección de la raíz"""
        print(f"         🔍 Explorando contenido de la sección:")

        try:
            if section_key == 'hero-about':
                self.demonstrate_hero_about_section()
            elif section_key == 'for-students':
                self.demonstrate_for_students_section()
            elif section_key == 'for-companies':
                self.demonstrate_for_companies_section()
            elif section_key == 'how-it-works':
                self.demonstrate_how_it_works_section()
        except Exception as e:
            print(f"            ⚠️  Error demostrando funcionalidades: {str(e)}")

    def demonstrate_hero_about_section(self):
        """Demostrar funcionalidades de la sección Hero/About"""
        print("            🎯 Explorando sección principal:")

        # Verificar elementos del hero (sin scroll adicional)
        hero_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='hero'], [id*='hero'], h1, .title, .subtitle")
        if hero_elements:
            print(f"               📋 {len(hero_elements)} elementos de presentación encontrados")

        # Verificar botones de acción principales
        cta_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".btn-primary, .cta-btn, [class*='call-to-action'], button")
        if cta_buttons:
            print(f"               🎯 {len(cta_buttons)} botones de acción principales")

        # Verificar elementos visuales
        images = self.driver.find_elements(By.CSS_SELECTOR, "img, .hero-image, .background-image")
        if images:
            print(f"               🖼️  {len(images)} elementos visuales")

        # Verificar navegación
        nav_elements = self.driver.find_elements(By.CSS_SELECTOR, "nav, .navbar, .navigation")
        if nav_elements:
            print("               🧭 Elementos de navegación presentes")

    def demonstrate_for_students_section(self):
        """Demostrar funcionalidades de la sección For Students"""
        print("            👨‍🎓 Explorando sección estudiantes:")

        # Verificar información específica para estudiantes
        student_info = self.driver.find_elements(By.CSS_SELECTOR, "[class*='student'], [id*='student'], .student-info, .student-benefits")
        if student_info:
            print(f"               📚 {len(student_info)} elementos informativos para estudiantes")

        # Verificar beneficios o características
        benefits = self.driver.find_elements(By.CSS_SELECTOR, ".benefit, .feature, .advantage, [class*='benefit']")
        if benefits:
            print(f"               ✅ {len(benefits)} beneficios destacados")

        # Verificar llamadas a acción para estudiantes
        student_ctas = self.driver.find_elements(By.CSS_SELECTOR, "[href*='student'], [href*='register'], .student-btn")
        if student_ctas:
            print(f"               🎓 {len(student_ctas)} acciones específicas para estudiantes")

        # Verificar testimonios o casos de éxito
        testimonials = self.driver.find_elements(By.CSS_SELECTOR, ".testimonial, .success-story, [class*='testimonial']")
        if testimonials:
            print(f"               💬 {len(testimonials)} testimonios o casos de éxito")

    def demonstrate_for_companies_section(self):
        """Demostrar funcionalidades de la sección For Companies"""
        print("            🏢 Explorando sección empresas:")

        # Verificar información específica para empresas
        company_info = self.driver.find_elements(By.CSS_SELECTOR, "[class*='company'], [id*='company'], .company-info, .employer-info")
        if company_info:
            print(f"               🏭 {len(company_info)} elementos informativos para empresas")

        # Verificar procesos de reclutamiento
        recruitment = self.driver.find_elements(By.CSS_SELECTOR, "[class*='recruit'], [class*='hire'], .recruitment-process")
        if recruitment:
            print(f"               🎯 {len(recruitment)} elementos sobre reclutamiento")

        # Verificar llamadas a acción para empresas
        company_ctas = self.driver.find_elements(By.CSS_SELECTOR, "[href*='company'], [href*='employer'], .company-btn")
        if company_ctas:
            print(f"               💼 {len(company_ctas)} acciones específicas para empresas")

        # Verificar estadísticas o métricas
        stats = self.driver.find_elements(By.CSS_SELECTOR, ".stat, .metric, .number, [class*='stat']")
        if stats:
            print(f"               📊 {len(stats)} estadísticas o métricas mostradas")

    def demonstrate_how_it_works_section(self):
        """Demostrar funcionalidades de la sección How it Works"""
        print("            ⚙️ Explorando sección funcionamiento:")

        # Verificar pasos del proceso
        steps = self.driver.find_elements(By.CSS_SELECTOR, ".step, .process-step, [class*='step'], .phase")
        if steps:
            print(f"               🔢 {len(steps)} pasos del proceso identificados")

        # Verificar explicaciones o guías
        explanations = self.driver.find_elements(By.CSS_SELECTOR, ".explanation, .guide, .how-to, [class*='explain']")
        if explanations:
            print(f"               📖 {len(explanations)} explicaciones disponibles")

        # Verificar elementos interactivos
        interactive = self.driver.find_elements(By.CSS_SELECTOR, ".interactive, .demo, button, .clickable")
        if interactive:
            print(f"               🖱️  {len(interactive)} elementos interactivos")

        # Verificar diagramas o flujos
        diagrams = self.driver.find_elements(By.CSS_SELECTOR, ".diagram, .flowchart, canvas, svg")
        if diagrams:
            print(f"               📈 {len(diagrams)} diagramas o representaciones visuales")

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

            # Crear nueva instancia para cada ciclo
            showcase = MoirAIDemoShowcase()

            try:
                print("🎬 Iniciando Demo Showcase de MoirAI MVP...")
                print("💡 Esta demostración mostrará EXPLORACIÓN COMPLETA:")
                print("   🏠 2.5 minutos explorando la raíz por secciones principales")
                print("   🧭 Navegación LINEAL del navbar desde Dashboard hasta la última sección")
                print("   👥 Demostración de funcionalidades para todos los roles")
                print("⏳ Asegúrate de que el servidor esté corriendo en localhost:8000")

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
                print("🏠 RAÍZ: Exploración completa de 4 secciones principales (Hero/About, For Students, For Companies, How it Works) - 2.5 minutos")
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

            finally:
                showcase.cleanup()

            # Pausa entre ciclos
            print(f"\n⏳ Esperando 10 segundos antes del siguiente ciclo...")
            print("   Presiona Ctrl+C para detener la demostración")
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n⏹️  Demostración detenida por el usuario")
        print(f"✅ Total de ciclos completados: {cycle_count}")
    except Exception as e:
        print(f"❌ Error general en la demostración: {str(e)}")
        print(f"✅ Ciclos completados antes del error: {cycle_count}")


if __name__ == "__main__":
    main()
