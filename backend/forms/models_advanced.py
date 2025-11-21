"""
Advanced models for enhanced form features
"""
from django.db import models
from django.contrib.postgres.fields import ArrayField
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
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='ab_tests')
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


class FormComment(models.Model):
    """Comments and annotations on form fields"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='form_comments')
    field_id = models.CharField(max_length=255, blank=True, help_text="Specific field this comment is about")
    content = models.TextField()
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='resolved_comments')
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'form_comments'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Comment on {self.form.title} by {self.user.email}"


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
    submission = models.ForeignKey('forms.Submission', on_delete=models.CASCADE, related_name='consents')
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
    recipients = ArrayField(models.EmailField(), help_text="Email addresses to send reports to")
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
