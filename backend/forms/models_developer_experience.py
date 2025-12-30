"""
Developer Experience Models

Features:
- API Versioning
- Plugin Architecture
- Custom Field SDK
- Webhook Enhancements
- SDK Generation
- Developer Portal
"""
import uuid
from django.db import models
from django.conf import settings


class APIVersion(models.Model):
    """
    API version management
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    version = models.CharField(max_length=20, unique=True)  # e.g., 'v1', 'v2'
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('development', 'Development'),
            ('beta', 'Beta'),
            ('stable', 'Stable'),
            ('deprecated', 'Deprecated'),
            ('retired', 'Retired'),
        ],
        default='development'
    )
    
    # Details
    release_date = models.DateField(null=True)
    deprecation_date = models.DateField(null=True)
    sunset_date = models.DateField(null=True)
    
    # Documentation
    changelog = models.TextField(blank=True)
    breaking_changes = models.JSONField(default=list)
    migration_guide = models.TextField(blank=True)
    
    # Features
    supported_features = models.JSONField(default=list)
    
    # Stats
    active_consumers = models.IntegerField(default=0)
    request_count_30d = models.BigIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-version']
    
    def __str__(self):
        return f"API {self.version} ({self.status})"


class FormsAPIKey(models.Model):
    """
    API key management with scopes and rate limits
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='forms_api_keys'
    )
    
    # Key info
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    key_prefix = models.CharField(max_length=8, help_text="First 8 chars of key")
    key_hash = models.CharField(max_length=64, unique=True)
    
    # Scopes
    scopes = models.JSONField(
        default=list,
        help_text="List of allowed scopes"
    )
    
    # Restrictions
    allowed_origins = models.JSONField(default=list)
    allowed_ips = models.JSONField(default=list)
    api_version = models.CharField(max_length=20, default='v1')
    
    # Rate limiting
    rate_limit_per_minute = models.IntegerField(default=60)
    rate_limit_per_day = models.IntegerField(default=10000)
    
    # Status
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True)
    
    # Usage stats
    last_used_at = models.DateTimeField(null=True)
    total_requests = models.BigIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']


class APIUsageLog(models.Model):
    """API usage logging for analytics"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    api_key = models.ForeignKey(
        FormsAPIKey,
        on_delete=models.CASCADE,
        related_name='usage_logs'
    )
    
    # Request details
    method = models.CharField(max_length=10)
    endpoint = models.CharField(max_length=500)
    status_code = models.IntegerField()
    response_time_ms = models.FloatField()
    
    # Additional info
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    request_size_bytes = models.IntegerField(default=0)
    response_size_bytes = models.IntegerField(default=0)
    
    # Error info
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['api_key', 'created_at']),
            models.Index(fields=['endpoint', 'created_at']),
        ]


class Plugin(models.Model):
    """
    Plugin/extension for the form builder
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic info
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    # Author
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='authored_plugins'
    )
    author_name = models.CharField(max_length=200, blank=True)
    author_url = models.URLField(blank=True)
    
    # Repository
    repository_url = models.URLField(blank=True)
    homepage_url = models.URLField(blank=True)
    
    # Version
    version = models.CharField(max_length=50)
    min_platform_version = models.CharField(max_length=20, blank=True)
    max_platform_version = models.CharField(max_length=20, blank=True)
    
    # Type
    plugin_type = models.CharField(
        max_length=50,
        choices=[
            ('field_type', 'Custom Field Type'),
            ('validator', 'Validator'),
            ('integration', 'Integration'),
            ('theme', 'Theme'),
            ('analytics', 'Analytics'),
            ('submission_handler', 'Submission Handler'),
            ('ui_extension', 'UI Extension'),
        ],
        default='field_type'
    )
    
    # Configuration
    config_schema = models.JSONField(
        default=dict,
        help_text="JSON Schema for plugin configuration"
    )
    default_config = models.JSONField(default=dict)
    
    # Code/Assets
    entry_point = models.CharField(max_length=200, blank=True)
    bundle_url = models.URLField(blank=True)
    
    # Hooks
    hooks = models.JSONField(
        default=list,
        help_text="List of hooks this plugin uses"
    )
    
    # Permissions
    required_permissions = models.JSONField(default=list)
    
    # Status
    is_published = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Stats
    install_count = models.IntegerField(default=0)
    rating_average = models.FloatField(default=0)
    rating_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-install_count']
    
    def __str__(self):
        return f"{self.name} v{self.version}"


