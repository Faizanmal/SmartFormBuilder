"""
New advanced features models:
- Smart Field Dependencies & Auto-Population
- Submission Bulk Actions & Batch Processing
- Advanced Bot & Spam Detection
- Smart External Validation
- Form Testing & Preview Suite
- Submission Workflow Pipeline
- Smart Form Recommendations Engine
- Form Analytics Export & Scheduling
- Submission Comments System
- Form Cloning & Templates
"""
from django.db import models
import uuid
from django.conf import settings

# Database-agnostic array field
if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
    from django.contrib.postgres.fields import ArrayField
    ArrayFieldType = ArrayField
else:
    # For SQLite and other databases, use JSONField to store arrays
    ArrayFieldType = models.JSONField


# ============================================================================
# SMART FIELD DEPENDENCIES & AUTO-POPULATION
# ============================================================================

class FieldDependency(models.Model):
    """Define dependencies between form fields for auto-population"""
    DEPENDENCY_TYPES = [
        ('api', 'External API'),
        ('database', 'Database Lookup'),
        ('calculation', 'Calculated Value'),
        ('conditional', 'Conditional Logic'),
        ('cross_form', 'Cross-Form Dependency'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='field_dependencies')
    source_field_id = models.CharField(max_length=100, help_text="Field that triggers the dependency")
    target_field_ids = ArrayFieldType(
        models.CharField(max_length=100),
        default=list,
        help_text="Fields to be auto-populated"
    )
    dependency_type = models.CharField(max_length=20, choices=DEPENDENCY_TYPES)
    
    # API Configuration
    api_endpoint = models.URLField(blank=True, help_text="External API endpoint")
    api_method = models.CharField(max_length=10, default='GET', choices=[('GET', 'GET'), ('POST', 'POST')])
    api_headers = models.JSONField(default=dict, blank=True)
    api_params_template = models.JSONField(default=dict, help_text="Parameter mapping template")
    response_mapping = models.JSONField(default=dict, help_text="Map API response to form fields")
    
    # Database Lookup Configuration
    lookup_table = models.CharField(max_length=100, blank=True)
    lookup_query = models.JSONField(default=dict, blank=True)
    
    # Calculation Configuration
    calculation_formula = models.TextField(blank=True, help_text="Python expression for calculation")
    
    # Cache settings
    cache_duration = models.IntegerField(default=3600, help_text="Cache API results in seconds")
    
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text="Execution order priority")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'field_dependencies'
        ordering = ['priority', 'created_at']
        indexes = [
            models.Index(fields=['form', 'source_field_id']),
        ]
    
    def __str__(self):
        return f"{self.form.title} - {self.source_field_id} dependency"


