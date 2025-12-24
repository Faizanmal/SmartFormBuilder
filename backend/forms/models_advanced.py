"""
Advanced models for enhanced form features
"""
from django.db import models

import uuid


class FormStep(models.Model):
    """Model for multi-step form configuration"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='steps')
    step_number = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    fields = models.JSONField(default=list, help_text="List of field IDs in this step")
    conditional_logic = models.JSONField(default=dict, help_text="Branching logic for this step")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'form_steps'
        ordering = ['step_number']
        unique_together = ['form', 'step_number']
        
    def __str__(self):
        return f"{self.form.title} - Step {self.step_number}"


class PartialSubmission(models.Model):
    """Partial/draft submissions for save & resume functionality"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='partial_submissions')
    email = models.EmailField(help_text="Email for resuming submission")
    payload_json = models.JSONField(default=dict)
    current_step = models.IntegerField(default=1)
    resume_token = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    is_abandoned = models.BooleanField(default=False)
    abandoned_at = models.DateTimeField(null=True, blank=True)
    recovery_email_sent = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(help_text="When this draft expires")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'partial_submissions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['resume_token']),
            models.Index(fields=['form', 'email']),
        ]
        
    def __str__(self):
        return f"Partial submission for {self.form.title}"


class FormABTest(models.Model):
    """A/B testing for form variations"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='ab_tests_advanced')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    variant_a_schema = models.JSONField(help_text="Control variant")
    variant_b_schema = models.JSONField(help_text="Test variant")
    traffic_split = models.IntegerField(default=50, help_text="Percentage for variant B (0-100)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Metrics
    variant_a_views = models.IntegerField(default=0)
    variant_a_submissions = models.IntegerField(default=0)
    variant_b_views = models.IntegerField(default=0)
    variant_b_submissions = models.IntegerField(default=0)
    
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    winner = models.CharField(max_length=10, choices=[('a', 'Variant A'), ('b', 'Variant B')], null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'form_ab_tests'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.form.title} - {self.name}"
    
    @property
    def variant_a_conversion_rate(self):
        if self.variant_a_views == 0:
            return 0
        return round((self.variant_a_submissions / self.variant_a_views) * 100, 2)
    
    @property
    def variant_b_conversion_rate(self):
        if self.variant_b_views == 0:
            return 0
        return round((self.variant_b_submissions / self.variant_b_views) * 100, 2)


class TeamMember(models.Model):
    """Team membership with role-based permissions"""
    
    ROLE_CHOICES = [
        ('viewer', 'Viewer'),
        ('editor', 'Editor'),
        ('admin', 'Admin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey('users.Team', on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    invited_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='sent_invitations')
    invited_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'team_members'
        unique_together = ['team', 'user']
        
    def __str__(self):
        return f"{self.user.email} - {self.team.name} ({self.role})"


class FormShare(models.Model):
    """Sharing settings for forms with granular access control"""
    
    PERMISSION_CHOICES = [
        ('view', 'View Only'),
        ('submit', 'Can Submit'),
        ('edit', 'Can Edit'),
        ('manage', 'Full Management'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='shares')
    shared_with_user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True, related_name='shared_forms')
    shared_with_email = models.EmailField(blank=True, help_text="For sharing with non-users")
    permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default='view')
    share_token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='created_shares')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'form_shares'
        
    def __str__(self):
        recipient = self.shared_with_user.email if self.shared_with_user else self.shared_with_email
        return f"{self.form.title} shared with {recipient}"


class FormAnalytics(models.Model):
    """Detailed analytics and tracking for forms"""
    
    EVENT_TYPE_CHOICES = [
        ('view', 'Form View'),
        ('start', 'Form Started'),
        ('field_focus', 'Field Focused'),
        ('field_blur', 'Field Blurred'),
        ('field_error', 'Field Error'),
        ('step_complete', 'Step Completed'),
        ('abandon', 'Form Abandoned'),
        ('submit', 'Form Submitted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='analytics_events')
    session_id = models.CharField(max_length=255, help_text="Session tracking ID")
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    field_id = models.CharField(max_length=255, blank=True)
    field_label = models.CharField(max_length=255, blank=True)
    step_number = models.IntegerField(null=True, blank=True)
    event_data = models.JSONField(default=dict, help_text="Additional event metadata")
    
    # User context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    device_type = models.CharField(max_length=50, blank=True)  # mobile, tablet, desktop
    browser = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    referrer = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'form_analytics'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['form', '-created_at']),
            models.Index(fields=['session_id']),
        ]
        
    def __str__(self):
        return f"{self.form.title} - {self.event_type}"


class LeadScore(models.Model):
    """Lead scoring based on form responses"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.OneToOneField('forms.Submission', on_delete=models.CASCADE, related_name='lead_score')
    total_score = models.IntegerField(default=0)
    score_breakdown = models.JSONField(default=dict, help_text="Detailed scoring by field")
    quality = models.CharField(
        max_length=20,
        choices=[
            ('cold', 'Cold'),
            ('warm', 'Warm'),
            ('hot', 'Hot'),
            ('qualified', 'Qualified'),
        ],
        default='cold'
    )
    assigned_to = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_leads')
    follow_up_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('contacted', 'Contacted'),
            ('negotiating', 'Negotiating'),
            ('won', 'Won'),
            ('lost', 'Lost'),
        ],
        default='pending'
    )
    notes = models.TextField(blank=True)
    last_contacted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lead_scores'
        ordering = ['-total_score']
        
    def __str__(self):
        return f"Lead {self.submission.id} - Score: {self.total_score}"


