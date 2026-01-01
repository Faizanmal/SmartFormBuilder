"""
Comprehensive database models for all interactive features in SmartFormBuilder.
Includes models for collaboration, gamification, analytics, workflows, voice, chatbot, submissions, AR, and gestures.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import json

User = get_user_model()


# ==================== COLLABORATION MODELS ====================

class CollaborationSession(models.Model):
    """Track active collaboration sessions on forms"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    form_id = models.CharField(max_length=100, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    max_users = models.IntegerField(default=50, validators=[MinValueValidator(1)])
    
    class Meta:
        db_table = 'collaboration_session'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['form_id', 'is_active']),
        ]
    
    def __str__(self):
        return f"Collaboration - {self.form_id}"


class UserSession(models.Model):
    """Track individual user participation in collaboration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    collaboration = models.ForeignKey(CollaborationSession, on_delete=models.CASCADE, related_name='users')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    color = models.CharField(max_length=7, default='#3498db')  # Hex color for cursor
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_session'
        ordering = ['-joined_at']
        indexes = [
            models.Index(fields=['collaboration', 'user']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"{self.username} in {self.collaboration.form_id}"
    
    def is_active(self):
        return self.left_at is None


class CollaborationMessage(models.Model):
    """Chat messages during collaboration"""
    MESSAGE_TYPES = [
        ('text', 'Text Message'),
        ('system', 'System Message'),
        ('notification', 'Notification'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    collaboration = models.ForeignKey(CollaborationSession, on_delete=models.CASCADE, related_name='messages')
    user_session = models.ForeignKey(UserSession, on_delete=models.SET_NULL, null=True, blank=True)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read_by = models.ManyToManyField(UserSession, related_name='read_messages', blank=True)
    
    class Meta:
        db_table = 'collaboration_message'
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['collaboration', 'timestamp']),
        ]
    
    def __str__(self):
        return f"Message in {self.collaboration.form_id}"


class CursorPosition(models.Model):
    """Track cursor positions for real-time collaboration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_session = models.OneToOneField(UserSession, on_delete=models.CASCADE, related_name='cursor')
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    field_id = models.CharField(max_length=100, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cursor_position'
    
    def __str__(self):
        return f"Cursor for {self.user_session.username}"


# ==================== GAMIFICATION MODELS ====================

class GamificationProfile(models.Model):
    """User gamification profile tracking points, achievements, and streaks"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gamification_profile')
    total_points = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    level = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    experience = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    experience_to_next_level = models.IntegerField(default=1000)
    current_streak = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    longest_streak = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    last_activity_date = models.DateField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'gamification_profile'
        ordering = ['-total_points', '-level']
        indexes = [
            models.Index(fields=['total_points']),
            models.Index(fields=['level']),
        ]
    
    def __str__(self):
        return f"Profile of {self.user.username}"
    
    def add_points(self, points, reason=""):
        """Add points and handle level ups"""
        self.total_points += points
        self.experience += points
        
        # Check for level up
        while self.experience >= self.experience_to_next_level:
            self.level += 1
            self.experience -= self.experience_to_next_level
            self.experience_to_next_level = int(self.experience_to_next_level * 1.1)
        
        self.save()


class Achievement(models.Model):
    """Achievement definitions and tracking"""
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
        ('legendary', 'Legendary'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    key = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.URLField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    points_reward = models.IntegerField(default=50, validators=[MinValueValidator(0)])
    criteria = models.JSONField(default=dict)  # Criteria for unlocking
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'achievement'
        ordering = ['difficulty', 'name']
    
    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """Track which achievements users have unlocked"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_achievement'
        unique_together = ('user', 'achievement')
        ordering = ['-unlocked_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"


class PointsLog(models.Model):
    """Audit log for all points transactions"""
    REASON_CHOICES = [
        ('form_created', 'Form Created'),
        ('form_published', 'Form Published'),
        ('field_added', 'Field Added'),
        ('form_submitted', 'Form Submitted'),
        ('achievement', 'Achievement Unlocked'),
        ('daily_bonus', 'Daily Bonus'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='points_logs')
    amount = models.IntegerField(validators=[MinValueValidator(-1000)])
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    description = models.TextField(blank=True)
    form_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'points_log'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} points"


class DailyStreak(models.Model):
    """Track daily streaks for users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='daily_streak')
    current_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    max_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    last_activity_date = models.DateField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'daily_streak'
    
    def __str__(self):
        return f"Streak of {self.user.username}"


# ==================== ANALYTICS MODELS ====================

class InteractiveFormAnalytics(models.Model):
    """Aggregate analytics for a form"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    form_id = models.CharField(max_length=100, unique=True, db_index=True)
    total_views = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    total_submissions = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    completion_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    average_completion_time = models.IntegerField(default=0, help_text="in seconds")
    bounce_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    conversion_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'interactive_form_analytics'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Analytics for {self.form_id}"


class InteractiveFieldAnalytics(models.Model):
    """Per-field analytics"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    form_analytics = models.ForeignKey(InteractiveFormAnalytics, on_delete=models.CASCADE, related_name='fields')
    field_id = models.CharField(max_length=100)
    field_label = models.CharField(max_length=200)
    views = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    interactions = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    drop_offs = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    average_time_spent = models.IntegerField(default=0, help_text="in seconds")
    error_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    help_clicks = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    class Meta:
        db_table = 'interactive_field_analytics'
        unique_together = ('form_analytics', 'field_id')
        ordering = ['field_label']
    
    def __str__(self):
        return f"Analytics for {self.field_label}"


class InteractiveAnalyticsEvent(models.Model):
    """Individual analytics events for detailed tracking"""
    EVENT_TYPES = [
        ('view', 'Form View'),
        ('start', 'Form Started'),
        ('field_focus', 'Field Focus'),
        ('field_blur', 'Field Blur'),
        ('field_error', 'Field Error'),
        ('field_change', 'Field Changed'),
        ('help_click', 'Help Clicked'),
        ('submit', 'Form Submit'),
        ('abandon', 'Form Abandoned'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    form_id = models.CharField(max_length=100, db_index=True)
    form_analytics = models.ForeignKey(InteractiveFormAnalytics, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    session_id = models.CharField(max_length=100, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    field_id = models.CharField(max_length=100, null=True, blank=True)
    value = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'interactive_analytics_event'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['form_id', 'timestamp']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"{self.event_type} in {self.form_id}"


class InteractiveAnalyticsSnapshot(models.Model):
    """Daily/weekly/monthly snapshots of analytics"""
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    form_analytics = models.ForeignKey(InteractiveFormAnalytics, on_delete=models.CASCADE, related_name='snapshots')
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    period_date = models.DateField(db_index=True)
    views = models.IntegerField(default=0)
    submissions = models.IntegerField(default=0)
    completion_rate = models.FloatField(default=0.0)
    
    class Meta:
        db_table = 'interactive_analytics_snapshot'
        unique_together = ('form_analytics', 'period', 'period_date')
        ordering = ['-period_date']
    
    def __str__(self):
        return f"{self.form_analytics.form_id} - {self.period}"


# ==================== WORKFLOW MODELS ====================

class InteractiveWorkflow(models.Model):
    """Workflow definitions for form automation"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    TRIGGER_CHOICES = [
        ('form_submit', 'Form Submit'),
        ('field_change', 'Field Change'),
        ('time', 'Time-based'),
        ('webhook', 'Webhook'),
        ('manual', 'Manual'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    form_id = models.CharField(max_length=100, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workflows')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_CHOICES)
    trigger_config = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'interactive_workflow'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['form_id']),
        ]
    
    def __str__(self):
        return self.name


class InteractiveWorkflowStep(models.Model):
    """Steps within a workflow"""
    ACTION_CHOICES = [
        ('email', 'Send Email'),
        ('sms', 'Send SMS'),
        ('slack', 'Slack Notification'),
        ('webhook', 'Webhook Call'),
        ('conditional', 'Conditional Branch'),
        ('delay', 'Delay'),
        ('transform', 'Transform Data'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    workflow = models.ForeignKey(InteractiveWorkflow, on_delete=models.CASCADE, related_name='steps')
    order = models.IntegerField(validators=[MinValueValidator(1)])
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
    action_config = models.JSONField(default=dict)
    condition = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'interactive_workflow_step'
        unique_together = ('workflow', 'order')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.workflow.name} - Step {self.order}"


class InteractiveWorkflowExecution(models.Model):
    """Record of workflow executions"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    workflow = models.ForeignKey(InteractiveWorkflow, on_delete=models.CASCADE, related_name='executions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    trigger_data = models.JSONField(default=dict)
    result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    execution_time = models.IntegerField(null=True, blank=True, help_text="in milliseconds")
    
    class Meta:
        db_table = 'interactive_workflow_execution'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['workflow', 'status']),
        ]
    
    def __str__(self):
        return f"Execution of {self.workflow.name}"


class InteractiveWorkflowStepExecution(models.Model):
    """Track individual step executions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    execution = models.ForeignKey(InteractiveWorkflowExecution, on_delete=models.CASCADE, related_name='step_executions')
    step = models.ForeignKey(InteractiveWorkflowStep, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ], default='pending')
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'interactive_workflow_step_execution'
        ordering = ['step__order']
    
    def __str__(self):
        return f"{self.step.workflow.name} - {self.step.action_type}"


# ==================== VOICE MODELS ====================

class VoiceTranscription(models.Model):
    """Store voice transcriptions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='voice_transcriptions')
    form_id = models.CharField(max_length=100, null=True, blank=True)
    field_id = models.CharField(max_length=100, null=True, blank=True)
    audio_file = models.FileField(upload_to='voice_transcriptions/%Y/%m/%d/')
    text = models.TextField()
    confidence = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    language = models.CharField(max_length=10, default='en-US')
    duration = models.IntegerField(help_text="in milliseconds")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'voice_transcription'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['form_id', 'field_id']),
        ]
    
    def __str__(self):
        return f"Transcription by {self.user.username}"


class VoiceCommand(models.Model):
    """Track voice commands and their execution"""
    COMMAND_TYPES = [
        ('add_field', 'Add Field'),
        ('delete_field', 'Delete Field'),
        ('rename_field', 'Rename Field'),
        ('change_type', 'Change Type'),
        ('submit', 'Submit'),
        ('clear', 'Clear'),
        ('undo', 'Undo'),
        ('redo', 'Redo'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='voice_commands')
    transcription = models.ForeignKey(VoiceTranscription, on_delete=models.SET_NULL, null=True)
    form_id = models.CharField(max_length=100)
    command_type = models.CharField(max_length=50, choices=COMMAND_TYPES)
    parameters = models.JSONField(default=dict)
    executed = models.BooleanField(default=False)
    result = models.JSONField(null=True, blank=True)
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'voice_command'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.command_type} by {self.user.username}"


# ==================== CHATBOT MODELS ====================

class ChatSession(models.Model):
    """Chatbot conversation sessions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions', null=True, blank=True)
    form_id = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_session'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"Chat session {self.id}"


class ChatMessage(models.Model):
    """Individual chat messages"""
    SENDER_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_message'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender}"


class ChatSuggestion(models.Model):
    """Quick suggestions for chatbot"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='suggestions')
    text = models.CharField(max_length=200)
    icon = models.CharField(max_length=50, blank=True)
    action = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'chat_suggestion'
    
    def __str__(self):
        return self.text


# ==================== SUBMISSION MODELS ====================

class FormSubmission(models.Model):
    """Individual form submissions"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    form_id = models.CharField(max_length=100, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    data = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    completion_time = models.IntegerField(null=True, blank=True, help_text="in seconds")
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'form_submission'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['form_id', 'status']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"Submission for {self.form_id}"


class SubmissionField(models.Model):
    """Individual field data within a submission"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    submission = models.ForeignKey(FormSubmission, on_delete=models.CASCADE, related_name='fields')
    field_id = models.CharField(max_length=100)
    field_label = models.CharField(max_length=200)
    value = models.TextField()
    
    class Meta:
        db_table = 'submission_field'
        unique_together = ('submission', 'field_id')
    
    def __str__(self):
        return f"{self.field_label}: {self.value}"


# ==================== AR/VR MODELS ====================

class ARAsset(models.Model):
    """3D models and AR assets"""
    ASSET_TYPES = [
        ('model', '3D Model'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('animation', 'Animation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    asset_type = models.CharField(max_length=50, choices=ASSET_TYPES)
    file = models.FileField(upload_to='ar_assets/%Y/%m/%d/')
    thumbnail = models.ImageField(upload_to='ar_assets/thumbnails/', null=True, blank=True)
    form_id = models.CharField(max_length=100, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ar_assets')
    metadata = models.JSONField(default=dict)  # Format, dimensions, etc.
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ar_asset'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'is_public']),
        ]
    
    def __str__(self):
        return self.name


class ARPreview(models.Model):
    """AR preview sessions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ar_previews')
    form_id = models.CharField(max_length=100)
    asset = models.ForeignKey(ARAsset, on_delete=models.SET_NULL, null=True, blank=True)
    rotation = models.JSONField(default=dict)  # x, y, z rotation
    scale = models.JSONField(default=dict)     # x, y, z scale
    position = models.JSONField(default=dict)  # x, y, z position
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'ar_preview'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"AR Preview by {self.user.username}"


# ==================== GESTURE MODELS ====================

class GestureSettings(models.Model):
    """User gesture recognition settings"""
    GESTURE_TYPES = [
        ('swipe', 'Swipe'),
        ('pinch', 'Pinch'),
        ('tap', 'Tap'),
        ('long_press', 'Long Press'),
        ('rotate', 'Rotate'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gesture_settings')
    enabled = models.BooleanField(default=True)
    sensitivity = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="1-10 scale"
    )
    gestures = models.JSONField(default=dict)  # Gesture to action mapping
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'gesture_settings'
    
    def __str__(self):
        return f"Gesture settings for {self.user.username}"


class GestureEvent(models.Model):
    """Log of gesture events"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gesture_events')
    form_id = models.CharField(max_length=100, null=True, blank=True)
    gesture_type = models.CharField(max_length=50, choices=[
        ('swipe', 'Swipe'),
        ('pinch', 'Pinch'),
        ('tap', 'Tap'),
        ('long_press', 'Long Press'),
        ('rotate', 'Rotate'),
    ])
    direction = models.CharField(max_length=20, null=True, blank=True)  # left, right, up, down
    coordinates = models.JSONField(default=dict)  # x, y
    action_triggered = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'gesture_event'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.gesture_type} by {self.user.username}"