class ExternalAPIProvider(models.Model):
    """Configured external API providers for field auto-population"""
    PROVIDER_TYPES = [
        ('postal', 'Postal/Address Service'),
        ('business', 'Business Registry'),
        ('vehicle', 'Vehicle Information'),
        ('financial', 'Financial Services'),
        ('identity', 'Identity Verification'),
        ('custom', 'Custom API'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    provider_type = models.CharField(max_length=50, choices=PROVIDER_TYPES)
    base_url = models.URLField()
    auth_type = models.CharField(
        max_length=20,
        choices=[('none', 'None'), ('api_key', 'API Key'), ('oauth', 'OAuth'), ('basic', 'Basic Auth')],
        default='api_key'
    )
    credentials = models.JSONField(default=dict, help_text="Encrypted credentials")
    rate_limit = models.IntegerField(default=100, help_text="Requests per minute")
    timeout = models.IntegerField(default=5, help_text="Request timeout in seconds")
    
    # Usage tracking
    total_requests = models.IntegerField(default=0)
    failed_requests = models.IntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'external_api_providers'
    
    def __str__(self):
        return self.name


class FieldAutoPopulationLog(models.Model):
    """Log of field auto-population attempts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dependency = models.ForeignKey(FieldDependency, on_delete=models.CASCADE, related_name='logs')
    submission = models.ForeignKey('forms.Submission', on_delete=models.SET_NULL, null=True, blank=True)
    
    source_value = models.JSONField(help_text="Value that triggered auto-population")
    populated_fields = models.JSONField(default=dict, help_text="Fields and their populated values")
    
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    response_time_ms = models.IntegerField(default=0)
    cache_hit = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'field_autopopulation_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['dependency', '-created_at']),
        ]


# ============================================================================
# SUBMISSION BULK ACTIONS & BATCH PROCESSING
# ============================================================================

class BulkAction(models.Model):
    """Track bulk operations on submissions"""
    ACTION_TYPES = [
        ('approve', 'Bulk Approve'),
        ('reject', 'Bulk Reject'),
        ('delete', 'Bulk Delete'),
        ('export', 'Bulk Export'),
        ('tag', 'Bulk Tag'),
        ('assign', 'Bulk Assign'),
        ('status_change', 'Bulk Status Change'),
        ('transform', 'Data Transformation'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('partial', 'Partially Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='bulk_actions')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='bulk_actions')
    
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Selection criteria
    submission_ids = ArrayFieldType(
        models.UUIDField(),
        default=list,
        help_text="Specific submission IDs"
    )
    filter_criteria = models.JSONField(default=dict, help_text="Query filters for selection")
    
    # Action configuration
    action_params = models.JSONField(default=dict, help_text="Action-specific parameters")
    
    # Progress tracking
    total_submissions = models.IntegerField(default=0)
    processed_submissions = models.IntegerField(default=0)
    successful_submissions = models.IntegerField(default=0)
    failed_submissions = models.IntegerField(default=0)
    
    # Results
    result_data = models.JSONField(default=dict, help_text="Action results and errors")
    export_file_url = models.URLField(blank=True, help_text="For export actions")
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    estimated_completion = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bulk_actions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['form', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.action_type} - {self.total_submissions} submissions"


class BatchProcessingQueue(models.Model):
    """Queue for asynchronous batch processing"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bulk_action = models.ForeignKey(BulkAction, on_delete=models.CASCADE, related_name='queue_items')
    submission = models.ForeignKey('forms.Submission', on_delete=models.CASCADE)
    
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')],
        default='pending'
    )
    retry_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    result = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'batch_processing_queue'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['bulk_action', 'status']),
        ]


# ============================================================================
# ADVANCED BOT & SPAM DETECTION
# ============================================================================

