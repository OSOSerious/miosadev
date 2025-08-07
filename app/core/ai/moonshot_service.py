# app/core/ai/moonshot_service.py
import httpx
from typing import Optional, Dict, List, Any
from app.core.config import settings
import logging
import json

logger = logging.getLogger(__name__)

class MoonshotService:
    """Moonshot AI service for Kimi models"""
    
    BASE_URL = "https://api.moonshot.cn/v1"
    
    # Available Moonshot models
    AVAILABLE_MODELS = [
        "kimi-k2-instruct",    # Kimi K2 instruction model (primary)
        "moonshot-v1-8k",      # 8K context
        "moonshot-v1-32k",     # 32K context  
        "moonshot-v1-128k",    # 128K context
    ]
    
    def __init__(self):
        if not settings.MOONSHOT_API_KEY:
            logger.warning("MOONSHOT_API_KEY not configured, Kimi models will not be available")
            self.enabled = False
            return
            
        self.api_key = settings.MOONSHOT_API_KEY
        self.model = settings.MOONSHOT_MODEL
        self.enabled = True
        
        # Validate model
        if self.model not in self.AVAILABLE_MODELS:
            logger.warning(f"Model {self.model} not in available models, using kimi-k2-instruct")
            self.model = "kimi-k2-instruct"
            
        logger.info(f"Using Moonshot model: {self.model}")
    
    async def complete(self, prompt: str, response_format: Optional[Dict] = None) -> str:
        """Generate completion from prompt"""
        if not self.enabled:
            raise Exception("Moonshot service not configured")
            
        messages = [{"role": "user", "content": prompt}]
        return await self.generate_response(messages)
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Generate AI response using Moonshot API"""
        
        if not self.enabled:
            raise Exception("Moonshot service not configured - please set MOONSHOT_API_KEY")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 401:
                    raise Exception("Invalid Moonshot API key")
                elif response.status_code == 429:
                    raise Exception("Moonshot API rate limit exceeded")
                elif response.status_code != 200:
                    raise Exception(f"Moonshot API error: {response.status_code} - {response.text}")
                
                data = response.json()
                
                if "choices" in data and data["choices"]:
                    content = data["choices"][0]["message"]["content"]
                    if content:
                        logger.debug(f"Successfully used Moonshot model: {self.model}")
                        return content.strip()
                
                raise Exception("No valid response from Moonshot API")
                
        except httpx.TimeoutException:
            raise Exception("Moonshot API request timed out")
        except Exception as e:
            logger.error(f"Error calling Moonshot API: {e}")
            raise
    
    async def check_health(self) -> bool:
        """Check if Moonshot service is healthy"""
        if not self.enabled:
            return False
            
        try:
            response = await self.generate_response(
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            if response:
                logger.info("Moonshot health check passed")
                return True
        except Exception as e:
            logger.error(f"Moonshot health check failed: {e}")
        
        return False

# Singleton instance
moonshot_service = MoonshotService()