"""
Advanced third-party integrations marketplace models
"""
from django.db import models
import uuid


class IntegrationProvider(models.Model):
    """Third-party integration providers available in the marketplace"""
    CATEGORY_CHOICES = [
        ('crm', 'CRM'),
        ('email', 'Email Marketing'),
        ('productivity', 'Productivity'),
        ('analytics', 'Analytics'),
        ('payment', 'Payment'),
        ('storage', 'Storage'),
        ('communication', 'Communication'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    logo_url = models.URLField(blank=True)
    api_base_url = models.URLField()
    auth_type = models.CharField(
        max_length=20,
        choices=[('oauth', 'OAuth 2.0'), ('api_key', 'API Key'), ('basic', 'Basic Auth')],
        default='api_key'
    )
    documentation_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    popularity_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'integration_providers'
        ordering = ['-popularity_score', 'name']
    
    def __str__(self):
        return self.name


class IntegrationConnection(models.Model):
    """User's connection to a third-party service"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='integration_connections')
    provider = models.ForeignKey(IntegrationProvider, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, help_text="User-friendly name for this connection")
    credentials = models.JSONField(
        default=dict,
        help_text="Encrypted auth tokens, API keys, or OAuth tokens"
    )
    oauth_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="OAuth tokens, refresh tokens, expiry"
    )
    is_active = models.BooleanField(default=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    error_count = models.IntegerField(default=0)
    last_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'integration_connections'
        unique_together = [['user', 'provider', 'name']]
    
    def __str__(self):
        return f"{self.user.email} - {self.provider.name}"


class IntegrationWorkflow(models.Model):
    """Zapier-style automation workflows"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='workflows')
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='workflows', null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    trigger_type = models.CharField(
        max_length=50,
        choices=[
            ('form_submit', 'New Form Submission'),
            ('form_complete', 'Form Completed'),
            ('field_value', 'Specific Field Value'),
            ('schedule', 'Scheduled'),
        ]
    )
    trigger_config = models.JSONField(default=dict, help_text="Trigger conditions and filters")
    actions = models.JSONField(
        default=list,
        help_text="List of actions to execute (e.g., create CRM contact, send email)"
    )
    is_active = models.BooleanField(default=True)
    execution_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    last_executed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'integration_workflows'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class WebhookEndpoint(models.Model):
    """Custom webhook configurations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='webhooks')
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='webhooks')
    name = models.CharField(max_length=200)
    url = models.URLField()
    method = models.CharField(
        max_length=10,
        choices=[('POST', 'POST'), ('PUT', 'PUT'), ('PATCH', 'PATCH')],
        default='POST'
    )
    headers = models.JSONField(default=dict, help_text="Custom HTTP headers")
    payload_template = models.TextField(
        blank=True,
        help_text="Custom payload template (uses Jinja2 syntax)"
    )
    events = models.JSONField(
        default=list,
        help_text="Events that trigger this webhook (e.g., ['submission.created', 'submission.updated'])"
    )
    retry_count = models.IntegerField(default=3, help_text="Number of retry attempts on failure")
    retry_delay = models.IntegerField(default=60, help_text="Delay between retries in seconds")
    timeout = models.IntegerField(default=30, help_text="Request timeout in seconds")
    is_active = models.BooleanField(default=True)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'webhook_endpoints'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.form.title}"


class WebhookLog(models.Model):
    """Log of webhook execution attempts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    webhook = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE, related_name='logs')
    submission = models.ForeignKey('forms.Submission', on_delete=models.CASCADE, null=True, blank=True)
    event = models.CharField(max_length=100)
    status_code = models.IntegerField(null=True)
    request_payload = models.JSONField(default=dict)
    response_body = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    duration_ms = models.IntegerField(null=True, help_text="Request duration in milliseconds")
    retry_attempt = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'webhook_logs_marketplace'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['webhook', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.webhook.name} - {self.event} - {self.status_code}"


class IntegrationTemplate(models.Model):
    """Pre-built integration templates for common use cases"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(IntegrationProvider, on_delete=models.CASCADE, related_name='templates')
    name = models.CharField(max_length=200)
    description = models.TextField()
    use_case = models.CharField(max_length=200, help_text="e.g., 'Sync leads to Google Sheets'")
    icon = models.CharField(max_length=50, blank=True)
    config_template = models.JSONField(
        default=dict,
        help_text="Pre-configured workflow or webhook settings"
    )
    required_fields = models.JSONField(
        default=list,
        help_text="List of fields user must configure"
    )
    is_featured = models.BooleanField(default=False)
    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'integration_templates'
        ordering = ['-is_featured', '-usage_count']
    
    def __str__(self):
        return f"{self.name} - {self.provider.name}"