class AutomatedFollowUp(models.Model):
    """Automated follow-up sequences"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='follow_ups')
    submission = models.ForeignKey('forms.Submission', on_delete=models.CASCADE, related_name='follow_ups')
    sequence_step = models.IntegerField(help_text="Step number in the sequence")
    send_after_hours = models.IntegerField(help_text="Hours after submission to send")
    subject = models.CharField(max_length=500)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    scheduled_for = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'automated_follow_ups'
        ordering = ['scheduled_for']
        
    def __str__(self):
        return f"Follow-up #{self.sequence_step} for {self.submission.id}"


class WhiteLabelConfig(models.Model):
    """White-label configuration for agencies"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='white_label_config')
    custom_domain = models.CharField(max_length=255, blank=True)
    ssl_certificate = models.TextField(blank=True)
    ssl_key = models.TextField(blank=True)
    
    # Branding
    logo_url = models.URLField(blank=True)
    primary_color = models.CharField(max_length=7, default='#000000')
    secondary_color = models.CharField(max_length=7, default='#ffffff')
    custom_css = models.TextField(blank=True)
    
    # Email branding
    email_from_name = models.CharField(max_length=255, blank=True)
    email_from_address = models.EmailField(blank=True)
    email_footer = models.TextField(blank=True)
    
    # Features
    hide_branding = models.BooleanField(default=False)
    custom_terms_url = models.URLField(blank=True)
    custom_privacy_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'white_label_configs'
        
    def __str__(self):
        return f"White-label for {self.user.email}"


