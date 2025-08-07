from typing import Dict, Any, List, Optional
import asyncio
import logging
from datetime import datetime
from app.agents.communication import CommunicationAgent
from app.agents.database_architect import DatabaseArchitectAgent
from app.agents.backend_developer import BackendDeveloperAgent
from app.agents.frontend_developer import FrontendDeveloperAgent
from app.agents.mcp_integration import MCPIntegrationAgent
from app.storage import SessionManager

logger = logging.getLogger(__name__)

class ApplicationGenerationCoordinator:
    def __init__(self):
        self.agents = self._initialize_agents()
        self.sessions = {}
        self.current_session = None
        self.session_manager = SessionManager()
        
    def _initialize_agents(self) -> Dict[str, Any]:
        return {
            "communication": CommunicationAgent(),
            "database_architect": DatabaseArchitectAgent(),
            "backend_developer": BackendDeveloperAgent(),
            "frontend_developer": FrontendDeveloperAgent(),
            "mcp_integration": MCPIntegrationAgent()
        }
    
    async def start_consultation(self, session_id: str, initial_message: str) -> Dict:
        """Start a new consultation session"""
        
        # Initialize session with consultation-focused structure
        self.current_session = {
            "id": session_id,
            "started_at": datetime.now(),
            "phase": "initial",
            "messages": [],
            "extracted_info": {},
            "requirements": {},
            "generated_components": {},
            "ready_for_generation": False,
            "preview_announced": False,
            # Background build lifecycle tracking
            "background_build": {
                "status": "idle",           # idle | starting | scaffolding | generating | complete | error
                "progress": 0,                # 0-100
                "error": None,
                "preview_url": None,
                "last_update": datetime.now().isoformat()
            }
        }
        
        self.sessions[session_id] = self.current_session
        
        # Process the initial message
        result = await self.process_consultation_message(session_id, initial_message)
        
        return result
    
    async def process_consultation_message(self, session_id: str, message: str) -> Dict:
        """Process message with proper state management"""
        
        # Get full session data
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Add message to history
        session["messages"].append({
            "role": "user",
            "content": message
        })
        
        # Process through communication agent
        result = await self.agents["communication"].process_task({
            "type": "understand_request",
            "message": message,
            "session_data": session
        })
        
        # Update session with new info
        session["phase"] = result["phase"]
        session["extracted_info"] = result["extracted_info"]
        session["messages"].append({
            "role": "assistant",
            "content": result["response"]
        })
        session["ready_for_generation"] = result.get("ready_for_generation", False)
        
        # Save session to persistent storage
        self.session_manager.save_session(session_id, session)
        
        # If we have enough info by layer2, trigger a background build (non-blocking)
        try:
            if result["phase"] in ("layer2", "layer3", "recommendation") and \
               self._has_enough_info_to_build(session.get("extracted_info", {})) and \
               session.get("background_build", {}).get("status") in ("idle", "error"):
                await self._trigger_background_build(session_id, session["extracted_info"])
        except Exception as e:
            # Don't break the consultation on background failures
            session["background_build"]["status"] = "error"
            session["background_build"]["error"] = str(e)
            session["background_build"]["last_update"] = datetime.now().isoformat()
            self.session_manager.save_session(session_id, session)
        
        # When ready, automatically suggest solution
        if result["phase"] == "recommendation":
            solution = await self._generate_solution_recommendation(result["extracted_info"])
            result["solution"] = solution
        
        # Determine preview readiness and set announcement flag once
        preview_ready = session.get("background_build", {}).get("status") == "complete"
        if preview_ready and not session.get("preview_announced"):
            session["preview_announced"] = True
            self.session_manager.save_session(session_id, session)

        return {
            "session_id": session_id,
            "response": result["response"],
            "phase": result["phase"],
            "progress": result["progress"],
            "ready_for_generation": result.get("ready_for_generation", False),
            "solution": result.get("solution"),
            "background_build": session.get("background_build"),
            "preview_ready": preview_ready,
            "preview_announced": session.get("preview_announced", False)
        }
    
    async def continue_consultation(
        self, 
        session_id: str, 
        message: str
    ) -> Dict:
        """Continue an existing consultation"""
        
        return await self.process_consultation_message(session_id, message)
    
    async def _generate_solution_recommendation(self, extracted_info: Dict) -> Dict:
        """Generate a solution recommendation based on extracted info"""
        
        problem_area = extracted_info.get("problem_area", "process")
        business_impact = extracted_info.get("business_impact_level", "medium")
        
        # Determine the best technical approach
        solution_map = {
            "support": {
                "type": "Customer Service Platform",
                "stack": "FastAPI + React + PostgreSQL",
                "features": ["Ticket Management", "Auto-Routing", "AI Responses", "Analytics"]
            },
            "sales": {
                "type": "Sales Automation System",
                "stack": "Django + Vue.js + PostgreSQL",
                "features": ["Lead Tracking", "Pipeline Management", "Email Automation", "Reporting"]
            },
            "operations": {
                "type": "Operations Dashboard",
                "stack": "FastAPI + React + TimescaleDB",
                "features": ["Real-time Monitoring", "Process Automation", "KPI Tracking", "Alerts"]
            },
            "data": {
                "type": "Analytics Platform",
                "stack": "FastAPI + React + PostgreSQL + Redis",
                "features": ["Data Pipeline", "Visualization", "Reporting", "ML Insights"]
            },
            "process": {
                "type": "Workflow Automation System",
                "stack": "FastAPI + React + PostgreSQL",
                "features": ["Process Builder", "Task Management", "Integration Hub", "Monitoring"]
            }
        }
        
        solution = solution_map.get(problem_area, solution_map["process"])
        
        return {
            "recommended_solution": solution["type"],
            "technical_stack": solution["stack"],
            "core_features": solution["features"],
            "estimated_impact": f"Will reduce {extracted_info.get('time_spent', 'significant time')} spent on {extracted_info.get('surface_problem', 'this problem')}",
            "next_steps": "Ready to generate your custom application"
        }
    
    async def generate_application(self, session_id: str) -> Dict:
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        if not session.get("ready_for_generation"):
            raise ValueError("Consultation not complete")
        
        try:
            requirements = await self._extract_requirements(session)
            session["requirements"] = requirements
            
            integrations = await self._identify_integrations(session)
            session["integrations"] = integrations
            
            database = await self._design_database(requirements)
            session["generated_components"]["database"] = database
            
            backend = await self._generate_backend(
                database, 
                requirements, 
                integrations
            )
            session["generated_components"]["backend"] = backend
            
            mcp_connectors = await self._setup_mcp_integrations(integrations)
            session["generated_components"]["mcp_connectors"] = mcp_connectors
            
            frontend = await self._generate_frontend(
                backend, 
                requirements,
                session.get("extracted_info", {}).get("design_preferences", {})
            )
            session["generated_components"]["frontend"] = frontend
            
            deployment = await self._prepare_deployment(session)
            session["generated_components"]["deployment"] = deployment
            
            project_id = await self._create_project(session)
            
            return {
                "status": "success",
                "project_id": project_id,
                "components": session["generated_components"],
                "summary": await self._generate_summary(session)
            }
            
        except Exception as e:
            logger.error(f"Error generating application: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _extract_requirements(self, session: Dict) -> Dict:
        return await self.agents["communication"].process_task({
            "type": "extract_requirements",
            "consultation": session.get("extracted_info", {})
        })
    
    async def _identify_integrations(self, session: Dict) -> List[Dict]:
        result = await self.agents["communication"].process_task({
            "type": "identify_integrations",
            "context": session.get("extracted_info", {})
        })
        return result.get("integrations", [])
    
    async def _design_database(self, requirements: Dict) -> Dict:
        return await self.agents["database_architect"].process_task({
            "type": "design_schema",
            "requirements": requirements
        })
    
    async def _generate_backend(
        self, 
        database: Dict, 
        requirements: Dict, 
        integrations: List[Dict]
    ) -> Dict:
        return await self.agents["backend_developer"].process_task({
            "type": "generate_backend",
            "database_schema": database,
            "requirements": requirements,
            "integrations": integrations,
            "framework": requirements.get("backend_framework", "fastapi")
        })
    
    async def _setup_mcp_integrations(self, integrations: List[Dict]) -> List[Dict]:
        connectors = []
        
        for integration in integrations:
            connector = await self.agents["mcp_integration"].process_task({
                "type": "integrate_tool",
                "tool_type": integration.get("type"),
                "requirements": integration
            })
            connectors.append(connector)
        
        return connectors
    
    async def _generate_frontend(
        self, 
        backend: Dict, 
        requirements: Dict,
        design_preferences: Dict
    ) -> Dict:
        return await self.agents["frontend_developer"].process_task({
            "type": "generate_frontend",
            "backend_api": backend,
            "requirements": requirements,
            "design_preferences": design_preferences,
            "framework": requirements.get("frontend_framework", "react")
        })

    def _has_enough_info_to_build(self, info: Dict) -> bool:
        """Heuristics to start background scaffolding around layer2."""
        if not info:
            return False
        # Common fields extracted by CommunicationAgent
        has_problem = bool(info.get("surface_problem") or info.get("specific_challenge"))
        has_process = bool(info.get("current_process") or info.get("current_process_description"))
        # Optional: some impact/time signal helps
        has_impact = bool(info.get("time_spent") or info.get("growth_impact") or info.get("quantified_impact"))
        return has_problem and has_process and has_impact

    async def _trigger_background_build(self, session_id: str, info: Dict) -> None:
        """Mark session and spawn a non-blocking background build task."""
        session = self.sessions.get(session_id)
        if not session:
            return
        session["background_build"]["status"] = "starting"
        session["background_build"]["progress"] = 5
        session["background_build"]["error"] = None
        session["background_build"]["last_update"] = datetime.now().isoformat()
        self.session_manager.save_session(session_id, session)

        # Fire-and-forget background task
        asyncio.create_task(self._run_background_build(session_id))

    async def _run_background_build(self, session_id: str) -> None:
        """Progressively generate components without blocking the consultation."""
        session = self.sessions.get(session_id)
        if not session:
            return
        try:
            session["background_build"]["status"] = "scaffolding"
            session["background_build"]["progress"] = 15
            session["background_build"]["last_update"] = datetime.now().isoformat()
            self.session_manager.save_session(session_id, session)

            # Derive minimal requirements from extracted_info
            requirements = await self._extract_requirements(session)
            session["requirements"] = requirements
            session["background_build"]["progress"] = 25
            self.session_manager.save_session(session_id, session)

            # Identify integrations early
            integrations = await self._identify_integrations(session)
            session["integrations"] = integrations
            session["background_build"]["progress"] = 35
            self.session_manager.save_session(session_id, session)

            # Database design
            database = await self._design_database(requirements)
            session["generated_components"]["database"] = database
            session["background_build"]["progress"] = 55
            session["background_build"]["status"] = "generating"
            self.session_manager.save_session(session_id, session)

            # Backend generation
            backend = await self._generate_backend(
                database,
                requirements,
                integrations
            )
            session["generated_components"]["backend"] = backend
            session["background_build"]["progress"] = 75
            self.session_manager.save_session(session_id, session)

            # Frontend generation (basic scaffolding)
            frontend = await self._generate_frontend(
                backend,
                requirements,
                session.get("extracted_info", {}).get("design_preferences", {})
            )
            session["generated_components"]["frontend"] = frontend
            session["background_build"]["progress"] = 90
            self.session_manager.save_session(session_id, session)

            # Optionally: prepare deployment artifacts (lightweight)
            deployment = await self._prepare_deployment(session)
            session["generated_components"]["deployment"] = deployment
            session["background_build"]["progress"] = 100
            session["background_build"]["status"] = "complete"
            session["background_build"]["last_update"] = datetime.now().isoformat()

            # Optional preview URL stub (integrate with live preview system later)
            session["background_build"]["preview_url"] = None
            
            self.session_manager.save_session(session_id, session)
        except Exception as e:
            session = self.sessions.get(session_id) or {}
            if session:
                session.setdefault("background_build", {})
                session["background_build"]["status"] = "error"
                session["background_build"]["error"] = str(e)
                session["background_build"]["last_update"] = datetime.now().isoformat()
                self.session_manager.save_session(session_id, session)

    def get_build_status(self, session_id: str) -> Dict:
        """Lightweight accessor for background build status for use by API layer or UI polling."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        return {
            "session_id": session_id,
            "background_build": session.get("background_build", {}),
            "preview_ready": session.get("background_build", {}).get("status") == "complete",
            "preview_announced": session.get("preview_announced", False)
        }
    
    async def _prepare_deployment(self, session: Dict) -> Dict:
        components = session["generated_components"]
        
        return {
            "docker_compose": await self._generate_docker_compose(components),
            "kubernetes": await self._generate_kubernetes_manifests(components),
            "ci_cd": await self._generate_ci_cd_pipeline(components),
            "environment_vars": await self._extract_env_vars(components)
        }
    
    async def _generate_docker_compose(self, components: Dict) -> str:
        services = []
        
        if "backend" in components:
            services.append("""
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/app
    depends_on:
      - db
            """)
        
        if "frontend" in components:
            services.append("""
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://backend:8000
    depends_on:
      - backend
            """)
        
        services.append("""
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=app
    volumes:
      - postgres_data:/var/lib/postgresql/data
        """)
        
        return f"""version: '3.8'

services:
{''.join(services)}

volumes:
  postgres_data:
"""
    
    async def _generate_kubernetes_manifests(self, components: Dict) -> Dict:
        return {}
    
    async def _generate_ci_cd_pipeline(self, components: Dict) -> Dict:
        return {
            "github_actions": """
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          docker-compose run backend pytest
          docker-compose run frontend npm test
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Deploy
        run: |
          echo "Deploy to production"
"""
        }
    
    async def _extract_env_vars(self, components: Dict) -> Dict:
        env_vars = {
            "DATABASE_URL": "postgresql://user:password@localhost:5432/app",
            "JWT_SECRET": "your-secret-key",
            "FRONTEND_URL": "http://localhost:3000",
            "BACKEND_URL": "http://localhost:8000"
        }
        
        for connector in components.get("mcp_connectors", []):
            for credential in connector.get("required_credentials", []):
                env_vars[credential] = f"your-{credential.lower()}"
        
        return env_vars
    
    async def _create_project(self, session: Dict) -> str:
        import uuid
        project_id = str(uuid.uuid4())
        
        return project_id
    
    async def _generate_summary(self, session: Dict) -> str:
        components = session["generated_components"]
        
        summary = f"""
Application Generation Complete!

Generated Components:
- Database: {len(components.get('database', {}).get('tables', []))} tables
- Backend: {components.get('backend', {}).get('framework', 'N/A')} framework
- Frontend: {components.get('frontend', {}).get('framework', 'N/A')} framework
- Integrations: {len(components.get('mcp_connectors', []))} tools connected

The application has been successfully generated with all requested features.
"""
        
        return summary
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session from memory or load from storage"""
        # Try memory first
        session = self.sessions.get(session_id)
        if session:
            return session
        
        # Try loading from storage
        session = self.session_manager.load_session(session_id)
        if session:
            self.sessions[session_id] = session
            return session
        
        return None
    
    def list_sessions(self) -> List[Dict]:
        """List all sessions from memory and storage"""
        # Get sessions from storage
        stored_sessions = self.session_manager.list_sessions()
        
        # Merge with in-memory sessions
        session_ids = set()
        all_sessions = []
        
        # Add stored sessions
        for session in stored_sessions:
            session_ids.add(session["id"])
            all_sessions.append(session)
        
        # Add in-memory sessions not in storage
        for session in self.sessions.values():
            if session["id"] not in session_ids:
                all_sessions.append({
                    "id": session["id"],
                    "started_at": session["started_at"],
                    "phase": session["phase"],
                    "ready_for_generation": session.get("ready_for_generation", False)
                })
        
        return all_sessions