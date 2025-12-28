"""
Advanced analytics, heatmaps, and user behavior models
"""
from django.db import models
import uuid


class FormHeatmapData(models.Model):
    """Aggregated heatmap data for form interactions"""
    INTERACTION_TYPES = [
        ('click', 'Click'),
        ('hover', 'Hover'),
        ('scroll', 'Scroll'),
        ('focus', 'Focus'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='heatmap_data')
    field_id = models.CharField(max_length=100, blank=True, help_text="Field ID or empty for general form")
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    
    # Position data (normalized 0-100)
    x_position = models.FloatField(help_text="X position as percentage")
    y_position = models.FloatField(help_text="Y position as percentage")
    
    # Aggregated data
    interaction_count = models.IntegerField(default=1)
    avg_duration_ms = models.FloatField(default=0, help_text="Average interaction duration")
    
    device_type = models.CharField(
        max_length=20,
        choices=[('desktop', 'Desktop'), ('mobile', 'Mobile'), ('tablet', 'Tablet')],
        default='desktop'
    )
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'form_heatmap_data'
        indexes = [
            models.Index(fields=['form', 'date']),
            models.Index(fields=['form', 'field_id']),
        ]


class SessionRecording(models.Model):
    """Session recording metadata for form interactions"""
    STATUS_CHOICES = [
        ('recording', 'Recording'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='session_recordings')
    session_id = models.CharField(max_length=100, unique=True)
    
    # Session metadata
    device_type = models.CharField(max_length=20, default='desktop')
    browser = models.CharField(max_length=50, blank=True)
    os = models.CharField(max_length=50, blank=True)
    screen_width = models.IntegerField(default=0)
    screen_height = models.IntegerField(default=0)
    country = models.CharField(max_length=50, blank=True)
    
    # Recording data
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='recording')
    events_count = models.IntegerField(default=0)
    events_data = models.JSONField(default=list, help_text="Compressed event stream")
    recording_url = models.URLField(blank=True, help_text="URL to stored recording file")
    
    # Session metrics
    duration_seconds = models.IntegerField(default=0)
    completed_form = models.BooleanField(default=False)
    drop_off_field = models.CharField(max_length=100, blank=True)
    rage_clicks_count = models.IntegerField(default=0)
    u_turns_count = models.IntegerField(default=0, help_text="Navigation back and forth")
    
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'session_recordings'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['form', 'started_at']),
            models.Index(fields=['form', 'completed_form']),
        ]
    
    def __str__(self):
        return f"Session {self.session_id[:8]}... for {self.form.title}"


