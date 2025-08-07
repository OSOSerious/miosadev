"""
Model Context Protocol (MCP) Implementation
Handles communication with external tools and services
"""

from typing import Dict, Any, List, Optional
import json
import asyncio
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class MCPMessage:
    """Represents an MCP message"""
    
    def __init__(self, type: str, tool: str, operation: str, data: Dict[str, Any]):
        self.type = type  # request, response, event
        self.tool = tool
        self.operation = operation
        self.data = data
        self.id = self._generate_id()
        
    def _generate_id(self) -> str:
        import uuid
        return str(uuid.uuid4())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "tool": self.tool,
            "operation": self.operation,
            "data": self.data
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())

class MCPConnector(ABC):
    """Abstract base class for MCP connectors"""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the tool"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the tool"""
        pass
    
    @abstractmethod
    async def send_message(self, message: MCPMessage) -> MCPMessage:
        """Send a message and receive response"""
        pass
    
    @abstractmethod
    async def get_capabilities(self) -> Dict:
        """Get tool capabilities"""
        pass

class MCPProtocol:
    """Main MCP protocol handler"""
    
    def __init__(self):
        self.connectors: Dict[str, MCPConnector] = {}
        self.message_queue = asyncio.Queue()
        self.response_handlers = {}
        
    async def register_connector(self, tool_name: str, connector: MCPConnector) -> bool:
        """Register a new tool connector"""
        try:
            if await connector.connect():
                self.connectors[tool_name] = connector
                logger.info(f"Registered connector for {tool_name}")
                return True
            else:
                logger.error(f"Failed to connect to {tool_name}")
                return False
        except Exception as e:
            logger.error(f"Error registering connector for {tool_name}: {e}")
            return False
    
    async def unregister_connector(self, tool_name: str) -> None:
        """Unregister a tool connector"""
        if tool_name in self.connectors:
            await self.connectors[tool_name].disconnect()
            del self.connectors[tool_name]
            logger.info(f"Unregistered connector for {tool_name}")
    
    async def send_request(self, tool: str, operation: str, data: Dict) -> Optional[Dict]:
        """Send a request to a tool"""
        if tool not in self.connectors:
            logger.error(f"No connector registered for {tool}")
            return None
        
        message = MCPMessage("request", tool, operation, data)
        
        try:
            response = await self.connectors[tool].send_message(message)
            return response.data if response else None
        except Exception as e:
            logger.error(f"Error sending request to {tool}: {e}")
            return None
    
    async def discover_capabilities(self, tool: str) -> Optional[Dict]:
        """Discover capabilities of a tool"""
        if tool not in self.connectors:
            logger.error(f"No connector registered for {tool}")
            return None
        
        try:
            return await self.connectors[tool].get_capabilities()
        except Exception as e:
            logger.error(f"Error discovering capabilities for {tool}: {e}")
            return None
    
    async def batch_request(self, requests: List[Dict]) -> List[Optional[Dict]]:
        """Send multiple requests in parallel"""
        tasks = []
        
        for req in requests:
            task = self.send_request(req["tool"], req["operation"], req.get("data", {}))
            tasks.append(task)
        
        return await asyncio.gather(*tasks)
    
    async def subscribe_to_events(self, tool: str, event_type: str, handler: callable) -> None:
        """Subscribe to events from a tool"""
        key = f"{tool}:{event_type}"
        
        if key not in self.response_handlers:
            self.response_handlers[key] = []
        
        self.response_handlers[key].append(handler)
        logger.info(f"Subscribed to {event_type} events from {tool}")
    
    async def process_event(self, message: MCPMessage) -> None:
        """Process an incoming event"""
        key = f"{message.tool}:{message.operation}"
        
        if key in self.response_handlers:
            for handler in self.response_handlers[key]:
                try:
                    await handler(message.data)
                except Exception as e:
                    logger.error(f"Error processing event: {e}")
    
    def get_connected_tools(self) -> List[str]:
        """Get list of connected tools"""
        return list(self.connectors.keys())
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all connectors"""
        health = {}
        
        for tool, connector in self.connectors.items():
            try:
                # Send a simple health check request
                response = await self.send_request(tool, "health", {})
                health[tool] = response is not None
            except:
                health[tool] = False
        
        return health

class MCPCapabilities:
    """Defines capabilities that can be discovered via MCP"""
    
    def __init__(self):
        self.operations = []
        self.data_types = []
        self.events = []
        self.limits = {}
        
    def add_operation(self, name: str, description: str, parameters: Dict) -> None:
        """Add an operation capability"""
        self.operations.append({
            "name": name,
            "description": description,
            "parameters": parameters
        })
    
    def add_data_type(self, name: str, schema: Dict) -> None:
        """Add a data type capability"""
        self.data_types.append({
            "name": name,
            "schema": schema
        })
    
    def add_event(self, name: str, description: str) -> None:
        """Add an event capability"""
        self.events.append({
            "name": name,
            "description": description
        })
    
    def set_limit(self, name: str, value: Any) -> None:
        """Set a limit/constraint"""
        self.limits[name] = value
    
    def to_dict(self) -> Dict:
        """Convert capabilities to dictionary"""
        return {
            "operations": self.operations,
            "data_types": self.data_types,
            "events": self.events,
            "limits": self.limits
        }

class MCPSecurity:
    """Handles security for MCP connections"""
    
    def __init__(self):
        self.api_keys = {}
        self.oauth_tokens = {}
        self.permissions = {}
        
    def add_api_key(self, tool: str, api_key: str) -> None:
        """Store API key for a tool"""
        self.api_keys[tool] = api_key
    
    def add_oauth_token(self, tool: str, token: Dict) -> None:
        """Store OAuth token for a tool"""
        self.oauth_tokens[tool] = token
    
    def get_credentials(self, tool: str) -> Optional[Dict]:
        """Get credentials for a tool"""
        creds = {}
        
        if tool in self.api_keys:
            creds["api_key"] = self.api_keys[tool]
        
        if tool in self.oauth_tokens:
            creds["oauth_token"] = self.oauth_tokens[tool]
        
        return creds if creds else None
    
    def check_permission(self, tool: str, operation: str) -> bool:
        """Check if operation is permitted for a tool"""
        if tool not in self.permissions:
            return True  # Default allow if no permissions set
        
        tool_perms = self.permissions[tool]
        
        if "allow_all" in tool_perms and tool_perms["allow_all"]:
            return True
        
        if "allowed_operations" in tool_perms:
            return operation in tool_perms["allowed_operations"]
        
        if "denied_operations" in tool_perms:
            return operation not in tool_perms["denied_operations"]
        
        return True
    
    def set_permissions(self, tool: str, permissions: Dict) -> None:
        """Set permissions for a tool"""
        self.permissions[tool] = permissions