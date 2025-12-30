"""
Performance & Scalability Models

Features:
- Edge Computing Integration
- Intelligent Preloading
- Database Optimization
- CDN Integration
- Multi-Region Deployment
- Performance Monitoring
"""
import uuid
from django.db import models
from django.conf import settings


class EdgeComputingConfig(models.Model):
    """
    Edge computing configuration for form processing
    Enables serverless edge functions for low-latency operations
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    form = models.OneToOneField(
        'forms.Form',
        on_delete=models.CASCADE,
        related_name='edge_config'
    )
    
    is_enabled = models.BooleanField(default=False)
    
    # Edge provider
    provider = models.CharField(
        max_length=50,
        choices=[
            ('cloudflare', 'Cloudflare Workers'),
            ('aws_lambda_edge', 'AWS Lambda@Edge'),
            ('vercel_edge', 'Vercel Edge Functions'),
            ('fastly', 'Fastly Compute@Edge'),
            ('deno_deploy', 'Deno Deploy'),
        ],
        default='cloudflare'
    )
    
    # Regions
    enabled_regions = models.JSONField(
        default=list,
        help_text="List of edge regions to deploy to"
    )
    primary_region = models.CharField(max_length=50, default='auto')
    
    # Edge functions
    functions = models.JSONField(
        default=dict,
        help_text="Edge function configurations"
    )
    
    # Caching at edge
    cache_form_config = models.BooleanField(default=True)
    cache_ttl = models.IntegerField(default=300, help_text="Cache TTL in seconds")
    cache_rules = models.JSONField(default=list)
    
    # Validation at edge
    validate_at_edge = models.BooleanField(default=True)
    sanitize_at_edge = models.BooleanField(default=True)
    
    # Rate limiting at edge
    rate_limit_at_edge = models.BooleanField(default=True)
    rate_limit_config = models.JSONField(default=dict)
    
    # Stats
    edge_requests = models.BigIntegerField(default=0)
    origin_requests = models.BigIntegerField(default=0)
    avg_edge_latency_ms = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class IntelligentPreloadConfig(models.Model):
    """
    AI-powered intelligent preloading for form assets
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    form = models.OneToOneField(
        'forms.Form',
        on_delete=models.CASCADE,
        related_name='preload_config'
    )
    
    is_enabled = models.BooleanField(default=True)
    
    # Preload strategies
    preload_next_step = models.BooleanField(default=True)
    preload_likely_branches = models.BooleanField(default=True)
    preload_dropdown_options = models.BooleanField(default=True)
    preload_validation_rules = models.BooleanField(default=True)
    
    # AI prediction
    use_ai_prediction = models.BooleanField(default=False)
    prediction_model = models.CharField(max_length=100, default='navigation_predictor')
    prediction_threshold = models.FloatField(default=0.7)
    
    # Preload timing
    preload_on_focus = models.BooleanField(default=True)
    preload_on_input = models.BooleanField(default=False)
    preload_delay_ms = models.IntegerField(default=200)
    
    # Resource hints
    dns_prefetch = models.JSONField(default=list, help_text="Domains to DNS prefetch")
    preconnect = models.JSONField(default=list, help_text="Origins to preconnect")
    preload_assets = models.JSONField(default=list, help_text="Assets to preload")
    prefetch_pages = models.JSONField(default=list, help_text="Pages to prefetch")
    
    # Bandwidth awareness
    respect_save_data = models.BooleanField(default=True)
    network_aware = models.BooleanField(default=True)
    disable_on_slow = models.BooleanField(default=True)
    
    # Stats
    preloads_triggered = models.BigIntegerField(default=0)
    preloads_used = models.BigIntegerField(default=0)
    avg_time_saved_ms = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PreloadPrediction(models.Model):
    """Track preload prediction accuracy"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    config = models.ForeignKey(
        IntelligentPreloadConfig,
        on_delete=models.CASCADE,
        related_name='predictions'
    )
    
    # Prediction details
    current_step = models.CharField(max_length=100)
    predicted_next = models.CharField(max_length=100)
    actual_next = models.CharField(max_length=100, blank=True)
    confidence = models.FloatField()
    
    was_correct = models.BooleanField(default=False)
    preload_used = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)


class DatabaseOptimizationConfig(models.Model):
    """
    Database optimization recommendations and auto-tuning
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    form = models.OneToOneField(
        'forms.Form',
        on_delete=models.CASCADE,
        related_name='db_optimization'
    )
    
    # Auto-optimization
    auto_optimize = models.BooleanField(default=False)
    optimization_schedule = models.CharField(max_length=50, default='weekly')
    
    # Query optimization
    use_query_cache = models.BooleanField(default=True)
    query_cache_ttl = models.IntegerField(default=60)
    
    # Indexing recommendations
    recommended_indexes = models.JSONField(default=list)
    applied_indexes = models.JSONField(default=list)
    
    # Partitioning
    use_partitioning = models.BooleanField(default=False)
    partition_by = models.CharField(max_length=50, blank=True)
    partition_config = models.JSONField(default=dict)
    
    # Connection pooling
    pool_size = models.IntegerField(default=10)
    max_overflow = models.IntegerField(default=20)
    pool_timeout = models.IntegerField(default=30)
    
    # Read replicas
    use_read_replicas = models.BooleanField(default=False)
    read_replica_config = models.JSONField(default=dict)
    
    # Query analysis
    slow_query_threshold_ms = models.IntegerField(default=1000)
    analyzed_queries = models.JSONField(default=list)
    
    last_optimized_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class QueryAnalysis(models.Model):
    """Analyzed slow query"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    config = models.ForeignKey(
        DatabaseOptimizationConfig,
        on_delete=models.CASCADE,
        related_name='query_analyses'
    )
    
    # Query details
    query_hash = models.CharField(max_length=64)
    query_template = models.TextField()
    avg_duration_ms = models.FloatField()
    max_duration_ms = models.FloatField()
    execution_count = models.IntegerField(default=0)
    
    # Analysis
    explain_plan = models.JSONField(default=dict)
    optimization_suggestions = models.JSONField(default=list)
    
    # Status
    is_optimized = models.BooleanField(default=False)
    optimization_applied = models.TextField(blank=True)
    
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-avg_duration_ms']


class CDNConfig(models.Model):
    """
    CDN integration configuration
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    form = models.OneToOneField(
        'forms.Form',
        on_delete=models.CASCADE,
        related_name='cdn_config'
    )
    
    is_enabled = models.BooleanField(default=True)
    
    # Provider
    provider = models.CharField(
        max_length=50,
        choices=[
            ('cloudflare', 'Cloudflare'),
            ('cloudfront', 'AWS CloudFront'),
            ('fastly', 'Fastly'),
            ('akamai', 'Akamai'),
            ('bunny', 'BunnyCDN'),
            ('custom', 'Custom'),
        ],
        default='cloudflare'
    )
    
    # Configuration
    cdn_domain = models.CharField(max_length=200, blank=True)
    origin_domain = models.CharField(max_length=200, blank=True)
    
    # Caching
    cache_static_assets = models.BooleanField(default=True)
    cache_form_schema = models.BooleanField(default=True)
    cache_api_responses = models.BooleanField(default=False)
    
    cache_rules = models.JSONField(
        default=list,
        help_text="Custom caching rules"
    )
    
    # TTL settings
    default_ttl = models.IntegerField(default=86400)
    max_ttl = models.IntegerField(default=604800)
    browser_ttl = models.IntegerField(default=14400)
    
    # Optimization
    minify_html = models.BooleanField(default=True)
    minify_css = models.BooleanField(default=True)
    minify_js = models.BooleanField(default=True)
    compress_images = models.BooleanField(default=True)
    webp_conversion = models.BooleanField(default=True)
    brotli_compression = models.BooleanField(default=True)
    
    # Security
    https_only = models.BooleanField(default=True)
    hsts_enabled = models.BooleanField(default=True)
    
    # Invalidation
    auto_invalidate_on_publish = models.BooleanField(default=True)
    invalidation_patterns = models.JSONField(default=list)
    
    # Stats
    cache_hit_ratio = models.FloatField(default=0)
    bandwidth_saved_bytes = models.BigIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CDNPurgeLog(models.Model):
    """Log of CDN cache purges"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    config = models.ForeignKey(
        CDNConfig,
        on_delete=models.CASCADE,
        related_name='purge_logs'
    )
    
    purge_type = models.CharField(
        max_length=20,
        choices=[
            ('all', 'All'),
            ('path', 'Path'),
            ('tag', 'Tag'),
            ('prefix', 'Prefix'),
        ]
    )
    
    purge_target = models.CharField(max_length=500)
    reason = models.CharField(max_length=200, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True)


class MultiRegionConfig(models.Model):
    """
    Multi-region deployment configuration
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    form = models.OneToOneField(
        'forms.Form',
        on_delete=models.CASCADE,
        related_name='multi_region_config'
    )
    
    is_enabled = models.BooleanField(default=False)
    
    # Regions
    primary_region = models.CharField(max_length=50, default='us-east-1')
    active_regions = models.JSONField(
        default=list,
        help_text="List of active regions"
    )
    
    # Routing strategy
    routing_strategy = models.CharField(
        max_length=50,
        choices=[
            ('latency', 'Latency-based'),
            ('geo', 'Geographic'),
            ('weighted', 'Weighted'),
            ('failover', 'Failover'),
        ],
        default='latency'
    )
    
    routing_weights = models.JSONField(
        default=dict,
        help_text="Region weights for weighted routing"
    )
    
    # Replication
    replication_mode = models.CharField(
        max_length=20,
        choices=[
            ('async', 'Asynchronous'),
            ('sync', 'Synchronous'),
            ('eventual', 'Eventually Consistent'),
        ],
        default='async'
    )
    
    replication_lag_threshold_ms = models.IntegerField(default=1000)
    
    # Failover
    enable_auto_failover = models.BooleanField(default=True)
    failover_threshold_errors = models.IntegerField(default=5)
    failover_window_seconds = models.IntegerField(default=60)
    health_check_interval = models.IntegerField(default=30)
    
    # Regional settings
    region_configs = models.JSONField(
        default=dict,
        help_text="Per-region configuration overrides"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class RegionHealth(models.Model):
    """Health status of a region"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    config = models.ForeignKey(
        MultiRegionConfig,
        on_delete=models.CASCADE,
        related_name='region_health'
    )
    
    region = models.CharField(max_length=50)
    
    # Health status
    is_healthy = models.BooleanField(default=True)
    health_score = models.FloatField(default=100)
    
    # Metrics
    latency_ms = models.FloatField(default=0)
    error_rate = models.FloatField(default=0)
    request_count = models.IntegerField(default=0)
    
    # Last check
    last_check_at = models.DateTimeField(auto_now=True)
    last_healthy_at = models.DateTimeField(null=True)
    last_unhealthy_at = models.DateTimeField(null=True)
    
    # Failover status
    is_failover_active = models.BooleanField(default=False)
    failover_target = models.CharField(max_length=50, blank=True)
    
    class Meta:
        unique_together = ['config', 'region']


class PerformanceMonitor(models.Model):
    """
    Real-time performance monitoring configuration
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    form = models.OneToOneField(
        'forms.Form',
        on_delete=models.CASCADE,
        related_name='performance_monitor'
    )
    
    is_enabled = models.BooleanField(default=True)
    
    # Metrics collection
    collect_core_web_vitals = models.BooleanField(default=True)
    collect_custom_metrics = models.BooleanField(default=True)
    collect_user_timing = models.BooleanField(default=True)
    collect_resource_timing = models.BooleanField(default=True)
    
    # Sampling
    sample_rate = models.FloatField(default=1.0, help_text="0.0-1.0")
    
    # Alerting
    enable_alerts = models.BooleanField(default=True)
    alert_channels = models.JSONField(default=list)
    
    # Thresholds
    lcp_threshold_ms = models.IntegerField(default=2500)
    fid_threshold_ms = models.IntegerField(default=100)
    cls_threshold = models.FloatField(default=0.1)
    ttfb_threshold_ms = models.IntegerField(default=600)
    
    # Budgets
    performance_budget = models.JSONField(
        default=dict,
        help_text="Performance budget configuration"
    )
    
    # Integration
    analytics_endpoint = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PerformanceSnapshot(models.Model):
    """
    Point-in-time performance snapshot
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    monitor = models.ForeignKey(
        PerformanceMonitor,
        on_delete=models.CASCADE,
        related_name='snapshots'
    )
    
    # Time window
    window_start = models.DateTimeField()
    window_end = models.DateTimeField()
    
    # Core Web Vitals
    lcp_p50 = models.FloatField(null=True)
    lcp_p75 = models.FloatField(null=True)
    lcp_p95 = models.FloatField(null=True)
    
    fid_p50 = models.FloatField(null=True)
    fid_p75 = models.FloatField(null=True)
    fid_p95 = models.FloatField(null=True)
    
    cls_p50 = models.FloatField(null=True)
    cls_p75 = models.FloatField(null=True)
    cls_p95 = models.FloatField(null=True)
    
    ttfb_p50 = models.FloatField(null=True)
    ttfb_p75 = models.FloatField(null=True)
    ttfb_p95 = models.FloatField(null=True)
    
    # Custom metrics
    custom_metrics = models.JSONField(default=dict)
    
    # Aggregates
    total_page_views = models.IntegerField(default=0)
    unique_visitors = models.IntegerField(default=0)
    
    # Breakdown
    by_device = models.JSONField(default=dict)
    by_connection = models.JSONField(default=dict)
    by_browser = models.JSONField(default=dict)
    by_country = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-window_end']


class EnhancedPerformanceAlert(models.Model):
    """Enhanced performance alert record with Core Web Vitals tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    monitor = models.ForeignKey(
        PerformanceMonitor,
        on_delete=models.CASCADE,
        related_name='enhanced_alerts'
    )
    
    # Alert details
    alert_type = models.CharField(
        max_length=50,
        choices=[
            ('lcp_regression', 'LCP Regression'),
            ('fid_regression', 'FID Regression'),
            ('cls_regression', 'CLS Regression'),
            ('ttfb_regression', 'TTFB Regression'),
            ('error_spike', 'Error Spike'),
            ('budget_exceeded', 'Budget Exceeded'),
        ]
    )
    
    severity = models.CharField(
        max_length=20,
        choices=[
            ('info', 'Info'),
            ('warning', 'Warning'),
            ('critical', 'Critical'),
        ]
    )
    
    metric = models.CharField(max_length=50)
    threshold = models.FloatField()
    actual_value = models.FloatField()
    
    message = models.TextField()
    details = models.JSONField(default=dict)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('acknowledged', 'Acknowledged'),
            ('resolved', 'Resolved'),
        ],
        default='active'
    )
    
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    acknowledged_at = models.DateTimeField(null=True)
    resolved_at = models.DateTimeField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class LoadTestConfig(models.Model):
    """
    Load testing configuration
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    form = models.ForeignKey(
        'forms.Form',
        on_delete=models.CASCADE,
        related_name='load_tests'
    )
    
    name = models.CharField(max_length=200)
    
    # Test configuration
    test_type = models.CharField(
        max_length=20,
        choices=[
            ('smoke', 'Smoke Test'),
            ('load', 'Load Test'),
            ('stress', 'Stress Test'),
            ('spike', 'Spike Test'),
            ('soak', 'Soak Test'),
        ],
        default='load'
    )
    
    # Virtual users
    vus_start = models.IntegerField(default=1)
    vus_target = models.IntegerField(default=100)
    ramp_up_duration = models.IntegerField(default=60, help_text="Seconds")
    hold_duration = models.IntegerField(default=300, help_text="Seconds")
    ramp_down_duration = models.IntegerField(default=30, help_text="Seconds")
    
    # Scenarios
    scenarios = models.JSONField(
        default=list,
        help_text="Test scenarios to run"
    )
    
    # Thresholds
    success_rate_threshold = models.FloatField(default=0.99)
    response_time_p95_threshold = models.IntegerField(default=1000)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class LoadTestRun(models.Model):
    """Load test execution record"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    config = models.ForeignKey(
        LoadTestConfig,
        on_delete=models.CASCADE,
        related_name='runs'
    )
    
    # Execution
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('running', 'Running'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    
    # Results
    total_requests = models.IntegerField(default=0)
    successful_requests = models.IntegerField(default=0)
    failed_requests = models.IntegerField(default=0)
    
    avg_response_time_ms = models.FloatField(null=True)
    p50_response_time_ms = models.FloatField(null=True)
    p95_response_time_ms = models.FloatField(null=True)
    p99_response_time_ms = models.FloatField(null=True)
    
    requests_per_second = models.FloatField(null=True)
    
    # Pass/Fail
    passed_thresholds = models.BooleanField(null=True)
    threshold_results = models.JSONField(default=dict)
    
    # Detailed results
    timeline_data = models.JSONField(default=list)
    error_breakdown = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class ResourceOptimization(models.Model):
    """
    Resource optimization recommendations
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    form = models.ForeignKey(
        'forms.Form',
        on_delete=models.CASCADE,
        related_name='resource_optimizations'
    )
    
    # Resource details
    resource_type = models.CharField(
        max_length=50,
        choices=[
            ('image', 'Image'),
            ('script', 'Script'),
            ('stylesheet', 'Stylesheet'),
            ('font', 'Font'),
            ('video', 'Video'),
            ('other', 'Other'),
        ]
    )
    
    resource_url = models.URLField()
    original_size_bytes = models.BigIntegerField()
    optimized_size_bytes = models.BigIntegerField(null=True)
    
    # Optimization
    optimization_type = models.CharField(max_length=100)
    optimization_details = models.JSONField(default=dict)
    
    potential_savings_bytes = models.BigIntegerField(default=0)
    potential_time_savings_ms = models.FloatField(default=0)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('recommended', 'Recommended'),
            ('applied', 'Applied'),
            ('skipped', 'Skipped'),
        ],
        default='recommended'
    )
    
    applied_at = models.DateTimeField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-potential_savings_bytes']


class AutoScalingConfig(models.Model):
    """
    Auto-scaling configuration
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    form = models.OneToOneField(
        'forms.Form',
        on_delete=models.CASCADE,
        related_name='autoscaling_config'
    )
    
    is_enabled = models.BooleanField(default=False)
    
    # Scaling bounds
    min_instances = models.IntegerField(default=1)
    max_instances = models.IntegerField(default=10)
    
    # Scaling triggers
    cpu_scale_up_threshold = models.IntegerField(default=70)
    cpu_scale_down_threshold = models.IntegerField(default=30)
    memory_scale_up_threshold = models.IntegerField(default=80)
    
    request_rate_threshold = models.IntegerField(
        default=100,
        help_text="Requests per second per instance"
    )
    
    # Timing
    scale_up_cooldown = models.IntegerField(default=60, help_text="Seconds")
    scale_down_cooldown = models.IntegerField(default=300, help_text="Seconds")
    
    # Predictive scaling
    use_predictive_scaling = models.BooleanField(default=False)
    prediction_window_hours = models.IntegerField(default=24)
    
    # Current state
    current_instances = models.IntegerField(default=1)
    last_scale_action = models.CharField(max_length=20, blank=True)
    last_scale_at = models.DateTimeField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ScalingEvent(models.Model):
    """Record of scaling events"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    config = models.ForeignKey(
        AutoScalingConfig,
        on_delete=models.CASCADE,
        related_name='events'
    )
    
    # Event details
    action = models.CharField(
        max_length=20,
        choices=[
            ('scale_up', 'Scale Up'),
            ('scale_down', 'Scale Down'),
        ]
    )
    
    from_instances = models.IntegerField()
    to_instances = models.IntegerField()
    
    # Trigger
    trigger_type = models.CharField(max_length=50)
    trigger_value = models.FloatField()
    trigger_threshold = models.FloatField()
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('initiated', 'Initiated'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='initiated'
    )
    
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True)
    
    class Meta:
        ordering = ['-created_at']
