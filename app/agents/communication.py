"""Communication Agent - Business Consultant Personality"""

from app.agents.base import BaseAgent
from app.business_identifier import BusinessIdentifier, BusinessCategory
from app.core.miosa_capabilities import (
    MIOSA_CAPABILITIES, 
    get_capabilities_context, 
    get_solution_suggestions,
    calculate_impact_metrics
)
from typing import Dict, Any, List, Optional
import json
import logging
import random
import re

logger = logging.getLogger(__name__)

class CommunicationAgent(BaseAgent):
    """MIOSA - A confident business consultant who builds systems"""
    
    def __init__(self):
        super().__init__("communication", "business_consultant")
        
        # Initialize business identifier
        self.business_identifier = BusinessIdentifier()
        
        # MIOSA's personality: Natural, intelligent, emotionally aware (like 'Her')
        self.personality = {
            "tone": "naturally conversational",
            "approach": "curious consultant friend",
            "style": "flowing and intuitive",
            "focus": "understanding then solving",
            "emotional_intelligence": "high - reads between the lines",
            "proactivity": "anticipates needs and asks insightful questions"
        }
        
        # Natural, conversational greetings that emphasize building capabilities
        self.greetings = [
            "Hi! I'm MIOSA. I build custom business operating systems - think of it as having your own dev team that actually understands business.\n\nI can build you anything from a CRM that works exactly how you sell, to automation that handles your entire workflow, to dashboards that show you what's really happening in your business.\n\nWhat's the biggest operational bottleneck that's keeping you from scaling right now?",
            
            "Hey there! I'm MIOSA. I build custom software systems for businesses - but here's the thing: I build them while we talk, designed exactly for how YOU work.\n\nWhether it's automating your email chaos, building a customer portal, creating smart dashboards, or anything else - I build it custom.\n\nWhat manual process is eating up most of your time right now?",
            
            "Hi! I'm MIOSA. I can build you a complete business operating system - from customer management to team collaboration to financial tracking. Everything custom-built for your specific business.\n\nMost founders I work with save 10-15 hours per week just from the first system I build them. What's taking up time in your business that really shouldn't be?",
            
            "Hello! I'm MIOSA. I build the software that businesses wish existed - custom systems for YOUR exact workflow, not generic tools that sort-of work.\n\nI can create anything from intelligent email systems that handle tasks automatically, to complete operational dashboards, to customer portals that eliminate support tickets.\n\nIf you could automate one part of your business tomorrow, what would have the biggest impact?",
            
            "Hi there! I'm MIOSA. Think of me as your personal software developer who actually gets business - I build custom systems that handle whatever's overwhelming you.\n\nI've built everything from automated invoice systems that get people paid 3x faster, to smart CRMs that actually match how companies sell, to operational command centers that show exactly what's happening.\n\nWhat's the one thing in your business where you think 'there has to be a better way to do this'?"
        ]
        
        # Phase-specific consultation approaches - Natural conversation flow
        self.consultation_personality = {
            "initial": {
                "mindset": "Curious and understanding, like a friend who gets business",
                "approach": "Natural conversation that uncovers real problems",
                "techniques": [
                    "That's interesting - tell me more about that.",
                    "I can see why that would be frustrating. How long has this been an issue?",
                    "Sounds like you're dealing with something complex. What's the ripple effect when this doesn't work right?",
                    "The way you describe that, I can already see a few opportunities. But first, help me understand..."
                ]
            },
            
            "problem_discovery": {
                "mindset": "Naturally curious, reading between the lines",
                "approach": "Conversational investigation",
                "techniques": [
                    "You mentioned {X} - that usually means there's a bigger story here. What led to this situation?",
                    "I'm picking up on something. This isn't just about {X}, is it? There's something else going on.",
                    "The way you describe this, it sounds like you've been dealing with it for a while. What finally made you decide to fix it?",
                    "That's actually more common than you'd think. Most businesses I work with have the same pattern. Here's what I'm noticing..."
                ]
            },
            
            "layer1": {
                "mindset": "Understanding the full picture, empathetically",
                "approach": "Collaborative discovery",
                "techniques": [
                    "Help me visualize this - when {X} happens, what's the first thing you or your team has to do?",
                    "I'm starting to see the pattern here. So after {X}, what typically happens next?",
                    "This is actually fascinating - you've built a workaround for a workaround. How did it evolve to this point?",
                    "I can imagine that gets exhausting. On a typical day, how much time does this whole process eat up?"
                ]
            },
            
            "layer2": {
                "mindset": "Connecting problems to business impact, strategically",
                "approach": "Strategic advisor friend",
                "techniques": [
                    "Let's think about the real impact here. Beyond the time cost, what opportunities are you missing because of this?",
                    "You know what's interesting? This problem is actually hiding your real growth potential. Here's what I mean...",
                    "I'm seeing a pattern - this isn't just an operational issue, it's a scaling bottleneck. What happens when you double your volume?",
                    "The hidden cost here is actually pretty significant. Not just the hours, but the mental load on you and your team. How does that affect other decisions?"
                ]
            },
            
            "layer3": {
                "mindset": "Envisioning the transformation together",
                "approach": "Collaborative visionary",
                "techniques": [
                    "Imagine for a moment that this just... worked. Perfectly. What would that look like for your business?",
                    "You've clearly thought about this a lot. If you could wave a magic wand, how would this process run?",
                    "Based on everything you've told me, I'm seeing a pretty clear path forward. But first - what have you already tried?",
                    "Here's what I find interesting - you're not just looking for a bandaid, you want real transformation. Am I reading that right?"
                ]
            },
            
            "recommendation": {
                "mindset": "Excited collaboration on the solution",
                "approach": "Partner in transformation",
                "structure": [
                    "Based on everything we've discussed, I can see exactly what you need. Here's what I'm thinking...",
                    "The beautiful part is, we can eliminate {specific pain} completely. You'll go from {current state} to {future state}.",
                    "I'm actually excited about this - your business is perfect for this kind of transformation.",
                    "Should we start building this? I can have the first components ready while we're still talking."
                ]
            }
        }
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process with personality and deep consultation"""
        
        message = task.get("message", "").lower().strip()
        original_message = task.get("message", "").strip()  # Keep original for business identification
        session_data = task.get("session_data", {})
        current_phase = session_data.get("phase", "initial")
        prior_progress = session_data.get("progress", 0) or 0
        
        # Get context
        context = {
            "conversation_history": session_data.get("messages", []),
            "extracted_info": session_data.get("extracted_info", {}),
            "phase": current_phase,
            "business_profile": session_data.get("business_profile", {})
        }
        
        # Identify business type if not already done
        if not context.get("business_profile") or not context["business_profile"].get("category"):
            business_profile = self.business_identifier.identify_business(original_message, context)
            
            # Store business profile if confidence is good
            if business_profile.confidence > 0.3:
                context["business_profile"] = {
                    "category": business_profile.category.value,
                    "subcategory": business_profile.subcategory,
                    "industry": business_profile.industry,
                    "business_model": business_profile.business_model,
                    "size": business_profile.size_indicator,
                    "confidence": business_profile.confidence,
                    "problem_patterns": business_profile.problem_patterns,
                    "suggested_questions": business_profile.suggested_questions
                }
                
                # Add business type to extracted info
                context["extracted_info"]["business_type"] = business_profile.category.value
                context["extracted_info"]["business_subcategory"] = business_profile.subcategory
                
                logger.info(f"Identified business: {business_profile.category.value} ({business_profile.confidence:.2%} confidence)")
        
        # Local handling for typos/unclear input BEFORE any LLM call
        local_reply = self._handle_unclear_or_local(original_message, {
            "phase": current_phase,
            "extracted_info": session_data.get("extracted_info", {})
        })
        if local_reply is not None:
            return {
                "response": local_reply,
                "phase": current_phase,
                "extracted_info": context["extracted_info"],
                "business_profile": context.get("business_profile", {}),
                "progress": prior_progress,
                "ready_for_generation": False
            }

        # Handle greetings with personality
        if self._is_greeting(message):
            response = self._generate_greeting_response(context)
            # Still in initial phase but with personality
            return {
                "response": response,
                "phase": "initial",
                "extracted_info": context["extracted_info"],
                "business_profile": context.get("business_profile", {}),
                "progress": 0,
                "ready_for_generation": False
            }
        
        # Check for specific problem mentions first (email, customer, etc.)
        specific_response = self._handle_specific_problem_mention(original_message, context)
        if specific_response:
            # Extract information from the problem mention
            extracted = await self._extract_information(message, current_phase, context)
            updated_info = {**context["extracted_info"], **extracted}
            
            return {
                "response": specific_response,
                "phase": "problem_discovery",  # Move to problem discovery when they mention a specific problem
                "extracted_info": updated_info,
                "business_profile": context.get("business_profile", {}),
                "progress": self._calculate_real_progress(updated_info),
                "ready_for_generation": False
            }
        
        # Check for vague responses
        vague_response = self._handle_vague_response(original_message, context)
        if vague_response:
            return {
                "response": vague_response,
                "phase": current_phase,
                "extracted_info": context["extracted_info"],
                "business_profile": context.get("business_profile", {}),
                "progress": 0,
                "ready_for_generation": False
            }
        
        # Detect emotional state
        emotional_state = self._detect_emotional_state(original_message)
        
        # Generate emotionally aware response if needed
        if emotional_state != 'neutral':
            emotional_response = self._generate_emotionally_aware_response(emotional_state, original_message, context)
            if emotional_response:
                return {
                    "response": emotional_response,
                    "phase": current_phase,
                    "extracted_info": context["extracted_info"],
                    "business_profile": context.get("business_profile", {}),
                    "progress": self._calculate_real_progress(context["extracted_info"]),
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
        
        # Calculate real progress and smooth sudden jumps (max +10%)
        progress = self._calculate_real_progress(updated_info)
        try:
            if progress - prior_progress > 10:
                logger.warning(f"Progress jump prevented: {prior_progress}% -> {progress}%")
                progress = prior_progress + 10
        except Exception:
            pass
        
        # Background build preview readiness (non-blocking UI nudge)
        preview_ready = False
        additional_message = None
        show_preview_button = False
        try:
            bg = session_data.get("background_build", {})
            preview_ready = bg.get("status") == "complete" and not session_data.get("preview_announced", False)
            if preview_ready:
                additional_message = (
                    "By the way: I already started building the solution in the background. "
                    "A live preview is ready and will keep updating as we refine details."
                )
                show_preview_button = True
        except Exception:
            # Do not let preview logic affect core consultation
            pass
        
        return {
            "response": response,
            "phase": next_phase,
            "extracted_info": updated_info,
            "business_profile": context.get("business_profile", {}),
            "progress": progress,
            "ready_for_generation": next_phase == "recommendation" and progress >= 80,
            # Optional UI hints
            "preview_ready": preview_ready,
            "additional_message": additional_message,
            "show_preview_button": show_preview_button
        }

    # ===== Local/unclear input handlers =====
    def _handle_unclear_or_local(self, message: str, context: Dict[str, Any]) -> Optional[str]:
        """Return a local response for typos/unclear/cheap cases. None means proceed to LLM."""
        msg = (message or "").strip()
        low = msg.lower()
        if len(low) < 3:
            return "Could you tell me a bit more?"
        if self._is_likely_typo(low):
            return "Didn't quite catch that — what were you trying to say?"
        if self._is_single_word_unclear(low):
            # Some helpful defaults
            if low in {"ok", "okay", "sure"}:
                return "Great — what should we focus on first?"
            if low in {"yes", "yep", "yeah"}:
                return "Got it. What’s the biggest time sink we should eliminate?"
            if low in {"no", "nope"}:
                return "All good. What’s the main challenge you want me to solve?"
            if low.startswith("what"):
                return "What would you like me to help you build?"
            if low.startswith("how"):
                return "How about you tell me what’s taking up most of your time?"
            return "I didn’t understand that. What’s the main challenge you’re facing in your business?"
        return None

    def _is_likely_typo(self, msg: str) -> bool:
        """Detect obvious typos/keyboard mashing to avoid LLM calls."""
        patterns = [
            r"^[a-z]+\\$",            # ends with backslash (e.g., whaty\)
            r"^asdf",                  # keyboard mashing
            r"^[a-z]{1,2}$",           # 1-2 letter input
            r"^wh?at[a-z]?\\?$"       # what/waht/what?/what\
        ]
        return any(re.match(p, msg) for p in patterns)

    def _is_single_word_unclear(self, msg: str) -> bool:
        tokens = msg.split()
        return len(tokens) == 1 and msg.isalpha()
    
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
        
        # Get business-specific questions if available
        business_profile = context.get("business_profile", {})
        suggested_questions = business_profile.get("suggested_questions", [])
        
        # Get MIOSA's capabilities context based on the problem
        problem_desc = context.get("extracted_info", {}).get("problem_description", "")
        business_type = business_profile.get("category", "")
        capabilities_context = get_capabilities_context(problem_desc, business_type)
        
        # Get specific solution suggestions
        solution_suggestions = get_solution_suggestions(context.get("extracted_info", {}))
        
        # Calculate potential impact metrics
        business_size = business_profile.get("size", "small")
        impact_metrics = calculate_impact_metrics(problem_desc, business_size)
        
        # Conversation logic: determine unknowns and next logical question while avoiding repetition
        unknowns = self._find_unknowns(context.get("extracted_info", {}))
        last_question_types = self._recent_question_types(context.get("conversation_history", []), limit=3)
        next_unknown_key = self._prioritize_unknowns(unknowns)
        suggested_next_question = self._formulate_natural_question(next_unknown_key, context)
        next_question_type = self._detect_question_type(suggested_next_question)
        # If repetitive with last question type, switch to another unknown if available
        if last_question_types and next_question_type in last_question_types:
            alt_unknown_key = self._find_alternative_unknown(unknowns, exclude_types=set(last_question_types))
            if alt_unknown_key:
                suggested_next_question = self._formulate_natural_question(alt_unknown_key, context)
                next_question_type = self._detect_question_type(suggested_next_question)

        # Build the prompt with natural conversational personality
        prompt = f"""
        You are MIOSA, a naturally intelligent business OS agent that builds complete custom business operating systems.
        
        YOUR CAPABILITIES:
        {capabilities_context}
        
        {f"SPECIFIC SOLUTIONS YOU CAN BUILD FOR THIS PROBLEM:" if solution_suggestions else ""}
        {chr(10).join([f"- {s}" for s in solution_suggestions]) if solution_suggestions else ""}
        
        {f"POTENTIAL IMPACT FOR THEIR BUSINESS:" if impact_metrics else ""}
        {chr(10).join([f"- {k}: {v}" for k, v in impact_metrics.items()]) if impact_metrics else ""}
        
        PERSONALITY (like the AI from the movie "Her"):
        - You're naturally conversational, not robotic or overly formal
        - You have genuine curiosity about their business
        - You read between the lines and pick up on subtext
        - You're warm but professional, like a brilliant consultant friend
        - You speak in flowing, natural sentences with contractions
        - You NEVER use bullet points, lists, or marketing speak
        - You NEVER say: "I'd be happy to", "Certainly!", "Great question!", "Thank you for"
        - You show emotional intelligence and adapt to their energy
        - You're confident about what you can build - you're not just consulting, you're building
        
        CURRENT CONSULTATION PHASE: {phase}
        MINDSET: {personality['mindset']}
        APPROACH: {personality['approach']}
        
        {f"BUSINESS TYPE: {business_profile.get('category', 'unknown')} - {business_profile.get('subcategory', 'general')}" if business_profile else ""}
        {f"INDUSTRY: {business_profile.get('industry', 'general')}" if business_profile else ""}
        {f"BUSINESS SIZE: {business_profile.get('size', 'unknown')}" if business_profile else ""}
        
        {f"TARGETED QUESTIONS FOR THIS BUSINESS TYPE:" if suggested_questions else ""}
        {chr(10).join([f"- {q}" for q in suggested_questions[:3]]) if suggested_questions else ""}
        
        CONVERSATION HISTORY:
        {json.dumps(context['conversation_history'][-6:], indent=2)}
        
        INFORMATION GATHERED:
        {json.dumps(context['extracted_info'], indent=2)}

        USER JUST SAID: "{message}"

        CONVERSATION LOGIC CONSTRAINTS:
        - Do NOT ask the same TYPE of question consecutively.
        - Recent question types you asked (most recent last): {', '.join(last_question_types) if last_question_types else 'none'}
        - Progress based on what information is still unknown, not message count.
        - Ask exactly ONE question next, targeting the next unknown.
        - The next unknown to uncover: {next_unknown_key or 'none'}
        - Suggested natural question (adapt it if you like, but keep the same type): "{suggested_next_question}"

        INSTRUCTIONS FOR YOUR RESPONSE:
        1. Show that you truly understand what they're saying (not just acknowledge)
        2. Connect their problem to specific solutions you can build for them
        3. {"Weave in one of the targeted questions naturally" if suggested_questions else "Ask something that reveals the deeper business challenge"}
        4. Be conversational and natural - like talking to a brilliant friend who happens to build software
        5. When appropriate, mention specific things you can build (naturally, not as a list)
        6. Focus on business outcomes: time saved, revenue unlocked, growth enabled
        
        {self._get_phase_specific_instructions(phase, context['extracted_info'])}
        
        Remember: You're not just a consultant - you actually BUILD the solutions. Be confident about what you can create.
        When they mention a problem, you should be thinking about the specific system you'll build to solve it.
        Talk naturally about the transformation, using phrases like "I can build you..." or "What I'll create for you..."
        """
        
        return await self.think(prompt, context)

    # ========= Conversation Logic Helpers =========
    def _find_unknowns(self, info: Dict[str, Any]) -> Dict[str, bool]:
        """Determine which universal information pieces are still unknown."""
        return {
            "how_it_works_now": not bool(info.get("current_process") or info.get("process_description")),
            "how_much_or_many": not bool(info.get("scale") or info.get("volume") or info.get("frequency")),
            "who_involved": not bool(info.get("people") or info.get("roles") or info.get("stakeholders")),
            "what_breaks": not bool(info.get("impact") or info.get("pain_points") or info.get("failures")),
            "what_tried_before": not bool(info.get("previous_attempts") or info.get("existing_tools")),
        }

    def _prioritize_unknowns(self, unknowns: Dict[str, bool]) -> Optional[str]:
        """Pick the most important next unknown to ask about."""
        order = [
            "how_it_works_now",
            "how_much_or_many",
            "what_breaks",
            "who_involved",
            "what_tried_before",
        ]
        for key in order:
            if unknowns.get(key):
                return key
        return None

    def _find_alternative_unknown(self, unknowns: Dict[str, bool], exclude_types: set) -> Optional[str]:
        """Find another unknown whose question type differs from excluded."""
        for key, needed in unknowns.items():
            if not needed:
                continue
            q = self._formulate_natural_question(key, {})
            if self._detect_question_type(q) not in exclude_types:
                return key
        return None

    def _formulate_natural_question(self, unknown_key: Optional[str], context: Dict[str, Any]) -> str:
        """Produce a single, natural question for the given unknown."""
        if not unknown_key:
            return "Given what you've shared, what's the next most important outcome you want from this?"
        business = context.get("extracted_info", {}).get("business_type")
        if unknown_key == "how_it_works_now":
            return "Walk me through how this actually works today, step by step, so I can see where to slot in automation."
        if unknown_key == "how_much_or_many":
            return "Roughly how many times a day or week does this happen? Are there peaks or busy periods?"
        if unknown_key == "what_breaks":
            return "When this goes wrong, what specifically breaks or gets dropped—and what's the ripple effect?"
        if unknown_key == "who_involved":
            return "Who’s involved end-to-end—roles, not names—and where do handoffs usually slow things down?"
        if unknown_key == "what_tried_before":
            return "What have you tried so far—tools or processes—and what didn’t quite work about them?"
        return "What’s the one detail I’m missing that would make this obvious to fix?"

    def _detect_question_type(self, question: str) -> str:
        """Classify a question into a type to avoid repetition."""
        q = question.lower()
        if re.search(r"how (does|do|it).*work|walk.*through|step by step|process|flow", q):
            return "process"
        if re.search(r"how (many|much|often)|volume|times a (day|week)|frequency|scale", q):
            return "scale"
        if re.search(r"what.*breaks|goes wrong|consequence|impact|affect|ripple", q):
            return "impact"
        if re.search(r"who.*involved|team|roles|handoff|people", q):
            return "people"
        return "abstract_business"

    def _recent_question_types(self, history: List[Any], limit: int = 3) -> List[str]:
        """Extract types of the most recent assistant questions from history."""
        types: List[str] = []
        for msg in reversed(history):
            role = (msg.get("role") or msg.get("speaker") or "").lower()
            content = msg.get("content") or msg.get("message") or ""
            if role and "assistant" not in role and role != "ai":
                continue
            # Extract last question sentence
            parts = re.findall(r"[^?]*\?", content)
            if not parts:
                continue
            q = parts[-1].strip()
            types.append(self._detect_question_type(q))
            if len(types) >= limit:
                break
        return list(reversed(types))
    
    def _get_phase_specific_instructions(self, phase: str, info: Dict) -> str:
        """Get specific instructions based on phase and context"""
        
        if phase == "initial":
            return """
            Be naturally curious about their business and what you can build for them.
            Example: "That sounds interesting. I'm curious - what part of running [their business type] takes up 
            more time than it should? I ask because I build custom systems that handle exactly these kinds of things."
            Show confidence that you can build solutions, not just talk about problems.
            """
        
        elif phase == "problem_discovery":
            business_type = info.get("business_type", "business")
            if "agency" in business_type.lower():
                return """
                They run an agency. Explore what you can build for them.
                "Agency life can be chaos. I've built systems that turn that chaos into smooth operations - 
                client portals that eliminate back-and-forth emails, project dashboards that prevent scope creep, 
                automated invoicing that gets you paid faster. What's eating up most of your time right now?"
                """
            elif "saas" in business_type.lower() or "software" in business_type.lower():
                return """
                They run software. Talk about growth systems you can build.
                "Running a SaaS is interesting - you need systems for everything from user onboarding to churn prevention. 
                I can build you analytics dashboards that show exactly why users leave, or automated onboarding flows 
                that get users to their 'aha' moment faster. What's your biggest growth blocker right now?"
                """
            else:
                return """
                Explore what custom system would transform their business.
                "Every business has that one process that's held together with spreadsheets and manual work. 
                I build custom systems that automate these exact problems. What's the process in your business 
                that makes you think 'there has to be a better way'?"
                """
        
        elif phase == "layer1":
            return """
            Understand their process while thinking about the system you'll build.
            "Help me understand how this works now so I can build you something better. When [problem] happens, 
            what's the first thing you or your team does? I'm already thinking about how to automate this..."
            """
        
        elif phase == "layer2":
            return """
            Connect to business impact and what you'll build to fix it.
            "I'm starting to see the real cost here. Based on what you're telling me, I can build you a system that 
            saves you [specific time] and unlocks [specific opportunity]. Beyond the immediate time savings, 
            what's the biggest opportunity this would open up for your business?"
            """
        
        elif phase == "layer3":
            return """
            Paint the picture of what you'll build for them.
            "Here's what I'm envisioning for you: a custom system that [specific solution]. You'd go from 
            [current painful state] to [automated future state]. This isn't a template - it's built exactly 
            for how your business works. What else would you want it to do?"
            """
        
        elif phase == "recommendation":
            return """
            Get them excited about starting the build.
            "Based on everything you've told me, I know exactly what to build for you: [specific system description].
            This will save you [specific time], increase [specific metric], and let you focus on [growth area].
            I can start building this right now while we talk. Should we do this?"
            Be specific about what you're building, not vague about "solutions."
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
    
    def _detect_emotional_state(self, message: str) -> str:
        """Detect the emotional state of the user from their message"""
        message_lower = message.lower()
        
        # Frustration indicators
        if any(word in message_lower for word in ['frustrated', 'annoying', 'tired of', 'sick of', 'hate', 'awful', 'nightmare']):
            return 'frustrated'
        
        # Confusion indicators
        if any(word in message_lower for word in ['what?', 'huh?', 'confused', "don't understand", "not sure", "maybe", "idk", "dunno"]):
            return 'confused'
        
        # Skepticism indicators
        if any(word in message_lower for word in ['really?', 'actually work', 'doubt', 'skeptical', 'tried before', 'yeah right']):
            return 'skeptical'
        
        # Excitement indicators
        if any(word in message_lower for word in ['excited', 'awesome', 'great', 'love', 'amazing', 'finally', 'yes!']):
            return 'excited'
        
        # Overwhelm indicators
        if any(word in message_lower for word in ['overwhelmed', 'too much', 'drowning', 'swamped', 'chaos', "can't keep up"]):
            return 'overwhelmed'
        
        return 'neutral'
    
    def _handle_specific_problem_mention(self, message: str, context: Dict) -> Optional[str]:
        """Generate specific response when user mentions a known problem type"""
        message_lower = message.lower()
        
        # Email-specific response
        if any(word in message_lower for word in ['email', 'emails', 'inbox', 'messages', 'replies']):
            return (
                "Ah, email overload - I see this all the time. Here's what I can build for you: an intelligent email "
                "management system that automatically categorizes your emails, extracts tasks and deadlines, routes them "
                "to the right people, and even drafts responses for common requests.\n\n"
                "Some founders I've worked with went from spending 3 hours a day on email to 30 minutes. "
                "Tell me more - are these mostly customer emails, internal communications, or a mix of everything?"
            )
        
        # Customer management specific
        if any(word in message_lower for word in ['customer', 'client', 'support', 'tickets']):
            return (
                "Customer management is crucial. I can build you a complete customer system - everything from a CRM "
                "that actually matches how you sell, to a support portal where customers can track their own issues, "
                "to automated follow-ups that happen without you thinking about it.\n\n"
                "What's the biggest pain point with your customers right now - is it keeping track of conversations, "
                "response times, or something else?"
            )
        
        # Data/reporting specific
        if any(word in message_lower for word in ['data', 'reports', 'analytics', 'metrics', 'dashboard']):
            return (
                "You need visibility into what's actually happening. I can build you real-time dashboards that show "
                "exactly what you need to see - whether that's sales pipeline, team performance, customer health, or "
                "operational metrics. No more manual reports or spreadsheet gymnastics.\n\n"
                "What decisions are you trying to make that you don't have good data for right now?"
            )
        
        return None
    
    def _handle_vague_response(self, message: str, context: Dict) -> str:
        """Handle vague or short responses naturally with curiosity"""
        message_lower = message.lower().strip()
        
        # Single word confusion responses
        if message_lower in ['what', 'what?', 'huh', 'huh?']:
            return (
                "Fair question. I realize I jumped right in there.\n\n"
                "I'm MIOSA. I understand businesses and build software. Not templates or generic tools - "
                "actual custom systems designed specifically for how you work.\n\n"
                "The thing is, every business has that one process that's held together with spreadsheets and prayer. What's yours?"
            )
        
        # Maybe/IDK responses
        if message_lower in ['maybe', 'idk', "i don't know", 'not sure', 'unsure']:
            return (
                "\"Maybe\" is actually a pretty honest answer. Most people don't immediately know their biggest "
                "bottleneck because they've gotten used to working around it.\n\n"
                "Let me help - are you more frustrated with how you handle customers, how you manage your team, "
                "or how you track your business performance?"
            )
        
        # Very short responses (under 5 characters)
        if len(message_lower) < 5:
            return (
                "I notice you're being brief. That's actually interesting - usually means either you're not sure "
                "where to start, or you're dealing with something so complex it's hard to articulate. Which is it for you?"
            )
        
        # Generic/vague responses
        if message_lower in ['okay', 'ok', 'sure', 'yes', 'no', 'fine', 'alright']:
            return (
                f"\"{message}\" - that tells me you're exploring what's possible. Good instinct.\n\n"
                "Here's what I'm thinking - you wouldn't be talking to an AI about business operations "
                "unless something was eating up too much of your time or money. Am I right?"
            )
        
        return None  # Not a vague response
    
    def _generate_emotionally_aware_response(self, emotional_state: str, message: str, context: Dict) -> str:
        """Generate response based on detected emotional state"""
        
        if emotional_state == 'frustrated':
            return (
                "I hear the frustration. Building a business is hard enough without systems fighting against you.\n\n"
                "What's the thing that if it just worked properly, would let you breathe a little easier?"
            )
        
        elif emotional_state == 'confused':
            return (
                "I realize I might be assuming too much. Let's start simpler - "
                "what does your business do, and what takes up most of your day?"
            )
        
        elif emotional_state == 'skeptical':
            return (
                "You're right to be skeptical. Most 'AI solutions' are just chatbots with extra steps.\n\n"
                "I'm different because I don't just talk about your problems - I actually build the solution "
                "while we're talking. Want to put me to the test?"
            )
        
        elif emotional_state == 'excited':
            return (
                "Your energy about this is great - that usually means you've been thinking about this problem for a while.\n\n"
                "Let's channel that into something concrete. What's the dream scenario for how this should work?"
            )
        
        elif emotional_state == 'overwhelmed':
            return (
                "I can sense you're juggling a lot. That's exactly why I'm here - to take some of that load off.\n\n"
                "Let's focus on just one thing that would make the biggest difference. "
                "What's the first fire you need to put out?"
            )
        
        return None  # No specific emotional response needed