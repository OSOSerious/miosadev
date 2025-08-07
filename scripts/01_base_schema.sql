-- PostgreSQL 15+ with TimescaleDB, pgvector, and all extensions
-- This is the PRODUCTION-READY schema with ALL components

- - Enable Required Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For fuzzy text search
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For composite indexes
CREATE EXTENSION IF NOT EXISTS "timescaledb"; -- For time-series data
CREATE EXTENSION IF NOT EXISTS "vector"; -- For AI embeddings
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements"; -- For query performance monitoring
CREATE EXTENSION IF NOT EXISTS "postgres_fdw"; -- For multi-tenant database connections
- - =====================================================
-- CORE USER & AUTHENTICATION (COMPLETE)
-- =====================================================
- - Users table with complete profile
CREATE TABLE users (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
email VARCHAR(255) UNIQUE NOT NULL,
email_verified BOOLEAN DEFAULT false,
password_hash VARCHAR(255) NOT NULL,

```
-- Profile Information
full_name VARCHAR(255),
display_name VARCHAR(100),
avatar_url TEXT,
phone_number VARCHAR(50),
phone_verified BOOLEAN DEFAULT false,

-- Business Context (Critical for consultation)
company_name VARCHAR(255),
company_size VARCHAR(50), -- 'solo', 'small', 'medium', 'enterprise'
industry VARCHAR(100),
industry_specific_details JSONB DEFAULT '{}', -- Store industry-specific info
role VARCHAR(100),
business_stage VARCHAR(50), -- 'idea', 'mvp', 'growth', 'scale', 'enterprise'
annual_revenue_range VARCHAR(50), -- '$0-10k', '$10k-100k', '$100k-1M', '$1M-10M', '$10M+'
team_size INTEGER,

-- Growth & Goals
primary_goal TEXT, -- What they want to achieve
growth_blockers JSONB DEFAULT '[]', -- Current challenges
timeline_urgency VARCHAR(50), -- 'immediate', 'short-term', 'medium-term', 'long-term'

-- Account Status
status VARCHAR(50) DEFAULT 'active',
onboarding_completed BOOLEAN DEFAULT false,
onboarding_stage VARCHAR(50) DEFAULT 'initial', -- Track where they are in onboarding

-- Voice Preferences
voice_enabled BOOLEAN DEFAULT true,
preferred_voice_model VARCHAR(50) DEFAULT 'whisper',
voice_language VARCHAR(10) DEFAULT 'en',

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),
updated_at TIMESTAMPTZ DEFAULT NOW(),
last_login_at TIMESTAMPTZ,
last_active_at TIMESTAMPTZ,
deleted_at TIMESTAMPTZ,

-- Metadata
metadata JSONB DEFAULT '{}',
referral_source VARCHAR(100),
utm_data JSONB DEFAULT '{}', -- Marketing attribution

CONSTRAINT chk_user_status CHECK (status IN ('active', 'inactive', 'suspended', 'deleted'))

```

);

- - =====================================================
-- CONSULTATION & ONBOARDING (COMPLETE)
-- =====================================================
- - Consultation sessions with complete flow tracking
CREATE TABLE consultation_sessions (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

```
-- Session State
phase VARCHAR(50) NOT NULL DEFAULT 'initial', -- 'initial', 'layer1', 'layer2', 'layer3', 'recommendation', 'building', 'completed'
sub_phase VARCHAR(50), -- For tracking micro-steps within phases
status VARCHAR(50) DEFAULT 'active',

-- Problem Discovery (Layer 1)
surface_problem TEXT, -- Initial problem statement
problem_type VARCHAR(100), -- 'support', 'sales', 'operations', 'growth', 'team', 'workflow', 'data'
problem_urgency VARCHAR(50), -- How urgent is this problem

-- Context Analysis (Layer 2)
current_process_description TEXT, -- How they currently handle it
process_steps JSONB DEFAULT '[]', -- Detailed workflow steps
people_involved INTEGER,
time_spent_daily DECIMAL(5,2), -- Hours per day
tools_currently_used JSONB DEFAULT '[]', -- Current tech stack
pain_points JSONB DEFAULT '[]', -- Specific friction points

-- Business Impact (Layer 3)
business_impact VARCHAR(50), -- 'low', 'medium', 'high', 'critical'
financial_impact JSONB DEFAULT '{}', -- Cost analysis
growth_impact TEXT, -- How it affects growth
team_impact TEXT, -- How it affects the team
customer_impact TEXT, -- How it affects customers

-- Scale & Growth Context
current_volume JSONB DEFAULT '{}', -- Current transaction/ticket/process volume
expected_growth_rate DECIMAL(5,2), -- Expected % growth
scaling_challenges JSONB DEFAULT '[]',
competitive_pressure TEXT,

-- Industry Context
industry_specific_needs JSONB DEFAULT '{}',
compliance_requirements JSONB DEFAULT '[]',
industry_benchmarks JSONB DEFAULT '{}',

-- Solution Design
recommended_solution_type VARCHAR(100),
solution_architecture JSONB DEFAULT '{}',
key_features JSONB DEFAULT '[]',
integrations_needed JSONB DEFAULT '[]',

-- Build Context (What happens during generation)
build_started_at TIMESTAMPTZ,
build_context JSONB DEFAULT '{}', -- Additional context gathered during build
build_iterations INTEGER DEFAULT 0,

-- Engagement Tracking
total_messages INTEGER DEFAULT 0,
voice_messages INTEGER DEFAULT 0,
avg_response_time_seconds INTEGER,
engagement_score DECIMAL(3,2), -- 0-1 score

-- Timestamps
started_at TIMESTAMPTZ DEFAULT NOW(),
recommendation_presented_at TIMESTAMPTZ,
build_initiated_at TIMESTAMPTZ,
completed_at TIMESTAMPTZ,
last_interaction_at TIMESTAMPTZ DEFAULT NOW(),

INDEX idx_consultation_user_id (user_id),
INDEX idx_consultation_phase (phase),
INDEX idx_consultation_status (status)

```

);

