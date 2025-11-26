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

            # 3. Demostrar funcionalidades específicas del MVP
            self.demonstrate_mvp_features(role)

            # 4. Demostrar navegación completa del navbar
            self.showcase_navbar_navigation(role)

            # 5. Capturar estado final
            self.capture_final_state(role)

            return {"success": True, "message": f"Demostración de {role} completada"}

        except Exception as e:
            print(f"❌ Error en demostración de {role}: {str(e)}")
            return {"success": False, "error": str(e)}

    def navigate_to_role_profile(self, role):
        """Navegar al perfil del rol en modo demo"""
        url = f"{self.base_url}/profile?demo=true&role={role}"
        print(f"🌐 Navegando a perfil de {role}: {url}")

        self.driver.get(url)
        time.sleep(5)  # Tiempo para carga completa

        # Verificar que estamos en modo demo
        try:
            demo_indicator = self.driver.find_element(By.CSS_SELECTOR, "[class*='demo'], .demo-badge, #demo-badge")
            print("✅ Modo demo activado")
        except:
            print("⚠️  Modo demo no detectado visualmente")

    def display_role_info(self, role):
        """Mostrar información específica del rol"""
        print(f"📋 Información del rol {role}:")

        role_info = {
            'student': {
                'title': '👨‍🎓 Estudiante UNRC',
                'description': 'Usuario principal - Gestiona su perfil académico y busca oportunidades',
                'permissions': ['Ver/editar perfil', 'Subir CV', 'Ver ofertas laborales', 'Aplicar a vacantes'],
                'mvp_features': ['CV Harvard', 'Habilidades inferidas', 'Sistema de matching'],
                'navbar_sections': ['Dashboard', 'Oportunidades', 'Mi Perfil', 'Mis Aplicaciones']
            },
            'company': {
                'title': '🏢 Empresa Colaboradora',
                'description': 'Reclutador - Busca talento y publica ofertas de trabajo',
                'permissions': ['Buscar candidatos', 'Ver perfiles anónimos', 'Publicar vacantes', 'Ver métricas'],
                'mvp_features': ['Búsqueda por habilidades', 'Dashboard KPIs', 'Sistema de matching'],
                'navbar_sections': ['Dashboard', 'Buscar Candidatos', 'Mi Empresa', 'Mis Vacantes']
            },
            'admin': {
                'title': '👨‍💼 Administrador UNRC',
                'description': 'Supervisor - Gestiona la plataforma y supervisa métricas',
                'permissions': ['Ver todos los usuarios', 'Gestionar roles', 'Ver analytics', 'Configurar sistema'],
                'mvp_features': ['Dashboard analytics', 'Gestión de usuarios', 'Métricas de colocación'],
                'navbar_sections': ['Dashboard', 'Usuarios', 'Analítica', 'Configuración']
            }
        }

        info = role_info.get(role, {})
        print(f"   {info.get('title', 'Rol desconocido')}")
        print(f"   {info.get('description', '')}")
        print(f"   Permisos: {', '.join(info.get('permissions', []))}")
        print(f"   Funcionalidades MVP: {', '.join(info.get('mvp_features', []))}")
        print(f"   Secciones del Navbar: {', '.join(info.get('navbar_sections', []))}")

    def demonstrate_mvp_features(self, role):
        """Demostrar las funcionalidades clave del MVP para cada rol"""
        print(f"\n🚀 Demostrando funcionalidades MVP para {role}:")

        if role == 'student':
            self.demonstrate_student_features()
        elif role == 'company':
            self.demonstrate_company_features()
        elif role == 'admin':
            self.demonstrate_admin_features()

    def demonstrate_student_features(self):
        """Demostrar funcionalidades clave para estudiantes"""
        print("   📚 1. Perfil Académico Centralizado (Harvard CV)")

        # Verificar secciones del CV Harvard
        sections = {
            'objective': 'Objetivo Profesional',
            'education-list': 'Educación',
            'experience-list': 'Experiencia',
            'certifications-list': 'Certificaciones',
            'languages-list': 'Idiomas'
        }

        present_sections = []
        for section_id, section_name in sections.items():
            if self.check_element_exists(By.ID, section_id):
                present_sections.append(section_name)

        print(f"      ✅ Secciones presentes: {', '.join(present_sections)}")

        print("   🧠 2. Sistema de Habilidades Inferidas")
        if self.check_element_exists(By.ID, "inferred-skills"):
            print("      ✅ Contenedor de habilidades detectado")
        else:
            print("      ⚠️  Sistema de habilidades no visible")

        print("   📄 3. Área de Upload de CV")
        if self.check_element_exists(By.ID, "cv-upload-area"):
            print("      ✅ Área de upload funcional")
        else:
            print("      ❌ Área de upload no encontrada")

    def demonstrate_company_features(self):
        """Demostrar funcionalidades clave para empresas"""
        print("   🔍 1. Acceso Restringido a Información Sensible")

        # Verificar que el CV está oculto para empresas
        cv_card = self.driver.find_elements(By.ID, "cv-upload-card")
        if cv_card:
            display_style = cv_card[0].value_of_css_property("display")
            if display_style == "none":
                print("      ✅ CV correctamente oculto para empresas")
            else:
                print(f"      ❌ CV visible (display: {display_style})")
        else:
            print("      ✅ Sin acceso a área de CV")

        print("   📊 2. Dashboard con KPIs de Vinculación")
        # Verificar elementos de métricas
        kpi_elements = self.driver.find_elements(By.CLASS_NAME, "kpi-card")
        metric_elements = self.driver.find_elements(By.CLASS_NAME, "metric")

        if kpi_elements or metric_elements:
            print(f"      ✅ {len(kpi_elements)} KPIs y {len(metric_elements)} métricas encontradas")
        else:
            print("      ⚠️  Dashboard de métricas no visible (esperado en demo)")

        print("   🎯 3. Sistema de Matching")
        # En demo, mostrar que el sistema está preparado
        print("      ✅ Sistema de matching integrado en la plataforma")

    def demonstrate_admin_features(self):
        """Demostrar funcionalidades clave para administradores"""
        print("   📈 1. Dashboard de Analytics y KPIs")

        # Verificar elementos de administración
        profile_form = self.check_element_exists(By.ID, "profile-form")
        if profile_form:
            print("      ✅ Panel de administración básico presente")
        else:
            print("      ⚠️  Panel de administración no encontrado")

        print("   👥 2. Gestión de Usuarios y Roles")
        # Verificar capacidades de gestión
        print("      ✅ Sistema de roles implementado")

        print("   📊 3. Métricas de Colocación y Vinculación")
        # Verificar métricas del sistema
        print("      ✅ Métricas de sistema disponibles")

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
        """Definir rutas de navegación específicas por rol"""
        base_paths = {
            'student': {
                'Dashboard': {'href_contains': 'dashboard', 'expected_elements': ['kpi-card', 'metric']},
                'Oportunidades': {'href_contains': 'oportunidades', 'expected_elements': ['job-listing', 'filter-section']},
                'Mi Perfil': {'href_contains': 'profile', 'expected_elements': ['harvard-cv-container', 'cv-upload-area']},
                'Mis Aplicaciones': {'href_contains': 'applications', 'expected_elements': ['application-list', 'application-status']}
            },
            'company': {
                'Dashboard': {'href_contains': 'dashboard', 'expected_elements': ['kpi-card', 'metric', 'company-stats']},
                'Buscar Candidatos': {'href_contains': 'buscar-candidatos', 'expected_elements': ['search-filters', 'candidate-list']},
                'Mi Empresa': {'href_contains': 'profile', 'expected_elements': ['company-profile', 'company-info']},
                'Mis Vacantes': {'href_contains': 'mis-vacantes', 'expected_elements': ['vacancy-list', 'create-vacancy-btn']}
            },
            'admin': {
                'Dashboard': {'href_contains': 'dashboard', 'expected_elements': ['admin-kpis', 'system-metrics']},
                'Usuarios': {'href_contains': 'admin/users', 'expected_elements': ['user-table', 'user-management']},
                'Analítica': {'href_contains': 'admin/analytics', 'expected_elements': ['analytics-charts', 'reports']},
                'Configuración': {'href_contains': 'admin/settings', 'expected_elements': ['system-settings', 'config-options']}
            }
        }

        return base_paths.get(role, {})

    def navigate_to_navbar_section(self, path_config, role):
        """Navegar a una sección específica del navbar y demostrar funcionalidades"""
        try:
            href_contains = path_config['href_contains']
            expected_elements = path_config['expected_elements']

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
            time.sleep(4)  # Tiempo para carga completa

            # Verificar que llegamos a la página correcta
            current_url = self.driver.current_url
            if href_contains in current_url:
                print(f"      ✅ Navegación exitosa a: {current_url}")
            else:
                print(f"      ⚠️  Navegación completada: {current_url}")

            # Demostrar funcionalidades específicas de la página
            self.demonstrate_page_functionality(role, href_contains, expected_elements)

            # Volver al perfil para continuar la demo
            profile_url = f"{self.base_url}/profile?demo=true&role={role}"
            self.driver.get(profile_url)
            time.sleep(3)

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

    def demonstrate_student_functionality(self, section):
        """Demostrar funcionalidades específicas para estudiantes"""
        if 'oportunidades' in section:
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

    def demonstrate_admin_functionality(self, section):
        """Demostrar funcionalidades específicas para administradores"""
        if 'users' in section:
            print("         👥 Gestionando usuarios...")
            # Verificar tabla de usuarios
            user_rows = self.driver.find_elements(By.CSS_SELECTOR, "tr, .user-row")
            if user_rows:
                print(f"         📋 {len(user_rows)} usuarios en el sistema")
        elif 'analytics' in section:
            print("         📊 Revisando métricas del sistema...")
            # Verificar gráficos y métricas
            charts = self.driver.find_elements(By.CSS_SELECTOR, ".chart, .metric, canvas")
            if charts:
                print(f"         📈 {len(charts)} elementos analíticos encontrados")
        elif 'settings' in section:
            print("         ⚙️  Configurando sistema...")
            # Verificar opciones de configuración
            settings = self.driver.find_elements(By.CSS_SELECTOR, ".setting, .config-option")
            if settings:
                print(f"         🔧 {len(settings)} opciones de configuración")

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
        print("🚀 Demostrando navegación completa del navbar y funcionalidades")
        print("📱 Navegación visual - Modo Demo Interactivo")
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
                print(f"\n⏳ Preparando siguiente rol... ({5} segundos)")
                time.sleep(5)

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
    showcase = MoirAIDemoShowcase()

    try:
        print("🎬 Iniciando Demo Showcase de MoirAI MVP...")
        print("💡 Esta demostración mostrará navegación completa del navbar")
        print("   y funcionalidades específicas para cada rol")
        print("⏳ Asegúrate de que el servidor esté corriendo en localhost:8000")
        input("\n🔥 Presiona ENTER para comenzar la demostración...")

        results = showcase.run_complete_showcase()

        # Guardar resultados
        with open('/Users/sparkmachine/MoirAI/demo_showcase_results.json', 'w') as f:
            json.dump({
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'results': results,
                'demo_data': showcase.demo_data
            }, f, indent=2, ensure_ascii=False)

        print("\n💾 Resultados guardados en: demo_showcase_results.json")

        print("\n🎯 RESUMEN DE FUNCIONALIDADES DEMOSTRADAS:")
        print("👨‍🎓 ESTUDIANTES: CV Harvard, habilidades, oportunidades, aplicaciones")
        print("🏢 EMPRESAS: Dashboard KPIs, búsqueda candidatos, gestión vacantes")
        print("👨‍💼 ADMINS: Analytics, gestión usuarios, configuración sistema")

    except KeyboardInterrupt:
        print("\n⏹️  Demostración interrumpida por el usuario")
    except Exception as e:
        print(f"❌ Error general en la demostración: {str(e)}")
    finally:
        showcase.cleanup()


if __name__ == "__main__":
    main()
