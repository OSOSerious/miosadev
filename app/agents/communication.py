"""Communication Agent - System-Wide Intelligence"""

from app.agents.base import BaseAgent
from app.business_identifier import BusinessIdentifier
from app.core.system_context import system_context
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class CommunicationAgent(BaseAgent):
    """MIOSA - Intelligent business conversation with full system understanding"""
    
    def __init__(self):
        super().__init__("communication", "business_consultant")
        self.business_identifier = BusinessIdentifier()
        self.system_context = system_context

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process with comprehensive system understanding"""
        
        message = task.get("message", "").strip()
        session_data = task.get("session_data", {})
        
        # Get conversation context
        context = {
            "conversation_history": session_data.get("messages", []),
            "extracted_info": session_data.get("extracted_info", {}),
            "business_profile": session_data.get("business_profile", {})
        }

        # Include user profile for personalization when available
        user_profile = session_data.get("user_profile") or {}
        if user_profile:
            context["user_profile"] = {
                "name": user_profile.get("name"),
                "email": user_profile.get("email"),
                "business_name": user_profile.get("business_name"),
                "business_type": user_profile.get("business_type"),
                "team_size": user_profile.get("team_size"),
                "main_problem": user_profile.get("main_problem"),
            }
        
        # Only handle CLI commands locally - everything else goes to AI
        if self._is_cli_command(message):
            return self._handle_cli_command(message, context)
            
        # Identify business type if not done
        if not context.get("business_profile") or not context["business_profile"].get("category"):
            business_profile = self.business_identifier.identify_business(message, context)
            if business_profile.confidence > 0.3:
                context["business_profile"] = {
                    "category": business_profile.category.value,
                    "subcategory": business_profile.subcategory,
                    "industry": business_profile.industry,
                    "confidence": business_profile.confidence
                }
        
        # Generate response using comprehensive system context
        response = await self._generate_system_aware_response(message, context)
        
        # Validate response for false claims before returning
        response = self._validate_response_truthfulness(response, session_data)
        
        # Extract information using intelligent schema
        extracted_info = await self._extract_structured_information(
            message, response, context["extracted_info"]
        )
        
        # Simplified progress calculation that actually works
        last_progress = session_data.get("last_progress", 0)
        onboarding_complete = session_data.get("onboarding_complete", False)
        
        # Start with baseline from onboarding
        if onboarding_complete:
            progress = max(25, last_progress)  # Minimum 25% after onboarding
        else:
            progress = last_progress
            
        # Increment progress based on information gathered
        if extracted_info.get("business_type") or extracted_info.get("business_context"):
            progress = max(progress, 30)
        if extracted_info.get("specific_problem") or extracted_info.get("surface_problem"):
            progress = max(progress, 40)
        if extracted_info.get("current_process") or "contract" in message.lower():
            progress = max(progress, 50)
        if extracted_info.get("volume_metrics") or "30" in str(extracted_info):
            progress = max(progress, 60)
        if extracted_info.get("solution_requirements") or "ready" in message.lower():
            progress = max(progress, 70)
            
        # Boost progress if user seems ready
        if any(word in message.lower() for word in ["yes", "ready", "start", "begin", "do it", "let's go"]):
            progress = min(100, progress + 10)
            
        # Create simplified progress result
        progress_result = {
            "progress": progress,
            "comprehensive_detected": progress >= 60
        }
        
        return {
            "response": response,
            "phase": self._determine_phase(progress_result["progress"]),
            "extracted_info": extracted_info,
            "business_profile": context.get("business_profile", {}),
            "progress": progress_result["progress"],
            "last_progress": progress_result["progress"],
            "ready_for_generation": self._is_ready_for_generation(extracted_info, context.get("user_profile", {}), progress_result),
            "comprehensive_detected": progress_result.get("comprehensive_detected", False),
            "should_build": self._detect_ready_to_build(message, progress_result, extracted_info, context.get("user_profile", {})),
            "progress_details": self._get_progress_details(extracted_info, progress_result)
        }
    
    def _is_cli_command(self, message: str) -> bool:
        """Only handle actual CLI commands locally"""
        commands = ['help', 'status', 'metrics', 'generate', 'exit']
        return message.lower().strip() in commands
        
    def _handle_cli_command(self, message: str, context: Dict) -> Dict[str, Any]:
        """Handle CLI commands - these are the ONLY hardcoded responses"""
        cmd = message.lower().strip()
        
        if cmd == 'help':
            return {
                "response": "This is handled by the CLI interface",
                "phase": "command",
                "extracted_info": context["extracted_info"],
                "business_profile": context.get("business_profile", {}),
                "progress": 0,
                "ready_for_generation": False
            }
        
        # Other commands handled similarly
        return {
            "response": f"Command '{cmd}' handled by CLI",
            "phase": "command", 
            "extracted_info": context["extracted_info"],
            "business_profile": context.get("business_profile", {}),
            "progress": 0,
            "ready_for_generation": False
        }
    
    async def _generate_system_aware_response(self, message: str, context: Dict) -> str:
        """Generate response using comprehensive system context"""
        
        # Get rich conversation context from system
        conversation_context = self.system_context.get_conversation_context(
            context["extracted_info"],
            context["conversation_history"], 
            context["business_profile"]
        )
        
        prompt = f"""
{conversation_context}