- - Detailed consultation messages with AI analysis
CREATE TABLE consultation_messages (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
session_id UUID NOT NULL REFERENCES consultation_sessions(id) ON DELETE CASCADE,

```
-- Message Details
role VARCHAR(20) NOT NULL, -- 'user', 'miosa'
content TEXT NOT NULL,
voice_transcript TEXT, -- If voice was used
voice_audio_url TEXT, -- Stored voice recording

-- Message Context
phase VARCHAR(50) NOT NULL,
sub_phase VARCHAR(50),
message_purpose VARCHAR(100), -- 'greeting', 'question', 'clarification', 'recommendation', 'confirmation'

-- AI Analysis
intent_analysis JSONB DEFAULT '{}',
emotional_state JSONB DEFAULT '{}', -- Detect stress, excitement, confusion, etc.
urgency_detected BOOLEAN DEFAULT false,
confidence_level DECIMAL(3,2),

-- Information Extraction
extracted_entities JSONB DEFAULT '{}', -- Company names, tools, numbers, etc.
extracted_requirements JSONB DEFAULT '[]',
extracted_constraints JSONB DEFAULT '[]',

-- Response Quality
response_helpful BOOLEAN, -- User feedback
response_rating INTEGER CHECK (response_rating >= 1 AND response_rating <= 5),

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),

INDEX idx_consultation_msg_session (session_id),
INDEX idx_consultation_msg_created (created_at)

```

);

- - Consultation insights (what AI learns from each session)
CREATE TABLE consultation_insights (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
session_id UUID NOT NULL REFERENCES consultation_sessions(id) ON DELETE CASCADE,
user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

```
-- Insight Type
insight_type VARCHAR(100) NOT NULL, -- 'pattern', 'preference', 'need', 'constraint'
insight_category VARCHAR(100),

-- Insight Content
insight TEXT NOT NULL,
confidence_score DECIMAL(3,2),

-- Application
applied_to_recommendation BOOLEAN DEFAULT false,
applied_to_build BOOLEAN DEFAULT false,

-- Timestamps
discovered_at TIMESTAMPTZ DEFAULT NOW(),

INDEX idx_consultation_insights_session (session_id),
INDEX idx_consultation_insights_user (user_id)

```

);

- - =====================================================
-- CONVERSATION MEMORY & CONTEXT (COMPLETE)
-- =====================================================
- - Long-term conversation memory
CREATE TABLE conversation_memory (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

```
-- Memory Classification
memory_type VARCHAR(50) NOT NULL, -- 'fact', 'preference', 'context', 'relationship', 'goal', 'constraint'
memory_category VARCHAR(100), -- 'business', 'technical', 'personal', 'team', 'product'

-- Memory Content
memory_key VARCHAR(255) NOT NULL, -- Searchable key
content TEXT NOT NULL,
structured_data JSONB DEFAULT '{}', -- Structured version of the memory

-- Source & Confidence
source_type VARCHAR(50), -- 'explicit_statement', 'inferred', 'observed_behavior'
source_message_id UUID REFERENCES messages(id),
confidence_score DECIMAL(3,2) DEFAULT 0.8,
verification_status VARCHAR(50) DEFAULT 'unverified', -- 'unverified', 'user_confirmed', 'behavior_confirmed'

-- Importance & Usage
importance_score DECIMAL(3,2) DEFAULT 0.5,
relevance_decay_rate DECIMAL(4,3) DEFAULT 0.001, -- How fast it becomes less relevant
access_count INTEGER DEFAULT 0,
last_accessed_at TIMESTAMPTZ,

-- Relationships
related_memories UUID[] DEFAULT '{}',
related_project_id UUID REFERENCES projects(id),
related_entities JSONB DEFAULT '[]', -- People, companies, tools mentioned

-- Embeddings for semantic search
embedding vector(1536),
embedding_model VARCHAR(50),

-- Lifecycle
valid_from TIMESTAMPTZ DEFAULT NOW(),
valid_until TIMESTAMPTZ, -- Some memories expire
superseded_by UUID REFERENCES conversation_memory(id), -- When updated

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),
updated_at TIMESTAMPTZ DEFAULT NOW(),

UNIQUE(user_id, memory_key),
INDEX idx_conv_memory_user_type (user_id, memory_type),
INDEX idx_conv_memory_importance (importance_score DESC),
INDEX idx_conv_memory_category (memory_category),
INDEX idx_conv_memory_embedding ON conversation_memory USING ivfflat (embedding vector_cosine_ops)
  
```

);

- - Memory relationships and context web
CREATE TABLE memory_relationships (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
memory_id_1 UUID NOT NULL REFERENCES conversation_memory(id) ON DELETE CASCADE,
memory_id_2 UUID NOT NULL REFERENCES conversation_memory(id) ON DELETE CASCADE,

```
-- Relationship Details
relationship_type VARCHAR(50) NOT NULL, -- 'contradicts', 'supports', 'updates', 'related_to'
relationship_strength DECIMAL(3,2) DEFAULT 0.5,

-- Metadata
discovered_at TIMESTAMPTZ DEFAULT NOW(),
discovered_by VARCHAR(50), -- Which agent/process found this

UNIQUE(memory_id_1, memory_id_2, relationship_type)

```

);

- - =====================================================
-- PROJECTS & APPLICATIONS (COMPLETE)
-- =====================================================
- - Projects with full lifecycle tracking
CREATE TABLE projects (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
consultation_session_id UUID REFERENCES consultation_sessions(id),

```
-- Project Details
name VARCHAR(255) NOT NULL,
slug VARCHAR(255) NOT NULL,
description TEXT,
type VARCHAR(50) NOT NULL, -- 'web-app', 'mobile-app', 'api', 'workflow', 'automation', 'dashboard'
category VARCHAR(100), -- 'crm', 'ecommerce', 'saas', 'internal-tool', etc.

-- Status & Lifecycle
status VARCHAR(50) DEFAULT 'initializing',
stage VARCHAR(50) DEFAULT 'development', -- 'development', 'staging', 'production'
visibility VARCHAR(20) DEFAULT 'private',

-- Technical Configuration
technology_stack JSONB DEFAULT '{}',
framework VARCHAR(50), -- 'react', 'vue', 'svelte', etc.
database_type VARCHAR(50), -- 'postgresql', 'mongodb', etc.

-- Features & Capabilities
features JSONB DEFAULT '[]',
integrations JSONB DEFAULT '[]',
api_endpoints JSONB DEFAULT '[]',

-- Build Information
initial_prompt TEXT, -- What user asked for
build_instructions JSONB DEFAULT '{}', -- Detailed build specs
build_iterations INTEGER DEFAULT 0,
last_build_error TEXT,

-- Deployment Information
deployment_url TEXT,
staging_url TEXT,
custom_domain TEXT,
ssl_enabled BOOLEAN DEFAULT true,

-- Analytics & Usage
total_users INTEGER DEFAULT 0,
active_users_30d INTEGER DEFAULT 0,
api_calls_30d INTEGER DEFAULT 0,
storage_used_mb DECIMAL(12,2) DEFAULT 0,

-- Business Context
business_value_estimate DECIMAL(12,2),
time_saved_hours_monthly DECIMAL(8,2),

-- Daytona Workspace
daytona_workspace_id VARCHAR(255),
workspace_status VARCHAR(50),

-- Repository
repository_url TEXT,
repository_type VARCHAR(20) DEFAULT 'git',
default_branch VARCHAR(50) DEFAULT 'main',

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),
updated_at TIMESTAMPTZ DEFAULT NOW(),
first_deployed_at TIMESTAMPTZ,
last_deployed_at TIMESTAMPTZ,
archived_at TIMESTAMPTZ,

UNIQUE(user_id, slug),
INDEX idx_projects_user_id (user_id),
INDEX idx_projects_status (status),
INDEX idx_projects_type (type)

```

);

