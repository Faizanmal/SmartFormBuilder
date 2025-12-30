"""
Emerging Technology Integration Models

Comprehensive models for:
- AI-Powered Form Optimization
- Conversational AI Chatbots (Claude, Gemini integration)
- Smart Form Layout Suggestions
- Automated Form Personalization
- Computer Vision Heatmap Analysis
"""
from django.db import models
import uuid


# ============================================================================
# AI-POWERED FORM OPTIMIZATION
# ============================================================================

class AILayoutSuggestion(models.Model):
    """AI-powered layout suggestions based on heatmap analysis"""
    SUGGESTION_TYPES = [
        ('field_order', 'Field Ordering'),
        ('field_grouping', 'Field Grouping'),
        ('remove_field', 'Remove Field'),
        ('add_field', 'Add Field'),
        ('field_size', 'Field Size Change'),
        ('visual_hierarchy', 'Visual Hierarchy'),
        ('mobile_optimization', 'Mobile Optimization'),
    ]
    
    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='ai_layout_suggestions')
    
    suggestion_type = models.CharField(max_length=30, choices=SUGGESTION_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Affected fields
    field_ids = models.JSONField(default=list, help_text="Fields affected by this suggestion")
    
    # Suggestion details
    title = models.CharField(max_length=255)
    description = models.TextField()
    rationale = models.TextField(help_text="AI reasoning for this suggestion")
    
    # Impact predictions
    predicted_conversion_lift = models.FloatField(default=0, help_text="Predicted conversion improvement %")
    predicted_completion_lift = models.FloatField(default=0, help_text="Predicted completion improvement %")
    confidence_score = models.FloatField(default=0, help_text="AI confidence 0-1")
    
    # Before/After schema
    current_schema = models.JSONField(default=dict, help_text="Current field arrangement")
    suggested_schema = models.JSONField(default=dict, help_text="Suggested new arrangement")
    
    # Heatmap analysis data
    heatmap_data = models.JSONField(default=dict, help_text="Heatmap analysis that led to this suggestion")
    interaction_patterns = models.JSONField(default=dict, help_text="User interaction patterns analyzed")
    
    # Status
    is_applied = models.BooleanField(default=False)
    applied_at = models.DateTimeField(null=True, blank=True)
    applied_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    # A/B test for suggestion
    ab_test_running = models.BooleanField(default=False)
    ab_test_id = models.UUIDField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_layout_suggestions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['form', 'is_applied']),
            models.Index(fields=['form', 'priority']),
        ]
    
    def __str__(self):
        return f"{self.form.title} - {self.suggestion_type}: {self.title}"


