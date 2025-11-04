"""
Tests to ensure code quality compliance with Issue #8 requirements.
These tests prevent regression of the 6 critical issues identified.
"""
import pytest
import re
from pathlib import Path


class TestDatabaseAsyncSyncConsistency:
    """Issue 1: Verify database operations are consistently synchronous"""
    
    def test_database_uses_sync_engine(self):
        """Database should use synchronous create_engine, not AsyncEngine"""
        db_file = Path(__file__).parent.parent / "app" / "core" / "database.py"
        content = db_file.read_text()
        
        # Should use sync imports
        assert "from sqlmodel import create_engine" in content
        assert "from sqlmodel import Session" in content or "Session" in content
        
        # Should NOT use async
        assert "AsyncEngine" not in content
        assert "AsyncSession" not in content
        assert "async def create_db_and_tables" not in content
        assert "async def get_session" not in content
    
    def test_event_handlers_dont_mix_async_sync_incorrectly(self):
        """Startup/shutdown events should handle sync db calls properly"""
        main_file = Path(__file__).parent.parent / "app" / "main.py"
        content = main_file.read_text()
        
        # Event handlers can be async (FastAPI requirement)
        # but they should call sync database functions directly
        assert "async def startup_event" in content or "def startup_event" in content
        assert "create_db_and_tables()" in content  # Sync call is fine


class TestPasswordHashMigration:
    """Issue 2: Verify password_hash fields have defaults if they exist"""
    
    def test_student_model_password_hash_optional(self):
        """If Student has password_hash, it must be Optional with default"""
        models_file = Path(__file__).parent.parent / "app" / "models" / "__init__.py"
        content = models_file.read_text()
        
        # Find Student model
        student_match = re.search(r'class Student\(.*?\):(.*?)(?=class\s|\Z)', content, re.DOTALL)
        if student_match:
            model_content = student_match.group(1)
            if 'password_hash' in model_content.lower():
                # Must have default or Optional
                assert ('default=' in model_content or 'Optional' in model_content), \
                    "password_hash must be Optional or have a default value"
    
    def test_company_model_password_hash_optional(self):
        """If Company has password_hash, it must be Optional with default"""
        models_file = Path(__file__).parent.parent / "app" / "models" / "__init__.py"
        content = models_file.read_text()
        
        # Find Company model
        company_match = re.search(r'class Company\(.*?\):(.*?)(?=class\s|\Z)', content, re.DOTALL)
        if company_match:
            model_content = company_match.group(1)
            if 'password_hash' in model_content.lower():
                # Must have default or Optional
                assert ('default=' in model_content or 'Optional' in model_content), \
                    "password_hash must be Optional or have a default value"


class TestAuthEndpointCorrectness:
    """Issue 3: Verify auth endpoint imports and API response consistency"""
    
    def test_auth_service_imported(self):
        """AuthService must be imported in auth endpoint"""
        auth_file = Path(__file__).parent.parent / "app" / "api" / "endpoints" / "auth.py"
        content = auth_file.read_text()
        
        assert "from app.middleware.auth import AuthService" in content, \
            "AuthService must be imported from app.middleware.auth"
    
    def test_api_key_response_shape_consistent(self):
        """API key response should use consistent shape from schema"""
        # Verify schema defines ApiKeyCreatedResponse correctly
        schemas_file = Path(__file__).parent.parent / "app" / "schemas" / "__init__.py"
        content = schemas_file.read_text()
        
        # Should have ApiKeyCreatedResponse with api_key and key_info
        assert "class ApiKeyCreatedResponse" in content
        assert "api_key: str" in content
        assert "key_info: ApiKeyResponse" in content


