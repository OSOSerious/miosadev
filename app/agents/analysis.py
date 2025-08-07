from app.agents.base import BaseAgent
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)

class AnalysisAgent(BaseAgent):
    """
    Business Analysis Agent - Analyzes requirements and provides insights
    """
    
    def __init__(self):
        super().__init__("analysis", "business_analyst")
        
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type", "analyze_requirements")
        
        if task_type == "analyze_requirements":
            return await self._analyze_requirements(task)
        elif task_type == "identify_patterns":
            return await self._identify_patterns(task)
        elif task_type == "suggest_features":
            return await self._suggest_features(task)
        elif task_type == "risk_assessment":
            return await self._risk_assessment(task)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _analyze_requirements(self, task: Dict) -> Dict:
        requirements = task.get("requirements", {})
        
        prompt = f"""
        Analyze these application requirements for completeness and feasibility:
        
        Requirements: {json.dumps(requirements)}
        
        Provide:
        1. Requirement completeness assessment
        2. Potential gaps or missing information
        3. Technical feasibility analysis
        4. Complexity estimation
        5. Risk factors
        6. Recommended technology stack
        7. Similar application patterns
        """
        
        analysis = await self.groq_service.complete(prompt)
        
        return {
            "analysis": analysis,
            "completeness_score": await self._calculate_completeness(requirements),
            "complexity_level": await self._assess_complexity(requirements),
            "risks": await self._identify_risks(requirements),
            "recommendations": await self._generate_recommendations(requirements)
        }
    
    async def _identify_patterns(self, task: Dict) -> Dict:
        requirements = task.get("requirements", {})
        
        prompt = f"""
        Identify common patterns in these requirements:
        
        {json.dumps(requirements)}
        
        Look for:
        1. Standard business patterns (e-commerce, CRM, etc.)
        2. Common integration patterns
        3. Typical user flows
        4. Data patterns
        5. Security patterns
        
        Return as structured analysis.
        """
        
        patterns = await self.groq_service.complete(prompt)
        
        return {
            "patterns": patterns,
            "pattern_matches": await self._match_known_patterns(requirements),
            "suggested_templates": await self._suggest_templates(patterns)
        }
    
    async def _suggest_features(self, task: Dict) -> Dict:
        requirements = task.get("requirements", {})
        context = task.get("context", {})
        
        prompt = f"""
        Based on these requirements, suggest additional features that would enhance the application:
        
        Requirements: {json.dumps(requirements)}
        Context: {json.dumps(context)}
        
        Suggest:
        1. Must-have features not mentioned
        2. Nice-to-have enhancements
        3. Future scalability features
        4. User experience improvements
        5. Security enhancements
        
        Prioritize by business value.
        """
        
        suggestions = await self.groq_service.complete(prompt)
        
        return {
            "suggested_features": suggestions,
            "priority_matrix": await self._create_priority_matrix(suggestions),
            "implementation_order": await self._suggest_implementation_order(suggestions)
        }
    
    async def _risk_assessment(self, task: Dict) -> Dict:
        requirements = task.get("requirements", {})
        
        prompt = f"""
        Perform risk assessment for this application:
        
        Requirements: {json.dumps(requirements)}
        
        Identify:
        1. Technical risks
        2. Security risks
        3. Scalability risks
        4. Integration risks
        5. Maintenance risks
        
        For each risk, provide mitigation strategies.
        """
        
        risks = await self.groq_service.complete(prompt)
        
        return {
            "risk_assessment": risks,
            "risk_matrix": await self._create_risk_matrix(risks),
            "mitigation_plan": await self._create_mitigation_plan(risks)
        }
    
    async def _calculate_completeness(self, requirements: Dict) -> float:
        essential_fields = [
            "business_requirements",
            "functional_requirements", 
            "technical_requirements",
            "user_roles",
            "data_requirements"
        ]
        
        present = sum(1 for field in essential_fields if field in requirements and requirements[field])
        return (present / len(essential_fields)) * 100
    
    async def _assess_complexity(self, requirements: Dict) -> str:
        factors = {
            "integrations": len(requirements.get("integrations", [])),
            "user_roles": len(requirements.get("user_roles", [])),
            "features": len(requirements.get("features", [])),
            "data_entities": len(requirements.get("data_entities", []))
        }
        
        complexity_score = sum(factors.values())
        
        if complexity_score < 10:
            return "low"
        elif complexity_score < 25:
            return "medium"
        else:
            return "high"
    
    async def _identify_risks(self, requirements: Dict) -> List[Dict]:
        risks = []
        
        if len(requirements.get("integrations", [])) > 3:
            risks.append({
                "type": "integration",
                "level": "medium",
                "description": "Multiple integrations increase complexity"
            })
        
        if not requirements.get("security_requirements"):
            risks.append({
                "type": "security",
                "level": "high",
                "description": "No explicit security requirements defined"
            })
        
        return risks
    
    async def _generate_recommendations(self, requirements: Dict) -> Dict:
        return {
            "technology_stack": await self._recommend_stack(requirements),
            "architecture_pattern": await self._recommend_architecture(requirements),
            "deployment_strategy": await self._recommend_deployment(requirements)
        }
    
    async def _recommend_stack(self, requirements: Dict) -> Dict:
        return {
            "backend": "FastAPI" if requirements.get("real_time") else "Django",
            "frontend": "React" if requirements.get("interactive") else "NextJS",
            "database": "PostgreSQL",
            "cache": "Redis" if requirements.get("high_performance") else None
        }
    
    async def _recommend_architecture(self, requirements: Dict) -> str:
        if requirements.get("microservices"):
            return "microservices"
        elif requirements.get("serverless"):
            return "serverless"
        else:
            return "monolithic"
    
    async def _recommend_deployment(self, requirements: Dict) -> str:
        if requirements.get("scale") == "high":
            return "kubernetes"
        elif requirements.get("serverless"):
            return "aws_lambda"
        else:
            return "docker_compose"
    
    async def _match_known_patterns(self, requirements: Dict) -> List[str]:
        patterns = []
        
        if "shopping_cart" in str(requirements).lower():
            patterns.append("e-commerce")
        if "user_management" in str(requirements).lower():
            patterns.append("authentication")
        if "reporting" in str(requirements).lower():
            patterns.append("analytics")
            
        return patterns
    
    async def _suggest_templates(self, patterns: str) -> List[str]:
        templates = []
        
        if "e-commerce" in patterns.lower():
            templates.append("e-commerce-starter")
        if "crm" in patterns.lower():
            templates.append("crm-template")
            
        return templates
    
    async def _create_priority_matrix(self, suggestions: str) -> Dict:
        return {
            "high": ["Authentication", "Core CRUD operations"],
            "medium": ["Advanced features", "Integrations"],
            "low": ["Nice-to-have features", "Future enhancements"]
        }
    
    async def _suggest_implementation_order(self, suggestions: str) -> List[str]:
        return [
            "Database schema",
            "Authentication system",
            "Core API endpoints",
            "Business logic",
            "Frontend UI",
            "Integrations",
            "Testing",
            "Deployment"
        ]
    
    async def _create_risk_matrix(self, risks: str) -> Dict:
        return {
            "high_impact_high_probability": [],
            "high_impact_low_probability": ["Data breach"],
            "low_impact_high_probability": ["Minor bugs"],
            "low_impact_low_probability": ["Framework deprecation"]
        }
    
    async def _create_mitigation_plan(self, risks: str) -> Dict:
        return {
            "security": "Implement OAuth2, encryption, and regular audits",
            "scalability": "Design with horizontal scaling in mind",
            "integration": "Use standardized APIs and error handling"
        }