class SessionEvent(models.Model):
    """Individual events in a session recording"""
    EVENT_TYPES = [
        ('page_view', 'Page View'),
        ('field_focus', 'Field Focus'),
        ('field_blur', 'Field Blur'),
        ('field_change', 'Field Change'),
        ('field_error', 'Field Error'),
        ('click', 'Click'),
        ('scroll', 'Scroll'),
        ('mouse_move', 'Mouse Move'),
        ('keypress', 'Keypress'),
        ('form_submit', 'Form Submit'),
        ('form_abandon', 'Form Abandon'),
        ('step_change', 'Step Change'),
        ('rage_click', 'Rage Click'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(SessionRecording, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    timestamp = models.BigIntegerField(help_text="Timestamp in milliseconds from session start")
    
    # Event data
    target_element = models.CharField(max_length=200, blank=True)
    field_id = models.CharField(max_length=100, blank=True)
    x_position = models.IntegerField(default=0)
    y_position = models.IntegerField(default=0)
    scroll_position = models.IntegerField(default=0)
    
    # Additional event data
    data = models.JSONField(default=dict, help_text="Event-specific data")
    
    class Meta:
        db_table = 'session_events'
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['session', 'timestamp']),
        ]


class DropOffAnalysis(models.Model):
    """Field-level drop-off analysis"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='dropoff_analysis')
    field_id = models.CharField(max_length=100)
    field_label = models.CharField(max_length=255)
    field_order = models.IntegerField()
    
    # Funnel metrics
    visitors_reached = models.IntegerField(default=0, help_text="Users who reached this field")
    visitors_completed = models.IntegerField(default=0, help_text="Users who completed this field")
    visitors_dropped = models.IntegerField(default=0, help_text="Users who abandoned at this field")
    
    drop_off_rate = models.FloatField(default=0)
    
    # Time metrics
    avg_time_on_field = models.FloatField(default=0, help_text="Seconds")
    
    # Error analysis
    validation_errors = models.IntegerField(default=0)
    most_common_error = models.CharField(max_length=500, blank=True)
    
    # Reasons for drop-off (analyzed)
    suspected_reasons = models.JSONField(
        default=list,
        help_text="AI-analyzed reasons for drop-off"
    )
    
    analysis_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dropoff_analysis'
        unique_together = [['form', 'field_id', 'analysis_date']]
        ordering = ['field_order']


class ABTestResult(models.Model):
    """Statistical results for A/B tests"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ab_test = models.ForeignKey('forms.ABTest', on_delete=models.CASCADE, related_name='results')
    
    # Control variant (original form)
    control_visitors = models.IntegerField(default=0)
    control_conversions = models.IntegerField(default=0)
    control_conversion_rate = models.FloatField(default=0)
    
    # Treatment variant
    variant = models.ForeignKey('forms.FormVariant', on_delete=models.CASCADE)
    variant_visitors = models.IntegerField(default=0)
    variant_conversions = models.IntegerField(default=0)
    variant_conversion_rate = models.FloatField(default=0)
    
    # Statistical analysis
    relative_improvement = models.FloatField(default=0, help_text="Percentage improvement over control")
    p_value = models.FloatField(null=True, blank=True)
    confidence_level = models.FloatField(default=0, help_text="Percentage (e.g., 95.0)")
    is_significant = models.BooleanField(default=False)
    
    # Additional metrics
    sample_size_needed = models.IntegerField(default=0, help_text="For statistical power")
    estimated_completion_date = models.DateField(null=True, blank=True)
    
    calculated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ab_test_results'
        ordering = ['-calculated_at']
    
    def __str__(self):
        return f"Results for {self.ab_test.name} - {self.variant.name}"


class BehaviorInsight(models.Model):
    """AI-generated behavior insights"""
    INSIGHT_TYPES = [
        ('pattern', 'User Pattern'),
        ('anomaly', 'Anomaly Detected'),
        ('optimization', 'Optimization Opportunity'),
        ('trend', 'Trend Analysis'),
        ('prediction', 'Prediction'),
    ]
    
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='behavior_insights')
    insight_type = models.CharField(max_length=50, choices=INSIGHT_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Supporting data
    supporting_data = models.JSONField(default=dict)
    affected_fields = models.JSONField(default=list, help_text="Field IDs affected")
    
    # Recommendations
    recommendations = models.JSONField(default=list)
    
    # Impact estimation
    estimated_impact = models.FloatField(null=True, blank=True, help_text="Estimated conversion improvement %")
    
    is_actionable = models.BooleanField(default=True)
    is_dismissed = models.BooleanField(default=False)
    dismissed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    generated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'behavior_insights'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.insight_type}: {self.title}"


class FormFunnel(models.Model):
    """Funnel analysis for multi-step forms"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='funnels')
    name = models.CharField(max_length=255, default='Default Funnel')
    
    # Funnel configuration
    steps = models.JSONField(
        default=list,
        help_text="List of step configurations with labels and conditions"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'form_funnels'
    
    def __str__(self):
        return f"Funnel: {self.name}"


class FunnelStepMetric(models.Model):
    """Metrics for each step in a funnel"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    funnel = models.ForeignKey(FormFunnel, on_delete=models.CASCADE, related_name='step_metrics')
    step_index = models.IntegerField()
    step_name = models.CharField(max_length=255)
    
    entered_count = models.IntegerField(default=0)
    completed_count = models.IntegerField(default=0)
    dropped_count = models.IntegerField(default=0)
    
    avg_time_seconds = models.FloatField(default=0)
    conversion_rate = models.FloatField(default=0)
    
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'funnel_step_metrics'
        unique_together = [['funnel', 'step_index', 'date']]
        ordering = ['step_index']