class AuditLog(models.Model):
    """Audit trail for compliance and security"""
    
    ACTION_CHOICES = [
        ('form_create', 'Form Created'),
        ('form_update', 'Form Updated'),
        ('form_delete', 'Form Deleted'),
        ('form_publish', 'Form Published'),
        ('submission_view', 'Submission Viewed'),
        ('submission_export', 'Submissions Exported'),
        ('user_login', 'User Login'),
        ('user_logout', 'User Logout'),
        ('permission_change', 'Permission Changed'),
        ('integration_add', 'Integration Added'),
        ('integration_remove', 'Integration Removed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=50, help_text="e.g., form, submission, user")
    resource_id = models.CharField(max_length=255)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]
        
    def __str__(self):
        return f"{self.user.email if self.user else 'Unknown'} - {self.action}"


class ConsentRecord(models.Model):
    """GDPR consent tracking"""
    
    CONSENT_TYPE_CHOICES = [
        ('marketing', 'Marketing Communications'),
        ('analytics', 'Analytics & Tracking'),
        ('data_processing', 'Data Processing'),
        ('third_party', 'Third-party Sharing'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey('forms.Submission', on_delete=models.CASCADE, related_name='consent_records')
    consent_type = models.CharField(max_length=50, choices=CONSENT_TYPE_CHOICES)
    granted = models.BooleanField(default=False)
    consent_text = models.TextField(help_text="Text of the consent agreement")
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'consent_records'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Consent for {self.submission.id} - {self.consent_type}"


class ConversationalSession(models.Model):
    """Session for conversational/chatbot-style forms"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='conversational_sessions')
    session_token = models.CharField(max_length=255, unique=True)
    conversation_history = models.JSONField(default=list, help_text="List of Q&A pairs")
    collected_data = models.JSONField(default=dict, help_text="Data collected so far")
    current_field_id = models.CharField(max_length=255, blank=True)
    is_complete = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'conversational_sessions'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Conversation: {self.form.title} - {'Complete' if self.is_complete else 'In Progress'}"


class ScheduledReport(models.Model):
    """Scheduled analytics reports"""
    
    SCHEDULE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='scheduled_reports')
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_CHOICES)
    recipients = models.JSONField(default=list, help_text="Email addresses to send reports to")
    report_options = models.JSONField(default=dict, help_text="Chart types, metrics to include, etc.")
    is_active = models.BooleanField(default=True)
    next_run = models.DateTimeField(help_text="When to send next report")
    last_run = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scheduled_reports'
        ordering = ['next_run']
        
    def __str__(self):
        return f"{self.form.title} - {self.schedule_type} report"


# ========================================
# NEW AUTOMATION FEATURES MODELS
# ========================================


class NurturingWorkflow(models.Model):
    """Automated lead nurturing workflow configuration"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('archived', 'Archived'),
    ]
    
    TRIGGER_CHOICES = [
        ('submission', 'Form Submission'),
        ('score_threshold', 'Lead Score Threshold'),
        ('abandonment', 'Form Abandonment'),
        ('time_delay', 'Time After Previous Action'),
        ('webhook', 'External Webhook'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='nurturing_workflows')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    trigger_type = models.CharField(max_length=30, choices=TRIGGER_CHOICES, default='submission')
    trigger_conditions = models.JSONField(default=dict, help_text="Conditions to trigger workflow")
    actions = models.JSONField(default=list, help_text="List of actions in sequence")
    is_active = models.BooleanField(default=False)
    
    # Statistics
    total_triggered = models.IntegerField(default=0)
    total_completed = models.IntegerField(default=0)
    total_failed = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'nurturing_workflows'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Workflow: {self.name} ({self.status})"


class WorkflowExecution(models.Model):
    """Track individual workflow executions"""
    
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('waiting', 'Waiting for delay'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(NurturingWorkflow, on_delete=models.CASCADE, related_name='executions')
    submission = models.ForeignKey('forms.Submission', on_delete=models.CASCADE, null=True, blank=True, related_name='workflow_executions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    current_action_index = models.IntegerField(default=0)
    context_data = models.JSONField(default=dict, help_text="Data passed between actions")
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    next_action_at = models.DateTimeField(null=True, blank=True, help_text="When to execute next action")
    
    class Meta:
        db_table = 'workflow_executions'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['workflow', 'status']),
            models.Index(fields=['next_action_at']),
        ]
        
    def __str__(self):
        return f"Execution of {self.workflow.name} - {self.status}"


class WorkflowActionLog(models.Model):
    """Log each action executed in a workflow"""
    
    ACTION_TYPE_CHOICES = [
        ('send_email', 'Send Email'),
        ('send_sms', 'Send SMS'),
        ('webhook', 'Call Webhook'),
        ('crm_sync', 'Sync to CRM'),
        ('slack_notify', 'Slack Notification'),
        ('assign_lead', 'Assign Lead'),
        ('update_score', 'Update Lead Score'),
        ('add_tag', 'Add Tag'),
        ('delay', 'Delay'),
        ('condition', 'Condition Check'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    execution = models.ForeignKey(WorkflowExecution, on_delete=models.CASCADE, related_name='action_logs')
    action_type = models.CharField(max_length=30, choices=ACTION_TYPE_CHOICES)
    action_config = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ], default='pending')
    result_data = models.JSONField(default=dict, help_text="Response/result from action")
    error_message = models.TextField(blank=True)
    executed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'workflow_action_logs'
        ordering = ['executed_at']
        
    def __str__(self):
        return f"{self.action_type} - {self.status}"


class FormIntegration(models.Model):
    """User-configured integrations from the marketplace"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Setup'),
        ('connected', 'Connected'),
        ('error', 'Connection Error'),
        ('disabled', 'Disabled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='form_integrations')
    integration_id = models.CharField(max_length=100, help_text="ID from marketplace catalog")
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Authentication
    auth_type = models.CharField(max_length=20, choices=[
        ('oauth', 'OAuth 2.0'),
        ('api_key', 'API Key'),
        ('webhook', 'Webhook'),
        ('basic', 'Basic Auth'),
    ], default='api_key')
    credentials = models.JSONField(default=dict, help_text="Encrypted credentials")
    
    # Configuration
    config = models.JSONField(default=dict, help_text="Integration-specific settings")
    field_mapping = models.JSONField(default=dict, help_text="Form field to integration field mapping")
    
    # Sync settings
    sync_on_submit = models.BooleanField(default=True)
    sync_on_update = models.BooleanField(default=False)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_sync_status = models.CharField(max_length=20, blank=True)
    sync_error = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'form_integrations'
        ordering = ['-created_at']
        unique_together = ['form', 'integration_id']
        
    def __str__(self):
        return f"{self.name} for {self.form.title}"


class AlertConfig(models.Model):
    """Configuration for predictive analytics alerts"""
    
    ALERT_TYPE_CHOICES = [
        ('submission_spike', 'Submission Spike'),
        ('submission_drop', 'Submission Drop'),
        ('conversion_drop', 'Conversion Rate Drop'),
        ('abandonment_spike', 'Abandonment Spike'),
        ('score_threshold', 'Lead Score Threshold'),
        ('anomaly', 'Anomaly Detected'),
        ('forecast_target', 'Forecast Target'),
    ]
    
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('slack', 'Slack'),
        ('sms', 'SMS'),
        ('webhook', 'Webhook'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='alert_configs')
    name = models.CharField(max_length=255)
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    
    # Threshold settings
    threshold_value = models.FloatField(default=0, help_text="Threshold to trigger alert")
    threshold_direction = models.CharField(max_length=10, choices=[
        ('above', 'Above'),
        ('below', 'Below'),
        ('change', 'Change'),
    ], default='above')
    comparison_period = models.CharField(max_length=20, default='day', help_text="hour, day, week, month")
    
    # Notification settings
    notification_channels = models.JSONField(default=list, help_text="List of channels: email, slack, sms, webhook")
    notification_emails = models.JSONField(default=list, help_text="List of email addresses")
    slack_webhook = models.URLField(blank=True)
    custom_webhook = models.URLField(blank=True)
    
    # Alert state
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    trigger_count = models.IntegerField(default=0)
    cooldown_minutes = models.IntegerField(default=60, help_text="Minutes between alerts")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'alert_configs'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Alert: {self.name} ({self.alert_type})"


class AlertHistory(models.Model):
    """History of triggered alerts"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert_config = models.ForeignKey(AlertConfig, on_delete=models.CASCADE, related_name='history')
    triggered_value = models.FloatField(help_text="The value that triggered the alert")
    threshold_value = models.FloatField(help_text="The threshold at time of trigger")
    message = models.TextField()
    notifications_sent = models.JSONField(default=list, help_text="List of notification channels used")
    acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'alert_history'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Alert triggered: {self.alert_config.name}"


class VoiceDesignSession(models.Model):
    """Session for voice-activated form design"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='voice_sessions')
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, null=True, blank=True, related_name='voice_sessions')
    
    session_token = models.CharField(max_length=255, unique=True)
    current_schema = models.JSONField(default=dict, help_text="Current form schema being designed")
    command_history = models.JSONField(default=list, help_text="List of voice commands and actions")
    
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'voice_design_sessions'
        ordering = ['-started_at']
        
    def __str__(self):
        return f"Voice session for {self.user.email}"


class ComplianceScan(models.Model):
    """Record of compliance scans performed on forms"""
    
    SCAN_TYPE_CHOICES = [
        ('gdpr', 'GDPR'),
        ('wcag', 'WCAG Accessibility'),
        ('hipaa', 'HIPAA'),
        ('pci', 'PCI-DSS'),
        ('ccpa', 'CCPA'),
        ('full', 'Full Scan'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='compliance_scans')
    scan_type = models.CharField(max_length=20, choices=SCAN_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Results
    overall_score = models.IntegerField(default=0, help_text="0-100 compliance score")
    issues_found = models.IntegerField(default=0)
    issues_fixed = models.IntegerField(default=0)
    scan_results = models.JSONField(default=dict, help_text="Detailed scan results")
    auto_fixes_applied = models.JSONField(default=list, help_text="List of auto-fixes applied")
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'compliance_scans'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.scan_type} scan for {self.form.title} - {self.overall_score}%"


class OptimizationSuggestion(models.Model):
    """AI-generated optimization suggestions for forms"""
    
    CATEGORY_CHOICES = [
        ('conversion', 'Conversion Rate'),
        ('completion', 'Completion Rate'),
        ('abandonment', 'Reduce Abandonment'),
        ('engagement', 'Engagement'),
        ('accessibility', 'Accessibility'),
        ('performance', 'Performance'),
    ]
    
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('applied', 'Applied'),
        ('dismissed', 'Dismissed'),
        ('testing', 'In A/B Test'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='optimization_suggestions')
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    expected_impact = models.CharField(max_length=100, help_text="e.g., '+15% conversion'")
    
    # What to change
    target_field_id = models.CharField(max_length=255, blank=True)
    current_value = models.JSONField(default=dict)
    suggested_value = models.JSONField(default=dict)
    
    # If applied
    applied_at = models.DateTimeField(null=True, blank=True)
    applied_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    # A/B Test reference
    ab_test = models.ForeignKey(FormABTest, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'optimization_suggestions'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Suggestion: {self.title}"


class DailyFormStats(models.Model):
    """Daily aggregated statistics for forms (for predictive analytics)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='daily_stats')
    date = models.DateField()
    
    # Core metrics
    views = models.IntegerField(default=0)
    starts = models.IntegerField(default=0)
    submissions = models.IntegerField(default=0)
    abandons = models.IntegerField(default=0)
    
    # Calculated rates
    conversion_rate = models.FloatField(default=0)
    abandonment_rate = models.FloatField(default=0)
    completion_rate = models.FloatField(default=0)
    
    # Time metrics
    avg_completion_time = models.FloatField(default=0, help_text="Average time in seconds")
    
    # Lead scoring
    avg_lead_score = models.FloatField(default=0)
    hot_leads = models.IntegerField(default=0)
    
    # Device breakdown
    mobile_submissions = models.IntegerField(default=0)
    desktop_submissions = models.IntegerField(default=0)
    tablet_submissions = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'daily_form_stats'
        unique_together = ['form', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['form', '-date']),
        ]
        
    def __str__(self):
        return f"Stats for {self.form.title} on {self.date}"


class GeneratedContent(models.Model):
    """Store AI-generated content for forms"""
    
    CONTENT_TYPE_CHOICES = [
        ('description', 'Form Description'),
        ('thank_you', 'Thank You Message'),
        ('email_template', 'Email Template'),
        ('sms_template', 'SMS Template'),
        ('help_text', 'Field Help Text'),
        ('placeholder', 'Field Placeholder'),
        ('validation_message', 'Validation Message'),
        ('consent_text', 'Consent Text'),
        ('translation', 'Translation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='generated_content')
    content_type = models.CharField(max_length=30, choices=CONTENT_TYPE_CHOICES)
    field_id = models.CharField(max_length=255, blank=True, help_text="If content is for specific field")
    
    content = models.JSONField(help_text="Generated content")
    language = models.CharField(max_length=10, default='en')
    
    # Generation context
    prompt_used = models.TextField(blank=True)
    model_used = models.CharField(max_length=50, default='gpt-4')
    
    # Usage
    is_applied = models.BooleanField(default=False)
    applied_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'generated_content'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.content_type} for {self.form.title}"


class PersonalizationRule(models.Model):
    """Rules for form personalization"""
    
    TRIGGER_CHOICES = [
        ('url_param', 'URL Parameter'),
        ('cookie', 'Cookie Value'),
        ('user_attribute', 'User Attribute'),
        ('crm_data', 'CRM Data'),
        ('time', 'Time-based'),
        ('location', 'Geolocation'),
        ('device', 'Device Type'),
        ('referrer', 'Referrer'),
    ]
    
    ACTION_CHOICES = [
        ('prefill', 'Prefill Field'),
        ('show', 'Show Field'),
        ('hide', 'Hide Field'),
        ('modify_options', 'Modify Options'),
        ('change_text', 'Change Text'),
        ('redirect', 'Redirect'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='personalization_rules')
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text="Higher priority rules run first")
    
    # Trigger configuration
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_CHOICES)
    trigger_config = models.JSONField(default=dict, help_text="Trigger-specific configuration")
    
    # Action configuration
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    action_config = models.JSONField(default=dict, help_text="Action-specific configuration")
    
    # Statistics
    times_triggered = models.IntegerField(default=0)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'personalization_rules'
        ordering = ['-priority', '-created_at']
        
    def __str__(self):
        return f"Rule: {self.name}"
