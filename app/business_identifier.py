"""
Business Type Identification System for MIOSA
Intelligently identifies and categorizes businesses for targeted consultation
"""

from typing import Dict, List, Optional, Tuple
import re
from dataclasses import dataclass
from enum import Enum

class BusinessCategory(Enum):
    """Main business categories"""
    SAAS = "saas"
    ECOMMERCE = "ecommerce"
    AGENCY = "agency"
    MARKETPLACE = "marketplace"
    PROFESSIONAL_SERVICES = "professional_services"
    HEALTHCARE = "healthcare"
    FINTECH = "fintech"
    EDTECH = "edtech"
    LOGISTICS = "logistics"
    HOSPITALITY = "hospitality"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    NONPROFIT = "nonprofit"
    MEDIA = "media"
    REAL_ESTATE = "real_estate"
    UNKNOWN = "unknown"

@dataclass
class BusinessProfile:
    """Complete business profile after identification"""
    category: BusinessCategory
    subcategory: str
    industry: str
    business_model: str
    target_market: str
    size_indicator: str
    confidence: float
    keywords_matched: List[str]
    problem_patterns: List[str]
    suggested_questions: List[str]

class BusinessIdentifier:
    """
    Identifies business type from user messages and context.
    Uses multiple signals to determine the most likely business type.
    """
    
    def __init__(self):
        self.business_patterns = self._initialize_patterns()
        self.industry_keywords = self._initialize_industry_keywords()
        self.problem_patterns = self._initialize_problem_patterns()
        
    def identify_business(self, message: str, context: Dict = None) -> BusinessProfile:
        """
        Main method to identify business type from user input
        """
        message_lower = message.lower()
        context = context or {}
        
        # Extract all signals
        signals = {
            'keywords': self._extract_keywords(message_lower),
            'business_model': self._identify_business_model(message_lower),
            'industry': self._identify_industry(message_lower),
            'size': self._identify_business_size(message_lower),
            'problems': self._identify_problem_patterns(message_lower),
            'tech_stack': self._extract_tech_stack(message_lower)
        }
        
        # Score each business category
        category_scores = {}
        for category in BusinessCategory:
            if category != BusinessCategory.UNKNOWN:
                score = self._calculate_category_score(category, signals, message_lower)
                category_scores[category] = score
        
        # Get the best match
        best_category = max(category_scores, key=category_scores.get)
        confidence = category_scores[best_category]
        
        # If confidence is too low, mark as unknown
        if confidence < 0.25:
            best_category = BusinessCategory.UNKNOWN
        
        # Build the complete profile
        profile = self._build_business_profile(
            best_category, 
            signals, 
            confidence,
            message_lower
        )
        
        return profile
    
    def _initialize_patterns(self) -> Dict:
        """Initialize business type patterns"""
        return {
            BusinessCategory.SAAS: {
                'keywords': ['saas', 'software', 'subscription', 'platform', 'app', 'cloud', 
                            'users', 'mrr', 'arr', 'churn', 'retention', 'onboarding'],
                'phrases': ['software as a service', 'monthly recurring', 'user acquisition',
                           'customer acquisition cost', 'lifetime value'],
                'problems': ['churn', 'onboarding', 'user retention', 'scaling', 'pricing']
            },
            BusinessCategory.ECOMMERCE: {
                'keywords': ['store', 'shop', 'products', 'inventory', 'orders', 'shipping',
                            'cart', 'checkout', 'payment', 'catalog', 'sku', 'fulfillment',
                            'ecommerce', 'e-commerce', 'selling', 'sell', 'jewelry', 'retail'],
                'phrases': ['online store', 'e-commerce', 'selling online', 'drop shipping',
                           'product catalog', 'inventory management', 'e-commerce store'],
                'problems': ['inventory', 'shipping', 'returns', 'cart abandonment', 'conversion']
            },
            BusinessCategory.AGENCY: {
                'keywords': ['agency', 'clients', 'projects', 'consulting', 'services',
                            'deliverables', 'retainer', 'billable', 'scope', 'proposal',
                            'help', 'marketing', 'digital'],
                'phrases': ['digital agency', 'marketing agency', 'consulting firm',
                           'creative agency', 'ai agency', 'development agency', 'help businesses'],
                'problems': ['project management', 'client communication', 'billing', 'scope creep']
            },
            BusinessCategory.MARKETPLACE: {
                'keywords': ['marketplace', 'buyers', 'sellers', 'vendors', 'listings',
                            'commission', 'transactions', 'matching', 'two-sided'],
                'phrases': ['two-sided marketplace', 'buyer and seller', 'vendor marketplace'],
                'problems': ['liquidity', 'chicken and egg', 'trust', 'matching', 'quality control']
            },
            BusinessCategory.HEALTHCARE: {
                'keywords': ['patient', 'doctor', 'medical', 'health', 'clinic', 'hospital',
                            'appointment', 'prescription', 'diagnosis', 'treatment', 'hipaa',
                            'dentist', 'dental', 'physician', 'nurse', 'therapy'],
                'phrases': ['healthcare provider', 'medical practice', 'dental practice',
                           'patient care', 'electronic health records'],
                'problems': ['appointment scheduling', 'patient records', 'billing', 'compliance']
            },
            BusinessCategory.FINTECH: {
                'keywords': ['payment', 'transaction', 'banking', 'finance', 'money', 'wallet',
                            'lending', 'investment', 'trading', 'crypto', 'compliance', 'kyc'],
                'phrases': ['payment processing', 'financial services', 'digital banking'],
                'problems': ['compliance', 'fraud', 'kyc', 'aml', 'transaction processing']
            },
            BusinessCategory.PROFESSIONAL_SERVICES: {
                'keywords': ['lawyer', 'accountant', 'consultant', 'advisor', 'firm',
                            'practice', 'clients', 'cases', 'engagement', 'advisory',
                            'attorneys', 'attorney', 'litigation', 'legal', 'law'],
                'phrases': ['law firm', 'accounting firm', 'consulting practice', 'legal practice'],
                'problems': ['client management', 'document management', 'time tracking', 'billing']
            },
            BusinessCategory.REAL_ESTATE: {
                'keywords': ['property', 'real estate', 'listing', 'rental', 'tenant',
                            'landlord', 'lease', 'apartment', 'house', 'broker', 'agent',
                            'properties', 'manage', 'rent'],
                'phrases': ['property management', 'real estate agency', 'rental properties', 'manage properties'],
                'problems': ['property management', 'tenant screening', 'maintenance', 'listings']
            },
            BusinessCategory.EDTECH: {
                'keywords': ['education', 'learning', 'course', 'student', 'teacher',
                            'curriculum', 'lesson', 'quiz', 'assignment', 'grades'],
                'phrases': ['online education', 'learning platform', 'course platform'],
                'problems': ['student engagement', 'course delivery', 'assessment', 'progress tracking']
            },
            BusinessCategory.LOGISTICS: {
                'keywords': ['shipping', 'delivery', 'logistics', 'freight', 'warehouse',
                            'fleet', 'route', 'tracking', 'dispatch', 'carrier'],
                'phrases': ['logistics company', 'delivery service', 'shipping company'],
                'problems': ['route optimization', 'tracking', 'fleet management', 'last mile']
            }
        }
    
    def _initialize_industry_keywords(self) -> Dict:
        """Industry-specific keywords for better identification"""
        return {
            'b2b': ['b2b', 'business to business', 'enterprise', 'companies', 'organizations'],
            'b2c': ['b2c', 'consumer', 'customers', 'users', 'retail'],
            'b2b2c': ['b2b2c', 'platform', 'marketplace', 'both businesses and consumers'],
            'dental': ['dental', 'dentist', 'orthodontist', 'dental practice', 'teeth'],
            'medical': ['medical', 'doctor', 'physician', 'patient', 'healthcare'],
            'legal': ['legal', 'law', 'lawyer', 'attorney', 'litigation'],
            'construction': ['construction', 'contractor', 'building', 'renovation'],
            'restaurant': ['restaurant', 'food', 'dining', 'menu', 'orders'],
            'fitness': ['gym', 'fitness', 'workout', 'training', 'membership'],
            'beauty': ['salon', 'spa', 'beauty', 'cosmetics', 'styling']
        }
    
    def _initialize_problem_patterns(self) -> Dict:
        """Problem patterns by business type"""
        return {
            'manual_operations': ['manual', 'by hand', 'spreadsheet', 'repetitive', 'time-consuming'],
            'scaling_issues': ['scaling', 'growth', 'can\'t keep up', 'overwhelming', 'bottleneck'],
            'customer_management': ['customer', 'client', 'crm', 'contacts', 'relationships'],
            'financial_management': ['invoicing', 'billing', 'payments', 'accounting', 'expenses'],
            'communication': ['communication', 'email', 'messaging', 'collaboration', 'coordination'],
            'data_management': ['data', 'analytics', 'reporting', 'insights', 'metrics'],
            'automation_needs': ['automate', 'automation', 'ai', 'efficiency', 'streamline']
        }
    
    def _extract_keywords(self, message: str) -> List[str]:
        """Extract business-related keywords from message"""
        keywords = []
        
        # Check against all pattern keywords
        for category_patterns in self.business_patterns.values():
            for keyword in category_patterns.get('keywords', []):
                if keyword in message:
                    keywords.append(keyword)
        
        return keywords
    
    def _identify_business_model(self, message: str) -> str:
        """Identify the business model from the message"""
        models = {
            'subscription': ['subscription', 'recurring', 'monthly', 'annual', 'saas'],
            'transactional': ['sell', 'selling', 'sales', 'transaction', 'purchase'],
            'marketplace': ['marketplace', 'platform', 'connect', 'buyers and sellers'],
            'service': ['service', 'consulting', 'agency', 'freelance', 'contractor'],
            'product': ['product', 'manufacturing', 'produce', 'inventory']
        }
        
        for model, keywords in models.items():
            if any(keyword in message for keyword in keywords):
                return model
        
        return 'unknown'
    
    def _identify_industry(self, message: str) -> str:
        """Identify the specific industry"""
        for industry, keywords in self.industry_keywords.items():
            if any(keyword in message for keyword in keywords):
                return industry
        return 'general'
    
    def _identify_business_size(self, message: str) -> str:
        """Identify business size indicators"""
        size_patterns = {
            'solo': ['solo', 'alone', 'just me', 'one person', 'individual'],
            'small': ['small', 'few', 'team of', 'startup', '<10', 'less than 10'],
            'medium': ['medium', 'growing', '10-50', 'dozen', 'multiple teams'],
            'large': ['large', 'enterprise', 'hundreds', 'thousands', 'global']
        }
        
        for size, patterns in size_patterns.items():
            if any(pattern in message for pattern in patterns):
                return size
        
        # Try to extract from numbers
        import re
        numbers = re.findall(r'\b(\d+)\s*(?:employees?|people|team members?)\b', message)
        if numbers:
            count = int(numbers[0])
            if count <= 1:
                return 'solo'
            elif count <= 10:
                return 'small'
            elif count <= 50:
                return 'medium'
            else:
                return 'large'
        
        return 'unknown'
    
    def _identify_problem_patterns(self, message: str) -> List[str]:
        """Identify problem patterns in the message"""
        problems = []
        for problem_type, patterns in self.problem_patterns.items():
            if any(pattern in message for pattern in patterns):
                problems.append(problem_type)
        return problems
    
    def _extract_tech_stack(self, message: str) -> List[str]:
        """Extract mentioned technologies"""
        tech_keywords = [
            'excel', 'sheets', 'slack', 'teams', 'zoom', 'salesforce', 'hubspot',
            'quickbooks', 'stripe', 'shopify', 'wordpress', 'squarespace', 'wix',
            'mailchimp', 'sendgrid', 'twilio', 'aws', 'google cloud', 'azure',
            'notion', 'airtable', 'monday', 'asana', 'jira', 'trello'
        ]
        
        return [tech for tech in tech_keywords if tech in message]
    
    def _calculate_category_score(self, category: BusinessCategory, signals: Dict, message: str) -> float:
        """Calculate confidence score for a business category"""
        score = 0.0
        patterns = self.business_patterns.get(category, {})
        
        # Keyword matching (40% weight) - more flexible matching
        keywords = patterns.get('keywords', [])
        keyword_matches = 0
        for keyword in keywords:
            if keyword in message:
                # Full match gets more weight
                keyword_matches += 1.0
            elif any(word in message for word in keyword.split()):
                # Partial match gets less weight
                keyword_matches += 0.5
        
        if keywords:
            score += min((keyword_matches / len(keywords)) * 0.4, 0.4)
        
        # Phrase matching (30% weight)
        phrases = patterns.get('phrases', [])
        phrase_matches = sum(1 for p in phrases if p.lower() in message)
        if phrases:
            score += min((phrase_matches / len(phrases)) * 0.3, 0.3)
        
        # Problem pattern matching (20% weight)
        problem_patterns = patterns.get('problems', [])
        problem_matches = sum(1 for p in problem_patterns if p in message)
        if problem_patterns:
            score += min((problem_matches / len(problem_patterns)) * 0.2, 0.2)
        
        # Business model alignment (10% weight)
        if self._is_model_aligned(category, signals['business_model']):
            score += 0.1
        
        # Bonus for explicit category mentions
        if category.value in message:
            score += 0.3
        
        # Additional bonus for strong indicators
        strong_indicators = {
            BusinessCategory.ECOMMERCE: ['store', 'shop', 'selling', 'e-commerce'],
            BusinessCategory.PROFESSIONAL_SERVICES: ['firm', 'attorneys', 'lawyer', 'law firm'],
            BusinessCategory.REAL_ESTATE: ['properties', 'rental', 'manage', 'property'],
            BusinessCategory.AGENCY: ['help', 'businesses', 'marketing', 'digital']
        }
        
        if category in strong_indicators:
            for indicator in strong_indicators[category]:
                if indicator in message:
                    score += 0.15
                    break
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _is_model_aligned(self, category: BusinessCategory, model: str) -> bool:
        """Check if business model aligns with category"""
        alignments = {
            BusinessCategory.SAAS: ['subscription', 'recurring'],
            BusinessCategory.ECOMMERCE: ['transactional', 'product'],
            BusinessCategory.AGENCY: ['service', 'project'],
            BusinessCategory.MARKETPLACE: ['marketplace', 'platform'],
            BusinessCategory.PROFESSIONAL_SERVICES: ['service', 'consulting']
        }
        
        return model in alignments.get(category, [])
    
    def _build_business_profile(self, category: BusinessCategory, signals: Dict, 
                                confidence: float, message: str) -> BusinessProfile:
        """Build complete business profile"""
        
        # Generate targeted questions based on business type
        questions = self._generate_targeted_questions(category, signals)
        
        # Determine subcategory
        subcategory = self._determine_subcategory(category, message)
        
        return BusinessProfile(
            category=category,
            subcategory=subcategory,
            industry=signals['industry'],
            business_model=signals['business_model'],
            target_market=self._determine_target_market(message),
            size_indicator=signals['size'],
            confidence=confidence,
            keywords_matched=signals['keywords'],
            problem_patterns=signals['problems'],
            suggested_questions=questions
        )
    
    def _determine_subcategory(self, category: BusinessCategory, message: str) -> str:
        """Determine business subcategory"""
        subcategories = {
            BusinessCategory.AGENCY: {
                'ai_automation': ['ai', 'automation', 'artificial intelligence'],
                'marketing': ['marketing', 'advertising', 'seo', 'ppc'],
                'development': ['development', 'software', 'web', 'app'],
                'design': ['design', 'creative', 'branding', 'ui', 'ux'],
                'consulting': ['consulting', 'strategy', 'advisory']
            },
            BusinessCategory.SAAS: {
                'crm': ['crm', 'customer relationship', 'sales pipeline'],
                'project_management': ['project', 'task', 'management'],
                'communication': ['chat', 'messaging', 'communication'],
                'analytics': ['analytics', 'data', 'metrics', 'insights'],
                'automation': ['automation', 'workflow', 'integration']
            },
            BusinessCategory.HEALTHCARE: {
                'dental': ['dental', 'dentist', 'orthodontic'],
                'medical': ['medical', 'doctor', 'physician', 'clinic'],
                'mental_health': ['therapy', 'counseling', 'mental health'],
                'specialty': ['specialist', 'surgery', 'cardiology', 'dermatology']
            }
        }
        
        if category in subcategories:
            for subcat, keywords in subcategories[category].items():
                if any(keyword in message for keyword in keywords):
                    return subcat
        
        return 'general'
    
    def _determine_target_market(self, message: str) -> str:
        """Determine target market from message"""
        if any(word in message for word in ['b2b', 'businesses', 'companies', 'enterprise']):
            return 'b2b'
        elif any(word in message for word in ['b2c', 'consumers', 'customers', 'users']):
            return 'b2c'
        elif any(word in message for word in ['marketplace', 'both', 'sellers and buyers']):
            return 'b2b2c'
        return 'unknown'
    
    def _generate_targeted_questions(self, category: BusinessCategory, signals: Dict) -> List[str]:
        """Generate specific questions based on business type"""
        
        questions = {
            BusinessCategory.AGENCY: [
                "How many clients are you currently managing?",
                "What's your average project timeline from start to finish?",
                "How do you currently track project deliverables and client communications?",
                "What's the most time-consuming part of managing client projects?"
            ],
            BusinessCategory.SAAS: [
                "How many active users do you have on your platform?",
                "What's your current monthly churn rate?",
                "How long does your onboarding process typically take?",
                "What's the biggest bottleneck in your user acquisition funnel?"
            ],
            BusinessCategory.ECOMMERCE: [
                "How many orders are you processing daily/weekly?",
                "What's your current cart abandonment rate?",
                "How do you manage inventory across different channels?",
                "What percentage of customer service time goes to order status inquiries?"
            ],
            BusinessCategory.HEALTHCARE: [
                "How many patients/appointments do you handle daily?",
                "What's your current no-show rate for appointments?",
                "How much time does your staff spend on phone calls for scheduling?",
                "Are you dealing with insurance verification manually?"
            ],
            BusinessCategory.MARKETPLACE: [
                "How many active buyers and sellers do you have?",
                "What's your current take rate or commission structure?",
                "How do you handle trust and safety between parties?",
                "What's your biggest challenge - supply or demand?"
            ],
            BusinessCategory.PROFESSIONAL_SERVICES: [
                "How many active clients or cases are you managing?",
                "How do you currently track billable hours?",
                "What's your average collection time for invoices?",
                "How much time goes into creating proposals or reports?"
            ],
            BusinessCategory.FINTECH: [
                "What's your daily transaction volume?",
                "How do you currently handle KYC/AML compliance?",
                "What's your fraud rate?",
                "How long does customer onboarding take?"
            ],
            BusinessCategory.REAL_ESTATE: [
                "How many properties are you currently managing?",
                "What's your vacancy rate?",
                "How do you handle maintenance requests?",
                "How much time goes into tenant screening?"
            ]
        }
        
        # Get base questions for the category
        base_questions = questions.get(category, [
            "How many customers/clients do you currently serve?",
            "What manual process takes up most of your team's time?",
            "What's preventing you from scaling faster?",
            "If you could automate one thing tomorrow, what would it be?"
        ])
        
        # Add problem-specific questions
        if 'scaling_issues' in signals['problems']:
            base_questions.append("At what point does your current system start breaking down?")
        
        if 'manual_operations' in signals['problems']:
            base_questions.append("How many hours per week go into these manual tasks?")
        
        return base_questions[:4]  # Return top 4 most relevant questions


