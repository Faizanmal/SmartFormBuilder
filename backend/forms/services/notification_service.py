"""
Notification Service for sending emails/SMS on form submissions
"""
from typing import Dict, Any
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Handle email and SMS notifications for form submissions"""
    
    @staticmethod
    def render_template(template_str: str, context: Dict[str, Any]) -> str:
        """
        Render a template string with context variables
        
        Args:
            template_str: Template string with {{variable}} placeholders
            context: Dictionary of variables to replace
            
        Returns:
            Rendered string
        """
        # Simple placeholder replacement
        result = template_str
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        return result
    
    @staticmethod
    def send_email(
        recipient: str,
        subject: str,
        body: str,
        html_body: str = None
    ) -> bool:
        """
        Send an email notification
        
        Args:
            recipient: Email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@formforge.io')
            
            send_mail(
                subject=subject,
                message=body,
                from_email=from_email,
                recipient_list=[recipient],
                fail_silently=False,
                html_message=html_body
            )
            logger.info(f"Email sent to {recipient}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {e}")
            return False
    
    @staticmethod
    def send_sms(phone_number: str, message: str) -> bool:
        """
        Send an SMS notification (placeholder for Twilio integration)
        
        Args:
            phone_number: Recipient phone number
            message: SMS text
            
        Returns:
            True if successful, False otherwise
        """
        # TODO: Integrate with Twilio or similar SMS provider
        logger.info(f"SMS notification (not implemented): {phone_number} - {message}")
        return True
    
    @staticmethod
    def process_submission_notifications(submission, form):
        """
        Process and send all configured notifications for a submission
        
        Args:
            submission: Submission model instance
            form: Form model instance
        """
        notifications = form.notifications.filter(
            is_active=True,
            trigger='on_submit'
        )
        
        # Build context from submission data
        context = {
            'form_title': form.title,
            'submission_id': str(submission.id),
            'submitted_at': submission.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'ip_address': submission.ip_address or 'N/A',
        }
        
        # Add all form fields to context
        payload = submission.payload_json or {}
        for key, value in payload.items():
            # Convert lists to comma-separated strings
            if isinstance(value, list):
                value = ', '.join(str(v) for v in value)
            context[key] = value
        
        # Send each notification
        for notification in notifications:
            try:
                rendered_body = NotificationService.render_template(
                    notification.template,
                    context
                )
                
                if notification.type == 'email':
                    subject = NotificationService.render_template(
                        notification.subject or f"New submission: {form.title}",
                        context
                    )
                    NotificationService.send_email(
                        recipient=notification.recipient,
                        subject=subject,
                        body=rendered_body
                    )
                
                elif notification.type == 'sms':
                    NotificationService.send_sms(
                        phone_number=notification.recipient,
                        message=rendered_body
                    )
                
                elif notification.type == 'webhook':
                    # Webhook handled by webhook_service in integrations
                    pass
                
            except Exception as e:
                logger.error(f"Failed to send notification {notification.id}: {e}")
    
    @staticmethod
    def send_payment_notification(submission, form, status: str):
        """
        Send payment-related notifications
        
        Args:
            submission: Submission model instance
            form: Form model instance
            status: 'success' or 'failure'
        """
        trigger = 'on_payment' if status == 'success' else 'on_failure'
        
        notifications = form.notifications.filter(
            is_active=True,
            trigger=trigger
        )
        
        context = {
            'form_title': form.title,
            'submission_id': str(submission.id),
            'payment_status': submission.payment_status,
            'payment_amount': f"${submission.payment_amount / 100:.2f}" if submission.payment_amount else 'N/A',
            'payment_id': submission.payment_id or 'N/A',
        }
        
        for notification in notifications:
            try:
                rendered_body = NotificationService.render_template(
                    notification.template,
                    context
                )
                
                if notification.type == 'email':
                    subject = NotificationService.render_template(
                        notification.subject or f"Payment {status}: {form.title}",
                        context
                    )
                    NotificationService.send_email(
                        recipient=notification.recipient,
                        subject=subject,
                        body=rendered_body
                    )
                
            except Exception as e:
                logger.error(f"Failed to send payment notification: {e}")
