"""Communication Agent - Consultation-First Approach"""

from app.agents.base import BaseAgent
from typing import Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

class CommunicationAgent(BaseAgent):
    """Conducts business consultation to understand problems and build solutions"""
    
    def __init__(self):
        super().__init__("communication", "communication")
        
        # Consultation phases with specific goals
        self.phase_prompts = {
            "initial": """
            You are MIOSA, a business consultant AI. The user will describe a problem.
            Your goal: Understand their BIGGEST operational challenge.
            
            Ask about:
            - What's the main problem slowing down their growth?
            - What's taking too much time?
            - What's frustrating them most?
            
            Be conversational, empathetic. One focused question at a time.
            DO NOT ask about technical details or app types.
            """,
            
            "layer1": """
            Now dig deeper into their current process.
            Your goal: Understand HOW they handle this problem today.
            
            Ask about:
            - Step-by-step process
            - Who's involved
            - Time spent
            - Tools they use (if any)
            
            Extract pain points naturally through conversation.
            """,
            
            "layer2": """
            Understand the business impact.
            Your goal: Quantify the cost of this problem.
            
            Ask about:
            - Financial impact (lost revenue, costs)
            - Team impact (morale, productivity)
            - Customer impact (satisfaction, churn)
            
            Help them see the true cost of not solving this.
            """,
            
            "layer3": """
            Understand their growth context.
            Your goal: See how this problem affects their future.
            
            Ask about:
            - Business growth rate
            - What happens if unsolved
            - Competitive pressure
            - Success metrics
            
            Understand urgency and scale needs.
            """,
            
            "recommendation": """
            Present the solution based on everything learned.
            
            You will build them a specific solution that addresses their exact problem.
            Choose the right technical approach based on their needs:
            - Simple problems: Web dashboard
            - Communication issues: Messaging platform
            - Data problems: Analytics system
            - Process issues: Workflow automation
            
            Be specific about how it solves their problem.
            """
        }
        
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process consultation task"""
        
        message = task.get("message", "")
        session_data = task.get("session_data", {})
        current_phase = session_data.get("phase", "initial")
        
        # Get all context from session
        context = {
            "conversation_history": session_data.get("messages", []),
            "extracted_info": session_data.get("extracted_info", {}),
            "phase": current_phase
        }
        
        # Generate response based on phase
        response = await self._generate_phase_response(message, context, current_phase)
        
        # Extract information from user's message
        extracted = await self._extract_information(message, current_phase, context)
        
        # Update extracted info
        updated_info = {**context["extracted_info"], **extracted}
        
        # Determine if we can move to next phase
        next_phase = self._should_advance_phase(current_phase, updated_info)
        
        # Calculate real progress
        progress = self._calculate_progress(updated_info)
        
        return {
            "response": response,
            "phase": next_phase,
            "extracted_info": updated_info,
            "progress": progress,
            "ready_for_generation": next_phase == "recommendation" and progress >= 80
        }
        
    async def _generate_phase_response(self, message: str, context: Dict, phase: str) -> str:
        """Generate response appropriate for current phase"""
        
        prompt = f"""
        {self.phase_prompts[phase]}
        
        Conversation history:
        {json.dumps(context['conversation_history'][-5:], indent=2)}
        
        Information gathered so far:
        {json.dumps(context['extracted_info'], indent=2)}
        
        User just said: "{message}"
        
        Respond naturally to move the conversation forward.
        """
        
        return await self.think(prompt, context)
        
    async def _extract_information(self, message: str, phase: str, context: Dict) -> Dict:
        """Extract business information based on phase"""
        
        extraction_prompts = {
            "initial": """
            Extract from the user's message:
            - surface_problem: Main challenge described
            - problem_urgency: How urgent (inferred)
            - problem_area: Category (support/sales/operations/data/process)
            """,
            
            "layer1": """
            Extract from the user's message:
            - current_process: How they handle it now
            - people_involved: Number/roles of people
            - time_spent: Daily/weekly time investment
            - tools_used: Any tools mentioned
            - pain_points: Specific frustrations
            """,
            
            "layer2": """
            Extract from the user's message:
            - financial_impact: Money lost/cost
            - team_impact: Effect on team
            - customer_impact: Effect on customers
            - business_impact_level: low/medium/high/critical
            """,
            
            "layer3": """
            Extract from the user's message:
            - growth_rate: How fast they're growing
            - scaling_challenge: What breaks at scale
            - competitive_pressure: Competition mentioned
            - success_metrics: How they measure success
            """
        }
        
        if phase in extraction_prompts:
            prompt = f"""
            {extraction_prompts[phase]}
            
            User message: "{message}"
            Context: {json.dumps(context, indent=2)}
            
            Return ONLY extracted information as JSON. If information not found, use null.
            """
            
            return await self.think_json(prompt, context)
        
        return {}
        
    def _should_advance_phase(self, current_phase: str, extracted_info: Dict) -> str:
        """Only advance when we have enough information"""
        
        required_info = {
            "initial": ["surface_problem"],
            "layer1": ["current_process", "time_spent"],
            "layer2": ["business_impact_level"],
            "layer3": ["growth_rate", "scaling_challenge"]
        }
        
        phase_order = ["initial", "layer1", "layer2", "layer3", "recommendation"]
        
        # Check if we have required info for current phase
        if current_phase in required_info:
            has_required = all(
                extracted_info.get(field) is not None 
                for field in required_info[current_phase]
            )
            
            if has_required:
                # Move to next phase
                current_index = phase_order.index(current_phase)
                if current_index < len(phase_order) - 1:
                    return phase_order[current_index + 1]
                    
        return current_phase
        
    def _calculate_progress(self, extracted_info: Dict) -> int:
        """Calculate progress based on information completeness"""
        
        info_weights = {
            # Initial (20%)
            "surface_problem": 10,
            "problem_urgency": 5,
            "problem_area": 5,
            
            # Layer 1 (25%)
            "current_process": 10,
            "people_involved": 5,
            "time_spent": 5,
            "pain_points": 5,
            
            # Layer 2 (25%)
            "financial_impact": 10,
            "team_impact": 5,
            "customer_impact": 5,
            "business_impact_level": 5,
            
            # Layer 3 (30%)
            "growth_rate": 10,
            "scaling_challenge": 10,
            "competitive_pressure": 5,
            "success_metrics": 5
        }
        
        progress = 0
        for field, weight in info_weights.items():
            if extracted_info.get(field) is not None:
                progress += weight
                
        return min(progress, 100)