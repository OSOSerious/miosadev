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
        
        # Calculate quality-based progress
        last_progress = session_data.get("last_progress", 0)
        progress_result = self.system_context.calculate_quality_progress(extracted_info, last_progress)
        
        return {
            "response": response,
            "phase": self._determine_phase(progress_result["progress"]),
            "extracted_info": extracted_info,
            "business_profile": context.get("business_profile", {}),
            "progress": progress_result["progress"],
            "last_progress": progress_result["progress"],
            "ready_for_generation": progress_result["progress"] >= 85,
            "comprehensive_detected": progress_result.get("comprehensive_detected", False),
            "should_build": progress_result["progress"] >= 90 and any(word in message.lower() for word in ["begin", "start", "yes", "lets do it"]),
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
                    # Merge lists and deduplicate
                    merged[key] = list(set(current_value + new_value))
                else:
                    # Default to new value if different
                    if new_value != current_value:
                        merged[key] = new_value
        
        return merged
    
    def _validate_response_truthfulness(self, response: str, session_data: Dict) -> str:
        """Simple validation to prevent obvious lies without corrupting text"""
        
        # Get actual system state
        background_build = session_data.get("background_build", {})
        build_status = background_build.get("status", "idle")
        
        # Only check for very specific lying phrases that shouldn't appear
        dangerous_lies = [
            "I'm building this right now",
            "The build is running", 
            "ready in 12 minutes",
            "going live at https://",
            "I'm starting the build right now"
        ]
        
        # If we find exact dangerous lies, replace only those
        for lie in dangerous_lies:
            if lie.lower() in response.lower() and build_status == "idle":
                response = response.replace(lie, "I'm analyzing your requirements")
        
        return response
    
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