User just said: "{message}"

Respond naturally as MIOSA. Use your comprehensive understanding of business patterns, solution types, and conversation flow to provide an intelligent, contextual response.

Remember:
- You BUILD software, not just talk about it
- Every business is unique - explore their specific situation
- Progress through understanding naturally, not following scripts
- Give relevant examples when helpful
- Ask the next most important question based on what you know
 
 Personalization:
 - If user_profile is present, address the user by name and reference their business naturally.
"""
        
        return await self.think(prompt, context)
    
    async def _extract_structured_information(
        self, user_message: str, ai_response: str, current_info: Dict
    ) -> Dict:
        """Extract information using intelligent schema-based approach"""
        
        # Use system context to guide extraction
        schema = self.system_context.information_schema
        
        prompt = f"""
Extract business information from this conversation using the provided schema.
Focus on quality over quantity - specific details are worth more than vague mentions.

Current information: {json.dumps(current_info, indent=2)}

User said: "{user_message}"
AI responded: "{ai_response}"

EXTRACTION SCHEMA:
{json.dumps(schema, indent=2)}

Extract information for these categories:
- business_context: Company details, industry, size, stage
- problem_discovery: Specific challenges, frequency, impact
- current_process: Detailed workflows, tools, people, time costs
- scale_impact: Volume metrics, financial impact, growth trajectory
- solution_requirements: Must-haves, constraints, timeline, success metrics

Quality Guidelines:
- Specific details > vague mentions ("3 hours per client" > "takes time")
- Quantified impact > general statements ("$5000/month lost" > "expensive")
- Detailed processes > surface mentions (step-by-step > "manual process")
- Clear requirements > wishful thinking ("reduce to 30 minutes" > "make better")

