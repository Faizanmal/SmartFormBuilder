"""
Predictive form completion and smart defaults models
"""
from django.db import models
import uuid


class UserSubmissionHistory(models.Model):
    """Track user submission patterns for predictions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_identifier = models.CharField(
        max_length=200,
        help_text="Email, user ID, or anonymous identifier",
        db_index=True
    )
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='user_histories')
    field_values = models.JSONField(default=dict, help_text="Historical field values")
    completion_time = models.IntegerField(help_text="Time to complete in seconds")
    device_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_submission_histories'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_identifier', 'form']),
        ]
    
    def __str__(self):
        return f"{self.user_identifier} - {self.form.title}"


class FieldPrediction(models.Model):
    """AI-powered field value predictions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='field_predictions')
    field_id = models.CharField(max_length=100)
    field_type = models.CharField(max_length=50)
    prediction_rule = models.JSONField(
        default=dict,
        help_text="Rule for prediction (e.g., ZIP -> City mapping)"
    )
    ml_model_id = models.CharField(max_length=100, blank=True, help_text="ML model identifier if used")
    confidence_threshold = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.70,
        help_text="Minimum confidence to show prediction"
    )
    is_active = models.BooleanField(default=True)
    accuracy_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Historical accuracy percentage"
    )
    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'field_predictions'
        unique_together = [['form', 'field_id']]
    
    def __str__(self):
        return f"{self.form.title} - {self.field_id}"


class AutoFillTemplate(models.Model):
    """Templates for auto-filling common field patterns"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='autofill_templates')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    field_mappings = models.JSONField(
        default=dict,
        help_text="Map of field IDs to auto-fill values"
    )
    is_global = models.BooleanField(default=False, help_text="Available across all forms")
    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'autofill_templates'
    
    def __str__(self):
        return self.name


class SmartDefault(models.Model):
    """Smart default values for form fields"""
    SOURCE_TYPES = [
        ('url_param', 'URL Parameter'),
        ('user_profile', 'User Profile'),
        ('cookie', 'Cookie'),
        ('local_storage', 'Local Storage'),
        ('geolocation', 'Geolocation'),
        ('previous_submission', 'Previous Submission'),
        ('calculation', 'Calculation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='smart_defaults')
    field_id = models.CharField(max_length=100)
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES)
    source_config = models.JSONField(
        default=dict,
        help_text="Configuration for the source (e.g., URL param name, profile field)"
    )
    transformation = models.JSONField(
        default=dict,
        blank=True,
        help_text="Data transformation rules"
    )
    fallback_value = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'smart_defaults'
        unique_together = [['form', 'field_id']]
    
    def __str__(self):
        return f"{self.form.title} - {self.field_id} ({self.source_type})"


class CompletionPrediction(models.Model):
    """Predict form completion progress"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='completion_predictions')
    session_id = models.CharField(max_length=100, db_index=True)
    current_field_index = models.IntegerField()
    total_fields = models.IntegerField()
    required_fields_completed = models.IntegerField()
    required_fields_total = models.IntegerField()
    predicted_completion_percent = models.IntegerField(
        help_text="AI-predicted completion percentage"
    )
    estimated_time_remaining = models.IntegerField(
        help_text="Estimated seconds to completion"
    )
    confidence_score = models.DecimalField(max_digits=4, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'completion_predictions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.form.title} - {self.predicted_completion_percent}%"


class ProgressiveDisclosure(models.Model):
    """Configuration for progressive field disclosure"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='progressive_disclosure')
    is_enabled = models.BooleanField(default=False)
    disclosure_strategy = models.CharField(
        max_length=50,
        choices=[
            ('basic_first', 'Basic Fields First'),
            ('conditional', 'Conditional Disclosure'),
            ('ai_adaptive', 'AI Adaptive'),
        ],
        default='basic_first'
    )
    basic_fields = models.JSONField(
        default=list,
        help_text="List of field IDs shown initially"
    )
    advanced_fields = models.JSONField(
        default=list,
        help_text="List of field IDs shown after basics"
    )
    disclosure_rules = models.JSONField(
        default=dict,
        help_text="Conditions for revealing fields"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'progressive_disclosures'
    
    def __str__(self):
        return f"{self.form.title} - Progressive Disclosure"


class PredictionFeedback(models.Model):
    """Track accuracy of predictions for improvement"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prediction = models.ForeignKey(
        FieldPrediction,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    submission = models.ForeignKey('forms.Submission', on_delete=models.CASCADE)
    predicted_value = models.JSONField()
    actual_value = models.JSONField()
    was_accepted = models.BooleanField(help_text="Did user accept the prediction?")
    confidence_score = models.DecimalField(max_digits=4, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'prediction_feedback'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Feedback for {self.prediction} - {'Accepted' if self.was_accepted else 'Rejected'}"
