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


# ========================================
# AUTOMATION FEATURE TASKS
# ========================================

@shared_task
def process_workflow_executions():
    """
    Process pending workflow executions
    Run every minute
    """
    from forms.models_advanced import WorkflowExecution, WorkflowActionLog
    from forms.services.workflow_service import WorkflowService
    import logging
    
    logger = logging.getLogger(__name__)
    now = timezone.now()
    
    # Get executions ready to process
    ready_executions = WorkflowExecution.objects.filter(
        status='waiting',
        next_action_at__lte=now
    )
    
    processed = 0
    for execution in ready_executions:
        try:
            service = WorkflowService()
            
            # Get current action
            actions = execution.workflow.actions
            if execution.current_action_index >= len(actions):
                execution.status = 'completed'
                execution.completed_at = now
                execution.save()
                continue
            
            action = actions[execution.current_action_index]
            
            # Execute action
            result = service._execute_action(action, execution.context_data)
            
            # Log action
            WorkflowActionLog.objects.create(
                execution=execution,
                action_type=action.get('type'),
                action_config=action,
                status='success' if result.get('success') else 'failed',
                result_data=result,
                error_message=result.get('error', ''),
            )
            
            # Move to next action
            execution.current_action_index += 1
            
            # Check for delay on next action
            if execution.current_action_index < len(actions):
                next_action = actions[execution.current_action_index]
                delay = next_action.get('delay_minutes', 0)
                if delay > 0:
                    execution.next_action_at = now + timedelta(minutes=delay)
                else:
                    execution.next_action_at = now
            else:
                execution.status = 'completed'
                execution.completed_at = now
                
                # Update workflow stats
                execution.workflow.total_completed += 1
                execution.workflow.save()
            
            execution.save()
            processed += 1
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {execution.id} - {e}")
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.save()
            
            execution.workflow.total_failed += 1
            execution.workflow.save()
    
    return {'processed': processed}


@shared_task
def trigger_workflows_on_submission(submission_id):
    """
    Trigger workflows when a submission is created
    """
    from forms.models import Submission
    from forms.models_advanced import NurturingWorkflow, WorkflowExecution
    from forms.services.workflow_service import WorkflowService
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        submission = Submission.objects.get(id=submission_id)
        
        # Find active workflows for this form
        workflows = NurturingWorkflow.objects.filter(
            form=submission.form,
            is_active=True,
            trigger_type='submission'
        )
        
        service = WorkflowService()
        triggered = 0
        
        for workflow in workflows:
            # Check trigger conditions
            conditions = workflow.trigger_conditions
            if service._check_conditions(conditions, submission.payload_json):
                # Create execution
                execution = WorkflowExecution.objects.create(
                    workflow=workflow,
                    submission=submission,
                    context_data=submission.payload_json,
                    next_action_at=timezone.now(),
                )
                
                workflow.total_triggered += 1
                workflow.save()
                
                triggered += 1
                logger.info(f"Triggered workflow {workflow.id} for submission {submission_id}")
        
        return {'triggered': triggered}
        
    except Submission.DoesNotExist:
        return {'error': 'Submission not found'}
    except Exception as e:
        logger.error(f"Failed to trigger workflows: {e}")
        return {'error': str(e)}


