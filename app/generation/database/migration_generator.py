"""
Database Migration Generator for MIOSA Generation Engine

Generates Alembic migrations from schema changes and business requirements.
Supports complex migrations including data transformations and rollbacks.
"""

import textwrap
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class MigrationType(Enum):
    """Types of database migrations"""
    CREATE_TABLE = "create_table"
    DROP_TABLE = "drop_table"
    ADD_COLUMN = "add_column"
    DROP_COLUMN = "drop_column"
    MODIFY_COLUMN = "modify_column"
    ADD_INDEX = "add_index"
    DROP_INDEX = "drop_index"
    ADD_CONSTRAINT = "add_constraint"
    DROP_CONSTRAINT = "drop_constraint"
    CREATE_ENUM = "create_enum"
    MODIFY_ENUM = "modify_enum"
    DATA_MIGRATION = "data_migration"
    CUSTOM_SQL = "custom_sql"


@dataclass
class ColumnChange:
    """Represents a column change in migration"""
    name: str
    old_type: Optional[str] = None
    new_type: Optional[str] = None
    old_nullable: Optional[bool] = None
    new_nullable: Optional[bool] = None
    old_default: Optional[str] = None
    new_default: Optional[str] = None
    old_length: Optional[int] = None
    new_length: Optional[int] = None


@dataclass
class MigrationStep:
    """Single migration step"""
    type: MigrationType
    table_name: Optional[str] = None
    column_name: Optional[str] = None
    column_type: Optional[str] = None
    column_change: Optional[ColumnChange] = None
    index_name: Optional[str] = None
    constraint_name: Optional[str] = None
    sql: Optional[str] = None
    rollback_sql: Optional[str] = None
    description: Optional[str] = None
    data_transformation: Optional[str] = None


@dataclass
class Migration:
    """Complete migration specification"""
    name: str
    revision_id: str
    down_revision: Optional[str]
    steps: List[MigrationStep]
    description: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    branch_labels: Optional[str] = None


