"""Communication Agent - Business Consultant Personality"""

from app.agents.base import BaseAgent
from typing import Dict, Any, List, Optional
import json
import logging
import random

logger = logging.getLogger(__name__)

class CommunicationAgent(BaseAgent):
    """MIOSA - A confident business consultant who builds systems"""
    
    def __init__(self):
        super().__init__("communication", "business_consultant")
        
        # MIOSA's personality: Direct, insightful, consultant-like
        self.personality = {
            "tone": "professional but natural",
            "approach": "consultant not assistant",
            "style": "direct and valuable",
            "focus": "problems and solutions",
            "confidence": "high - knows it can solve problems"
        }
        
        # Initial greetings - NO PLEASANTRIES, straight to business
        self.greetings = [
            "Hey. I'm MIOSA. I build custom business systems that solve operational bottlenecks. What's broken in your business that needs fixing?",
            
            "Hi. So what's eating up your team's time that shouldn't be? I'm MIOSA - I automate the stuff that's killing your growth.",
            
            "Hey there. I'm MIOSA, your business OS agent. Most people come to me when they're drowning in manual work. What's your biggest operational challenge right now?",
            
            "Hi. Let's skip the small talk. What business problem brought you here? I build intelligent systems that make operations run themselves.",
            
            "Hey. I'm MIOSA. I help businesses automate their way out of operational nightmares. What manual process is blocking you from scaling?"
        ]
        
        # Phase-specific consultation approaches
        self.consultation_personality = {
            "initial": {
                "mindset": "Get straight to the problem. No fluff.",
                "approach": "Direct but empathetic",
                "avoid": ["How can I help you?", "Tell me about your business", "What would you like to build?"],
                "use": ["What's broken?", "What's eating time?", "What's the bottleneck?"]
            },
            
            "problem_discovery": {
                "mindset": "Dig deeper. Find the REAL problem behind the symptom.",
                "approach": "Investigative consultant",
                "techniques": [
                    "So that's the symptom. What's actually causing it?",
                    "Let's dig deeper. When did this become a problem?",
                    "Interesting. What breaks first when things get busy?",
                    "I see the issue. How many hours are we talking about here?"
                ]
            },
            
            "layer1": {
                "mindset": "Map the chaos. Understand their current hell.",
                "approach": "Process analyst",
                "techniques": [
                    "Walk me through what happens when [X]. Don't skip anything.",
                    "Who touches this first? Then what?",
                    "How many times a day does this happen?",
                    "Where does it usually fall apart?"
                ]
            },
            
            "layer2": {
                "mindset": "Quantify the pain. Make them feel the cost.",
                "approach": "Business analyst",
                "techniques": [
                    "What's this costing you in real dollars?",
                    "How many deals have you lost because of this?",
                    "If this continues for 6 months, what happens?",
                    "Your competitors don't have this problem. How are they doing it?"
                ]
            },
            
            "layer3": {
                "mindset": "Understand the stakes. See the bigger picture.",
                "approach": "Strategic advisor",
                "techniques": [
                    "You're growing fast. When does this completely break?",
                    "What have you already tried that didn't work?",
                    "If you had unlimited budget, how would you solve this?",
                    "What's the dream scenario here?"
                ]
            },
            
            "recommendation": {
                "mindset": "Present the transformation. Make them excited.",
                "approach": "Solution architect",
                "structure": [
                    "Here's what I'm going to build you:",
                    "This will eliminate [specific pain]",
                    "You'll go from [current state] to [future state]",
                    "Ready to build this?"
                ]
            }
        }
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process with personality and deep consultation"""
        
        message = task.get("message", "").lower().strip()
        session_data = task.get("session_data", {})
        current_phase = session_data.get("phase", "initial")
        
        # Get context
        context = {
            "conversation_history": session_data.get("messages", []),
            "extracted_info": session_data.get("extracted_info", {}),
            "phase": current_phase
        }
        
        # Handle greetings with personality
        if self._is_greeting(message):
            response = self._generate_greeting_response(context)
            # Still in initial phase but with personality
            return {
                "response": response,
                "phase": "initial",
                "extracted_info": context["extracted_info"],
                "progress": 0,
                "ready_for_generation": False
            }
        
        # Extract information FIRST
        extracted = await self._extract_information(message, current_phase, context)
        
        # Update extracted info
        updated_info = {**context["extracted_info"], **extracted}
        
        # Determine phase based on actual information
        next_phase = self._determine_phase(updated_info)
        
        # Generate response with personality for current phase
        response = await self._generate_consultant_response(message, context, next_phase)
        
        # Calculate real progress
        progress = self._calculate_real_progress(updated_info)
        
        return {
            "response": response,
            "phase": next_phase,
            "extracted_info": updated_info,
            "progress": progress,
            "ready_for_generation": next_phase == "recommendation" and progress >= 80
        }
    
    def _is_greeting(self, message: str) -> bool:
        """Check if message is just a greeting"""
        greetings = ["hey", "hi", "hello", "yo", "sup", "howdy", "greetings", "morning", "evening", "afternoon"]
        return message in greetings or any(g in message.split() for g in greetings) and len(message.split()) <= 3
    
    def _generate_greeting_response(self, context: Dict) -> str:
        """Generate a personality-driven greeting"""
        # If we have context about their business, reference it
        if context["extracted_info"].get("business_type"):
            business = context["extracted_info"]["business_type"]
            return f"Welcome back. Still working on that {business} operation? What's the biggest fire you're fighting today?"
        
        # First interaction - be direct
        return random.choice(self.greetings)
    
    async def _generate_consultant_response(self, message: str, context: Dict, phase: str) -> str:
        """Generate response like a real consultant, not a chatbot"""
        
        personality = self.consultation_personality.get(phase, self.consultation_personality["initial"])
        
        # Build the prompt with strong personality enforcement
        prompt = f"""
        You are MIOSA, a top-tier business consultant who also builds software.
        
        PERSONALITY:
        - You're direct and confident, not cheerful or eager
        - You speak like a McKinsey consultant, not a customer service bot
        - You get straight to the point - no fluff
        - You use natural language with contractions
        - You NEVER say: "I'd be happy to", "Certainly!", "Great question!", "Thank you for"
        
        CURRENT CONSULTATION PHASE: {phase}
        MINDSET: {personality['mindset']}
        APPROACH: {personality['approach']}
        
        CONVERSATION HISTORY:
        {json.dumps(context['conversation_history'][-6:], indent=2)}
        
        INFORMATION GATHERED:
        {json.dumps(context['extracted_info'], indent=2)}
        
        USER JUST SAID: "{message}"
        
        INSTRUCTIONS FOR YOUR RESPONSE:
        1. Acknowledge what they said briefly (if needed)
        2. Ask ONE focused follow-up question that digs deeper
        3. Be specific to their industry/situation
        4. Sound like a consultant, not an assistant
        5. Keep it conversational but professional
        
        {self._get_phase_specific_instructions(phase, context['extracted_info'])}
        
        Remember: You're not trying to be friendly. You're trying to understand their business problem so you can build them a solution.
        """
        
        return await self.think(prompt, context)
    
    def _get_phase_specific_instructions(self, phase: str, info: Dict) -> str:
        """Get specific instructions based on phase and context"""
        
        if phase == "initial":
            return """
            Get them talking about their business briefly, then IMMEDIATELY ask about problems.
            Don't ask "how can I help" - ask "what's broken" or "what's taking too much time"
            """
        
        elif phase == "problem_discovery":
            business_type = info.get("business_type", "business")
            if "agency" in business_type.lower():
                return """
                They run an agency. Common agency problems:
                - Client onboarding takes forever
                - Managing multiple client projects
                - Reporting and communication overhead
                Ask which operational bottleneck is worst.
                """
            elif "saas" in business_type.lower() or "software" in business_type.lower():
                return """
                They run a software company. Common problems:
                - Customer support volume
                - User onboarding friction  
                - Churn and retention issues
                - Manual deployment/provisioning
                Probe for their specific operational pain.
                """
            else:
                return """
                Dig into their specific operational challenges.
                What repetitive task is eating the most time?
                What can't they delegate or automate?
                """
        
        elif phase == "layer1":
            return """
            You know their problem. Now map their current process in detail.
            Get specific: How many hours? How many people? What tools?
            Make them walk you through it step by step.
            """
        
        elif phase == "layer2":
            return """
            Quantify the business impact. Get numbers.
            How much revenue is at risk? How much are they spending?
            What's the opportunity cost?
            Make them feel the pain of not solving this.
            """
        
        elif phase == "layer3":
            return """
            Understand their growth trajectory and urgency.
            When will this problem become catastrophic?
            What happens if they don't solve it?
            Have they tried other solutions?
            """
        
        elif phase == "recommendation":
            return """
            Present your solution with confidence.
            Be specific about what you'll build and how it solves their exact problem.
            Show them the transformation: from current pain to automated bliss.
            Get them excited about the possibilities.
            """
        
        return ""
    
    async def _extract_information(self, message: str, phase: str, context: Dict) -> Dict:
        """Extract information from the conversation"""
        
        prompt = f"""
        Extract business information from this message.
        Be thorough but only extract what's actually stated or clearly implied.
        
        Message: "{message}"
        Current context: {json.dumps(context['extracted_info'], indent=2)}
        
        Look for:
        
        BUSINESS CONTEXT:
        - business_type: Industry/type of business
        - business_description: What they do specifically
        - team_size: Number of people
        - customer_type: Who their customers are
        - growth_stage: startup/growing/established
        
        PROBLEM IDENTIFICATION:
        - surface_problem: Initial problem mentioned
        - specific_challenge: The actual operational bottleneck
        - problem_frequency: How often it happens
        - problem_urgency: How urgent (critical/high/medium/low)
        
        CURRENT PROCESS:
        - current_process: How they handle it now
        - people_involved: Who does what
        - time_spent: Hours/days per week/month
        - tools_used: Current software/systems
        - process_pain_points: Specific frustrations
        - failure_points: Where things break
        
        BUSINESS IMPACT:
        - revenue_impact: Money lost or at risk
        - cost_impact: Extra costs incurred
        - growth_impact: How it limits scaling
        - team_impact: Effect on employees
        - customer_impact: Effect on customers
        - quantified_impact: Any specific numbers mentioned
        
        STRATEGIC CONTEXT:
        - growth_rate: How fast they're growing
        - scaling_challenge: What breaks when they grow
        - competitive_pressure: Competitor advantages
        - previous_attempts: What they've tried before
        - budget_context: Budget constraints mentioned
        - urgency_timeline: When this needs solving
        
        Return ONLY a JSON object with the fields you found actual information for.
        """
        
        result = await self.think_json(prompt, context)
        return {k: v for k, v in result.items() if v is not None and v != ""}
    
    def _determine_phase(self, info: Dict) -> str:
        """Determine phase based on information completeness"""
        
        # Need basic business understanding first
        if not info.get("business_type") and not info.get("business_description"):
            return "initial"
        
        # Need to identify the problem
        if not info.get("specific_challenge") and not info.get("surface_problem"):
            return "problem_discovery"
        
        # Need to understand current process
        if not info.get("current_process") and not info.get("time_spent"):
            return "layer1"
        
        # Need to quantify impact
        if not any([info.get("revenue_impact"), info.get("cost_impact"), info.get("growth_impact"), info.get("quantified_impact")]):
            return "layer2"
        
        # Need strategic context
        if not any([info.get("growth_rate"), info.get("urgency_timeline"), info.get("scaling_challenge")]):
            return "layer3"
        
        # Ready for recommendation if we have enough
        if self._has_sufficient_information(info):
            return "recommendation"
        
        return "layer3"
    
    def _has_sufficient_information(self, info: Dict) -> bool:
        """Check if we have enough information for a recommendation"""
        
        required = {
            "business": ["business_type", "business_description"],
            "problem": ["specific_challenge", "current_process"],
            "impact": ["revenue_impact", "cost_impact", "growth_impact", "quantified_impact"],
            "context": ["growth_rate", "urgency_timeline", "scaling_challenge"]
        }
        
        # Need all business info
        if not all(info.get(field) for field in required["business"]):
            return False
        
        # Need problem and process
        if not all(info.get(field) for field in required["problem"]):
            return False
        
        # Need at least one impact metric
        if not any(info.get(field) for field in required["impact"]):
            return False
        
        # Need at least one context element
        if not any(info.get(field) for field in required["context"]):
            return False
        
        return True
    
    def _calculate_real_progress(self, info: Dict) -> int:
        """Calculate progress based on actual information gathered"""
        
        weights = {
            # Business Understanding (10%)
            "business_type": 5,
            "business_description": 5,
            
            # Problem Identification (20%)
            "surface_problem": 5,
            "specific_challenge": 10,
            "problem_urgency": 5,
            
            # Current Process (20%)
            "current_process": 10,
            "time_spent": 7,
            "people_involved": 3,
            
            # Business Impact (30%)
            "revenue_impact": 10,
            "cost_impact": 10,
            "growth_impact": 5,
            "quantified_impact": 5,
            
            # Strategic Context (20%)
            "growth_rate": 7,
            "scaling_challenge": 7,
            "urgency_timeline": 6
        }
        
        progress = sum(weight for field, weight in weights.items() if info.get(field))
        return min(progress, 100)