class PluginVersion(models.Model):
    """Version history for plugins"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    plugin = models.ForeignKey(
        Plugin,
        on_delete=models.CASCADE,
        related_name='versions'
    )
    
    version = models.CharField(max_length=50)
    changelog = models.TextField(blank=True)
    
    bundle_url = models.URLField()
    bundle_hash = models.CharField(max_length=64)
    
    is_stable = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['plugin', 'version']
        ordering = ['-created_at']


class PluginInstallation(models.Model):
    """Plugin installation for a user/workspace"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    plugin = models.ForeignKey(
        Plugin,
        on_delete=models.CASCADE,
        related_name='installations'
    )
    
    # Owner can be user or workspace
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='installed_plugins'
    )
    workspace = models.ForeignKey(
        'forms.TeamWorkspace',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='installed_plugins'
    )
    
    # Configuration
    config = models.JSONField(default=dict)
    
    # Status
    is_enabled = models.BooleanField(default=True)
    installed_version = models.CharField(max_length=50)
    
    installed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['plugin', 'user'], ['plugin', 'workspace']]


class CustomFieldType(models.Model):
    """
    Custom field type definition (SDK for custom fields)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic info
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    
    # Owner
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='custom_field_types'
    )
    
    # Field definition
    field_schema = models.JSONField(
        default=dict,
        help_text="JSON Schema for field value"
    )
    
    config_schema = models.JSONField(
        default=dict,
        help_text="JSON Schema for field configuration options"
    )
    
    default_config = models.JSONField(default=dict)
    
    # Rendering
    render_component = models.TextField(
        blank=True,
        help_text="React component code for rendering"
    )
    
    edit_component = models.TextField(
        blank=True,
        help_text="React component for editing field config"
    )
    
    # Validation
    validation_rules = models.JSONField(default=list)
    custom_validator = models.TextField(
        blank=True,
        help_text="JavaScript validation function"
    )
    
    # Storage
    storage_type = models.CharField(
        max_length=20,
        choices=[
            ('string', 'String'),
            ('number', 'Number'),
            ('boolean', 'Boolean'),
            ('array', 'Array'),
            ('object', 'Object'),
            ('file', 'File'),
        ],
        default='string'
    )
    
    # Features
    supports_multi = models.BooleanField(default=False)
    supports_conditional = models.BooleanField(default=True)
    supports_prefill = models.BooleanField(default=True)
    supports_calculation = models.BooleanField(default=False)
    
    # Status
    is_published = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class WebhookSigningKey(models.Model):
    """
    Webhook signing key for secure webhook delivery
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='webhook_signing_keys'
    )
    
    # Key info
    name = models.CharField(max_length=200)
    key_id = models.CharField(max_length=32, unique=True)
    secret_hash = models.CharField(max_length=64)
    
    # Algorithm
    algorithm = models.CharField(
        max_length=20,
        choices=[
            ('hmac-sha256', 'HMAC-SHA256'),
            ('hmac-sha512', 'HMAC-SHA512'),
            ('ed25519', 'Ed25519'),
        ],
        default='hmac-sha256'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    rotated_at = models.DateTimeField(null=True)
    expires_at = models.DateTimeField(null=True)


class WebhookDelivery(models.Model):
    """
    Webhook delivery tracking
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Reference to webhook endpoint
    webhook_endpoint = models.ForeignKey(
        'forms.WebhookEndpoint',
        on_delete=models.CASCADE,
        related_name='deliveries'
    )
    
    # Event
    event_type = models.CharField(max_length=100)
    event_id = models.CharField(max_length=100)
    
    # Payload
    payload = models.JSONField()
    
    # Delivery details
    attempt = models.IntegerField(default=1)
    max_attempts = models.IntegerField(default=3)
    
    # Request
    request_url = models.URLField()
    request_headers = models.JSONField(default=dict)
    
    # Response
    response_status = models.IntegerField(null=True)
    response_headers = models.JSONField(default=dict)
    response_body = models.TextField(blank=True)
    response_time_ms = models.FloatField(null=True)
    
    # Signature
    signature = models.CharField(max_length=200, blank=True)
    signature_header = models.CharField(max_length=100, default='X-Signature-256')
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('success', 'Success'),
            ('failed', 'Failed'),
            ('retrying', 'Retrying'),
        ],
        default='pending'
    )
    
    error_message = models.TextField(blank=True)
    
    scheduled_at = models.DateTimeField()
    delivered_at = models.DateTimeField(null=True)
    next_retry_at = models.DateTimeField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class SDKGenerator(models.Model):
    """
    SDK generation configuration
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sdk_generators'
    )
    
    name = models.CharField(max_length=200)
    
    # Target language/framework
    target = models.CharField(
        max_length=50,
        choices=[
            ('typescript', 'TypeScript'),
            ('javascript', 'JavaScript'),
            ('python', 'Python'),
            ('ruby', 'Ruby'),
            ('go', 'Go'),
            ('php', 'PHP'),
            ('java', 'Java'),
            ('csharp', 'C#'),
            ('swift', 'Swift'),
            ('kotlin', 'Kotlin'),
        ]
    )
    
    # API version
    api_version = models.CharField(max_length=20, default='v1')
    
    # Configuration
    config = models.JSONField(
        default=dict,
        help_text="SDK generation configuration"
    )
    
    # Generated SDK
    package_name = models.CharField(max_length=200)
    package_version = models.CharField(max_length=50, default='1.0.0')
    
    last_generated_at = models.DateTimeField(null=True)
    download_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class DeveloperPortal(models.Model):
    """
    Developer portal configuration
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='developer_portals'
    )
    
    # Portal info
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    # Branding
    logo_url = models.URLField(blank=True)
    primary_color = models.CharField(max_length=7, default='#0066cc')
    custom_css = models.TextField(blank=True)
    
    # Content
    welcome_message = models.TextField(blank=True)
    getting_started = models.TextField(blank=True)
    
    # Features
    show_api_reference = models.BooleanField(default=True)
    show_sdk_downloads = models.BooleanField(default=True)
    show_webhooks = models.BooleanField(default=True)
    show_playground = models.BooleanField(default=True)
    show_changelog = models.BooleanField(default=True)
    
    # Access
    is_public = models.BooleanField(default=False)
    require_api_key = models.BooleanField(default=True)
    
    # Analytics
    track_usage = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name


class APIPlayground(models.Model):
    """
    API playground/sandbox environment
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    portal = models.ForeignKey(
        DeveloperPortal,
        on_delete=models.CASCADE,
        related_name='playgrounds'
    )
    
    # Playground config
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Example requests
    examples = models.JSONField(
        default=list,
        help_text="Pre-configured example requests"
    )
    
    # Sandbox data
    sandbox_forms = models.JSONField(default=list)
    sandbox_submissions = models.JSONField(default=list)
    
    # Rate limiting for playground
    rate_limit_per_minute = models.IntegerField(default=30)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CodeSample(models.Model):
    """
    Code samples for documentation
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Context
    endpoint = models.CharField(max_length=200)
    method = models.CharField(max_length=10)
    
    # Sample
    language = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    code = models.TextField()
    
    # Dependencies
    dependencies = models.JSONField(default=list)
    
    # Ordering
    order = models.IntegerField(default=0)
    
    is_published = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['endpoint', 'order']


class ErrorCode(models.Model):
    """
    API error code documentation
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    code = models.CharField(max_length=50, unique=True)
    http_status = models.IntegerField()
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Resolution
    possible_causes = models.JSONField(default=list)
    resolution_steps = models.JSONField(default=list)
    
    # Related
    related_docs = models.JSONField(default=list)
    
    is_published = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code}: {self.title}"


