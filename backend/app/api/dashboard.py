"""
Dashboard API routes for RealVibe Site Copilot
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.api.auth import get_current_user, TokenData

router = APIRouter()


@router.get("/metrics")
async def get_dashboard_metrics(current_user: TokenData = Depends(get_current_user)):
    """Get dashboard metrics for the current site"""
    # TODO: Implement metrics calculation
    return {
        "autofill_percentage": 0.0,
        "average_review_time": 0.0,
        "cycle_time_reduction": 0.0,
        "total_runs": 0,
        "completed_runs": 0
    }


@router.get("/recent-activity")
async def get_recent_activity(current_user: TokenData = Depends(get_current_user)):
    """Get recent activity for the dashboard"""
    # TODO: Implement recent activity
    return {"message": "Recent activity endpoint - to be implemented"}

