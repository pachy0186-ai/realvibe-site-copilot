"""
Gmail service for RealVibe Site Copilot.
Handles email notifications to reviewers and stakeholders.
"""

import os
import base64
import json
from typing import List, Dict, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings


class GmailService:
    """Service for sending email notifications via Gmail API."""
    
    # Gmail API scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    def __init__(self):
        self.service = None
        self.credentials = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Gmail API service with authentication."""
        try:
            # Load credentials from environment or file
            creds = None
            
            # Check for stored credentials
            if hasattr(settings, 'GMAIL_CREDENTIALS_JSON'):
                creds_data = json.loads(settings.GMAIL_CREDENTIALS_JSON)
                creds = Credentials.from_authorized_user_info(creds_data, self.SCOPES)
            
            # If there are no (valid) credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    # For production, you would handle OAuth flow differently
                    print("Gmail credentials not available or invalid")
                    return
            
            # Build the service
            self.service = build('gmail', 'v1', credentials=creds)
            self.credentials = creds
            
        except Exception as e:
            print(f"Failed to initialize Gmail service: {e}")
            self.service = None
    
    async def send_notification(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Send an email notification.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body_text: Plain text body
            body_html: HTML body (optional)
            from_email: Sender email (optional, uses authenticated account)
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.service:
            print("Gmail service not initialized")
            return False
        
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['To'] = to_email
            message['Subject'] = subject
            
            if from_email:
                message['From'] = from_email
            
            # Add text part
            text_part = MIMEText(body_text, 'plain')
            message.attach(text_part)
            
            # Add HTML part if provided
            if body_html:
                html_part = MIMEText(body_html, 'html')
                message.attach(html_part)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send message
            send_result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"Email sent successfully. Message ID: {send_result.get('id')}")
            return True
            
        except HttpError as error:
            print(f"Gmail API error: {error}")
            return False
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    async def send_review_notification(
        self,
        reviewer_email: str,
        questionnaire_name: str,
        sponsor: str,
        run_id: str,
        autofill_percentage: float,
        fields_needing_review: int,
        review_url: str
    ) -> bool:
        """
        Send a notification to reviewer when questionnaire needs review.
        
        Args:
            reviewer_email: Email of the reviewer
            questionnaire_name: Name of the questionnaire
            sponsor: Sponsor name
            run_id: Run identifier
            autofill_percentage: Percentage of fields auto-filled
            fields_needing_review: Number of fields requiring review
            review_url: URL to review the questionnaire
            
        Returns:
            True if notification was sent successfully
        """
        subject = f"Review Required: {questionnaire_name}"
        
        # Plain text body
        body_text = f"""
Dear Reviewer,

A questionnaire has been processed and requires your review:

Questionnaire: {questionnaire_name}
Sponsor: {sponsor}
Run ID: {run_id}
Autofill Success Rate: {autofill_percentage:.1f}%
Fields Requiring Review: {fields_needing_review}

Please review the questionnaire at: {review_url}

Target review time: ≤15 minutes

