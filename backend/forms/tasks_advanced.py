"""
Celery tasks for automated form scheduling and lifecycle management
"""
from celery import shared_task
from django.utils import timezone


@shared_task
def check_scheduled_forms():
    """Check and activate scheduled forms (runs every 5 minutes)"""
    from forms.services.scheduling_service import SchedulingService
    
    service = SchedulingService()
    result = service.check_and_activate_scheduled_forms()
    return result


@shared_task
def check_expired_forms():
    """Check and expire forms (runs every hour)"""
    from forms.services.scheduling_service import SchedulingService
    
    service = SchedulingService()
    result = service.check_and_expire_forms()
    return result


@shared_task
def process_recurring_forms():
    """Process recurring forms and create new instances (runs daily)"""
    from forms.services.scheduling_service import SchedulingService
    
    service = SchedulingService()
    result = service.process_recurring_forms()
    return result


@shared_task
def check_conditional_activations():
    """Check conditional form activations (runs every 15 minutes)"""
    from forms.services.scheduling_service import SchedulingService
    
    service = SchedulingService()
    result = service.check_conditional_activation()
    return result


@shared_task
def auto_archive_old_forms():
    """Auto-archive inactive forms (runs weekly)"""
    from forms.services.scheduling_service import SchedulingService
    
    service = SchedulingService()
    result = service.auto_archive_old_forms(days_inactive=90)
    return result


@shared_task
def sync_offline_submissions():
    """Sync pending offline submissions (runs every 10 minutes)"""
    from forms.models_mobile import OfflineSubmission
    from forms.models import Submission
    
    pending = OfflineSubmission.objects.filter(status='pending')[:100]
    synced_count = 0
    
    for offline_sub in pending:
        try:
            # Create actual submission
            submission = Submission.objects.create(
                form=offline_sub.form,
                data=offline_sub.submission_data,
                created_at=offline_sub.created_at
            )
            
            offline_sub.status = 'synced'
            offline_sub.synced_submission_id = submission.id
            offline_sub.synced_at = timezone.now()
            offline_sub.save()
            
            synced_count += 1
        except Exception as e:
            offline_sub.status = 'failed'
            offline_sub.sync_error = str(e)
            offline_sub.sync_attempts += 1
            offline_sub.save()
    
    return {'synced': synced_count}


@shared_task
def execute_workflow(workflow_id, trigger_data):
    """Execute integration workflow asynchronously"""
    from forms.services.integration_marketplace_service import IntegrationMarketplaceService
    
    service = IntegrationMarketplaceService()
    result = service.execute_workflow(workflow_id, trigger_data)
    return result


@shared_task
def retry_failed_webhooks():
    """Retry failed webhooks (runs every 30 minutes)"""
    from forms.models_integrations_marketplace import WebhookLog
    from forms.services.integration_marketplace_service import IntegrationMarketplaceService
    from datetime import timedelta
    
    service = IntegrationMarketplaceService()
    
    # Find failed webhooks from last 24 hours
    failed_logs = WebhookLog.objects.filter(
        status_code__gte=400,
        created_at__gte=timezone.now() - timedelta(hours=24),
        retry_attempt__lt=3
    )[:50]
    
    retried = 0
    for log in failed_logs:
        service.retry_webhook(str(log.id))
        retried += 1
    
    return {'retried': retried}


@shared_task
def refresh_oauth_tokens():
    """Refresh expiring OAuth tokens (runs daily)"""
    from forms.models_integrations_marketplace import IntegrationConnection
    from forms.services.integration_marketplace_service import IntegrationMarketplaceService
    from datetime import datetime, timedelta
    
    service = IntegrationMarketplaceService()
    
    # Find connections with tokens expiring in next 24 hours
    expiring = IntegrationConnection.objects.filter(
        oauth_data__expires_at__lte=(datetime.now() + timedelta(hours=24)).isoformat(),
        is_active=True
    )
    
    refreshed = 0
    for connection in expiring:
        result = service.refresh_oauth_token(str(connection.id))
        if result.get('success'):
            refreshed += 1
    
    return {'refreshed': refreshed}


@shared_task
def cleanup_old_edit_sessions():
    """Cleanup inactive edit sessions (runs hourly)"""
    from forms.models_collaboration import FormEditSession
    from datetime import timedelta
    
    cutoff = timezone.now() - timedelta(hours=1)
    
    inactive_sessions = FormEditSession.objects.filter(
        last_activity_at__lt=cutoff,
        is_active=True
    )
    
    count = inactive_sessions.count()
    inactive_sessions.update(is_active=False)
    
    return {'cleaned_up': count}


@shared_task
def send_scheduled_notifications():
    """Send scheduled form notifications (runs every hour)"""
    from forms.services.realtime_service import MobileService
    
    service = MobileService()
    
    # Implementation for scheduled notifications
    # This would check for upcoming form deadlines, reminders, etc.
    
    return {'notifications_sent': 0}


@shared_task
def update_theme_ratings():
    """Recalculate theme ratings (runs daily)"""
    from forms.models_themes import Theme, ThemeRating
    from django.db.models import Avg, Count
    
    themes = Theme.objects.filter(is_public=True)
    updated = 0
    
    for theme in themes:
        ratings = ThemeRating.objects.filter(theme=theme).aggregate(
            avg=Avg('rating'),
            count=Count('id')
        )
        
        theme.rating_average = ratings['avg'] or 0
        theme.rating_count = ratings['count'] or 0
        theme.save()
        updated += 1
    
    return {'themes_updated': updated}