@shared_task
def check_alert_conditions():
    """
    Check all active alerts and trigger notifications if conditions are met
    Run every 15 minutes
    """
    from forms.models_advanced import AlertConfig, AlertHistory
    from forms.services.predictive_analytics_service import PredictiveAnalyticsService
    import logging
    import requests
    from django.core.mail import send_mail
    
    logger = logging.getLogger(__name__)
    now = timezone.now()
    
    alerts = AlertConfig.objects.filter(is_active=True)
    triggered_count = 0
    
    for alert in alerts:
        try:
            # Check cooldown
            if alert.last_triggered_at:
                cooldown_end = alert.last_triggered_at + timedelta(minutes=alert.cooldown_minutes)
                if now < cooldown_end:
                    continue
            
            # Get current metric value
            service = PredictiveAnalyticsService()
            current_value = service._get_metric_value(
                alert.form_id,
                alert.alert_type,
                alert.comparison_period
            )
            
            # Check threshold
            should_trigger = False
            if alert.threshold_direction == 'above':
                should_trigger = current_value > alert.threshold_value
            elif alert.threshold_direction == 'below':
                should_trigger = current_value < alert.threshold_value
            else:  # change
                should_trigger = abs(current_value) > alert.threshold_value
            
            if should_trigger:
                # Create alert history
                message = f"Alert: {alert.name} - {alert.alert_type} is {current_value} ({alert.threshold_direction} {alert.threshold_value})"
                
                history = AlertHistory.objects.create(
                    alert_config=alert,
                    triggered_value=current_value,
                    threshold_value=alert.threshold_value,
                    message=message,
                )
                
                # Send notifications
                notifications_sent = []
                
                if 'email' in alert.notification_channels and alert.notification_emails:
                    try:
                        send_mail(
                            subject=f"Alert: {alert.name}",
                            message=message,
                            from_email='alerts@smartformbuilder.com',
                            recipient_list=alert.notification_emails,
                        )
                        notifications_sent.append('email')
                    except:
                        pass
                
                if 'slack' in alert.notification_channels and alert.slack_webhook:
                    try:
                        requests.post(alert.slack_webhook, json={'text': message})
                        notifications_sent.append('slack')
                    except:
                        pass
                
                if 'webhook' in alert.notification_channels and alert.custom_webhook:
                    try:
                        requests.post(alert.custom_webhook, json={
                            'alert_name': alert.name,
                            'alert_type': alert.alert_type,
                            'value': current_value,
                            'threshold': alert.threshold_value,
                            'message': message,
                        })
                        notifications_sent.append('webhook')
                    except:
                        pass
                
                history.notifications_sent = notifications_sent
                history.save()
                
                # Update alert
                alert.last_triggered_at = now
                alert.trigger_count += 1
                alert.save()
                
                triggered_count += 1
                logger.info(f"Alert triggered: {alert.name}")
                
        except Exception as e:
            logger.error(f"Failed to check alert {alert.id}: {e}")
    
    return {'alerts_triggered': triggered_count}


@shared_task
def aggregate_daily_stats():
    """
    Aggregate daily statistics for all forms
    Run once per day at midnight
    """
    from forms.models import Form, Submission
    from forms.models_advanced import DailyFormStats, FormAnalytics, LeadScore
    from django.db.models import Avg
    import logging
    
    logger = logging.getLogger(__name__)
    yesterday = (timezone.now() - timedelta(days=1)).date()
    
    forms = Form.objects.filter(status='published')
    created = 0
    
    for form in forms:
        try:
            # Get analytics events
            events = FormAnalytics.objects.filter(
                form=form,
                created_at__date=yesterday
            )
            
            views = events.filter(event_type='view').count()
            starts = events.filter(event_type='start').count()
            abandons = events.filter(event_type='abandon').count()
            
            # Get submissions
            submissions = Submission.objects.filter(
                form=form,
                created_at__date=yesterday
            )
            submission_count = submissions.count()
            
            # Device breakdown
            desktop = submissions.filter(device_type='desktop').count() if hasattr(Submission, 'device_type') else 0
            mobile = submissions.filter(device_type='mobile').count() if hasattr(Submission, 'device_type') else 0
            tablet = submissions.filter(device_type='tablet').count() if hasattr(Submission, 'device_type') else 0
            
            # Calculate rates
            conversion_rate = (submission_count / views * 100) if views > 0 else 0
            abandonment_rate = (abandons / starts * 100) if starts > 0 else 0
            completion_rate = (submission_count / starts * 100) if starts > 0 else 0
            
            # Lead scores
            lead_scores = LeadScore.objects.filter(submission__in=submissions)
            avg_score = lead_scores.aggregate(avg=Avg('total_score'))['avg'] or 0
            hot_leads = lead_scores.filter(quality='hot').count()
            
            # Create or update stats
            DailyFormStats.objects.update_or_create(
                form=form,
                date=yesterday,
                defaults={
                    'views': views,
                    'starts': starts,
                    'submissions': submission_count,
                    'abandons': abandons,
                    'conversion_rate': round(conversion_rate, 2),
                    'abandonment_rate': round(abandonment_rate, 2),
                    'completion_rate': round(completion_rate, 2),
                    'avg_lead_score': round(avg_score, 2),
                    'hot_leads': hot_leads,
                    'mobile_submissions': mobile,
                    'desktop_submissions': desktop,
                    'tablet_submissions': tablet,
                }
            )
            created += 1
            
        except Exception as e:
            logger.error(f"Failed to aggregate stats for form {form.id}: {e}")
    
    return {'forms_processed': created, 'date': str(yesterday)}


