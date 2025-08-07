"""
State Machine for Application Generation Process
"""

from enum import Enum
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class GenerationState(Enum):
    INITIAL = "initial"
    CONSULTING = "consulting"
    REQUIREMENTS_GATHERED = "requirements_gathered"
    DATABASE_DESIGN = "database_design"
    BACKEND_GENERATION = "backend_generation"
    FRONTEND_GENERATION = "frontend_generation"
    INTEGRATION_SETUP = "integration_setup"
    TESTING = "testing"
    DEPLOYMENT_READY = "deployment_ready"
    COMPLETED = "completed"
    FAILED = "failed"

class ApplicationStateMachine:
    """Manages the state transitions for application generation"""
    
    def __init__(self):
        self.current_state = GenerationState.INITIAL
        self.state_history = [GenerationState.INITIAL]
        self.context = {}
        
        # Define valid transitions
        self.transitions = {
            GenerationState.INITIAL: [GenerationState.CONSULTING],
            GenerationState.CONSULTING: [GenerationState.REQUIREMENTS_GATHERED, GenerationState.FAILED],
            GenerationState.REQUIREMENTS_GATHERED: [GenerationState.DATABASE_DESIGN, GenerationState.FAILED],
            GenerationState.DATABASE_DESIGN: [GenerationState.BACKEND_GENERATION, GenerationState.FAILED],
            GenerationState.BACKEND_GENERATION: [GenerationState.FRONTEND_GENERATION, GenerationState.INTEGRATION_SETUP, GenerationState.FAILED],
            GenerationState.FRONTEND_GENERATION: [GenerationState.INTEGRATION_SETUP, GenerationState.TESTING, GenerationState.FAILED],
            GenerationState.INTEGRATION_SETUP: [GenerationState.TESTING, GenerationState.FAILED],
            GenerationState.TESTING: [GenerationState.DEPLOYMENT_READY, GenerationState.FAILED],
            GenerationState.DEPLOYMENT_READY: [GenerationState.COMPLETED, GenerationState.FAILED],
            GenerationState.COMPLETED: [],
            GenerationState.FAILED: [GenerationState.INITIAL]  # Allow restart
        }
    
    def can_transition_to(self, target_state: GenerationState) -> bool:
        """Check if transition to target state is valid"""
        return target_state in self.transitions.get(self.current_state, [])
    
    def transition_to(self, target_state: GenerationState, context: Optional[Dict] = None) -> bool:
        """Transition to a new state"""
        if not self.can_transition_to(target_state):
            logger.error(f"Invalid transition from {self.current_state} to {target_state}")
            return False
        
        logger.info(f"Transitioning from {self.current_state} to {target_state}")
        
        self.current_state = target_state
        self.state_history.append(target_state)
        
        if context:
            self.context.update(context)
        
        return True
    
    def get_current_state(self) -> GenerationState:
        """Get the current state"""
        return self.current_state
    
    def get_state_history(self) -> list:
        """Get the history of state transitions"""
        return self.state_history
    
    def get_context(self) -> Dict:
        """Get the current context"""
        return self.context
    
    def update_context(self, updates: Dict) -> None:
        """Update the context with new information"""
        self.context.update(updates)
    
    def reset(self) -> None:
        """Reset the state machine to initial state"""
        self.current_state = GenerationState.INITIAL
        self.state_history = [GenerationState.INITIAL]
        self.context = {}
        logger.info("State machine reset to initial state")
    
    def get_next_states(self) -> list:
        """Get possible next states from current state"""
        return self.transitions.get(self.current_state, [])
    
    def is_terminal_state(self) -> bool:
        """Check if current state is terminal (no further transitions)"""
        return self.current_state in [GenerationState.COMPLETED, GenerationState.FAILED]
    
    def get_progress_percentage(self) -> float:
        """Calculate progress percentage based on current state"""
        state_weights = {
            GenerationState.INITIAL: 0,
            GenerationState.CONSULTING: 10,
            GenerationState.REQUIREMENTS_GATHERED: 20,
            GenerationState.DATABASE_DESIGN: 35,
            GenerationState.BACKEND_GENERATION: 50,
            GenerationState.FRONTEND_GENERATION: 65,
            GenerationState.INTEGRATION_SETUP: 80,
            GenerationState.TESTING: 90,
            GenerationState.DEPLOYMENT_READY: 95,
            GenerationState.COMPLETED: 100,
            GenerationState.FAILED: -1
        }
        
        return state_weights.get(self.current_state, 0)
    
    def validate_state_data(self, state: GenerationState, data: Dict) -> bool:
        """Validate that required data exists for a state transition"""
        required_data = {
            GenerationState.REQUIREMENTS_GATHERED: ["business_requirements", "technical_requirements"],
            GenerationState.DATABASE_DESIGN: ["entities", "relationships"],
            GenerationState.BACKEND_GENERATION: ["api_endpoints", "services"],
            GenerationState.FRONTEND_GENERATION: ["components", "pages"],
            GenerationState.INTEGRATION_SETUP: ["integrations"],
            GenerationState.DEPLOYMENT_READY: ["deployment_config", "environment_vars"]
        }
        
        required_fields = required_data.get(state, [])
        
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field '{field}' for state {state}")
                return False
        
        return True