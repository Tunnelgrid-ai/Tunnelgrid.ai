"""
ANALYSIS API ROUTES - AI-POWERED BRAND ANALYSIS

PURPOSE: Provides secure server-side API for AI brand analysis processing

SECURITY BENEFITS:
- API keys stored securely on server-side only  
- Rate limiting and usage monitoring
- Proper error handling and logging
- Input validation and sanitization

ENDPOINTS:
- POST /start - Start brand analysis job for an audit
- GET /status/{job_id} - Get analysis job status and progress
- GET /results/{audit_id} - Get analysis results for an audit

ARCHITECTURE:
Frontend → FastAPI Backend → OpenAI → Backend → Frontend
"""

import asyncio
import uuid
import time
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, BackgroundTasks, Path
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..core.database import get_supabase_client
from ..core.config import settings
from ..core.performance_config import PerformanceConfig
from ..models.analysis import (
    AnalysisJobRequest,
    AnalysisJobResponse, 
    AnalysisJobStatusResponse,
    AnalysisJobStatus,
    AIAnalysisRequest,
    AnalysisResults,
    LLMServiceType
)
from ..services.ai_analysis import openai_service

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

# Add UUID validation helper function
def validate_uuid(uuid_string: str, field_name: str) -> str:
    """Validate UUID format and return normalized UUID string"""
    try:
        # This will raise ValueError if invalid UUID format
        uuid_obj = uuid.UUID(uuid_string)
        return str(uuid_obj)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name} format. Must be a valid UUID."
        )

