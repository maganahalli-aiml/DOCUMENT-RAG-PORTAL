-- Document RAG Portal Database Initialization
-- This script sets up the database schema for the portal

-- Create database and user (handled by docker-compose environment)
-- CREATE DATABASE document_portal;
-- CREATE USER portal_user WITH PASSWORD 'portal_password';
-- GRANT ALL PRIVILEGES ON DATABASE document_portal TO portal_user;

-- Connect to the database
\c document_portal;

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables for document management
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    content_type VARCHAR(100),
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    processing_status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tables for user sessions (if needed for advanced auth)
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(100) NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    user_role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

-- Create tables for cache management (if using SQL cache)
CREATE TABLE IF NOT EXISTS cache_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    cache_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tables for document comparisons
CREATE TABLE IF NOT EXISTS document_comparisons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document1_id UUID REFERENCES documents(id),
    document2_id UUID REFERENCES documents(id),
    similarity_score DECIMAL(5,4),
    comparison_method VARCHAR(50),
    common_words INTEGER,
    unique_words_doc1 INTEGER,
    unique_words_doc2 INTEGER,
    comparison_metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(100)
);

-- Create tables for system metrics
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,4),
    metric_unit VARCHAR(50),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_documents_filename ON documents(filename);
CREATE INDEX IF NOT EXISTS idx_documents_upload_timestamp ON documents(upload_timestamp);
CREATE INDEX IF NOT EXISTS idx_documents_processed ON documents(processed);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_cache_entries_key ON cache_entries(cache_key);
CREATE INDEX IF NOT EXISTS idx_cache_entries_expires ON cache_entries(expires_at);
CREATE INDEX IF NOT EXISTS idx_document_comparisons_docs ON document_comparisons(document1_id, document2_id);
CREATE INDEX IF NOT EXISTS idx_system_metrics_name_time ON system_metrics(metric_name, recorded_at);

-- Create function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert some initial system configuration
INSERT INTO system_metrics (metric_name, metric_value, metric_unit, metadata) VALUES
    ('system_version', 1.0, 'version', '{"description": "Initial system setup"}'),
    ('db_schema_version', 1.0, 'version', '{"description": "Database schema version"}')
ON CONFLICT DO NOTHING;

-- Grant permissions to the portal user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO portal_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO portal_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO portal_user;
