-- Create table for tracking generated applications
CREATE TABLE IF NOT EXISTS generated_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES consultation_sessions(id),
    project_id VARCHAR(255) UNIQUE NOT NULL,
    project_name VARCHAR(255),
    description TEXT,
    
    -- Component tracking
    database_schema JSONB,
    backend_config JSONB,
    frontend_config JSONB,
    integrations JSONB,
    deployment_config JSONB,
    
    -- Metadata
    requirements JSONB,
    generation_status VARCHAR(50) DEFAULT 'pending',
    generation_started_at TIMESTAMP,
    generation_completed_at TIMESTAMP,
    
    -- Files generated
    files_generated INTEGER DEFAULT 0,
    total_lines_of_code INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_generated_applications_session_id ON generated_applications(session_id);
CREATE INDEX idx_generated_applications_project_id ON generated_applications(project_id);
CREATE INDEX idx_generated_applications_status ON generated_applications(generation_status);

-- Add generation_phase to consultation_sessions if not exists
ALTER TABLE consultation_sessions 
ADD COLUMN IF NOT EXISTS generation_phase VARCHAR(50) DEFAULT 'initial';

ALTER TABLE consultation_sessions 
ADD COLUMN IF NOT EXISTS ready_for_generation BOOLEAN DEFAULT FALSE;

-- Create table for generation logs
CREATE TABLE IF NOT EXISTS generation_logs (
    id SERIAL PRIMARY KEY,
    application_id UUID REFERENCES generated_applications(id),
    phase VARCHAR(100),
    message TEXT,
    details JSONB,
    log_level VARCHAR(20) DEFAULT 'info',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for generated_applications
DROP TRIGGER IF EXISTS update_generated_applications_updated_at ON generated_applications;
CREATE TRIGGER update_generated_applications_updated_at 
BEFORE UPDATE ON generated_applications 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();