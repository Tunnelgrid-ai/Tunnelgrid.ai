-- =============================================================================
-- PHASE 6: STUDY MANAGEMENT TABLES
-- =============================================================================
-- 
-- PURPOSE: Add comprehensive study management functionality
-- 
-- TABLES:
-- - user_studies: Main study records
-- - study_progress_snapshots: Progress tracking for each step
-- - study_shares: Study sharing and collaboration
-- - study_templates: Reusable study templates
-- 
-- FEATURES:
-- - Study creation and management
-- - Progress saving and restoration
-- - Study sharing with permissions
-- - Template system for quick start
-- - Statistics and analytics
-- =============================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- 1. USER STUDIES TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS user_studies (
    study_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    brand_id UUID NOT NULL,
    product_id UUID,
    study_name VARCHAR(255) NOT NULL,
    study_description TEXT,
    current_step VARCHAR(50) NOT NULL DEFAULT 'brand_info',
    progress_percentage INTEGER NOT NULL DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    status VARCHAR(50) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'in_progress', 'setup_completed', 'analysis_running', 'completed', 'failed')),
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    analysis_job_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_studies_user_id ON user_studies(user_id);
CREATE INDEX IF NOT EXISTS idx_user_studies_status ON user_studies(status);
CREATE INDEX IF NOT EXISTS idx_user_studies_created_at ON user_studies(created_at);
CREATE INDEX IF NOT EXISTS idx_user_studies_last_accessed ON user_studies(last_accessed_at);
CREATE INDEX IF NOT EXISTS idx_user_studies_brand_id ON user_studies(brand_id);
CREATE INDEX IF NOT EXISTS idx_user_studies_not_deleted ON user_studies(study_id) WHERE NOT is_deleted;

