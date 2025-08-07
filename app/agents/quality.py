from app.agents.base import BaseAgent
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)

class QualityAgent(BaseAgent):
    """
    Quality Agent - Ensures code quality and testing
    """
    
    def __init__(self):
        super().__init__("quality", "quality_assurance")
        
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type", "review_code")
        
        if task_type == "review_code":
            return await self._review_code(task)
        elif task_type == "generate_tests":
            return await self._generate_tests(task)
        elif task_type == "security_audit":
            return await self._security_audit(task)
        elif task_type == "performance_review":
            return await self._performance_review(task)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _review_code(self, task: Dict) -> Dict:
        code_files = task.get("code_files", {})
        
        reviews = {}
        for file_path, code in code_files.items():
            reviews[file_path] = await self._review_single_file(file_path, code)
        
        overall_quality = await self._calculate_overall_quality(reviews)
        
        return {
            "file_reviews": reviews,
            "overall_quality_score": overall_quality,
            "summary": await self._generate_review_summary(reviews),
            "recommendations": await self._generate_recommendations(reviews)
        }
    
    async def _review_single_file(self, file_path: str, code: str) -> Dict:
        prompt = f"""
        Review this code file for quality:
        
        File: {file_path}
        Code:
        {code}
        
        Check for:
        1. Code style and formatting
        2. Best practices
        3. Potential bugs
        4. Security issues
        5. Performance concerns
        6. Documentation
        7. Test coverage needs
        
        Provide detailed feedback.
        """
        
        review = await self.groq_service.complete(prompt)
        
        return {
            "review": review,
            "issues": await self._extract_issues(review),
            "score": await self._calculate_file_score(review)
        }
    
    async def _generate_tests(self, task: Dict) -> Dict:
        component = task.get("component", {})
        framework = task.get("framework", "pytest")
        
        test_files = {}
        
        if "backend" in component:
            test_files.update(await self._generate_backend_tests(component["backend"], framework))
        
        if "frontend" in component:
            test_files.update(await self._generate_frontend_tests(component["frontend"]))
        
        test_files["test_config.py"] = await self._generate_test_config(framework)
        
        test_files["conftest.py"] = await self._generate_pytest_fixtures()
        
        return {
            "test_files": test_files,
            "coverage_config": await self._generate_coverage_config(),
            "test_documentation": await self._generate_test_documentation(test_files)
        }
    
    async def _generate_backend_tests(self, backend: Dict, framework: str) -> Dict[str, str]:
        tests = {}
        
        for endpoint in backend.get("endpoints", []):
            test_name = f"test_{endpoint['name']}.py"
            tests[f"tests/{test_name}"] = await self._generate_endpoint_test(endpoint, framework)
        
        tests["tests/test_models.py"] = await self._generate_model_tests(backend.get("models", []))
        
        tests["tests/test_services.py"] = await self._generate_service_tests(backend.get("services", []))
        
        tests["tests/test_integration.py"] = await self._generate_integration_tests(backend)
        
        return tests
    
    async def _generate_endpoint_test(self, endpoint: Dict, framework: str) -> str:
        return f"""import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class Test{endpoint.get('name', 'Endpoint').title()}:
    
    def test_get_{endpoint.get('name', 'endpoint')}(self):
        response = client.get("/{endpoint.get('path', '')}")
        assert response.status_code == 200
        assert "data" in response.json()
    
    def test_post_{endpoint.get('name', 'endpoint')}(self):
        data = {{"test": "data"}}
        response = client.post("/{endpoint.get('path', '')}", json=data)
        assert response.status_code == 201
    
    def test_unauthorized_access(self):
        response = client.get("/{endpoint.get('path', '')}", headers={{"Authorization": "Bearer invalid"}})
        assert response.status_code == 401
    
    @pytest.mark.parametrize("invalid_data", [
        {{}},
        {{"invalid": "field"}},
        None
    ])
    def test_invalid_input(self, invalid_data):
        response = client.post("/{endpoint.get('path', '')}", json=invalid_data)
        assert response.status_code == 422
"""
    
    async def _generate_model_tests(self, models: List[Dict]) -> str:
        return """import pytest
from app.models import *

class TestModels:
    
    def test_model_creation(self):
        # Test model instantiation
        pass
    
    def test_model_validation(self):
        # Test field validation
        pass
    
    def test_model_relationships(self):
        # Test database relationships
        pass
    
    def test_model_methods(self):
        # Test custom model methods
        pass
"""
    
    async def _generate_service_tests(self, services: List[Dict]) -> str:
        return """import pytest
from unittest.mock import Mock, patch
from app.services import *

class TestServices:
    
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    async def test_service_logic(self, mock_db):
        # Test business logic
        pass
    
    async def test_error_handling(self, mock_db):
        # Test error scenarios
        pass
    
    async def test_data_transformation(self):
        # Test data processing
        pass
"""
    
    async def _generate_integration_tests(self, backend: Dict) -> str:
        return """import pytest
import asyncio
from app.main import app
from app.db.session import engine

class TestIntegration:
    
    @pytest.fixture(scope="class")
    async def setup_database(self):
        # Setup test database
        yield
        # Cleanup
    
    async def test_full_workflow(self, setup_database):
        # Test complete user workflow
        pass
    
    async def test_concurrent_operations(self):
        # Test concurrent requests
        pass
    
    async def test_transaction_rollback(self):
        # Test transaction handling
        pass
"""
    
    async def _generate_frontend_tests(self, frontend: Dict) -> Dict[str, str]:
        framework = frontend.get("framework", "react")
        
        tests = {}
        
        if framework == "react":
            tests["tests/App.test.jsx"] = """import { render, screen } from '@testing-library/react';
import App from '../src/App';

describe('App Component', () => {
    test('renders without crashing', () => {
        render(<App />);
        expect(screen.getByRole('main')).toBeInTheDocument();
    });
    
    test('navigation works correctly', () => {
        // Test routing
    });
});
"""
            
            tests["tests/components.test.jsx"] = """import { render, fireEvent } from '@testing-library/react';
import { Button, Form, List } from '../src/components';

describe('Components', () => {
    test('Button handles click events', () => {
        const handleClick = jest.fn();
        const { getByRole } = render(<Button onClick={handleClick}>Click me</Button>);
        fireEvent.click(getByRole('button'));
        expect(handleClick).toHaveBeenCalledTimes(1);
    });
});
"""
        
        tests["tests/e2e/app.spec.js"] = """describe('E2E Tests', () => {
    beforeEach(() => {
        cy.visit('http://localhost:3000');
    });
    
    it('completes user registration flow', () => {
        cy.get('[data-testid="register-button"]').click();
        cy.get('input[name="email"]').type('test@example.com');
        cy.get('input[name="password"]').type('securePassword123');
        cy.get('button[type="submit"]').click();
        cy.url().should('include', '/dashboard');
    });
});
"""
        
        return tests
    
    async def _generate_test_config(self, framework: str) -> str:
        if framework == "pytest":
            return """import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database configuration
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")

@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(TEST_DATABASE_URL)
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def test_session(test_engine):
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()
"""
        return ""
    
    async def _generate_pytest_fixtures(self) -> str:
        return """import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}

@pytest.fixture
def sample_data():
    return {
        "name": "Test Item",
        "description": "Test Description",
        "price": 99.99
    }
"""
    
    async def _generate_coverage_config(self) -> Dict[str, str]:
        return {
            ".coveragerc": """[run]
source = app
omit = 
    */tests/*
    */migrations/*
    */__pycache__/*
    */venv/*

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = htmlcov
""",
            "jest.config.js": """module.exports = {
    collectCoverageFrom: [
        'src/**/*.{js,jsx,ts,tsx}',
        '!src/**/*.d.ts',
        '!src/index.js',
        '!src/serviceWorker.js',
    ],
    coverageThreshold: {
        global: {
            branches: 70,
            functions: 70,
            lines: 70,
            statements: 70,
        },
    },
};
"""
        }
    
    async def _generate_test_documentation(self, test_files: Dict) -> str:
        return """# Test Documentation

## Running Tests

### Backend Tests
```bash
pytest tests/ -v --cov=app --cov-report=html
```

### Frontend Tests
```bash
npm test
npm run test:coverage
```

### E2E Tests
```bash
npm run cypress:open
```

## Test Structure
- Unit tests for all services and models
- Integration tests for API endpoints
- E2E tests for critical user flows

## Coverage Requirements
- Minimum 80% code coverage
- All critical paths must be tested
- Security-related code must have 100% coverage
"""
    
    async def _security_audit(self, task: Dict) -> Dict:
        code = task.get("code", {})
        
        vulnerabilities = await self._scan_for_vulnerabilities(code)
        
        return {
            "vulnerabilities": vulnerabilities,
            "security_score": await self._calculate_security_score(vulnerabilities),
            "recommendations": await self._generate_security_recommendations(vulnerabilities),
            "compliance_check": await self._check_compliance(code)
        }
    
    async def _scan_for_vulnerabilities(self, code: Dict) -> List[Dict]:
        vulnerabilities = []
        
        for file_path, content in code.items():
            prompt = f"""
            Scan this code for security vulnerabilities:
            
            {content}
            
            Check for:
            1. SQL injection
            2. XSS vulnerabilities
            3. Insecure authentication
            4. Exposed secrets
            5. CSRF vulnerabilities
            6. Insecure dependencies
            """
            
            scan_result = await self.groq_service.complete(prompt)
            
            if "vulnerability" in scan_result.lower():
                vulnerabilities.append({
                    "file": file_path,
                    "issues": scan_result
                })
        
        return vulnerabilities
    
    async def _calculate_security_score(self, vulnerabilities: List[Dict]) -> int:
        if not vulnerabilities:
            return 100
        
        score = 100 - (len(vulnerabilities) * 10)
        return max(0, score)
    
    async def _generate_security_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        recommendations = [
            "Implement input validation on all user inputs",
            "Use parameterized queries to prevent SQL injection",
            "Enable CORS with specific origins only",
            "Implement rate limiting on all endpoints",
            "Use environment variables for sensitive configuration",
            "Regularly update dependencies to patch vulnerabilities"
        ]
        
        return recommendations
    
    async def _check_compliance(self, code: Dict) -> Dict:
        return {
            "gdpr": True,
            "pci_dss": False,
            "hipaa": False,
            "sox": False
        }
    
    async def _performance_review(self, task: Dict) -> Dict:
        code = task.get("code", {})
        
        return {
            "performance_issues": await self._identify_performance_issues(code),
            "optimization_suggestions": await self._generate_optimizations(code),
            "benchmarks": await self._generate_benchmarks(code)
        }
    
    async def _identify_performance_issues(self, code: Dict) -> List[Dict]:
        issues = []
        
        for file_path, content in code.items():
            if "SELECT * FROM" in content:
                issues.append({
                    "file": file_path,
                    "issue": "Avoid SELECT * queries",
                    "severity": "medium"
                })
            
            if "for" in content and "for" in content[content.index("for")+10:]:
                issues.append({
                    "file": file_path,
                    "issue": "Nested loops detected",
                    "severity": "high"
                })
        
        return issues
    
    async def _generate_optimizations(self, code: Dict) -> List[str]:
        return [
            "Implement database query caching",
            "Use database indexes on frequently queried columns",
            "Implement pagination for large datasets",
            "Use async/await for I/O operations",
            "Implement connection pooling",
            "Use CDN for static assets"
        ]
    
    async def _generate_benchmarks(self, code: Dict) -> Dict:
        return {
            "api_response_time": "< 200ms",
            "database_query_time": "< 50ms",
            "page_load_time": "< 2s",
            "concurrent_users": "> 1000"
        }
    
    async def _extract_issues(self, review: str) -> List[Dict]:
        issues = []
        
        if "bug" in review.lower():
            issues.append({"type": "bug", "severity": "high"})
        if "security" in review.lower():
            issues.append({"type": "security", "severity": "critical"})
        if "performance" in review.lower():
            issues.append({"type": "performance", "severity": "medium"})
        
        return issues
    
    async def _calculate_file_score(self, review: str) -> int:
        score = 100
        
        if "bug" in review.lower():
            score -= 20
        if "security" in review.lower():
            score -= 30
        if "performance" in review.lower():
            score -= 10
        
        return max(0, score)
    
    async def _calculate_overall_quality(self, reviews: Dict) -> int:
        if not reviews:
            return 100
        
        scores = []
        for file_path, review in reviews.items():
            scores.append(review.get("score", 50))
        
        return sum(scores) // len(scores)
    
    async def _generate_review_summary(self, reviews: Dict) -> str:
        total_issues = 0
        critical_issues = 0
        
        for review in reviews.values():
            issues = review.get("issues", [])
            total_issues += len(issues)
            critical_issues += sum(1 for i in issues if i.get("severity") == "critical")
        
        return f"Found {total_issues} issues ({critical_issues} critical) across {len(reviews)} files"
    
    async def _generate_recommendations(self, reviews: Dict) -> List[str]:
        recommendations = []
        
        for review in reviews.values():
            if review.get("score", 100) < 70:
                recommendations.append("Refactor low-scoring files")
        
        recommendations.extend([
            "Add comprehensive test coverage",
            "Implement code linting",
            "Set up continuous integration",
            "Add code documentation"
        ])
        
        return recommendations