# Generated migration for advanced form features

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0002_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        # FormStep
        migrations.CreateModel(
            name='FormStep',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('step_number', models.IntegerField()),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('fields', models.JSONField(default=list, help_text='List of field IDs in this step')),
                ('conditional_logic', models.JSONField(default=dict, help_text='Branching logic for this step')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='forms.form')),
            ],
            options={
                'db_table': 'form_steps',
                'ordering': ['step_number'],
            },
        ),
        migrations.AddConstraint(
            model_name='formstep',
            constraint=models.UniqueConstraint(fields=['form', 'step_number'], name='unique_form_step'),
        ),
        
        # PartialSubmission
        migrations.CreateModel(
            name='PartialSubmission',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(help_text='Email for resuming submission', max_length=254)),
                ('payload_json', models.JSONField(default=dict)),
                ('current_step', models.IntegerField(default=1)),
                ('resume_token', models.CharField(max_length=255, unique=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.CharField(blank=True, max_length=500)),
                ('is_abandoned', models.BooleanField(default=False)),
                ('abandoned_at', models.DateTimeField(blank=True, null=True)),
                ('recovery_email_sent', models.BooleanField(default=False)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('expires_at', models.DateTimeField(help_text='When this draft expires')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='partial_submissions', to='forms.form')),
            ],
            options={
                'db_table': 'partial_submissions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='partialsubmission',
            index=models.Index(fields=['resume_token'], name='idx_resume_token'),
        ),
        migrations.AddIndex(
            model_name='partialsubmission',
            index=models.Index(fields=['form', 'email'], name='idx_form_email'),
        ),
        
        # FormABTest
        migrations.CreateModel(
            name='FormABTest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('variant_a_schema', models.JSONField(help_text='Control variant')),
                ('variant_b_schema', models.JSONField(help_text='Test variant')),
                ('traffic_split', models.IntegerField(default=50, help_text='Percentage for variant B (0-100)')),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('running', 'Running'), ('completed', 'Completed'), ('paused', 'Paused')], default='draft', max_length=20)),
                ('variant_a_views', models.IntegerField(default=0)),
                ('variant_a_submissions', models.IntegerField(default=0)),
                ('variant_b_views', models.IntegerField(default=0)),
                ('variant_b_submissions', models.IntegerField(default=0)),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('winner', models.CharField(blank=True, choices=[('a', 'Variant A'), ('b', 'Variant B')], max_length=10, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ab_tests', to='forms.form')),
            ],
            options={
                'db_table': 'form_ab_tests',
                'ordering': ['-created_at'],
            },
        ),
        
        # TeamMember
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('role', models.CharField(choices=[('viewer', 'Viewer'), ('editor', 'Editor'), ('admin', 'Admin')], default='viewer', max_length=20)),
                ('invited_at', models.DateTimeField(auto_now_add=True)),
                ('invited_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sent_invitations', to='users.user')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='users.team')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_memberships', to='users.user')),
            ],
            options={
                'db_table': 'team_members',
            },
        ),
        migrations.AddConstraint(
            model_name='teammember',
            constraint=models.UniqueConstraint(fields=['team', 'user'], name='unique_team_member'),
        ),
        
        # FormComment
        migrations.CreateModel(
            name='FormComment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('field_id', models.CharField(blank=True, help_text='Specific field this comment is about', max_length=255)),
                ('content', models.TextField()),
                ('resolved', models.BooleanField(default=False)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='forms.form')),
                ('resolved_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resolved_comments', to='users.user')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='form_comments', to='users.user')),
            ],
            options={
                'db_table': 'form_comments',
                'ordering': ['-created_at'],
            },
        ),
        
        # FormShare
        migrations.CreateModel(
            name='FormShare',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('shared_with_email', models.EmailField(blank=True, help_text='For sharing with non-users', max_length=254)),
                ('permission', models.CharField(choices=[('view', 'View Only'), ('submit', 'Can Submit'), ('edit', 'Can Edit'), ('manage', 'Full Management')], default='view', max_length=20)),
                ('share_token', models.CharField(max_length=255, unique=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_shares', to='users.user')),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shares', to='forms.form')),
                ('shared_with_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shared_forms', to='users.user')),
            ],
            options={
                'db_table': 'form_shares',
            },
        ),
        
        # FormAnalytics
        migrations.CreateModel(
            name='FormAnalytics',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('session_id', models.CharField(help_text='Session tracking ID', max_length=255)),
                ('event_type', models.CharField(choices=[('view', 'Form View'), ('start', 'Form Started'), ('field_focus', 'Field Focused'), ('field_blur', 'Field Blurred'), ('field_error', 'Field Error'), ('step_complete', 'Step Completed'), ('abandon', 'Form Abandoned'), ('submit', 'Form Submitted')], max_length=20)),
                ('field_id', models.CharField(blank=True, max_length=255)),
                ('field_label', models.CharField(blank=True, max_length=255)),
                ('step_number', models.IntegerField(blank=True, null=True)),
                ('event_data', models.JSONField(default=dict, help_text='Additional event metadata')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.CharField(blank=True, max_length=500)),
                ('device_type', models.CharField(blank=True, max_length=50)),
                ('browser', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('referrer', models.URLField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analytics_events', to='forms.form')),
            ],
            options={
                'db_table': 'form_analytics',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='formanalytics',
            index=models.Index(fields=['form', '-created_at'], name='idx_form_created'),
        ),
        migrations.AddIndex(
            model_name='formanalytics',
            index=models.Index(fields=['session_id'], name='idx_session_id'),
        ),
        
        # LeadScore
        migrations.CreateModel(
            name='LeadScore',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('total_score', models.IntegerField(default=0)),
                ('score_breakdown', models.JSONField(default=dict, help_text='Detailed scoring by field')),
                ('quality', models.CharField(choices=[('cold', 'Cold'), ('warm', 'Warm'), ('hot', 'Hot'), ('qualified', 'Qualified')], default='cold', max_length=20)),
                ('follow_up_status', models.CharField(choices=[('pending', 'Pending'), ('contacted', 'Contacted'), ('negotiating', 'Negotiating'), ('won', 'Won'), ('lost', 'Lost')], default='pending', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('last_contacted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_leads', to='users.user')),
                ('submission', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='lead_score', to='forms.submission')),
            ],
            options={
                'db_table': 'lead_scores',
                'ordering': ['-total_score'],
            },
        ),
        
        # AutomatedFollowUp
        migrations.CreateModel(
            name='AutomatedFollowUp',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('sequence_step', models.IntegerField(help_text='Step number in the sequence')),
                ('send_after_hours', models.IntegerField(help_text='Hours after submission to send')),
                ('subject', models.CharField(max_length=500)),
                ('content', models.TextField()),
                ('status', models.CharField(choices=[('scheduled', 'Scheduled'), ('sent', 'Sent'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='scheduled', max_length=20)),
                ('scheduled_for', models.DateTimeField()),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('error_message', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follow_ups', to='forms.form')),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follow_ups', to='forms.submission')),
            ],
            options={
                'db_table': 'automated_follow_ups',
                'ordering': ['scheduled_for'],
            },
        ),
        
        # WhiteLabelConfig
        migrations.CreateModel(
            name='WhiteLabelConfig',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('custom_domain', models.CharField(blank=True, max_length=255)),
                ('ssl_certificate', models.TextField(blank=True)),
                ('ssl_key', models.TextField(blank=True)),
                ('logo_url', models.URLField(blank=True)),
                ('primary_color', models.CharField(default='#000000', max_length=7)),
                ('secondary_color', models.CharField(default='#ffffff', max_length=7)),
                ('custom_css', models.TextField(blank=True)),
                ('email_from_name', models.CharField(blank=True, max_length=255)),
                ('email_from_address', models.EmailField(blank=True, max_length=254)),
                ('email_footer', models.TextField(blank=True)),
                ('hide_branding', models.BooleanField(default=False)),
                ('custom_terms_url', models.URLField(blank=True)),
                ('custom_privacy_url', models.URLField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='white_label_config', to='users.user')),
            ],
            options={
                'db_table': 'white_label_configs',
            },
        ),
        
        # AuditLog
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action', models.CharField(choices=[('form_create', 'Form Created'), ('form_update', 'Form Updated'), ('form_delete', 'Form Deleted'), ('form_publish', 'Form Published'), ('submission_view', 'Submission Viewed'), ('submission_export', 'Submissions Exported'), ('user_login', 'User Login'), ('user_logout', 'User Logout'), ('permission_change', 'Permission Changed'), ('integration_add', 'Integration Added'), ('integration_remove', 'Integration Removed')], max_length=50)),
                ('resource_type', models.CharField(help_text='e.g., form, submission, user', max_length=50)),
                ('resource_id', models.CharField(max_length=255)),
                ('details', models.JSONField(default=dict)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.CharField(blank=True, max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs', to='users.user')),
            ],
            options={
                'db_table': 'audit_logs',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['user', '-created_at'], name='idx_user_created'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['resource_type', 'resource_id'], name='idx_resource'),
        ),
        
        # ConsentRecord
        migrations.CreateModel(
            name='ConsentRecord',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('consent_type', models.CharField(choices=[('marketing', 'Marketing Communications'), ('analytics', 'Analytics & Tracking'), ('data_processing', 'Data Processing'), ('third_party', 'Third-party Sharing')], max_length=50)),
                ('granted', models.BooleanField(default=False)),
                ('consent_text', models.TextField(help_text='Text of the consent agreement')),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.CharField(max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('revoked_at', models.DateTimeField(blank=True, null=True)),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consents', to='forms.submission')),
            ],
            options={
                'db_table': 'consent_records',
                'ordering': ['-created_at'],
            },
        ),
    ]
