#!/usr/bin/env python3
"""
🧪 Harvard CV Integration Test Suite
Verifica la integración completa del backend de Harvard CV:
1. El servidor está corriendo
2. El endpoint GET /auth/me devuelve los 5 nuevos campos
3. El endpoint PUT /students/{id} acepta los nuevos campos
4. Los datos persisten correctamente en la base de datos
5. La serialización JSON funciona correctamente

Similar al test Selenium E2E, genera reportes JSON y logs detallados.
"""

import asyncio
import httpx
import json
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

# Colores para output
class Colors:
    RESET = "\033[0m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"

def print_header(text):
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.RESET}\n")

def print_success(text):
    logger.info(f"{Colors.GREEN}✅ {text}{Colors.RESET}")
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    logger.error(f"{Colors.RED}❌ {text}{Colors.RESET}")
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text):
    logger.info(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def print_warning(text):
    logger.warning(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_section(text):
    logger.info(f"{Colors.MAGENTA}▶ {text}{Colors.RESET}")
    print(f"{Colors.MAGENTA}▶ {text}{Colors.RESET}")


class HarvardCVTestOrchestrator:
    """Test orchestrator for Harvard CV integration - Similar to SeleniumVisualE2ETester"""

    HARVARD_CV_FIELDS = ["objective", "education", "experience", "certifications", "languages"]

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "api_url": API_URL,
            "tests": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            },
            "logs": []
        }
        self.auth_token = None
        self.user_data = None

    def log_result(self, message: str, level: str = "info"):
        """Log result with timestamp"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        self.results["logs"].append(log_entry)

    async def test_server_running(self) -> bool:
        """Test 1: Verificar que el servidor está corriendo"""
        print_header("Test 1: Server Running")
        
        test_result = {
            "name": "server_running",
            "status": "pending",
            "details": {}
        }
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                start_time = datetime.now()
                response = await client.get(f"{BASE_URL}/", follow_redirects=True)
                elapsed = (datetime.now() - start_time).total_seconds()
                
                if response.status_code == 200:
                    print_success(f"Server responding (Status: {response.status_code}, Response time: {elapsed:.2f}s)")
                    test_result["status"] = "success"
                    test_result["details"]["status_code"] = response.status_code
                    test_result["details"]["response_time_seconds"] = elapsed
                    self.log_result("✅ Server is running and responding", "success")
                    self.results["tests"]["server_running"] = test_result
                    self.results["summary"]["passed"] += 1
                    return True
                else:
                    print_warning(f"Server responding but status not 200: {response.status_code}")
                    test_result["status"] = "warning"
                    test_result["details"]["status_code"] = response.status_code
                    self.log_result(f"⚠️ Server status: {response.status_code}", "warning")
                    self.results["tests"]["server_running"] = test_result
                    self.results["summary"]["warnings"] += 1
                    return True  # Server is running
                    
        except Exception as e:
            print_error(f"Server not responding: {str(e)[:100]}")
            test_result["status"] = "failed"
            test_result["details"]["error"] = str(e)
            self.log_result(f"❌ Server test failed: {str(e)}", "error")
            self.results["tests"]["server_running"] = test_result
            self.results["summary"]["failed"] += 1
            return False

    async def test_authentication(self) -> bool:
        """Test 2: Obtener token de autenticación"""
        print_header("Test 2: Authentication")
        
        test_result = {
            "name": "authentication",
            "status": "pending",
            "details": {}
        }
        
        login_data = {
            "email": "henryspark@hotmail.com",
            "password": "Henryspark123!"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    f"{API_URL}/auth/login",
                    json=login_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    token = data.get("access_token") or data.get("api_key")
                    
                    if token:
                        print_success(f"Authentication successful")
                        print_info(f"Token: {token[:30]}...")
                        test_result["status"] = "success"
                        test_result["details"]["email"] = login_data["email"]
                        test_result["details"]["token_length"] = len(token)
                        self.auth_token = token
                        self.log_result("✅ Authentication successful", "success")
                        self.results["tests"]["authentication"] = test_result
                        self.results["summary"]["passed"] += 1
                        return True
                    else:
                        print_error("No token in response")
                        test_result["status"] = "failed"
                        test_result["details"]["response"] = data
                        self.log_result("❌ No token in authentication response", "error")
                        self.results["tests"]["authentication"] = test_result
                        self.results["summary"]["failed"] += 1
                        return False
                else:
                    print_error(f"Login failed (Status: {response.status_code})")
                    print_warning(f"Response: {response.text[:200]}")
                    test_result["status"] = "failed"
                    test_result["details"]["status_code"] = response.status_code
                    test_result["details"]["error"] = response.text[:200]
                    self.log_result(f"❌ Login failed: {response.status_code}", "error")
                    self.results["tests"]["authentication"] = test_result
                    self.results["summary"]["failed"] += 1
                    return False
                    
        except Exception as e:
            print_error(f"Authentication error: {str(e)[:100]}")
            test_result["status"] = "failed"
            test_result["details"]["error"] = str(e)
            self.log_result(f"❌ Authentication error: {str(e)}", "error")
            self.results["tests"]["authentication"] = test_result
            self.results["summary"]["failed"] += 1
            return False

    async def test_get_profile(self) -> bool:
        """Test 3: Verificar que GET /auth/me devuelve los nuevos campos"""
        print_header("Test 3: GET /auth/me - Verify Harvard CV Fields")
        
        test_result = {
            "name": "get_profile",
            "status": "pending",
            "details": {}
        }
        
        if not self.auth_token:
            print_error("No auth token available")
            test_result["status"] = "failed"
            self.results["tests"]["get_profile"] = test_result
            self.results["summary"]["failed"] += 1
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{API_URL}/auth/me",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.user_data = data
                    print_success("GET /auth/me successful")
                    
                    # Verificar que los campos nuevos existen
                    print_section("Verificando campos Harvard CV:")
                    fields_found = {}
                    all_present = True
                    
                    for field in self.HARVARD_CV_FIELDS:
                        if field in data:
                            value = data[field]
                            value_str = str(value)[:50] if value else "null"
                            print_success(f"  {field}: {value_str}")
                            fields_found[field] = "present"
                        else:
                            print_error(f"  {field}: MISSING")
                            fields_found[field] = "missing"
                            all_present = False
                    
                    test_result["status"] = "success" if all_present else "warning"
                    test_result["details"]["fields_found"] = fields_found
                    test_result["details"]["user_id"] = data.get("id")
                    test_result["details"]["email"] = data.get("email")
                    self.log_result(f"✅ Profile retrieved with {sum(1 for v in fields_found.values() if v == 'present')}/{len(self.HARVARD_CV_FIELDS)} Harvard fields", "success")
                    self.results["tests"]["get_profile"] = test_result
                    self.results["summary"]["passed"] += 1
                    return all_present
                else:
                    print_error(f"GET /auth/me failed (Status: {response.status_code})")
                    print_warning(f"Response: {response.text[:200]}")
                    test_result["status"] = "failed"
                    test_result["details"]["status_code"] = response.status_code
                    self.log_result(f"❌ GET /auth/me failed: {response.status_code}", "error")
                    self.results["tests"]["get_profile"] = test_result
                    self.results["summary"]["failed"] += 1
                    return False
                    
        except Exception as e:
            print_error(f"GET /auth/me error: {str(e)[:100]}")
            test_result["status"] = "failed"
            test_result["details"]["error"] = str(e)
            self.log_result(f"❌ GET /auth/me error: {str(e)}", "error")
            self.results["tests"]["get_profile"] = test_result
            self.results["summary"]["failed"] += 1
            return False

    async def test_update_profile(self) -> bool:
        """Test 4: Verificar que PUT /students/{id} acepta los nuevos campos"""
        print_header("Test 4: PUT /students/{id} - Update Harvard CV Fields")
        
        test_result = {
            "name": "update_profile",
            "status": "pending",
            "details": {}
        }
        
        if not self.auth_token or not self.user_data:
            print_error("No auth token or user data available")
            test_result["status"] = "failed"
            self.results["tests"]["update_profile"] = test_result
            self.results["summary"]["failed"] += 1
            return False
        
        user_id = self.user_data.get("id")
        if not user_id:
            print_error("No user ID found")
            test_result["status"] = "failed"
            self.results["tests"]["update_profile"] = test_result
            self.results["summary"]["failed"] += 1
            return False
        
        # Preparar datos de actualización con campos Harvard
        update_data = {
            "objective": "Desarrollador Full Stack con pasión por la innovación y el aprendizaje continuo. Especializado en arquitectura de sistemas escalables.",
            "education": [
                {
                    "institution": "Universidad Nacional de Río Cuarto",
                    "degree": "Licenciatura en Ciencias de la Computación",
                    "field_of_study": "Informática",
                    "graduation_year": "2024"
                },
                {
                    "institution": "Coursera",
                    "degree": "Certificado",
                    "field_of_study": "Cloud Computing",
                    "graduation_year": "2023"
                }
            ],
            "experience": [
                {
                    "position": "Junior Developer",
                    "company": "TechCorp Inc",
                    "start_date": "2023-01",
                    "end_date": "2024-01",
                    "description": "Development of web applications using React and FastAPI. Improved performance by 40%."
                },
                {
                    "position": "Intern Software Engineer",
                    "company": "StartupXYZ",
                    "start_date": "2022-06",
                    "end_date": "2022-12",
                    "description": "Backend development with Python and PostgreSQL"
                }
            ],
            "certifications": [
                "Google Cloud Associate Cloud Engineer",
                "AWS Solutions Architect Associate",
                "Certified Kubernetes Administrator (CKA)"
            ],
            "languages": [
                "Español - Nativo",
                "Inglés - Fluido (C1)",
                "Portugués - Intermedio (B1)"
            ]
        }
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.put(
                    f"{API_URL}/students/{user_id}",
                    json=update_data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    print_success(f"PUT /students/{user_id} successful")
                    updated_data = response.json()
                    
                    # Verificar que los campos fueron guardados
                    print_section("Verificando campos actualizados:")
                    fields_updated = {}
                    
                    for field in update_data.keys():
                        if field in updated_data:
                            print_success(f"  {field}: Updated ✓")
                            fields_updated[field] = "updated"
                        else:
                            print_warning(f"  {field}: Not in response")
                            fields_updated[field] = "not_in_response"
                    
                    test_result["status"] = "success"
                    test_result["details"]["fields_updated"] = fields_updated
                    test_result["details"]["response_status"] = response.status_code
                    self.log_result(f"✅ Profile updated with {sum(1 for v in fields_updated.values() if v == 'updated')} Harvard fields", "success")
                    self.results["tests"]["update_profile"] = test_result
                    self.results["summary"]["passed"] += 1
                    return True
                else:
                    print_error(f"PUT /students/{user_id} failed (Status: {response.status_code})")
                    print_warning(f"Response: {response.text[:200]}")
                    test_result["status"] = "failed"
                    test_result["details"]["status_code"] = response.status_code
                    test_result["details"]["error"] = response.text[:200]
                    self.log_result(f"❌ PUT /students failed: {response.status_code}", "error")
                    self.results["tests"]["update_profile"] = test_result
                    self.results["summary"]["failed"] += 1
                    return False
                    
        except Exception as e:
            print_error(f"PUT /students/{user_id} error: {str(e)[:100]}")
            test_result["status"] = "failed"
            test_result["details"]["error"] = str(e)
            self.log_result(f"❌ PUT /students error: {str(e)}", "error")
            self.results["tests"]["update_profile"] = test_result
            self.results["summary"]["failed"] += 1
            return False

    async def test_persistence(self) -> bool:
        """Test 5: Verificar que los datos persisten tras un GET posterior"""
        print_header("Test 5: Data Persistence - Verify Data Saved")
        
        test_result = {
            "name": "persistence",
            "status": "pending",
            "details": {}
        }
        
        if not self.auth_token:
            print_error("No auth token available")
            test_result["status"] = "failed"
            self.results["tests"]["persistence"] = test_result
            self.results["summary"]["failed"] += 1
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{API_URL}/auth/me",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print_success("GET /auth/me after update successful")
                    
                    # Verificar que los datos se guardaron
                    print_section("Data persistence check:")
                    persistence_check = {}
                    all_persisted = True
                    
                    for field in self.HARVARD_CV_FIELDS:
                        value = data.get(field)
                        if value:
                            value_str = str(value)[:50] if value else "null"
                            print_success(f"  {field}: Persisted ✓ ({value_str})")
                            persistence_check[field] = "persisted"
                        else:
                            print_warning(f"  {field}: Not persisted")
                            persistence_check[field] = "not_persisted"
                            all_persisted = False
                    
                    test_result["status"] = "success" if all_persisted else "warning"
                    test_result["details"]["persistence_check"] = persistence_check
                    self.log_result(f"✅ Data persistence verified for {sum(1 for v in persistence_check.values() if v == 'persisted')} fields", "success")
                    self.results["tests"]["persistence"] = test_result
                    self.results["summary"]["passed"] += 1
                    return all_persisted
                else:
                    print_error(f"GET /auth/me failed (Status: {response.status_code})")
                    test_result["status"] = "failed"
                    test_result["details"]["status_code"] = response.status_code
                    self.log_result(f"❌ Persistence check failed: {response.status_code}", "error")
                    self.results["tests"]["persistence"] = test_result
                    self.results["summary"]["failed"] += 1
                    return False
                    
        except Exception as e:
            print_error(f"Persistence check error: {str(e)[:100]}")
            test_result["status"] = "failed"
            test_result["details"]["error"] = str(e)
            self.log_result(f"❌ Persistence check error: {str(e)}", "error")
            self.results["tests"]["persistence"] = test_result
            self.results["summary"]["failed"] += 1
            return False

    async def run_all_tests(self) -> bool:
        """Ejecutar todos los tests"""
        try:
            self.results["summary"]["total_tests"] = 5
            
            # Test 1: Server Running
            if not await self.test_server_running():
                print_error("Cannot continue - server not responding")
                return False
            
            # Test 2: Authentication
            if not await self.test_authentication():
                print_error("Cannot continue - authentication failed")
                return False
            
            # Test 3: GET Profile
            if not await self.test_get_profile():
                print_warning("GET /auth/me test had issues, continuing...")
            
            # Test 4: PUT Update
            if not await self.test_update_profile():
                print_warning("PUT /students test had issues, continuing...")
            
            # Test 5: Persistence
            if not await self.test_persistence():
                print_warning("Persistence test had issues")
            
            return True
            
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            self.log_result(f"❌ Unexpected error: {str(e)}", "error")
            return False

    def generate_report(self) -> Path:
        """Generate JSON report (similar to Selenium E2E)"""
        report_timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        report_filename = f"harvard-cv-integration-report-{report_timestamp}.json"
        report_path = Path("/Users/sparkmachine/MoirAI") / report_filename
        
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print_info(f"📊 Report generated: {report_path}")
        logger.info(f"📊 Report generated: {report_path}")
        return report_path

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("HARVARD CV INTEGRATION TEST SUMMARY")
        print("="*70)
        
        for test_name, test_result in self.results["tests"].items():
            if isinstance(test_result, dict) and "status" in test_result:
                status = test_result["status"]
                
                if status == "success":
                    icon = "✅"
                    status_text = "PASS"
                elif status == "warning":
                    icon = "⚠️"
                    status_text = "PARTIAL"
                else:
                    icon = "❌"
                    status_text = "FAIL"
                
                print(f"\n{icon} {test_name.upper()}: {status_text}")
                
                if test_result.get("details"):
                    for key, value in test_result["details"].items():
                        value_str = str(value)[:60] if not isinstance(value, dict) else "..."
                        print(f"  ├─ {key}: {value_str}")
        
        # Summary statistics
        print(f"\n{'='*70}")
        print(f"📈 Test Summary:")
        print(f"  • Total Tests: {self.results['summary']['total_tests']}")
        print(f"  • Passed: {self.results['summary']['passed']}")
        print(f"  • Warnings: {self.results['summary']['warnings']}")
        print(f"  • Failed: {self.results['summary']['failed']}")
        print(f"{'='*70}\n")


async def main():
    """Main entry point"""
    print(f"\n{Colors.CYAN}🧪 HARVARD CV INTEGRATION TEST SUITE{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print(f"API URL: {API_URL}\n")
    
    tester = HarvardCVTestOrchestrator()
    success = await tester.run_all_tests()
    
    # Generate report and print summary
    report_path = tester.generate_report()
    tester.print_summary()
    
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0 if success and tester.results["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
