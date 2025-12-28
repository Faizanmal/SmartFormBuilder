"""
Performance monitoring and optimization models
"""
from django.db import models
import uuid


class PerformanceMetric(models.Model):
    """Real-time performance metrics for forms"""
    METRIC_TYPES = [
        ('load_time', 'Page Load Time'),
        ('ttfb', 'Time to First Byte'),
        ('fcp', 'First Contentful Paint'),
        ('lcp', 'Largest Contentful Paint'),
        ('fid', 'First Input Delay'),
        ('cls', 'Cumulative Layout Shift'),
        ('tti', 'Time to Interactive'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='performance_metrics')
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    value = models.FloatField(help_text="Metric value in milliseconds or score")
    device_type = models.CharField(
        max_length=20,
        choices=[('desktop', 'Desktop'), ('mobile', 'Mobile'), ('tablet', 'Tablet')],
        default='desktop'
    )
    connection_type = models.CharField(
        max_length=20,
        choices=[('4g', '4G'), ('3g', '3G'), ('2g', '2G'), ('slow-2g', 'Slow 2G'), ('wifi', 'WiFi')],
        default='wifi'
    )
    user_agent = models.CharField(max_length=500, blank=True)
    browser = models.CharField(max_length=50, blank=True)
    browser_version = models.CharField(max_length=20, blank=True)
    os = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    region = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'performance_metrics'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['form', 'metric_type', 'created_at']),
            models.Index(fields=['form', 'device_type']),
        ]
    
    def __str__(self):
        return f"{self.form.title} - {self.metric_type}: {self.value}ms"


class FieldCompletionMetric(models.Model):
    """Track how long users take to complete each field"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='field_metrics')
    field_id = models.CharField(max_length=100)
    field_label = models.CharField(max_length=255)
    field_type = models.CharField(max_length=50)
    
    # Timing metrics
    avg_completion_time = models.FloatField(default=0, help_text="Average time in seconds")
    min_completion_time = models.FloatField(default=0)
    max_completion_time = models.FloatField(default=0)
    p50_completion_time = models.FloatField(default=0, help_text="50th percentile")
    p95_completion_time = models.FloatField(default=0, help_text="95th percentile")
    
    # Engagement metrics
    total_interactions = models.IntegerField(default=0)
    total_completions = models.IntegerField(default=0)
    drop_off_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    correction_count = models.IntegerField(default=0, help_text="How many times users corrected input")
    
    completion_rate = models.FloatField(default=0, help_text="Percentage of users who completed this field")
    
    date = models.DateField(help_text="Date this metric was calculated for")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'field_completion_metrics'
        unique_together = [['form', 'field_id', 'date']]
        indexes = [
            models.Index(fields=['form', 'date']),
        ]
    
    def __str__(self):
        return f"{self.field_label} - {self.avg_completion_time}s avg"


class FormCacheConfig(models.Model):
    """Caching configuration for frequently accessed forms"""
    CACHE_STRATEGIES = [
        ('aggressive', 'Aggressive - Cache everything, refresh on publish'),
        ('balanced', 'Balanced - Cache with periodic refresh'),
        ('minimal', 'Minimal - Cache only static assets'),
        ('none', 'No Caching'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='cache_config')
    
    strategy = models.CharField(max_length=20, choices=CACHE_STRATEGIES, default='balanced')
    cache_ttl = models.IntegerField(default=3600, help_text="Cache TTL in seconds")
    
    # CDN settings
    cdn_enabled = models.BooleanField(default=False)
    cdn_purge_on_update = models.BooleanField(default=True)
    
    # Asset optimization
    lazy_load_images = models.BooleanField(default=True)
    lazy_load_fields = models.BooleanField(default=True, help_text="Lazy load fields below the fold")
    lazy_load_threshold = models.IntegerField(default=5, help_text="Number of fields visible initially")
    
    # Image optimization
    auto_optimize_images = models.BooleanField(default=True)
    image_quality = models.IntegerField(default=85, help_text="JPEG quality 1-100")
    max_image_width = models.IntegerField(default=1920)
    convert_to_webp = models.BooleanField(default=True)
    
    # Prefetching
    prefetch_next_step = models.BooleanField(default=True)
    preload_fonts = models.BooleanField(default=True)
    
    last_cache_purge = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'form_cache_configs'
    
    def __str__(self):
        return f"Cache config for {self.form.title}"


class PerformanceAlert(models.Model):
    """Alerts for performance degradation"""
    ALERT_TYPES = [
        ('slow_load', 'Slow Load Time'),
        ('high_error_rate', 'High Error Rate'),
        ('drop_off_spike', 'Drop-off Rate Spike'),
        ('cache_miss', 'High Cache Miss Rate'),
        ('slow_field', 'Slow Field Completion'),
    ]
    
    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='performance_alerts')
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='warning')
    message = models.TextField()
    metric_value = models.FloatField()
    threshold_value = models.FloatField()
    details = models.JSONField(default=dict)
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'performance_alerts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.severity.upper()}: {self.alert_type} for {self.form.title}"


class AssetOptimization(models.Model):
    """Track optimized assets for forms"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='optimized_assets')
    original_url = models.URLField()
    optimized_url = models.URLField()
    original_size = models.IntegerField(help_text="Size in bytes")
    optimized_size = models.IntegerField(help_text="Size in bytes")
    compression_ratio = models.FloatField(help_text="Percentage saved")
    asset_type = models.CharField(
        max_length=20,
        choices=[('image', 'Image'), ('font', 'Font'), ('script', 'Script'), ('style', 'Stylesheet')]
    )
    format = models.CharField(max_length=20, blank=True, help_text="e.g., webp, woff2")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'asset_optimizations'
    
    def __str__(self):
        return f"Optimized {self.asset_type}: {self.compression_ratio}% saved"
