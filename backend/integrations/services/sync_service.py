"""
Integration sync service - handles sending submissions to integrations
"""
from django.utils import timezone
from integrations.models import Integration, WebhookLog
from integrations.services.google_sheets import append_row_to_sheet, create_spreadsheet


def sync_submission_to_integrations(submission):
    """Sync a submission to all active integrations for its form"""
    form = submission.form
    integrations = Integration.objects.filter(
        form=form,
        status='active'
    )
    
    for integration in integrations:
        try:
            if integration.type == 'google_sheets':
                # Queue async task
                from integrations.tasks import sync_to_google_sheets
                sync_to_google_sheets.delay(str(submission.id))
                
            elif integration.type == 'webhook':
                # Create webhook log and queue delivery
                trigger_webhook(integration, submission)
                
            elif integration.type == 'email':
                # Queue async email task
                from integrations.tasks import send_submission_email
                send_submission_email.delay(str(submission.id))
                
            integration.last_triggered_at = timezone.now()
            integration.save()
            
        except Exception as e:
            integration.status = 'error'
            integration.error_message = str(e)
            integration.save()


def trigger_webhook(integration, submission):
    """Create webhook log entry and queue delivery task"""
    config = integration.get_config()
    webhook_url = config.get('url')
    
    if not webhook_url:
        return
    
    # Prepare payload
    payload = {
        'event': 'form.submission',
        'form': {
            'id': str(submission.form.id),
            'title': submission.form.title,
            'slug': submission.form.slug,
        },
        'submission': {
            'id': str(submission.id),
            'created_at': submission.created_at.isoformat(),
            'ip_address': submission.ip_address,
            'data': submission.payload_json,
        }
    }
    
    # Create webhook log
    webhook_log = WebhookLog.objects.create(
        integration=integration,
        submission=submission,
        payload_json=payload,
        status='pending'
    )
    
    # Queue delivery task
    from integrations.tasks import deliver_webhook
    deliver_webhook.delay(str(webhook_log.id))


def sync_to_google_sheets(integration, submission):
    """Sync submission to Google Sheets"""
    config = integration.get_config()
    
    if not config:
        raise Exception("No Google Sheets credentials found")
    
    # Get or create spreadsheet ID from config
    spreadsheet_id = config.get('spreadsheet_id')
    
    if not spreadsheet_id:
        # Create a new spreadsheet
        spreadsheet_id = create_spreadsheet(
            config,
            f"{submission.form.title} - Submissions"
        )
        config['spreadsheet_id'] = spreadsheet_id
        integration.set_config(config)
        integration.save()
    
    # Prepare row data
    form_fields = submission.form.schema_json.get('fields', [])
    headers = ['Submission ID', 'Submitted At', 'IP Address']
    headers.extend([field.get('label', field.get('id')) for field in form_fields])
    
    values = [
        str(submission.id),
        submission.created_at.isoformat(),
        submission.ip_address or ''
    ]
    
    # Add field values
    for field in form_fields:
        field_id = field.get('id')
        value = submission.payload_json.get(field_id, '')
        
        # Convert lists to comma-separated strings
        if isinstance(value, list):
            value = ', '.join(str(v) for v in value)
        
        values.append(str(value))
    
    # Append to sheet
    append_row_to_sheet(config, spreadsheet_id, values)


def sync_to_email(integration, submission):
    """Send email notification for submission"""
    from django.core.mail import send_mail
    from django.conf import settings
    
    config = integration.get_config()
    recipients = config.get('recipients', [])
    
    if not recipients:
        return
    
    subject = f"New submission for {submission.form.title}"
    
    # Build email body
    body_lines = [
        f"Form: {submission.form.title}",
        f"Submitted: {submission.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"IP Address: {submission.ip_address or 'Unknown'}",
        "",
        "Submission Data:",
        "=" * 50,
    ]
    
    form_fields = submission.form.schema_json.get('fields', [])
    for field in form_fields:
        field_id = field.get('id')
        label = field.get('label', field_id)
        value = submission.payload_json.get(field_id, '')
        
        if isinstance(value, list):
            value = ', '.join(str(v) for v in value)
        
        body_lines.append(f"{label}: {value}")
    
    body = "\n".join(body_lines)
    
    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        recipients,
        fail_silently=False,
    )
