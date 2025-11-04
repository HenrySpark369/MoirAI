"""
Tests for critical fixes in the MoirAI application
Testing database sync/async consistency, model fields, and API functionality
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.main import app
from app.core.database import get_session
from app.models import Student, Company


# Test database setup
@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with dependency override"""
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestDatabaseSyncFixes:
    """Test that database operations are properly synchronous"""
    
    def test_create_db_and_tables_is_sync(self):
        """Verify create_db_and_tables is a synchronous function"""
        from app.core.database import create_db_and_tables
        import inspect
        
        # Should not be a coroutine function
        assert not inspect.iscoroutinefunction(create_db_and_tables)
    
    def test_get_session_is_sync_generator(self):
        """Verify get_session is a synchronous generator"""
        from app.core.database import get_session
        import inspect
        
        # Should not be a coroutine function
        assert not inspect.iscoroutinefunction(get_session)
        # Should be a generator
        assert inspect.isgeneratorfunction(get_session)


class TestModelPasswordHashFields:
    """Test that Student and Company models have password_hash fields"""
    
    def test_student_has_password_hash_field(self, session: Session):
        """Verify Student model has password_hash field"""
        student = Student(
            name="Test Student",
            email="test@student.com",
            program="Computer Science",
            skills="[]",
            soft_skills="[]",
            projects="[]"
        )
        
        # Should not raise an error - password_hash should be optional
        assert hasattr(student, 'password_hash')
        assert student.password_hash is None
        
        # Should be able to set it
        student.password_hash = "hashed_password_123"
        assert student.password_hash == "hashed_password_123"
        
        # Should be able to save to database
        session.add(student)
        session.commit()
        session.refresh(student)
        
        assert student.id is not None
        assert student.password_hash == "hashed_password_123"
    
    def test_company_has_password_hash_field(self, session: Session):
        """Verify Company model has password_hash field"""
        company = Company(
            name="Test Company",
            email="test@company.com",
            industry="Technology",
            size="startup"
        )
        
        # Should not raise an error - password_hash should be optional
        assert hasattr(company, 'password_hash')
        assert company.password_hash is None
        
        # Should be able to set it
        company.password_hash = "hashed_password_456"
        assert company.password_hash == "hashed_password_456"
        
        # Should be able to save to database
        session.add(company)
        session.commit()
        session.refresh(company)
        
        assert company.id is not None
        assert company.password_hash == "hashed_password_456"
    
    def test_student_without_password_hash_works(self, session: Session):
        """Verify Student can be created without password_hash (backward compatibility)"""
        student = Student(
            name="Legacy Student",
            email="legacy@student.com",
            program="Engineering",
            skills="[]",
            soft_skills="[]",
            projects="[]"
        )
        
        # password_hash should default to None
        assert student.password_hash is None
        
        # Should save successfully without password_hash
        session.add(student)
        session.commit()
        session.refresh(student)
        
        assert student.id is not None
        assert student.password_hash is None


class TestHealthEndpoints:
    """Test that health and monitoring endpoints work correctly"""
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns correct response"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "operational"
    
    def test_health_endpoint(self, client: TestClient):
        """Test health endpoint returns correct response"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_info_endpoint(self, client: TestClient):
        """Test info endpoint returns correct response"""
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "features" in data
        assert isinstance(data["features"], list)
    
    def test_compliance_endpoint(self, client: TestClient):
        """Test compliance endpoint returns correct response"""
        response = client.get("/compliance")
        assert response.status_code == 200
        data = response.json()
        assert "privacy_by_design" in data
        assert "consent_required" in data
        assert data["consent_required"] is True


class TestValidationErrors:
    """Test that validation errors return correct HTTP status code"""
    
    def test_validation_error_returns_422(self, client: TestClient):
        """Test that validation errors return 422 status code"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "name": "",  # Too short
                "email": "invalid-email",  # Invalid email
                "role": "invalid_role"  # Invalid role
            }
        )
        
        # Should return 422 for validation errors
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "VALIDATION_ERROR"


class TestAuthEndpoints:
    """Test authentication endpoints work correctly"""
    
    def test_register_student_creates_api_key(self, client: TestClient):
        """Test that registering a student creates an API key"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "name": "John Doe",
                "email": "john@student.com",
                "role": "student",
                "program": "Computer Science"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Should return user info
        assert data["user_id"] is not None
        assert data["name"] == "John Doe"
        assert data["email"] == "john@student.com"
        assert data["role"] == "student"
        
        # Should return API key info
        assert "api_key" in data
        assert "key_id" in data
        assert "scopes" in data
        assert isinstance(data["scopes"], list)
        assert len(data["scopes"]) > 0
    
    def test_auth_me_endpoint_with_valid_key(self, client: TestClient):
        """Test /auth/me endpoint with valid API key"""
        # First register a user
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "name": "Jane Doe",
                "email": "jane@company.com",
                "role": "company",
                "industry": "Technology",
                "company_size": "startup",
                "location": "Mexico City"
            }
        )
        
        assert register_response.status_code == 201
        api_key = register_response.json()["api_key"]
        
        # Now use the API key
        me_response = client.get(
            "/api/v1/auth/me",
            headers={"X-API-Key": api_key}
        )
        
        assert me_response.status_code == 200
        data = me_response.json()
        assert data["email"] == "jane@company.com"
        assert data["role"] == "company"
        assert "permissions" in data
    
    def test_auth_me_endpoint_without_key_returns_401(self, client: TestClient):
        """Test /auth/me endpoint without API key returns 401"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
        data = response.json()
        # The error response uses our custom ErrorResponse schema
        assert "message" in data
        assert data["success"] is False


class TestAuthServiceSync:
    """Test that AuthService methods are synchronous"""
    
    def test_auth_service_get_current_user_is_sync(self):
        """Verify AuthService.get_current_user is synchronous"""
        from app.middleware.auth import AuthService
        import inspect
        
        # Should not be a coroutine function
        assert not inspect.iscoroutinefunction(AuthService.get_current_user)
    
    def test_auth_service_log_activity_is_sync(self):
        """Verify AuthService._log_activity is synchronous"""
        from app.middleware.auth import AuthService
        import inspect
        
        # Should not be a coroutine function
        assert not inspect.iscoroutinefunction(AuthService._log_activity)
