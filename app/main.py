from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import uuid
from typing import Dict, Any

from app.core.config import settings
from app.orchestration.coordinator import ApplicationGenerationCoordinator

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

coordinator = ApplicationGenerationCoordinator()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting MIOSA Application Generation Platform v{settings.VERSION}")
    
    from app.core.ai.groq_service import GroqService
    groq = GroqService()
    groq_health = await groq.check_health()
    if groq_health:
        logger.info("Groq service is healthy")
    else:
        logger.warning("Groq service health check failed")
    
    yield
    
    logger.info("Shutting down MIOSA")

app = FastAPI(
    title="MIOSA - AI Application Generation Platform",
    version=settings.VERSION,
    description="Generate complete applications through intelligent consultation",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.get("/")
async def root():
    return {
        "app": "MIOSA",
        "version": settings.VERSION,
        "status": "running",
        "description": "AI Application Generation Platform",
        "docs": "/api/docs",
        "endpoints": {
            "consultation": "/api/v1/consultation/start",
            "generate": "/api/v1/generate",
            "sessions": "/api/v1/sessions"
        }
    }

@app.get("/health")
async def health_check():
    from app.core.ai.groq_service import GroqService
    groq = GroqService()
    groq_health = await groq.check_health()
    
    return {
        "status": "healthy" if groq_health else "degraded",
        "version": settings.VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "groq": "healthy" if groq_health else "unhealthy",
            "agents": "healthy",
            "orchestrator": "healthy"
        }
    }

@app.post("/api/v1/consultation/start")
async def start_consultation(request: Dict[str, Any]):
    try:
        session_id = str(uuid.uuid4())
        message = request.get("message", "")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        result = await coordinator.start_consultation(session_id, message)
        
        return {
            "session_id": session_id,
            "response": result.get("response"),
            "phase": result.get("phase"),
            "progress": result.get("progress", 0),
            "ready_for_generation": result.get("ready_for_generation", False)
        }
    except Exception as e:
        logger.error(f"Error starting consultation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/consultation/continue")
async def continue_consultation(request: Dict[str, Any]):
    try:
        session_id = request.get("session_id")
        message = request.get("message", "")
        
        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")
        
        result = await coordinator.continue_consultation(session_id, message)
        
        return {
            "session_id": session_id,
            "response": result.get("response"),
            "phase": result.get("phase"),
            "progress": result.get("progress", 0),
            "ready_for_generation": result.get("ready_for_generation", False),
            "solution": result.get("solution")
        }
    except Exception as e:
        logger.error(f"Error continuing consultation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/generate")
async def generate_application(request: Dict[str, Any]):
    try:
        session_id = request.get("session_id")
        
        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")
        
        result = await coordinator.generate_application(session_id)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return {
            "status": "success",
            "project_id": result.get("project_id"),
            "summary": result.get("summary"),
            "components": {
                "database": "Generated",
                "backend": "Generated",
                "frontend": "Generated",
                "integrations": "Configured",
                "deployment": "Ready"
            }
        }
    except Exception as e:
        logger.error(f"Error generating application: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/sessions")
async def list_sessions():
    try:
        sessions = coordinator.list_sessions()
        return {
            "sessions": sessions,
            "count": len(sessions)
        }
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/sessions/{session_id}")
async def get_session(session_id: str):
    try:
        session = coordinator.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session_id,
            "phase": session.get("phase"),
            "started_at": session.get("started_at"),
            "requirements": session.get("requirements", {}),
            "components": list(session.get("generated_components", {}).keys())
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/tools/discover")
async def discover_tool_capabilities(request: Dict[str, Any]):
    try:
        tool_type = request.get("tool_type")
        
        if not tool_type:
            raise HTTPException(status_code=400, detail="Tool type is required")
        
        from app.agents.mcp_integration import MCPIntegrationAgent
        agent = MCPIntegrationAgent()
        
        result = await agent.process_task({
            "type": "discover_capabilities",
            "tool_type": tool_type
        })
        
        return result
    except Exception as e:
        logger.error(f"Error discovering tool capabilities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )