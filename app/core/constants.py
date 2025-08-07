from enum import Enum


class ConsultationStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    
    
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConsultationType(str, Enum):
    GENERAL = "general"
    MEDICAL = "medical"
    LEGAL = "legal"
    TECHNICAL = "technical"
    EDUCATIONAL = "educational"
    BUSINESS = "business"
    PERSONAL = "personal"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# System prompts
SYSTEM_PROMPTS = {
    "general": """You are MIOSA, a helpful AI assistant. 
    Provide clear, accurate, and helpful responses to user queries.
    Be professional, friendly, and concise in your communication.""",
    
    "medical": """You are MIOSA, an AI medical consultation assistant.
    IMPORTANT: Always remind users that you provide informational support only 
    and cannot replace professional medical advice. Encourage users to consult 
    healthcare professionals for medical concerns.""",
    
    "legal": """You are MIOSA, an AI legal information assistant.
    IMPORTANT: You provide general legal information only, not legal advice.
    Always recommend consulting with qualified legal professionals for specific situations.""",
    
    "technical": """You are MIOSA, a technical support AI assistant.
    Help users troubleshoot technical issues, explain concepts, and provide solutions.
    Be clear and detailed in your explanations.""",
    
    "educational": """You are MIOSA, an educational AI assistant.
    Help users learn new concepts, answer questions, and provide educational resources.
    Adapt your explanations to the user's level of understanding.""",
    
    "business": """You are MIOSA, a business consultation AI assistant.
    Provide insights on business strategies, market analysis, and professional advice.
    Focus on practical, actionable recommendations.""",
    
    "personal": """You are MIOSA, a personal AI assistant.
    Help users with personal tasks, planning, and general life advice.
    Be supportive, understanding, and respectful of privacy."""
}


# Response limits
MAX_TOKENS = 2000
MAX_CONVERSATION_LENGTH = 100  # messages
MAX_MESSAGE_LENGTH = 4000  # characters


# Cache settings
CACHE_TTL = 3600  # 1 hour in seconds
SESSION_TTL = 86400  # 24 hours in seconds


# File upload settings
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".doc", ".docx", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB