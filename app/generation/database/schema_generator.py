"""
Database Schema Generator - Creates SQL schemas from requirements
"""

from typing import Dict, List, Any
import json

class SchemaGenerator:
    """Generates database schemas from requirements"""
    
    def __init__(self):
        self.db_types = ["postgresql", "mysql", "sqlite"]
        
    async def generate_schema(self, requirements: Dict, db_type: str = "postgresql") -> Dict:
        """Generate complete database schema"""
        
        entities = await self._identify_entities(requirements)
        
        tables = []
        for entity in entities:
            table = await self._generate_table(entity, db_type)
            tables.append(table)
        
        relationships = await self._identify_relationships(entities, requirements)
        
        indexes = await self._generate_indexes(tables, requirements)
        
        return {
            "tables": tables,
            "relationships": relationships,
            "indexes": indexes,
            "sql": await self._generate_sql(tables, relationships, indexes, db_type)
        }
    
    async def _identify_entities(self, requirements: Dict) -> List[Dict]:
        """Extract entities from requirements"""
        entities = []
        
        # Extract from business requirements
        if "user" in str(requirements).lower():
            entities.append({
                "name": "users",
                "fields": [
                    {"name": "email", "type": "VARCHAR(255)", "unique": True, "required": True},
                    {"name": "password_hash", "type": "VARCHAR(255)", "required": True},
                    {"name": "full_name", "type": "VARCHAR(255)"},
                    {"name": "is_active", "type": "BOOLEAN", "default": True},
                    {"name": "role", "type": "VARCHAR(50)", "default": "user"}
                ]
            })
        
        # Add more entity detection logic based on requirements
        for entity_name in requirements.get("entities", []):
            entities.append(await self._create_entity_definition(entity_name, requirements))
        
        return entities
    
    async def _generate_table(self, entity: Dict, db_type: str) -> Dict:
        """Generate table definition from entity"""
        
        columns = [
            {"name": "id", "type": "SERIAL" if db_type == "postgresql" else "INT AUTO_INCREMENT", "primary_key": True}
        ]
        
        for field in entity.get("fields", []):
            columns.append(field)
        
        # Add audit fields
        columns.extend([
            {"name": "created_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"},
            {"name": "updated_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"}
        ])
        
        return {
            "name": entity["name"],
            "columns": columns
        }
    
    async def _identify_relationships(self, entities: List[Dict], requirements: Dict) -> List[Dict]:
        """Identify relationships between entities"""
        relationships = []
        
        # Detect common patterns
        for entity in entities:
            entity_name = entity["name"]
            
            # Look for foreign key references
            for other_entity in entities:
                if other_entity["name"] != entity_name:
                    # Check if entity references another
                    if f"{other_entity['name'][:-1]}_id" in str(entity.get("fields", [])):
                        relationships.append({
                            "type": "many_to_one",
                            "from": entity_name,
                            "to": other_entity["name"],
                            "foreign_key": f"{other_entity['name'][:-1]}_id"
                        })
        
        return relationships
    
    async def _generate_indexes(self, tables: List[Dict], requirements: Dict) -> List[Dict]:
        """Generate indexes for performance"""
        indexes = []
        
        for table in tables:
            # Index foreign keys
            for column in table["columns"]:
                if column["name"].endswith("_id") and column["name"] != "id":
                    indexes.append({
                        "name": f"idx_{table['name']}_{column['name']}",
                        "table": table["name"],
                        "columns": [column["name"]]
                    })
            
            # Index unique fields
            for column in table["columns"]:
                if column.get("unique"):
                    indexes.append({
                        "name": f"idx_{table['name']}_{column['name']}_unique",
                        "table": table["name"],
                        "columns": [column["name"]],
                        "unique": True
                    })
        
        return indexes
    
    async def _generate_sql(self, tables: List[Dict], relationships: List[Dict], indexes: List[Dict], db_type: str) -> str:
        """Generate SQL DDL statements"""
        sql_statements = []
        
        # Create tables
        for table in tables:
            sql = await self._generate_create_table_sql(table, db_type)
            sql_statements.append(sql)
        
        # Add foreign keys
        for rel in relationships:
            sql = await self._generate_foreign_key_sql(rel, db_type)
            sql_statements.append(sql)
        
        # Create indexes
        for index in indexes:
            sql = await self._generate_index_sql(index, db_type)
            sql_statements.append(sql)
        
        return "\n\n".join(sql_statements)
    
    async def _generate_create_table_sql(self, table: Dict, db_type: str) -> str:
        """Generate CREATE TABLE statement"""
        columns_sql = []
        
        for column in table["columns"]:
            col_sql = f"    {column['name']} {column['type']}"
            
            if column.get("primary_key"):
                col_sql += " PRIMARY KEY"
            if column.get("required"):
                col_sql += " NOT NULL"
            if column.get("unique"):
                col_sql += " UNIQUE"
            if "default" in column:
                default_val = column["default"]
                if isinstance(default_val, bool):
                    default_val = str(default_val).upper()
                elif isinstance(default_val, str) and default_val != "CURRENT_TIMESTAMP":
                    default_val = f"'{default_val}'"
                col_sql += f" DEFAULT {default_val}"
            
            columns_sql.append(col_sql)
        
        return f"""CREATE TABLE {table['name']} (
{','.join(columns_sql)}
);"""
    
    async def _generate_foreign_key_sql(self, relationship: Dict, db_type: str) -> str:
        """Generate foreign key constraint"""
        return f"""ALTER TABLE {relationship['from']} 
ADD CONSTRAINT fk_{relationship['from']}_{relationship['to']} 
FOREIGN KEY ({relationship['foreign_key']}) 
REFERENCES {relationship['to']}(id) 
ON DELETE CASCADE;"""
    
    async def _generate_index_sql(self, index: Dict, db_type: str) -> str:
        """Generate CREATE INDEX statement"""
        unique = "UNIQUE " if index.get("unique") else ""
        columns = ", ".join(index["columns"])
        
        return f"CREATE {unique}INDEX {index['name']} ON {index['table']} ({columns});"
    
    async def _create_entity_definition(self, entity_name: str, requirements: Dict) -> Dict:
        """Create entity definition from requirements"""
        
        # Common field patterns
        common_fields = {
            "product": [
                {"name": "name", "type": "VARCHAR(255)", "required": True},
                {"name": "description", "type": "TEXT"},
                {"name": "price", "type": "DECIMAL(10,2)", "required": True},
                {"name": "sku", "type": "VARCHAR(100)", "unique": True},
                {"name": "stock_quantity", "type": "INTEGER", "default": 0}
            ],
            "order": [
                {"name": "order_number", "type": "VARCHAR(50)", "unique": True, "required": True},
                {"name": "user_id", "type": "INTEGER", "required": True},
                {"name": "total_amount", "type": "DECIMAL(10,2)", "required": True},
                {"name": "status", "type": "VARCHAR(50)", "default": "pending"},
                {"name": "shipping_address", "type": "TEXT"}
            ],
            "category": [
                {"name": "name", "type": "VARCHAR(100)", "required": True, "unique": True},
                {"name": "description", "type": "TEXT"},
                {"name": "parent_category_id", "type": "INTEGER"},
                {"name": "is_active", "type": "BOOLEAN", "default": True}
            ]
        }
        
        # Use common fields if available, otherwise generate basic structure
        fields = common_fields.get(entity_name.lower(), [
            {"name": "name", "type": "VARCHAR(255)", "required": True},
            {"name": "description", "type": "TEXT"}
        ])
        
        return {
            "name": entity_name.lower() + "s" if not entity_name.endswith("s") else entity_name,
            "fields": fields
        }
    
    async def generate_migrations(self, schema: Dict) -> Dict[str, str]:
        """Generate migration files"""
        migrations = {}
        
        # Up migration
        migrations["001_initial_migration_up.sql"] = schema["sql"]
        
        # Down migration
        down_sql = []
        for table in reversed(schema["tables"]):
            down_sql.append(f"DROP TABLE IF EXISTS {table['name']} CASCADE;")
        
        migrations["001_initial_migration_down.sql"] = "\n".join(down_sql)
        
        return migrations
    
    async def generate_seed_data(self, schema: Dict) -> str:
        """Generate seed data for testing"""
        seed_statements = []
        
        for table in schema["tables"]:
            if table["name"] == "users":
                seed_statements.append("""
INSERT INTO users (email, password_hash, full_name, is_active, role) VALUES
('admin@example.com', '$2b$12$hash', 'Admin User', true, 'admin'),
('user@example.com', '$2b$12$hash', 'Test User', true, 'user');
""")
            elif table["name"] == "products":
                seed_statements.append("""
INSERT INTO products (name, description, price, sku, stock_quantity) VALUES
('Product 1', 'Description for product 1', 99.99, 'PROD001', 100),
('Product 2', 'Description for product 2', 149.99, 'PROD002', 50);
""")
        
        return "\n".join(seed_statements)