Best regards,
RealVibe Site Copilot
        """.strip()
        
        # HTML body
        body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #2563eb; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .metrics {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #2563eb; }}
        .metric-label {{ font-size: 12px; color: #666; }}
        .cta-button {{ 
            display: inline-block; 
            background-color: #2563eb; 
            color: white; 
            padding: 12px 24px; 
            text-decoration: none; 
            border-radius: 5px; 
            margin: 20px 0; 
        }}
        .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Review Required</h1>
        <p>RealVibe Site Copilot</p>
    </div>
    
    <div class="content">
        <h2>Questionnaire Ready for Review</h2>
        
        <p>Dear Reviewer,</p>
        
        <p>A questionnaire has been processed and requires your attention:</p>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-value">{autofill_percentage:.1f}%</div>
                <div class="metric-label">Autofill Success</div>
            </div>
            <div class="metric">
                <div class="metric-value">{fields_needing_review}</div>
                <div class="metric-label">Fields Need Review</div>
            </div>
            <div class="metric">
                <div class="metric-value">≤15 min</div>
                <div class="metric-label">Target Review Time</div>
            </div>
        </div>
        
        <p><strong>Questionnaire:</strong> {questionnaire_name}</p>
        <p><strong>Sponsor:</strong> {sponsor}</p>
        <p><strong>Run ID:</strong> {run_id}</p>
        
        <a href="{review_url}" class="cta-button">Start Review</a>
        
        <p>Please complete your review as soon as possible to maintain our target cycle time.</p>
    </div>
    
    <div class="footer">
        <p>This is an automated notification from RealVibe Site Copilot</p>
        <p>If you have questions, please contact your site administrator</p>
    </div>
</body>
</html>
        """.strip()
        
        return await self.send_notification(
            to_email=reviewer_email,
            subject=subject,
            body_text=body_text,
            body_html=body_html
        )
    
    async def send_completion_notification(
        self,
        stakeholder_email: str,
        questionnaire_name: str,
        sponsor: str,
        run_id: str,
        autofill_percentage: float,
        review_time: int,
        cycle_time_saved: float
    ) -> bool:
        """
        Send notification when questionnaire review is completed.
        
        Args:
            stakeholder_email: Email of stakeholder to notify
            questionnaire_name: Name of the questionnaire
            sponsor: Sponsor name
            run_id: Run identifier
            autofill_percentage: Final autofill percentage
            review_time: Time spent on review (minutes)
            cycle_time_saved: Estimated time saved (weeks)
            
        Returns:
            True if notification was sent successfully
        """
        subject = f"Completed: {questionnaire_name}"
        
        # Plain text body
        body_text = f"""
Questionnaire Review Completed

Questionnaire: {questionnaire_name}
Sponsor: {sponsor}
Run ID: {run_id}

Performance Metrics:
- Autofill Success Rate: {autofill_percentage:.1f}%
- Review Time: {review_time} minutes
- Estimated Cycle Time Saved: {cycle_time_saved:.1f} weeks

The questionnaire has been successfully processed and reviewed.

Best regards,
RealVibe Site Copilot
        """.strip()
        
        # HTML body
        body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #10b981; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .metrics {{ background-color: #f0fdf4; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #10b981; }}
        .metric-label {{ font-size: 12px; color: #666; }}
        .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>✅ Review Completed</h1>
        <p>RealVibe Site Copilot</p>
    </div>
    
    <div class="content">
        <h2>Questionnaire Successfully Processed</h2>
        
        <p><strong>Questionnaire:</strong> {questionnaire_name}</p>
        <p><strong>Sponsor:</strong> {sponsor}</p>
        <p><strong>Run ID:</strong> {run_id}</p>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-value">{autofill_percentage:.1f}%</div>
                <div class="metric-label">Autofill Success</div>
            </div>
            <div class="metric">
                <div class="metric-value">{review_time}</div>
                <div class="metric-label">Review Time (min)</div>
            </div>
            <div class="metric">
                <div class="metric-value">{cycle_time_saved:.1f}</div>
                <div class="metric-label">Time Saved (weeks)</div>
            </div>
        </div>
        
        <p>The questionnaire has been successfully processed and is ready for submission.</p>
    </div>
    
    <div class="footer">
        <p>This is an automated notification from RealVibe Site Copilot</p>
    </div>
</body>
</html>
        """.strip()
        
        return await self.send_notification(
            to_email=stakeholder_email,
            subject=subject,
            body_text=body_text,
            body_html=body_html
        )
    
    async def send_error_notification(
        self,
        admin_email: str,
        error_type: str,
        error_details: str,
        run_id: Optional[str] = None
    ) -> bool:
        """
        Send error notification to administrators.
        
        Args:
            admin_email: Administrator email
            error_type: Type of error
            error_details: Detailed error information
            run_id: Run identifier if applicable
            
        Returns:
            True if notification was sent successfully
        """
        subject = f"Site Copilot Error: {error_type}"
        
        body_text = f"""
Site Copilot Error Alert

Error Type: {error_type}
Run ID: {run_id or 'N/A'}
Timestamp: {datetime.utcnow().isoformat()}

Error Details:
{error_details}

Please investigate and resolve this issue.

RealVibe Site Copilot System
        """.strip()
        
        return await self.send_notification(
            to_email=admin_email,
            subject=subject,
            body_text=body_text
        )
    
    def is_service_available(self) -> bool:
        """Check if Gmail service is available and authenticated."""
        return self.service is not None and self.credentials is not None
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Gmail service connection and return status."""
        if not self.service:
            return {
                "status": "error",
                "message": "Gmail service not initialized"
            }
        
        try:
            # Test by getting user profile
            profile = self.service.users().getProfile(userId='me').execute()
            
            return {
                "status": "success",
                "message": "Gmail service connected successfully",
                "email": profile.get('emailAddress'),
                "messages_total": profile.get('messagesTotal', 0)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Gmail service test failed: {str(e)}"
            }

