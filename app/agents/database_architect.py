from app.agents.base import BaseAgent
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)

class DatabaseArchitectAgent(BaseAgent):
    def __init__(self):
        super().__init__("database_architect", "schema_designer")
        
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type", "design_schema")
        
        if task_type == "design_schema":
            return await self._design_schema(task)
        elif task_type == "optimize_schema":
            return await self._optimize_schema(task)
        elif task_type == "generate_migrations":
            return await self._generate_migrations(task)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _design_schema(self, task: Dict) -> Dict:
        requirements = task.get("requirements", {})
        
        prompt = f"""
        Design a complete database schema for this application:
        
        Requirements: {json.dumps(requirements)}
        
        Consider:
        1. All entities and their relationships
        2. Field types and constraints
        3. Indexes for performance
        4. Foreign key relationships
        5. Audit fields (created_at, updated_at, etc.)
        
        Return a detailed schema design with:
        1. Table definitions
        2. Relationships
        3. Indexes
        4. Constraints
        5. Design rationale
        """
        
        schema_design = await self.groq_service.complete(prompt)
        
        sql_schema = await self._generate_sql_schema(schema_design)
        
        relationships = await self._extract_relationships(schema_design)
        
        return {
            "design": schema_design,
            "sql_schema": sql_schema,
            "relationships": relationships,
            "tables": await self._parse_tables(sql_schema)
        }
    
    async def _generate_sql_schema(self, design: str) -> str:
        prompt = f"""
        Generate complete PostgreSQL schema from this design:
        
        {design}
        
        Include:
        1. CREATE TABLE statements
        2. Primary keys
        3. Foreign keys
        4. Indexes
        5. Constraints
        6. Comments
        
        Return valid PostgreSQL DDL.
        """
        
        return await self.groq_service.complete(prompt)
    
    async def _extract_relationships(self, design: str) -> List[Dict]:
        prompt = f"""
        Extract all database relationships from this design:
        
        {design}
        
        For each relationship, identify:
        1. Parent table
        2. Child table
        3. Relationship type (one-to-one, one-to-many, many-to-many)
        4. Foreign key fields
        5. Cascade rules
        
        Return as JSON array.
        """
        
        result = await self.groq_service.complete(
            prompt,
            response_format={"type": "json_object"}
        )
        
        return json.loads(result).get("relationships", [])
    
    async def _parse_tables(self, sql_schema: str) -> List[Dict]:
        prompt = f"""
        Parse this SQL schema and extract table information:
        
        {sql_schema}
        
        For each table, extract:
        1. Table name
        2. Columns with types
        3. Primary key
        4. Foreign keys
        5. Indexes
        
        Return as JSON array.
        """
        
        result = await self.groq_service.complete(
            prompt,
            response_format={"type": "json_object"}
        )
        
        return json.loads(result).get("tables", [])
    
    async def _optimize_schema(self, task: Dict) -> Dict:
        schema = task.get("schema", {})
        performance_requirements = task.get("performance_requirements", {})
        
        prompt = f"""
        Optimize this database schema for performance:
        
        Schema: {json.dumps(schema)}
        Performance Requirements: {json.dumps(performance_requirements)}
        
        Suggest:
        1. Additional indexes
        2. Denormalization opportunities
        3. Partitioning strategies
        4. Caching recommendations
        5. Query optimization tips
        """
        
        optimization = await self.groq_service.complete(prompt)
        
        return {
            "recommendations": optimization,
            "optimized_schema": await self._apply_optimizations(schema, optimization)
        }
    
    async def _apply_optimizations(self, schema: Dict, optimizations: str) -> Dict:
        prompt = f"""
        Apply these optimizations to the schema:
        
        Original Schema: {json.dumps(schema)}
        Optimizations: {optimizations}
        
        Return the optimized schema.
        """
        
        result = await self.groq_service.complete(
            prompt,
            response_format={"type": "json_object"}
        )
        
        return json.loads(result)
    
    async def _generate_migrations(self, task: Dict) -> Dict:
        schema = task.get("schema", {})
        
        prompt = f"""
        Generate database migration files for this schema:
        
        {json.dumps(schema)}
        
        Create:
        1. Up migration (create tables)
        2. Down migration (drop tables)
        3. Seed data migration
        
        Use standard migration format.
        """
        
        migrations = await self.groq_service.complete(prompt)
        
        return {
            "up": migrations,
            "down": await self._generate_down_migration(schema),
            "seed": await self._generate_seed_data(schema)
        }
    
    async def _generate_down_migration(self, schema: Dict) -> str:
        tables = schema.get("tables", [])
        return "\n".join([f"DROP TABLE IF EXISTS {table['name']} CASCADE;" for table in tables])
    
    async def _generate_seed_data(self, schema: Dict) -> str:
        prompt = f"""
        Generate sample seed data for this schema:
        
        {json.dumps(schema)}
        
        Create realistic sample data for testing.
        """
        
        return await self.groq_service.complete(prompt)