class MigrationGenerator:
    """
    Generates Alembic migrations for database schema changes.
    
    Features:
    - Automatic migration detection from schema differences
    - Safe column type changes with data preservation
    - Complex data migrations with rollback support
    - Index and constraint management
    - Enum type modifications
    - Multi-step migrations with dependencies
    - Production-safe migration patterns
    - Rollback strategy generation
    """
    
    def __init__(self, project_name: str = "MIOSA"):
        self.project_name = project_name
        self.migrations: List[Migration] = []
        
    def generate_revision_id(self, content: str) -> str:
        """Generate unique revision ID based on content"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"{timestamp}_{content_hash}"
    
    def create_initial_migration(
        self, 
        schema_sql: str,
        description: str = "Initial database schema"
    ) -> Migration:
        """Create initial migration from complete schema"""
        
        steps = [
            MigrationStep(
                type=MigrationType.CUSTOM_SQL,
                sql=schema_sql,
                rollback_sql="-- Manual rollback required for initial migration",
                description="Create initial database schema"
            )
        ]
        
        revision_id = self.generate_revision_id(schema_sql)
        
        migration = Migration(
            name="initial_schema",
            revision_id=revision_id,
            down_revision=None,
            steps=steps,
            description=description
        )
        
        return migration
    
    def create_add_table_migration(
        self,
        table_name: str,
        columns: List[Dict[str, Any]],
        indexes: List[Dict[str, Any]] = None,
        description: str = None
    ) -> Migration:
        """Create migration to add a new table"""
        
        steps = []
        
        # Create table step
        create_sql = self._generate_create_table_sql(table_name, columns)
        drop_sql = f"DROP TABLE IF EXISTS {table_name};"
        
        steps.append(
            MigrationStep(
                type=MigrationType.CREATE_TABLE,
                table_name=table_name,
                sql=create_sql,
                rollback_sql=drop_sql,
                description=f"Create {table_name} table"
            )
        )
        
        # Add indexes
        if indexes:
            for index in indexes:
                index_sql = self._generate_create_index_sql(index)
                drop_index_sql = f"DROP INDEX IF EXISTS {index['name']};"
                
                steps.append(
                    MigrationStep(
                        type=MigrationType.ADD_INDEX,
                        table_name=table_name,
                        index_name=index['name'],
                        sql=index_sql,
                        rollback_sql=drop_index_sql,
                        description=f"Create index {index['name']}"
                    )
                )
        
        revision_id = self.generate_revision_id(f"add_table_{table_name}")
        
        return Migration(
            name=f"add_{table_name}_table",
            revision_id=revision_id,
            down_revision=None,  # Set when adding to migration chain
            steps=steps,
            description=description or f"Add {table_name} table"
        )
    
    def create_add_column_migration(
        self,
        table_name: str,
        column_name: str,
        column_type: str,
        nullable: bool = True,
        default: Optional[str] = None,
        description: str = None
    ) -> Migration:
        """Create migration to add a column to existing table"""
        
        # Build column definition
        column_def = f"{column_name} {column_type}"
        if not nullable:
            column_def += " NOT NULL"
        if default:
            column_def += f" DEFAULT {default}"
        
        add_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_def};"
        drop_sql = f"ALTER TABLE {table_name} DROP COLUMN {column_name};"
        
        steps = [
            MigrationStep(
                type=MigrationType.ADD_COLUMN,
                table_name=table_name,
                column_name=column_name,
                column_type=column_type,
                sql=add_sql,
                rollback_sql=drop_sql,
                description=f"Add {column_name} column to {table_name}"
            )
        ]
        
        revision_id = self.generate_revision_id(f"add_column_{table_name}_{column_name}")
        
        return Migration(
            name=f"add_{column_name}_to_{table_name}",
            revision_id=revision_id,
            down_revision=None,
            steps=steps,
            description=description or f"Add {column_name} column to {table_name}"
        )
    
    def create_modify_column_migration(
        self,
        table_name: str,
        column_name: str,
        old_type: str,
        new_type: str,
        data_transformation: Optional[str] = None,
        description: str = None
    ) -> Migration:
        """Create migration to modify column type with data preservation"""
        
        steps = []
        
        # Step 1: Add temporary column with new type
        temp_column = f"{column_name}_temp"
        add_temp_sql = f"ALTER TABLE {table_name} ADD COLUMN {temp_column} {new_type};"
        
        steps.append(
            MigrationStep(
                type=MigrationType.ADD_COLUMN,
                table_name=table_name,
                column_name=temp_column,
                sql=add_temp_sql,
                description=f"Add temporary column {temp_column}"
            )
        )
        
        # Step 2: Migrate data to temporary column
        if data_transformation:
            update_sql = f"""
            UPDATE {table_name} 
            SET {temp_column} = {data_transformation}
            WHERE {column_name} IS NOT NULL;
            """
        else:
            update_sql = f"""
            UPDATE {table_name} 
            SET {temp_column} = {column_name}::{new_type}
            WHERE {column_name} IS NOT NULL;
            """
        
        steps.append(
            MigrationStep(
                type=MigrationType.DATA_MIGRATION,
                table_name=table_name,
                sql=update_sql,
                data_transformation=data_transformation,
                description=f"Migrate data from {column_name} to {temp_column}"
            )
        )
        
        # Step 3: Drop old column
        drop_old_sql = f"ALTER TABLE {table_name} DROP COLUMN {column_name};"
        
        steps.append(
            MigrationStep(
                type=MigrationType.DROP_COLUMN,
                table_name=table_name,
                column_name=column_name,
                sql=drop_old_sql,
                description=f"Drop old {column_name} column"
            )
        )
        
        # Step 4: Rename temporary column
        rename_sql = f"ALTER TABLE {table_name} RENAME COLUMN {temp_column} TO {column_name};"
        
        steps.append(
            MigrationStep(
                type=MigrationType.MODIFY_COLUMN,
                table_name=table_name,
                column_name=column_name,
                sql=rename_sql,
                description=f"Rename {temp_column} to {column_name}"
            )
        )
        
        revision_id = self.generate_revision_id(f"modify_{table_name}_{column_name}")
        
        return Migration(
            name=f"modify_{column_name}_in_{table_name}",
            revision_id=revision_id,
            down_revision=None,
            steps=steps,
            description=description or f"Change {column_name} type from {old_type} to {new_type}"
        )
    
    def create_enum_migration(
        self,
        enum_name: str,
        values: List[str],
        old_values: List[str] = None,
        description: str = None
    ) -> Migration:
        """Create migration for enum type creation or modification"""
        
        steps = []
        
        if old_values is None:
            # Create new enum
            values_str = "', '".join(values)
            create_sql = f"CREATE TYPE {enum_name} AS ENUM ('{values_str}');"
            drop_sql = f"DROP TYPE IF EXISTS {enum_name};"
            
            steps.append(
                MigrationStep(
                    type=MigrationType.CREATE_ENUM,
                    sql=create_sql,
                    rollback_sql=drop_sql,
                    description=f"Create {enum_name} enum type"
                )
            )
        else:
            # Modify existing enum
            new_values = set(values) - set(old_values)
            removed_values = set(old_values) - set(values)
            
            # Add new enum values
            for value in new_values:
                add_sql = f"ALTER TYPE {enum_name} ADD VALUE '{value}';"
                steps.append(
                    MigrationStep(
                        type=MigrationType.MODIFY_ENUM,
                        sql=add_sql,
                        description=f"Add '{value}' to {enum_name} enum"
                    )
                )
            
            # Note: PostgreSQL doesn't support removing enum values directly
            if removed_values:
                steps.append(
                    MigrationStep(
                        type=MigrationType.CUSTOM_SQL,
                        sql=f"-- WARNING: Cannot remove enum values: {', '.join(removed_values)}",
                        description=f"Note about removed values from {enum_name}"
                    )
                )
        
        revision_id = self.generate_revision_id(f"enum_{enum_name}")
        
        return Migration(
            name=f"modify_{enum_name}_enum",
            revision_id=revision_id,
            down_revision=None,
            steps=steps,
            description=description or f"Modify {enum_name} enum type"
        )
    
    def create_data_migration(
        self,
        name: str,
        forward_sql: str,
        backward_sql: str,
        description: str = None
    ) -> Migration:
        """Create a pure data migration"""
        
        steps = [
            MigrationStep(
                type=MigrationType.DATA_MIGRATION,
                sql=forward_sql,
                rollback_sql=backward_sql,
                description=description or f"Data migration: {name}"
            )
        ]
        
        revision_id = self.generate_revision_id(f"data_{name}")
        
        return Migration(
            name=f"data_migration_{name}",
            revision_id=revision_id,
            down_revision=None,
            steps=steps,
            description=description or f"Data migration: {name}"
        )
    
    def generate_alembic_migration_file(self, migration: Migration) -> str:
        """Generate complete Alembic migration file"""
        
        # Generate upgrade function
        upgrade_statements = []
        for step in migration.steps:
            if step.sql:
                if step.description:
                    upgrade_statements.append(f"    # {step.description}")
                upgrade_statements.append(f"    op.execute(\"\"\"{step.sql}\"\"\")")
        
        upgrade_body = "\n".join(upgrade_statements) if upgrade_statements else "    pass"
        
        # Generate downgrade function
        downgrade_statements = []
        for step in reversed(migration.steps):
            if step.rollback_sql:
                if step.description:
                    downgrade_statements.append(f"    # Rollback: {step.description}")
                downgrade_statements.append(f"    op.execute(\"\"\"{step.rollback_sql}\"\"\")")
        
        downgrade_body = "\n".join(downgrade_statements) if downgrade_statements else "    pass"
        
        # Generate file content
        return textwrap.dedent(f'''
        """
        {migration.description or migration.name}
        
        Revision ID: {migration.revision_id}
        Revises: {migration.down_revision or ""}
        Create Date: {datetime.now().isoformat()}
        """
        
        from alembic import op
        import sqlalchemy as sa
        from sqlalchemy.dialects import postgresql
        
        
        # Revision identifiers
        revision = "{migration.revision_id}"
        down_revision = {repr(migration.down_revision)}
        branch_labels = {repr(migration.branch_labels)}
        depends_on = {repr(migration.dependencies) if migration.dependencies else None}
        
        
        def upgrade() -> None:
            """Apply migration changes"""
        {upgrade_body}
        
        
        def downgrade() -> None:
            """Rollback migration changes"""
        {downgrade_body}
        ''').strip()
    
    def create_performance_migration(
        self,
        table_name: str,
        optimization_type: str = "indexing",
        description: str = None
    ) -> Migration:
        """Create migration focused on performance optimizations"""
        
        steps = []
        
        if optimization_type == "indexing":
            # Common performance indexes
            performance_indexes = [
                {
                    "name": f"idx_{table_name}_created_at_desc",
                    "sql": f"CREATE INDEX CONCURRENTLY idx_{table_name}_created_at_desc ON {table_name} (created_at DESC);",
                    "drop": f"DROP INDEX CONCURRENTLY IF EXISTS idx_{table_name}_created_at_desc;"
                },
                {
                    "name": f"idx_{table_name}_tenant_active",
                    "sql": f"CREATE INDEX CONCURRENTLY idx_{table_name}_tenant_active ON {table_name} (tenant_id) WHERE deleted_at IS NULL;",
                    "drop": f"DROP INDEX CONCURRENTLY IF EXISTS idx_{table_name}_tenant_active;"
                }
            ]
            
            for idx in performance_indexes:
                steps.append(
                    MigrationStep(
                        type=MigrationType.ADD_INDEX,
                        table_name=table_name,
                        index_name=idx["name"],
                        sql=idx["sql"],
                        rollback_sql=idx["drop"],
                        description=f"Add performance index {idx['name']}"
                    )
                )
        
        elif optimization_type == "partitioning":
            # Table partitioning
            partition_sql = f"""
            -- Convert {table_name} to partitioned table
            CREATE TABLE {table_name}_new (LIKE {table_name}) PARTITION BY RANGE (created_at);
            
            -- Create partitions for current and next month
            CREATE TABLE {table_name}_current PARTITION OF {table_name}_new
            FOR VALUES FROM (date_trunc('month', CURRENT_DATE)) TO (date_trunc('month', CURRENT_DATE) + interval '1 month');
            
            CREATE TABLE {table_name}_next PARTITION OF {table_name}_new
            FOR VALUES FROM (date_trunc('month', CURRENT_DATE) + interval '1 month') TO (date_trunc('month', CURRENT_DATE) + interval '2 months');
            
            -- Migrate data
            INSERT INTO {table_name}_new SELECT * FROM {table_name};
            
            -- Rename tables
            ALTER TABLE {table_name} RENAME TO {table_name}_old;
            ALTER TABLE {table_name}_new RENAME TO {table_name};
            """
            
            steps.append(
                MigrationStep(
                    type=MigrationType.CUSTOM_SQL,
                    table_name=table_name,
                    sql=partition_sql,
                    rollback_sql=f"-- Manual rollback required for partitioning",
                    description=f"Convert {table_name} to partitioned table"
                )
            )
        
        revision_id = self.generate_revision_id(f"performance_{table_name}")
        
        return Migration(
            name=f"performance_optimization_{table_name}",
            revision_id=revision_id,
            down_revision=None,
            steps=steps,
            description=description or f"Performance optimization for {table_name}"
        )
    
    def create_security_migration(
        self,
        description: str = "Enhance database security"
    ) -> Migration:
        """Create migration for security enhancements"""
        
        security_sql = textwrap.dedent('''
        -- Enable row level security on sensitive tables
        ALTER TABLE users ENABLE ROW LEVEL SECURITY;
        ALTER TABLE consultation_sessions ENABLE ROW LEVEL SECURITY;
        ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
        
        -- Create policies for multi-tenant isolation
        CREATE POLICY tenant_isolation_users ON users
            FOR ALL TO application_user
            USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
        
        CREATE POLICY tenant_isolation_sessions ON consultation_sessions
            FOR ALL TO application_user
            USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
        
        CREATE POLICY tenant_isolation_projects ON projects
            FOR ALL TO application_user
            USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
        
        -- Create application user role
        CREATE ROLE application_user;
        GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO application_user;
        GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO application_user;
        ''')
        
        rollback_sql = textwrap.dedent('''
        -- Disable row level security
        ALTER TABLE users DISABLE ROW LEVEL SECURITY;
        ALTER TABLE consultation_sessions DISABLE ROW LEVEL SECURITY;
        ALTER TABLE projects DISABLE ROW LEVEL SECURITY;
        
        -- Drop policies
        DROP POLICY IF EXISTS tenant_isolation_users ON users;
        DROP POLICY IF EXISTS tenant_isolation_sessions ON consultation_sessions;
        DROP POLICY IF EXISTS tenant_isolation_projects ON projects;
        
        -- Drop role
        DROP ROLE IF EXISTS application_user;
        ''')
        
        steps = [
            MigrationStep(
                type=MigrationType.CUSTOM_SQL,
                sql=security_sql,
                rollback_sql=rollback_sql,
                description="Implement row-level security and multi-tenant isolation"
            )
        ]
        
        revision_id = self.generate_revision_id("security_enhancements")
        
        return Migration(
            name="security_enhancements",
            revision_id=revision_id,
            down_revision=None,
            steps=steps,
            description=description
        )
    
    def _generate_create_table_sql(
        self, 
        table_name: str, 
        columns: List[Dict[str, Any]]
    ) -> str:
        """Generate CREATE TABLE SQL statement"""
        column_defs = []
        
        for col in columns:
            col_def = f"{col['name']} {col['type']}"
            
            if not col.get('nullable', True):
                col_def += " NOT NULL"
            if col.get('primary_key', False):
                col_def += " PRIMARY KEY"
            if col.get('unique', False):
                col_def += " UNIQUE"
            if 'default' in col:
                col_def += f" DEFAULT {col['default']}"
            if 'foreign_key' in col:
                col_def += f" REFERENCES {col['foreign_key']}"
            
            column_defs.append(col_def)
        
        return f"CREATE TABLE {table_name} (\n    " + ",\n    ".join(column_defs) + "\n);"
    
    def _generate_create_index_sql(self, index: Dict[str, Any]) -> str:
        """Generate CREATE INDEX SQL statement"""
        index_type = index.get('type', 'btree')
        unique = "UNIQUE " if index.get('unique', False) else ""
        concurrent = "CONCURRENTLY " if index.get('concurrent', True) else ""
        
        columns = ", ".join(index['columns'])
        
        sql = f"CREATE {unique}INDEX {concurrent}{index['name']} ON {index['table']}"
        
        if index_type != 'btree':
            sql += f" USING {index_type}"
        
        sql += f" ({columns})"
        
        if 'where' in index:
            sql += f" WHERE {index['where']}"
        
        return sql + ";"