class ConversationalAIConfig(models.Model):
    """Configuration for AI chatbot integration (Claude, Gemini, OpenAI)"""
    AI_PROVIDERS = [
        ('openai', 'OpenAI GPT-4'),
        ('anthropic', 'Anthropic Claude'),
        ('google', 'Google Gemini'),
        ('custom', 'Custom LLM'),
    ]
    
    CONVERSATION_MODES = [
        ('form_filling', 'Form Filling Assistant'),
        ('guided', 'Guided Conversation'),
        ('freeform', 'Freeform Chat'),
        ('hybrid', 'Hybrid Mode'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='conversational_ai_config')
    
    is_enabled = models.BooleanField(default=False)
    ai_provider = models.CharField(max_length=20, choices=AI_PROVIDERS, default='openai')
    conversation_mode = models.CharField(max_length=20, choices=CONVERSATION_MODES, default='form_filling')
    
    # Provider-specific settings
    api_key_encrypted = models.TextField(blank=True, help_text="Encrypted API key")
    model_name = models.CharField(max_length=100, default='gpt-4o')
    
    # Personality and behavior
    assistant_name = models.CharField(max_length=100, default='Form Assistant')
    assistant_persona = models.TextField(
        blank=True,
        default="You are a friendly and helpful form assistant.",
        help_text="System prompt for AI personality"
    )
    welcome_message = models.TextField(
        default="Hi! I'm here to help you fill out this form. Let's get started!",
        help_text="Initial greeting message"
    )
    
    # Conversation settings
    max_clarification_attempts = models.IntegerField(default=3)
    allow_skip_optional = models.BooleanField(default=True)
    provide_progress_updates = models.BooleanField(default=True)
    summarize_on_completion = models.BooleanField(default=True)
    
    # Multi-language support
    supported_languages = models.JSONField(default=list, help_text="List of supported language codes")
    auto_detect_language = models.BooleanField(default=True)
    
    # Context awareness
    use_form_context = models.BooleanField(default=True, help_text="Use form schema to guide conversation")
    use_user_history = models.BooleanField(default=False, help_text="Use past interactions for personalization")
    
    # Voice settings
    voice_enabled = models.BooleanField(default=False)
    voice_id = models.CharField(max_length=100, blank=True, help_text="TTS voice ID")
    
    # Token/cost management
    max_tokens_per_conversation = models.IntegerField(default=4000)
    max_tokens_per_response = models.IntegerField(default=500)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'conversational_ai_configs'
    
    def __str__(self):
        return f"Conversational AI for {self.form.title}"


class ConversationSession(models.Model):
    """Track individual conversation sessions with AI"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='conversation_sessions')
    config = models.ForeignKey(ConversationalAIConfig, on_delete=models.CASCADE)
    
    session_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # User context
    user_identifier = models.CharField(max_length=255, blank=True, help_text="Email or session ID")
    device_type = models.CharField(max_length=50, blank=True)
    language_detected = models.CharField(max_length=10, blank=True)
    
    # Conversation state
    current_field_index = models.IntegerField(default=0)
    collected_data = models.JSONField(default=dict, help_text="Form data collected so far")
    fields_completed = models.JSONField(default=list)
    fields_skipped = models.JSONField(default=list)
    
    # Metrics
    total_messages = models.IntegerField(default=0)
    user_messages = models.IntegerField(default=0)
    ai_messages = models.IntegerField(default=0)
    total_tokens_used = models.IntegerField(default=0)
    clarification_count = models.IntegerField(default=0)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Resulting submission
    submission = models.ForeignKey('forms.Submission', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'conversation_sessions'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['form', 'status']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"Conversation {self.session_id[:8]}..."


class ConversationMessage(models.Model):
    """Individual messages in a conversation"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ConversationSession, on_delete=models.CASCADE, related_name='messages')
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    
    # For field-related messages
    related_field_id = models.CharField(max_length=100, blank=True)
    extracted_value = models.JSONField(null=True, blank=True, help_text="Value extracted from user message")
    
    # Input method
    input_method = models.CharField(
        max_length=20,
        choices=[('text', 'Text'), ('voice', 'Voice')],
        default='text'
    )
    voice_audio_url = models.URLField(blank=True)
    
    # Token usage
    tokens_used = models.IntegerField(default=0)
    
    # Sentiment analysis
    sentiment = models.CharField(max_length=20, blank=True)
    confidence = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conversation_messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class AIPersonalization(models.Model):
    """AI-driven dynamic form adaptation based on user behavior"""
    ADAPTATION_TYPES = [
        ('field_order', 'Field Order'),
        ('field_visibility', 'Field Visibility'),
        ('default_values', 'Default Values'),
        ('validation_rules', 'Validation Rules'),
        ('ui_complexity', 'UI Complexity'),
        ('language', 'Language'),
        ('theme', 'Theme'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='ai_personalizations')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    adaptation_type = models.CharField(max_length=30, choices=ADAPTATION_TYPES)
    
    # Trigger conditions
    trigger_conditions = models.JSONField(
        default=dict,
        help_text="""
        Conditions to apply this personalization, e.g.:
        {
            "user_segment": "returning",
            "device": "mobile",
            "referrer_contains": "google",
            "previous_abandonment": true
        }
        """
    )
    
    # Adaptation rules
    adaptation_rules = models.JSONField(
        default=dict,
        help_text="Rules for how to adapt the form"
    )
    
    # ML model for prediction
    ml_model_id = models.CharField(max_length=100, blank=True)
    prediction_threshold = models.FloatField(default=0.7)
    
    # Stats
    times_applied = models.IntegerField(default=0)
    conversion_improvement = models.FloatField(default=0, help_text="Measured improvement in conversion %")
    
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_personalizations'
        ordering = ['priority']
    
    def __str__(self):
        return f"{self.form.title} - {self.name}"


class UserBehaviorProfile(models.Model):
    """Track user behavior patterns for personalization"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_identifier = models.CharField(max_length=255, unique=True, help_text="Email or fingerprint")
    
    # Behavior metrics
    forms_viewed = models.IntegerField(default=0)
    forms_started = models.IntegerField(default=0)
    forms_completed = models.IntegerField(default=0)
    forms_abandoned = models.IntegerField(default=0)
    
    # Preferences learned
    preferred_device = models.CharField(max_length=50, blank=True)
    preferred_language = models.CharField(max_length=10, blank=True)
    preferred_time_of_day = models.CharField(max_length=20, blank=True)
    avg_completion_time = models.FloatField(default=0)
    
    # Engagement scores
    engagement_score = models.FloatField(default=0, help_text="0-100 engagement score")
    likelihood_to_complete = models.FloatField(default=0.5, help_text="ML predicted completion probability")
    
    # Field preferences
    field_preferences = models.JSONField(
        default=dict,
        help_text="Learned preferences for field types and interactions"
    )
    
    # Common values for auto-fill
    common_values = models.JSONField(
        default=dict,
        help_text="Common field values for this user"
    )
    
    # Segment assignment
    segments = models.JSONField(default=list, help_text="User segments this profile belongs to")
    
    first_seen_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_behavior_profiles'
        indexes = [
            models.Index(fields=['user_identifier']),
            models.Index(fields=['engagement_score']),
        ]
    
    def __str__(self):
        return f"Profile: {self.user_identifier}"


class HeatmapAnalysis(models.Model):
    """Computer vision analysis of user interaction heatmaps"""
    ANALYSIS_TYPES = [
        ('click', 'Click Heatmap'),
        ('scroll', 'Scroll Heatmap'),
        ('attention', 'Attention Heatmap'),
        ('mouse_movement', 'Mouse Movement'),
        ('form_flow', 'Form Flow'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='heatmap_analyses')
    
    analysis_type = models.CharField(max_length=30, choices=ANALYSIS_TYPES)
    device_type = models.CharField(max_length=20, default='desktop')
    
    # Date range analyzed
    start_date = models.DateField()
    end_date = models.DateField()
    sessions_analyzed = models.IntegerField(default=0)
    
    # Aggregated heatmap data
    heatmap_image_url = models.URLField(blank=True, help_text="Generated heatmap image")
    raw_data = models.JSONField(default=dict, help_text="Raw interaction data points")
    
    # AI analysis results
    hotspots = models.JSONField(
        default=list,
        help_text="Identified hotspot regions with coordinates"
    )
    cold_zones = models.JSONField(
        default=list,
        help_text="Areas with low engagement"
    )
    flow_patterns = models.JSONField(
        default=dict,
        help_text="User flow patterns through form"
    )
    
    # Insights
    ai_insights = models.JSONField(
        default=list,
        help_text="AI-generated insights from heatmap analysis"
    )
    optimization_suggestions = models.JSONField(
        default=list,
        help_text="Suggested optimizations based on analysis"
    )
    
    # Comparison with previous analysis
    previous_analysis = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='next_analysis'
    )
    improvement_metrics = models.JSONField(default=dict, help_text="Comparison with previous period")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'heatmap_analyses'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.form.title} - {self.analysis_type} ({self.start_date} to {self.end_date})"


# ============================================================================
# INDUSTRY BENCHMARKING
# ============================================================================

class IndustryBenchmark(models.Model):
    """Industry benchmark data for form performance comparison"""
    INDUSTRIES = [
        ('healthcare', 'Healthcare'),
        ('finance', 'Finance'),
        ('education', 'Education'),
        ('ecommerce', 'E-Commerce'),
        ('saas', 'SaaS'),
        ('real_estate', 'Real Estate'),
        ('hospitality', 'Hospitality'),
        ('nonprofit', 'Non-Profit'),
        ('consulting', 'Consulting'),
        ('other', 'Other'),
    ]
    
    FORM_TYPES = [
        ('contact', 'Contact Form'),
        ('registration', 'Registration'),
        ('checkout', 'Checkout'),
        ('survey', 'Survey'),
        ('lead_gen', 'Lead Generation'),
        ('application', 'Application'),
        ('booking', 'Booking'),
        ('feedback', 'Feedback'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    industry = models.CharField(max_length=50, choices=INDUSTRIES)
    form_type = models.CharField(max_length=50, choices=FORM_TYPES)
    
    # Benchmark metrics
    avg_conversion_rate = models.FloatField(help_text="Average conversion rate %")
    avg_completion_rate = models.FloatField(help_text="Average completion rate %")
    avg_abandonment_rate = models.FloatField(help_text="Average abandonment rate %")
    avg_time_to_complete = models.FloatField(help_text="Average time to complete in seconds")
    avg_fields_count = models.FloatField(help_text="Average number of fields")
    
    # Field performance benchmarks
    field_metrics = models.JSONField(
        default=dict,
        help_text="Performance metrics by field type"
    )
    
    # Top performing patterns
    best_practices = models.JSONField(default=list, help_text="Industry best practices")
    common_mistakes = models.JSONField(default=list, help_text="Common mistakes to avoid")
    
    # Statistical data
    sample_size = models.IntegerField(help_text="Number of forms in benchmark")
    percentile_data = models.JSONField(default=dict, help_text="Percentile distribution")
    
    # Period
    period = models.CharField(max_length=20, help_text="e.g., 2024-Q4")
    valid_from = models.DateField()
    valid_until = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'industry_benchmarks'
        unique_together = [['industry', 'form_type', 'period']]
    
    def __str__(self):
        return f"{self.industry} - {self.form_type} ({self.period})"


class FormBenchmarkComparison(models.Model):
    """Compare form performance against industry benchmarks"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='benchmark_comparisons')
    benchmark = models.ForeignKey(IndustryBenchmark, on_delete=models.CASCADE)
    
    # Form's metrics
    form_conversion_rate = models.FloatField()
    form_completion_rate = models.FloatField()
    form_abandonment_rate = models.FloatField()
    form_avg_time = models.FloatField()
    
    # Comparison results
    conversion_vs_benchmark = models.FloatField(help_text="Percentage above/below benchmark")
    completion_vs_benchmark = models.FloatField()
    abandonment_vs_benchmark = models.FloatField()
    time_vs_benchmark = models.FloatField()
    
    # Percentile rankings
    conversion_percentile = models.IntegerField(help_text="Percentile rank 1-100")
    completion_percentile = models.IntegerField()
    overall_percentile = models.IntegerField()
    
    # AI recommendations
    improvement_recommendations = models.JSONField(
        default=list,
        help_text="AI recommendations to improve vs benchmark"
    )
    
    priority_actions = models.JSONField(
        default=list,
        help_text="Prioritized action items"
    )
    
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'form_benchmark_comparisons'
        ordering = ['-calculated_at']
    
    def __str__(self):
        return f"{self.form.title} vs {self.benchmark.industry} benchmark"
