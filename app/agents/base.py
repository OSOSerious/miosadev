from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
import logging
from app.core.ai.groq_service import GroqService

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.groq_service = GroqService()
        self.context = {}
        
    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    def update_context(self, context: Dict[str, Any]):
        self.context.update(context)
    
    def get_context(self) -> Dict[str, Any]:
        return self.context
    
    async def log_activity(self, activity: str, data: Optional[Dict] = None):
        logger.info(f"[{self.name}] {activity}", extra={"data": data})
    
    async def think(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Use AI to process a prompt and return text response"""
        try:
            full_prompt = f"Role: {self.role}\n\n{prompt}"
            if context:
                full_prompt += f"\n\nContext: {json.dumps(context, indent=2)}"
            
            response = await self.groq_service.complete(full_prompt)
            return response
        except Exception as e:
            logger.error(f"Error in {self.name} thinking: {e}")
            return "I apologize, but I'm having trouble processing that request. Could you please rephrase or provide more details?"
    
    async def think_json(self, prompt: str, context: Optional[Dict] = None) -> Dict:
        """Use AI to process a prompt and return JSON response"""
        try:
            full_prompt = f"Role: {self.role}\n\n{prompt}"
            if context:
                full_prompt += f"\n\nContext: {json.dumps(context, indent=2)}"
            full_prompt += "\n\nReturn your response as valid JSON only."
            
            response = await self.groq_service.complete(
                full_prompt,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON in {self.name}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error in {self.name} thinking JSON: {e}")
            return {}