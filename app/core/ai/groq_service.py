# app/core/ai/groq_service.py
from groq import AsyncGroq
from typing import Optional, Dict, List, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class GroqService:
    """Main Groq service for AI operations with fallback models"""
    
    # Updated list of available models on Groq (Dec 2024)
    AVAILABLE_MODELS = [
        "llama-3.1-8b-instant",     # Fast and reliable
        "llama-3.2-3b-preview",      # Smallest, fastest
        "llama-3.2-11b-vision-preview",  # Mid-size
        "llama-3.2-90b-vision-preview",  # Largest available
        "gemma2-9b-it",              # Google's Gemma 2
        "llama3-groq-8b-8192-tool-use-preview",  # Tool use capable
        "llama3-groq-70b-8192-tool-use-preview", # Larger tool use
    ]
    
    def __init__(self):
        self.client = AsyncGroq(
            api_key=settings.GROQ_API_KEY,
            timeout=30.0,
            max_retries=3
        )
        # Use configured model or fallback to first available
        configured_model = settings.GROQ_MODEL
        
        # Map old model names to new ones
        model_mapping = {
            "mixtral-8x7b-32768": "llama-3.1-8b-instant",
            "llama3-8b-8192": "llama-3.1-8b-instant",
            "llama3-70b-8192": "llama-3.2-90b-vision-preview",
            "llama-3.3-70b-versatile": "llama-3.2-90b-vision-preview",
        }
        
        # Use mapped model if old model configured
        if configured_model in model_mapping:
            self.model = model_mapping[configured_model]
            logger.info(f"Mapped old model {configured_model} to {self.model}")
        elif configured_model in self.AVAILABLE_MODELS:
            self.model = configured_model
        else:
            self.model = self.AVAILABLE_MODELS[0]
            logger.warning(f"Model {configured_model} not available, using {self.model}")
            
        logger.info(f"Using Groq model: {self.model}")
    
    async def complete(self, prompt: str, response_format: Optional[Dict] = None) -> str:
        """Generate completion from prompt with automatic fallback"""
        messages = [{"role": "user", "content": prompt}]
        
        # Try each model until one works
        models_to_try = [self.model] + [m for m in self.AVAILABLE_MODELS if m != self.model]
        
        for model in models_to_try:
            try:
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
                
                # Note: Some models may not support JSON response format
                if response_format and not "vision" in model:
                    kwargs["response_format"] = response_format
                
                response = await self.client.chat.completions.create(**kwargs)
                
                if response.choices and response.choices[0].message:
                    content = response.choices[0].message.content
                    if content:
                        logger.debug(f"Successfully used model: {model}")
                        return content
                    
            except Exception as e:
                error_msg = str(e).lower()
                if "over capacity" in error_msg or "503" in error_msg:
                    logger.warning(f"Model {model} is over capacity, trying next model...")
                    continue
                elif "not found" in error_msg or "404" in error_msg or "decommissioned" in error_msg:
                    logger.warning(f"Model {model} not available, trying next model...")
                    continue
                elif "does not support response_format" in error_msg:
                    # Try without response_format
                    try:
                        kwargs.pop("response_format", None)
                        response = await self.client.chat.completions.create(**kwargs)
                        if response.choices and response.choices[0].message:
                            content = response.choices[0].message.content
                            if content:
                                logger.debug(f"Successfully used model {model} without response_format")
                                return content
                    except Exception as e2:
                        logger.error(f"Error with model {model} (retry): {e2}")
                        continue
                else:
                    logger.error(f"Error with model {model}: {e}")
                    continue
        
        # If all models fail, raise an error
        raise Exception("All Groq models are currently unavailable. Please try again later.")
    
    async def check_health(self) -> bool:
        """Check if Groq service is healthy"""
        test_models = [self.model] + self.AVAILABLE_MODELS[:2]  # Check first 3 models
        
        for model in test_models:
            try:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                if response and response.choices:
                    logger.info(f"Groq health check passed with model: {model}")
                    # Update default model to working one
                    if model != self.model:
                        self.model = model
                        logger.info(f"Switched to working model: {model}")
                    return True
            except Exception as e:
                logger.debug(f"Health check failed for {model}: {e}")
                continue
        
        logger.error("All models failed health check")
        return False
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        consultation_type: str = "general",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Generate AI response with automatic model fallback"""
        
        models_to_try = [self.model] + [m for m in self.AVAILABLE_MODELS if m != self.model]
        
        for model in models_to_try:
            try:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=1,
                    stream=False
                )
                
                if response.choices and response.choices[0].message:
                    content = response.choices[0].message.content
                    if content:
                        logger.debug(f"Successfully used model: {model}")
                        return content.strip()
                    
            except Exception as e:
                error_msg = str(e).lower()
                if "over capacity" in error_msg or "503" in error_msg:
                    logger.warning(f"Model {model} over capacity, trying fallback...")
                    continue
                elif "not found" in error_msg or "404" in error_msg or "decommissioned" in error_msg:
                    logger.warning(f"Model {model} not available, trying fallback...")
                    continue
                else:
                    logger.error(f"Error with {model}: {e}")
                    continue
        
        raise Exception("All Groq models are currently unavailable. Please try again later.")

# Singleton instance for backward compatibility
groq_service = GroqService()