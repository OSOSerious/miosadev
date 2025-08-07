from app.agents.base import BaseAgent
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)

class MCPIntegrationAgent(BaseAgent):
    def __init__(self):
        super().__init__("mcp_integration", "tool_connector")
        self.supported_tools = ["notion", "slack", "google", "github", "custom"]
        
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type", "integrate_tool")
        
        if task_type == "integrate_tool":
            return await self._integrate_tool(task)
        elif task_type == "discover_capabilities":
            return await self._discover_capabilities(task)
        elif task_type == "generate_connector":
            return await self._generate_connector(task)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _integrate_tool(self, task: Dict) -> Dict:
        tool_type = task.get("tool_type")
        requirements = task.get("requirements", {})
        
        if tool_type not in self.supported_tools:
            raise ValueError(f"Unsupported tool: {tool_type}")
        
        capabilities = await self._discover_mcp_capabilities(tool_type)
        
        connector_code = await self._generate_tool_connector(
            tool_type, 
            requirements, 
            capabilities
        )
        
        setup_instructions = await self._generate_setup_instructions(
            tool_type,
            requirements
        )
        
        return {
            "tool_type": tool_type,
            "capabilities": capabilities,
            "connector_code": connector_code,
            "setup_instructions": setup_instructions,
            "required_credentials": await self._identify_credentials(tool_type)
        }
    
    async def _discover_mcp_capabilities(self, tool_type: str) -> Dict:
        prompt = f"""
        Discover MCP (Model Context Protocol) capabilities for {tool_type}:
        
        Identify:
        1. Available operations
        2. Data types supported
        3. API endpoints
        4. Authentication methods
        5. Rate limits
        6. Webhooks/events
        
        Return as structured JSON.
        """
        
        result = await self.groq_service.complete(
            prompt,
            response_format={"type": "json_object"}
        )
        
        return json.loads(result)
    
    async def _generate_tool_connector(
        self, 
        tool_type: str, 
        requirements: Dict, 
        capabilities: Dict
    ) -> Dict[str, str]:
        
        files = {}
        
        files[f"connector.py"] = await self._generate_connector_class(
            tool_type, 
            capabilities
        )
        
        files[f"operations.py"] = await self._generate_operations(
            tool_type,
            requirements,
            capabilities
        )
        
        files[f"auth.py"] = await self._generate_auth_handler(
            tool_type,
            capabilities
        )
        
        files[f"models.py"] = await self._generate_data_models(
            tool_type,
            capabilities
        )
        
        files[f"sync.py"] = await self._generate_sync_logic(
            tool_type,
            requirements
        )
        
        return files
    
    async def _generate_connector_class(self, tool_type: str, capabilities: Dict) -> str:
        prompt = f"""
        Generate an MCP connector class for {tool_type}:
        
        Capabilities: {json.dumps(capabilities)}
        
        Include:
        1. Connection initialization
        2. Authentication setup
        3. Base methods for all operations
        4. Error handling
        5. Rate limiting
        6. Connection pooling
        """
        
        return await self.groq_service.complete(prompt)
    
    async def _generate_operations(
        self, 
        tool_type: str, 
        requirements: Dict, 
        capabilities: Dict
    ) -> str:
        prompt = f"""
        Generate operation methods for {tool_type} MCP connector:
        
        Requirements: {json.dumps(requirements)}
        Capabilities: {json.dumps(capabilities)}
        
        Include:
        1. CRUD operations
        2. Search/query methods
        3. Bulk operations
        4. Custom workflows
        5. Data transformation
        """
        
        return await self.groq_service.complete(prompt)
    
    async def _generate_auth_handler(self, tool_type: str, capabilities: Dict) -> str:
        prompt = f"""
        Generate authentication handler for {tool_type}:
        
        Capabilities: {json.dumps(capabilities)}
        
        Include:
        1. OAuth flow (if applicable)
        2. API key management
        3. Token refresh logic
        4. Credential storage
        5. Permission validation
        """
        
        return await self.groq_service.complete(prompt)
    
    async def _generate_data_models(self, tool_type: str, capabilities: Dict) -> str:
        prompt = f"""
        Generate data models for {tool_type} integration:
        
        Capabilities: {json.dumps(capabilities)}
        
        Include:
        1. Request/response models
        2. Entity models
        3. Event models
        4. Error models
        5. Validation schemas
        """
        
        return await self.groq_service.complete(prompt)
    
    async def _generate_sync_logic(self, tool_type: str, requirements: Dict) -> str:
        prompt = f"""
        Generate data synchronization logic for {tool_type}:
        
        Requirements: {json.dumps(requirements)}
        
        Include:
        1. Two-way sync
        2. Conflict resolution
        3. Change detection
        4. Batch processing
        5. Event listeners
        6. Retry logic
        """
        
        return await self.groq_service.complete(prompt)
    
    async def _generate_setup_instructions(self, tool_type: str, requirements: Dict) -> str:
        prompt = f"""
        Generate setup instructions for {tool_type} integration:
        
        Requirements: {json.dumps(requirements)}
        
        Include:
        1. Prerequisites
        2. API key/OAuth setup
        3. Permission configuration
        4. Testing steps
        5. Troubleshooting guide
        """
        
        return await self.groq_service.complete(prompt)
    
    async def _identify_credentials(self, tool_type: str) -> List[str]:
        credentials_map = {
            "notion": ["NOTION_API_KEY", "NOTION_WORKSPACE_ID"],
            "slack": ["SLACK_BOT_TOKEN", "SLACK_APP_TOKEN", "SLACK_SIGNING_SECRET"],
            "google": ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REFRESH_TOKEN"],
            "github": ["GITHUB_TOKEN", "GITHUB_APP_ID", "GITHUB_PRIVATE_KEY"]
        }
        
        return credentials_map.get(tool_type, [])
    
    async def _discover_capabilities(self, task: Dict) -> Dict:
        tool_type = task.get("tool_type")
        return await self._discover_mcp_capabilities(tool_type)
    
    async def _generate_connector(self, task: Dict) -> Dict:
        tool_type = task.get("tool_type")
        requirements = task.get("requirements", {})
        capabilities = await self._discover_mcp_capabilities(tool_type)
        
        return await self._generate_tool_connector(tool_type, requirements, capabilities)