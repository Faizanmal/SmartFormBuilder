"""
Form auto-save, recovery, and draft management models
"""
from django.db import models
import uuid


class FormBuilderAutoSave(models.Model):
    """Auto-save data for form builder (design mode)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(
        'forms.Form',
        on_delete=models.CASCADE,
        related_name='builder_autosaves',
        null=True,
        blank=True
    )
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='form_autosaves')
    
    # For new forms that haven't been saved yet
    temp_id = models.CharField(max_length=100, blank=True, db_index=True)
    
    # Auto-saved content
    schema_json = models.JSONField(default=dict)
    settings_json = models.JSONField(default=dict)
    title = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    
    # Editor state
    editor_state = models.JSONField(
        default=dict,
        help_text="Editor UI state (selected field, scroll position, etc.)"
    )
    
    # Recovery info
    is_recovered = models.BooleanField(default=False)
    recovered_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    browser_session_id = models.CharField(max_length=100, blank=True)
    device_info = models.JSONField(default=dict)
    
    last_saved_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'form_builder_autosaves'
        ordering = ['-last_saved_at']
        indexes = [
            models.Index(fields=['user', 'form']),
            models.Index(fields=['user', 'temp_id']),
        ]
    
    def __str__(self):
        if self.form:
            return f"Auto-save for {self.form.title}"
        return f"Auto-save (new form) - {self.temp_id[:8]}..."


class FormBuilderCrashRecovery(models.Model):
    """Recovery data after browser crash or accidental closure"""
    RECOVERY_STATUS = [
        ('pending', 'Pending Recovery'),
        ('recovered', 'Recovered'),
        ('dismissed', 'Dismissed'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='crash_recoveries')
    form = models.ForeignKey(
        'forms.Form',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='crash_recoveries'
    )
    
    # Recovery data
    autosave = models.ForeignKey(
        FormBuilderAutoSave,
        on_delete=models.CASCADE,
        related_name='crash_recoveries'
    )
    
    status = models.CharField(max_length=20, choices=RECOVERY_STATUS, default='pending')
    
    # Crash information
    crash_reason = models.CharField(
        max_length=50,
        choices=[
            ('browser_crash', 'Browser Crash'),
            ('tab_closed', 'Tab Closed'),
            ('session_expired', 'Session Expired'),
            ('network_error', 'Network Error'),
            ('unknown', 'Unknown'),
        ],
        default='unknown'
    )
    
    # What was lost
    unsaved_changes_summary = models.JSONField(default=dict)
    estimated_work_time = models.IntegerField(default=0, help_text="Estimated minutes of work")
    
    expires_at = models.DateTimeField()
    recovered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'form_builder_crash_recoveries'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Recovery for {self.user.email} - {self.status}"


class FormPublishSchedule(models.Model):
    """Schedule forms for future publishing"""
    SCHEDULE_STATUS = [
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='publish_schedules')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    
    scheduled_for = models.DateTimeField()
    status = models.CharField(max_length=20, choices=SCHEDULE_STATUS, default='scheduled')
    
    # What version to publish
    schema_snapshot = models.JSONField(default=dict, help_text="Schema at time of scheduling")
    settings_snapshot = models.JSONField(default=dict)
    
    # Options
    notify_on_publish = models.BooleanField(default=True)
    auto_unpublish_at = models.DateTimeField(null=True, blank=True)
    
    # Results
    published_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'form_publish_schedules'
        ordering = ['-scheduled_for']
    
    def __str__(self):
        return f"Schedule: {self.form.title} at {self.scheduled_for}"


class DraftVersion(models.Model):
    """Draft versions with auto-save snapshots"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='draft_versions')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    
    # Draft content
    schema_json = models.JSONField(default=dict)
    settings_json = models.JSONField(default=dict)
    
    # Version info
    version_number = models.IntegerField()
    is_auto_save = models.BooleanField(default=True)
    save_trigger = models.CharField(
        max_length=50,
        choices=[
            ('auto_30s', 'Auto-save (30s)'),
            ('auto_change', 'Auto-save (on change)'),
            ('manual', 'Manual Save'),
            ('publish_preview', 'Before Publish'),
        ],
        default='auto_30s'
    )
    
    # Changes summary
    changes_summary = models.JSONField(
        default=dict,
        help_text="Summary of changes from previous version"
    )
    
    # Comparison support
    diff_from_previous = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'draft_versions'
        ordering = ['-version_number']
        unique_together = [['form', 'version_number']]
    
    def __str__(self):
        return f"Draft v{self.version_number} for {self.form.title}"


class OfflineFormDraft(models.Model):
    """Offline form builder drafts (synced when online)"""
    SYNC_STATUS = [
        ('pending', 'Pending Sync'),
        ('syncing', 'Syncing'),
        ('synced', 'Synced'),
        ('conflict', 'Conflict'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='offline_form_drafts')
    form = models.ForeignKey(
        'forms.Form',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='offline_drafts'
    )
    
    # Offline-generated ID (for new forms)
    offline_id = models.CharField(max_length=100, unique=True)
    
    # Draft data
    schema_json = models.JSONField(default=dict)
    settings_json = models.JSONField(default=dict)
    title = models.CharField(max_length=500)
    
    # Sync status
    sync_status = models.CharField(max_length=20, choices=SYNC_STATUS, default='pending')
    
    # Conflict resolution
    has_conflict = models.BooleanField(default=False)
    server_version = models.JSONField(default=dict, blank=True)
    conflict_resolved = models.BooleanField(default=False)
    resolution_choice = models.CharField(
        max_length=20,
        choices=[
            ('keep_local', 'Keep Local'),
            ('keep_server', 'Keep Server'),
            ('merge', 'Merge'),
        ],
        blank=True
    )
    
    # Metadata
    created_offline_at = models.DateTimeField()
    last_modified_offline_at = models.DateTimeField()
    synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'offline_form_drafts'
        ordering = ['-last_modified_offline_at']
    
    def __str__(self):
        return f"Offline draft: {self.title}"


class AutoSaveConfig(models.Model):
    """User's auto-save preferences"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='autosave_config')
    
    # Auto-save settings
    enabled = models.BooleanField(default=True)
    interval_seconds = models.IntegerField(default=30)
    save_on_field_change = models.BooleanField(default=True)
    save_on_step_change = models.BooleanField(default=True)
    
    # Recovery settings
    recovery_enabled = models.BooleanField(default=True)
    recovery_retention_hours = models.IntegerField(default=72)
    
    # Version history
    keep_version_history = models.BooleanField(default=True)
    max_versions = models.IntegerField(default=50)
    
    # Notifications
    notify_on_recovery_available = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'autosave_configs'
    
    def __str__(self):
        return f"Auto-save config for {self.user.email}"
