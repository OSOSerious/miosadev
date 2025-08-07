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
from app.core.onboarding import OnboardingFlow, OnboardingStep, UserProfile

logger = logging.getLogger(__name__)

class ApplicationGenerationCoordinator:
    def __init__(self):
        self.agents = self._initialize_agents()
        self.sessions = {}
        self.current_session = None
        self.session_manager = SessionManager()
        self.onboarding = OnboardingFlow()
        
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
        
        # Initialize session with onboarding-first structure
        self.current_session = {
            "id": session_id,
            "started_at": datetime.now(),
            "phase": "onboarding",  # Start with onboarding
            "messages": [],
            "extracted_info": {},
            "requirements": {},
            "planned_components": {},  # Plans, not generated components
            "generated_components": {},  # Initialize to prevent crashes
            "ready_for_generation": False,
            "preview_announced": False,
            # User profile and onboarding
            "user_profile": {},
            "onboarding_step": OnboardingStep.NAME,
            "onboarding_complete": False,
            # Background planning lifecycle tracking  
            "background_build": {
                "status": "idle",           # idle | planning | analyzing | planning_architecture | plan_ready | error
                "progress": 0,                # 0-100
                "error": None,
                "preview_url": None,
                "last_update": datetime.now().isoformat()
            }
        }
        
        self.sessions[session_id] = self.current_session
        
        # Start with onboarding instead of jumping into consultation
        if initial_message.strip():
            # Check if this might be a returning user
            existing_user = self._try_recognize_returning_user(initial_message)
            if existing_user:
                return await self._handle_returning_user(session_id, existing_user, initial_message)
            else:
                # New user - start onboarding
                return await self.process_onboarding_message(session_id, initial_message)
        else:
            # No initial message - start onboarding
            welcome_msg = self.onboarding.get_welcome_message()
            session = self.current_session
            session["messages"].append({
                "role": "assistant", 
                "content": welcome_msg
            })
            
            return {
                "session_id": session_id,
                "response": welcome_msg,
                "phase": "onboarding",
                "progress": 0,
                "onboarding_step": OnboardingStep.NAME.value,
                "ready_for_generation": False
            }
    
    async def process_onboarding_message(self, session_id: str, message: str) -> Dict:
        """Process onboarding messages to capture user profile"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Add user message to history
        session["messages"].append({
            "role": "user",
            "content": message
        })
        
        # Process the onboarding step
        current_step = session.get("onboarding_step", OnboardingStep.NAME)
        profile = session.get("user_profile", {})
        
        # Special case: if they're asking for help or seem confused during onboarding  
        confusion_indicators = ["help", "what", "huh", "?", "confused", "don't understand", "lost"]
        frustration_indicators = ["wtf", "fuck", "stupid", "broken", "sucks", "hate", "annoying", "terrible"]
        correction_indicators = ["not my name", "that's not", "wrong", "no that", "incorrect", "i didn't say"]
        
        message_lower = message.lower().strip()
        
        # Check for frustration first
        if any(word in message_lower for word in frustration_indicators):
            help_msg = f"""I understand this might be frustrating. Let me clarify - I need a few basic details to build custom software specifically for YOUR business.

Currently, I need: {self._get_friendly_step_description(current_step)}

For example, if {self._get_step_example(current_step)}"""
            
        # Check for correction (user saying that wasn't their name/info)
        elif any(phrase in message_lower for phrase in correction_indicators):
            # If they're correcting, we need to go back to the appropriate step
            if current_step == OnboardingStep.EMAIL and profile.get("name"):
                # They're saying the name was wrong, go back to name step
                session["onboarding_step"] = OnboardingStep.NAME
                profile.pop("name", None)
                help_msg = "No worries! Let's start over. What's your actual first name?"
            else:
                help_msg = f"Let me correct that. {self.onboarding.get_current_question(current_step, profile)}"
        
        # Check for confusion
        elif any(word in message_lower for word in confusion_indicators):
            help_msg = f"""No problem! I'm MIOSA - I build custom business software. To create something perfect for you, I need to understand your business first.

Right now I need: {self._get_friendly_step_description(current_step)}

