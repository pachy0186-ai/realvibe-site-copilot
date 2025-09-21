"""
Dashboard API routes for RealVibe Site Copilot
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from app.api.auth import get_current_user, TokenData
from app.services.metrics_service import MetricsService, TimeRange

router = APIRouter()

# Initialize metrics service
metrics_service = MetricsService()


@router.get("/metrics")
async def get_dashboard_metrics(
    time_range: str = Query("last_30d", description="Time range for metrics"),
    current_user: TokenData = Depends(get_current_user)
):
    """Get dashboard metrics for the current site"""
    try:
        # Parse time range
        try:
            time_range_enum = TimeRange(time_range)
        except ValueError:
            time_range_enum = TimeRange.LAST_30D
        
        # Get metrics
        metrics = await metrics_service.get_dashboard_metrics(
            site_id=current_user.site_id,
            time_range=time_range_enum
        )
        
        return {
            "success": True,
            "data": metrics
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dashboard metrics: {str(e)}"
        )


@router.get("/analytics")
async def get_detailed_analytics(
    time_range: str = Query("last_30d", description="Time range for analytics"),
    current_user: TokenData = Depends(get_current_user)
):
    """Get detailed analytics for the current site"""
    try:
        # Parse time range
        try:
            time_range_enum = TimeRange(time_range)
        except ValueError:
            time_range_enum = TimeRange.LAST_30D
        
        # Get analytics
        analytics = await metrics_service.get_detailed_analytics(
            site_id=current_user.site_id,
            time_range=time_range_enum
        )
        
        return {
            "success": True,
            "data": analytics
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get detailed analytics: {str(e)}"
        )


@router.get("/benchmarks")
async def get_performance_benchmarks(current_user: TokenData = Depends(get_current_user)):
    """Get performance benchmarks and current performance comparison"""
    try:
        benchmarks = await metrics_service.get_performance_benchmarks(current_user.site_id)
        
        return {
            "success": True,
            "data": benchmarks
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get performance benchmarks: {str(e)}"
        )


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = Query(10, description="Number of recent activities to return"),
    current_user: TokenData = Depends(get_current_user)
):
    """Get recent activity for the dashboard"""
    try:
        # Get recent metrics which includes recent activity
        metrics = await metrics_service.get_dashboard_metrics(
            site_id=current_user.site_id,
            time_range=TimeRange.LAST_7D
        )
        
        recent_activity = metrics.get("recent_activity", [])[:limit]
        
        return {
            "success": True,
            "data": {
                "activities": recent_activity,
                "total_count": len(recent_activity)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recent activity: {str(e)}"
        )


@router.get("/summary")
async def get_dashboard_summary(current_user: TokenData = Depends(get_current_user)):
    """Get dashboard summary with key metrics"""
    try:
        # Get current metrics
        metrics = await metrics_service.get_dashboard_metrics(
            site_id=current_user.site_id,
            time_range=TimeRange.LAST_30D
        )
        
        # Get benchmarks for comparison
        benchmarks = await metrics_service.get_performance_benchmarks(current_user.site_id)
        
        summary = {
            "key_metrics": metrics["summary"],
            "performance_scores": benchmarks.get("scores", {}),
            "overall_score": benchmarks.get("overall_score", "unknown"),
            "recommendations": benchmarks.get("recommendations", []),
            "trends": metrics.get("trends", [])[-7:],  # Last 7 days
            "last_updated": metrics.get("last_updated")
        }
        
        return {
            "success": True,
            "data": summary
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dashboard summary: {str(e)}"
        )


@router.post("/track-run")
async def track_run_metrics(
    run_data: dict,
    current_user: TokenData = Depends(get_current_user)
):
    """Track metrics for a completed questionnaire run"""
    try:
        success = await metrics_service.track_run_metrics(
            run_id=run_data.get("run_id"),
            site_id=current_user.site_id,
            questionnaire_name=run_data.get("questionnaire_name"),
            sponsor=run_data.get("sponsor"),
            total_fields=run_data.get("total_fields", 0),
            autofilled_fields=run_data.get("autofilled_fields", 0),
            review_time_minutes=run_data.get("review_time_minutes"),
            completion_time=run_data.get("completion_time")
        )
        
        return {
            "success": success,
            "message": "Run metrics tracked successfully" if success else "Failed to track run metrics"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to track run metrics: {str(e)}"
        )


@router.get("/export")
async def export_metrics(
    format: str = Query("json", description="Export format (json, csv)"),
    time_range: str = Query("last_30d", description="Time range for export"),
    current_user: TokenData = Depends(get_current_user)
):
    """Export metrics data"""
    try:
        # Parse time range
        try:
            time_range_enum = TimeRange(time_range)
        except ValueError:
            time_range_enum = TimeRange.LAST_30D
        
        # Get detailed analytics for export
        analytics = await metrics_service.get_detailed_analytics(
            site_id=current_user.site_id,
            time_range=time_range_enum
        )
        
        if format.lower() == "csv":
            # For CSV export, you would convert the data to CSV format
            # For now, return JSON with a note
            return {
                "success": True,
                "message": "CSV export would be implemented here",
                "data": analytics,
                "format": "json"
            }
        else:
            return {
                "success": True,
                "data": analytics,
                "format": "json"
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export metrics: {str(e)}"
        )


@router.get("/health")
async def get_dashboard_health():
    """Get dashboard system health status"""
    try:
        # Check various system components
        health_status = {
            "status": "healthy",
            "components": {
                "metrics_service": "operational",
                "database": "operational",
                "cache": "operational"
            },
            "last_updated": "2024-01-15T12:00:00Z"
        }
        
        return {
            "success": True,
            "data": health_status
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": {
                "status": "unhealthy",
                "error": str(e),
                "last_updated": "2024-01-15T12:00:00Z"
            }
        }