-- =============================================================================
-- 2. STUDY PROGRESS SNAPSHOTS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS study_progress_snapshots (
    snapshot_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    study_id UUID NOT NULL REFERENCES user_studies(study_id) ON DELETE CASCADE,
    step_name VARCHAR(50) NOT NULL,
    step_data JSONB NOT NULL DEFAULT '{}',
    progress_percentage INTEGER NOT NULL CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_study_progress_study_id ON study_progress_snapshots(study_id);
CREATE INDEX IF NOT EXISTS idx_study_progress_step_name ON study_progress_snapshots(step_name);
CREATE INDEX IF NOT EXISTS idx_study_progress_created_at ON study_progress_snapshots(created_at);

-- =============================================================================
-- 3. STUDY SHARES TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS study_shares (
    share_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    study_id UUID NOT NULL REFERENCES user_studies(study_id) ON DELETE CASCADE,
    shared_by UUID NOT NULL,
    shared_with_email VARCHAR(255) NOT NULL,
    permission_level VARCHAR(20) NOT NULL DEFAULT 'view' CHECK (permission_level IN ('view', 'edit', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    accepted_at TIMESTAMP WITH TIME ZONE,
    accepted_by UUID
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_study_shares_study_id ON study_shares(study_id);
CREATE INDEX IF NOT EXISTS idx_study_shares_shared_with_email ON study_shares(shared_with_email);
CREATE INDEX IF NOT EXISTS idx_study_shares_is_active ON study_shares(is_active);
CREATE INDEX IF NOT EXISTS idx_study_shares_expires_at ON study_shares(expires_at);

-- =============================================================================
-- 4. STUDY TEMPLATES TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS study_templates (
    template_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_name VARCHAR(255) NOT NULL,
    template_description TEXT,
    template_data JSONB NOT NULL DEFAULT '{}',
    created_by UUID,
    is_public BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_study_templates_created_by ON study_templates(created_by);
CREATE INDEX IF NOT EXISTS idx_study_templates_is_public ON study_templates(is_public);
CREATE INDEX IF NOT EXISTS idx_study_templates_usage_count ON study_templates(usage_count);

-- =============================================================================
-- 5. TRIGGERS AND FUNCTIONS
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to update last_accessed_at
CREATE OR REPLACE FUNCTION update_last_accessed_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_accessed_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to update completed_at when status changes to completed
CREATE OR REPLACE FUNCTION update_completed_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
        NEW.completed_at = NOW();
        NEW.is_completed = TRUE;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to increment usage count for templates
CREATE OR REPLACE FUNCTION increment_template_usage()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE study_templates 
    SET usage_count = usage_count + 1 
    WHERE template_id = NEW.template_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- =============================================================================
-- 6. APPLY TRIGGERS
-- =============================================================================

-- Update timestamps automatically
CREATE TRIGGER update_user_studies_updated_at 
    BEFORE UPDATE ON user_studies 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_studies_last_accessed 
    BEFORE UPDATE ON user_studies 
    FOR EACH ROW EXECUTE FUNCTION update_last_accessed_at();

CREATE TRIGGER update_user_studies_completed_at 
    BEFORE UPDATE ON user_studies 
    FOR EACH ROW EXECUTE FUNCTION update_completed_at();

CREATE TRIGGER update_study_progress_updated_at 
    BEFORE UPDATE ON study_progress_snapshots 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_study_templates_updated_at 
    BEFORE UPDATE ON study_templates 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Increment template usage when study is created from template
CREATE TRIGGER increment_template_usage_trigger 
    AFTER INSERT ON user_studies 
    FOR EACH ROW EXECUTE FUNCTION increment_template_usage();

-- =============================================================================
-- 7. SAMPLE DATA (OPTIONAL)
-- =============================================================================

-- Insert a sample public template
INSERT INTO study_templates (
    template_name, 
    template_description, 
    template_data, 
    is_public
) VALUES (
    'Basic Brand Analysis',
    'A comprehensive brand analysis template covering all essential aspects',
    '{
        "steps": ["brand_info", "personas", "products", "topics", "questions", "review"],
        "default_settings": {
            "brand_info": {"required_fields": ["name", "description"]},
            "personas": {"min_count": 3, "max_count": 5},
            "topics": {"min_count": 5, "max_count": 10},
            "questions": {"min_count": 10, "max_count": 20}
        }
    }',
    TRUE
) ON CONFLICT DO NOTHING;

-- =============================================================================
-- 8. COMMENTS
-- =============================================================================

COMMENT ON TABLE user_studies IS 'Main table for user study management';
COMMENT ON TABLE study_progress_snapshots IS 'Progress tracking for each study step';
COMMENT ON TABLE study_shares IS 'Study sharing and collaboration features';
COMMENT ON TABLE study_templates IS 'Reusable study templates for quick start';

COMMENT ON COLUMN user_studies.study_id IS 'Unique identifier for the study';
COMMENT ON COLUMN user_studies.user_id IS 'User who created the study';
COMMENT ON COLUMN user_studies.brand_id IS 'Associated brand for the study';
COMMENT ON COLUMN user_studies.current_step IS 'Current step in the study workflow';
COMMENT ON COLUMN user_studies.progress_percentage IS 'Overall progress percentage (0-100)';
COMMENT ON COLUMN user_studies.status IS 'Current status of the study';
COMMENT ON COLUMN user_studies.analysis_job_id IS 'Reference to analysis job if analysis is running';

-- =============================================================================
-- MIGRATION COMPLETE
-- =============================================================================

-- Verify tables were created successfully
SELECT 
    table_name, 
    column_count,
    index_count
FROM (
    SELECT 
        'user_studies' as table_name,
        COUNT(*) as column_count,
        (SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'user_studies') as index_count
    FROM information_schema.columns 
    WHERE table_name = 'user_studies'
    UNION ALL
    SELECT 
        'study_progress_snapshots' as table_name,
        COUNT(*) as column_count,
        (SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'study_progress_snapshots') as index_count
    FROM information_schema.columns 
    WHERE table_name = 'study_progress_snapshots'
    UNION ALL
    SELECT 
        'study_shares' as table_name,
        COUNT(*) as column_count,
        (SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'study_shares') as index_count
    FROM information_schema.columns 
    WHERE table_name = 'study_shares'
    UNION ALL
    SELECT 
        'study_templates' as table_name,
        COUNT(*) as column_count,
        (SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'study_templates') as index_count
    FROM information_schema.columns 
    WHERE table_name = 'study_templates'
) as table_info
ORDER BY table_name; 