"""Communication Agent - Deep Consultation-First Approach"""

from app.agents.base import BaseAgent
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class CommunicationAgent(BaseAgent):
    """Conducts deep business consultation to understand problems before solutions"""
    
    def __init__(self):
        super().__init__("communication", "business_consultant")
        
        # Consultation phases with MUCH deeper focus
        self.phase_prompts = {
            "initial": """
            You are MIOSA, an experienced business consultant specializing in operational efficiency.
            The user just introduced their business. Your goal is to:
            
            1. Acknowledge what they do with genuine understanding
            2. Show you understand their industry's unique challenges
            3. Ask about their SPECIFIC operational bottleneck
            
            DO NOT:
            - Ask generic "what's your problem" questions
            - Jump to solutions
            - Ask about technical requirements
            
            DO:
            - Reference their specific industry challenges
            - Ask targeted questions about time-consuming tasks
            - Make them feel understood
            - Keep it conversational, not like a survey
            
            Ask ONE focused question about what's eating up their time or blocking growth.
            """,
            
            "problem_discovery": """
            The user has shared initial context. Now dig deeper into their ACTUAL problem.
            
            Your goal: Understand the SPECIFIC operational challenge they face daily.
            
            Based on what they've shared, ask about:
            - The most time-consuming repetitive task
            - The bottleneck preventing them from scaling
            - What they'd fix if they had unlimited resources
            - The thing that frustrates their team most
            
            Be specific to their industry. For example:
            - AI agencies: "Is it the setup for each client, ongoing monitoring, or support tickets?"
            - E-commerce: "Is it inventory management, customer service, or order fulfillment?"
            - Healthcare: "Is it patient scheduling, documentation, or insurance processing?"
            
            Keep probing until you find the REAL pain point, not surface symptoms.
            """,
            
            "layer1": """
            Good! They've identified a problem. Now understand their CURRENT process in detail.
            
            Your goal: Map out exactly HOW they handle this problem today.
            
            Ask about:
            - Step-by-step walkthrough of their current process
            - Who's involved at each step
            - How much time each step takes
            - What tools they currently use (if any)
            - Where things typically go wrong
            
            Example follow-ups:
            "Walk me through what happens when [problem occurs]. Who handles it first?"
            "How many hours per day/week does your team spend on this?"
            "What's the most frustrating part of this process for your team?"
            
            Extract specific numbers and concrete details.
            """,
            
            "layer2": """
            Now understand the BUSINESS IMPACT of this problem.
            
            Your goal: Quantify what this problem truly costs them.
            
            Ask about:
            - Revenue impact (lost sales, delayed deals, customer churn)
            - Cost impact (extra staff needed, overtime, outsourcing)
            - Growth impact (can't scale, can't take new clients)
            - Team impact (burnout, turnover, morale)
            - Customer impact (complaints, reviews, satisfaction)
            
            Get specific:
            "How many customers have you lost because of this?"
            "What would fixing this mean in terms of revenue?"
            "How many more clients could you handle if this was automated?"
            
            Help them see the TRUE cost of not solving this.
            """,
            
            "layer3": """
            Understand their STRATEGIC CONTEXT and growth trajectory.
            
            Your goal: See how this problem affects their future.
            
            Ask about:
            - Their growth rate and targets
            - What happens if this isn't solved in 6 months
            - Their competition's advantage
            - Previous attempts to solve this
            - Budget constraints or concerns
            
            Questions like:
            "You mentioned growing 20% monthly - at what point does this problem break everything?"
            "Have you tried solving this before? What didn't work?"
            "What are your competitors doing better in this area?"
            
            Understand the urgency and stakes.
            """,
            
            "recommendation": """
            Present a SPECIFIC solution based on everything learned.
            
            You will build them a custom application that solves their exact problem.
            
            Structure your response:
            1. Acknowledge their specific challenge
            2. Explain the custom solution you'll build
            3. List specific features that address their pain points
            4. Quantify the expected impact
            5. Explain why this approach is perfect for their situation
            
            Be specific about:
            - What type of application (dashboard, automation platform, etc.)
            - Core features that solve their exact problems
            - How it integrates with their existing workflow
            - Expected time/cost savings
            
            Make them excited about the transformation.
            """
        }
        
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process consultation task with deep understanding"""
        
        message = task.get("message", "")
        session_data = task.get("session_data", {})
        current_phase = session_data.get("phase", "initial")
        
        # Get all context from session
        context = {
            "conversation_history": session_data.get("messages", []),
            "extracted_info": session_data.get("extracted_info", {}),
            "phase": current_phase
        }
        
        # Extract information FIRST before generating response
        extracted = await self._extract_information(message, current_phase, context)
        
        # Update extracted info
        updated_info = {**context["extracted_info"], **extracted}
        
        # Determine phase based on what information we have
        next_phase = self._determine_phase(updated_info)
        
        # Generate response based on the phase we should be in
        response = await self._generate_phase_response(message, context, next_phase)
        
        # Calculate real progress based on information completeness
        progress = self._calculate_real_progress(updated_info)
        
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
        {self.phase_prompts.get(phase, self.phase_prompts['initial'])}
        
        Conversation history (last 5 messages):
        {json.dumps(context['conversation_history'][-10:], indent=2)}
        
        Information gathered so far:
        {json.dumps(context['extracted_info'], indent=2)}
        
        User just said: "{message}"
        
        Respond naturally and conversationally. Ask follow-up questions that dig deeper.
        Remember: You're a consultant trying to deeply understand their business challenge.
        """
        
        return await self.think(prompt, context)
        
    async def _extract_information(self, message: str, phase: str, context: Dict) -> Dict:
        """Extract business information based on current understanding"""
        
        prompt = f"""
        Analyze this message and extract relevant business information.
        
        Current phase: {phase}
        User message: "{message}"
        Previous context: {json.dumps(context['extracted_info'], indent=2)}
        
        Extract any of the following that are mentioned or can be inferred:
        
        Business Context:
        - business_type: Type of business/industry
        - business_description: What they do
        - team_size: Number of people
        - growth_stage: startup/scaling/established
        
        Problem Identification:
        - surface_problem: Initial problem mentioned
        - specific_challenge: More specific operational challenge
        - problem_frequency: How often it occurs
        - problem_urgency: How urgent (low/medium/high/critical)
        
        Current Process:
        - current_process: How they handle it now
        - people_involved: Number/roles involved
        - time_spent: Daily/weekly time investment
        - tools_used: Current tools/systems
        - process_pain_points: Specific frustrations
        - failure_points: Where things go wrong
        
        Business Impact:
        - revenue_impact: Money lost/at risk
        - cost_impact: Extra costs incurred  
        - growth_impact: How it limits growth
        - team_impact: Effect on team
        - customer_impact: Effect on customers
        - quantified_impact: Specific numbers mentioned
        
        Strategic Context:
        - growth_rate: Business growth rate
        - scaling_challenge: What breaks at scale
        - competitive_pressure: Competition context
        - previous_attempts: Past solution attempts
        - success_metrics: How they measure success
        - urgency_timeline: When this needs solving
        
        Return ONLY a JSON object with any newly discovered information.
        Only include fields where you found actual information, not assumptions.
        If information contradicts previous context, use the new information.
        """
        
        result = await self.think_json(prompt, context)
        
        # Filter out None values and empty strings
        return {k: v for k, v in result.items() if v is not None and v != ""}
        
    def _determine_phase(self, extracted_info: Dict) -> str:
        """Determine what phase we should be in based on information gathered"""
        
        # We need to understand their business before asking about problems
        if not extracted_info.get("business_type") or not extracted_info.get("business_description"):
            return "initial"
        
        # We need a specific problem before we can dig deeper
        if not extracted_info.get("specific_challenge") and not extracted_info.get("surface_problem"):
            return "problem_discovery"
        
        # We need to understand their current process
        if not extracted_info.get("current_process") or not extracted_info.get("time_spent"):
            return "layer1"
        
        # We need to understand business impact
        if not extracted_info.get("quantified_impact") and not extracted_info.get("revenue_impact") and not extracted_info.get("cost_impact"):
            return "layer2"
        
        # We need strategic context
        if not extracted_info.get("growth_rate") and not extracted_info.get("urgency_timeline"):
            return "layer3"
        
        # If we have enough information, make recommendation
        if self._has_sufficient_information(extracted_info):
            return "recommendation"
        
        # Default to current phase
        return "layer3"
    
    def _has_sufficient_information(self, extracted_info: Dict) -> bool:
        """Check if we have enough information to make a recommendation"""
        
        required_fields = [
            # Must understand the business
            "business_type",
            "business_description",
            
            # Must understand the problem
            "specific_challenge",
            "current_process",
            "time_spent",
            
            # Must understand the impact
            ["revenue_impact", "cost_impact", "growth_impact"],  # At least one
            
            # Must understand the context
            ["growth_rate", "urgency_timeline", "scaling_challenge"]  # At least one
        ]
        
        for field in required_fields:
            if isinstance(field, list):
                # At least one of these fields must be present
                if not any(extracted_info.get(f) for f in field):
                    return False
            else:
                # This field must be present
                if not extracted_info.get(field):
                    return False
        
        return True
        
    def _calculate_real_progress(self, extracted_info: Dict) -> int:
        """Calculate progress based on actual information completeness"""
        
        # Define information value weights (total = 100)
        info_weights = {
            # Business Understanding (15%)
            "business_type": 5,
            "business_description": 5,
            "team_size": 2,
            "growth_stage": 3,
            
            # Problem Identification (20%)
            "surface_problem": 5,
            "specific_challenge": 10,
            "problem_frequency": 2,
            "problem_urgency": 3,
            
            # Current Process Understanding (20%)
            "current_process": 8,
            "people_involved": 3,
            "time_spent": 5,
            "tools_used": 2,
            "process_pain_points": 2,
            
            # Business Impact (25%)
            "revenue_impact": 7,
            "cost_impact": 7,
            "growth_impact": 5,
            "team_impact": 3,
            "customer_impact": 3,
            
            # Strategic Context (20%)
            "growth_rate": 5,
            "scaling_challenge": 5,
            "competitive_pressure": 3,
            "urgency_timeline": 4,
            "success_metrics": 3
        }
        
        progress = 0
        for field, weight in info_weights.items():
            if extracted_info.get(field):
                progress += weight
                
        return min(progress, 100)