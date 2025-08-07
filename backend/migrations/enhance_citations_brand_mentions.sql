-- =============================================================================
-- MIGRATION: Enhance Citations and Brand Mentions Tables
-- PURPOSE: Add additional fields for OpenAI Responses API integration
-- DATE: 2024-01-XX
-- =============================================================================

-- Add new columns to citations table for enhanced citation tracking
ALTER TABLE citations 
ADD COLUMN source_title TEXT,
ADD COLUMN start_index INTEGER,
ADD COLUMN end_index INTEGER;

-- Add constraints for new citation fields
ALTER TABLE citations 
ADD CONSTRAINT valid_start_index CHECK (start_index IS NULL OR start_index >= 0),
ADD CONSTRAINT valid_end_index CHECK (end_index IS NULL OR end_index >= 0),
ADD CONSTRAINT valid_index_range CHECK (
    start_index IS NULL OR end_index IS NULL OR start_index <= end_index
);

-- Add new columns to brand_mentions table for source attribution
ALTER TABLE brand_mentions 
ADD COLUMN sentiment VARCHAR(20) DEFAULT 'neutral',
ADD COLUMN source_url TEXT,
ADD COLUMN source_title TEXT;

-- Add constraints for new brand mention fields
ALTER TABLE brand_mentions 
ADD CONSTRAINT valid_sentiment CHECK (sentiment IN ('positive', 'negative', 'neutral')),
ADD CONSTRAINT valid_brand_source_url CHECK (
    source_url IS NULL OR 
    source_url ~ '^https?://[^\s<>"{}|\\^`[\]]+(\.[^\s<>"{}|\\^`[\]]+)*$'
);

-- Create indexes for new fields
CREATE INDEX idx_citations_source_title ON citations(source_title);
CREATE INDEX idx_citations_start_index ON citations(start_index);
CREATE INDEX idx_citations_end_index ON citations(end_index);

CREATE INDEX idx_brand_mentions_sentiment_type ON brand_mentions(sentiment);
CREATE INDEX idx_brand_mentions_source_url ON brand_mentions(source_url);
CREATE INDEX idx_brand_mentions_source_title ON brand_mentions(source_title);

-- Composite indexes for common queries
CREATE INDEX idx_citations_response_source ON citations(response_id, source_url);
CREATE INDEX idx_brand_mentions_brand_sentiment_type ON brand_mentions(brand_name, sentiment);
CREATE INDEX idx_brand_mentions_brand_source ON brand_mentions(brand_name, source_url);

-- Add comments for documentation
COMMENT ON COLUMN citations.source_title IS 'Title of the source page/article from web search';
COMMENT ON COLUMN citations.start_index IS 'Start position of citation in response text';
COMMENT ON COLUMN citations.end_index IS 'End position of citation in response text';

COMMENT ON COLUMN brand_mentions.sentiment IS 'Sentiment classification (positive/negative/neutral)';
COMMENT ON COLUMN brand_mentions.source_url IS 'Source URL where this brand mention was found';
COMMENT ON COLUMN brand_mentions.source_title IS 'Title of the source where brand mention was found';

-- =============================================================================
-- UPDATE EXISTING DATA (if any)
-- =============================================================================

-- Update existing brand mentions to have default sentiment
UPDATE brand_mentions 
SET sentiment = 'neutral' 
WHERE sentiment IS NULL;

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================

-- Verify the new structure
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'citations' 
ORDER BY ordinal_position;

SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'brand_mentions' 
ORDER BY ordinal_position; 