@shared_task
def generate_optimization_suggestions_batch():
    """
    Generate optimization suggestions for all active forms
    Run once per week
    """
    from forms.models import Form
    from forms.models_advanced import OptimizationSuggestion
    from forms.services.optimization_service import FormOptimizationService
    import logging
    
    logger = logging.getLogger(__name__)
    service = FormOptimizationService()
    
    forms = Form.objects.filter(status='published')
    suggestions_created = 0
    
    for form in forms:
        try:
            # Generate suggestions
            suggestions = service.generate_optimization_suggestions(form.id)
            
            for suggestion in suggestions:
                # Check if similar suggestion exists
                exists = OptimizationSuggestion.objects.filter(
                    form=form,
                    title=suggestion.get('title'),
                    status='pending'
                ).exists()
                
                if not exists:
                    OptimizationSuggestion.objects.create(
                        form=form,
                        category=suggestion.get('category', 'conversion'),
                        priority=suggestion.get('priority', 'medium'),
                        title=suggestion.get('title'),
                        description=suggestion.get('description'),
                        expected_impact=suggestion.get('expected_impact'),
                        target_field_id=suggestion.get('field_id', ''),
                        current_value=suggestion.get('current_value', {}),
                        suggested_value=suggestion.get('suggested_value', {}),
                    )
                    suggestions_created += 1
                    
        except Exception as e:
            logger.error(f"Failed to generate suggestions for form {form.id}: {e}")
    
    return {'suggestions_created': suggestions_created}


@shared_task
def sync_integration(integration_id, submission_id):
    """
    Sync a submission to an integration
    """
    from forms.models import Submission
    from forms.models_advanced import FormIntegration
    from forms.services.marketplace_service import IntegrationMarketplaceService
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        integration = FormIntegration.objects.get(id=integration_id)
        submission = Submission.objects.get(id=submission_id)
        
        service = IntegrationMarketplaceService()
        result = service.sync_to_integration(
            integration.integration_id,
            integration.credentials,
            submission.payload_json,
            integration.field_mapping
        )
        
        # Update integration status
        integration.last_sync_at = timezone.now()
        integration.last_sync_status = 'success' if result.get('success') else 'error'
        integration.sync_error = result.get('error', '')
        integration.save()
        
        return result
        
    except Exception as e:
        logger.error(f"Integration sync failed: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def cleanup_old_voice_sessions():
    """
    Clean up inactive voice design sessions
    Run once per day
    """
    from forms.models_advanced import VoiceDesignSession
    
    # Sessions inactive for more than 24 hours
    cutoff = timezone.now() - timedelta(hours=24)
    
    inactive_sessions = VoiceDesignSession.objects.filter(
        is_active=True,
        last_activity_at__lt=cutoff
    )
    
    count = inactive_sessions.count()
    inactive_sessions.update(
        is_active=False,
        ended_at=timezone.now()
    )
    
    return {'closed_sessions': count}


@shared_task
def run_compliance_scans_batch():
    """
    Run compliance scans on all published forms
    Run once per month
    """
    from forms.models import Form
    from forms.models_advanced import ComplianceScan
    from forms.services.compliance_service import ComplianceService
    import logging
    
    logger = logging.getLogger(__name__)
    service = ComplianceService()
    
    forms = Form.objects.filter(status='published')
    scans_created = 0
    
    for form in forms:
        try:
            # Run scan
            result = service.scan_form(form.schema, ['gdpr', 'wcag'])
            
            # Create scan record
            ComplianceScan.objects.create(
                form=form,
                scan_type='full',
                status='completed',
                overall_score=result.get('overall_score', 0),
                issues_found=result.get('total_issues', 0),
                scan_results=result,
                started_at=timezone.now(),
                completed_at=timezone.now(),
            )
            scans_created += 1
            
        except Exception as e:
            logger.error(f"Failed to scan form {form.id}: {e}")
    
    return {'scans_completed': scans_created}