- - Project build history
CREATE TABLE project_builds (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

```
-- Build Details
build_number INTEGER NOT NULL,
trigger_type VARCHAR(50), -- 'user_request', 'auto_improvement', 'bug_fix', 'feature_add'
trigger_message TEXT,

-- Build Process
status VARCHAR(50) DEFAULT 'queued', -- 'queued', 'building', 'testing', 'deploying', 'completed', 'failed'
started_at TIMESTAMPTZ,
completed_at TIMESTAMPTZ,
duration_seconds INTEGER,

-- Changes Made
changes_description TEXT,
files_modified JSONB DEFAULT '[]',
features_added JSONB DEFAULT '[]',
bugs_fixed JSONB DEFAULT '[]',

-- Quality Metrics
test_results JSONB DEFAULT '{}',
code_quality_score DECIMAL(3,2),
performance_score DECIMAL(3,2),
security_score DECIMAL(3,2),

-- Deployment
deployed BOOLEAN DEFAULT false,
deployment_url TEXT,
rollback_build_id UUID REFERENCES project_builds(id),

-- Logs
build_logs TEXT,
error_logs TEXT,

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),

INDEX idx_builds_project_id (project_id),
INDEX idx_builds_status (status),
INDEX idx_builds_created (created_at DESC)

```

);

- - =====================================================
-- MULTI-AGENT SYSTEM (COMPLETE)
-- =====================================================
- - Agent definitions with capabilities
CREATE TABLE agents (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
agent_type VARCHAR(50) UNIQUE NOT NULL,

```
-- Agent Details
name VARCHAR(100) NOT NULL,
description TEXT,
version VARCHAR(20) DEFAULT '1.0.0',

-- Capabilities
capabilities JSONB NOT NULL DEFAULT '[]',
supported_tasks JSONB DEFAULT '[]',
max_concurrent_tasks INTEGER DEFAULT 5,

-- Configuration
configuration JSONB DEFAULT '{}',
model_preferences JSONB DEFAULT '{}', -- Which AI models to use

-- Performance
avg_execution_time_ms INTEGER,
success_rate DECIMAL(5,2),
total_executions BIGINT DEFAULT 0,

-- Status
is_active BOOLEAN DEFAULT true,
health_status VARCHAR(50) DEFAULT 'healthy',
last_health_check TIMESTAMPTZ,

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),
updated_at TIMESTAMPTZ DEFAULT NOW()

```

);

- - Agent task executions with full context
CREATE TABLE agent_executions (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
agent_id UUID NOT NULL REFERENCES agents(id),
user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
project_id UUID REFERENCES projects(id) ON DELETE CASCADE,

```
-- Task Details
task_type VARCHAR(100) NOT NULL,
task_description TEXT,
task_parameters JSONB DEFAULT '{}',
priority VARCHAR(20) DEFAULT 'normal',

-- Execution Context
triggered_by VARCHAR(50), -- 'user', 'system', 'schedule', 'event'
parent_execution_id UUID REFERENCES agent_executions(id),
conversation_context JSONB DEFAULT '{}',
memory_context UUID[] DEFAULT '{}', -- Related memories used

-- Execution State
status VARCHAR(50) DEFAULT 'pending',
progress INTEGER DEFAULT 0,
checkpoint_data JSONB DEFAULT '{}', -- For resuming

-- Results
result JSONB DEFAULT '{}',
output_artifacts JSONB DEFAULT '[]', -- Files, images, etc. created
side_effects JSONB DEFAULT '[]', -- Other changes made

-- Performance
execution_time_ms INTEGER,
tokens_used INTEGER,
api_calls_made INTEGER,
cost_estimate DECIMAL(10,4),

-- Error Handling
error_count INTEGER DEFAULT 0,
last_error TEXT,
retry_count INTEGER DEFAULT 0,
max_retries INTEGER DEFAULT 3,

-- Dependencies
depends_on UUID[] DEFAULT '{}',
blocks UUID[] DEFAULT '{}',

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),
scheduled_for TIMESTAMPTZ,
started_at TIMESTAMPTZ,
completed_at TIMESTAMPTZ,

INDEX idx_executions_agent_id (agent_id),
INDEX idx_executions_user_id (user_id),
INDEX idx_executions_status (status),
INDEX idx_executions_scheduled (scheduled_for)

```

);

- - Create hypertable for agent executions
SELECT create_hypertable('agent_executions', 'created_at');
- - Agent communication log
CREATE TABLE agent_communications (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
from_agent_id UUID NOT NULL REFERENCES agents(id),
to_agent_id UUID NOT NULL REFERENCES agents(id),
execution_id UUID REFERENCES agent_executions(id),

```
-- Message Details
message_type VARCHAR(50) NOT NULL, -- 'request', 'response', 'notification'
content JSONB NOT NULL,

-- Timing
sent_at TIMESTAMPTZ DEFAULT NOW(),
received_at TIMESTAMPTZ,
processed_at TIMESTAMPTZ,

INDEX idx_agent_comm_from (from_agent_id),
INDEX idx_agent_comm_to (to_agent_id),
INDEX idx_agent_comm_execution (execution_id)

```

);

