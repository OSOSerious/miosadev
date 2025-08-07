- - MIOSA Database Schema - Base44 Architecture Additions
-- These tables complement the main schema to support Base44-like functionality
- - =====================================================
-- APP TEMPLATES & GENERATION
-- =====================================================
- - App templates library (like Base44's idea library)
CREATE TABLE app_templates (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

```
-- Template Details
name VARCHAR(255) NOT NULL,
slug VARCHAR(255) UNIQUE NOT NULL,
category VARCHAR(100) NOT NULL, -- 'crm', 'ecommerce', 'finance', 'travel', 'home_management'
subcategory VARCHAR(100),

-- Template Content
description TEXT,
preview_image_url TEXT,
demo_url TEXT,

-- Base Configuration
initial_prompt TEXT, -- Seed prompt for users
default_features JSONB DEFAULT '[]',
default_integrations JSONB DEFAULT '[]',
default_data_schema JSONB DEFAULT '{}',

-- UI Configuration
default_theme JSONB DEFAULT '{}',
design_style VARCHAR(50), -- 'claymorphism', 'glassmorphism', 'minimal', 'modern'
color_scheme JSONB DEFAULT '{}',

-- Popularity & Usage
usage_count INTEGER DEFAULT 0,
rating DECIMAL(3,2),

-- Status
is_featured BOOLEAN DEFAULT false,
is_active BOOLEAN DEFAULT true,

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),
updated_at TIMESTAMPTZ DEFAULT NOW(),

INDEX idx_templates_category (category),
INDEX idx_templates_featured (is_featured)

```

);

- - Generated app schemas (automatic database structure)
CREATE TABLE app_generated_schemas (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

```
-- Schema Generation
generation_method VARCHAR(50), -- 'ai_generated', 'template_based', 'manual'
source_prompt TEXT,

-- Schema Structure
tables JSONB NOT NULL DEFAULT '[]', -- Array of table definitions
relationships JSONB DEFAULT '[]', -- Foreign keys, joins
indexes JSONB DEFAULT '[]',

-- Data Model
entities JSONB DEFAULT '[]', -- Business entities identified
attributes JSONB DEFAULT '{}', -- Attributes per entity

-- Validation Rules
validation_rules JSONB DEFAULT '{}',
business_rules JSONB DEFAULT '[]',

-- Migration Support
migration_sql TEXT, -- SQL to create the schema
rollback_sql TEXT, -- SQL to rollback

-- Version Control
version INTEGER DEFAULT 1,
is_current BOOLEAN DEFAULT true,

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),
applied_at TIMESTAMPTZ,

INDEX idx_app_schemas_project (project_id)

```

);

- - =====================================================
-- AUTHENTICATION & PERMISSIONS SYSTEM
-- =====================================================
- - App-specific authentication configuration
CREATE TABLE app_auth_config (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

```
-- Auth Methods
email_password_enabled BOOLEAN DEFAULT true,
magic_link_enabled BOOLEAN DEFAULT false,

-- OAuth Providers
oauth_providers JSONB DEFAULT '[]', -- ['google', 'microsoft', 'facebook', 'github']
oauth_configs JSONB DEFAULT '{}', -- Provider-specific settings

-- SSO Configuration
sso_enabled BOOLEAN DEFAULT false,
sso_providers JSONB DEFAULT '[]',
saml_config JSONB DEFAULT '{}',

-- Session Configuration
session_duration_minutes INTEGER DEFAULT 10080, -- 7 days
refresh_token_enabled BOOLEAN DEFAULT true,

-- Security Settings
require_email_verification BOOLEAN DEFAULT true,
mfa_enabled BOOLEAN DEFAULT false,
password_policy JSONB DEFAULT '{"min_length": 8, "require_uppercase": true, "require_number": true}',

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),
updated_at TIMESTAMPTZ DEFAULT NOW(),

UNIQUE(project_id)

```

);

- - App-specific user roles and permissions
CREATE TABLE app_roles (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

```
-- Role Definition
role_name VARCHAR(100) NOT NULL,
role_slug VARCHAR(100) NOT NULL,
description TEXT,

-- Permissions
permissions JSONB NOT NULL DEFAULT '[]', -- Array of permission strings
resource_access JSONB DEFAULT '{}', -- Resource-level permissions

-- UI Permissions
allowed_pages JSONB DEFAULT '[]',
hidden_components JSONB DEFAULT '[]',

-- Data Permissions
data_access_rules JSONB DEFAULT '{}', -- Row-level security rules

-- Hierarchy
parent_role_id UUID REFERENCES app_roles(id),
priority INTEGER DEFAULT 0,

-- Status
is_active BOOLEAN DEFAULT true,
is_system_role BOOLEAN DEFAULT false, -- Built-in roles

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),

UNIQUE(project_id, role_slug),
INDEX idx_app_roles_project (project_id)

```

);

- - App users (end users of generated apps)
CREATE TABLE app_users (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

```
-- Authentication
email VARCHAR(255),
email_verified BOOLEAN DEFAULT false,
password_hash VARCHAR(255),

-- OAuth Identities
oauth_identities JSONB DEFAULT '[]', -- Array of {provider, provider_id, email}

-- Profile
display_name VARCHAR(255),
avatar_url TEXT,
profile_data JSONB DEFAULT '{}', -- Custom profile fields

-- Roles & Permissions
role_ids UUID[] DEFAULT '{}',
custom_permissions JSONB DEFAULT '[]',

-- Session Management
last_login_at TIMESTAMPTZ,
login_count INTEGER DEFAULT 0,

-- Status
status VARCHAR(50) DEFAULT 'active',
blocked_at TIMESTAMPTZ,
blocked_reason TEXT,

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),
updated_at TIMESTAMPTZ DEFAULT NOW(),

UNIQUE(project_id, email),
INDEX idx_app_users_project (project_id),
INDEX idx_app_users_email (email)

```

);

- - =====================================================
-- VISUAL EDITOR & UI COMPONENTS
-- =====================================================
- - UI component library
CREATE TABLE ui_components (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

```
-- Component Details
name VARCHAR(255) NOT NULL,
category VARCHAR(100), -- 'layout', 'form', 'data', 'navigation', 'media'
component_type VARCHAR(100) NOT NULL,

-- Component Code
react_code TEXT,
vue_code TEXT,
svelte_code TEXT,

-- Properties
default_props JSONB DEFAULT '{}',
prop_definitions JSONB DEFAULT '[]', -- Schema for props

-- Styling
default_styles JSONB DEFAULT '{}',
style_variants JSONB DEFAULT '[]',

-- Events
supported_events JSONB DEFAULT '[]',

-- Usage
is_premium BOOLEAN DEFAULT false,
usage_count INTEGER DEFAULT 0,

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),
updated_at TIMESTAMPTZ DEFAULT NOW()

```

);

- - Visual editor state per project
CREATE TABLE visual_editor_state (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

```
-- Page Structure
pages JSONB NOT NULL DEFAULT '[]', -- Array of page configurations
current_page_id VARCHAR(255),

-- Component Tree
component_tree JSONB DEFAULT '{}', -- Hierarchical component structure
selected_component_id VARCHAR(255),

-- Design System
theme JSONB DEFAULT '{}',
design_tokens JSONB DEFAULT '{}', -- Colors, spacing, typography
global_styles JSONB DEFAULT '{}',

-- Layout
responsive_breakpoints JSONB DEFAULT '{"mobile": 640, "tablet": 768, "desktop": 1024}',
grid_settings JSONB DEFAULT '{}',

-- State Management
app_state_schema JSONB DEFAULT '{}',
global_state JSONB DEFAULT '{}',

-- History
undo_stack JSONB DEFAULT '[]',
redo_stack JSONB DEFAULT '[]',

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),
last_edited_at TIMESTAMPTZ DEFAULT NOW(),

UNIQUE(project_id)

```

);

- - =====================================================
-- BUILT-IN INTEGRATIONS
-- =====================================================
- - Integration templates (pre-configured integrations)
CREATE TABLE integration_templates (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

```
-- Template Info
provider VARCHAR(100) NOT NULL, -- 'email', 'sms', 'stripe', 'google', 'slack'
name VARCHAR(255) NOT NULL,
description TEXT,

-- Configuration Template
default_config JSONB DEFAULT '{}',
required_fields JSONB DEFAULT '[]',
optional_fields JSONB DEFAULT '[]',

-- API Details
base_url TEXT,
auth_method VARCHAR(50), -- 'api_key', 'oauth2', 'basic'

-- Features
supported_actions JSONB DEFAULT '[]', -- ['send_email', 'send_sms', 'charge_payment']
webhooks_supported BOOLEAN DEFAULT false,

-- Documentation
docs_url TEXT,
example_usage JSONB DEFAULT '{}',

-- Status
is_active BOOLEAN DEFAULT true,
is_premium BOOLEAN DEFAULT false,

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW()

```

);

- - App-specific integration instances
CREATE TABLE app_integrations (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
template_id UUID REFERENCES integration_templates(id),

```
-- Integration Details
name VARCHAR(255) NOT NULL,
provider VARCHAR(100) NOT NULL,

-- Configuration
config JSONB DEFAULT '{}', -- Encrypted sensitive data
is_configured BOOLEAN DEFAULT false,

-- Usage
enabled BOOLEAN DEFAULT true,
usage_count INTEGER DEFAULT 0,
last_used_at TIMESTAMPTZ,

-- Webhooks
webhook_endpoint TEXT,
webhook_secret_hash VARCHAR(255),

-- Status
health_status VARCHAR(50) DEFAULT 'unknown',
last_health_check TIMESTAMPTZ,
error_message TEXT,

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),
configured_at TIMESTAMPTZ,

INDEX idx_app_integrations_project (project_id)

```

);

- - Auto-generated API endpoints
CREATE TABLE app_api_endpoints (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

```
-- Endpoint Details
path VARCHAR(255) NOT NULL,
method VARCHAR(10) NOT NULL, -- 'GET', 'POST', 'PUT', 'DELETE', 'PATCH'

-- Configuration
authentication_required BOOLEAN DEFAULT true,
required_permissions JSONB DEFAULT '[]',

-- Request/Response
request_schema JSONB DEFAULT '{}',
response_schema JSONB DEFAULT '{}',

-- Implementation
handler_type VARCHAR(50), -- 'database', 'custom', 'integration'
handler_config JSONB DEFAULT '{}',

-- Rate Limiting
rate_limit_enabled BOOLEAN DEFAULT true,
rate_limit_config JSONB DEFAULT '{"requests_per_minute": 60}',

-- Documentation
description TEXT,
example_request JSONB,
example_response JSONB,

-- Usage Metrics
total_calls BIGINT DEFAULT 0,
avg_response_time_ms INTEGER,

-- Status
is_active BOOLEAN DEFAULT true,

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),
last_called_at TIMESTAMPTZ,

UNIQUE(project_id, path, method),
INDEX idx_api_endpoints_project (project_id)

```

);

- - =====================================================
-- DEPLOYMENT & HOSTING
-- =====================================================
- - Deployment configurations
CREATE TABLE deployment_configs (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

```
-- Environment
environment VARCHAR(50) NOT NULL, -- 'development', 'staging', 'production'

-- URLs
deployment_url TEXT,
custom_domain TEXT,
subdomain VARCHAR(255), -- base44 subdomain

-- SSL Configuration
ssl_enabled BOOLEAN DEFAULT true,
ssl_certificate_id VARCHAR(255),
ssl_auto_renew BOOLEAN DEFAULT true,

-- Resources
compute_tier VARCHAR(50) DEFAULT 'starter', -- 'starter', 'growth', 'scale'
memory_mb INTEGER DEFAULT 512,
cpu_units INTEGER DEFAULT 256,

-- Auto-scaling
auto_scaling_enabled BOOLEAN DEFAULT false,
min_instances INTEGER DEFAULT 1,
max_instances INTEGER DEFAULT 3,

-- CDN Configuration
cdn_enabled BOOLEAN DEFAULT true,
cdn_regions JSONB DEFAULT '["us", "eu", "asia"]',

-- Environment Variables
env_variables JSONB DEFAULT '{}', -- Encrypted

-- Status
deployment_status VARCHAR(50) DEFAULT 'not_deployed',
last_deployment_at TIMESTAMPTZ,

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),
updated_at TIMESTAMPTZ DEFAULT NOW(),

UNIQUE(project_id, environment),
INDEX idx_deployment_project (project_id)

```

);

- - Domain management
CREATE TABLE app_domains (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

```
-- Domain Details
domain_name VARCHAR(255) NOT NULL,
subdomain VARCHAR(255),

-- DNS Configuration
dns_configured BOOLEAN DEFAULT false,
dns_records JSONB DEFAULT '[]',
nameservers JSONB DEFAULT '[]',

-- Verification
verification_method VARCHAR(50), -- 'dns', 'file'
verification_token VARCHAR(255),
verified_at TIMESTAMPTZ,

-- SSL
ssl_status VARCHAR(50) DEFAULT 'pending',
ssl_issued_at TIMESTAMPTZ,
ssl_expires_at TIMESTAMPTZ,

-- Status
status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'active', 'failed'

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),

UNIQUE(domain_name),
INDEX idx_domains_project (project_id)

```

);

- - =====================================================
-- COLLABORATION FEATURES
-- =====================================================
- - Shared workspaces for collaboration
CREATE TABLE project_workspaces (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

```
-- Workspace Details
name VARCHAR(255) DEFAULT 'Main Workspace',
description TEXT,

-- Access Control
visibility VARCHAR(50) DEFAULT 'private', -- 'private', 'team', 'public'
invite_link_hash VARCHAR(255),
invite_link_expires_at TIMESTAMPTZ,

-- Settings
allow_anonymous_view BOOLEAN DEFAULT false,
require_approval BOOLEAN DEFAULT true,

-- Activity
active_users INTEGER DEFAULT 0,
total_edits INTEGER DEFAULT 0,

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),
last_activity_at TIMESTAMPTZ,

UNIQUE(project_id)

```

);

- - Workspace members
CREATE TABLE workspace_members (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
workspace_id UUID NOT NULL REFERENCES project_workspaces(id) ON DELETE CASCADE,
user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

```
-- Access Level
role VARCHAR(50) NOT NULL, -- 'owner', 'admin', 'editor', 'viewer'
permissions JSONB DEFAULT '[]',

-- Activity
last_active_at TIMESTAMPTZ,
contribution_count INTEGER DEFAULT 0,

-- Status
status VARCHAR(50) DEFAULT 'active',
invited_by UUID REFERENCES users(id),

-- Timestamps
joined_at TIMESTAMPTZ DEFAULT NOW(),

UNIQUE(workspace_id, user_id),
INDEX idx_workspace_members (workspace_id)

```

);

- - Real-time collaboration sessions
CREATE TABLE collaboration_sessions (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
workspace_id UUID NOT NULL REFERENCES project_workspaces(id) ON DELETE CASCADE,

```
-- Session Info
session_token VARCHAR(255) UNIQUE NOT NULL,

-- Participants
active_users JSONB DEFAULT '[]', -- Array of {user_id, cursor_position, selected_component}

-- State Sync
last_sync_at TIMESTAMPTZ DEFAULT NOW(),
sync_version INTEGER DEFAULT 1,

-- Activity
changes_count INTEGER DEFAULT 0,

-- Timestamps
started_at TIMESTAMPTZ DEFAULT NOW(),
expires_at TIMESTAMPTZ,

INDEX idx_collab_sessions_workspace (workspace_id)

```

);

- - =====================================================
-- VERSION CONTROL & HISTORY
-- =====================================================
- - Project version snapshots (more detailed than project_builds)
CREATE TABLE project_snapshots (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

```
-- Version Info
version_number VARCHAR(50) NOT NULL,
version_tag VARCHAR(255),

-- Snapshot Type
snapshot_type VARCHAR(50), -- 'manual', 'auto', 'pre_deploy', 'rollback'

-- Complete State
project_config JSONB NOT NULL, -- Full project configuration
database_schema JSONB NOT NULL,
visual_editor_state JSONB NOT NULL,
api_endpoints JSONB NOT NULL,
integrations JSONB NOT NULL,

-- Changes
changes_summary TEXT,
changed_by UUID REFERENCES users(id),

-- Deployment
is_deployed BOOLEAN DEFAULT false,
deployed_to_environments JSONB DEFAULT '[]',

-- Timestamps
created_at TIMESTAMPTZ DEFAULT NOW(),

INDEX idx_snapshots_project (project_id),
INDEX idx_snapshots_created (created_at DESC)

```

);

- - =====================================================
-- ANALYTICS & MONITORING
-- =====================================================
- - App usage analytics (for built apps)
CREATE TABLE app_analytics (
time TIMESTAMPTZ NOT NULL,
project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

```
-- Metrics
metric_type VARCHAR(100) NOT NULL, -- 'page_view', 'api_call', 'user_action', 'error'
metric_name VARCHAR(255),
metric_value DOUBLE PRECISION DEFAULT 1,

-- Context
user_id UUID, -- App user, not platform user
session_id VARCHAR(255),
page_path VARCHAR(255),

-- Device Info
device_type VARCHAR(50),
browser VARCHAR(100),
os VARCHAR(100),

-- Location
country_code VARCHAR(2),
region VARCHAR(100),

-- Additional Data
metadata JSONB DEFAULT '{}',

PRIMARY KEY (time, project_id, metric_type)

```

);

- - Create hypertable for app analytics
SELECT create_hypertable('app_analytics', 'time');
- - =====================================================
-- CREDIT & USAGE TRACKING
-- =====================================================
- - Integration credits usage
CREATE TABLE integration_credits_usage (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
project_id UUID REFERENCES projects(id),

```
-- Credit Details
credits_used INTEGER NOT NULL,
integration_type VARCHAR(100), -- 'llm', 'email', 'sms', 'storage', 'api'

-- Context
action_description TEXT,
endpoint_called VARCHAR(255),

-- Response
success BOOLEAN DEFAULT true,
error_message TEXT,
response_time_ms INTEGER,

-- Timestamp
used_at TIMESTAMPTZ DEFAULT NOW(),

INDEX idx_credits_user (user_id),
INDEX idx_credits_project (project_id),
INDEX idx_credits_used_at (used_at DESC)

```

);

- - Create hypertable for credits usage
SELECT create_hypertable('integration_credits_usage', 'used_at');
- - =====================================================
-- DISCUSSION MODE & AI ARCHITECTURE CHAT
-- =====================================================
- - Architecture discussions (Base44's "Discuss Mode")
CREATE TABLE architecture_discussions (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

```
-- Discussion Context
discussion_type VARCHAR(50), -- 'pre_build', 'refinement', 'troubleshooting'
topic VARCHAR(255),

-- Messages
messages JSONB DEFAULT '[]', -- Array of {role, content, timestamp}

-- Decisions Made
architecture_decisions JSONB DEFAULT '[]',
schema_decisions JSONB DEFAULT '[]',

-- Status
status VARCHAR(50) DEFAULT 'active',
resolved BOOLEAN DEFAULT false,

-- Timestamps
started_at TIMESTAMPTZ DEFAULT NOW(),
last_message_at TIMESTAMPTZ,

INDEX idx_discussions_project (project_id)

```

);

- - =====================================================
-- ENHANCED VIEWS FOR BASE44 FUNCTIONALITY
-- =====================================================
- - Project overview with Base44 metrics
CREATE VIEW v_project_base44_overview AS
SELECT
[p.id](http://p.id/),
[p.name](http://p.name/),
p.status,
p.deployment_url,

```
-- Template Used
at.name as template_name,
at.category as template_category,

-- Authentication
aac.oauth_providers,
COUNT(DISTINCT au.id) as total_app_users,

-- Integrations
COUNT(DISTINCT ai.id) as active_integrations,

-- API Endpoints
COUNT(DISTINCT aae.id) as api_endpoints_count,

-- Deployment
dc.environment,
dc.custom_domain,
dc.deployment_status,

-- Collaboration
COUNT(DISTINCT wm.user_id) as team_members,

-- Usage
SUM(icu.credits_used) as total_credits_used

```

FROM projects p
LEFT JOIN app_templates at ON [p.id](http://p.id/) = [at.id](http://at.id/) -- Assuming template reference
LEFT JOIN app_auth_config aac ON [p.id](http://p.id/) = aac.project_id
LEFT JOIN app_users au ON [p.id](http://p.id/) = au.project_id
LEFT JOIN app_integrations ai ON [p.id](http://p.id/) = ai.project_id AND ai.enabled = true
LEFT JOIN app_api_endpoints aae ON [p.id](http://p.id/) = aae.project_id
LEFT JOIN deployment_configs dc ON [p.id](http://p.id/) = dc.project_id AND dc.environment = 'production'
LEFT JOIN project_workspaces pw ON [p.id](http://p.id/) = pw.project_id
LEFT JOIN workspace_members wm ON [pw.id](http://pw.id/) = wm.workspace_id
LEFT JOIN integration_credits_usage icu ON [p.id](http://p.id/) = icu.project_id

GROUP BY [p.id](http://p.id/), [p.name](http://p.name/), p.status, p.deployment_url, [at.name](http://at.name/), at.category,
aac.oauth_providers, dc.environment, dc.custom_domain, dc.deployment_status;

- - =====================================================
-- TRIGGERS FOR BASE44 FUNCTIONALITY
-- =====================================================
- - Auto-generate API endpoints when database schema changes
CREATE OR REPLACE FUNCTION auto_generate_api_endpoints()
RETURNS TRIGGER AS $$
DECLARE
v_table JSONB;
BEGIN
-- For each table in the schema
FOR v_table IN SELECT * FROM jsonb_array_elements(NEW.tables)
LOOP
-- Generate CRUD endpoints
INSERT INTO app_api_endpoints (
project_id,
path,
method,
handler_type,
handler_config,
description
) VALUES
-- GET all
(NEW.project_id,
'/api/' || (v_table->>'name') || 's',
'GET',
'database',
jsonb_build_object('table', v_table->>'name', 'operation', 'list'),
'Get all ' || (v_table->>'name') || 's'),
-- GET one
(NEW.project_id,
'/api/' || (v_table->>'name') || 's/:id',
'GET',
'database',
jsonb_build_object('table', v_table->>'name', 'operation', 'get'),
'Get ' || (v_table->>'name') || ' by ID'),
-- POST
(NEW.project_id,
'/api/' || (v_table->>'name') || 's',
'POST',
'database',
jsonb_build_object('table', v_table->>'name', 'operation', 'create'),
'Create new ' || (v_table->>'name')),
-- PUT
(NEW.project_id,
'/api/' || (v_table->>'name') || 's/:id',
'PUT',
'database',
jsonb_build_object('table', v_table->>'name', 'operation', 'update'),
'Update ' || (v_table->>'name')),
-- DELETE
(NEW.project_id,
'/api/' || (v_table->>'name') || 's/:id',
'DELETE',
'database',
jsonb_build_object('table', v_table->>'name', 'operation', 'delete'),
'Delete ' || (v_table->>'name'))
ON CONFLICT (project_id, path, method) DO NOTHING;
END LOOP;

```
RETURN NEW;

```

END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auto_generate_api
AFTER INSERT OR UPDATE ON app_generated_schemas
FOR EACH ROW
WHEN (NEW.is_current = true)
EXECUTE FUNCTION auto_generate_api_endpoints();

- - Track integration credit usage
CREATE OR REPLACE FUNCTION track_integration_usage()
RETURNS TRIGGER AS $$
BEGIN
-- Record credit usage when integration is called
INSERT INTO integration_credits_usage (
user_id,
project_id,
credits_used,
integration_type,
action_description,
used_at
) VALUES (
NEW.user_id,
NEW.project_id,
1, -- Each request = 1 credit as per Base44
CASE
WHEN NEW.path LIKE '%/ai/%' THEN 'llm'
WHEN NEW.path LIKE '%/email/%' THEN 'email'
WHEN NEW.path LIKE '%/sms/%' THEN 'sms'
ELSE 'api'
END,
NEW.method || ' ' || NEW.path,
NOW()
);

```
RETURN NEW;

```

END;
$$ LANGUAGE plpgsql;

- - =====================================================
-- INITIAL DATA FOR BASE44 FEATURES
-- =====================================================
- - Insert default app templates
INSERT INTO app_templates (name, slug, category, description, initial_prompt, default_features) VALUES
('CRM System', 'crm-system', 'crm', 'Customer relationship management with leads, contacts, and deals',
'I need a CRM to manage my sales pipeline with contact management and deal tracking',
'["contact_management", "deal_pipeline", "activity_tracking", "email_integration"]'::jsonb),

('E-commerce Store', 'ecommerce-store', 'ecommerce', 'Online store with products, cart, and checkout',
'I want to build an online store to sell products with shopping cart and payment processing',
'["product_catalog", "shopping_cart", "checkout", "order_management", "payment_integration"]'::jsonb),

('Task Manager', 'task-manager', 'productivity', 'Project and task management with team collaboration',
'I need a task management app for my team with projects, tasks, and assignments',
'["project_management", "task_tracking", "team_collaboration", "notifications"]'::jsonb),

('Appointment Booking', 'appointment-booking', 'scheduling', 'Service booking with calendar integration',
'I want to build an appointment booking system for my services with availability management',
'["calendar_view", "availability_management", "booking_flow", "reminders"]'::jsonb),

('Inventory Management', 'inventory-management', 'operations', 'Track inventory, suppliers, and orders',
'I need an inventory management system to track stock levels and manage suppliers',
'["stock_tracking", "supplier_management", "purchase_orders", "low_stock_alerts"]'::jsonb);

- - Insert integration templates
INSERT INTO integration_templates (provider, name, description, supported_actions, auth_method) VALUES
('email', 'Email Service', 'Send transactional and marketing emails',
'["send_email", "send_bulk", "track_opens", "track_clicks"]'::jsonb, 'api_key'),

('sms', 'SMS Service', 'Send SMS notifications and alerts',
'["send_sms", "send_bulk_sms", "delivery_status"]'::jsonb, 'api_key'),

('stripe', 'Stripe Payments', 'Accept payments and manage subscriptions',
'["create_payment", "create_subscription", "refund", "webhook"]'::jsonb, 'api_key'),

('openai', 'OpenAI Integration', 'Add AI capabilities to your app',
'["chat_completion", "text_generation", "embeddings"]'::jsonb, 'api_key'),

('google', 'Google Services', 'Calendar, Drive, and other Google services',
'["calendar_events", "drive_files", "sheets_data"]'::jsonb, 'oauth2'),

('slack', 'Slack Integration', 'Send notifications to Slack channels',
'["send_message", "create_channel", "upload_file"]'::jsonb, 'oauth2');

- - =====================================================
-- MAINTENANCE NOTES FOR BASE44 FEATURES
-- =====================================================
- - This extension adds all Base44-specific functionality:
-- 1. App template library for quick starts
-- 2. Automatic database schema generation
-- 3. Built-in authentication with OAuth support
-- 4. Role-based permissions per app
-- 5. Visual editor state management
-- 6. Pre-configured integrations
-- 7. Auto-generated API endpoints
-- 8. Deployment and domain management
-- 9. Real-time collaboration
-- 10. Version control with snapshots
-- 11. App analytics and monitoring
-- 12. Credit usage tracking
-- 13. Architecture discussion mode