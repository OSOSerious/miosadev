# app/core/ai/groq_service.py
from groq import AsyncGroq
from typing import Optional, Dict, List, Any
from app.core.config import settings
import logging
import time


logger = logging.getLogger(__name__)

class _TokenTracker:
    """Lightweight session token/cost tracker with console display."""
    def __init__(self):
        self.reset()

    def reset(self):
        self.call_count = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self.calls: List[Dict[str, Any]] = []

    def estimate_tokens(self, text: Optional[str]) -> int:
        if not text:
            return 0
        # Rough heuristic ~4 chars/token
        return max(1, int(len(text) / 4))

    def _model_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """ESTIMATE ONLY: rough cost estimate mapping; override via env/settings.

        Reads optional overrides from settings via GROQ_PRICING_OVERRIDES env as
        a JSON mapping of model -> [in_per_k, out_per_k]. If not provided, falls
        back to conservative defaults. These values are NOT used for billing.
        """
        # Default USD per 1k tokens (input, output) — estimates only
        default_pricing = {
            "llama-3.1-8b-instant": (0.05, 0.08),
            "llama-3.2-3b-preview": (0.02, 0.03),
            "llama-3.2-11b-vision-preview": (0.10, 0.12),
            "llama-3.2-90b-vision-preview": (0.60, 0.80),
            "gemma2-9b-it": (0.06, 0.08),
            "llama3-groq-8b-8192-tool-use-preview": (0.08, 0.10),
            "llama3-groq-70b-8192-tool-use-preview": (0.50, 0.70),
        }
        try:
            overrides = getattr(settings, "GROQ_PRICING_OVERRIDES", None) or {}
            pricing = {**default_pricing, **overrides}
        except Exception:
            pricing = default_pricing
        inp_k, out_k = pricing.get(model, default_pricing["llama-3.1-8b-instant"])  # fallback
        # Make it explicit in logs that this is an estimate
        logger.debug("Cost estimate only (not for billing). model=%s in_k=%.4f out_k=%.4f", model, inp_k, out_k)
        return (input_tokens / 1000.0) * inp_k + (output_tokens / 1000.0) * out_k

    def track(self, model: str, prompt: str, output: Optional[str], ok: bool, started: float, error: Optional[Exception] = None) -> Dict[str, Any]:
        self.call_count += 1
        input_tokens = self.estimate_tokens(prompt)
        output_tokens = self.estimate_tokens(output)
        cost = self._model_cost(model, input_tokens, output_tokens)
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += cost
        metrics = {
            "call_number": self.call_count,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
            "success": ok,
            "duration_ms": int((time.time() - started) * 1000),
            "timestamp": time.time(),
        }
        self.calls.append(metrics)
        self._display(metrics)
        return metrics

    def _display(self, m: Dict[str, Any]):
        try:
            logger.info(
                "\n" +
                "┌──────────────────────────────────────────────┐\n"
                f"│ 🔄 LLM Call #{m['call_number']:<3}                           │\n"
                "├──────────────────────────────────────────────┤\n"
                f"│ Model: {m['model']:<35}│\n"
                f"│ Input: {m['input_tokens']:<5} tokens                         │\n"
                f"│ Output: {m['output_tokens']:<5} tokens                        │\n"
                f"│ Cost: ${m['cost']:.5f}                              │\n"
                f"│ Status: {'✅ Success' if m['success'] else '❌ Failed':<29}│\n"
                f"│ Duration: {m['duration_ms']} ms                         │\n"
                "├──────────────────────────────────────────────┤\n"
                f"│ Session Total:                                     │\n"
                f"│ Calls: {self.call_count:<3} | Tokens: {self.total_input_tokens + self.total_output_tokens:<6}          │\n"
                f"│ Cost: ${self.total_cost:.4f}                               │\n"
                "└──────────────────────────────────────────────┘\n"
            )
        except Exception:
            pass

    def session_metrics(self) -> Dict[str, Any]:
        total_tokens = self.total_input_tokens + self.total_output_tokens
        avg_tokens = int(total_tokens / self.call_count) if self.call_count else 0
        return {
            "calls": self.call_count,
            "tokens": total_tokens,
            "cost": self.total_cost,
            "avgTokensPerCall": avg_tokens,
        }

class GroqService:
    """Main Groq service for AI operations with fallback models"""
    
    # Updated list of available models on Groq (Dec 2024)
    AVAILABLE_MODELS = [
        "moonshotai/kimi-k2-instruct",  # Kimi K2 - Primary model
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
            "mixtral-8x7b-32768": "moonshotai/kimi-k2-instruct",
            "llama3-8b-8192": "moonshotai/kimi-k2-instruct",
            "llama3-70b-8192": "moonshotai/kimi-k2-instruct",
            "llama-3.3-70b-versatile": "moonshotai/kimi-k2-instruct",
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
        self._tracker = _TokenTracker()
    
    async def complete(self, prompt: str, response_format: Optional[Dict] = None) -> str:
        """Generate completion from prompt with automatic fallback"""
        messages = [{"role": "user", "content": prompt}]
        
        # Try each model until one works
        models_to_try = [self.model] + [m for m in self.AVAILABLE_MODELS if m != self.model]
        
        for model in models_to_try:
            try:
                started = time.time()
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
                        self._tracker.track(model, prompt, content, True, started)
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
                        started = time.time()
                        kwargs.pop("response_format", None)
                        response = await self.client.chat.completions.create(**kwargs)
                        if response.choices and response.choices[0].message:
                            content = response.choices[0].message.content
                            if content:
                                logger.debug(f"Successfully used model {model} without response_format")
                                self._tracker.track(model, prompt, content, True, started)
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
                started = time.time()
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
                        # Track using concatenated user content as prompt estimate
                        joined_prompt = "\n".join(m.get("content", "") for m in messages)
                        self._tracker.track(model, joined_prompt, content, True, started)
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

    # ========== Metrics API ==========
    def get_session_metrics(self) -> Dict[str, Any]:
        return self._tracker.session_metrics()

    def reset_session_metrics(self) -> None:
        self._tracker.reset()

# Singleton instance for backward compatibility
groq_service = GroqService()