- - ==============================================0
- =======
-- AI RECOMMENDATIONS & DECISIONS (COMPLETE)
-- =====================================================
- - AI recommendations with full tracking
CREATE TABLE ai_recommendations (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
project_id UUID REFERENCES projects(id),
session_id UUID REFERENCES consultation_sessions(id),

```
-- Recommendation Details
recommendation_type VARCHAR(100) NOT NULL,
category VARCHAR(100),
title VARCHAR(255) NOT NULL,
description TEXT NOT NULL,

-- Context
triggered_by VARCHAR(50), -- 'consultation', 'usage_pattern', 'performance_issue', 'growth_opportunity'
context_data JSONB DEFAULT '{}',

-- Solution Architecture
solution_type VARCHAR(100),
solution_components JSONB DEFAULT '[]',
implementation_steps JSONB DEFAULT '[]',
required_resources JSONB DEFAULT '{}',

-- Impact Analysis
business_impact JSONB DEFAULT '{}',
estimated_value DECIMAL(12,2),
time_to_implement VARCHAR(50),
complexity_score DECIMAL(3,2),

-- AI Reasoning
confidence_score DECIMAL(3,2) NOT NULL,
reasoning TEXT,
supporting_data JSONB DEFAULT '{}',
alternative_options JSONB DEFAULT '[]',

-- User Interaction
presented_at TIMESTAMPTZ,
presentation_method VARCHAR(50), -- 'chat', 'dashboard', 'email', 'notification'
user_response VARCHAR(50), -- 'accepted', 'rejected', 'modified', 'deferred', 'ignored'
user_feedback TEXT,
response_reasoning TEXT,

-- Implementation Tracking
implementation_status VARCHAR(50) DEFAULT 'pending',
implementation_started_at TIMESTAMPTZ,
implementation_completed_at TIMESTAMPTZ,
actual_impact JSONB DEFAULT '{}',

-- Learning
outcome_rating INTEGER CHECK (outcome_rating >= 1 AND outcome_rating <= 5),
lessons_learned TEXT,

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),
expires_at TIMESTAMPTZ, -- Some recommendations become irrelevant

INDEX idx_recommendations_user_id (user_id),
INDEX idx_recommendations_type (recommendation_type),
INDEX idx_recommendations_status (implementation_status),
INDEX idx_recommendations_confidence (confidence_score DESC)

```

);

- - =====================================================
-- BUILT-IN DATABASES (COMPLETE MULTI-TENANT)
-- =====================================================
- - User database schemas with full isolation
CREATE TABLE user_database_schemas (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
project_id UUID REFERENCES projects(id) ON DELETE CASCADE,

```
-- Schema Details
schema_name VARCHAR(255) NOT NULL UNIQUE,
display_name VARCHAR(255),
database_type VARCHAR(100) NOT NULL,
template_used VARCHAR(100),

-- Database Configuration
connection_config JSONB DEFAULT '{}', -- Encrypted connection details
isolation_level VARCHAR(50) DEFAULT 'strict', -- 'strict', 'shared', 'custom'

-- Structure
tables_count INTEGER DEFAULT 0,
views_count INTEGER DEFAULT 0,
indexes_count INTEGER DEFAULT 0,

-- Data Statistics
total_records BIGINT DEFAULT 0,
storage_used_mb DECIMAL(12,2) DEFAULT 0,
last_vacuum_at TIMESTAMPTZ,

-- Features
features_enabled JSONB DEFAULT '{"analytics": true, "export": true, "api": true, "backup": true}',

-- API Access
api_key_hash VARCHAR(255),
api_endpoints JSONB DEFAULT '{}',
api_rate_limits JSONB DEFAULT '{}',

-- Status
status VARCHAR(50) DEFAULT 'active',
health_status VARCHAR(50) DEFAULT 'healthy',
last_health_check TIMESTAMPTZ,

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),
last_accessed_at TIMESTAMPTZ,
last_modified_at TIMESTAMPTZ,

INDEX idx_user_schemas_user_id (user_id),
INDEX idx_user_schemas_project_id (project_id),
INDEX idx_user_schemas_status (status)

```

);

- - User database tables with detailed structure
CREATE TABLE user_database_tables (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
schema_id UUID NOT NULL REFERENCES user_database_schemas(id) ON DELETE CASCADE,

```
-- Table Details
table_name VARCHAR(255) NOT NULL,
display_name VARCHAR(255),
description TEXT,
table_type VARCHAR(50) DEFAULT 'standard', -- 'standard', 'view', 'materialized_view'

-- Structure
columns JSONB NOT NULL DEFAULT '[]', -- Full column definitions
primary_key JSONB DEFAULT '{}',
foreign_keys JSONB DEFAULT '[]',
indexes JSONB DEFAULT '[]',
constraints JSONB DEFAULT '[]',
triggers JSONB DEFAULT '[]',

-- Data Info
record_count BIGINT DEFAULT 0,
size_bytes BIGINT DEFAULT 0,
avg_row_size_bytes INTEGER,

-- Performance
read_count BIGINT DEFAULT 0,
write_count BIGINT DEFAULT 0,
last_analyzed_at TIMESTAMPTZ,

-- AI Features
ai_insights_enabled BOOLEAN DEFAULT true,
embedding_column VARCHAR(255), -- For vector search

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),
updated_at TIMESTAMPTZ DEFAULT NOW(),
last_data_modified_at TIMESTAMPTZ,

UNIQUE(schema_id, table_name),
INDEX idx_user_tables_schema_id (schema_id)

```

);

- - User database access logs
CREATE TABLE user_database_access_logs (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
schema_id UUID NOT NULL REFERENCES user_database_schemas(id) ON DELETE CASCADE,
user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

```
-- Access Details
access_type VARCHAR(50) NOT NULL, -- 'query', 'insert', 'update', 'delete', 'schema_change'
table_name VARCHAR(255),

-- Query Info
query_hash VARCHAR(64), -- For identifying repeated queries
query_text TEXT, -- Sanitized query

-- Performance
execution_time_ms INTEGER,
rows_affected INTEGER,

-- Context
access_method VARCHAR(50), -- 'app', 'api', 'export', 'admin'
ip_address INET,
user_agent TEXT,

-- Timestamp
accessed_at TIMESTAMPTZ DEFAULT NOW(),

INDEX idx_db_access_schema (schema_id),
INDEX idx_db_access_user (user_id),
INDEX idx_db_access_time (accessed_at DESC)

```

);

- - Create hypertable for access logs
SELECT create_hypertable('user_database_access_logs', 'accessed_at');
- - =====================================================
-- BUSINESS INTELLIGENCE & INSIGHTS (COMPLETE)
-- =====================================================
- - Business insights with actionable intelligence
CREATE TABLE business_insights (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
project_id UUID REFERENCES projects(id),
schema_id UUID REFERENCES user_database_schemas(id),

```
-- Insight Classification
insight_type VARCHAR(100) NOT NULL,
category VARCHAR(100) NOT NULL,
subcategory VARCHAR(100),

-- Insight Content
title VARCHAR(255) NOT NULL,
summary TEXT NOT NULL,
detailed_analysis TEXT,

-- Data Sources
data_sources JSONB DEFAULT '[]',
queries_used JSONB DEFAULT '[]',
time_period_analyzed JSONB DEFAULT '{}',

-- Findings
key_metrics JSONB DEFAULT '{}',
trends_identified JSONB DEFAULT '[]',
anomalies_detected JSONB DEFAULT '[]',
correlations_found JSONB DEFAULT '[]',

-- Visualizations
charts JSONB DEFAULT '[]', -- Chart configs for rendering

-- Business Impact
impact_level VARCHAR(50), -- 'low', 'medium', 'high', 'critical'
urgency_level VARCHAR(50), -- 'low', 'medium', 'high', 'urgent'
potential_value DECIMAL(12,2),
risk_if_ignored DECIMAL(12,2),

-- Recommendations
recommended_actions JSONB DEFAULT '[]',
implementation_guide TEXT,
estimated_effort VARCHAR(50),

-- Competitive Context
competitive_advantage TEXT,
market_comparison JSONB DEFAULT '{}',

-- AI Confidence
confidence_score DECIMAL(3,2),
evidence_strength VARCHAR(50),

-- User Engagement
viewed BOOLEAN DEFAULT false,
viewed_at TIMESTAMPTZ,
view_duration_seconds INTEGER,
shared_with JSONB DEFAULT '[]',

-- User Response
user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
user_feedback TEXT,
action_taken VARCHAR(100),
action_taken_at TIMESTAMPTZ,

-- Results Tracking
expected_outcome JSONB DEFAULT '{}',
actual_outcome JSONB DEFAULT '{}',
outcome_measured_at TIMESTAMPTZ,

-- Lifecycle
generated_at TIMESTAMPTZ DEFAULT NOW(),
valid_until TIMESTAMPTZ,
superseded_by UUID REFERENCES business_insights(id),

INDEX idx_insights_user_id (user_id),
INDEX idx_insights_type (insight_type),
INDEX idx_insights_impact (impact_level),
INDEX idx_insights_generated (generated_at DESC),
INDEX idx_insights_value (potential_value DESC)

```

);

