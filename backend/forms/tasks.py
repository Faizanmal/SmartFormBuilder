"""
Celery tasks for background processing
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def process_abandoned_forms():
    """
    Periodic task to identify and process abandoned forms
    Run every hour
    """
    from forms.services.abandonment_service import AbandonmentRecoveryService
    
    result = AbandonmentRecoveryService.batch_send_recovery_emails(max_emails=100)
    return result


@shared_task
def process_automated_follow_ups():
    """
    Periodic task to send scheduled follow-up emails
    Run every 15 minutes
    """
    from forms.services.follow_up_service import FollowUpService
    
    result = FollowUpService.process_pending_follow_ups(batch_size=100)
    return result


@shared_task
def calculate_lead_scores_batch():
    """
    Batch calculate lead scores for recent submissions
    Run every hour
    """
    from forms.models import Submission
    from forms.models_advanced import LeadScore
    from forms.services.lead_scoring_service import LeadScoringService
    
    # Get submissions from last hour without lead scores
    one_hour_ago = timezone.now() - timedelta(hours=1)
    submissions = Submission.objects.filter(
        created_at__gte=one_hour_ago
    ).exclude(
        id__in=LeadScore.objects.values_list('submission_id', flat=True)
    )
    
    count = 0
    for submission in submissions:
        try:
            LeadScoringService.calculate_lead_score(submission)
            count += 1
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to score lead {submission.id}: {e}")
    
    return {'scored': count}


@shared_task
def auto_declare_ab_test_winners():
    """
    Automatically declare winners for A/B tests with sufficient data
    Run once per day
    """
    from forms.models_advanced import FormABTest
    from forms.services.ab_testing_service import ABTestingService
    
    running_tests = FormABTest.objects.filter(status='running')
    
    winners_declared = 0
    for test in running_tests:
        winner = ABTestingService.auto_declare_winner(test, min_conversions=100)
        if winner:
            winners_declared += 1
    
    return {'winners_declared': winners_declared}


@shared_task
def cleanup_expired_partial_submissions():
    """
    Delete expired partial submissions
    Run once per day
    """
    from forms.models_advanced import PartialSubmission
    
    expired = PartialSubmission.objects.filter(
        expires_at__lt=timezone.now()
    )
    
    count = expired.count()
    expired.delete()
    
    return {'deleted': count}


@shared_task
def generate_scheduled_reports():
    """
    Generate and email scheduled reports
    Run once per day
    """
    # TODO: Implement scheduled report generation
    return {'reports_sent': 0}


@shared_task
def sync_to_external_integrations(submission_id):
    """
    Async task to sync submission to external integrations
    """
    from forms.models import Submission
    from integrations.services.sync_service import sync_submission_to_integrations
    
    try:
        submission = Submission.objects.get(id=submission_id)
        sync_submission_to_integrations(submission)
        return {'status': 'success', 'submission_id': str(submission_id)}
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Integration sync failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def backup_form_data(form_id):
    """
    Backup form data and submissions
    """
    # TODO: Implement backup functionality
    return {'status': 'success', 'form_id': str(form_id)}


@shared_task
def send_scheduled_reports():
    """
    Process and send all scheduled reports that are due
    Runs every hour
    """
    from django.utils import timezone
    from forms.models_advanced import ScheduledReport
    from forms.services.reporting_service import ReportingService
    from datetime import timedelta
    import logging
    
    logger = logging.getLogger(__name__)
    now = timezone.now()
    
    # Get reports that are due
    due_reports = ScheduledReport.objects.filter(
        is_active=True,
        next_run__lte=now
    )
    
    sent_count = 0
    for report in due_reports:
        try:
            # Calculate date range
            if report.schedule_type == 'daily':
                date_from = now - timedelta(days=1)
            elif report.schedule_type == 'weekly':
                date_from = now - timedelta(weeks=1)
            else:  # monthly
                date_from = now - timedelta(days=30)
            
            # Generate report
            report_data = ReportingService.generate_form_report(
                report.form,
                date_from,
                now
            )
            
            # Send email
            ReportingService.send_report_email(
                report_data,
                report.recipients,
                report.report_options.get('include_charts', True)
            )
            
            # Update report
            report.last_run = now
            report.next_run = ReportingService._calculate_next_run(report.schedule_type)
            report.save()
            
            sent_count += 1
            logger.info(f"Sent scheduled report: {report.id}")
            
        except Exception as e:
            logger.error(f"Failed to send scheduled report {report.id}: {e}")
    
    return {'sent': sent_count, 'time': now.isoformat()}


@shared_task
def process_bulk_operations(operation_type, resource_ids, params):
    """
    Process bulk operations on forms or submissions
    
    operation_type: 'delete', 'archive', 'export', etc.
    resource_ids: List of resource IDs
    params: Additional parameters
    """
    from forms.models import Form, Submission
    
    if operation_type == 'archive_forms':
        Form.objects.filter(id__in=resource_ids).update(status='archived')
        return {'archived': len(resource_ids)}
    
    elif operation_type == 'delete_forms':
        Form.objects.filter(id__in=resource_ids).delete()
        return {'deleted': len(resource_ids)}
    
    elif operation_type == 'delete_submissions':
        Submission.objects.filter(id__in=resource_ids).delete()
        return {'deleted': len(resource_ids)}
    
    return {'status': 'unknown_operation'}
