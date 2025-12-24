# Generated migration for automation features

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forms', '0005_formdraft_formvariant_abtest'),
    ]

    operations = [
        # Nurturing Workflow
        migrations.CreateModel(
            name='NurturingWorkflow',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('active', 'Active'), ('paused', 'Paused'), ('archived', 'Archived')], default='draft', max_length=20)),
                ('trigger_type', models.CharField(choices=[('submission', 'Form Submission'), ('score_threshold', 'Lead Score Threshold'), ('abandonment', 'Form Abandonment'), ('time_delay', 'Time After Previous Action'), ('webhook', 'External Webhook')], default='submission', max_length=30)),
                ('trigger_conditions', models.JSONField(default=dict, help_text='Conditions to trigger workflow')),
                ('actions', models.JSONField(default=list, help_text='List of actions in sequence')),
                ('is_active', models.BooleanField(default=False)),
                ('total_triggered', models.IntegerField(default=0)),
                ('total_completed', models.IntegerField(default=0)),
                ('total_failed', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nurturing_workflows', to='forms.form')),
            ],
            options={
                'db_table': 'nurturing_workflows',
                'ordering': ['-created_at'],
            },
        ),
        
        # Workflow Execution
        migrations.CreateModel(
            name='WorkflowExecution',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled'), ('waiting', 'Waiting for delay')], default='running', max_length=20)),
                ('current_action_index', models.IntegerField(default=0)),
                ('context_data', models.JSONField(default=dict, help_text='Data passed between actions')),
                ('error_message', models.TextField(blank=True)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('next_action_at', models.DateTimeField(blank=True, help_text='When to execute next action', null=True)),
                ('workflow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='executions', to='forms.nurturingworkflow')),
                ('submission', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='workflow_executions', to='forms.submission')),
            ],
            options={
                'db_table': 'workflow_executions',
                'ordering': ['-started_at'],
            },
        ),
        migrations.AddIndex(
            model_name='workflowexecution',
            index=models.Index(fields=['workflow', 'status'], name='workflow_ex_workflo_idx'),
        ),
        migrations.AddIndex(
            model_name='workflowexecution',
            index=models.Index(fields=['next_action_at'], name='workflow_ex_next_ac_idx'),
        ),
        
        # Workflow Action Log
        migrations.CreateModel(
            name='WorkflowActionLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action_type', models.CharField(choices=[('send_email', 'Send Email'), ('send_sms', 'Send SMS'), ('webhook', 'Call Webhook'), ('crm_sync', 'Sync to CRM'), ('slack_notify', 'Slack Notification'), ('assign_lead', 'Assign Lead'), ('update_score', 'Update Lead Score'), ('add_tag', 'Add Tag'), ('delay', 'Delay'), ('condition', 'Condition Check')], max_length=30)),
                ('action_config', models.JSONField(default=dict)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed'), ('skipped', 'Skipped')], default='pending', max_length=20)),
                ('result_data', models.JSONField(default=dict, help_text='Response/result from action')),
                ('error_message', models.TextField(blank=True)),
                ('executed_at', models.DateTimeField(auto_now_add=True)),
                ('execution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='action_logs', to='forms.workflowexecution')),
            ],
            options={
                'db_table': 'workflow_action_logs',
                'ordering': ['executed_at'],
            },
        ),
        
        # Form Integration
        migrations.CreateModel(
            name='FormIntegration',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('integration_id', models.CharField(help_text='ID from marketplace catalog', max_length=100)),
                ('name', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('pending', 'Pending Setup'), ('connected', 'Connected'), ('error', 'Connection Error'), ('disabled', 'Disabled')], default='pending', max_length=20)),
                ('auth_type', models.CharField(choices=[('oauth', 'OAuth 2.0'), ('api_key', 'API Key'), ('webhook', 'Webhook'), ('basic', 'Basic Auth')], default='api_key', max_length=20)),
                ('credentials', models.JSONField(default=dict, help_text='Encrypted credentials')),
                ('config', models.JSONField(default=dict, help_text='Integration-specific settings')),
                ('field_mapping', models.JSONField(default=dict, help_text='Form field to integration field mapping')),
                ('sync_on_submit', models.BooleanField(default=True)),
                ('sync_on_update', models.BooleanField(default=False)),
                ('last_sync_at', models.DateTimeField(blank=True, null=True)),
                ('last_sync_status', models.CharField(blank=True, max_length=20)),
                ('sync_error', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='integrations', to='forms.form')),
            ],
            options={
                'db_table': 'form_integrations',
                'ordering': ['-created_at'],
                'unique_together': {('form', 'integration_id')},
            },
        ),
        
        # Alert Config
        migrations.CreateModel(
            name='AlertConfig',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('alert_type', models.CharField(choices=[('submission_spike', 'Submission Spike'), ('submission_drop', 'Submission Drop'), ('conversion_drop', 'Conversion Rate Drop'), ('abandonment_spike', 'Abandonment Spike'), ('score_threshold', 'Lead Score Threshold'), ('anomaly', 'Anomaly Detected'), ('forecast_target', 'Forecast Target')], max_length=30)),
                ('is_active', models.BooleanField(default=True)),
                ('threshold_value', models.FloatField(default=0, help_text='Threshold to trigger alert')),
                ('threshold_direction', models.CharField(choices=[('above', 'Above'), ('below', 'Below'), ('change', 'Change')], default='above', max_length=10)),
                ('comparison_period', models.CharField(default='day', help_text='hour, day, week, month', max_length=20)),
                ('notification_channels', models.JSONField(default=list, help_text='List of channels: email, slack, sms, webhook')),
                ('notification_emails', models.JSONField(default=list, help_text='List of email addresses')),
                ('slack_webhook', models.URLField(blank=True)),
                ('custom_webhook', models.URLField(blank=True)),
                ('last_triggered_at', models.DateTimeField(blank=True, null=True)),
                ('trigger_count', models.IntegerField(default=0)),
                ('cooldown_minutes', models.IntegerField(default=60, help_text='Minutes between alerts')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alert_configs', to='forms.form')),
            ],
            options={
                'db_table': 'alert_configs',
                'ordering': ['-created_at'],
            },
        ),
        
        # Alert History
        migrations.CreateModel(
            name='AlertHistory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('triggered_value', models.FloatField(help_text='The value that triggered the alert')),
                ('threshold_value', models.FloatField(help_text='The threshold at time of trigger')),
                ('message', models.TextField()),
                ('notifications_sent', models.JSONField(default=list, help_text='List of notification channels used')),
                ('acknowledged', models.BooleanField(default=False)),
                ('acknowledged_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('alert_config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='forms.alertconfig')),
                ('acknowledged_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'alert_history',
                'ordering': ['-created_at'],
            },
        ),
        
        # Voice Design Session
        migrations.CreateModel(
            name='VoiceDesignSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('session_token', models.CharField(max_length=255, unique=True)),
                ('current_schema', models.JSONField(default=dict, help_text='Current form schema being designed')),
                ('command_history', models.JSONField(default=list, help_text='List of voice commands and actions')),
                ('is_active', models.BooleanField(default=True)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('last_activity_at', models.DateTimeField(auto_now=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='voice_sessions', to=settings.AUTH_USER_MODEL)),
                ('form', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='voice_sessions', to='forms.form')),
            ],
            options={
                'db_table': 'voice_design_sessions',
                'ordering': ['-started_at'],
            },
        ),
        
        # Compliance Scan
        migrations.CreateModel(
            name='ComplianceScan',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('scan_type', models.CharField(choices=[('gdpr', 'GDPR'), ('wcag', 'WCAG Accessibility'), ('hipaa', 'HIPAA'), ('pci', 'PCI-DSS'), ('ccpa', 'CCPA'), ('full', 'Full Scan')], max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('overall_score', models.IntegerField(default=0, help_text='0-100 compliance score')),
                ('issues_found', models.IntegerField(default=0)),
                ('issues_fixed', models.IntegerField(default=0)),
                ('scan_results', models.JSONField(default=dict, help_text='Detailed scan results')),
                ('auto_fixes_applied', models.JSONField(default=list, help_text='List of auto-fixes applied')),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='compliance_scans', to='forms.form')),
            ],
            options={
                'db_table': 'compliance_scans',
                'ordering': ['-created_at'],
            },
        ),
        
        # Optimization Suggestion
        migrations.CreateModel(
            name='OptimizationSuggestion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('category', models.CharField(choices=[('conversion', 'Conversion Rate'), ('completion', 'Completion Rate'), ('abandonment', 'Reduce Abandonment'), ('engagement', 'Engagement'), ('accessibility', 'Accessibility'), ('performance', 'Performance')], max_length=20)),
                ('priority', models.CharField(choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], default='medium', max_length=10)),
                ('status', models.CharField(choices=[('pending', 'Pending Review'), ('applied', 'Applied'), ('dismissed', 'Dismissed'), ('testing', 'In A/B Test')], default='pending', max_length=20)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('expected_impact', models.CharField(help_text="e.g., '+15% conversion'", max_length=100)),
                ('target_field_id', models.CharField(blank=True, max_length=255)),
                ('current_value', models.JSONField(default=dict)),
                ('suggested_value', models.JSONField(default=dict)),
                ('applied_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='optimization_suggestions', to='forms.form')),
                ('applied_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('ab_test', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='forms.formabtest')),
            ],
            options={
                'db_table': 'optimization_suggestions',
                'ordering': ['-created_at'],
            },
        ),
        
        # Daily Form Stats
        migrations.CreateModel(
            name='DailyFormStats',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('views', models.IntegerField(default=0)),
                ('starts', models.IntegerField(default=0)),
                ('submissions', models.IntegerField(default=0)),
                ('abandons', models.IntegerField(default=0)),
                ('conversion_rate', models.FloatField(default=0)),
                ('abandonment_rate', models.FloatField(default=0)),
                ('completion_rate', models.FloatField(default=0)),
                ('avg_completion_time', models.FloatField(default=0, help_text='Average time in seconds')),
                ('avg_lead_score', models.FloatField(default=0)),
                ('hot_leads', models.IntegerField(default=0)),
                ('mobile_submissions', models.IntegerField(default=0)),
                ('desktop_submissions', models.IntegerField(default=0)),
                ('tablet_submissions', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_stats', to='forms.form')),
            ],
            options={
                'db_table': 'daily_form_stats',
                'ordering': ['-date'],
                'unique_together': {('form', 'date')},
            },
        ),
        migrations.AddIndex(
            model_name='dailyformstats',
            index=models.Index(fields=['form', '-date'], name='daily_form__form_id_idx'),
        ),
        
        # Generated Content
        migrations.CreateModel(
            name='GeneratedContent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('content_type', models.CharField(choices=[('description', 'Form Description'), ('thank_you', 'Thank You Message'), ('email_template', 'Email Template'), ('sms_template', 'SMS Template'), ('help_text', 'Field Help Text'), ('placeholder', 'Field Placeholder'), ('validation_message', 'Validation Message'), ('consent_text', 'Consent Text'), ('translation', 'Translation')], max_length=30)),
                ('field_id', models.CharField(blank=True, help_text='If content is for specific field', max_length=255)),
                ('content', models.JSONField(help_text='Generated content')),
                ('language', models.CharField(default='en', max_length=10)),
                ('prompt_used', models.TextField(blank=True)),
                ('model_used', models.CharField(default='gpt-4', max_length=50)),
                ('is_applied', models.BooleanField(default=False)),
                ('applied_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='generated_content', to='forms.form')),
            ],
            options={
                'db_table': 'generated_content',
                'ordering': ['-created_at'],
            },
        ),
        
        # Personalization Rule
        migrations.CreateModel(
            name='PersonalizationRule',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('priority', models.IntegerField(default=0, help_text='Higher priority rules run first')),
                ('trigger_type', models.CharField(choices=[('url_param', 'URL Parameter'), ('cookie', 'Cookie Value'), ('user_attribute', 'User Attribute'), ('crm_data', 'CRM Data'), ('time', 'Time-based'), ('location', 'Geolocation'), ('device', 'Device Type'), ('referrer', 'Referrer')], max_length=20)),
                ('trigger_config', models.JSONField(default=dict, help_text='Trigger-specific configuration')),
                ('action_type', models.CharField(choices=[('prefill', 'Prefill Field'), ('show', 'Show Field'), ('hide', 'Hide Field'), ('modify_options', 'Modify Options'), ('change_text', 'Change Text'), ('redirect', 'Redirect')], max_length=20)),
                ('action_config', models.JSONField(default=dict, help_text='Action-specific configuration')),
                ('times_triggered', models.IntegerField(default=0)),
                ('last_triggered_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='personalization_rules', to='forms.form')),
            ],
            options={
                'db_table': 'personalization_rules',
                'ordering': ['-priority', '-created_at'],
            },
        ),
    ]