- - Create hypertable for insights
SELECT create_hypertable('business_insights', 'generated_at');
- - Predictive analytics with model tracking
CREATE TABLE predictive_analytics (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
project_id UUID REFERENCES projects(id),
schema_id UUID REFERENCES user_database_schemas(id),

```
-- Prediction Details
prediction_type VARCHAR(100) NOT NULL,
target_variable VARCHAR(255) NOT NULL,
prediction_horizon VARCHAR(50), -- 'next_day', 'next_week', 'next_month', 'next_quarter'

-- Time Frame
prediction_start_date DATE NOT NULL,
prediction_end_date DATE NOT NULL,
granularity VARCHAR(20),

-- Model Information
model_id VARCHAR(100),
model_type VARCHAR(100),
model_version VARCHAR(50),
model_config JSONB DEFAULT '{}',

-- Training Data
training_period_start DATE,
training_period_end DATE,
training_rows INTEGER,
features_used JSONB DEFAULT '[]',
feature_importance JSONB DEFAULT '{}',

-- Predictions
predictions JSONB NOT NULL, -- Time series predictions
confidence_intervals JSONB DEFAULT '{}',
prediction_metadata JSONB DEFAULT '{}',

-- Model Performance
accuracy_metrics JSONB DEFAULT '{}',
validation_results JSONB DEFAULT '{}',
backtesting_results JSONB DEFAULT '{}',

-- Business Context
business_assumptions JSONB DEFAULT '[]',
external_factors JSONB DEFAULT '[]',
scenario_analysis JSONB DEFAULT '{}',

-- Recommendations
recommended_actions JSONB DEFAULT '[]',
risk_factors JSONB DEFAULT '[]',
opportunity_windows JSONB DEFAULT '[]',

-- Tracking
actual_values JSONB DEFAULT '{}', -- Track actuals vs predictions
accuracy_score DECIMAL(3,2),

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),
model_trained_at TIMESTAMPTZ,
last_updated_at TIMESTAMPTZ,

INDEX idx_predictions_user_id (user_id),
INDEX idx_predictions_type (prediction_type),
INDEX idx_predictions_date_range (prediction_start_date, prediction_end_date)

```

);

- - =====================================================
-- INTEGRATION INTELLIGENCE (COMPLETE)
-- =====================================================
- - Enhanced integrations with deep intelligence
CREATE TABLE integrations (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
project_id UUID REFERENCES projects(id),

```
-- Integration Details
provider VARCHAR(100) NOT NULL,
provider_category VARCHAR(50), -- 'crm', 'email', 'payment', 'analytics', etc.
name VARCHAR(255) NOT NULL,
description TEXT,

-- Authentication
auth_type VARCHAR(50),
credentials JSONB DEFAULT '{}', -- Encrypted
refresh_token_encrypted TEXT,
expires_at TIMESTAMPTZ,

-- Configuration
configuration JSONB DEFAULT '{}',
sync_config JSONB DEFAULT '{}',
field_mappings JSONB DEFAULT '{}',

-- Webhooks
webhook_url TEXT,
webhook_secret_hash VARCHAR(255),
webhook_events JSONB DEFAULT '[]',

-- Data Sync
sync_enabled BOOLEAN DEFAULT true,
sync_frequency VARCHAR(50) DEFAULT 'real-time', -- 'real-time', 'hourly', 'daily'
last_sync_at TIMESTAMPTZ,
next_sync_at TIMESTAMPTZ,

-- Performance
total_syncs INTEGER DEFAULT 0,
failed_syncs INTEGER DEFAULT 0,
avg_sync_duration_seconds INTEGER,

-- Data Statistics
records_synced BIGINT DEFAULT 0,
data_volume_mb DECIMAL(12,2) DEFAULT 0,

-- Status
status VARCHAR(50) DEFAULT 'active',
health_status VARCHAR(50) DEFAULT 'healthy',
last_error TEXT,
error_count INTEGER DEFAULT 0,

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),
updated_at TIMESTAMPTZ DEFAULT NOW(),
last_health_check TIMESTAMPTZ,

INDEX idx_integrations_user_id (user_id),
INDEX idx_integrations_provider (provider),
INDEX idx_integrations_status (status)

```

);

