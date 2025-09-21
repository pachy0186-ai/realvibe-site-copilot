"""
Notifications API routes for RealVibe Site Copilot
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr
from app.api.auth import get_current_user, TokenData
from app.services.notification_service import NotificationService, NotificationType

router = APIRouter()

# Initialize notification service
notification_service = NotificationService()


class NotificationSettings(BaseModel):
    """Model for notification settings"""
    review_required_enabled: bool = True
    review_completed_enabled: bool = True
    error_alerts_enabled: bool = True
    daily_summary_enabled: bool = True
    reviewer_emails: List[EmailStr] = []
    stakeholder_emails: List[EmailStr] = []
    admin_emails: List[EmailStr] = []


class TestNotificationRequest(BaseModel):
    """Model for test notification request"""
    notification_type: str
    recipient_email: EmailStr
    test_data: Optional[Dict[str, Any]] = None


@router.get("/settings")
async def get_notification_settings(current_user: TokenData = Depends(get_current_user)):
    """Get notification settings for the current site"""
    try:
        # Get current settings from database or return defaults
        settings = NotificationSettings(
            reviewer_emails=["reviewer@realvibe.ai"],
            stakeholder_emails=["stakeholder@realvibe.ai"],
            admin_emails=["admin@realvibe.ai"]
        )
        
        return {
            "success": True,
            "data": settings.dict()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get notification settings: {str(e)}"
        )


@router.put("/settings")
async def update_notification_settings(
    settings: NotificationSettings,
    current_user: TokenData = Depends(get_current_user)
):
    """Update notification settings for the current site"""
    try:
        # In a real implementation, this would update the database
        # For now, we'll just return success
        
        return {
            "success": True,
            "message": "Notification settings updated successfully",
            "data": settings.dict()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update notification settings: {str(e)}"
        )


@router.post("/test")
async def test_notification_system(current_user: TokenData = Depends(get_current_user)):
    """Test the notification system for the current site"""
    try:
        test_results = await notification_service.test_notification_system(current_user.site_id)
        
        return {
            "success": True,
            "data": test_results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Notification system test failed: {str(e)}"
        )


@router.post("/send-test")
async def send_test_notification(
    request: TestNotificationRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """Send a test notification"""
    try:
        success = False
        
        if request.notification_type == "review_required":
            # Send test review notification
            success = await notification_service.send_review_notification(
                site_id=current_user.site_id,
                run_id="test-run-001",
                questionnaire_name="Test Feasibility Questionnaire",
                sponsor="Test Sponsor",
                autofill_percentage=75.0,
                fields_needing_review=3
            )
            
        elif request.notification_type == "review_completed":
            # Send test completion notification
            success = await notification_service.send_completion_notification(
                site_id=current_user.site_id,
                run_id="test-run-001",
                questionnaire_name="Test Feasibility Questionnaire",
                sponsor="Test Sponsor",
                autofill_percentage=85.0,
                review_time=10,
                cycle_time_saved=1.5
            )
            
        elif request.notification_type == "error_alert":
            # Send test error alert
            success = await notification_service.send_error_alert(
                site_id=current_user.site_id,
                error_type="Test Error",
                error_details="This is a test error notification",
                run_id="test-run-001"
            )
            
        elif request.notification_type == "daily_summary":
            # Send test daily summary
            success = await notification_service.send_daily_summary(current_user.site_id)
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown notification type: {request.notification_type}"
            )
        
        return {
            "success": success,
            "message": "Test notification sent successfully" if success else "Failed to send test notification"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send test notification: {str(e)}"
        )


@router.get("/logs")
async def get_notification_logs(
    limit: int = 50,
    current_user: TokenData = Depends(get_current_user)
):
    """Get notification logs for the current site"""
    try:
        # Mock notification logs for demo
        logs = [
            {
                "id": "log-001",
                "notification_type": "review_required",
                "recipient": "reviewer@realvibe.ai",
                "subject": "Review Required: Pfizer Phase III Feasibility",
                "status": "sent",
                "sent_at": "2024-01-15T10:45:00Z",
                "run_id": "run-001"
            },
            {
                "id": "log-002",
                "notification_type": "review_completed",
                "recipient": "stakeholder@realvibe.ai",
                "subject": "Completed: Pfizer Phase III Feasibility",
                "status": "sent",
                "sent_at": "2024-01-15T11:30:00Z",
                "run_id": "run-001"
            },
            {
                "id": "log-003",
                "notification_type": "review_required",
                "recipient": "reviewer@realvibe.ai",
                "subject": "Review Required: Novartis Oncology Study",
                "status": "sent",
                "sent_at": "2024-01-14T14:35:00Z",
                "run_id": "run-002"
            }
        ]
        
        return {
            "success": True,
            "data": {
                "logs": logs[:limit],
                "total_count": len(logs)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get notification logs: {str(e)}"
        )


@router.get("/stats")
async def get_notification_stats(current_user: TokenData = Depends(get_current_user)):
    """Get notification statistics for the current site"""
    try:
        # Mock notification statistics
        stats = {
            "total_sent": 156,
            "sent_today": 8,
            "success_rate": 98.7,
            "by_type": {
                "review_required": 89,
                "review_completed": 45,
                "error_alert": 12,
                "daily_summary": 10
            },
            "recent_activity": [
                {
                    "date": "2024-01-15",
                    "sent": 8,
                    "failed": 0
                },
                {
                    "date": "2024-01-14",
                    "sent": 12,
                    "failed": 1
                },
                {
                    "date": "2024-01-13",
                    "sent": 6,
                    "failed": 0
                }
            ]
        }
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get notification stats: {str(e)}"
        )


@router.post("/trigger/review-required")
async def trigger_review_notification(
    run_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Manually trigger a review required notification"""
    try:
        # This would typically get run details from database
        # For demo, using mock data
        success = await notification_service.send_review_notification(
            site_id=current_user.site_id,
            run_id=run_id,
            questionnaire_name="Manual Review Trigger",
            sponsor="Test Sponsor",
            autofill_percentage=70.0,
            fields_needing_review=5
        )
        
        return {
            "success": success,
            "message": "Review notification triggered successfully" if success else "Failed to trigger notification"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger review notification: {str(e)}"
        )


@router.get("/health")
async def check_notification_health():
    """Check the health of the notification system"""
    try:
        gmail_status = await notification_service.gmail_service.test_connection()
        
        health_status = {
            "status": "healthy" if gmail_status["status"] == "success" else "unhealthy",
            "gmail_service": gmail_status,
            "timestamp": "2024-01-15T12:00:00Z"
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
                "timestamp": "2024-01-15T12:00:00Z"
            }
        }

