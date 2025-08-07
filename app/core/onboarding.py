"""
MIOSA User Onboarding System
Captures user details before consultation to enable personalized service
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class OnboardingStep(Enum):
    NAME = "name"
    EMAIL = "email" 
    BUSINESS_NAME = "business_name"
    BUSINESS_TYPE = "business_type"
    TEAM_SIZE = "team_size"
    MAIN_PROBLEM = "main_problem"
    COMPLETE = "complete"

@dataclass
class UserProfile:
    """Complete user profile for personalized service"""
    
    # Required fields (no defaults)
    name: str
    email: str
    business_name: str
    business_type: str
    main_problem: str
    
    # Optional fields (with defaults)
    preferred_name: Optional[str] = None
    industry: Optional[str] = None
    team_size: Optional[int] = None
    role: Optional[str] = None
    urgency: Optional[str] = None
    communication_style: str = "professional"
    onboarding_complete: bool = False

class OnboardingFlow:
    """Manages the progressive onboarding conversation"""
    
    def __init__(self):
        self.steps = [
            {
                "field": "name",
                "question": "First, what's your name?",
                "required": True,
                "validation": self._validate_name
            },
            {
                "field": "email", 
                "question": "What's your email address?",
                "required": True,
                "validation": self._validate_email
            },
            {
                "field": "business_name",
                "question": "What's your business called?",
                "required": True,
                "validation": self._validate_business_name
            },
            {
                "field": "business_type",
                "question": "What type of business is it?",
                "required": True,
                "validation": self._validate_business_type
            },
            {
                "field": "team_size",
                "question": "How many people are on your team? (Just you, 2-5, 6-20, 20+)",
                "required": False,
                "validation": self._validate_team_size
            },
            {
                "field": "main_problem",
                "question": "What's the biggest operational challenge you're facing right now?",
                "required": True,
                "validation": self._validate_main_problem
            }
        ]
        
    def get_welcome_message(self) -> str:
        """Initial welcome message that starts onboarding"""
        return """╭────────────────────────────────────────────────────────────────────────────╮
│                                                                            │
│  🤖 MIOSA - Your Personal Business OS Agent                                │
│                                                                            │
│  I build custom software that runs YOUR business exactly how you want.     │
│  No templates. No generic solutions. Just your perfect system.             │
│                                                                            │
│  Let's start with a quick introduction so I can build something perfect    │
│  for your specific needs.                                                  │
│                                                                            │
╰────────────────────────────────────────────────────────────────────────────╯

