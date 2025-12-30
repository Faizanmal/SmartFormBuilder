"""
Mobile & PWA Enhancements Models

Features:
- Offline Form Synchronization
- Biometric Authentication
- Geolocation Features
- Mobile Payment Optimization (Apple Pay, Google Pay)
- Advanced Push Notifications
"""
from django.db import models
from django.conf import settings
import uuid


# ============================================================================
# OFFLINE SYNCHRONIZATION (Enhanced)
# ============================================================================

class OfflineSyncConfig(models.Model):
    """Advanced offline synchronization configuration"""
    SYNC_STRATEGIES = [
        ('queue_first', 'Queue First'),
        ('sync_when_online', 'Sync When Online'),
        ('background_sync', 'Background Sync'),
        ('periodic_sync', 'Periodic Sync'),
    ]
    
    CONFLICT_RESOLUTION = [
        ('server_wins', 'Server Wins'),
        ('client_wins', 'Client Wins'),
        ('merge', 'Merge'),
        ('manual', 'Manual Resolution'),
        ('timestamp', 'Latest Timestamp'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='offline_sync_config')
    
    is_enabled = models.BooleanField(default=True)
    sync_strategy = models.CharField(max_length=30, choices=SYNC_STRATEGIES, default='background_sync')
    
    # Conflict handling
    conflict_resolution = models.CharField(max_length=20, choices=CONFLICT_RESOLUTION, default='timestamp')
    
    # Storage limits
    max_offline_submissions = models.IntegerField(default=100)
    max_storage_mb = models.IntegerField(default=50)
    
    # Retry settings
    max_sync_retries = models.IntegerField(default=5)
    retry_interval_minutes = models.IntegerField(default=5)
    exponential_backoff = models.BooleanField(default=True)
    
    # Data handling
    compress_offline_data = models.BooleanField(default=True)
    encrypt_offline_data = models.BooleanField(default=True)
    
    # Partial sync
    partial_sync_enabled = models.BooleanField(default=True, help_text="Sync as fields are completed")
    
    # Status notifications
    notify_on_sync_complete = models.BooleanField(default=True)
    notify_on_sync_error = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'offline_sync_configs'
    
    def __str__(self):
        return f"Offline Sync for {self.form.title}"


class SyncQueue(models.Model):
    """Queue of pending synchronization items"""
    SYNC_STATUS = [
        ('pending', 'Pending'),
        ('syncing', 'Syncing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('conflict', 'Conflict'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='sync_queue')
    device_id = models.CharField(max_length=200)
    
    # Sync item
    local_id = models.CharField(max_length=100, help_text="Client-side ID")
    operation = models.CharField(
        max_length=20,
        choices=[('create', 'Create'), ('update', 'Update'), ('delete', 'Delete')]
    )
    data = models.JSONField()
    
    # Status
    status = models.CharField(max_length=20, choices=SYNC_STATUS, default='pending')
    retry_count = models.IntegerField(default=0)
    last_error = models.TextField(blank=True)
    
    # Timestamps
    created_offline_at = models.DateTimeField(help_text="When created offline")
    queued_at = models.DateTimeField(auto_now_add=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    
    # Result
    server_id = models.UUIDField(null=True, blank=True, help_text="Server-side submission ID")
    
    class Meta:
        db_table = 'sync_queue'
        ordering = ['created_offline_at']
        indexes = [
            models.Index(fields=['device_id', 'status']),
        ]
    
    def __str__(self):
        return f"Sync: {self.operation} - {self.status}"


class SyncConflict(models.Model):
    """Track and resolve sync conflicts"""
    RESOLUTION_STATUS = [
        ('pending', 'Pending Resolution'),
        ('auto_resolved', 'Auto Resolved'),
        ('manual_resolved', 'Manually Resolved'),
        ('discarded', 'Discarded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sync_item = models.ForeignKey(SyncQueue, on_delete=models.CASCADE, related_name='conflicts')
    
    # Conflict data
    client_data = models.JSONField()
    server_data = models.JSONField()
    merged_data = models.JSONField(null=True, blank=True)
    
    # Conflict details
    conflict_fields = models.JSONField(default=list, help_text="Fields with conflicts")
    conflict_type = models.CharField(max_length=50)
    
    # Resolution
    resolution_status = models.CharField(max_length=20, choices=RESOLUTION_STATUS, default='pending')
    resolution_strategy = models.CharField(max_length=30, blank=True)
    resolved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sync_conflicts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Conflict: {self.conflict_type} - {self.resolution_status}"


# ============================================================================
# BIOMETRIC AUTHENTICATION
# ============================================================================

class BiometricConfig(models.Model):
    """Biometric authentication configuration"""
    BIOMETRIC_TYPES = [
        ('fingerprint', 'Fingerprint'),
        ('face_id', 'Face ID'),
        ('iris', 'Iris Scan'),
        ('voice', 'Voice Recognition'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='biometric_config')
    
    is_enabled = models.BooleanField(default=False)
    
    # Allowed methods
    allowed_types = models.JSONField(
        default=list,
        help_text="List of allowed biometric types"
    )
    
    # Requirements
    require_on_start = models.BooleanField(default=False, help_text="Require auth to start form")
    require_on_submit = models.BooleanField(default=False, help_text="Require auth to submit")
    require_for_sensitive_fields = models.BooleanField(default=False)
    sensitive_field_ids = models.JSONField(default=list)
    
    # Fallback
    allow_passcode_fallback = models.BooleanField(default=True)
    passcode_fallback_after_failures = models.IntegerField(default=3)
    
    # Timeout
    auth_timeout_seconds = models.IntegerField(default=300)
    require_reauth_on_resume = models.BooleanField(default=True)
    
    # Platform-specific settings
    ios_settings = models.JSONField(default=dict)
    android_settings = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'biometric_configs'
    
    def __str__(self):
        return f"Biometric config for {self.form.title}"


class BiometricCredential(models.Model):
    """User biometric credentials"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='biometric_credentials')
    
    device_id = models.CharField(max_length=200)
    credential_id = models.CharField(max_length=500, unique=True)
    biometric_type = models.CharField(max_length=30)
    
    # Public key (for WebAuthn)
    public_key = models.TextField()
    attestation_type = models.CharField(max_length=50, blank=True)
    
    # Device info
    device_name = models.CharField(max_length=200, blank=True)
    device_os = models.CharField(max_length=50, blank=True)
    
    # Usage
    last_used_at = models.DateTimeField(null=True, blank=True)
    use_count = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'biometric_credentials'
        unique_together = [['user', 'device_id', 'biometric_type']]
    
    def __str__(self):
        return f"{self.user.email} - {self.biometric_type} on {self.device_name}"


class BiometricAuthEvent(models.Model):
    """Log of biometric authentication events"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='biometric_events')
    credential = models.ForeignKey(BiometricCredential, on_delete=models.CASCADE, null=True, blank=True)
    
    # Event details
    auth_type = models.CharField(max_length=30)
    success = models.BooleanField()
    
    # Context
    auth_purpose = models.CharField(max_length=50, help_text="form_start, submit, sensitive_field")
    field_id = models.CharField(max_length=100, blank=True)
    
    # Failure info
    failure_reason = models.CharField(max_length=100, blank=True)
    attempts_count = models.IntegerField(default=1)
    
    # Device info
    device_id = models.CharField(max_length=200)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'biometric_auth_events'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Biometric auth - {'Success' if self.success else 'Failed'}"


# ============================================================================
# GEOLOCATION FEATURES (Enhanced)
# ============================================================================

class GeolocationConfig(models.Model):
    """Advanced geolocation configuration for forms"""
    ACCURACY_LEVELS = [
        ('high', 'High (GPS)'),
        ('medium', 'Medium (WiFi)'),
        ('low', 'Low (IP-based)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='geolocation_config')
    
    is_enabled = models.BooleanField(default=False)
    
    # Collection settings
    accuracy_level = models.CharField(max_length=20, choices=ACCURACY_LEVELS, default='medium')
    require_location = models.BooleanField(default=False)
    allow_location_sharing = models.BooleanField(default=True)
    
    # Geofencing
    geofencing_enabled = models.BooleanField(default=False)
    geofence_rules = models.JSONField(
        default=list,
        help_text="""
        Geofence rules:
        [
            {
                "name": "Office Area",
                "type": "allow|deny",
                "shape": "circle",
                "center": {"lat": 40.7128, "lng": -74.0060},
                "radius_meters": 1000
            }
        ]
        """
    )
    
    # Location-based logic
    location_conditions = models.JSONField(
        default=list,
        help_text="Conditional logic based on location"
    )
    
    # Address auto-complete
    address_autocomplete_enabled = models.BooleanField(default=True)
    autocomplete_countries = models.JSONField(default=list, help_text="Limit to specific countries")
    
    # Reverse geocoding
    reverse_geocoding_enabled = models.BooleanField(default=True)
    geocoding_provider = models.CharField(max_length=30, default='google')
    
    # Map display
    show_map = models.BooleanField(default=False)
    map_style = models.CharField(max_length=50, default='roadmap')
    
    # Privacy
    store_precise_location = models.BooleanField(default=False, help_text="Store exact coordinates")
    anonymize_location = models.BooleanField(default=False, help_text="Round coordinates")
    anonymize_precision = models.IntegerField(default=2, help_text="Decimal places")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'geolocation_configs'
    
    def __str__(self):
        return f"Geolocation config for {self.form.title}"


class GeofenceEvent(models.Model):
    """Log of geofence events"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='geofence_events')
    session_id = models.CharField(max_length=100)
    
    # Event type
    event_type = models.CharField(
        max_length=20,
        choices=[('enter', 'Enter'), ('exit', 'Exit'), ('dwell', 'Dwell')]
    )
    geofence_name = models.CharField(max_length=200)
    
    # Location
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    accuracy = models.FloatField()
    
    # Result
    action_taken = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'geofence_events'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Geofence {self.event_type} - {self.geofence_name}"


class LocationValidation(models.Model):
    """Location-based field validation results"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='location_validations')
    submission = models.ForeignKey('forms.Submission', on_delete=models.CASCADE, null=True, blank=True)
    
    field_id = models.CharField(max_length=100)
    validation_type = models.CharField(max_length=50, help_text="address, coordinates, geofence")
    
    # Input
    input_value = models.TextField()
    
    # Validation result
    is_valid = models.BooleanField()
    validation_message = models.TextField(blank=True)
    
    # Geocoded data
    geocoded_address = models.JSONField(default=dict)
    geocoded_coordinates = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'location_validations'
    
    def __str__(self):
        return f"Location validation - {'Valid' if self.is_valid else 'Invalid'}"


# ============================================================================
# MOBILE PAYMENT OPTIMIZATION
# ============================================================================

class MobilePaymentConfig(models.Model):
    """Mobile payment configuration (Apple Pay, Google Pay, etc.)"""
    PAYMENT_PROVIDERS = [
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
        ('samsung_pay', 'Samsung Pay'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='mobile_payment_configs')
    
    provider = models.CharField(max_length=30, choices=PAYMENT_PROVIDERS)
    is_enabled = models.BooleanField(default=True)
    
    # Provider credentials
    merchant_id = models.CharField(max_length=200)
    credentials_encrypted = models.JSONField(default=dict)
    
    # Apple Pay specific
    apple_merchant_identifier = models.CharField(max_length=200, blank=True)
    apple_certificate_encrypted = models.TextField(blank=True)
    
    # Google Pay specific
    google_merchant_id = models.CharField(max_length=200, blank=True)
    google_gateway = models.CharField(max_length=50, blank=True)
    google_gateway_merchant_id = models.CharField(max_length=200, blank=True)
    
    # Payment settings
    supported_networks = models.JSONField(default=list, help_text="visa, mastercard, amex, etc.")
    supported_capabilities = models.JSONField(default=list, help_text="3DS, credit, debit")
    
    # Country/currency
    supported_countries = models.JSONField(default=list)
    supported_currencies = models.JSONField(default=list)
    default_currency = models.CharField(max_length=3, default='USD')
    
    # Display
    button_style = models.CharField(max_length=30, default='black')
    button_type = models.CharField(max_length=30, default='buy')
    
    # Shipping
    require_shipping = models.BooleanField(default=False)
    shipping_options = models.JSONField(default=list)
    
    # Testing
    test_mode = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mobile_payment_configs'
        unique_together = [['form', 'provider']]
    
    def __str__(self):
        return f"{self.provider} for {self.form.title}"


class MobilePaymentTransaction(models.Model):
    """Mobile payment transaction records"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('authorized', 'Authorized'),
        ('captured', 'Captured'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    config = models.ForeignKey(MobilePaymentConfig, on_delete=models.CASCADE, related_name='transactions')
    submission = models.ForeignKey('forms.Submission', on_delete=models.CASCADE, null=True, blank=True)
    
    # Transaction details
    provider_transaction_id = models.CharField(max_length=200, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Amount
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    
    # Payment method
    payment_method_type = models.CharField(max_length=50)
    card_network = models.CharField(max_length=30, blank=True)
    card_last_four = models.CharField(max_length=4, blank=True)
    
    # Billing info (sanitized)
    billing_name = models.CharField(max_length=200, blank=True)
    billing_email = models.EmailField(blank=True)
    billing_country = models.CharField(max_length=2, blank=True)
    
    # Device info
    device_type = models.CharField(max_length=50, blank=True)
    device_id = models.CharField(max_length=200, blank=True)
    
    # Error info
    error_code = models.CharField(max_length=50, blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mobile_payment_transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.config.provider} - {self.amount} {self.currency} - {self.status}"


# ============================================================================
# ADVANCED PUSH NOTIFICATIONS
# ============================================================================

class PushNotificationConfig(models.Model):
    """Advanced push notification configuration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='push_notification_config')
    
    is_enabled = models.BooleanField(default=False)
    
    # Notification triggers
    triggers = models.JSONField(
        default=list,
        help_text="""
        Notification triggers:
        [
            {
                "event": "form_reminder",
                "delay_hours": 24,
                "message_template": "Don't forget to complete your form!"
            },
            {
                "event": "deadline_approaching",
                "days_before": 2
            }
        ]
        """
    )
    
    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=True)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    quiet_hours_timezone = models.CharField(max_length=50, default='UTC')
    
    # Rate limiting
    max_notifications_per_day = models.IntegerField(default=5)
    min_interval_minutes = models.IntegerField(default=60)
    
    # Content
    default_title = models.CharField(max_length=200, default='Form Update')
    default_icon_url = models.URLField(blank=True)
    default_badge_url = models.URLField(blank=True)
    
    # Actions
    actions = models.JSONField(
        default=list,
        help_text="Action buttons for notifications"
    )
    
    # Rich notifications
    support_images = models.BooleanField(default=True)
    support_actions = models.BooleanField(default=True)
    
    # Personalization
    personalize_content = models.BooleanField(default=True)
    use_user_name = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'push_notification_configs'
    
    def __str__(self):
        return f"Push config for {self.form.title}"


class ScheduledNotification(models.Model):
    """Scheduled push notifications"""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    config = models.ForeignKey(PushNotificationConfig, on_delete=models.CASCADE, related_name='scheduled_notifications')
    subscription = models.ForeignKey('forms.PushNotificationSubscription', on_delete=models.CASCADE)
    
    # Schedule
    scheduled_for = models.DateTimeField()
    trigger_event = models.CharField(max_length=50)
    
    # Content
    title = models.CharField(max_length=200)
    body = models.TextField()
    image_url = models.URLField(blank=True)
    action_url = models.URLField(blank=True)
    data = models.JSONField(default=dict)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Retry
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'scheduled_notifications'
        ordering = ['scheduled_for']
        indexes = [
            models.Index(fields=['status', 'scheduled_for']),
        ]
    
    def __str__(self):
        return f"Scheduled: {self.title} for {self.scheduled_for}"


class NotificationAnalytics(models.Model):
    """Analytics for push notifications"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='notification_analytics')
    
    # Date
    date = models.DateField()
    
    # Metrics
    notifications_sent = models.IntegerField(default=0)
    notifications_delivered = models.IntegerField(default=0)
    notifications_clicked = models.IntegerField(default=0)
    notifications_dismissed = models.IntegerField(default=0)
    
    # By trigger
    by_trigger = models.JSONField(default=dict)
    
    # Rates
    delivery_rate = models.FloatField(default=0)
    click_rate = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_analytics'
        unique_together = [['form', 'date']]
        ordering = ['-date']
    
    def __str__(self):
        return f"Notification analytics: {self.form.title} - {self.date}"