- - Email intelligence with deep analysis
CREATE TABLE email_intelligence (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
integration_id UUID REFERENCES integrations(id),
schema_id UUID REFERENCES user_database_schemas(id),

```
-- Email Identification
email_id VARCHAR(255) UNIQUE NOT NULL,
thread_id VARCHAR(255),
in_reply_to VARCHAR(255),

-- Basic Info
subject VARCHAR(500),
sender_email VARCHAR(255),
sender_name VARCHAR(255),
recipient_emails TEXT[],
cc_emails TEXT[],

-- Content
body_text TEXT,
body_html TEXT,
attachments JSONB DEFAULT '[]',

-- AI Analysis
summary TEXT,
sentiment_score DECIMAL(3,2),
sentiment_explanation TEXT,
emotion_detected VARCHAR(50), -- 'neutral', 'happy', 'frustrated', 'urgent'

-- Intent Analysis
primary_intent VARCHAR(100),
secondary_intents JSONB DEFAULT '[]',
action_required BOOLEAN DEFAULT false,
urgency_level VARCHAR(20),

-- Business Signals
deal_stage_indicators JSONB DEFAULT '[]',
buying_signals_strength DECIMAL(3,2),
churn_risk_indicators JSONB DEFAULT '[]',
satisfaction_indicators JSONB DEFAULT '[]',

-- Extracted Information
mentioned_products JSONB DEFAULT '[]',
mentioned_competitors JSONB DEFAULT '[]',
price_mentions JSONB DEFAULT '[]',
timeline_mentions JSONB DEFAULT '[]',

-- Action Items
extracted_tasks JSONB DEFAULT '[]',
extracted_questions JSONB DEFAULT '[]',
commitments_made JSONB DEFAULT '[]',

-- Response Intelligence
response_required BOOLEAN DEFAULT false,
suggested_response_time INTERVAL,
response_talking_points JSONB DEFAULT '[]',
response_tone_recommendation VARCHAR(50),

-- Engagement Tracking
sent_at TIMESTAMPTZ,
received_at TIMESTAMPTZ,
opened_at TIMESTAMPTZ,
clicked_at TIMESTAMPTZ,
replied_at TIMESTAMPTZ,

-- Relationship Context
relationship_strength DECIMAL(3,2),
communication_frequency VARCHAR(50),

-- Timestamps
analyzed_at TIMESTAMPTZ,
created_at TIMESTAMPTZ DEFAULT NOW(),

INDEX idx_email_intel_user_id (user_id),
INDEX idx_email_intel_thread (thread_id),
INDEX idx_email_intel_sender (sender_email),
INDEX idx_email_intel_sentiment (sentiment_score),
INDEX idx_email_intel_urgency (urgency_level),
INDEX idx_email_intel_received (received_at DESC)

```

);

- - Meeting intelligence with comprehensive analysis
CREATE TABLE meeting_intelligence (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
integration_id UUID REFERENCES integrations(id),
schema_id UUID REFERENCES user_database_schemas(id),
project_id UUID REFERENCES projects(id),

```
-- Meeting Identification
meeting_id VARCHAR(255) UNIQUE NOT NULL,
calendar_event_id VARCHAR(255),

-- Basic Info
title VARCHAR(500),
meeting_type VARCHAR(100),
meeting_purpose JSONB DEFAULT '{}',

-- Time Details
scheduled_start TIMESTAMPTZ,
scheduled_end TIMESTAMPTZ,
actual_start TIMESTAMPTZ,
actual_end TIMESTAMPTZ,
duration_minutes INTEGER,

-- Participants
organizer_email VARCHAR(255),
participants JSONB DEFAULT '[]',
attendance_data JSONB DEFAULT '{}',
no_shows JSONB DEFAULT '[]',

-- Recording & Transcript
recording_url TEXT,
recording_duration_seconds INTEGER,
transcript_url TEXT,
transcript_text TEXT,
transcript_confidence DECIMAL(3,2),

-- AI Analysis - Summary
executive_summary TEXT,
detailed_summary TEXT,

-- AI Analysis - Content
agenda_items_discussed JSONB DEFAULT '[]',
key_topics JSONB DEFAULT '[]',
off_topic_percentage DECIMAL(3,2),

-- AI Analysis - Participants
speaker_stats JSONB DEFAULT '{}', -- Talk time, interruptions, etc.
engagement_scores JSONB DEFAULT '{}',
sentiment_by_participant JSONB DEFAULT '{}',

-- AI Analysis - Dynamics
overall_sentiment DECIMAL(3,2),
sentiment_timeline JSONB DEFAULT '[]',
energy_level VARCHAR(50), -- 'low', 'medium', 'high'
tension_moments JSONB DEFAULT '[]',
consensus_reached BOOLEAN,

-- Business Intelligence
decisions_made JSONB DEFAULT '[]',
action_items JSONB DEFAULT '[]',
blockers_identified JSONB DEFAULT '[]',
risks_discussed JSONB DEFAULT '[]',
opportunities_mentioned JSONB DEFAULT '[]',

-- Deal/Project Specific
deal_stage_before VARCHAR(50),
deal_stage_after VARCHAR(50),
deal_confidence_change DECIMAL(4,2),
objections_raised JSONB DEFAULT '[]',
objections_resolved JSONB DEFAULT '[]',

-- Competitive Intelligence
competitors_mentioned JSONB DEFAULT '[]',
competitive_positioning JSONB DEFAULT '{}',
win_loss_factors JSONB DEFAULT '[]',

-- Follow-up Intelligence
follow_up_required BOOLEAN DEFAULT false,
follow_up_items JSONB DEFAULT '[]',
next_meeting_suggested BOOLEAN DEFAULT false,
next_meeting_agenda JSONB DEFAULT '[]',

-- Quality Metrics
meeting_effectiveness_score DECIMAL(3,2),
objective_achievement_score DECIMAL(3,2),
time_management_score DECIMAL(3,2),
participation_balance_score DECIMAL(3,2),

-- Recommendations
meeting_improvements JSONB DEFAULT '[]',
participant_coaching JSONB DEFAULT '{}',

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),
analyzed_at TIMESTAMPTZ,

INDEX idx_meeting_intel_user_id (user_id),
INDEX idx_meeting_intel_type (meeting_type),
INDEX idx_meeting_intel_scheduled (scheduled_start),
INDEX idx_meeting_intel_effectiveness (meeting_effectiveness_score DESC)

```

);

- - =====================================================
-- DATA EXPORT & RETENTION (COMPLETE)
-- =====================================================
- - Comprehensive export tracking
CREATE TABLE data_exports (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
schema_id UUID REFERENCES user_database_schemas(id),
project_id UUID REFERENCES projects(id),

```
-- Export Configuration
export_name VARCHAR(255),
export_type VARCHAR(50) NOT NULL,
export_format VARCHAR(50) NOT NULL,
export_scope VARCHAR(50), -- 'full', 'partial', 'time_range', 'custom'

-- Data Selection
tables_included TEXT[] DEFAULT '{}',
tables_excluded TEXT[] DEFAULT '{}',
date_range_start TIMESTAMPTZ,
date_range_end TIMESTAMPTZ,
filters_applied JSONB DEFAULT '{}',
include_related_data BOOLEAN DEFAULT true,

-- Export Options
include_schema BOOLEAN DEFAULT true,
include_indexes BOOLEAN DEFAULT true,
include_constraints BOOLEAN DEFAULT true,
include_triggers BOOLEAN DEFAULT false,
include_views BOOLEAN DEFAULT true,
include_functions BOOLEAN DEFAULT false,

-- Migration Support
target_database VARCHAR(50),
migration_scripts_included BOOLEAN DEFAULT false,
compatibility_mode VARCHAR(50),

-- File Information
file_count INTEGER DEFAULT 1,
total_size_bytes BIGINT,
compression_type VARCHAR(20),
encryption_enabled BOOLEAN DEFAULT true,

-- Download Information
download_url TEXT,
download_token_hash VARCHAR(255),
download_count INTEGER DEFAULT 0,
download_expires_at TIMESTAMPTZ,

-- Intelligence Loss Analysis
features_used_count INTEGER,
insights_generated_count INTEGER,
automation_value_monthly DECIMAL(12,2),
intelligence_features_list JSONB DEFAULT '[]',

-- What They're Missing
exclusive_insights_count INTEGER,
ai_recommendations_count INTEGER,
predictive_models_count INTEGER,
estimated_value_loss_monthly DECIMAL(12,2),

-- Status
status VARCHAR(50) DEFAULT 'pending',
progress INTEGER DEFAULT 0,
error_message TEXT,

-- Timing
requested_at TIMESTAMPTZ DEFAULT NOW(),
started_at TIMESTAMPTZ,
completed_at TIMESTAMPTZ,
downloaded_at TIMESTAMPTZ,

INDEX idx_exports_user_id (user_id),
INDEX idx_exports_status (status),
INDEX idx_exports_requested (requested_at DESC)

```

);

