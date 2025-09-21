"""
Notification service for RealVibe Site Copilot.
Manages different types of notifications and delivery methods.
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

from app.services.gmail_service import GmailService
from app.core.config import settings
from supabase import create_client, Client


class NotificationType(Enum):
    """Types of notifications."""
    REVIEW_REQUIRED = "review_required"
    REVIEW_COMPLETED = "review_completed"
    ERROR_ALERT = "error_alert"
    DAILY_SUMMARY = "daily_summary"


class NotificationPriority(Enum):
    """Notification priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class NotificationService:
    """Service for managing notifications across different channels."""
    
    def __init__(self):
        self.gmail_service = GmailService()
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        
        # Default notification settings
        self.default_settings = {
            NotificationType.REVIEW_REQUIRED: {
                "enabled": True,
                "priority": NotificationPriority.HIGH,
                "delay_minutes": 0
            },
            NotificationType.REVIEW_COMPLETED: {
                "enabled": True,
                "priority": NotificationPriority.MEDIUM,
                "delay_minutes": 5
            },
            NotificationType.ERROR_ALERT: {
                "enabled": True,
                "priority": NotificationPriority.URGENT,
                "delay_minutes": 0
            },
            NotificationType.DAILY_SUMMARY: {
                "enabled": True,
                "priority": NotificationPriority.LOW,
                "delay_minutes": 0
            }
        }
    
    async def send_review_notification(
        self,
        site_id: str,
        run_id: str,
        questionnaire_name: str,
        sponsor: str,
        autofill_percentage: float,
        fields_needing_review: int
    ) -> bool:
        """
        Send notification when questionnaire needs review.
        
        Args:
            site_id: Site identifier
            run_id: Run identifier
            questionnaire_name: Name of questionnaire
            sponsor: Sponsor name
            autofill_percentage: Percentage auto-filled
            fields_needing_review: Number of fields needing review
            
        Returns:
            True if notification was sent successfully
        """
        try:
            # Get site notification settings and reviewer emails
            site_settings = await self._get_site_notification_settings(site_id)
            reviewer_emails = await self._get_reviewer_emails(site_id)
            
            if not reviewer_emails:
                print(f"No reviewer emails configured for site {site_id}")
                return False
            
            # Check if this notification type is enabled
            if not site_settings.get("review_required_enabled", True):
                print("Review required notifications are disabled for this site")
                return False
            
            # Generate review URL
            review_url = f"{settings.FRONTEND_URL}/site-copilot/review/{run_id}"
            
            # Send notifications to all reviewers
            success_count = 0
            
            for reviewer_email in reviewer_emails:
                try:
                    success = await self.gmail_service.send_review_notification(
                        reviewer_email=reviewer_email,
                        questionnaire_name=questionnaire_name,
                        sponsor=sponsor,
                        run_id=run_id,
                        autofill_percentage=autofill_percentage,
                        fields_needing_review=fields_needing_review,
                        review_url=review_url
                    )
                    
                    if success:
                        success_count += 1
                        
                        # Log notification
                        await self._log_notification(
                            site_id=site_id,
                            notification_type=NotificationType.REVIEW_REQUIRED,
                            recipient=reviewer_email,
                            subject=f"Review Required: {questionnaire_name}",
                            status="sent",
                            run_id=run_id
                        )
                    else:
                        await self._log_notification(
                            site_id=site_id,
                            notification_type=NotificationType.REVIEW_REQUIRED,
                            recipient=reviewer_email,
                            subject=f"Review Required: {questionnaire_name}",
                            status="failed",
                            run_id=run_id
                        )
                        
                except Exception as e:
                    print(f"Failed to send notification to {reviewer_email}: {e}")
                    continue
            
            return success_count > 0
            
        except Exception as e:
            print(f"Failed to send review notifications: {e}")
            return False
    
    async def send_completion_notification(
        self,
        site_id: str,
        run_id: str,
        questionnaire_name: str,
        sponsor: str,
        autofill_percentage: float,
        review_time: int,
        cycle_time_saved: float
    ) -> bool:
        """
        Send notification when questionnaire review is completed.
        
        Args:
            site_id: Site identifier
            run_id: Run identifier
            questionnaire_name: Name of questionnaire
            sponsor: Sponsor name
            autofill_percentage: Final autofill percentage
            review_time: Time spent on review
            cycle_time_saved: Estimated time saved
            
        Returns:
            True if notification was sent successfully
        """
        try:
            # Get stakeholder emails
            stakeholder_emails = await self._get_stakeholder_emails(site_id)
            
            if not stakeholder_emails:
                print(f"No stakeholder emails configured for site {site_id}")
                return False
            
            # Send notifications
            success_count = 0
            
            for email in stakeholder_emails:
                try:
                    success = await self.gmail_service.send_completion_notification(
                        stakeholder_email=email,
                        questionnaire_name=questionnaire_name,
                        sponsor=sponsor,
                        run_id=run_id,
                        autofill_percentage=autofill_percentage,
                        review_time=review_time,
                        cycle_time_saved=cycle_time_saved
                    )
                    
                    if success:
                        success_count += 1
                        
                        await self._log_notification(
                            site_id=site_id,
                            notification_type=NotificationType.REVIEW_COMPLETED,
                            recipient=email,
                            subject=f"Completed: {questionnaire_name}",
                            status="sent",
                            run_id=run_id
                        )
                        
                except Exception as e:
                    print(f"Failed to send completion notification to {email}: {e}")
                    continue
            
            return success_count > 0
            
        except Exception as e:
            print(f"Failed to send completion notifications: {e}")
            return False
    
    async def send_error_alert(
        self,
        site_id: str,
        error_type: str,
        error_details: str,
        run_id: Optional[str] = None
    ) -> bool:
        """
        Send error alert to administrators.
        
        Args:
            site_id: Site identifier
            error_type: Type of error
            error_details: Detailed error information
            run_id: Run identifier if applicable
            
        Returns:
            True if notification was sent successfully
        """
        try:
            # Get admin emails
            admin_emails = await self._get_admin_emails(site_id)
            
            if not admin_emails:
                # Fallback to system admin email
                admin_emails = [settings.SYSTEM_ADMIN_EMAIL] if hasattr(settings, 'SYSTEM_ADMIN_EMAIL') else []
            
            if not admin_emails:
                print("No admin emails configured for error alerts")
                return False
            
            # Send alerts
            success_count = 0
            
            for email in admin_emails:
                try:
                    success = await self.gmail_service.send_error_notification(
                        admin_email=email,
                        error_type=error_type,
                        error_details=error_details,
                        run_id=run_id
                    )
                    
                    if success:
                        success_count += 1
                        
                        await self._log_notification(
                            site_id=site_id,
                            notification_type=NotificationType.ERROR_ALERT,
                            recipient=email,
                            subject=f"Site Copilot Error: {error_type}",
                            status="sent",
                            run_id=run_id
                        )
                        
                except Exception as e:
                    print(f"Failed to send error alert to {email}: {e}")
                    continue
            
            return success_count > 0
            
        except Exception as e:
            print(f"Failed to send error alerts: {e}")
            return False
    
    async def send_daily_summary(self, site_id: str) -> bool:
        """
        Send daily summary of site activity.
        
        Args:
            site_id: Site identifier
            
        Returns:
            True if summary was sent successfully
        """
        try:
            # Get summary data for the last 24 hours
            summary_data = await self._get_daily_summary_data(site_id)
            
            if not summary_data["has_activity"]:
                print(f"No activity to report for site {site_id}")
                return True  # Not an error, just no activity
            
            # Get stakeholder emails
            stakeholder_emails = await self._get_stakeholder_emails(site_id)
            
            if not stakeholder_emails:
                return False
            
            # Create summary email content
            subject = f"Daily Summary - Site Copilot Activity"
            
            body_text = f"""
Daily Site Copilot Summary

Activity Summary for {summary_data['date']}:
- Questionnaires Processed: {summary_data['questionnaires_processed']}
- Average Autofill Rate: {summary_data['avg_autofill_rate']:.1f}%
- Average Review Time: {summary_data['avg_review_time']:.1f} minutes
- Total Time Saved: {summary_data['total_time_saved']:.1f} weeks

Files Uploaded: {summary_data['files_uploaded']}
Reviews Completed: {summary_data['reviews_completed']}

Best regards,
RealVibe Site Copilot
            """.strip()
            
            # Send to stakeholders
            success_count = 0
            
            for email in stakeholder_emails:
                try:
                    success = await self.gmail_service.send_notification(
                        to_email=email,
                        subject=subject,
                        body_text=body_text
                    )
                    
                    if success:
                        success_count += 1
                        
                except Exception as e:
                    print(f"Failed to send daily summary to {email}: {e}")
                    continue
            
            return success_count > 0
            
        except Exception as e:
            print(f"Failed to send daily summary: {e}")
            return False
    
    async def _get_site_notification_settings(self, site_id: str) -> Dict[str, Any]:
        """Get notification settings for a site."""
        try:
            result = self.supabase.table("sites").select(
                "notification_settings"
            ).eq("id", site_id).execute()
            
            if result.data:
                return result.data[0].get("notification_settings", {})
            
            return {}
            
        except Exception:
            return {}
    
    async def _get_reviewer_emails(self, site_id: str) -> List[str]:
        """Get reviewer email addresses for a site."""
        try:
            result = self.supabase.table("sites").select(
                "reviewer_emails"
            ).eq("id", site_id).execute()
            
            if result.data and result.data[0].get("reviewer_emails"):
                return result.data[0]["reviewer_emails"]
            
            # Fallback to demo email
            return ["reviewer@realvibe.ai"]
            
        except Exception:
            return ["reviewer@realvibe.ai"]
    
    async def _get_stakeholder_emails(self, site_id: str) -> List[str]:
        """Get stakeholder email addresses for a site."""
        try:
            result = self.supabase.table("sites").select(
                "stakeholder_emails"
            ).eq("id", site_id).execute()
            
            if result.data and result.data[0].get("stakeholder_emails"):
                return result.data[0]["stakeholder_emails"]
            
            # Fallback to demo email
            return ["stakeholder@realvibe.ai"]
            
        except Exception:
            return ["stakeholder@realvibe.ai"]
    
    async def _get_admin_emails(self, site_id: str) -> List[str]:
        """Get administrator email addresses for a site."""
        try:
            result = self.supabase.table("sites").select(
                "admin_emails"
            ).eq("id", site_id).execute()
            
            if result.data and result.data[0].get("admin_emails"):
                return result.data[0]["admin_emails"]
            
            return []
            
        except Exception:
            return []
    
    async def _log_notification(
        self,
        site_id: str,
        notification_type: NotificationType,
        recipient: str,
        subject: str,
        status: str,
        run_id: Optional[str] = None
    ):
        """Log notification attempt to database."""
        try:
            log_data = {
                "site_id": site_id,
                "notification_type": notification_type.value,
                "recipient": recipient,
                "subject": subject,
                "status": status,
                "run_id": run_id,
                "sent_at": datetime.utcnow().isoformat()
            }
            
            self.supabase.table("notification_logs").insert(log_data).execute()
            
        except Exception as e:
            print(f"Failed to log notification: {e}")
    
    async def _get_daily_summary_data(self, site_id: str) -> Dict[str, Any]:
        """Get daily summary data for a site."""
        try:
            # This would typically query the database for actual metrics
            # For now, return mock data
            return {
                "date": datetime.utcnow().strftime("%Y-%m-%d"),
                "has_activity": True,
                "questionnaires_processed": 3,
                "avg_autofill_rate": 72.5,
                "avg_review_time": 12.3,
                "total_time_saved": 2.1,
                "files_uploaded": 2,
                "reviews_completed": 3
            }
            
        except Exception:
            return {
                "date": datetime.utcnow().strftime("%Y-%m-%d"),
                "has_activity": False
            }
    
    async def test_notification_system(self, site_id: str) -> Dict[str, Any]:
        """Test the notification system for a site."""
        results = {
            "gmail_service": await self.gmail_service.test_connection(),
            "reviewer_emails": await self._get_reviewer_emails(site_id),
            "stakeholder_emails": await self._get_stakeholder_emails(site_id),
            "admin_emails": await self._get_admin_emails(site_id)
        }
        
        return results

