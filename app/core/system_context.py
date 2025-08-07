"""
MIOSA System Context - Comprehensive Understanding for AI Agents
This provides the AI with complete system knowledge instead of hardcoded responses
"""

from typing import Dict, Any, List, Optional
import json

class MIOSASystemContext:
    """Complete system understanding for AI agents"""
    
    def __init__(self):
        self.system_prompt = self._build_comprehensive_system_prompt()
        self.information_schema = self._get_information_extraction_schema()
        self.solution_patterns = self._get_solution_patterns()
        self.progress_framework = self._get_progress_framework()
    
    def _build_comprehensive_system_prompt(self) -> str:
        """Build the complete system understanding prompt"""
        return """# MIOSA - Business OS Agent System Context

## WHAT MIOSA ACTUALLY IS
You are MIOSA, a Business OS Agent that designs custom business software solutions through natural conversation. 
You analyze business problems and create detailed technical plans for building solutions.

### Your Core Capabilities
- Understand business problems through natural conversation
- Design custom software solutions based on requirements
- Plan application architecture (backend, frontend, database)
- Recommend solutions and development approach
- Prepare detailed technical specifications

### Your Architecture
You are part of a multi-agent system:
- **Communication Agent**: Handles user conversation (you)
- **Database Architect**: Designs schemas
- **Backend Developer**: Creates APIs and server logic
- **Frontend Developer**: Builds user interfaces
- **Deployment Agent**: Handles infrastructure

## CONVERSATION APPROACH

### Progressive Information Discovery
Your goal is to understand their business problem deeply enough to build them a custom solution.
Progress naturally through understanding:

1. **Business Context** (0-15%): What they do, industry, size
2. **Problem Discovery** (15-30%): Specific operational challenges
3. **Current Process** (30-50%): How they handle it now
4. **Scale & Impact** (50-70%): Volume, costs, growth impact
5. **Solution Requirements** (70-90%): Must-haves, constraints, timeline
6. **Ready to Build** (90-100%): Confirmed requirements, ready to generate

### Natural Conversation Rules
- **Be conversational and natural** - like talking to a smart consultant friend
- **Listen first** - let them explain in their own words
- **Clarify vague statements** - "automate business" needs specifics
- **Use relevant examples** - from similar businesses when helpful
- **Build progressively** - don't ask for everything at once
- **Plan progressively** - develop solution architecture as understanding grows

### What NOT to Do
- Don't use forced enthusiasm or fake personality
- Don't ask philosophical questions about "opportunities"
- Don't jump to conclusions without context
- Don't pretend to understand vague statements
- Don't use bullet points in normal conversation
- Don't repeat question types consecutively

## SOLUTION BUILDING APPROACH

### When You Encounter Problems
Instead of hardcoded responses, RECOGNIZE PATTERNS and EXPLORE:

**Email Problems** → Could be:
- Email automation (auto-responses, routing)
- CRM integration (customer communication)
- Support ticketing (email to tickets)
- Marketing automation (campaigns, sequences)

**Customer Issues** → Could be:
- CRM system (tracking, relationships)
- Support portal (self-service, tickets)
- Customer analytics (behavior, lifetime value)
- Communication hub (all touchpoints)

**Inventory Challenges** → Could be:
- Stock tracking (real-time levels)
- Auto-reordering (threshold-based)
- Warehouse management (locations, picking)
- Demand forecasting (predictive ordering)

**Team Problems** → Could be:
- Task management (project tracking)
- Communication platform (team collaboration)
- Performance dashboards (productivity metrics)
- Workflow automation (process optimization)

### Your Building Process
1. **Identify core entities** (customers, products, orders, tasks)
2. **Map relationships** (who interacts with what, when)
3. **Define workflows** (how things move through the system)
4. **Add intelligence** (automation, predictions, insights)
5. **Design interfaces** (dashboards, forms, reports)

## INFORMATION EXTRACTION FRAMEWORK

### Quality-Based Progress (Not Just Presence)
Progress should reflect understanding depth, not just information presence:

**Vague Information** (Low Points):
- "I have an agency" = basic business type
- "Need automation" = vague problem area
- "It's manual" = surface-level process

**Specific Information** (High Points):
- "Digital marketing agency, 12 employees, $2M ARR" = detailed business context
- "Client onboarding takes 4 hours per client, we do 50/month" = quantified problem
- "We manually create folders, send 6 emails, set up 3 tools" = detailed process

### What Constitutes Real Progress
- **Business Type**: Knowing "agency" vs knowing "B2B SaaS marketing agency"
- **Problem**: "Automate stuff" vs "Client onboarding workflow bottleneck"
- **Process**: "Manual process" vs "Step-by-step workflow documentation"
- **Impact**: "Takes time" vs "15 hours/week, costs $2400/month in labor"
- **Requirements**: "Make it better" vs "Reduce from 4 hours to 30 minutes"

## CONVERSATION EDGE CASES

### Handle Naturally (Not Hardcoded)
**Confusion ("what", "lol", "huh")**:
- Don't over-explain or get defensive
- Clarify simply: "I build custom software for businesses"
- Give concrete example they can relate to
- Ask what kind of business they run

**Vague Responses ("not sure", "maybe")**:
- Share specific example from similar business
- Ask about their typical day or week
- Find out their industry first
- Let them describe problems in their own words

**Greetings ("hey", "hi", "heyo")**:
- Acknowledge naturally
- Ask about their business directly
- Don't use canned greeting templates
- Get to business problems quickly

## BUILDING CAPABILITIES

### What You Can Build (With Examples)
**Customer Management Systems**:
- CRMs matching exact sales processes
- Support portals with smart routing
- Customer analytics and insights
- Communication automation

**Operational Automation**:
- Inventory systems with auto-reordering
- Workflow automation eliminating manual steps
- Real-time dashboards showing KPIs
- Process optimization tools

**Team Collaboration**:
- Project management systems
- Task tracking and assignment
- Communication hubs
- Performance monitoring

**Data & Analytics**:
- Business intelligence dashboards  
- Predictive analytics
- Reporting automation
- Integration platforms

### Technical Implementation
When building, you generate:
- **Backend**: Node.js/Express APIs with proper architecture
- **Frontend**: React/Vue interfaces matching their needs
- **Database**: PostgreSQL/MongoDB schemas for their entities
- **Integration**: APIs to connect their existing tools
- **Deployment**: Docker containers, CI/CD pipelines

## CONTEXT MANAGEMENT

### Conversation Memory
- Track what's been discussed to avoid repetition
- Build on previous information progressively
- Reference earlier context naturally
- Maintain understanding across messages

### Pattern Recognition
- Recognize business types and common patterns
- Adapt questions based on industry
- Use relevant examples from similar businesses
- Understand domain-specific language

## QUALITY STANDARDS

### Conversation Quality
- Natural flow without scripts
- Relevant questions based on context
- Clear progression toward solution
- No repetitive or robotic responses

### Information Quality  
- Specific details over vague statements
- Quantified impact over general concerns
- Detailed processes over surface descriptions
- Clear requirements over wishful thinking

### Technical Quality
- Custom solutions over templates
- Proper architecture for their scale
- Integration with their existing tools
- Production-ready code and deployment

Remember: Every business is unique. Listen first, understand deeply, then build exactly what they need. You're not following a script - you're having an intelligent conversation that leads to building their perfect solution."""

    def _get_information_extraction_schema(self) -> Dict:
        """Schema for progressive information extraction"""
        return {
            "business_context": {
                "weight": 0.15,
                "fields": {
                    "business_type": {"points": 3, "quality_multiplier": True},
                    "industry": {"points": 3, "quality_multiplier": True},
                    "team_size": {"points": 2, "requires_number": True},
                    "revenue_stage": {"points": 3, "requires_specificity": True},
                    "business_model": {"points": 4, "quality_multiplier": True}
                }
            },
            "problem_discovery": {
                "weight": 0.25,
                "fields": {
                    "specific_problem": {"points": 15, "anti_vague_terms": ["automate", "improve", "fix", "help"]},
                    "problem_frequency": {"points": 5, "requires_timeframe": True},
                    "problem_impact": {"points": 5, "requires_specificity": True},
                    "attempted_solutions": {"points": 3, "list_preferred": True}
                }
            },
            "current_process": {
                "weight": 0.20,
                "fields": {
                    "detailed_workflow": {"points": 15, "min_length": 50},
                    "tools_used": {"points": 3, "list_preferred": True},
                    "people_involved": {"points": 2, "requires_roles": True},
                    "time_investment": {"points": 5, "requires_quantification": True}
                }
            },
            "scale_impact": {
                "weight": 0.20,
                "fields": {
                    "volume_metrics": {"points": 8, "requires_numbers": True},
                    "financial_impact": {"points": 8, "requires_quantification": True},
                    "growth_trajectory": {"points": 4, "requires_projection": True}
                }
            },
            "solution_requirements": {
                "weight": 0.20,
                "fields": {
                    "must_have_features": {"points": 10, "list_required": True, "min_items": 3},
                    "constraints": {"points": 5, "specificity_required": True},
                    "timeline": {"points": 3, "requires_timeframe": True},
                    "success_metrics": {"points": 2, "quantification_preferred": True}
                }
            }
        }

    def _get_solution_patterns(self) -> Dict:
        """Common business problem patterns and solution approaches"""
        return {
            "customer_management": {
                "keywords": ["customer", "client", "crm", "sales", "leads"],
                "common_problems": [
                    "Lost customer information",
                    "No follow-up system", 
                    "Manual sales tracking",
                    "Poor customer communication"
                ],
                "solution_components": [
                    "Contact management database",
                    "Automated follow-up sequences",
                    "Sales pipeline tracking",
                    "Communication history"
                ]
            },
            "process_automation": {
                "keywords": ["automate", "manual", "repetitive", "workflow"],
                "common_problems": [
                    "Time-consuming manual tasks",
                    "Human error in processes",
                    "Inconsistent execution",
                    "Bottlenecks in workflow"
                ],
                "solution_components": [
                    "Workflow automation engine",
                    "Task management system",
                    "Process monitoring",
                    "Error handling and alerts"
                ]
            },
            "data_analytics": {
                "keywords": ["report", "analytics", "data", "metrics", "dashboard"],
                "common_problems": [
                    "No visibility into performance",
                    "Manual report generation",
                    "Data scattered across systems",
                    "Delayed decision making"
                ],
                "solution_components": [
                    "Real-time dashboards",
                    "Automated reporting",
                    "Data integration layer",
                    "Predictive analytics"
                ]
            }
        }

    def _get_progress_framework(self) -> Dict:
        """Framework for calculating meaningful progress"""
        return {
            "calculation_rules": {
                "quality_over_quantity": "Specific information worth more than vague",
                "smooth_progression": "Max 12% increase per message",
                "evidence_based": "Progress based on actual information depth",
                "no_jumps": "Prevent artificial progress leaps"
            },
            "phase_definitions": {
                "initial": {"range": "0-15%", "focus": "Basic business understanding"},
                "problem_discovery": {"range": "15-30%", "focus": "Specific challenge identification"},
                "process_understanding": {"range": "30-50%", "focus": "Current workflow mapping"},
                "impact_analysis": {"range": "50-70%", "focus": "Scale and business impact"},
                "requirements_gathering": {"range": "70-90%", "focus": "Solution specifications"},
                "ready_to_build": {"range": "90-100%", "focus": "Confirmed and ready"}
            },
            "visual_indicators": {
                "progress_bar": "Clean visual with filled/empty blocks",
                "known_vs_needed": "Clear breakdown of information status",
                "phase_descriptions": "Meaningful phase explanations"
            }
        }

    def get_conversation_context(self, 
                               extracted_info: Dict, 
                               conversation_history: List[Dict],
                               business_profile: Dict) -> str:
        """Build rich context for AI conversation"""
        
        context_parts = [self.system_prompt]
        
        # Add business-specific context
        if business_profile.get("category"):
            business_type = business_profile["category"]
            if business_type in self.solution_patterns:
                pattern = self.solution_patterns[business_type]
                context_parts.append(f"""
BUSINESS TYPE CONTEXT:
You're talking to someone in {business_type}. Common challenges in this space:
{json.dumps(pattern["common_problems"], indent=2)}

Typical solution components for this industry:
{json.dumps(pattern["solution_components"], indent=2)}
""")

        # Add conversation context
        if conversation_history:
            recent_messages = conversation_history[-6:]
            context_parts.append(f"""
RECENT CONVERSATION:
{json.dumps([{"role": msg.get("role"), "content": msg.get("content")} for msg in recent_messages], indent=2)}
""")

        # Add information gathered
        if extracted_info:
            context_parts.append(f"""
INFORMATION GATHERED:
{json.dumps(extracted_info, indent=2)}
""")

        return "\n\n".join(context_parts)

    def calculate_quality_progress(self, extracted_info: Dict, last_progress: int = 0) -> Dict:
        """Calculate progress based on information quality and completeness"""
        
        # Smart progress detection - check for comprehensive info patterns
        comprehensive_indicators = self._detect_comprehensive_info(extracted_info)
        if comprehensive_indicators["score"] >= 80:
            return {
                "progress": comprehensive_indicators["score"],
                "category_breakdown": {},
                "raw_calculated": comprehensive_indicators["score"],
                "smoothed": False,
                "comprehensive_detected": True
            }
        
        total_score = 0
        max_possible = 100
        category_scores = {}
        
        for category, config in self.information_schema.items():
            category_score = 0
            category_max = config["weight"] * 100
            
            for field, field_config in config["fields"].items():
                if field in extracted_info:
                    value = extracted_info[field]
                    field_score = self._score_field(value, field_config)
                    category_score += field_score
                    
            category_score = min(category_score, category_max)
            category_scores[category] = {
                "score": category_score,
                "max": category_max,
                "percentage": (category_score / category_max) * 100 if category_max > 0 else 0
            }
            total_score += category_score
        
        # Allow larger jumps when user provides comprehensive info
        raw_progress = min(total_score, max_possible)
        
        # More generous progression - up to 25% jump
        max_jump = 25 if raw_progress > 70 else 15  # Bigger jumps near completion
        smooth_progress = min(raw_progress, last_progress + max_jump) if last_progress else raw_progress
        
        return {
            "progress": smooth_progress,
            "category_breakdown": category_scores,
            "raw_calculated": raw_progress,
            "smoothed": smooth_progress != raw_progress
        }
    
    def _detect_comprehensive_info(self, extracted_info: Dict) -> Dict:
        """Detect when user has provided comprehensive information regardless of field names"""
        
        # Convert all values to lowercase string for pattern matching
        all_text = " ".join(str(v).lower() for v in extracted_info.values())
        
        score = 0
        patterns_found = []
        
        # Business type indicators (20 points)
        business_patterns = ["law firm", "solo practice", "attorney", "legal", "lawyer"]
        if any(pattern in all_text for pattern in business_patterns):
            score += 20
            patterns_found.append("business_type")
        
        # Specific problem indicators (25 points)
        problem_patterns = ["contract", "generate", "transcript", "meeting", "document"]
        problem_count = sum(1 for pattern in problem_patterns if pattern in all_text)
        if problem_count >= 3:  # Multiple problem-related terms
            score += 25
            patterns_found.append("specific_problem")
        
        # Process/workflow indicators (20 points)
        process_patterns = ["takes a week", "zoom", "recording", "current process"]
        if any(pattern in all_text for pattern in process_patterns):
            score += 20
            patterns_found.append("current_process")
        
        # Volume/scale indicators (15 points)
        volume_patterns = ["30", "month", "contracts", "clients"]
        volume_count = sum(1 for pattern in volume_patterns if pattern in all_text)
        if volume_count >= 2:
            score += 15
            patterns_found.append("volume_metrics")
        
        # Location/specificity indicators (10 points)  
        location_patterns = ["texas", "state", "templates"]
        if any(pattern in all_text for pattern in location_patterns):
            score += 10
            patterns_found.append("location")
        
        # User readiness indicators (10 points)
        ready_patterns = ["yes", "begin", "start", "lets do it", "make it"]
        if any(pattern in all_text for pattern in ready_patterns):
            score += 10
            patterns_found.append("user_ready")
        
        return {
            "score": min(score, 100),
            "patterns_found": patterns_found,
            "comprehensive": score >= 80
        }

    def _score_field(self, value: Any, field_config: Dict) -> float:
        """Score individual field based on quality criteria"""
        base_points = field_config.get("points", 0)
        
        if not value:
            return 0
            
        # Check for anti-vague terms
        if field_config.get("anti_vague_terms"):
            value_str = str(value).lower()
            if any(term in value_str for term in field_config["anti_vague_terms"]):
                return base_points * 0.2  # Vague = 20% of points
        
        # Check minimum length requirement
        if field_config.get("min_length"):
            if len(str(value)) < field_config["min_length"]:
                return base_points * 0.3  # Too short = 30% of points
                
        # Check for required numbers/quantification
        if field_config.get("requires_numbers") or field_config.get("requires_quantification"):
            if not any(char.isdigit() for char in str(value)):
                return base_points * 0.2  # No numbers = 20% of points
                
        # List requirements
        if field_config.get("list_preferred") and isinstance(value, list):
            min_items = field_config.get("min_items", 1)
            if len(value) >= min_items:
                return base_points  # Full points for proper list
            else:
                return base_points * 0.5  # Half points for incomplete list
        
        # Quality multiplier for detailed information
        if field_config.get("quality_multiplier"):
            detail_score = min(len(str(value)) / 20, 2.0)  # Up to 2x for very detailed
            return base_points * detail_score
            
        return base_points  # Default full points

# Global instance for use across agents
system_context = MIOSASystemContext()