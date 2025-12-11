"""
Form scheduling and lifecycle management models
"""
from django.db import models
import uuid


class FormSchedule(models.Model):
    """Schedule when forms go live or expire"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='schedule')
    start_date = models.DateTimeField(null=True, blank=True, help_text="When form becomes active")
    end_date = models.DateTimeField(null=True, blank=True, help_text="When form expires")
    timezone = models.CharField(max_length=100, default='UTC')
    max_submissions = models.IntegerField(
        null=True,
        blank=True,
        help_text="Auto-close form after X submissions"
    )
    auto_archive = models.BooleanField(default=False, help_text="Auto-archive when expired")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    activation_type = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immediate'),
            ('scheduled', 'Scheduled'),
            ('conditional', 'Conditional'),
        ],
        default='scheduled'
    )
    conditional_activation = models.JSONField(
        default=dict,
        blank=True,
        help_text="Conditions for activation (e.g., another form reaching target)"
    )
    notification_settings = models.JSONField(
        default=dict,
        help_text="User notifications for schedule events"
    )
    activated_at = models.DateTimeField(null=True, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'form_schedules'
    
    def __str__(self):
        return f"Schedule for {self.form.title}"


class RecurringForm(models.Model):
    """Configuration for recurring forms (e.g., weekly surveys)"""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template_form = models.ForeignKey(
        'forms.Form',
        on_delete=models.CASCADE,
        related_name='recurring_config',
        help_text="Template form to clone"
    )
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='recurring_forms')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    interval = models.IntegerField(default=1, help_text="Every X days/weeks/months")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True, help_text="When to stop creating forms")
    day_of_week = models.IntegerField(
        null=True,
        blank=True,
        help_text="For weekly: 0=Monday, 6=Sunday"
    )
    day_of_month = models.IntegerField(
        null=True,
        blank=True,
        help_text="For monthly: 1-31"
    )
    timezone = models.CharField(max_length=100, default='UTC')
    auto_publish = models.BooleanField(default=True, help_text="Auto-publish cloned forms")
    naming_pattern = models.CharField(
        max_length=200,
        default='{title} - {date}',
        help_text="Pattern for naming cloned forms"
    )
    is_active = models.BooleanField(default=True)
    last_created_at = models.DateTimeField(null=True, blank=True)
    next_creation_at = models.DateTimeField()
    forms_created_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'recurring_forms'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.template_form.title} - {self.frequency}"


class FormLifecycleEvent(models.Model):
    """Track form lifecycle events for automation and auditing"""
    EVENT_TYPES = [
        ('created', 'Created'),
        ('published', 'Published'),
        ('activated', 'Activated'),
        ('paused', 'Paused'),
        ('expired', 'Expired'),
        ('archived', 'Archived'),
        ('cloned', 'Cloned'),
        ('deleted', 'Deleted'),
        ('submission_limit_reached', 'Submission Limit Reached'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='lifecycle_events')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    triggered_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who triggered the event (if manual)"
    )
    automated = models.BooleanField(default=False, help_text="Whether event was automated")
    metadata = models.JSONField(default=dict, help_text="Additional event context")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'form_lifecycle_events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['form', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.form.title} - {self.event_type}"