# Usage Example
def identify_and_respond(user_message: str, context: Dict = None):
    """
    Example of how to use the business identifier in your Communication Agent
    """
    identifier = BusinessIdentifier()
    profile = identifier.identify_business(user_message, context)
    
    # Now you have detailed business information
    print(f"Business Type: {profile.category.value}")
    print(f"Subcategory: {profile.subcategory}")
    print(f"Industry: {profile.industry}")
    print(f"Confidence: {profile.confidence:.2%}")
    print(f"Size: {profile.size_indicator}")
    print(f"Problems Detected: {profile.problem_patterns}")
    
    # Use the suggested questions for targeted consultation
    print("\nSuggested follow-up questions:")
    for i, question in enumerate(profile.suggested_questions, 1):
        print(f"{i}. {question}")
    
    # Store in session for context
    session_update = {
        'business_profile': {
            'category': profile.category.value,
            'subcategory': profile.subcategory,
            'industry': profile.industry,
            'model': profile.business_model,
            'size': profile.size_indicator,
            'confidence': profile.confidence
        }
    }
    
    return profile, session_update


# Test cases
if __name__ == "__main__":
    test_messages = [
        "I'm an AI agency that helps dentists use AI to answer their phone calls",
        "We run a SaaS platform for project management with about 5000 users",
        "I have an e-commerce store selling handmade jewelry",
        "We're a law firm with 15 attorneys handling corporate litigation",
        "I run a marketplace connecting freelance developers with startups",
        "We're building a fintech app for peer-to-peer payments",
        "I manage 30 rental properties in the downtown area",
        "We help small businesses with their digital marketing",
        "I'm a solo consultant helping companies with data analytics"
    ]
    
    identifier = BusinessIdentifier()
    for msg in test_messages:
        print(f"\nMessage: {msg}")
        profile = identifier.identify_business(msg)
        print(f"Identified as: {profile.category.value} ({profile.subcategory})")
        print(f"Confidence: {profile.confidence:.2%}")
        print(f"Target Questions: {profile.suggested_questions[0]}")
        print("-" * 50)