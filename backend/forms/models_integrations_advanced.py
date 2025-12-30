"""
Integration & Ecosystem Expansion Models

Features:
- Webhook Transformation Engine
- API Marketplace
- Federated Form Sharing
- SSO Integration Hub (SAML, OAuth, LDAP)
- ERP System Connectors
- Legacy System Bridges
- GraphQL Support
- Advanced Rate Limiting
"""
from django.db import models
import uuid


# ============================================================================
# WEBHOOK TRANSFORMATION ENGINE
# ============================================================================

class WebhookTransformer(models.Model):
    """Transform webhooks between different service formats"""
    TRANSFORM_TYPES = [
        ('json_to_json', 'JSON to JSON'),
        ('json_to_xml', 'JSON to XML'),
        ('json_to_form', 'JSON to Form Data'),
        ('custom', 'Custom Transformation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='webhook_transformers')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    transform_type = models.CharField(max_length=30, choices=TRANSFORM_TYPES, default='json_to_json')
    
    # Transformation rules
    field_mappings = models.JSONField(
        default=dict,
        help_text="""
        Field mapping configuration:
        {
            "target_field": "source_field",
            "nested.field": "data.value",
            "computed_field": {"type": "template", "template": "{{firstName}} {{lastName}}"}
        }
        """
    )
    
    # Jinja2 templates for complex transformations
    template = models.TextField(
        blank=True,
        help_text="Jinja2 template for complex transformations"
    )
    
    # Pre/post processing
    pre_processors = models.JSONField(default=list, help_text="Functions to run before transformation")
    post_processors = models.JSONField(default=list, help_text="Functions to run after transformation")
    
    # Validation
    input_schema = models.JSONField(default=dict, help_text="JSON Schema for input validation")
    output_schema = models.JSONField(default=dict, help_text="JSON Schema for output validation")
    
    # Stats
    usage_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'webhook_transformers'
    
    def __str__(self):
        return self.name


class WebhookTransformLog(models.Model):
    """Log of webhook transformations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transformer = models.ForeignKey(WebhookTransformer, on_delete=models.CASCADE, related_name='logs')
    
    # Input/Output
    input_payload = models.JSONField()
    output_payload = models.JSONField(null=True, blank=True)
    
    # Result
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    # Performance
    duration_ms = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'webhook_transform_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Transform log - {self.transformer.name}"


# ============================================================================
# API MARKETPLACE
# ============================================================================

class MarketplaceIntegration(models.Model):
    """Third-party developer integrations for the marketplace"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]
    
    CATEGORY_CHOICES = [
        ('crm', 'CRM'),
        ('email', 'Email Marketing'),
        ('analytics', 'Analytics'),
        ('payment', 'Payment'),
        ('storage', 'Storage'),
        ('automation', 'Automation'),
        ('communication', 'Communication'),
        ('productivity', 'Productivity'),
        ('ai_ml', 'AI/ML'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    developer = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='marketplace_integrations')
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    tagline = models.CharField(max_length=300)
    description = models.TextField()
    
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    tags = models.JSONField(default=list)
    
    # Branding
    logo_url = models.URLField()
    banner_url = models.URLField(blank=True)
    screenshots = models.JSONField(default=list)
    
    # Technical details
    api_spec_url = models.URLField(blank=True, help_text="OpenAPI spec URL")
    documentation_url = models.URLField()
    support_url = models.URLField(blank=True)
    
    # OAuth settings for the integration
    oauth_client_id = models.CharField(max_length=200, blank=True)
    oauth_client_secret_encrypted = models.TextField(blank=True)
    oauth_scopes = models.JSONField(default=list)
    oauth_redirect_uri = models.URLField(blank=True)
    
    # Webhook configuration
    webhook_url = models.URLField(blank=True)
    webhook_events = models.JSONField(default=list)
    
    # Pricing
    is_free = models.BooleanField(default=True)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Stats
    install_count = models.IntegerField(default=0)
    rating_average = models.FloatField(default=0)
    rating_count = models.IntegerField(default=0)
    
    # Version
    version = models.CharField(max_length=20, default='1.0.0')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'marketplace_integrations'
        ordering = ['-install_count']
    
    def __str__(self):
        return self.name


class MarketplaceInstallation(models.Model):
    """User installations of marketplace integrations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration = models.ForeignKey(MarketplaceIntegration, on_delete=models.CASCADE, related_name='installations')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='marketplace_installations')
    
    # Configuration
    config = models.JSONField(default=dict, help_text="User's configuration for this integration")
    oauth_tokens = models.JSONField(default=dict, help_text="Encrypted OAuth tokens")
    
    # Connected forms
    connected_forms = models.ManyToManyField('forms.Form', related_name='marketplace_integrations', blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Usage
    last_used_at = models.DateTimeField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    
    installed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'marketplace_installations'
        unique_together = [['integration', 'user']]
    
    def __str__(self):
        return f"{self.user.email} - {self.integration.name}"


class MarketplaceReview(models.Model):
    """Reviews for marketplace integrations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration = models.ForeignKey(MarketplaceIntegration, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='marketplace_reviews')
    
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=200)
    review = models.TextField()
    
    # Helpful votes
    helpful_count = models.IntegerField(default=0)
    
    # Developer response
    developer_response = models.TextField(blank=True)
    developer_response_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'marketplace_reviews'
        unique_together = [['integration', 'user']]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.integration.name} - {self.rating} stars"


# ============================================================================
# FEDERATED FORM SHARING
# ============================================================================

class FederatedFormShare(models.Model):
    """Cross-platform form embedding with permission controls"""
    SHARE_TYPES = [
        ('embed', 'Embeddable Widget'),
        ('api', 'API Access'),
        ('iframe', 'iFrame Embed'),
        ('sdk', 'SDK Integration'),
    ]
    
    PERMISSION_LEVELS = [
        ('view', 'View Only'),
        ('submit', 'Can Submit'),
        ('full', 'Full Access'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='federated_shares')
    
    name = models.CharField(max_length=200)
    share_type = models.CharField(max_length=20, choices=SHARE_TYPES)
    permission_level = models.CharField(max_length=20, choices=PERMISSION_LEVELS, default='submit')
    
    # Access control
    share_token = models.CharField(max_length=100, unique=True)
    allowed_domains = models.JSONField(default=list, help_text="Domains allowed to embed")
    allowed_ips = models.JSONField(default=list, help_text="IPs allowed to access")
    
    # Customization
    custom_styling = models.JSONField(default=dict, help_text="Custom CSS overrides")
    branding_enabled = models.BooleanField(default=True)
    
    # Limits
    rate_limit_per_minute = models.IntegerField(default=60)
    max_daily_submissions = models.IntegerField(null=True, blank=True)
    
    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Stats
    views_count = models.IntegerField(default=0)
    submissions_count = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'federated_form_shares'
    
    def __str__(self):
        return f"{self.form.title} - {self.share_type}"


class FederatedAccessLog(models.Model):
    """Log of federated form access"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    share = models.ForeignKey(FederatedFormShare, on_delete=models.CASCADE, related_name='access_logs')
    
    action = models.CharField(max_length=20, help_text="view, submit, etc.")
    
    # Access context
    referring_domain = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Result
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'federated_access_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.share.name} - {self.action}"


# ============================================================================
# SSO INTEGRATION HUB
# ============================================================================

class SSOConfiguration(models.Model):
    """Extended SSO configuration for enterprise"""
    SSO_PROTOCOLS = [
        ('saml', 'SAML 2.0'),
        ('oauth', 'OAuth 2.0'),
        ('oidc', 'OpenID Connect'),
        ('ldap', 'LDAP'),
        ('active_directory', 'Active Directory'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('users.Team', on_delete=models.CASCADE, related_name='sso_configurations')
    
    name = models.CharField(max_length=200)
    protocol = models.CharField(max_length=30, choices=SSO_PROTOCOLS)
    is_primary = models.BooleanField(default=False)
    
    # General settings
    entity_id = models.CharField(max_length=500, blank=True)
    metadata_url = models.URLField(blank=True)
    
    # SAML settings
    saml_sso_url = models.URLField(blank=True)
    saml_slo_url = models.URLField(blank=True)
    saml_certificate = models.TextField(blank=True)
    saml_signing_algorithm = models.CharField(max_length=50, default='sha256')
    
    # OAuth/OIDC settings
    oauth_client_id = models.CharField(max_length=500, blank=True)
    oauth_client_secret_encrypted = models.TextField(blank=True)
    oauth_authorize_url = models.URLField(blank=True)
    oauth_token_url = models.URLField(blank=True)
    oauth_userinfo_url = models.URLField(blank=True)
    oauth_scopes = models.JSONField(default=list)
    
    # LDAP settings
    ldap_server = models.CharField(max_length=500, blank=True)
    ldap_port = models.IntegerField(default=389)
    ldap_use_ssl = models.BooleanField(default=False)
    ldap_base_dn = models.CharField(max_length=500, blank=True)
    ldap_bind_dn = models.CharField(max_length=500, blank=True)
    ldap_bind_password_encrypted = models.TextField(blank=True)
    ldap_user_search_filter = models.CharField(max_length=500, blank=True)
    
    # Attribute mapping
    attribute_mapping = models.JSONField(
        default=dict,
        help_text="""
        Map SSO attributes to user fields:
        {
            "email": "mail",
            "first_name": "givenName",
            "last_name": "sn",
            "groups": "memberOf"
        }
        """
    )
    
    # Role/group mapping
    role_mapping = models.JSONField(
        default=dict,
        help_text="Map SSO groups to application roles"
    )
    
    # Provisioning
    auto_provision_users = models.BooleanField(default=True)
    auto_update_users = models.BooleanField(default=True)
    auto_deactivate_users = models.BooleanField(default=False)
    
    # Domain restrictions
    allowed_email_domains = models.JSONField(default=list)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    login_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sso_configurations'
    
    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class SSOLoginEvent(models.Model):
    """Log of SSO login events"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sso_config = models.ForeignKey(SSOConfiguration, on_delete=models.CASCADE, related_name='login_events')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True)
    
    # Event details
    success = models.BooleanField(default=True)
    error_code = models.CharField(max_length=50, blank=True)
    error_message = models.TextField(blank=True)
    
    # SSO response data
    sso_subject = models.CharField(max_length=255, blank=True)
    sso_session_id = models.CharField(max_length=255, blank=True)
    sso_attributes = models.JSONField(default=dict)
    
    # Context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sso_login_events'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"SSO Login - {self.sso_config.name} - {'Success' if self.success else 'Failed'}"


# ============================================================================
# ERP SYSTEM CONNECTORS
# ============================================================================

class ERPConnector(models.Model):
    """Connectors for enterprise ERP systems"""
    ERP_SYSTEMS = [
        ('sap', 'SAP'),
        ('oracle', 'Oracle'),
        ('salesforce', 'Salesforce'),
        ('dynamics', 'Microsoft Dynamics'),
        ('netsuite', 'NetSuite'),
        ('workday', 'Workday'),
        ('custom', 'Custom ERP'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='erp_connectors')
    
    name = models.CharField(max_length=200)
    erp_system = models.CharField(max_length=30, choices=ERP_SYSTEMS)
    
    # Connection settings
    base_url = models.URLField()
    api_version = models.CharField(max_length=20, blank=True)
    
    # Authentication
    auth_type = models.CharField(
        max_length=30,
        choices=[
            ('oauth', 'OAuth 2.0'),
            ('api_key', 'API Key'),
            ('basic', 'Basic Auth'),
            ('certificate', 'Certificate'),
        ],
        default='oauth'
    )
    credentials_encrypted = models.JSONField(default=dict)
    
    # SAP-specific settings
    sap_client = models.CharField(max_length=10, blank=True)
    sap_system_id = models.CharField(max_length=10, blank=True)
    
    # Object mappings
    object_mappings = models.JSONField(
        default=dict,
        help_text="Map form submissions to ERP objects"
    )
    
    # Sync settings
    sync_direction = models.CharField(
        max_length=20,
        choices=[('push', 'Push Only'), ('pull', 'Pull Only'), ('bidirectional', 'Bidirectional')],
        default='push'
    )
    sync_frequency_minutes = models.IntegerField(default=15)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=30, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'erp_connectors'
    
    def __str__(self):
        return f"{self.name} ({self.erp_system})"


class ERPSyncLog(models.Model):
    """Log of ERP sync operations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    connector = models.ForeignKey(ERPConnector, on_delete=models.CASCADE, related_name='sync_logs')
    
    # Sync details
    direction = models.CharField(max_length=20)
    records_processed = models.IntegerField(default=0)
    records_succeeded = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('running', 'Running'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('partial', 'Partial Success'),
        ]
    )
    error_details = models.JSONField(default=list)
    
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'erp_sync_logs'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.connector.name} - {self.status}"


# ============================================================================
# LEGACY SYSTEM BRIDGES
# ============================================================================

class LegacySystemBridge(models.Model):
    """API adapters for older enterprise systems"""
    BRIDGE_TYPES = [
        ('soap', 'SOAP'),
        ('xml_rpc', 'XML-RPC'),
        ('file_based', 'File-Based (CSV, XML)'),
        ('database', 'Direct Database'),
        ('ftp', 'FTP/SFTP'),
        ('custom', 'Custom Protocol'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='legacy_bridges')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    bridge_type = models.CharField(max_length=30, choices=BRIDGE_TYPES)
    
    # Connection settings
    endpoint = models.CharField(max_length=500)
    credentials_encrypted = models.JSONField(default=dict)
    
    # SOAP-specific
    wsdl_url = models.URLField(blank=True)
    soap_action = models.CharField(max_length=255, blank=True)
    
    # File-based settings
    file_format = models.CharField(max_length=20, blank=True)
    file_encoding = models.CharField(max_length=20, default='utf-8')
    delimiter = models.CharField(max_length=5, default=',')
    
    # Database settings
    database_type = models.CharField(max_length=30, blank=True)
    connection_string_encrypted = models.TextField(blank=True)
    
    # FTP settings
    ftp_directory = models.CharField(max_length=500, blank=True)
    
    # Data transformation
    request_transformer = models.ForeignKey(
        WebhookTransformer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='request_bridges'
    )
    response_transformer = models.ForeignKey(
        WebhookTransformer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='response_bridges'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'legacy_system_bridges'
    
    def __str__(self):
        return f"{self.name} ({self.bridge_type})"


# ============================================================================
# GRAPHQL SUPPORT
# ============================================================================

class GraphQLConfig(models.Model):
    """GraphQL API configuration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='graphql_configs')
    
    is_enabled = models.BooleanField(default=True)
    
    # Endpoint settings
    endpoint_slug = models.SlugField(max_length=100, unique=True)
    
    # Query limits
    max_depth = models.IntegerField(default=10)
    max_complexity = models.IntegerField(default=1000)
    max_results = models.IntegerField(default=1000)
    
    # Caching
    cache_enabled = models.BooleanField(default=True)
    cache_ttl_seconds = models.IntegerField(default=300)
    
    # Introspection
    introspection_enabled = models.BooleanField(default=False)
    
    # Rate limiting
    rate_limit_per_minute = models.IntegerField(default=100)
    
    # Allowed operations
    queries_enabled = models.BooleanField(default=True)
    mutations_enabled = models.BooleanField(default=True)
    subscriptions_enabled = models.BooleanField(default=False)
    
    # Field-level access control
    exposed_types = models.JSONField(
        default=list,
        help_text="Types exposed through GraphQL"
    )
    field_restrictions = models.JSONField(
        default=dict,
        help_text="Field-level access restrictions"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'graphql_configs'
    
    def __str__(self):
        return f"GraphQL Config - {self.endpoint_slug}"


class GraphQLQueryLog(models.Model):
    """Log of GraphQL queries for analytics and debugging"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    config = models.ForeignKey(GraphQLConfig, on_delete=models.CASCADE, related_name='query_logs')
    
    # Query details
    operation_type = models.CharField(max_length=20)
    operation_name = models.CharField(max_length=100, blank=True)
    query_hash = models.CharField(max_length=64)
    query_complexity = models.IntegerField(default=0)
    query_depth = models.IntegerField(default=0)
    
    # Variables (sanitized)
    variables_count = models.IntegerField(default=0)
    
    # Execution
    duration_ms = models.IntegerField()
    status = models.CharField(max_length=20)
    error_message = models.TextField(blank=True)
    
    # Context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    # Cache
    cache_hit = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'graphql_query_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['query_hash']),
        ]
    
    def __str__(self):
        return f"GraphQL: {self.operation_type} - {self.operation_name or 'anonymous'}"


# ============================================================================
# ADVANCED RATE LIMITING
# ============================================================================

class RateLimitConfig(models.Model):
    """Granular API rate limiting configuration"""
    RATE_LIMIT_TYPES = [
        ('api', 'API Endpoint'),
        ('form', 'Form'),
        ('user', 'User'),
        ('ip', 'IP Address'),
        ('token', 'API Token'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='rate_limit_configs', null=True, blank=True)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='rate_limit_configs', null=True, blank=True)
    
    name = models.CharField(max_length=200)
    limit_type = models.CharField(max_length=20, choices=RATE_LIMIT_TYPES)
    
    # Rate limits
    requests_per_second = models.IntegerField(null=True, blank=True)
    requests_per_minute = models.IntegerField(null=True, blank=True)
    requests_per_hour = models.IntegerField(null=True, blank=True)
    requests_per_day = models.IntegerField(null=True, blank=True)
    
    # Burst handling
    burst_size = models.IntegerField(default=10, help_text="Allowed burst above limit")
    burst_duration_seconds = models.IntegerField(default=10)
    
    # Throttling behavior
    throttle_strategy = models.CharField(
        max_length=30,
        choices=[
            ('fixed_window', 'Fixed Window'),
            ('sliding_window', 'Sliding Window'),
            ('token_bucket', 'Token Bucket'),
            ('leaky_bucket', 'Leaky Bucket'),
        ],
        default='sliding_window'
    )
    
    # Response when limit exceeded
    exceed_response_code = models.IntegerField(default=429)
    exceed_response_message = models.TextField(default="Rate limit exceeded. Please try again later.")
    retry_after_header = models.BooleanField(default=True)
    
    # Exemptions
    exempt_ips = models.JSONField(default=list)
    exempt_users = models.JSONField(default=list)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rate_limit_configs'
    
    def __str__(self):
        return f"{self.name} - {self.limit_type}"


class RateLimitEvent(models.Model):
    """Log of rate limit events"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    config = models.ForeignKey(RateLimitConfig, on_delete=models.CASCADE, related_name='events')
    
    # Identifier
    identifier = models.CharField(max_length=255, help_text="IP, user ID, token, etc.")
    identifier_type = models.CharField(max_length=20)
    
    # Event
    exceeded = models.BooleanField(default=True)
    current_count = models.IntegerField()
    limit = models.IntegerField()
    
    # Context
    endpoint = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rate_limit_events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['identifier']),
            models.Index(fields=['exceeded', '-created_at']),
        ]
    
    def __str__(self):
        return f"Rate limit {'exceeded' if self.exceeded else 'checked'} - {self.identifier}"
