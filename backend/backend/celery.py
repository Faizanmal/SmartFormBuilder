"""
Celery configuration for SmartFormBuilder
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('smartformbuilder')

# Load config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    # Process abandoned forms every hour
    'process-abandoned-forms': {
        'task': 'forms.tasks.process_abandoned_forms',
        'schedule': crontab(minute=0),  # Every hour on the hour
    },
    # Process automated follow-ups every 15 minutes
    'process-automated-follow-ups': {
        'task': 'forms.tasks.process_automated_follow_ups',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    # Calculate lead scores for new submissions every hour
    'calculate-lead-scores': {
        'task': 'forms.tasks.calculate_lead_scores_batch',
        'schedule': crontab(minute=0),  # Every hour
    },
    # Auto-declare A/B test winners once per day
    'auto-declare-ab-winners': {
        'task': 'forms.tasks.auto_declare_ab_test_winners',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
    # Cleanup expired partial submissions daily
    'cleanup-expired-partials': {
        'task': 'forms.tasks.cleanup_expired_partial_submissions',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    # Send scheduled reports every hour
    'send-scheduled-reports': {
        'task': 'forms.tasks.send_scheduled_reports',
        'schedule': crontab(minute=0),  # Every hour
    },
}

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