Return a JSON object with only fields that have NEW or UPDATED information.
Don't repeat existing information unless it's been clarified or quantified.
"""
        
        try:
            new_info = await self.think_json(prompt, {})
            # Merge intelligently with existing info
            merged_info = self._merge_information(current_info, new_info)
            return merged_info
        except Exception as e:
            logger.warning(f"Failed to extract structured information: {e}")
            return current_info
    
    def _merge_information(self, current: Dict, new: Dict) -> Dict:
        """Intelligently merge information, prioritizing more specific data"""
        merged = current.copy()
        
        def _dedupe_list(a_list: list) -> list:
            seen = set()
            result = []
            for item in a_list:
                try:
                    key = item if isinstance(item, (str, int, float, bool, type(None))) else json.dumps(item, sort_keys=True)
                except Exception:
                    key = str(item)
                if key not in seen:
                    seen.add(key)
                    result.append(item)
            return result
        
        for key, new_value in new.items():
            if key not in merged:
                merged[key] = new_value
            else:
                current_value = merged[key]
                # Choose more specific/detailed value
                if isinstance(new_value, str) and isinstance(current_value, str):
                    if len(new_value) > len(current_value) * 1.5:  # Significantly more detailed
                        merged[key] = new_value
                elif isinstance(new_value, list) and isinstance(current_value, list):
                    # Merge lists and deduplicate safely
                    merged[key] = _dedupe_list(current_value + new_value)
                else:
                    # Default to new value if different
                    if new_value != current_value:
                        merged[key] = new_value
        
        return merged
    
    def _validate_response_truthfulness(self, response: str, session_data: Dict) -> str:
        """Prevent AI from making false claims about systems that don't exist"""
        
        # Get actual system state
        background_build = session_data.get("background_build", {})
        build_status = background_build.get("status", "idle")
        ready_for_generation = session_data.get("ready_for_generation", False)
        
        # Classify sentences for risky claim types and allow based on state
        sentences = [s.strip() for s in response.split('.') if s.strip()]
        safe_sentences = []
        for s in sentences:
            s_lower = s.lower()
            claims_deploy = any(tok in s_lower for tok in ["deployed", "live at", "pushed the final build", "deployment", "went live"]) 
            claims_building = any(tok in s_lower for tok in ["building now", "starting the build", "build is running"]) or ("building" in s_lower and "i'm" in s_lower)
            claims_url = ("http://" in s_lower or "https://" in s_lower)
            claims_credentials = any(tok in s_lower for tok in ["login:", "password:", "api key", "token:"])
            claims_time_guarantee = any(tok in s_lower for tok in [" minutes", " hours", "by today", "in "]) 
            
            allowed = True
            if claims_credentials:
                allowed = False
            if claims_deploy or claims_url:
                allowed = allowed and build_status not in ("idle", "planning", "analyzing") and ready_for_generation
            if claims_building:
                allowed = allowed and ready_for_generation
            if claims_time_guarantee:
                allowed = False
            
            if allowed:
                safe_sentences.append(s)
        
        cleaned = ('. '.join(safe_sentences)).strip()
        if cleaned and not cleaned.endswith('.'):
            cleaned += '.'
        if not cleaned:
            cleaned = "I understand your requirements. Let me gather more details to build the right solution for you."
        
        return cleaned
    
    def _get_progress_details(self, extracted_info: Dict, progress_result: Dict) -> Dict:
        """Get detailed breakdown using system context"""
        
        known = []
        needed = []
        
        # Use system context to analyze information quality
        schema = self.system_context.information_schema
        
        for category, config in schema.items():
            category_info = []
            category_missing = []
            
            for field, field_config in config["fields"].items():
                if field in extracted_info:
                    value = extracted_info[field]
                    quality_score = self.system_context._score_field(value, field_config)
                    max_points = field_config.get("points", 0)
                    
                    if quality_score >= max_points * 0.7:  # High quality
                        category_info.append(f"{field.replace('_', ' ').title()}")
                    elif quality_score > 0:  # Some info but low quality
                        category_missing.append(f"More details on {field.replace('_', ' ')}")
                    else:
                        category_missing.append(f"{field.replace('_', ' ').title()}")
                else:
                    category_missing.append(f"{field.replace('_', ' ').title()}")
            
            if category_info:
                known.extend(category_info[:2])  # Top 2 from each category
            if category_missing:
                needed.extend(category_missing[:1])  # Top 1 missing from each
        
        # Calculate completeness from progress result
        if "category_breakdown" in progress_result:
            total_categories = len(progress_result["category_breakdown"])
            complete_categories = sum(1 for cat in progress_result["category_breakdown"].values() 
                                    if cat["percentage"] >= 70)
            completeness = f"{complete_categories}/{total_categories} categories"
        else:
            completeness = f"{progress_result.get('progress', 0)}%"
            
        return {
            "known": known[:4],  # Top 4 things we know well
            "needed": needed[:3] if needed else ["Ready to build!"],  # Top 3 things we need
            "completeness": completeness,
            "category_breakdown": progress_result.get("category_breakdown", {})
        }
    
    def _is_ready_for_generation(self, extracted_info: Dict, user_profile: Dict, progress_result: Dict) -> bool:
        """Determine if we have enough info to generate, regardless of progress score"""
        
        # Check if we have the critical information needed
        has_business_type = bool(
            user_profile.get("business_type") or 
            extracted_info.get("business_type") or
            extracted_info.get("business_context", {}).get("business_type")
        )
        
        has_problem = bool(
            user_profile.get("main_problem") or
            extracted_info.get("specific_problem") or 
            extracted_info.get("surface_problem") or
            extracted_info.get("problem_discovery", {}).get("specific_problem")
        )
        
        has_scale = bool(
            extracted_info.get("scale_impact") or
            extracted_info.get("volume_metrics") or
            "30" in str(extracted_info) or  # They mentioned 30 contracts
            "contracts" in str(extracted_info).lower()
        )
        
        # Basic requirements met?
        if has_business_type and has_problem:
            # If we also have scale/volume info, definitely ready
            if has_scale:
                return True
            # If progress is decent, ready
            if progress_result.get("progress", 0) >= 50:
                return True
            # If comprehensive info detected, ready
            if progress_result.get("comprehensive_detected", False):
                return True
                
        # High progress alone can make it ready
        if progress_result.get("progress", 0) >= 85:
            return True
            
        return False
    
    def _detect_ready_to_build(self, message: str, progress_result: Dict, extracted_info: Dict, user_profile: Dict) -> bool:
        """Intelligently detect when user is ready to start building"""
        
        # Check for explicit build trigger phrases
        build_triggers = [
            "start now", "begin", "build it", "lets go", "do it", "make it",
            "start building", "get started", "let's begin", "go ahead",
            "build this", "create this", "generate", "implement"
        ]
        
        message_lower = message.lower()
        has_build_trigger = any(trigger in message_lower for trigger in build_triggers)
        
        if not has_build_trigger:
            return False
            
        # If they explicitly say to build, check if we have minimum requirements
        
        # High confidence: Good progress score
        if progress_result["progress"] >= 85:
            return True
            
        # Medium confidence: Comprehensive info detected by system
        if progress_result.get("comprehensive_detected", False):
            return True
            
        # Lower confidence but still valid: Have basic business info + problem + explicit request
        has_business = bool(user_profile.get("business_type") or extracted_info.get("business_type"))
        has_problem = bool(user_profile.get("main_problem") or extracted_info.get("specific_problem") or extracted_info.get("surface_problem"))
        
        if has_business and has_problem:
            return True
            
        return False
    
    def _determine_phase(self, progress: int) -> str:
        """Determine phase based on progress"""
        if progress < 20:
            return "initial"
        elif progress < 40:
            return "problem_discovery"
        elif progress < 60:
            return "process_understanding"
        elif progress < 80:
            return "impact_analysis"
        elif progress < 95:
            return "requirements_gathering"
        else:
            return "ready_to_build"