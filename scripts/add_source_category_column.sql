-- Add source_category column to brand_extractions table
-- This categorizes the source of each brand mention based on website analysis

ALTER TABLE brand_extractions 
ADD COLUMN source_category VARCHAR(50);

-- Add index for better performance on source_category queries
CREATE INDEX idx_brand_extractions_source_category ON brand_extractions(source_category);

-- Update existing records to have default category (optional)
UPDATE brand_extractions 
SET source_category = 'Unsure/Other' 
WHERE source_category IS NULL;

-- Create enum constraint for valid source categories
ALTER TABLE brand_extractions 
ADD CONSTRAINT chk_source_category 
CHECK (source_category IN (
    'Business/Service Sites',
    'Unsure/Other',
    'Blogs/Content Sites',
    'Educational Sites',
    'Government/Institutional',
    'News/Media Sites',
    'E-commerce Sites',
    'Directory/Review Sites',
    'Forums/Community Sites',
    'Search Engine'
));

-- Add comment explaining the column
COMMENT ON COLUMN brand_extractions.source_category IS 'Categorizes the source website type based on content and domain analysis';
