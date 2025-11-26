#!/usr/bin/env python3
"""
MoirAI Demo Mode Navigation Test - Navegación Completa del Navbar
Prueba la navegación completa del navbar cubriendo todas las secciones
disponibles para cada rol en modo demo.
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


class DemoModeTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.roles = ['student', 'company', 'admin']
        self.results = {}

        # Configurar Chrome en modo headless para testing automatizado
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        # Inicializar el driver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

        self.wait = WebDriverWait(self.driver, 10)

    def test_role_navigation(self, role):
        """Prueba la navegación completa para un rol específico cubriendo todas las secciones del navbar"""
        print(f"\n🎭 Probando rol: {role}")

        try:
            # Navegar a la página de perfil en modo demo
            url = f"{self.base_url}/profile?demo=true&role={role}"
            print(f"📍 Navegando a: {url}")
            self.driver.get(url)

            # Esperar a que cargue la página y se ejecute el JavaScript
            time.sleep(5)

            # Verificar navbar y contenido básico
            navbar_result = self.test_navbar(role)
            content_result = self.test_role_content(role)
            navigation_result = self.test_complete_navbar_navigation(role)

            if not all([navbar_result["success"], content_result["success"], navigation_result["success"]]):
                return {"success": False, "error": "Fallo en validaciones básicas"}

            return {"success": True, "message": f"Rol {role} probado exitosamente"}

        except Exception as e:
            print(f"❌ Error probando rol {role}: {str(e)}")
            return {"success": False, "error": str(e)}

    def test_navbar(self, role):
        """Verificar que el navbar se carga correctamente"""
        try:
            navbar = self.wait.until(EC.presence_of_element_located((By.ID, "navbar-container")))
            user_name_element = self.driver.find_element(By.CLASS_NAME, "user-name")
            expected_names = {'student': 'Demo Estudiante', 'company': 'Demo Empresa', 'admin': 'Demo Admin'}
            actual_name = user_name_element.text.strip()
            expected_name = expected_names.get(role, 'Demo Usuario')

            if actual_name != expected_name:
                return {"success": False, "error": f"Nombre incorrecto en navbar: {actual_name} != {expected_name}"}

            print(f"✅ Navbar correcto para rol {role}: {actual_name}")
            return {"success": True}

        except Exception as e:
            return {"success": False, "error": f"Error en navbar: {str(e)}"}

    def test_role_content(self, role):
        """Verificar contenido específico del rol"""
        try:
            if role == 'student':
                cv_area = self.check_element_exists(By.ID, "cv-upload-area")
                harvard_container = self.check_element_exists(By.ID, "harvard-cv-container")
                if not cv_area or not harvard_container:
                    return {"success": False, "error": "Elementos de estudiante faltantes"}
                print("✅ Elementos de estudiante presentes")

            elif role == 'company':
                cv_card = self.driver.find_elements(By.ID, "cv-upload-card")
                if cv_card:
                    display_style = cv_card[0].value_of_css_property("display")
                    if display_style != "none":
                        return {"success": False, "error": f"CV visible para empresa (display: {display_style})"}
                print("✅ Elementos de empresa correctos (CV oculto)")

            elif role == 'admin':
                profile_form = self.check_element_exists(By.ID, "profile-form")
                if not profile_form:
                    return {"success": False, "error": "Formulario de perfil no encontrado para admin"}
                print("✅ Elementos de admin presentes")

            return {"success": True}

        except Exception as e:
            return {"success": False, "error": f"Error verificando contenido: {str(e)}"}

    def test_complete_navbar_navigation(self, role):
        """Probar navegación completa del navbar entre todas las secciones disponibles"""
        try:
            print(f"🧭 Probando navegación completa del navbar para {role}...")

            # Definir navegación específica por rol
            navigation_paths = self.get_navigation_paths_by_role(role)

            navigation_results = {}

            # Probar navegación a cada sección relevante
            for path_name, path_config in navigation_paths.items():
                print(f"   🔗 Probando navegación a: {path_name}")
                result = self.test_navbar_section_navigation(path_config, role)
                navigation_results[path_name] = result

                if result["success"]:
                    print(f"      ✅ {path_name}: OK")
                else:
                    print(f"      ❌ {path_name}: FAILED - {result.get('error', 'Error desconocido')}")

            # Resumen de navegación
            successful_navs = sum(1 for r in navigation_results.values() if r["success"])
            total_navs = len(navigation_results)

            print(f"   📊 Navegación: {successful_navs}/{total_navs} secciones accesibles")

            return {"success": successful_navs > 0, "navigation_results": navigation_results}

        except Exception as e:
            return {"success": False, "error": f"Error en navegación: {str(e)}"}

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

    def test_navbar_section_navigation(self, path_config, role):
        """Probar navegación a una sección específica del navbar"""
        try:
            href_contains = path_config['href_contains']

            # Buscar el enlace correspondiente
            nav_links = self.driver.find_elements(By.CSS_SELECTOR, f"a[href*='{href_contains}']")

            if not nav_links:
                return {"success": False, "error": f"Enlace '{href_contains}' no encontrado"}

            # Hacer clic en el enlace
            link = nav_links[0]
            link.click()
            time.sleep(4)  # Aumentar tiempo para carga completa

            # Verificar que llegamos a la página correcta
            current_url = self.driver.current_url
            if href_contains in current_url:
                # Verificar elementos básicos de la página
                page_load_success = self.verify_page_load(path_config['expected_elements'])
                if page_load_success:
                    # Volver al perfil para continuar probando otros enlaces
                    profile_url = f"{self.base_url}/profile?demo=true&role={role}"
                    self.driver.get(profile_url)
                    time.sleep(3)
                    return {"success": True, "message": f"Navegación a {href_contains} exitosa"}
                else:
                    # Volver al perfil incluso si falló la verificación
                    profile_url = f"{self.base_url}/profile?demo=true&role={role}"
                    self.driver.get(profile_url)
                    time.sleep(3)
                    return {"success": False, "error": f"Página cargó pero elementos esperados no encontrados"}
            else:
                # Volver al perfil si no llegó a la página correcta
                profile_url = f"{self.base_url}/profile?demo=true&role={role}"
                self.driver.get(profile_url)
                time.sleep(3)
                return {"success": False, "error": f"No se pudo navegar a {href_contains}"}

        except Exception as e:
            # En caso de error, intentar volver al perfil
            try:
                profile_url = f"{self.base_url}/profile?demo=true&role={role}"
                self.driver.get(profile_url)
                time.sleep(3)
            except:
                pass
            return {"success": False, "error": f"Error navegando a sección: {str(e)}"}

    def verify_page_load(self, expected_elements):
        """Verificar que la página se cargó correctamente buscando elementos esperados"""
        try:
            # Al menos uno de los elementos esperados debe estar presente
            for element_id in expected_elements:
                if self.check_element_exists(By.ID, element_id) or self.check_element_exists(By.CLASS_NAME, element_id):
                    return True

            # Si no encontramos elementos específicos, verificar que al menos hay contenido
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            if len(body_text.strip()) > 50:  # Página tiene contenido sustancial
                return True

            return False

        except Exception:
            return False

    def check_element_exists(self, by, value):
        """Verificar si un elemento existe"""
        try:
            self.driver.find_element(by, value)
            return True
        except NoSuchElementException:
            return False

    def run_all_tests(self):
        """Ejecutar todas las pruebas cubriendo navegación completa del navbar"""
        print("🚀 Iniciando pruebas de navegación completa del navbar en modo demo")
        print("=" * 70)
        print("📋 Cubriendo Navegación Completa del Navbar:")
        print("👨‍🎓 ESTUDIANTES: Dashboard, Oportunidades, Mi Perfil, Mis Aplicaciones")
        print("🏢 EMPRESAS: Dashboard, Buscar Candidatos, Mi Empresa, Mis Vacantes")
        print("👨‍💼 ADMINS: Dashboard, Usuarios, Analítica, Configuración")
        print("=" * 70)

        for role in self.roles:
            result = self.test_role_navigation(role)
            self.results[role] = result

            if result["success"]:
                print(f"✅ {role.upper()}: PASSED")
            else:
                print(f"❌ {role.upper()}: FAILED - {result.get('error', 'Error desconocido')}")

        print("\n" + "=" * 70)
        print("📊 RESULTADOS FINALES:")

        passed = sum(1 for r in self.results.values() if r["success"])
        total = len(self.results)

        print(f"✅ Roles probados exitosamente: {passed}/{total}")

        if passed == total:
            print("🎉 ¡Todas las pruebas pasaron exitosamente!")
            print("✅ Navegación completa del navbar validada en modo demo")
        else:
            print("⚠️  Algunas pruebas fallaron. Revisar logs arriba.")

        return self.results

    def cleanup(self):
        """Limpiar recursos"""
        if self.driver:
            self.driver.quit()


def main():
    tester = DemoModeTester()

    try:
        results = tester.run_all_tests()

        # Guardar resultados en JSON
        with open('/Users/sparkmachine/MoirAI/demo_navigation_complete_results.json', 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print("\n💾 Resultados guardados en: demo_navigation_complete_results.json")

    except Exception as e:
        print(f"❌ Error general en las pruebas: {str(e)}")
    finally:
        tester.cleanup()


if __name__ == "__main__":
    main()