- - Retention and re-engagement tracking
CREATE TABLE retention_tracking (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

```
-- Risk Assessment
churn_risk_score DECIMAL(3,2),
churn_risk_factors JSONB DEFAULT '[]',

-- Engagement Metrics
last_login_days_ago INTEGER,
last_project_activity_days_ago INTEGER,
last_insight_viewed_days_ago INTEGER,

-- Usage Patterns
avg_sessions_per_week DECIMAL(5,2),
avg_session_duration_minutes DECIMAL(6,2),
feature_adoption_score DECIMAL(3,2),

-- Value Metrics
total_value_generated DECIMAL(12,2),
monthly_value_trend JSONB DEFAULT '[]',
roi_achieved DECIMAL(6,2),

-- Export Behavior
total_exports INTEGER DEFAULT 0,
last_export_date DATE,
export_frequency VARCHAR(50),

-- Re-engagement
re_engagement_attempted BOOLEAN DEFAULT false,
re_engagement_method VARCHAR(50),
re_engagement_successful BOOLEAN,

-- Timestamps
calculated_at TIMESTAMPTZ DEFAULT NOW(),

UNIQUE(user_id),
INDEX idx_retention_risk (churn_risk_score DESC)

```

);

- - =====================================================
-- PERFORMANCE & MONITORING (COMPLETE)
-- =====================================================
- - User activity tracking for behavior analysis
CREATE TABLE user_activity_log (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

```
-- Activity Details
activity_type VARCHAR(100) NOT NULL,
activity_category VARCHAR(50),
activity_description TEXT,

-- Context
project_id UUID REFERENCES projects(id),
feature_used VARCHAR(100),

-- Device & Session
session_id UUID,
device_type VARCHAR(50),
browser VARCHAR(100),
ip_address INET,

-- Performance
duration_ms INTEGER,

-- Timestamp
occurred_at TIMESTAMPTZ DEFAULT NOW(),

INDEX idx_activity_user_id (user_id),
INDEX idx_activity_type (activity_type),
INDEX idx_activity_occurred (occurred_at DESC)

```

);

- - Create hypertable for activity log
SELECT create_hypertable('user_activity_log', 'occurred_at');
- - System performance metrics
CREATE TABLE system_performance_metrics (
time TIMESTAMPTZ NOT NULL,

```
-- Metric Details
metric_category VARCHAR(50) NOT NULL,
metric_name VARCHAR(100) NOT NULL,
metric_value DOUBLE PRECISION NOT NULL,

-- Dimensions
component VARCHAR(100),
instance_id VARCHAR(100),
user_id UUID REFERENCES users(id),
project_id UUID REFERENCES projects(id),

-- Tags
tags JSONB DEFAULT '{}',

PRIMARY KEY (time, metric_category, metric_name, component)

```

);

