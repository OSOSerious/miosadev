-- Simple schema for MIOSA to get it working NOW

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create consultation sessions table
CREATE TABLE IF NOT EXISTS consultation_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    phase VARCHAR(50) DEFAULT 'initial',
    context JSONB DEFAULT '{}',
    ready_for_generation BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create consultation messages table
CREATE TABLE IF NOT EXISTS consultation_messages (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES consultation_sessions(id),
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    phase VARCHAR(50),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create generated applications table
CREATE TABLE IF NOT EXISTS generated_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES consultation_sessions(id),
    project_id VARCHAR(255) UNIQUE NOT NULL,
    project_name VARCHAR(255),
    components JSONB DEFAULT '{}',
    requirements JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_sessions_user ON consultation_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_session ON consultation_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_apps_session ON generated_applications(session_id);

-- Insert a test user
INSERT INTO users (email, full_name) 
VALUES ('cli@miosa.ai', 'CLI User')
ON CONFLICT (email) DO NOTHING;