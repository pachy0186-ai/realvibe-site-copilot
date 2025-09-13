"""
Questionnaires API routes for RealVibe Site Copilot
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.api.auth import get_current_user, TokenData
from app.agents.pipeline import AgentPipeline
from app.core.database import get_supabase
import uuid

router = APIRouter()


class AutofillRequest(BaseModel):
    """Request model for autofill operation"""
    questionnaire_template_id: str
    questionnaire_schema: Dict[str, Any]
    run_name: Optional[str] = None


class AutofillResponse(BaseModel):
    """Response model for autofill operation"""
    run_id: str
    status: str
    message: str


@router.get("/")
async def get_questionnaires(current_user: TokenData = Depends(get_current_user)):
    """Get all questionnaire templates"""
    try:
        supabase = get_supabase()
        response = supabase.table('questionnaire_templates').select('*').execute()
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch questionnaires: {str(e)}"
        )


@router.post("/autofill", response_model=AutofillResponse)
async def start_autofill(
    request: AutofillRequest,
    background_tasks: BackgroundTasks,
    current_user: TokenData = Depends(get_current_user)
):
    """Start autofill process for a questionnaire"""
    try:
        # Generate run ID
        run_id = str(uuid.uuid4())
        
        # Initialize pipeline
        pipeline = AgentPipeline()
        
        # Start pipeline execution in background
        background_tasks.add_task(
            execute_autofill_pipeline,
            pipeline,
            current_user.site_id,
            request.questionnaire_template_id,
            request.questionnaire_schema,
            run_id
        )
        
        return AutofillResponse(
            run_id=run_id,
            status="started",
            message="Autofill process started successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start autofill: {str(e)}"
        )


@router.get("/autofill/{run_id}/status")
async def get_autofill_status(
    run_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get status of an autofill run"""
    try:
        supabase = get_supabase()
        
        # Check if user has access to this run
        response = supabase.table('runs').select('*').eq('id', run_id).eq('site_id', current_user.site_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Run not found"
            )
        
        run_data = response.data[0]
        
        return {
            "run_id": run_id,
            "status": run_data.get("status", "unknown"),
            "autofill_percentage": run_data.get("autofill_percentage", 0.0),
            "start_time": run_data.get("start_time"),
            "end_time": run_data.get("end_time")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get autofill status: {str(e)}"
        )


async def execute_autofill_pipeline(
    pipeline: AgentPipeline,
    site_id: str,
    questionnaire_template_id: str,
    questionnaire_schema: Dict[str, Any],
    run_id: str
):
    """Execute the autofill pipeline in background"""
    try:
        # Create run record
        supabase = get_supabase()
        supabase.table('runs').insert({
            'id': run_id,
            'site_id': site_id,
            'questionnaire_template_id': questionnaire_template_id,
            'status': 'in_progress'
        }).execute()
        
        # Execute pipeline
        result = await pipeline.execute(
            site_id=site_id,
            questionnaire_template_id=questionnaire_template_id,
            questionnaire_schema=questionnaire_schema,
            run_id=run_id
        )
        
        # Update run record with results
        supabase.table('runs').update({
            'status': 'completed' if result['success'] else 'failed',
            'end_time': 'now()',
            'autofill_percentage': result.get('autofill_percentage', 0.0)
        }).eq('id', run_id).execute()
        
    except Exception as e:
        # Update run record with error
        try:
            supabase = get_supabase()
            supabase.table('runs').update({
                'status': 'failed',
                'end_time': 'now()'
            }).eq('id', run_id).execute()
        except:
            pass  # Ignore errors in error handling