@router.post("/start", response_model=AnalysisJobResponse)
async def start_analysis(request: AnalysisJobRequest, background_tasks: BackgroundTasks):
    """
    Start AI brand analysis for an audit
    
    This endpoint:
    1. Validates the audit exists and has queries
    2. Creates an analysis job record
    3. Starts background processing of all queries
    4. Returns job ID for progress tracking
    """
    try:
        logger.info(f"🚀 Starting analysis for audit: {request.audit_id}")
        
        # Validate UUID format
        validated_audit_id = validate_uuid(request.audit_id, "audit_id")
        
        # Verify audit exists and get audit details
        supabase = get_supabase_client()
        audit_result = supabase.table("audit").select("*").eq("audit_id", validated_audit_id).execute()
        
        if not audit_result.data:
            raise HTTPException(status_code=404, detail="Audit not found")
        
        audit = audit_result.data[0]
        
        # Check if analysis job already exists for this audit
        existing_job = supabase.table("analysis_jobs").select("*").eq("audit_id", validated_audit_id).execute()
        
        if existing_job.data:
            job = existing_job.data[0]
            if job['status'] in ['pending', 'running']:
                return AnalysisJobResponse(
                    success=True,
                    job_id=job['job_id'],
                    message="Analysis job already in progress",
                    total_queries=job['total_queries']
                )
            elif job['status'] == 'completed':
                return AnalysisJobResponse(
                    success=True,
                    job_id=job['job_id'],
                    message="Analysis already completed",
                    total_queries=job['total_queries']
                )
        
        # Validate OpenAI configuration
        if not settings.has_openai_config:
            raise HTTPException(
                status_code=503, 
                detail="OpenAI API is not configured. Please check OPENAI_API_KEY environment variable."
            )
        
        # Get all queries for the audit
        queries_result = supabase.table("queries").select("*").eq("audit_id", validated_audit_id).execute()
        
        if not queries_result.data:
            raise HTTPException(
                status_code=404, 
                detail=f"No queries found for audit {validated_audit_id}. Please generate questions first."
            )
        
        # Get persona details for context
        personas_result = supabase.table("personas").select("*").eq("audit_id", validated_audit_id).execute()
        personas_map = {p["persona_id"]: p for p in personas_result.data}
        
        if not personas_map:
            raise HTTPException(
                status_code=404, 
                detail=f"No personas found for audit {validated_audit_id}. Please generate personas first."
            )
        
        # Create analysis job record
        job_id = str(uuid.uuid4())
        job_data = {
            "job_id": job_id,
            "audit_id": validated_audit_id,
            "status": AnalysisJobStatus.PENDING.value,
            "total_queries": len(queries_result.data),
            "completed_queries": 0,
            "failed_queries": 0,
            "created_at": datetime.utcnow().isoformat()
        }
        
        job_result = supabase.table("analysis_jobs").insert(job_data).execute()
        
        if hasattr(job_result, 'error') and job_result.error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create analysis job: {job_result.error}"
            )
        
        logger.info(f"✅ Created analysis job {job_id} with {len(queries_result.data)} queries")
        
        # Update audit status to analysis_running
        try:
            supabase.table("audit").update({
                "status": "analysis_running"
            }).eq("audit_id", validated_audit_id).execute()
            logger.info(f"🔄 Updated audit {validated_audit_id} status to 'analysis_running'")
        except Exception as status_error:
            logger.warning(f"⚠️ Failed to update audit status to 'analysis_running': {status_error}")
        
        # Start background processing
        background_tasks.add_task(
            process_analysis_job,
            job_id,
            validated_audit_id, 
            queries_result.data,
            personas_map
        )
        
        return AnalysisJobResponse(
            success=True,
            job_id=job_id,
            message=f"Analysis started for {len(queries_result.data)} queries",
            total_queries=len(queries_result.data),
            estimated_completion_time=None  # Could calculate based on query count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error starting analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")

@router.get("/status/{job_id}", response_model=AnalysisJobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the current status of an analysis job
    """
    try:
        logger.info(f"📊 Getting status for job: {job_id}")
        
        # Validate UUID format
        validated_job_id = validate_uuid(job_id, "job_id")
        
        supabase = get_supabase_client()
        
        # Get job status from database
        result = supabase.table("analysis_jobs").select("*").eq("job_id", validated_job_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Analysis job not found")
        
        job = result.data[0]
        
        # Calculate progress percentage
        progress_percentage = 0.0
        if job['total_queries'] > 0:
            progress_percentage = (job['completed_queries'] / job['total_queries']) * 100
        
        return AnalysisJobStatusResponse(
            job_id=job['job_id'],
            audit_id=job['audit_id'],
            status=job['status'],
            total_queries=job['total_queries'],
            completed_queries=job['completed_queries'],
            failed_queries=job['failed_queries'],
            progress_percentage=progress_percentage,
            created_at=job['created_at'],
            completed_at=job.get('completed_at'),
            error_message=job.get('error_message')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting job status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")

@router.get("/results/{audit_id}", response_model=AnalysisResults)
async def get_analysis_results(audit_id: str):
    """
    Get comprehensive analysis results for a completed audit
    """
    try:
        logger.info(f"📋 Getting analysis results for audit: {audit_id}")
        
        # Validate UUID format
        validated_audit_id = validate_uuid(audit_id, "audit_id")
        
        supabase = get_supabase_client()
        
        # Get analysis job info
        job_result = supabase.table("analysis_jobs").select("*").eq("audit_id", validated_audit_id).execute()
        
        if not job_result.data:
            raise HTTPException(status_code=404, detail="Analysis results not found")
        
        job = job_result.data[0]
        
        if job["status"] not in [AnalysisJobStatus.COMPLETED.value, AnalysisJobStatus.PARTIAL_FAILURE.value]:
            raise HTTPException(
                status_code=400, 
                detail=f"Analysis not completed. Current status: {job['status']}"
            )
        
        # Get all responses for this audit (first get queries, then join responses)
        queries_result = supabase.table("queries").select("*").eq("audit_id", validated_audit_id).execute()
        
        if not queries_result.data:
            raise HTTPException(status_code=404, detail="No queries found for this audit")
        
        query_ids = [q["query_id"] for q in queries_result.data]
        responses_result = supabase.table("responses").select("*").in_("query_id", query_ids).execute()
        
        # Get personas and topics for brand reach analysis
        personas_result = supabase.table("personas").select("*").eq("audit_id", validated_audit_id).execute()
        topics_result = supabase.table("topics").select("*").eq("audit_id", validated_audit_id).execute()
        
        # Get brand extractions (NEW approach - replaces citations and brand_mentions)
        response_ids = [r["response_id"] for r in responses_result.data]
        brand_extractions_result = supabase.table("brand_extractions").select("*").in_("response_id", response_ids).execute()
        
        # Keep citations for backwards compatibility (but it might be empty)
        try:
            citations_result = supabase.table("citations").select("*").in_("response_id", response_ids).execute()
        except:
            citations_result = type('obj', (object,), {'data': []})()  # Empty fallback if table doesn't exist
        
        # Organize results with new brand_extractions data
        results = {
            "job_status": job,
            "total_responses": len(responses_result.data),
            "total_citations": len(citations_result.data),
            "total_brand_mentions": len(brand_extractions_result.data),  # Use brand_extractions count
            "responses": responses_result.data,
            "citations": citations_result.data,  # Keep for compatibility
            "brand_mentions": brand_extractions_result.data,  # NEW: Use brand_extractions as brand mentions
            "brand_extractions": brand_extractions_result.data,  # NEW: Include raw brand extractions
            "personas": personas_result.data,
            "topics": topics_result.data,
            "queries": queries_result.data
        }
        logger.info(f"📋 Retrieved results for audit {validated_audit_id}: {len(responses_result.data)} responses")
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")

@router.get("/comprehensive-report/{audit_id}")
async def get_comprehensive_report(audit_id: str):
    """
    Get comprehensive report metrics for a completed audit
    
    This endpoint uses pre-calculated metrics from the cache table for optimal performance.
    If cache is invalid or missing, it will trigger a recalculation.
    """
    try:
        logger.info(f"📊 Getting comprehensive report for audit: {audit_id}")
        
        # Validate UUID format
        validated_audit_id = validate_uuid(audit_id, "audit_id")
        
        supabase = get_supabase_client()
        
        # Step 1: Check if audit exists and analysis is completed
        audit_result = supabase.table("audit").select("*").eq("audit_id", validated_audit_id).execute()
        if not audit_result.data:
            raise HTTPException(status_code=404, detail="Audit not found")
        
        audit = audit_result.data[0]
        
        # Check if analysis is completed
        job_result = supabase.table("analysis_jobs").select("*").eq("audit_id", validated_audit_id).execute()
        if not job_result.data:
            raise HTTPException(status_code=404, detail="Analysis job not found")
        
        job = job_result.data[0]
        if job["status"] not in [AnalysisJobStatus.COMPLETED.value, AnalysisJobStatus.PARTIAL_FAILURE.value]:
            raise HTTPException(
                status_code=400, 
                detail=f"Analysis not completed. Current status: {job['status']}"
            )
        
        # Step 2: Check cache for pre-calculated metrics
        cache_result = supabase.table("comprehensive_metrics_cache").select("*").eq("audit_id", validated_audit_id).execute()
        
        cache_data = None
        if cache_result.data:
            cache_data = cache_result.data[0]
            logger.info(f"📋 Found cached metrics for audit {validated_audit_id}")
        
        # Step 3: If cache is invalid or missing, trigger recalculation
        if not cache_data or not cache_data.get("is_valid", False):
            logger.info(f"🔄 Cache invalid or missing, triggering recalculation for audit {validated_audit_id}")
            
            try:
                # Call the PostgreSQL function to calculate and cache metrics
                recalculation_result = supabase.rpc(
                    "calculate_comprehensive_metrics", 
                    {"p_audit_id": validated_audit_id}
                ).execute()
                
                # Fetch the updated cache
                cache_result = supabase.table("comprehensive_metrics_cache").select("*").eq("audit_id", validated_audit_id).execute()
                if cache_result.data:
                    cache_data = cache_result.data[0]
                    logger.info(f"✅ Metrics recalculated and cached for audit {validated_audit_id}")
                else:
                    raise Exception("Failed to retrieve recalculated metrics")
                    
            except Exception as calc_error:
                logger.error(f"❌ Failed to recalculate metrics: {calc_error}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to calculate comprehensive metrics: {str(calc_error)}"
                )
        
        # Step 4: Get brand information for the report
        brand_result = supabase.table("brand").select("*").eq("brand_id", audit["brand_id"]).execute()
        brand = brand_result.data[0] if brand_result.data else {}
        
        # Step 5: Compile comprehensive report from cached data
        comprehensive_report = {
            "audit_info": {
                "audit_id": validated_audit_id,
                "brand_name": brand.get("brand_name", "Unknown"),
                "brand_domain": brand.get("domain"),
                "total_queries": cache_data["total_queries"],
                "total_responses": cache_data["total_responses"],
                "analysis_date": cache_data["analysis_completed_at"]
            },
            "brand_visibility": {
                "overall_percentage": float(cache_data["overall_visibility_percentage"]),
                "total_brand_mentions": cache_data["target_brand_mentions"],
                "sentiment_distribution": cache_data["sentiment_distribution"],
                "platform_rankings": cache_data["platform_rankings"]
            },
            "competitor_analysis": {
                "total_competitors": len(cache_data["competitor_analysis"]),
                "competitor_brands": cache_data["competitor_analysis"]
            },
            "brand_reach": {
                "persona_visibility": cache_data["persona_visibility"],
                "topic_visibility": cache_data["topic_visibility"],
                "persona_topic_matrix": cache_data["persona_topic_matrix"]
            },
            "model_performance": cache_data["model_performance"],
            "strategic_insights": {
                "opportunity_gaps": cache_data["opportunity_gaps"],
                "content_strategy": cache_data["content_strategy"],
                "competitive_insights": cache_data["competitive_insights"]
            },
            "cache_info": {
                "cache_id": cache_data["cache_id"],
                "cache_version": cache_data["cache_version"],
                "created_at": cache_data["created_at"],
                "updated_at": cache_data["updated_at"],
                "is_valid": cache_data["is_valid"]
            }
        }
        
        logger.info(f"✅ Comprehensive report generated from cache for audit {validated_audit_id}")
        logger.info(f"📊 Metrics: {cache_data['overall_visibility_percentage']}% visibility, {len(cache_data['competitor_analysis'])} competitors")
        
        return comprehensive_report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating comprehensive report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate comprehensive report: {str(e)}")

@router.post("/comprehensive-report/{audit_id}/recalculate")
async def recalculate_comprehensive_report(audit_id: str):
    """
    Force recalculation of comprehensive report metrics
    
    This endpoint manually triggers recalculation of cached metrics.
    Useful when you want to refresh the cache without waiting for data changes.
    """
    try:
        logger.info(f"🔄 Force recalculating comprehensive report for audit: {audit_id}")
        
        # Validate UUID format
        validated_audit_id = validate_uuid(audit_id, "audit_id")
        
        supabase = get_supabase_client()
        
        # Check if audit exists
        audit_result = supabase.table("audit").select("*").eq("audit_id", validated_audit_id).execute()
        if not audit_result.data:
            raise HTTPException(status_code=404, detail="Audit not found")
        
        # Trigger recalculation
        try:
            recalculation_result = supabase.rpc(
                "calculate_comprehensive_metrics", 
                {"p_audit_id": validated_audit_id}
            ).execute()
            
            logger.info(f"✅ Metrics recalculated for audit {validated_audit_id}")
            
            return {
                "success": True,
                "message": "Comprehensive metrics recalculated successfully",
                "audit_id": validated_audit_id
            }
            
        except Exception as calc_error:
            logger.error(f"❌ Failed to recalculate metrics: {calc_error}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to recalculate comprehensive metrics: {str(calc_error)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error recalculating comprehensive report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to recalculate comprehensive report: {str(e)}")

async def process_analysis_job(
    job_id: str, 
    audit_id: str, 
    queries: List[Dict], 
    personas_map: Dict
):
    """
    Background task to process all AI analysis requests
    
    This function:
    1. Updates job status to 'running'
    2. Processes queries in batches to avoid overwhelming APIs
    3. Stores responses, citations, and brand mentions
    4. Updates progress in real-time
    5. Handles errors gracefully
    """
    logger.info(f"🔄 Starting background processing for job {job_id}")
    
    supabase = get_supabase_client()
    
    try:
        # Update job status to running
        supabase.table("analysis_jobs").update({
            "status": AnalysisJobStatus.RUNNING.value
        }).eq("job_id", job_id).execute()
        
        completed = 0
        failed = 0
        
        # Process queries in batches to avoid overwhelming APIs
        batch_size = PerformanceConfig.get_optimal_batch_size(len(queries))
        logger.info(f"📊 Using batch size: {batch_size} for {len(queries)} queries")
        
        for i in range(0, len(queries), batch_size):
            batch = queries[i:i + batch_size]
            
            logger.info(f"🔄 Processing batch {i//batch_size + 1}/{(len(queries) + batch_size - 1)//batch_size}")
            
            # Create tasks for concurrent processing within batch
            tasks = []
            for query in batch:
                persona = personas_map.get(query["persona"])
                if not persona:
                    logger.warning(f"⚠️ Persona {query['persona']} not found for query {query['query_id']}")
                    failed += 1
                    continue
                
                # Create analysis request
                analysis_request = AIAnalysisRequest(
                    query_id=query["query_id"],
                    audit_id=audit_id,  # NEW: Pass audit_id to the request
                    persona_description=persona["persona_description"],
                    question_text=query["query_text"],
                    model="gpt-4o",
                    service=LLMServiceType.OPENAI
                )
                
                # Add to batch processing
                tasks.append(process_single_query(analysis_request, supabase))
            
            # Process batch concurrently
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Count results and log details
                for result in results:
                    if isinstance(result, Exception):
                        failed += 1
                        logger.error(f"❌ Query processing failed: {result}")
                    else:
                        completed += 1
                        logger.debug(f"✅ Query processed successfully")
            
            # Update progress in database
            supabase.table("analysis_jobs").update({
                "completed_queries": completed,
                "failed_queries": failed
            }).eq("job_id", job_id).execute()
            
            logger.info(f"📊 Progress: {completed}/{len(queries)} completed, {failed} failed")
            
            # Rate limiting delay between batches (reduced for faster processing)
            if i + batch_size < len(queries):  # Don't delay after last batch
                batch_number = (i // batch_size) + 1
                total_batches = (len(queries) + batch_size - 1) // batch_size
                delay = PerformanceConfig.get_batch_delay(batch_number, total_batches)
                logger.info(f"⏳ Rate limiting delay: {delay}s (batch {batch_number}/{total_batches})")
                await asyncio.sleep(delay)
        
        # Determine final status
        if failed == 0:
            final_status = AnalysisJobStatus.COMPLETED.value
            logger.info(f"✅ Job {job_id} completed successfully")
            
            # Mark audit as completed since analysis finished successfully
            try:
                logger.info(f"🎉 Marking audit {audit_id} as completed after successful analysis")
                supabase.table("audit").update({
                    "status": "completed"
                }).eq("audit_id", audit_id).execute()
                logger.info(f"✅ Audit {audit_id} marked as completed")
            except Exception as audit_error:
                logger.error(f"❌ Failed to mark audit {audit_id} as completed: {audit_error}")
                
        elif completed > 0:
            final_status = AnalysisJobStatus.PARTIAL_FAILURE.value
            logger.warning(f"⚠️ Job {job_id} completed with {failed} failures")
        else:
            final_status = AnalysisJobStatus.FAILED.value
            logger.error(f"❌ Job {job_id} failed completely")
        
        # Mark job as completed
        supabase.table("analysis_jobs").update({
            "status": final_status,
            "completed_at": datetime.utcnow().isoformat(),
            "error_message": f"{failed} queries failed" if failed > 0 else None
        }).eq("job_id", job_id).execute()
        
        # Step 7: Calculate comprehensive metrics if analysis completed successfully
        if final_status == AnalysisJobStatus.COMPLETED.value:
            try:
                logger.info(f"📊 Calculating comprehensive metrics for audit {audit_id}")
                supabase.rpc("calculate_comprehensive_metrics", {"p_audit_id": audit_id}).execute()
                logger.info(f"✅ Comprehensive metrics calculated and cached for audit {audit_id}")
            except Exception as metrics_error:
                logger.warning(f"⚠️ Failed to calculate comprehensive metrics: {metrics_error}")
                # Don't fail the entire job if metrics calculation fails
        
        logger.info(f"🏁 Job {job_id} finished: {completed} completed, {failed} failed")
        
    except Exception as e:
        logger.error(f"💥 Critical error in job {job_id}: {e}")
        
        # Mark job as failed
        supabase.table("analysis_jobs").update({
            "status": AnalysisJobStatus.FAILED.value,
            "completed_at": datetime.utcnow().isoformat(),
            "error_message": str(e)
        }).eq("job_id", job_id).execute()

async def process_single_query(request: AIAnalysisRequest, supabase) -> bool:
    """
    Process a single query through two-stage AI analysis and store all results
    """
    try:
        logger.debug(f"🔍 Processing query {request.query_id}")
        
        # Get audit brand name and brand_id for brand extraction
        audit_brand_name = None
        brand_id = None
        try:
            # Get brand name from audit table
            audit_query = supabase.table("audit").select("brand_id").eq("audit_id", request.audit_id).execute()
            if audit_query.data:
                brand_id = audit_query.data[0]["brand_id"] 
                brand_query = supabase.table("brand").select("brand_name").eq("brand_id", brand_id).execute()
                if brand_query.data:
                    audit_brand_name = brand_query.data[0]["brand_name"]
                    logger.info(f"🎯 Target brand for analysis: {audit_brand_name}")
                else:
                    logger.warning(f"⚠️ No brand found for brand_id: {brand_id}")
            else:
                logger.warning(f"⚠️ No audit found for audit_id: {request.audit_id}")
        except Exception as e:
            logger.warning(f"⚠️ Could not retrieve audit brand name: {str(e)}")
        
        # Two-stage AI analysis 
        analysis_result = await openai_service.analyze_brand_perception(request, audit_brand_name)
        
        # Store response in database
        response_data = {
            "response_id": str(uuid.uuid4()),
            "query_id": request.query_id,
            "model": request.model,
            "response_text": analysis_result.response_text
        }
        
        response_result = supabase.table("responses").insert(response_data).execute()
        
        if hasattr(response_result, 'error') and response_result.error:
            raise Exception(f"Failed to store response: {response_result.error}")
        
        response_id = response_result.data[0]["response_id"]
        
        # Citations are now handled through brand_extractions with source information
        # No need for separate citations table since we extract source info with brands
        # Store brand extractions (NEW)
        if analysis_result.brand_extractions:
            brand_extractions_data = []
            for extraction in analysis_result.brand_extractions:
                brand_extractions_data.append({
                    "extraction_id": str(uuid.uuid4()),
                    "response_id": response_id,
                    "query_id": request.query_id,
                    "brand_id": brand_id if extraction.is_target_brand else None,
                    "is_target_brand": extraction.is_target_brand,
                    "source_domain": extraction.source_domain,
                    "source_url": extraction.source_url,
                    "article_title": extraction.article_title,
                    "extracted_brand_name": extraction.extracted_brand_name,
                    "context_snippet": extraction.context_snippet,
                    "mention_position": extraction.mention_position,
                    "sentiment_label": extraction.sentiment_label,
                    "source_category": extraction.source_category
                })
            
            try:
                supabase.table("brand_extractions").insert(brand_extractions_data).execute()
                logger.info(f"✅ Stored {len(brand_extractions_data)} brand extractions for query {request.query_id}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to store brand extractions: {str(e)}")
                # This makes it a partial failure since extraction data is critical
                raise Exception(f"Brand extraction storage failed: {str(e)}")
        
        # Check for extraction errors (log but don't fail the whole process)
        if analysis_result.extraction_error:
            logger.warning(f"⚠️ Brand extraction failed for query {request.query_id}: {analysis_result.extraction_error}")
            # Don't raise exception - let the main analysis succeed even if brand extraction fails
        
        logger.info(f"✅ Successfully processed query {request.query_id} with {len(analysis_result.brand_extractions)} brand extractions")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to process query {request.query_id}: {str(e)}")
        raise 