# app/core/ai/unified_service.py
from typing import Dict, List, Any, Optional
from app.core.config import settings
from app.core.ai.groq_service import groq_service
from app.core.ai.moonshot_service import moonshot_service
import logging

logger = logging.getLogger(__name__)

class UnifiedAIService:
    """Unified AI service that routes to appropriate provider based on model"""
    
    def __init__(self):
        self.groq = groq_service
        self.moonshot = moonshot_service
        
    def _get_provider_for_model(self, model: str) -> str:
        """Determine which provider to use for a given model"""
        if model.startswith("moonshot") or model.startswith("kimi") or "moonshot" in model:
            return "moonshot"
        else:
            return "groq"
    
    async def complete(self, prompt: str, model: Optional[str] = None, response_format: Optional[Dict] = None) -> str:
        """Generate completion using Kimi through Groq"""
        # Use Kimi through Groq (much simpler!)
        return await self.groq.complete(prompt, response_format)
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        consultation_type: str = "general",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Generate response using Kimi through Groq"""
        # Use Kimi through Groq (much simpler!)
        return await self.groq.generate_response(messages, consultation_type, temperature, max_tokens)
    
    async def check_health(self) -> Dict[str, bool]:
        """Check health of all available providers"""
        health = {}
        
        # Check Groq
        try:
            health["groq"] = await self.groq.check_health()
        except Exception as e:
            logger.error(f"Groq health check failed: {e}")
            health["groq"] = False
        
        # Check Moonshot if configured
        if self.moonshot.enabled:
            try:
                health["moonshot"] = await self.moonshot.check_health()
            except Exception as e:
                logger.error(f"Moonshot health check failed: {e}")
                health["moonshot"] = False
        else:
            health["moonshot"] = None  # Not configured
        
        return health

# Singleton instance
ai_service = UnifiedAIService()