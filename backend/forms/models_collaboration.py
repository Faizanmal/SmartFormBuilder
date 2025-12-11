"""
Collaborative real-time form editing models
"""
from django.db import models
import uuid


class FormCollaborator(models.Model):
    """Users who can collaborate on a form"""
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('editor', 'Editor'),
        ('reviewer', 'Reviewer'),
        ('viewer', 'Viewer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='collaborators')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='collaborative_forms')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    permissions = models.JSONField(
        default=dict,
        help_text="Granular permissions (edit_fields, edit_settings, publish, etc.)"
    )
    invited_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invited_collaborators'
    )
    invitation_accepted = models.BooleanField(default=False)
    last_active_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'form_collaborators'
        unique_together = [['form', 'user']]
    
    def __str__(self):
        return f"{self.user.email} - {self.form.title} ({self.role})"


class FormEditSession(models.Model):
    """Active editing sessions for real-time collaboration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='edit_sessions')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, unique=True, help_text="WebSocket session ID")
    cursor_position = models.JSONField(
        default=dict,
        help_text="Current cursor/selection position in form editor"
    )
    active_field = models.CharField(max_length=100, blank=True, help_text="Field currently being edited")
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'form_edit_sessions'
        indexes = [
            models.Index(fields=['form', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.email} editing {self.form.title}"


class FormChange(models.Model):
    """Track individual changes for real-time sync and history"""
    CHANGE_TYPES = [
        ('field_added', 'Field Added'),
        ('field_updated', 'Field Updated'),
        ('field_deleted', 'Field Deleted'),
        ('field_reordered', 'Field Reordered'),
        ('logic_added', 'Logic Added'),
        ('logic_updated', 'Logic Updated'),
        ('logic_deleted', 'Logic Deleted'),
        ('settings_updated', 'Settings Updated'),
        ('title_updated', 'Title Updated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='changes')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    session = models.ForeignKey(
        FormEditSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='changes'
    )
    change_type = models.CharField(max_length=50, choices=CHANGE_TYPES)
    field_id = models.CharField(max_length=100, blank=True, help_text="ID of affected field")
    previous_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    change_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="JSON path to changed property (e.g., 'fields.0.label')"
    )
    is_synced = models.BooleanField(default=False, help_text="Synced to other clients")
    conflict_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'form_changes'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['form', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.change_type} by {self.user.email}"


class FormComment(models.Model):
    """Comments on specific form fields"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='form_comments')
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    field_id = models.CharField(max_length=100, help_text="Field this comment is attached to")
    content = models.TextField()
    mentions = models.JSONField(
        default=list,
        help_text="List of mentioned user IDs"
    )
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_comments'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'form_comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['form', 'field_id']),
        ]
    
    def __str__(self):
        return f"Comment on {self.form.title} by {self.user.email}"


class FormReviewWorkflow(models.Model):
    """Review and approval workflow for forms"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_review', 'In Review'),
        ('changes_requested', 'Changes Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='review_workflow')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    submitted_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='submitted_reviews'
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewers = models.ManyToManyField(
        'users.User',
        related_name='review_assignments',
        through='FormReview'
    )
    required_approvals = models.IntegerField(default=1)
    current_approvals = models.IntegerField(default=0)
    auto_publish_on_approval = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'form_review_workflows'
    
    def __str__(self):
        return f"{self.form.title} - {self.status}"


class FormReview(models.Model):
    """Individual review of a form"""
    DECISION_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('changes_requested', 'Changes Requested'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(FormReviewWorkflow, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='form_reviews')
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES, default='pending')
    feedback = models.TextField(blank=True)
    change_requests = models.JSONField(
        default=list,
        help_text="Specific changes requested by reviewer"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'form_reviews'
        unique_together = [['workflow', 'reviewer']]
    
    def __str__(self):
        return f"{self.reviewer.email} - {self.decision}"


class ConflictResolution(models.Model):
    """Track conflict resolutions in collaborative editing"""
    RESOLUTION_STRATEGIES = [
        ('last_write_wins', 'Last Write Wins'),
        ('manual', 'Manual Resolution'),
        ('merge', 'Automatic Merge'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='conflicts')
    conflicting_changes = models.JSONField(
        default=list,
        help_text="List of conflicting FormChange IDs"
    )
    resolution_strategy = models.CharField(max_length=50, choices=RESOLUTION_STRATEGIES)
    resolved_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    final_value = models.JSONField(help_text="Final resolved value")
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conflict_resolutions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Conflict on {self.form.title} - {self.resolution_strategy}"


class ActivityLog(models.Model):
    """Detailed activity log for form editing"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='activity_logs')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    action = models.CharField(max_length=200, help_text="Human-readable action description")
    action_type = models.CharField(max_length=50)
    details = models.JSONField(default=dict, help_text="Additional action context")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'activity_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['form', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.action}"
