"""
Celery tasks for async operations
"""
from celery import shared_task
from django.utils import timezone
import requests
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5)
def deliver_webhook(self, webhook_log_id):
    """
    Deliver webhook with retry logic
    Uses exponential backoff: 60s, 300s, 900s, 3600s, 7200s
    """
    from integrations.models import WebhookLog, Integration
    from integrations.services.webhook_service import sign_payload
    
    try:
        webhook_log = WebhookLog.objects.get(id=webhook_log_id)
        integration = webhook_log.integration
        
        # Get webhook config
        config = integration.get_config()
        webhook_url = config.get('url')
        secret = config.get('secret', '')
        
        if not webhook_url:
            webhook_log.status = 'failed'
            webhook_log.response_body = 'No webhook URL configured'
            webhook_log.save()
            return
        
        # Prepare payload
        import json
        payload_str = json.dumps(webhook_log.payload_json)
        
        # Sign payload if secret is configured
        headers = {'Content-Type': 'application/json'}
        if secret:
            signature = sign_payload(payload_str, secret)
            headers['X-FormForge-Signature'] = signature
        
        # Make request with 10 second timeout
        webhook_log.status = 'retrying'
        webhook_log.save()
        
        response = requests.post(
            webhook_url,
            data=payload_str,
            headers=headers,
            timeout=10
        )
        
        # Update log with response
        webhook_log.response_status_code = response.status_code
        webhook_log.response_body = response.text[:5000]  # Truncate large responses
        
        # Check if successful (2xx status code)
        if 200 <= response.status_code < 300:
            webhook_log.status = 'success'
            integration.last_triggered_at = timezone.now()
            integration.status = 'active'
            integration.error_message = ''
            integration.save()
        else:
            # Retry on non-2xx
            raise Exception(f"Webhook returned status {response.status_code}")
        
        webhook_log.save()
        
    except requests.exceptions.Timeout:
        webhook_log.status = 'failed'
        webhook_log.response_body = 'Request timeout after 10 seconds'
        webhook_log.save()
        
        # Retry with exponential backoff
        raise self.retry(countdown=60 * (2 ** self.request.retries))
        
    except requests.exceptions.RequestException as e:
        webhook_log.status = 'failed'
        webhook_log.response_body = str(e)[:5000]
        webhook_log.save()
        
        # Retry with exponential backoff
        raise self.retry(countdown=60 * (2 ** self.request.retries))
        
    except Exception as e:
        logger.error(f"Webhook delivery error: {e}")
        webhook_log.status = 'failed'
        webhook_log.response_body = str(e)[:5000]
        webhook_log.save()
        
        # Mark integration as error if all retries exhausted
        if self.request.retries >= self.max_retries:
            integration.status = 'error'
            integration.error_message = f"Webhook delivery failed after {self.max_retries} retries"
            integration.save()


@shared_task
def send_submission_email(submission_id):
    """Send email notification for new submission"""
    from forms.models import Submission
    from integrations.services.sync_service import sync_to_email
    
    try:
        submission = Submission.objects.get(id=submission_id)
        
        # Get email integrations for this form
        email_integrations = submission.form.integrations.filter(
            type='email',
            status='active'
        )
        
        for integration in email_integrations:
            try:
                sync_to_email(integration, submission)
            except Exception as e:
                logger.error(f"Email send failed for integration {integration.id}: {e}")
                
    except Submission.DoesNotExist:
        logger.error(f"Submission {submission_id} not found")


@shared_task
def sync_to_google_sheets(submission_id):
    """Sync submission to Google Sheets"""
    from forms.models import Submission
    from integrations.services.sync_service import sync_to_google_sheets as sync_sheets
    
    try:
        submission = Submission.objects.get(id=submission_id)
        
        # Get Google Sheets integrations for this form
        sheets_integrations = submission.form.integrations.filter(
            type='google_sheets',
            status='active'
        )
        
        for integration in sheets_integrations:
            try:
                sync_sheets(integration, submission)
            except Exception as e:
                logger.error(f"Google Sheets sync failed for integration {integration.id}: {e}")
                integration.status = 'error'
                integration.error_message = str(e)
                integration.save()
                
    except Submission.DoesNotExist:
        logger.error(f"Submission {submission_id} not found")