- - Create hypertable for metrics
SELECT create_hypertable('system_performance_metrics', 'time');
- - =====================================================
-- ENHANCED VIEWS FOR COMPLETE VISIBILITY
-- =====================================================
- - User journey view
CREATE VIEW v_user_journey AS
SELECT
[u.id](http://u.id/) as user_id,
u.email,
u.company_name,
u.created_at as signup_date,

```
-- Onboarding Progress
cs.phase as consultation_phase,
cs.completed_at as consultation_completed,
EXTRACT(EPOCH FROM (cs.completed_at - cs.started_at))/60 as consultation_minutes,

-- First Project
fp.name as first_project_name,
fp.created_at as first_project_date,
EXTRACT(EPOCH FROM (fp.created_at - u.created_at))/3600 as hours_to_first_project,

-- Engagement
COUNT(DISTINCT p.id) as total_projects,
COUNT(DISTINCT bi.id) as insights_generated,
COUNT(DISTINCT ar.id) as recommendations_received,
COUNT(DISTINCT ar.id) FILTER (WHERE ar.user_response = 'accepted') as recommendations_accepted,

-- Value Generated
SUM(bi.estimated_value) as total_value_identified,
AVG(ar.confidence_score) as avg_recommendation_confidence,

-- Retention Risk
rt.churn_risk_score,
u.last_active_at,

-- Export Behavior
COUNT(DISTINCT de.id) as total_exports,
MAX(de.completed_at) as last_export_date

```

FROM users u
LEFT JOIN consultation_sessions cs ON [u.id](http://u.id/) = cs.user_id AND cs.status = 'completed'
LEFT JOIN LATERAL (
SELECT * FROM projects
WHERE user_id = [u.id](http://u.id/)
ORDER BY created_at ASC
LIMIT 1
) fp ON true
LEFT JOIN projects p ON [u.id](http://u.id/) = p.user_id
LEFT JOIN business_insights bi ON [u.id](http://u.id/) = bi.user_id
LEFT JOIN ai_recommendations ar ON [u.id](http://u.id/) = ar.user_id
LEFT JOIN retention_tracking rt ON [u.id](http://u.id/) = rt.user_id
LEFT JOIN data_exports de ON [u.id](http://u.id/) = de.user_id AND de.status = 'completed'

GROUP BY [u.id](http://u.id/), u.email, u.company_name, u.created_at, cs.phase, cs.completed_at,
cs.started_at, [fp.name](http://fp.name/), fp.created_at, rt.churn_risk_score, u.last_active_at;

- - Real-time system health dashboard
CREATE VIEW v_system_health AS
SELECT
-- User Metrics
COUNT(DISTINCT [u.id](http://u.id/)) as total_users,
COUNT(DISTINCT [u.id](http://u.id/)) FILTER (WHERE u.last_active_at > NOW() - INTERVAL '24 hours') as daily_active_users,
COUNT(DISTINCT [u.id](http://u.id/)) FILTER (WHERE u.last_active_at > NOW() - INTERVAL '7 days') as weekly_active_users,

```
-- Project Metrics
COUNT(DISTINCT p.id) as total_projects,
COUNT(DISTINCT p.id) FILTER (WHERE p.created_at > NOW() - INTERVAL '24 hours') as projects_created_24h,

-- Agent Performance
AVG(ae.execution_time_ms) FILTER (WHERE ae.created_at > NOW() - INTERVAL '1 hour') as avg_agent_execution_time,
COUNT(ae.id) FILTER (WHERE ae.status = 'failed' AND ae.created_at > NOW() - INTERVAL '1 hour') as failed_executions_1h,

-- Database Usage
COUNT(DISTINCT uds.id) as total_user_databases,
SUM(uds.total_records) as total_records_managed,
SUM(uds.storage_used_mb) as total_storage_mb,

-- Business Intelligence
COUNT(DISTINCT bi.id) FILTER (WHERE bi.generated_at > NOW() - INTERVAL '24 hours') as insights_generated_24h,
AVG(bi.confidence_score) FILTER (WHERE bi.generated_at > NOW() - INTERVAL '24 hours') as avg_insight_confidence,

-- System Load
(SELECT AVG(metric_value) FROM system_performance_metrics
 WHERE metric_name = 'cpu_usage' AND time > NOW() - INTERVAL '5 minutes') as current_cpu_usage,

(SELECT AVG(metric_value) FROM system_performance_metrics
 WHERE metric_name = 'memory_usage' AND time > NOW() - INTERVAL '5 minutes') as current_memory_usage

```

FROM users u
CROSS JOIN projects p
CROSS JOIN agent_executions ae
CROSS JOIN user_database_schemas uds
CROSS JOIN business_insights bi;

- - =====================================================
-- CRITICAL INDEXES FOR PERFORMANCE
-- =====================================================
- - Memory search optimization
CREATE INDEX idx_memory_search ON conversation_memory USING gin(
to_tsvector('english', content || ' ' || COALESCE(memory_key, ''))
);
- - Consultation flow optimization
CREATE INDEX idx_consultation_flow ON consultation_sessions(user_id, phase, status);
CREATE INDEX idx_consultation_messages_search ON consultation_messages USING gin(
to_tsvector('english', content)
);
- - Real-time analytics
CREATE INDEX idx_user_last_active ON users(last_active_at DESC);
CREATE INDEX idx_projects_recent ON projects(created_at DESC) WHERE status = 'active';
CREATE INDEX idx_insights_recent ON business_insights(generated_at DESC) WHERE viewed = false;
- - =====================================================
-- TRIGGERS FOR INTELLIGENT BEHAVIOR
-- =====================================================
- - Update user last_active_at
CREATE OR REPLACE FUNCTION update_user_last_active()
RETURNS TRIGGER AS $$
BEGIN
UPDATE users
SET last_active_at = NOW()
WHERE id = NEW.user_id;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_last_active
AFTER INSERT ON user_activity_log
FOR EACH ROW
EXECUTE FUNCTION update_user_last_active();

- - Auto-create retention opportunity after export
CREATE OR REPLACE FUNCTION create_retention_opportunity()
RETURNS TRIGGER AS $$
DECLARE
v_value_loss DECIMAL(12,2);
BEGIN
IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
-- Calculate value loss
v_value_loss := COALESCE(NEW.estimated_value_loss_monthly, 0);

```
    -- Update retention tracking
    INSERT INTO retention_tracking (
        user_id,
        last_export_date,
        total_exports,
        churn_risk_score
    ) VALUES (
        NEW.user_id,
        NEW.completed_at::DATE,
        1,
        CASE
            WHEN v_value_loss > 1000 THEN 0.8
            WHEN v_value_loss > 500 THEN 0.6
            ELSE 0.4
        END
    )
    ON CONFLICT (user_id) DO UPDATE SET
        last_export_date = EXCLUDED.last_export_date,
        total_exports = retention_tracking.total_exports + 1,
        churn_risk_score = GREATEST(retention_tracking.churn_risk_score, EXCLUDED.churn_risk_score);
END IF;

RETURN NEW;

```

END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_retention_after_export
AFTER UPDATE ON data_exports
FOR EACH ROW
EXECUTE FUNCTION create_retention_opportunity();

- - =====================================================
-- INITIAL DATA FOR AGENTS
-- =====================================================

INSERT INTO agents (agent_type, name, description, capabilities) VALUES
('orchestrator', 'Orchestration Agent', 'Central coordinator for all agent activities',
'["task_planning", "agent_coordination", "result_synthesis", "conflict_resolution"]'::jsonb),

('communication', 'Communication Agent', 'Natural language interface and conversation management',
'["natural_language_processing", "context_management", "emotional_intelligence", "voice_processing"]'::jsonb),

('analysis', 'Analysis Agent', 'Business intelligence and market research',
'["market_research", "competitive_analysis", "data_visualization", "trend_identification", "roi_calculation"]'::jsonb),

('development', 'Development Agent', 'Code generation and application building',
'["code_generation", "architecture_design", "testing", "optimization", "debugging"]'::jsonb),

('strategy', 'Strategy Agent', 'Business strategy and growth planning',
'["revenue_modeling", "growth_planning", "market_expansion", "business_validation", "pricing_strategy"]'::jsonb),

('deployment', 'Deployment Agent', 'Infrastructure and deployment management',
'["infrastructure_provisioning", "ci_cd_management", "monitoring", "scaling", "security_hardening"]'::jsonb),

('quality', 'Quality Agent', 'Code quality and security assurance',
'["code_review", "security_scanning", "performance_testing", "compliance_checking", "best_practices"]'::jsonb),

('data', 'Data Agent', 'Database design and data intelligence',
'["schema_design", "data_modeling", "query_optimization", "data_migration", "analytics_setup"]'::jsonb);

- - =====================================================
-- MAINTENANCE NOTES
-- =====================================================
- - This schema is PRODUCTION-READY and includes:
-- 1. Complete consultation flow tracking
-- 2. Long-term memory and context persistence
-- 3. AI recommendation tracking with outcomes
-- 4. Multi-tenant user databases with full isolation
-- 5. Comprehensive business intelligence
-- 6. Deep integration intelligence (email, meetings)
-- 7. Export tracking with retention analysis
-- 8. Performance monitoring and optimization
-- 9. Intelligent triggers for automation
-- 10. Voice support throughout the system
- - Regular maintenance tasks:
-- 1. Run VACUUM ANALYZE weekly
-- 2. Update table statistics daily
-- 3. Monitor hypertable chunk sizes
-- 4. Archive old activity logs monthly
-- 5. Refresh materialized views as needed