class SpamDetectionConfig(models.Model):
    """Spam detection configuration per form"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='spam_config')
    
    # Detection methods
    honeypot_enabled = models.BooleanField(default=True)
    timing_analysis_enabled = models.BooleanField(default=True)
    pattern_detection_enabled = models.BooleanField(default=True)
    ip_reputation_enabled = models.BooleanField(default=True)
    behavioral_analysis_enabled = models.BooleanField(default=False)
    
    # Thresholds
    min_fill_time_seconds = models.IntegerField(default=3, help_text="Minimum time to fill form")
    max_fill_time_seconds = models.IntegerField(default=3600, help_text="Maximum reasonable time")
    risk_score_threshold = models.IntegerField(default=70, help_text="0-100, block if exceeded")
    
    # Honeypot configuration
    honeypot_field_name = models.CharField(max_length=100, default='website_url')
    
    # Pattern detection
    suspicious_patterns = models.JSONField(
        default=list,
        help_text="Regex patterns for suspicious content"
    )
    blacklisted_emails = ArrayFieldType(
        models.CharField(max_length=255),
        default=list,
        blank=True
    )
    blacklisted_domains = ArrayFieldType(
        models.CharField(max_length=255),
        default=list,
        blank=True
    )
    
    # Actions
    action_on_detection = models.CharField(
        max_length=20,
        choices=[('block', 'Block'), ('flag', 'Flag for Review'), ('challenge', 'Challenge with CAPTCHA')],
        default='flag'
    )
    
    # External services
    captcha_provider = models.CharField(
        max_length=20,
        choices=[('none', 'None'), ('turnstile', 'Cloudflare Turnstile'), ('hcaptcha', 'hCaptcha'), ('recaptcha', 'reCAPTCHA')],
        default='none'
    )
    captcha_site_key = models.CharField(max_length=255, blank=True)
    captcha_secret_key = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'spam_detection_configs'
    
    def __str__(self):
        return f"Spam config for {self.form.title}"


class SpamDetectionLog(models.Model):
    """Log of spam detection attempts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='spam_logs')
    submission = models.ForeignKey('forms.Submission', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Detection results
    risk_score = models.IntegerField(default=0, help_text="0-100 spam probability")
    is_spam = models.BooleanField(default=False)
    detection_reasons = ArrayFieldType(
        models.CharField(max_length=200),
        default=list,
        help_text="Reasons for spam detection"
    )
    
    # Checks performed
    honeypot_triggered = models.BooleanField(default=False)
    timing_suspicious = models.BooleanField(default=False)
    pattern_matched = models.BooleanField(default=False)
    ip_blacklisted = models.BooleanField(default=False)
    behavioral_suspicious = models.BooleanField(default=False)
    
    # Submission details
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    fill_time_seconds = models.IntegerField(default=0)
    
    # Behavioral data
    mouse_movements = models.IntegerField(default=0, help_text="Number of mouse movements")
    keystrokes = models.IntegerField(default=0)
    field_interactions = models.IntegerField(default=0)
    
    # Action taken
    action_taken = models.CharField(
        max_length=20,
        choices=[('allowed', 'Allowed'), ('blocked', 'Blocked'), ('flagged', 'Flagged'), ('challenged', 'Challenged')],
        default='allowed'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'spam_detection_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['form', '-created_at']),
            models.Index(fields=['is_spam']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"Spam check - Score: {self.risk_score}"


class IPReputationCache(models.Model):
    """Cache IP reputation data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ip_address = models.GenericIPAddressField(unique=True)
    
    reputation_score = models.IntegerField(default=50, help_text="0-100, lower is worse")
    is_vpn = models.BooleanField(default=False)
    is_proxy = models.BooleanField(default=False)
    is_tor = models.BooleanField(default=False)
    is_datacenter = models.BooleanField(default=False)
    
    country_code = models.CharField(max_length=2, blank=True)
    asn = models.CharField(max_length=50, blank=True)
    
    total_submissions = models.IntegerField(default=0)
    spam_submissions = models.IntegerField(default=0)
    
    last_seen_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="Cache expiration")
    
    class Meta:
        db_table = 'ip_reputation_cache'
        indexes = [
            models.Index(fields=['ip_address']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.ip_address} - Score: {self.reputation_score}"


# ============================================================================
# SMART EXTERNAL VALIDATION
# ============================================================================

class ExternalValidationRule(models.Model):
    """External validation rules for form fields"""
    VALIDATION_TYPES = [
        ('business_registry', 'Business Registration Number'),
        ('iban', 'IBAN/Bank Account'),
        ('vat', 'VAT Number'),
        ('license', 'Professional License'),
        ('address', 'Address Verification'),
        ('domain', 'Domain Ownership'),
        ('phone_carrier', 'Phone Carrier Lookup'),
        ('email_mx', 'Email MX Record'),
        ('custom', 'Custom Validation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='validation_rules')
    field_id = models.CharField(max_length=100)
    field_label = models.CharField(max_length=255)
    
    validation_type = models.CharField(max_length=50, choices=VALIDATION_TYPES)
    
    # Validation service configuration
    service_provider = models.ForeignKey(
        ExternalAPIProvider,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validation_rules'
    )
    validation_endpoint = models.URLField(blank=True)
    validation_params = models.JSONField(default=dict)
    
    # Validation behavior
    is_required = models.BooleanField(default=False, help_text="Block submission if validation fails")
    show_validation_status = models.BooleanField(default=True, help_text="Show real-time validation to user")
    cache_results = models.BooleanField(default=True)
    cache_duration = models.IntegerField(default=86400, help_text="Cache duration in seconds")
    
    # Error messages
    error_message_invalid = models.CharField(max_length=500, default="This value could not be validated")
    error_message_service_error = models.CharField(max_length=500, default="Validation service unavailable")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'external_validation_rules'
        unique_together = [['form', 'field_id']]
    
    def __str__(self):
        return f"{self.form.title} - {self.field_label} validation"


class ValidationLog(models.Model):
    """Log of external validation attempts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    validation_rule = models.ForeignKey(ExternalValidationRule, on_delete=models.CASCADE, related_name='logs')
    submission = models.ForeignKey('forms.Submission', on_delete=models.SET_NULL, null=True, blank=True)
    
    input_value = models.CharField(max_length=500)
    is_valid = models.BooleanField(default=False)
    validation_details = models.JSONField(default=dict, help_text="Detailed validation results")
    
    response_time_ms = models.IntegerField(default=0)
    cache_hit = models.BooleanField(default=False)
    
    success = models.BooleanField(default=True, help_text="Whether validation service responded")
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'validation_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['validation_rule', '-created_at']),
        ]


# ============================================================================
# FORM TESTING & PREVIEW SUITE
# ============================================================================

class FormTestSuite(models.Model):
    """Test suite for a form"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='test_suites')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Test configuration
    test_types = ArrayFieldType(
        models.CharField(max_length=50),
        default=list,
        help_text="Types of tests to run: accessibility, performance, integration, etc."
    )
    
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'form_test_suites'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.form.title} - {self.name}"


class FormTestRun(models.Model):
    """Individual test run execution"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test_suite = models.ForeignKey(FormTestSuite, on_delete=models.CASCADE, related_name='test_runs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Test sample data
    sample_data = models.JSONField(default=dict, help_text="Sample data used for testing")
    
    # Results
    total_tests = models.IntegerField(default=0)
    passed_tests = models.IntegerField(default=0)
    failed_tests = models.IntegerField(default=0)
    warnings = models.IntegerField(default=0)
    
    test_results = models.JSONField(default=dict, help_text="Detailed test results")
    
    # Dry-run settings
    dry_run_webhooks = models.BooleanField(default=True, help_text="Don't actually send webhooks")
    dry_run_integrations = models.BooleanField(default=True, help_text="Don't trigger real integrations")
    
    # Performance metrics
    execution_time_ms = models.IntegerField(default=0)
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'form_test_runs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['test_suite', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Test run {self.id} - {self.status}"


class FormPreviewSession(models.Model):
    """Preview session for testing form as different user types"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='preview_sessions')
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE)
    
    # Preview configuration
    preview_as_role = models.CharField(max_length=50, blank=True, help_text="Preview as specific user role")
    device_type = models.CharField(
        max_length=20,
        choices=[('desktop', 'Desktop'), ('mobile', 'Mobile'), ('tablet', 'Tablet')],
        default='desktop'
    )
    browser_type = models.CharField(max_length=50, blank=True)
    
    # Session data
    session_token = models.CharField(max_length=255, unique=True)
    test_data = models.JSONField(default=dict, help_text="Pre-filled test data")
    
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'form_preview_sessions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Preview {self.form.title} - {self.device_type}"


class AccessibilityTestResult(models.Model):
    """Automated accessibility test results"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='accessibility_tests')
    test_run = models.ForeignKey(FormTestRun, on_delete=models.CASCADE, null=True, blank=True)
    
    # WCAG compliance
    wcag_level_tested = models.CharField(max_length=10, default='AA')
    is_compliant = models.BooleanField(default=False)
    
    # Issue counts
    critical_issues = models.IntegerField(default=0)
    serious_issues = models.IntegerField(default=0)
    moderate_issues = models.IntegerField(default=0)
    minor_issues = models.IntegerField(default=0)
    
    # Detailed issues
    issues = models.JSONField(default=list, help_text="List of accessibility issues with locations")
    
    # Scores
    accessibility_score = models.IntegerField(default=0, help_text="0-100 accessibility score")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'accessibility_test_results'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"A11y test for {self.form.title} - Score: {self.accessibility_score}"


# ============================================================================
# SUBMISSION WORKFLOW PIPELINE SYSTEM
# ============================================================================

class WorkflowPipeline(models.Model):
    """Define submission workflow pipeline stages"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='workflow_pipelines')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Stages configuration
    stages = models.JSONField(
        default=list,
        help_text="List of workflow stages with configuration"
    )
    
    # SLA Configuration
    enable_sla_tracking = models.BooleanField(default=False)
    default_sla_hours = models.IntegerField(default=24, help_text="Default SLA for each stage")
    
    # Auto-progression rules
    auto_progression_rules = models.JSONField(
        default=dict,
        help_text="Rules for automatic stage progression"
    )
    
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False, help_text="Default pipeline for this form")
    
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'workflow_pipelines'
        ordering = ['form', 'created_at']
    
    def __str__(self):
        return f"{self.form.title} - {self.name}"


class WorkflowStage(models.Model):
    """Individual workflow stage definition"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pipeline = models.ForeignKey(WorkflowPipeline, on_delete=models.CASCADE, related_name='stage_definitions')
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    
    order = models.IntegerField(default=0)
    color = models.CharField(max_length=7, default='#3B82F6', help_text="Hex color code")
    icon = models.CharField(max_length=50, blank=True)
    
    # Stage permissions
    can_view_roles = ArrayFieldType(
        models.CharField(max_length=50),
        default=list,
        blank=True,
        help_text="Roles that can view submissions in this stage"
    )
    can_edit_roles = ArrayFieldType(
        models.CharField(max_length=50),
        default=list,
        blank=True,
        help_text="Roles that can edit submissions in this stage"
    )
    can_progress_roles = ArrayFieldType(
        models.CharField(max_length=50),
        default=list,
        blank=True,
        help_text="Roles that can move submissions to next stage"
    )
    
    # SLA for this stage
    sla_hours = models.IntegerField(null=True, blank=True, help_text="Override pipeline SLA")
    
    # Notifications
    notify_on_enter = models.BooleanField(default=False)
    notify_on_sla_breach = models.BooleanField(default=True)
    notification_recipients = ArrayFieldType(
        models.EmailField(),
        default=list,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'workflow_stages'
        ordering = ['pipeline', 'order']
        unique_together = [['pipeline', 'slug']]
    
    def __str__(self):
        return f"{self.pipeline.name} - {self.name}"


class SubmissionWorkflowStatus(models.Model):
    """Track submission progress through workflow pipeline"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.OneToOneField('forms.Submission', on_delete=models.CASCADE, related_name='workflow_status')
    pipeline = models.ForeignKey(WorkflowPipeline, on_delete=models.CASCADE)
    current_stage = models.ForeignKey(WorkflowStage, on_delete=models.PROTECT, related_name='current_submissions')
    
    # Assignment
    assigned_to = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_submissions')
    assigned_at = models.DateTimeField(null=True, blank=True)
    
    # Timing
    entered_current_stage_at = models.DateTimeField(auto_now_add=True)
    sla_deadline = models.DateTimeField(null=True, blank=True)
    is_sla_breached = models.BooleanField(default=False)
    
    # Metadata
    notes = models.TextField(blank=True)
    tags = ArrayFieldType(
        models.CharField(max_length=100),
        default=list,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'submission_workflow_statuses'
        indexes = [
            models.Index(fields=['pipeline', 'current_stage']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['is_sla_breached']),
        ]
    
    def __str__(self):
        return f"Submission {self.submission.id} - {self.current_stage.name}"


class WorkflowStageTransition(models.Model):
    """Log of submission transitions between stages"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey('forms.Submission', on_delete=models.CASCADE, related_name='stage_transitions')
    from_stage = models.ForeignKey(WorkflowStage, on_delete=models.CASCADE, related_name='transitions_from', null=True, blank=True)
    to_stage = models.ForeignKey(WorkflowStage, on_delete=models.CASCADE, related_name='transitions_to')
    
    transitioned_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    transition_reason = models.TextField(blank=True)
    
    # Auto vs Manual
    is_automatic = models.BooleanField(default=False)
    
    # Timing
    time_in_previous_stage = models.IntegerField(default=0, help_text="Minutes spent in previous stage")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'workflow_stage_transitions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['submission', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.from_stage} → {self.to_stage}"


# ============================================================================
# SMART FORM RECOMMENDATIONS ENGINE
# ============================================================================

class FormOptimizationRecommendation(models.Model):
    """AI-powered optimization recommendations"""
    RECOMMENDATION_TYPES = [
        ('field_order', 'Field Reordering'),
        ('field_removal', 'Remove Field'),
        ('field_addition', 'Add Field'),
        ('field_type', 'Change Field Type'),
        ('label_improvement', 'Improve Label'),
        ('validation_adjustment', 'Adjust Validation'),
        ('conditional_logic', 'Add Conditional Logic'),
        ('styling', 'Styling Improvement'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('applied', 'Applied'),
        ('dismissed', 'Dismissed'),
        ('testing', 'In A/B Test'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='optimization_recommendations')
    
    recommendation_type = models.CharField(max_length=50, choices=RECOMMENDATION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Recommendation details
    title = models.CharField(max_length=200)
    description = models.TextField()
    reasoning = models.TextField(help_text="Why this recommendation was made")
    
    # Impact estimation
    estimated_improvement = models.FloatField(help_text="Estimated % improvement in conversion")
    confidence_score = models.FloatField(default=0.5, help_text="0-1 confidence in recommendation")
    
    # Implementation
    changes_json = models.JSONField(default=dict, help_text="Specific changes to apply")
    affected_fields = ArrayFieldType(
        models.CharField(max_length=100),
        default=list,
        blank=True
    )
    
    # Tracking
    applied_at = models.DateTimeField(null=True, blank=True)
    applied_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Results (if applied)
    actual_improvement = models.FloatField(null=True, blank=True, help_text="Measured improvement after applying")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'form_optimization_recommendations'
        ordering = ['-confidence_score', '-created_at']
        indexes = [
            models.Index(fields=['form', 'status']),
        ]
    
    def __str__(self):
        return f"{self.form.title} - {self.title}"


class FormBenchmark(models.Model):
    """Benchmark data comparing form performance"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='benchmarks')
    
    # Comparison category
    category = models.CharField(max_length=100, help_text="Form category for comparison")
    industry = models.CharField(max_length=100, blank=True)
    
    # Metrics
    form_conversion_rate = models.FloatField()
    category_avg_conversion_rate = models.FloatField()
    category_median_conversion_rate = models.FloatField()
    percentile_rank = models.IntegerField(help_text="Where this form ranks (0-100)")
    
    form_completion_time = models.FloatField(help_text="Seconds")
    category_avg_completion_time = models.FloatField()
    
    form_field_count = models.IntegerField()
    category_avg_field_count = models.FloatField()
    
    # Insights
    strengths = ArrayFieldType(
        models.CharField(max_length=200),
        default=list,
        blank=True
    )
    weaknesses = ArrayFieldType(
        models.CharField(max_length=200),
        default=list,
        blank=True
    )
    
    benchmark_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'form_benchmarks'
        ordering = ['-benchmark_date']
    
    def __str__(self):
        return f"{self.form.title} - Benchmark {self.benchmark_date}"


class OptimizationReport(models.Model):
    """Weekly optimization reports"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='optimization_reports')
    
    report_period_start = models.DateField()
    report_period_end = models.DateField()
    
    # Summary metrics
    total_recommendations = models.IntegerField(default=0)
    high_priority_recommendations = models.IntegerField(default=0)
    
    # Performance changes
    conversion_rate_change = models.FloatField(default=0, help_text="% change")
    completion_time_change = models.FloatField(default=0, help_text="% change")
    drop_off_rate_change = models.FloatField(default=0, help_text="% change")
    
    # Report data
    report_data = models.JSONField(default=dict, help_text="Detailed report content")
    
    # Distribution
    sent_to_users = ArrayFieldType(
        models.UUIDField(),
        default=list,
        blank=True,
        help_text="User IDs who received this report"
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'optimization_reports'
        ordering = ['-report_period_end']
    
    def __str__(self):
        return f"{self.form.title} - Report {self.report_period_start} to {self.report_period_end}"


# ============================================================================
# FORM ANALYTICS EXPORT & SCHEDULING (BONUS FEATURE #1)
# ============================================================================

class SubmissionComment(models.Model):
    """Comments and notes on submissions for team collaboration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey('forms.Submission', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='submission_comments')
    
    comment = models.TextField()
    
    # Threading
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Mentions
    mentioned_users = models.ManyToManyField('users.User', blank=True, related_name='mentioned_in_comments')
    
    # Attachments
    attachments = models.JSONField(default=list, blank=True, help_text="File attachments")
    
    # Status
    is_internal = models.BooleanField(default=True, help_text="Internal comment not visible to submitter")
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'submission_comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['submission', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.user.email} on submission {self.submission.id}"


class SubmissionNote(models.Model):
    """Quick notes and tags for submissions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey('forms.Submission', on_delete=models.CASCADE, related_name='notes')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    
    note_type = models.CharField(
        max_length=20,
        choices=[('note', 'Note'), ('flag', 'Flag'), ('reminder', 'Reminder'), ('todo', 'To-Do')],
        default='note'
    )
    
    content = models.TextField()
    color = models.CharField(max_length=7, default='#FCD34D', help_text="Hex color for visual organization")
    
    # For reminders
    remind_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'submission_notes'
        ordering = ['-created_at']


# ============================================================================
# FORM CLONING & TEMPLATES (BONUS FEATURE #3)
# ============================================================================

class FormClone(models.Model):
    """Track form cloning operations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_form = models.ForeignKey('forms.Form', on_delete=models.SET_NULL, null=True, related_name='clones')
    cloned_form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='clone_source')
    
    cloned_by = models.ForeignKey('users.User', on_delete=models.CASCADE)
    
    # Clone configuration
    include_logic = models.BooleanField(default=True)
    include_integrations = models.BooleanField(default=False)
    include_styling = models.BooleanField(default=True)
    include_settings = models.BooleanField(default=True)
    
    modifications = models.JSONField(default=dict, help_text="Modifications made during cloning")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'form_clones'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Clone of {self.original_form.title if self.original_form else 'deleted form'}"


class CustomFormTemplate(models.Model):
    """User-created form templates"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Template data
    schema_json = models.JSONField(help_text="Form schema template")
    preview_image_url = models.URLField(blank=True)
    
    # Categorization
    category = models.CharField(max_length=100)
    tags = ArrayFieldType(
        models.CharField(max_length=50),
        default=list,
        blank=True
    )
    
    # Ownership & Visibility
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='form_templates')
    is_public = models.BooleanField(default=False, help_text="Available to all users")
    team = models.ForeignKey('users.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='team_templates')
    
    # Usage stats
    usage_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'custom_form_templates'
        ordering = ['-usage_count', '-created_at']
    
    def __str__(self):
        return self.name


class TemplateFavorite(models.Model):
    """User favorites for quick template access"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='template_favorites')
    template = models.ForeignKey(CustomFormTemplate, on_delete=models.CASCADE, related_name='favorited_by')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'template_favorites'
        unique_together = [['user', 'template']]