{self._get_step_example(current_step)}"""
        else:
            # Not confused or frustrated, process normally
            help_msg = None
            
        # If we generated a help message, return it
        if help_msg:
            session["messages"].append({
                "role": "assistant",
                "content": help_msg
            })
            
            return {
                "session_id": session_id,
                "response": help_msg,
                "phase": "onboarding",
                "progress": 0,
                "onboarding_step": current_step.value,
                "ready_for_generation": False
            }
        
        # Process the onboarding answer
        next_step, response_msg, validation_success = self.onboarding.process_answer(
            current_step, message, profile
        )
        
        # Update session
        session["onboarding_step"] = next_step
        session["user_profile"] = profile
        
        if next_step == OnboardingStep.COMPLETE:
            # Onboarding complete - transition to consultation
            session["onboarding_complete"] = True
            session["phase"] = "consultation"
            
            # Create user profile object
            user_profile = UserProfile(
                name=profile.get("name", ""),
                email=profile.get("email", ""),
                business_name=profile.get("business_name", ""),
                business_type=profile.get("business_type", ""),
                team_size=profile.get("team_size", 1),
                main_problem=profile.get("main_problem", ""),
                onboarding_complete=True
            )
            session["user_profile"] = user_profile.__dict__
            
            # CRITICAL FIX: Seed extracted_info with onboarding data
            session["extracted_info"] = {
                "business_type": profile.get("business_type", ""),
                "business_name": profile.get("business_name", ""),
                "team_size": profile.get("team_size", 1),
                "surface_problem": profile.get("main_problem", ""),
                "specific_problem": profile.get("main_problem", ""),
                "user_ready": False
            }
            # Set initial progress from onboarding (not 0)
            session["last_progress"] = 25  # Onboarding gives us 25% baseline
        
        # Add response to history
        session["messages"].append({
            "role": "assistant",
            "content": response_msg
        })
        
        # Save session
        self.session_manager.save_session(session_id, session)
        
        return {
            "session_id": session_id,
            "response": response_msg,
            "phase": "consultation" if next_step == OnboardingStep.COMPLETE else "onboarding",
            "progress": 15 if next_step == OnboardingStep.COMPLETE else 0,
            "onboarding_step": next_step.value if next_step != OnboardingStep.COMPLETE else "complete",
            "onboarding_complete": next_step == OnboardingStep.COMPLETE,
            "user_profile": session.get("user_profile", {}),
            "ready_for_generation": False
        }
    
    async def process_consultation_message(self, session_id: str, message: str) -> Dict:
        """Process message with proper state management"""
        
        # Get full session data
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # If onboarding not complete, process onboarding first
        if not session.get("onboarding_complete", False):
            current_step: OnboardingStep = session.get("onboarding_step", OnboardingStep.NAME)
            profile: Dict[str, Any] = session.get("user_profile", {})
            
            # On first step, show welcome prompt rather than treating as an answer when empty
            if message.strip() == "" and current_step == OnboardingStep.NAME:
                welcome = self.onboarding.get_welcome_message()
                # Do not add an assistant message here; let CLI render
                return {
                    "session_id": session_id,
                    "response": welcome,
                    "phase": "onboarding",
                    "progress": 0,
                    "progress_details": {},
                    "ready_for_generation": False,
                }
            
            next_step, reply_text, valid = self.onboarding.process_answer(current_step, message, profile)
            
            # Persist profile and step
            session["user_profile"] = profile
            session["onboarding_step"] = next_step
            session["onboarding_complete"] = (next_step == OnboardingStep.COMPLETE) or profile.get("onboarding_complete", False)
            session["phase"] = "onboarding"
            
            # Record conversation turns
            session["messages"].append({"role": "user", "content": message})
            session["messages"].append({"role": "assistant", "content": reply_text})
            
            # Save and return immediately during onboarding
            self.session_manager.save_session(session_id, session)
            return {
                "session_id": session_id,
                "response": reply_text,
                "phase": "onboarding",
                "progress": 0,
                "progress_details": {},
                "ready_for_generation": False,
                "background_build": session.get("background_build"),
                "plan_ready": False,
                "preview_announced": session.get("preview_announced", False)
            }
        
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
        session["last_progress"] = result.get("last_progress", 0)  # Store for progress smoothing
        session["messages"].append({
            "role": "assistant",
            "content": result["response"]
        })
        session["ready_for_generation"] = result.get("ready_for_generation", False)
        
        # CRITICAL: If user has provided enough info, mark ready for generation
        if result.get("ready_for_generation") or result.get("should_build"):
            logger.info(f"Session {session_id} ready for generation")
            session["ready_for_generation"] = True
            
            # If they explicitly want to build now, set the phase
            if result.get("should_build"):
                session["phase"] = "building"
        
        # Save session to persistent storage
        self.session_manager.save_session(session_id, session)
        
        # Only trigger background planning (not building) when we have enough info
        try:
            if result["phase"] in ("process_understanding", "impact_analysis", "requirements_gathering") and \
               self._has_enough_info_to_plan(session.get("extracted_info", {})) and \
               session.get("background_build", {}).get("status") in ("idle", "error"):
                await self._trigger_background_planning(session_id, session["extracted_info"])
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
        
        # Determine plan readiness and set announcement flag once
        plan_ready = session.get("background_build", {}).get("status") == "plan_ready"
        if plan_ready and not session.get("preview_announced"):
            session["preview_announced"] = True
            self.session_manager.save_session(session_id, session)

        return {
            "session_id": session_id,
            "response": result["response"],
            "phase": result["phase"],
            "progress": result["progress"],
            "progress_details": result.get("progress_details", {}),
            "ready_for_generation": result.get("ready_for_generation", False),
            "solution": result.get("solution"),
            "comprehensive_detected": result.get("comprehensive_detected", False),
            "should_build": result.get("should_build", False),
            "background_build": session.get("background_build"),
            "plan_ready": plan_ready,
            "preview_announced": session.get("preview_announced", False)
        }
    
    async def continue_consultation(
        self, 
        session_id: str, 
        message: str
    ) -> Dict:
        """Continue an existing consultation - handles both onboarding and consultation phases"""
        
        session = self.sessions.get(session_id)
        if not session:
            # Load from storage if not in memory
            session = self.session_manager.load_session(session_id)
            if session:
                self.sessions[session_id] = session
            else:
                raise ValueError(f"Session {session_id} not found")
        
        # Check what phase we're in
        if not session.get("onboarding_complete", False):
            # Still in onboarding
            return await self.process_onboarding_message(session_id, message)
        else:
            # In consultation phase
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

    def _has_enough_info_to_plan(self, info: Dict) -> bool:
        """Heuristics to start background planning around layer2."""
        if not info:
            return False
        # Common fields extracted by CommunicationAgent
        has_problem = bool(info.get("surface_problem") or info.get("specific_challenge"))
        has_process = bool(info.get("current_process") or info.get("current_process_description"))
        # Optional: some impact/time signal helps
        has_impact = bool(info.get("time_spent") or info.get("growth_impact") or info.get("quantified_impact"))
        return has_problem and has_process and has_impact

    async def _trigger_background_planning(self, session_id: str, info: Dict) -> None:
        """Mark session and spawn a non-blocking background planning task."""
        session = self.sessions.get(session_id)
        if not session:
            return
        session["background_build"]["status"] = "planning"
        session["background_build"]["progress"] = 5
        session["background_build"]["error"] = None
        session["background_build"]["last_update"] = datetime.now().isoformat()
        self.session_manager.save_session(session_id, session)

        # Fire-and-forget background task for planning only
        asyncio.create_task(self._run_background_planning(session_id))

    async def _run_background_planning(self, session_id: str) -> None:
        """Progressively plan solution architecture without blocking the consultation."""
        session = self.sessions.get(session_id)
        if not session:
            return
        try:
            session["background_build"]["status"] = "analyzing"
            session["background_build"]["progress"] = 15
            session["background_build"]["last_update"] = datetime.now().isoformat()
            self.session_manager.save_session(session_id, session)

            # Derive minimal requirements from extracted_info (planning only)
            requirements = await self._extract_requirements(session)
            session["requirements"] = requirements
            session["background_build"]["progress"] = 30
            session["background_build"]["status"] = "planning_architecture"
            self.session_manager.save_session(session_id, session)

            # Identify integrations needed
            integrations = await self._identify_integrations(session)
            session["integrations"] = integrations
            session["background_build"]["progress"] = 50
            self.session_manager.save_session(session_id, session)

            # Plan database structure (no actual generation)
            database_plan = await self._plan_database(requirements)
            session["planned_components"]["database"] = database_plan
            session["background_build"]["progress"] = 70
            self.session_manager.save_session(session_id, session)

            # Plan backend architecture (no code generation)
            backend_plan = await self._plan_backend(requirements, integrations)
            session["planned_components"]["backend"] = backend_plan
            session["background_build"]["progress"] = 85
            self.session_manager.save_session(session_id, session)

            # Plan frontend approach
            frontend_plan = await self._plan_frontend(requirements)
            session["planned_components"]["frontend"] = frontend_plan
            session["background_build"]["progress"] = 100
            session["background_build"]["status"] = "plan_ready"
            session["background_build"]["last_update"] = datetime.now().isoformat()

            # No preview URL - this is just planning
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
        """Lightweight accessor for background planning status for use by API layer or UI polling."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        return {
            "session_id": session_id,
            "background_build": session.get("background_build", {}),
            "plan_ready": session.get("background_build", {}).get("status") == "plan_ready",
            "preview_announced": session.get("preview_announced", False)
        }
    
    async def _plan_database(self, requirements: Dict) -> Dict:
        """Plan database structure without generating actual schema"""
        return {
            "planned_tables": ["users", "projects", "tasks"],
            "database_type": "PostgreSQL",
            "approach": "Relational database with normalized structure"
        }
    
    async def _plan_backend(self, requirements: Dict, integrations: List) -> Dict:
        """Plan backend architecture without generating code"""
        return {
            "framework": "FastAPI",
            "architecture": "REST API with authentication",
            "planned_endpoints": ["/api/users", "/api/projects", "/api/tasks"],
            "integrations_needed": len(integrations)
        }
    
    async def _plan_frontend(self, requirements: Dict) -> Dict:
        """Plan frontend approach without generating components"""
        return {
            "framework": "React",
            "architecture": "SPA with routing", 
            "planned_pages": ["Dashboard", "Projects", "Settings"],
            "ui_library": "Material-UI"
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
    
    def _try_recognize_returning_user(self, message: str) -> Optional[Dict]:
        """Try to recognize if this is a returning user based on their message"""
        try:
            # Look for patterns that suggest returning user
            message_lower = message.lower()
            
            # Direct recognition patterns
            returning_patterns = [
                "i'm back", "back again", "hello again", "hi again",
                "remember me", "we talked before", "last time",
                "continue", "where we left off"
            ]
            
            if any(pattern in message_lower for pattern in returning_patterns):
                # Try to extract name from message
                words = message.split()
                for i, word in enumerate(words):
                    if word.lower() in ["i'm", "im", "my", "name", "called"]:
                        if i + 1 < len(words):
                            potential_name = words[i + 1].strip(",.!")
                            user = self.session_manager.find_user_by_name(potential_name)
                            if user:
                                return user
            
            # Check if message contains an email address
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, message)
            if emails:
                user = self.session_manager.load_user_profile_by_email(emails[0])
                if user:
                    return user
            
            return None
            
        except Exception as e:
            logger.error(f"Error recognizing returning user: {e}")
            return None
    
    async def _handle_returning_user(self, session_id: str, user_profile: Dict, initial_message: str) -> Dict:
        """Handle a returning user with existing profile"""
        try:
            session = self.current_session
            
            # Set up session with existing user profile
            session["user_profile"] = user_profile
            session["onboarding_complete"] = True
            session["phase"] = "consultation"
            
            user_name = user_profile.get("name", "")
            business_name = user_profile.get("business_name", "")
            
            welcome_back_msg = f"""Welcome back, {user_name}! 

I remember you - you run {business_name}, {user_profile.get('business_type', 'your business')}. Last time we were working on {user_profile.get('main_problem', 'improving your operations')}.

{initial_message}

Want to continue where we left off, or do you have a new challenge for me to solve?"""
            
            # Add messages to history
            session["messages"].extend([
                {
                    "role": "user",
                    "content": initial_message
                },
                {
                    "role": "assistant", 
                    "content": welcome_back_msg
                }
            ])
            
            # Save session
            self.session_manager.save_session(session_id, session)
            
            return {
                "session_id": session_id,
                "response": welcome_back_msg,
                "phase": "consultation",
                "progress": 15,  # Start with some progress since we know them
                "onboarding_complete": True,
                "user_profile": user_profile,
                "ready_for_generation": False,
                "returning_user": True
            }
            
        except Exception as e:
            logger.error(f"Error handling returning user: {e}")
            # Fall back to normal onboarding
            return await self.process_onboarding_message(session_id, initial_message)
    
    def _get_friendly_step_description(self, step: OnboardingStep) -> str:
        """Get user-friendly description of what we need"""
        descriptions = {
            OnboardingStep.NAME: "your actual name (not 'hey' or a greeting)",
            OnboardingStep.EMAIL: "your email address",
            OnboardingStep.BUSINESS_NAME: "the name of your business",
            OnboardingStep.BUSINESS_TYPE: "what kind of business you run",
            OnboardingStep.TEAM_SIZE: "how many people work with you",
            OnboardingStep.MAIN_PROBLEM: "the main operational challenge you're facing"
        }
        return descriptions.get(step, "some information")
    
    def _get_step_example(self, step: OnboardingStep) -> str:
        """Get helpful example for current step"""
        examples = {
            OnboardingStep.NAME: "your name is 'John' or 'Sarah', just type that",
            OnboardingStep.EMAIL: "you'd type something like 'john@company.com'",
            OnboardingStep.BUSINESS_NAME: "your company is called 'TechCorp', type 'TechCorp'",
            OnboardingStep.BUSINESS_TYPE: "you run a 'Law Firm' or 'Marketing Agency', just tell me which",
            OnboardingStep.TEAM_SIZE: "you have 5 people, just type '5' or '5 people'",
            OnboardingStep.MAIN_PROBLEM: "you're struggling with 'managing client emails' or 'tracking inventory', describe it briefly"
        }
        return examples.get(step, "")
    
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