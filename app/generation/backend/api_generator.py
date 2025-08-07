"""
API Generator - Creates REST/GraphQL APIs from schema
"""

from typing import Dict, List, Any
import json

class APIGenerator:
    """Generates API endpoints from database schema"""
    
    def __init__(self):
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict:
        return {
            "fastapi": {
                "main": self._fastapi_main_template,
                "route": self._fastapi_route_template,
                "model": self._fastapi_model_template
            }
        }
    
    async def generate_fastapi_app(self, schema: Dict, requirements: Dict) -> Dict[str, str]:
        """Generate complete FastAPI application"""
        
        files = {}
        
        # Main app file
        files['main.py'] = await self._generate_main_app(schema, requirements)
        
        # Models
        for table in schema.get('tables', []):
            model_file = f"models/{table['name']}.py"
            files[model_file] = await self._generate_model(table)
            
        # API routes
        for table in schema.get('tables', []):
            route_file = f"api/routes/{table['name']}.py"
            files[route_file] = await self._generate_routes(table)
            
        # Services
        for table in schema.get('tables', []):
            service_file = f"services/{table['name']}_service.py"
            files[service_file] = await self._generate_service(table)
            
        # MCP integrations
        for integration in requirements.get('integrations', []):
            integration_file = f"integrations/{integration['type']}.py"
            files[integration_file] = await self._generate_mcp_integration(integration)
            
        return files
    
    async def _generate_main_app(self, schema: Dict, requirements: Dict) -> str:
        return """from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.routes import router
from app.core.config import settings
from app.db.session import init_db

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    await init_db()
    yield
    logger.info("Shutting down application...")

app = FastAPI(
    title="{title}",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {{"status": "healthy"}}
""".format(title=requirements.get('app_name', 'Generated App'))
    
    async def _generate_model(self, table: Dict) -> str:
        fields = []
        for column in table.get('columns', []):
            field_type = self._map_sql_to_python_type(column['type'])
            nullable = "Optional[{type}] = None" if column.get('nullable') else field_type
            fields.append(f"    {column['name']}: {nullable}")
        
        return f"""from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class {table['name'].title()}(Base):
    __tablename__ = "{table['name']}"
    
    id = Column(Integer, primary_key=True, index=True)
{chr(10).join(fields)}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
"""
    
    async def _generate_routes(self, table: Dict) -> str:
        entity_name = table['name']
        entity_class = entity_name.title()
        
        return f"""from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.{entity_name} import {entity_class}
from app.schemas.{entity_name} import {entity_class}Create, {entity_class}Update, {entity_class}Response
from app.services.{entity_name}_service import {entity_class}Service

router = APIRouter(prefix="/{entity_name}s", tags=["{entity_name}s"])

@router.get("/", response_model=List[{entity_class}Response])
async def get_{entity_name}s(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    service = {entity_class}Service(db)
    return await service.get_all(skip=skip, limit=limit)

@router.get("/{{{entity_name}_id}}", response_model={entity_class}Response)
async def get_{entity_name}(
    {entity_name}_id: int,
    db: Session = Depends(get_db)
):
    service = {entity_class}Service(db)
    result = await service.get_by_id({entity_name}_id)
    if not result:
        raise HTTPException(status_code=404, detail="{entity_class} not found")
    return result

@router.post("/", response_model={entity_class}Response, status_code=201)
async def create_{entity_name}(
    {entity_name}: {entity_class}Create,
    db: Session = Depends(get_db)
):
    service = {entity_class}Service(db)
    return await service.create({entity_name})

@router.put("/{{{entity_name}_id}}", response_model={entity_class}Response)
async def update_{entity_name}(
    {entity_name}_id: int,
    {entity_name}: {entity_class}Update,
    db: Session = Depends(get_db)
):
    service = {entity_class}Service(db)
    result = await service.update({entity_name}_id, {entity_name})
    if not result:
        raise HTTPException(status_code=404, detail="{entity_class} not found")
    return result

@router.delete("/{{{entity_name}_id}}", status_code=204)
async def delete_{entity_name}(
    {entity_name}_id: int,
    db: Session = Depends(get_db)
):
    service = {entity_class}Service(db)
    if not await service.delete({entity_name}_id):
        raise HTTPException(status_code=404, detail="{entity_class} not found")
"""
    
    async def _generate_service(self, table: Dict) -> str:
        entity_name = table['name']
        entity_class = entity_name.title()
        
        return f"""from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.{entity_name} import {entity_class}
from app.schemas.{entity_name} import {entity_class}Create, {entity_class}Update
import logging

logger = logging.getLogger(__name__)

class {entity_class}Service:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[{entity_class}]:
        return self.db.query({entity_class}).offset(skip).limit(limit).all()
    
    async def get_by_id(self, {entity_name}_id: int) -> Optional[{entity_class}]:
        return self.db.query({entity_class}).filter({entity_class}.id == {entity_name}_id).first()
    
    async def create(self, {entity_name}_data: {entity_class}Create) -> {entity_class}:
        db_{entity_name} = {entity_class}(**{entity_name}_data.dict())
        self.db.add(db_{entity_name})
        self.db.commit()
        self.db.refresh(db_{entity_name})
        return db_{entity_name}
    
    async def update(self, {entity_name}_id: int, {entity_name}_data: {entity_class}Update) -> Optional[{entity_class}]:
        db_{entity_name} = await self.get_by_id({entity_name}_id)
        if not db_{entity_name}:
            return None
        
        for key, value in {entity_name}_data.dict(exclude_unset=True).items():
            setattr(db_{entity_name}, key, value)
        
        self.db.commit()
        self.db.refresh(db_{entity_name})
        return db_{entity_name}
    
    async def delete(self, {entity_name}_id: int) -> bool:
        db_{entity_name} = await self.get_by_id({entity_name}_id)
        if not db_{entity_name}:
            return False
        
        self.db.delete(db_{entity_name})
        self.db.commit()
        return True
"""
    
    async def _generate_mcp_integration(self, integration: Dict) -> str:
        return f"""# MCP Integration for {integration.get('type', 'unknown')}
from typing import Dict, Any
import httpx
import logging

logger = logging.getLogger(__name__)

class {integration.get('type', 'Unknown').title()}Integration:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "{integration.get('base_url', 'https://api.example.com')}"
    
    async def connect(self) -> bool:
        \"\"\"Establish connection to {integration.get('type')}\"\"\"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{{self.base_url}}/health",
                    headers={{"Authorization": f"Bearer {{self.api_key}}"}}
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection failed: {{e}}")
            return False
    
    async def sync_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Sync data with {integration.get('type')}\"\"\"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{{self.base_url}}/sync",
                json=data,
                headers={{"Authorization": f"Bearer {{self.api_key}}"}}
            )
            return response.json()
"""
    
    def _map_sql_to_python_type(self, sql_type: str) -> str:
        type_mapping = {
            "INTEGER": "int",
            "VARCHAR": "str",
            "TEXT": "str",
            "BOOLEAN": "bool",
            "DATETIME": "datetime",
            "FLOAT": "float",
            "DECIMAL": "float",
            "JSON": "Dict[str, Any]"
        }
        return type_mapping.get(sql_type.upper(), "Any")
    
    def _fastapi_main_template(self) -> str:
        return """from fastapi import FastAPI
from app.api import router

app = FastAPI()
app.include_router(router)
"""
    
    def _fastapi_route_template(self) -> str:
        return """from fastapi import APIRouter
router = APIRouter()
"""
    
    def _fastapi_model_template(self) -> str:
        return """from pydantic import BaseModel
class Model(BaseModel):
    pass
"""
    
    async def generate_graphql_api(self, schema: Dict, requirements: Dict) -> Dict[str, str]:
        """Generate GraphQL API from schema"""
        files = {}
        
        files['schema.graphql'] = await self._generate_graphql_schema(schema)
        files['resolvers.py'] = await self._generate_graphql_resolvers(schema)
        files['server.py'] = await self._generate_graphql_server(requirements)
        
        return files
    
    async def _generate_graphql_schema(self, schema: Dict) -> str:
        types = []
        for table in schema.get('tables', []):
            fields = []
            for column in table.get('columns', []):
                gql_type = self._map_sql_to_graphql_type(column['type'])
                nullable = "" if column.get('required') else ""
                fields.append(f"  {column['name']}: {gql_type}{nullable}")
            
            types.append(f"""type {table['name'].title()} {{
{chr(10).join(fields)}
}}""")
        
        return f"""# GraphQL Schema
{chr(10).join(types)}

type Query {{
  # Add query fields
}}

type Mutation {{
  # Add mutation fields
}}
"""
    
    async def _generate_graphql_resolvers(self, schema: Dict) -> str:
        return """from typing import Dict, Any

class Resolvers:
    @staticmethod
    async def resolve_query(parent, info, **kwargs):
        # Implement query resolvers
        pass
    
    @staticmethod
    async def resolve_mutation(parent, info, **kwargs):
        # Implement mutation resolvers
        pass
"""
    
    async def _generate_graphql_server(self, requirements: Dict) -> str:
        return """from ariadne import make_executable_schema, load_schema_from_path
from ariadne.asgi import GraphQL
from fastapi import FastAPI

type_defs = load_schema_from_path("schema.graphql")
schema = make_executable_schema(type_defs)

app = FastAPI()
app.mount("/graphql", GraphQL(schema, debug=True))
"""
    
    def _map_sql_to_graphql_type(self, sql_type: str) -> str:
        type_mapping = {
            "INTEGER": "Int",
            "VARCHAR": "String",
            "TEXT": "String",
            "BOOLEAN": "Boolean",
            "DATETIME": "String",
            "FLOAT": "Float",
            "DECIMAL": "Float",
            "JSON": "String"
        }
        return type_mapping.get(sql_type.upper(), "String")