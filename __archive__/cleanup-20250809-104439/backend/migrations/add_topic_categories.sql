-- =============================================================================
-- TOPICS CATEGORIZATION MIGRATION
-- =============================================================================
-- Purpose: Add topic categorization support to the topics table
-- Categories: unbranded, branded, comparative
-- Distribution: 4 unbranded, 3 branded, 3 comparative topics per audit
-- =============================================================================

-- Step 1: Add the topic_category column with constraint
ALTER TABLE topics 
ADD COLUMN topic_category VARCHAR(20) 
CHECK (topic_category IN ('unbranded', 'branded', 'comparative'));

-- Step 2: Update existing topics with default category
-- Note: You may want to manually categorize existing topics or regenerate them
UPDATE topics 
SET topic_category = 'unbranded' 
WHERE topic_category IS NULL;

-- Step 3: Make the column NOT NULL after setting defaults
ALTER TABLE topics 
ALTER COLUMN topic_category SET NOT NULL;

-- Step 4: Add index for better query performance
CREATE INDEX idx_topics_category ON topics(topic_category);
CREATE INDEX idx_topics_audit_category ON topics(audit_id, topic_category);

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================

-- Check that all topics now have categories
SELECT 
  topic_category,
  COUNT(*) as count
FROM topics 
GROUP BY topic_category
ORDER BY topic_category;

-- Check category distribution per audit
SELECT 
  audit_id,
  topic_category,
  COUNT(*) as count
FROM topics 
GROUP BY audit_id, topic_category
ORDER BY audit_id, topic_category;

-- =============================================================================
-- ROLLBACK SCRIPT (if needed)
-- =============================================================================
/*
-- To rollback this migration, run:
DROP INDEX IF EXISTS idx_topics_category;
DROP INDEX IF EXISTS idx_topics_audit_category;
ALTER TABLE topics DROP COLUMN IF EXISTS topic_category;
*/ 