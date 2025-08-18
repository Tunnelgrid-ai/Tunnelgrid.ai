-- Fix the invalidate_metrics_cache function to handle tables without audit_id
-- The responses table doesn't have audit_id, so we need to get it from the related query

-- First, drop the existing triggers that depend on the function
DROP TRIGGER IF EXISTS trigger_invalidate_cache_responses ON responses;
DROP TRIGGER IF EXISTS trigger_invalidate_cache_brand_extractions ON brand_extractions;
DROP TRIGGER IF EXISTS trigger_invalidate_cache_queries ON queries;

-- Now drop and recreate the function
DROP FUNCTION IF EXISTS invalidate_metrics_cache();

CREATE OR REPLACE FUNCTION invalidate_metrics_cache()
RETURNS TRIGGER AS $$
DECLARE
    v_audit_id UUID;
BEGIN
    -- Handle different tables that might not have audit_id directly
    IF TG_TABLE_NAME = 'responses' THEN
        -- For responses table, get audit_id from the related query
        SELECT q.audit_id INTO v_audit_id
        FROM queries q
        WHERE q.query_id = COALESCE(NEW.query_id, OLD.query_id);
    ELSIF TG_TABLE_NAME = 'brand_extractions' THEN
        -- For brand_extractions table, get audit_id from the related query
        SELECT q.audit_id INTO v_audit_id
        FROM queries q
        WHERE q.query_id = COALESCE(NEW.query_id, OLD.query_id);
    ELSE
        -- For other tables (like queries), audit_id is directly available
        v_audit_id := COALESCE(NEW.audit_id, OLD.audit_id);
    END IF;
    
    -- Only invalidate if we found an audit_id
    IF v_audit_id IS NOT NULL THEN
        UPDATE comprehensive_metrics_cache 
        SET is_valid = FALSE, 
            last_calculation_error = 'Cache invalidated due to data changes'
        WHERE audit_id = v_audit_id;
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Recreate the triggers with the fixed function
CREATE TRIGGER trigger_invalidate_cache_responses
    AFTER INSERT OR UPDATE OR DELETE ON responses
    FOR EACH ROW
    EXECUTE FUNCTION invalidate_metrics_cache();

CREATE TRIGGER trigger_invalidate_cache_brand_extractions
    AFTER INSERT OR UPDATE OR DELETE ON brand_extractions
    FOR EACH ROW
    EXECUTE FUNCTION invalidate_metrics_cache();

CREATE TRIGGER trigger_invalidate_cache_queries
    AFTER INSERT OR UPDATE OR DELETE ON queries
    FOR EACH ROW
    EXECUTE FUNCTION invalidate_metrics_cache();
