from app.agents.base import BaseAgent
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)

class BackendDeveloperAgent(BaseAgent):
    def __init__(self):
        super().__init__("backend_developer", "api_builder")
        self.supported_frameworks = ["fastapi", "flask", "django", "express"]
        
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type", "generate_backend")
        
        if task_type == "generate_backend":
            return await self._generate_backend(task)
        elif task_type == "generate_api":
            return await self._generate_api(task)
        elif task_type == "generate_services":
            return await self._generate_services(task)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _generate_backend(self, task: Dict) -> Dict:
        schema = task.get("database_schema", {})
        requirements = task.get("requirements", {})
        integrations = task.get("integrations", [])
        framework = task.get("framework", "fastapi")
        
        prompt = f"""
        Generate a complete {framework} backend application:
        
        Database Schema: {json.dumps(schema)}
        Requirements: {json.dumps(requirements)}
        Integrations: {json.dumps(integrations)}
        
        Generate:
        1. Project structure
        2. Database models
        3. API endpoints (CRUD + custom)
        4. Service layer
        5. Authentication system
        6. Integration connections
        7. Error handling
        8. Configuration
        
        Follow best practices for {framework}.
        """
        
        backend_design = await self.groq_service.complete(prompt)
        
        files = await self._generate_backend_files(
            backend_design, 
            schema, 
            requirements, 
            integrations, 
            framework
        )
        
        return {
            "framework": framework,
            "design": backend_design,
            "files": files,
            "dependencies": await self._extract_dependencies(backend_design, framework),
            "deployment_config": await self._generate_deployment_config(framework)
        }
    
    async def _generate_backend_files(
        self, 
        design: str, 
        schema: Dict, 
        requirements: Dict, 
        integrations: List,
        framework: str
    ) -> Dict[str, str]:
        
        files = {}
        
        if framework == "fastapi":
            files = await self._generate_fastapi_files(schema, requirements, integrations)
        elif framework == "flask":
            files = await self._generate_flask_files(schema, requirements, integrations)
        elif framework == "django":
            files = await self._generate_django_files(schema, requirements, integrations)
        
        return files
    
    async def _generate_fastapi_files(
        self, 
        schema: Dict, 
        requirements: Dict, 
        integrations: List
    ) -> Dict[str, str]:
        
        files = {}
        
        files["main.py"] = await self._generate_fastapi_main(requirements)
        
        files["config.py"] = await self._generate_config(requirements, integrations)
        
        for table in schema.get("tables", []):
            model_name = table["name"]
            files[f"models/{model_name}.py"] = await self._generate_model(table, "fastapi")
            files[f"routes/{model_name}.py"] = await self._generate_routes(table, "fastapi")
            files[f"services/{model_name}_service.py"] = await self._generate_service(table)
        
        files["auth/auth.py"] = await self._generate_auth_system("fastapi", requirements)
        
        for integration in integrations:
            integration_type = integration.get("type", "unknown")
            files[f"integrations/{integration_type}.py"] = await self._generate_integration(integration)
        
        files["requirements.txt"] = await self._generate_requirements("fastapi", integrations)
        
        return files
    
    async def _generate_fastapi_main(self, requirements: Dict) -> str:
        prompt = f"""
        Generate a FastAPI main.py file with:
        
        Requirements: {json.dumps(requirements)}
        
        Include:
        1. FastAPI app initialization
        2. CORS middleware
        3. Route registration
        4. Error handlers
        5. Startup/shutdown events
        6. API documentation setup
        """
        
        return await self.groq_service.complete(prompt)
    
    async def _generate_model(self, table: Dict, framework: str) -> str:
        prompt = f"""
        Generate a {framework} model for this table:
        
        {json.dumps(table)}
        
        Include:
        1. Field definitions
        2. Relationships
        3. Validators
        4. Methods
        5. Proper typing
        """
        
        return await self.groq_service.complete(prompt)
    
    async def _generate_routes(self, table: Dict, framework: str) -> str:
        prompt = f"""
        Generate {framework} API routes for this table:
        
        {json.dumps(table)}
        
        Include:
        1. CRUD endpoints
        2. Query parameters
        3. Request/response schemas
        4. Authentication decorators
        5. Error handling
        """
        
        return await self.groq_service.complete(prompt)
    
    async def _generate_service(self, table: Dict) -> str:
        prompt = f"""
        Generate a service layer for this table:
        
        {json.dumps(table)}
        
        Include:
        1. Business logic
        2. Database operations
        3. Validation
        4. Error handling
        5. Transaction management
        """
        
        return await self.groq_service.complete(prompt)
    
    async def _generate_auth_system(self, framework: str, requirements: Dict) -> str:
        prompt = f"""
        Generate an authentication system for {framework}:
        
        Requirements: {json.dumps(requirements)}
        
        Include:
        1. JWT token generation
        2. User registration
        3. Login/logout
        4. Password hashing
        5. Role-based access
        6. Token refresh
        """
        
        return await self.groq_service.complete(prompt)
    
    async def _generate_integration(self, integration: Dict) -> str:
        prompt = f"""
        Generate integration code for:
        
        {json.dumps(integration)}
        
        Include:
        1. Connection setup
        2. Authentication
        3. API methods
        4. Error handling
        5. Rate limiting
        6. Data transformation
        """
        
        return await self.groq_service.complete(prompt)
    
    async def _generate_config(self, requirements: Dict, integrations: List) -> str:
        prompt = f"""
        Generate configuration file with:
        
        Requirements: {json.dumps(requirements)}
        Integrations: {json.dumps(integrations)}
        
        Include:
        1. Environment variables
        2. Database settings
        3. API keys
        4. Feature flags
        5. Logging config
        """
        
        return await self.groq_service.complete(prompt)
    
    async def _generate_requirements(self, framework: str, integrations: List) -> str:
        base_deps = {
            "fastapi": ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "python-jose", "passlib", "python-multipart"],
            "flask": ["flask", "flask-sqlalchemy", "flask-cors", "flask-jwt-extended", "flask-migrate"],
            "django": ["django", "djangorestframework", "django-cors-headers", "djangorestframework-simplejwt"]
        }
        
        deps = base_deps.get(framework, [])
        
        for integration in integrations:
            if integration.get("type") == "notion":
                deps.append("notion-client")
            elif integration.get("type") == "slack":
                deps.append("slack-sdk")
            elif integration.get("type") == "google":
                deps.append("google-api-python-client")
        
        return "\n".join(deps)
    
    async def _extract_dependencies(self, design: str, framework: str) -> List[str]:
        prompt = f"""
        Extract all Python dependencies from this {framework} application design:
        
        {design}
        
        Return as a list of package names.
        """
        
        result = await self.groq_service.complete(
            prompt,
            response_format={"type": "json_object"}
        )
        
        return json.loads(result).get("dependencies", [])
    
    async def _generate_deployment_config(self, framework: str) -> Dict:
        configs = {
            "fastapi": {
                "dockerfile": "FROM python:3.11\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nCMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]",
                "command": "uvicorn main:app --reload",
                "port": 8000
            },
            "flask": {
                "dockerfile": "FROM python:3.11\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nCMD [\"flask\", \"run\", \"--host\", \"0.0.0.0\"]",
                "command": "flask run",
                "port": 5000
            }
        }
        
        return configs.get(framework, configs["fastapi"])
    
    async def _generate_flask_files(
        self, 
        schema: Dict, 
        requirements: Dict, 
        integrations: List
    ) -> Dict[str, str]:
        return {}
    
    async def _generate_django_files(
        self, 
        schema: Dict, 
        requirements: Dict, 
        integrations: List
    ) -> Dict[str, str]:
        return {}