class TestSecretsConfiguration:
    """Issue 4: Verify secrets come from environment variables"""
    
    def test_config_uses_pydantic_settings(self):
        """Configuration should use pydantic-settings for env vars"""
        config_file = Path(__file__).parent.parent / "app" / "core" / "config.py"
        content = config_file.read_text()
        
        assert "BaseSettings" in content, "Should use pydantic BaseSettings"
        assert "from pydantic_settings import BaseSettings" in content or \
               "from pydantic.settings import BaseSettings" in content
    
    def test_secret_key_not_hardcoded(self):
        """SECRET_KEY should not be hardcoded in config.py"""
        config_file = Path(__file__).parent.parent / "app" / "core" / "config.py"
        content = config_file.read_text()
        
        # Check SECRET_KEY uses Field() for environment loading
        secret_key_pattern = r'SECRET_KEY.*?Field\('
        assert re.search(secret_key_pattern, content, re.DOTALL), \
            "SECRET_KEY should use Field() to load from environment"
        
        # Should NOT have hardcoded values like SECRET_KEY = "some-secret-123"
        hardcoded_pattern = r'SECRET_KEY\s*[:=]\s*["\'][a-zA-Z0-9_\-]{20,}'
        assert not re.search(hardcoded_pattern, content), \
            "SECRET_KEY appears to be hardcoded"


class TestAPICompatibility:
    """Issue 5: Verify API routes maintain backward compatibility"""
    
    def test_api_prefix_maintains_compatibility(self):
        """API_V1_STR should be /api/v1 for backward compatibility"""
        config_file = Path(__file__).parent.parent / "app" / "core" / "config.py"
        content = content = config_file.read_text()
        
        # Extract API_V1_STR value (handles both old and new pydantic syntax)
        # New syntax: API_V1_STR: str = "/api/v1"
        # Old syntax: API_V1_STR = "/api/v1"
        api_match = re.search(r'API_V1_STR\s*:\s*str\s*=\s*["\']([^"\']+)["\']|API_V1_STR\s*=\s*["\']([^"\']+)["\']', content)
        assert api_match, "API_V1_STR should be defined"
        
        api_prefix = api_match.group(1) or api_match.group(2)
        # Should be /api/v1 or configurable via env
        assert api_prefix == "/api/v1" or "Field(" in content, \
            f"API prefix is '{api_prefix}' which may break compatibility. Should be '/api/v1' or configurable."
    
    def test_cors_configurable(self):
        """CORS origins should be configurable via environment"""
        config_file = Path(__file__).parent.parent / "app" / "core" / "config.py"
        content = config_file.read_text()
        
        assert "BACKEND_CORS_ORIGINS" in content, "CORS origins should be defined"
        # Should use List type (configurable)
        assert "List[str]" in content or "list[str]" in content


class TestHTTPStatusAndMonitoring:
    """Issue 6: Verify HTTP status codes and monitoring endpoints"""
    
    def test_validation_returns_422(self):
        """Validation errors should return 422 Unprocessable Entity"""
        main_file = Path(__file__).parent.parent / "app" / "main.py"
        content = main_file.read_text()
        
        assert "RequestValidationError" in content
        assert "status_code=422" in content or "status_code = 422" in content, \
            "Validation errors must return 422 status code"
    
    def test_health_endpoints_exist(self):
        """Critical monitoring endpoints should exist"""
        main_file = Path(__file__).parent.parent / "app" / "main.py"
        content = main_file.read_text()
        
        required_endpoints = [
            ("/", "root endpoint"),
            ("/health", "health check"),
            ("/info", "API info"),
            ("/compliance", "compliance info"),
        ]
        
        for endpoint, description in required_endpoints:
            assert f'"{endpoint}"' in content or f"'{endpoint}'" in content, \
                f"Missing {description} endpoint: {endpoint}"


class TestIntegration:
    """Integration tests to verify the system works end-to-end"""
    
    def test_app_imports_successfully(self):
        """Application should import without errors"""
        try:
            from app.main import app
            assert app is not None
        except Exception as e:
            pytest.fail(f"Failed to import app: {e}")
    
    def test_database_initialization(self):
        """Database should initialize without errors"""
        try:
            from app.core.database import create_db_and_tables
            create_db_and_tables()
        except Exception as e:
            pytest.fail(f"Failed to initialize database: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