class Changelog(models.Model):
    """
    API changelog entries
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    version = models.CharField(max_length=50)
    release_date = models.DateField()
    
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    
    # Changes
    new_features = models.JSONField(default=list)
    improvements = models.JSONField(default=list)
    bug_fixes = models.JSONField(default=list)
    breaking_changes = models.JSONField(default=list)
    deprecations = models.JSONField(default=list)
    
    # Full changelog
    full_changelog = models.TextField(blank=True)
    
    # Status
    is_published = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-release_date']
    
    def __str__(self):
        return f"v{self.version} - {self.title}"


class RateLimitTier(models.Model):
    """
    Rate limit tier configuration
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    # Limits
    requests_per_minute = models.IntegerField(default=60)
    requests_per_hour = models.IntegerField(default=1000)
    requests_per_day = models.IntegerField(default=10000)
    
    # Burst
    burst_limit = models.IntegerField(default=100)
    
    # Features
    priority_queue = models.BooleanField(default=False)
    dedicated_support = models.BooleanField(default=False)
    
    # Pricing
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.name


class DeveloperFeedback(models.Model):
    """
    Developer feedback on API/documentation
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Source
    page_url = models.URLField()
    endpoint = models.CharField(max_length=200, blank=True)
    
    # Feedback
    rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        null=True
    )
    feedback_type = models.CharField(
        max_length=50,
        choices=[
            ('bug', 'Bug Report'),
            ('improvement', 'Improvement'),
            ('question', 'Question'),
            ('other', 'Other'),
        ],
        default='other'
    )
    
    message = models.TextField()
    
    # User
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    email = models.EmailField(blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('new', 'New'),
            ('reviewed', 'Reviewed'),
            ('actioned', 'Actioned'),
            ('closed', 'Closed'),
        ],
        default='new'
    )
    
    response = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
