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
from typing import List, Dict, Optional
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
        print(f"🔍 ENTERING get_analysis_results for audit: {audit_id}")
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
        
        # Get citations
        response_ids = [r["response_id"] for r in responses_result.data]
        citations_result = supabase.table("citations").select("*").in_("response_id", response_ids).execute()
        
        # Get brand mentions
        mentions_result = supabase.table("brand_mentions").select("*").in_("response_id", response_ids).execute()
        
        # Get competitors data
        print(f"🔍 Fetching competitors for audit: {validated_audit_id}")
        logger.info(f"🔍 Fetching competitors for audit: {validated_audit_id}")
        competitors_result = supabase.table("competitors").select("*").eq("audit_id", validated_audit_id).order("mention_count", desc=True).execute()
        print(f"🏆 Found {len(competitors_result.data)} competitors for audit {validated_audit_id}")
        logger.info(f"🏆 Found {len(competitors_result.data)} competitors for audit {validated_audit_id}")
        
        # Organize results
        results = {
            "job_status": job,
            "total_responses": len(responses_result.data),
            "total_citations": len(citations_result.data),
            "total_brand_mentions": len(mentions_result.data),
            "responses": responses_result.data,
            "citations": citations_result.data,
            "brand_mentions": mentions_result.data,
            "competitors": competitors_result.data,
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
    4. Aggregates brand mentions and competitors across all queries
    5. Updates progress in real-time
    6. Handles errors gracefully
    """
    logger.info(f"🔄 Starting background processing for job {job_id}")
    
    supabase = get_supabase_client()
    
    try:
        # Get brand name from audit for competitor identification
        # First get brand_id from audit, then get brand_name from brand table
        audit_result = supabase.table("audit").select("brand_id").eq("audit_id", audit_id).execute()
        brand_name = None
        if audit_result.data and audit_result.data[0].get("brand_id"):
            brand_id = audit_result.data[0]["brand_id"]
            brand_result = supabase.table("brand").select("brand_name").eq("brand_id", brand_id).execute()
            if brand_result.data:
                brand_name = brand_result.data[0].get("brand_name")
                logger.info(f"🏷️ Brand name for competitor identification: {brand_name}")
            else:
                logger.warning(f"⚠️ No brand found for brand_id: {brand_id}")
        else:
            logger.warning(f"⚠️ No brand_id found for audit: {audit_id}")
        
        # Update job status to running
        supabase.table("analysis_jobs").update({
            "status": AnalysisJobStatus.RUNNING.value
        }).eq("job_id", job_id).execute()
        
        completed = 0
        failed = 0
        
        # Dictionary to aggregate brand mentions across all queries
        brand_mentions_aggregated = {}  # brand_name -> count
        
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
                    persona_description=persona["persona_description"],
                    question_text=query["query_text"],
                    model="openai-4o",
                    service=LLMServiceType.OPENAI,
                    brand_name=brand_name
                )
                
                # Add to batch processing
                tasks.append(process_single_query_with_aggregation(analysis_request, supabase, audit_id, brand_mentions_aggregated))
            
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
        
        # Aggregate and store all brand mentions (including primary brand and competitors)
        if brand_mentions_aggregated:
            logger.info(f"📊 Aggregating {len(brand_mentions_aggregated)} unique brands across all queries")
            
            # Clear existing competitors for this audit
            try:
                supabase.table("competitors").delete().eq("audit_id", audit_id).execute()
                logger.info(f"🗑️ Cleared existing competitors for audit {audit_id}")
            except Exception as clear_error:
                logger.warning(f"⚠️ Failed to clear existing competitors: {clear_error}")
            
            # Store aggregated brand mentions
            competitors_data = []
            for brand_name, mention_count in brand_mentions_aggregated.items():
                competitors_data.append({
                    "competitor_id": str(uuid.uuid4()),
                    "audit_id": audit_id,
                    "brand_name": brand_name,
                    "mention_count": mention_count
                })
            
            if competitors_data:
                try:
                    competitors_result = supabase.table("competitors").insert(competitors_data).execute()
                    if hasattr(competitors_result, 'error') and competitors_result.error:
                        logger.error(f"❌ Failed to store aggregated competitors: {competitors_result.error}")
                    else:
                        logger.info(f"✅ Successfully stored {len(competitors_data)} aggregated brand mentions")
                        logger.info(f"📊 Brand mention counts: {brand_mentions_aggregated}")
                except Exception as store_error:
                    logger.error(f"❌ Error storing aggregated competitors: {store_error}")
        
        logger.info(f"🏁 Job {job_id} finished: {completed} completed, {failed} failed")
        
    except Exception as e:
        logger.error(f"💥 Critical error in job {job_id}: {e}")
        
        # Mark job as failed
        supabase.table("analysis_jobs").update({
            "status": AnalysisJobStatus.FAILED.value,
            "completed_at": datetime.utcnow().isoformat(),
            "error_message": str(e)
        }).eq("job_id", job_id).execute()

async def process_single_query(request: AIAnalysisRequest, supabase, audit_id: str = None) -> bool:
    """
    Process a single query through AI analysis and store results
    
    Args:
        request: AIAnalysisRequest with query details
        supabase: Supabase client for database operations
        
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        Exception: If processing fails
    """
    try:
        logger.debug(f"🔍 Processing query {request.query_id}")
        
        # Analyze with OpenAI
        analysis_result = await openai_service.analyze_brand_perception(request)
        
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
        
        # Store citations if any
        if analysis_result.citations:
            citations_data = []
            for citation in analysis_result.citations:
                citations_data.append({
                    "citation_id": str(uuid.uuid4()),
                    "response_id": response_id,
                    "citation_text": citation.text,
                    "source_url": citation.source_url
                })
            
            citations_result = supabase.table("citations").insert(citations_data).execute()
            
            if hasattr(citations_result, 'error') and citations_result.error:
                logger.warning(f"⚠️ Failed to store citations for {request.query_id}: {citations_result.error}")
        
        # Store brand mentions if any
        if analysis_result.brand_mentions:
            mentions_data = []
            for mention in analysis_result.brand_mentions:
                mentions_data.append({
                    "mention_id": str(uuid.uuid4()),
                    "response_id": response_id,
                    "brand_name": mention.brand_name,
                    "mention_context": mention.context,
                    "sentiment_score": mention.sentiment_score
                })
            
            mentions_result = supabase.table("brand_mentions").insert(mentions_data).execute()
            
            if hasattr(mentions_result, 'error') and mentions_result.error:
                logger.warning(f"⚠️ Failed to store brand mentions for {request.query_id}: {mentions_result.error}")
        
        # Store competitors if any (will be aggregated later)
        if analysis_result.competitors and audit_id:
            logger.info(f"📊 Found {len(analysis_result.competitors)} competitors in this query")
            # Note: Competitors will be aggregated and stored at the end of the analysis job
        elif analysis_result.competitors:
            logger.warning(f"⚠️ Competitors found but no audit_id provided: {len(analysis_result.competitors)} competitors")
        else:
            logger.info(f"📊 No competitors found for this query")
        
        logger.debug(f"✅ Successfully processed query {request.query_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error processing query {request.query_id}: {e}")
        raise e

async def process_single_query_with_aggregation(request: AIAnalysisRequest, supabase, audit_id: str = None, brand_mentions_aggregated: Dict = None) -> bool:
    """
    Process a single query through AI analysis and store results, while aggregating brand mentions
    
    Args:
        request: AIAnalysisRequest with query details
        supabase: Supabase client for database operations
        audit_id: Audit ID for storing results
        brand_mentions_aggregated: Dictionary to aggregate brand mentions across queries
        
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        Exception: If processing fails
    """
    try:
        logger.debug(f"🔍 Processing query {request.query_id}")
        
        # Analyze with OpenAI (pass target brand for competitor identification)
        target_brand = request.brand_name if hasattr(request, 'brand_name') else None
        analysis_result = await openai_service.analyze_brand_perception(request, target_brand)
        
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
        
        # Store citations if any
        if analysis_result.citations:
            citations_data = []
            for citation in analysis_result.citations:
                citations_data.append({
                    "citation_id": str(uuid.uuid4()),
                    "response_id": response_id,
                    "citation_text": citation.text,
                    "source_url": citation.source_url
                })
            
            citations_result = supabase.table("citations").insert(citations_data).execute()
            
            if hasattr(citations_result, 'error') and citations_result.error:
                logger.warning(f"⚠️ Failed to store citations for {request.query_id}: {citations_result.error}")
        
        # Store brand mentions if any
        if analysis_result.brand_mentions:
            mentions_data = []
            for mention in analysis_result.brand_mentions:
                mentions_data.append({
                    "mention_id": str(uuid.uuid4()),
                    "response_id": response_id,
                    "brand_name": mention.brand_name,
                    "mention_context": mention.context,
                    "sentiment_score": mention.sentiment_score
                })
                
                # Aggregate brand mentions for competitors table
                if brand_mentions_aggregated is not None:
                    brand_name = mention.brand_name
                    brand_mentions_aggregated[brand_name] = brand_mentions_aggregated.get(brand_name, 0) + 1
            
            mentions_result = supabase.table("brand_mentions").insert(mentions_data).execute()
            
            if hasattr(mentions_result, 'error') and mentions_result.error:
                logger.warning(f"⚠️ Failed to store brand mentions for {request.query_id}: {mentions_result.error}")
        
        # Also aggregate competitors from the AI response
        if analysis_result.competitors and brand_mentions_aggregated is not None:
            logger.info(f"📊 Found {len(analysis_result.competitors)} competitors in this query")
            for competitor in analysis_result.competitors:
                brand_name = competitor.brand_name
                brand_mentions_aggregated[brand_name] = brand_mentions_aggregated.get(brand_name, 0) + competitor.mention_count
        elif analysis_result.competitors:
            logger.warning(f"⚠️ Competitors found but no aggregation dict provided: {len(analysis_result.competitors)} competitors")
        else:
            logger.info(f"📊 No competitors found for this query")
        
        logger.debug(f"✅ Successfully processed query {request.query_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error processing query {request.query_id}: {e}")
        raise e 