I'm MIOSA. First, what's your name?"""

    def get_current_question(self, current_step: OnboardingStep, profile: Dict) -> str:
        """Get the current onboarding question"""
        
        if current_step == OnboardingStep.NAME:
            return self.get_welcome_message()
        
        # Find the step
        step_index = self._get_step_index(current_step)
        if step_index == -1 or step_index >= len(self.steps):
            return self._complete_onboarding(profile)
            
        step = self.steps[step_index]
        
        # Personalize the question using their name
        name = profile.get("name", "")
        if name and current_step != OnboardingStep.NAME:
            return f"Thanks {name}! {step['question']}"
        else:
            return step["question"]
    
    def process_answer(self, current_step: OnboardingStep, answer: str, profile: Dict) -> Tuple[OnboardingStep, str, bool]:
        """Process user's answer and return next step, message, and validation status"""
        
        step_index = self._get_step_index(current_step)
        if step_index == -1:
            return OnboardingStep.COMPLETE, self._complete_onboarding(profile), True
            
        step = self.steps[step_index]
        field = step["field"]
        
        # Validate the answer
        validation_result = step["validation"](answer)
        if not validation_result[0]:
            # Validation failed
            name = profile.get("name", "")
            error_msg = f"{"Sorry " + name + ", " if name else ""}{validation_result[1]}"
            return current_step, error_msg, False
        
        # Store the validated answer
        profile[field] = validation_result[2] if len(validation_result) > 2 else answer
        
        # Move to next step
        next_step_index = step_index + 1
        if next_step_index >= len(self.steps):
            # Onboarding complete
            profile["onboarding_complete"] = True
            return OnboardingStep.COMPLETE, self._complete_onboarding(profile), True
        
        # Map step index to OnboardingStep enum
        step_mapping = [
            OnboardingStep.NAME,
            OnboardingStep.EMAIL, 
            OnboardingStep.BUSINESS_NAME,
            OnboardingStep.BUSINESS_TYPE,
            OnboardingStep.TEAM_SIZE,
            OnboardingStep.MAIN_PROBLEM
        ]
        
        next_step = step_mapping[next_step_index] if next_step_index < len(step_mapping) else OnboardingStep.COMPLETE
        next_question = self.get_current_question(next_step, profile)
        
        return next_step, next_question, True
    
    def _get_step_index(self, step: OnboardingStep) -> int:
        """Get the index of the current step"""
        step_field_map = {
            OnboardingStep.NAME: "name",
            OnboardingStep.EMAIL: "email", 
            OnboardingStep.BUSINESS_NAME: "business_name",
            OnboardingStep.BUSINESS_TYPE: "business_type",
            OnboardingStep.TEAM_SIZE: "team_size",
            OnboardingStep.MAIN_PROBLEM: "main_problem"
        }
        
        field = step_field_map.get(step)
        if not field:
            return -1
            
        # Find the step index by field name
        for i, step_info in enumerate(self.steps):
            if step_info["field"] == field:
                return i
        
        return -1
    
    def _complete_onboarding(self, profile: Dict) -> str:
        """Generate completion message with summary"""
        name = profile.get("name", "")
        business_name = profile.get("business_name", "your business")
        business_type = profile.get("business_type", "")
        main_problem = profile.get("main_problem", "your challenge")
        
        return f"""Perfect, {name}! I now understand you run {business_name}, {business_type}.

Your main challenge: {main_problem}

Now let's dive deep into this issue so I can build you the perfect solution. Tell me more about how this problem affects your day-to-day operations."""
    
    # Validation methods
    def _validate_name(self, name: str) -> Tuple[bool, str, str]:
        name = name.strip()
        if not name:
            return False, "please tell me your name so I can personalize our conversation.", ""
        if len(name) < 2:
            return False, "that seems too short for a name. What's your full name?", ""
        
        # Split the input to check each word
        words = name.lower().split()
        
        # Reject common non-names and greetings
        invalid_names = [
            'hey', 'hi', 'hello', 'yo', 'sup', 'heyo', 'hiya',
            'um', 'uh', 'err', 'hmm', 'what', 'wtf', 'lol', 'lmao', 'rofl', 'haha',
            'yes', 'no', 'ok', 'okay', 'sure', 'maybe', 'nope', 'yep', 'yeah', 'nah',
            'test', 'testing', 'asdf', 'abc', '123', 'qwerty',
            'wait', 'stop', 'hold', 'pause', 'continue', 'next', 'skip',
            'help', 'info', 'about', 'why', 'how', 'when', 'where', 'who',
            'fuck', 'shit', 'damn', 'crap', 'hell', 'bro', 'dude', 'man',
            'cool', 'nice', 'good', 'bad', 'great', 'awesome',
            'idk', 'dunno', 'whatever', 'nothing', 'something',
            'blah', 'meh', 'ugh', 'sigh', 'hmph'
        ]
        
        # Check if ANY word in the input is invalid (catches "lol wait", "hey there", etc)
        for word in words:
            if word in invalid_names:
                # Return appropriate message based on the invalid word found
                if word in ['lol', 'lmao', 'rofl', 'haha']:
                    return False, "I know this seems formal, but I need your real name to build your custom system. What should I call you?", ""
                elif word in ['wait', 'stop', 'hold', 'pause']:
                    return False, "No problem, take your time. When you're ready, what's your first name?", ""
                elif word in ['bro', 'dude', 'man']:
                    return False, "I get it - this feels formal. But I need your actual name to personalize your system. What's your first name?", ""
                elif word in ['wtf', 'fuck', 'shit', 'damn']:
                    return False, "I understand if this is frustrating. Just need your first name to get started - what should I call you?", ""
                else:
                    return False, "I need your actual name to personalize our conversation. What should I call you?", ""
        
        # Also check the full string
        if name.lower() in invalid_names:
            # Vary the response based on what they typed
            if name.lower() in ['ok', 'okay', 'sure', 'yes', 'yeah']:
                return False, "Great! So what's your actual name?", ""
            elif name.lower() in ['lol', 'lmao', 'rofl', 'haha']:
                return False, "I know this seems formal, but I need your real name to build your custom system. What should I call you?", ""
            elif name.lower() in ['wait', 'stop', 'hold', 'pause']:
                return False, "No problem, take your time. When you're ready, what's your first name?", ""
            elif name.lower() in ['wtf', 'fuck', 'shit', 'damn']:
                return False, "I understand if this is frustrating. Just need your first name to get started - what should I call you?", ""
            else:
                return False, "I need your actual name to personalize our conversation. What should I call you?", ""
        
        # Check if it looks like a real name (at least has some letters)
        if not any(c.isalpha() for c in name):
            return False, "please provide your actual name.", ""
        
        # Reject single common English words that aren't typically names
        common_words = [
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
            'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
            'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who',
            'boy', 'did', 'man', 'car', 'let', 'put', 'say', 'she', 'too', 'use',
            'well', 'just', 'like', 'want', 'need', 'have', 'been', 'were', 'than'
        ]
        
        # But allow actual names that might be words (like "Will", "May", "Rose")
        # Note: "well" is NOT a name - it's just a word
        allowed_word_names = ['will', 'may', 'rose', 'grace', 'hope', 'faith', 'joy', 'mark', 'bill', 'jack']
        
        if name.lower() in common_words and name.lower() not in allowed_word_names:
            return False, "That doesn't seem like a real name. What's your actual first name?", ""
            
        return True, "", name.title()
    
    def _validate_email(self, email: str) -> Tuple[bool, str, str]:
        email = email.strip().lower()
        if not email:
            return False, "I need your email to send you updates about your project.", ""
        if "@" not in email or "." not in email:
            return False, "that doesn't look like a valid email address.", ""
        return True, "", email
    
    def _validate_business_name(self, business_name: str) -> Tuple[bool, str, str]:
        business_name = business_name.strip()
        if not business_name:
            return False, "what do you call your business?", ""
        return True, "", business_name
    
    def _validate_business_type(self, business_type: str) -> Tuple[bool, str, str]:
        business_type = business_type.strip()
        if not business_type:
            return False, "what type of business do you run?", ""
        return True, "", business_type.lower()
    
    def _validate_team_size(self, team_size: str) -> Tuple[bool, str, int]:
        if not team_size.strip():
            return True, "", 1  # Default to 1 if not provided
        
        team_size_clean = team_size.lower().strip()
        
        # Parse team size
        if any(word in team_size_clean for word in ["just me", "solo", "myself", "one", "1"]):
            return True, "", 1
        elif any(word in team_size_clean for word in ["2-5", "few", "small", "2", "3", "4", "5"]):
            return True, "", 3  # Average
        elif any(word in team_size_clean for word in ["6-20", "medium", "10", "15"]):
            return True, "", 12  # Average
        elif any(word in team_size_clean for word in ["20+", "large", "many", "lots"]):
            return True, "", 25  # Average
        
        # Try to extract number
        import re
        numbers = re.findall(r'\d+', team_size_clean)
        if numbers:
            return True, "", int(numbers[0])
        
        return True, "", 1  # Default to 1 if unclear
    
    def _validate_main_problem(self, main_problem: str) -> Tuple[bool, str, str]:
        main_problem = main_problem.strip()
        if not main_problem:
            return False, "I need to understand your main challenge to build the right solution.", ""
        if len(main_problem) < 10:
            return False, "can you give me a bit more detail about this challenge?", ""
        return True, "", main_problem

class PersonalizedResponder:
    """Generates personalized responses using user profile"""
    
    def __init__(self, profile: UserProfile):
        self.profile = profile
    
    def get_greeting(self) -> str:
        """Get personalized greeting"""
        return f"Hi {self.profile.name}! How can I help {self.profile.business_name} today?"
    
    def get_progress_message(self, progress: int) -> str:
        """Get personalized progress message"""
        return f"Great progress, {self.profile.name}! I'm understanding {self.profile.business_name} better."
    
    def get_ready_message(self, solution_type: str) -> str:
        """Get personalized ready-to-build message"""
        return f"Alright {self.profile.name}, I have everything I need to build your {solution_type} for {self.profile.business_name}. Ready to start?"
    
    def get_building_message(self, project_name: str) -> str:
        """Get personalized building message"""
        return f"Building your {project_name} now, {self.profile.name}. This is designed specifically for how {self.profile.business_name} operates."
    
    def get_completion_message(self, project_name: str) -> str:
        """Get personalized completion message"""
        return f"{self.profile.name}, your {project_name} is ready! Built exactly for how {self.profile.business_name} works."

# Global onboarding flow instance
onboarding_flow = OnboardingFlow()