from app.agents.base import BaseAgent
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)

class FrontendDeveloperAgent(BaseAgent):
    def __init__(self):
        super().__init__("frontend_developer", "ui_builder")
        self.supported_frameworks = ["react", "vue", "angular", "svelte", "nextjs"]
        
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type", "generate_frontend")
        
        if task_type == "generate_frontend":
            return await self._generate_frontend(task)
        elif task_type == "generate_components":
            return await self._generate_components(task)
        elif task_type == "generate_pages":
            return await self._generate_pages(task)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _generate_frontend(self, task: Dict) -> Dict:
        backend_api = task.get("backend_api", {})
        requirements = task.get("requirements", {})
        design_preferences = task.get("design_preferences", {})
        framework = task.get("framework", "react")
        
        prompt = f"""
        Generate a complete {framework} frontend application:
        
        Backend API: {json.dumps(backend_api)}
        Requirements: {json.dumps(requirements)}
        Design Preferences: {json.dumps(design_preferences)}
        
        Generate:
        1. Project structure
        2. Component hierarchy
        3. Page layouts
        4. State management
        5. API integration
        6. Routing
        7. Authentication flow
        8. Styling approach
        """
        
        frontend_design = await self.groq_service.complete(prompt)
        
        files = await self._generate_frontend_files(
            frontend_design,
            backend_api,
            requirements,
            framework
        )
        
        return {
            "framework": framework,
            "design": frontend_design,
            "files": files,
            "dependencies": await self._extract_dependencies(frontend_design, framework),
            "build_config": await self._generate_build_config(framework)
        }
    
    async def _generate_frontend_files(
        self,
        design: str,
        backend_api: Dict,
        requirements: Dict,
        framework: str
    ) -> Dict[str, str]:
        
        files = {}
        
        if framework == "react":
            files = await self._generate_react_files(backend_api, requirements)
        elif framework == "vue":
            files = await self._generate_vue_files(backend_api, requirements)
        elif framework == "nextjs":
            files = await self._generate_nextjs_files(backend_api, requirements)
        
        return files
    
    async def _generate_react_files(
        self,
        backend_api: Dict,
        requirements: Dict
    ) -> Dict[str, str]:
        
        files = {}
        
        files["src/App.jsx"] = await self._generate_app_component("react", requirements)
        
        files["src/api/client.js"] = await self._generate_api_client(backend_api)
        
        files["src/store/index.js"] = await self._generate_state_management("react", requirements)
        
        components = await self._identify_components(requirements)
        for component in components:
            files[f"src/components/{component}.jsx"] = await self._generate_component(
                component, "react", requirements
            )
        
        pages = await self._identify_pages(requirements)
        for page in pages:
            files[f"src/pages/{page}.jsx"] = await self._generate_page(
                page, "react", requirements
            )
        
        files["src/hooks/useAuth.js"] = await self._generate_auth_hook("react")
        
        files["src/router/index.jsx"] = await self._generate_router("react", pages)
        
        files["package.json"] = await self._generate_package_json("react", requirements)
        
        return files
    
    async def _generate_app_component(self, framework: str, requirements: Dict) -> str:
        prompt = f"""
        Generate the main App component for {framework}:
        
        Requirements: {json.dumps(requirements)}
        
        Include:
        1. Router setup
        2. Global state provider
        3. Theme provider
        4. Error boundary
        5. Loading states
        """
        
        return await self.groq_service.complete(prompt)
    
    async def _generate_api_client(self, backend_api: Dict) -> str:
        prompt = f"""
        Generate an API client for this backend:
        
        {json.dumps(backend_api)}
        
        Include:
        1. Axios/fetch setup
        2. Request interceptors
        3. Response interceptors
        4. Error handling
        5. Token management
        6. API methods for all endpoints
        """
        
        return await self.groq_service.complete(prompt)
    
    async def _generate_state_management(self, framework: str, requirements: Dict) -> str:
        prompt = f"""
        Generate state management for {framework}:
        
        Requirements: {json.dumps(requirements)}
        
        Include:
        1. Store setup (Redux/Zustand/Context)
        2. Actions/reducers
        3. Selectors
        4. Middleware
        5. Persistence
        """
        
        return await self.groq_service.complete(prompt)
    
    async def _identify_components(self, requirements: Dict) -> List[str]:
        prompt = f"""
        Identify all UI components needed for these requirements:
        
        {json.dumps(requirements)}
        
        Return a list of component names.
        """
        
        result = await self.groq_service.complete(
            prompt,
            response_format={"type": "json_object"}
        )
        
        return json.loads(result).get("components", [])
    
    async def _generate_component(self, component: str, framework: str, requirements: Dict) -> str:
        prompt = f"""
        Generate a {framework} component named {component}:
        
        Requirements: {json.dumps(requirements)}
        
        Include:
        1. Component logic
        2. Props interface
        3. State management
        4. Event handlers
        5. Styling
        6. Accessibility
        """
        
        return await self.groq_service.complete(prompt)
    
    async def _identify_pages(self, requirements: Dict) -> List[str]:
        prompt = f"""
        Identify all pages/routes needed for these requirements:
        
        {json.dumps(requirements)}
        
        Return a list of page names.
        """
        
        result = await self.groq_service.complete(
            prompt,
            response_format={"type": "json_object"}
        )
        
        return json.loads(result).get("pages", [])
    
    async def _generate_page(self, page: str, framework: str, requirements: Dict) -> str:
        prompt = f"""
        Generate a {framework} page component for {page}:
        
        Requirements: {json.dumps(requirements)}
        
        Include:
        1. Page layout
        2. Data fetching
        3. Component composition
        4. Route parameters
        5. SEO metadata
        """
        
        return await self.groq_service.complete(prompt)
    
    async def _generate_auth_hook(self, framework: str) -> str:
        prompt = f"""
        Generate an authentication hook for {framework}:
        
        Include:
        1. Login/logout methods
        2. User state
        3. Token management
        4. Protected route logic
        5. Auto-refresh
        """
        
        return await self.groq_service.complete(prompt)
    
    async def _generate_router(self, framework: str, pages: List[str]) -> str:
        prompt = f"""
        Generate a router configuration for {framework}:
        
        Pages: {json.dumps(pages)}
        
        Include:
        1. Route definitions
        2. Protected routes
        3. Lazy loading
        4. 404 handling
        5. Route guards
        """
        
        return await self.groq_service.complete(prompt)
    
    async def _generate_package_json(self, framework: str, requirements: Dict) -> str:
        base_deps = {
            "react": {
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "react-router-dom": "^6.0.0",
                    "axios": "^1.0.0",
                    "zustand": "^4.0.0"
                },
                "devDependencies": {
                    "vite": "^5.0.0",
                    "@vitejs/plugin-react": "^4.0.0"
                }
            },
            "vue": {
                "dependencies": {
                    "vue": "^3.3.0",
                    "vue-router": "^4.0.0",
                    "pinia": "^2.0.0",
                    "axios": "^1.0.0"
                }
            }
        }
        
        package = base_deps.get(framework, base_deps["react"])
        
        return json.dumps({
            "name": "miosa-generated-app",
            "version": "1.0.0",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            **package
        }, indent=2)
    
    async def _extract_dependencies(self, design: str, framework: str) -> List[str]:
        prompt = f"""
        Extract all npm dependencies from this {framework} application design:
        
        {design}
        
        Return as a list of package names.
        """
        
        result = await self.groq_service.complete(
            prompt,
            response_format={"type": "json_object"}
        )
        
        return json.loads(result).get("dependencies", [])
    
    async def _generate_build_config(self, framework: str) -> Dict:
        configs = {
            "react": {
                "bundler": "vite",
                "build_command": "npm run build",
                "dev_command": "npm run dev",
                "output_dir": "dist"
            },
            "vue": {
                "bundler": "vite",
                "build_command": "npm run build",
                "dev_command": "npm run dev",
                "output_dir": "dist"
            }
        }
        
        return configs.get(framework, configs["react"])
    
    async def _generate_vue_files(self, backend_api: Dict, requirements: Dict) -> Dict[str, str]:
        return {}
    
    async def _generate_nextjs_files(self, backend_api: Dict, requirements: Dict) -> Dict[str, str]:
        return {}