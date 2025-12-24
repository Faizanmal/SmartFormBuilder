"""
Mobile-optimized form experience models
"""
from django.db import models
import uuid


class MobileOptimization(models.Model):
    """Mobile-specific optimizations for forms"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='mobile_optimization')
    
    # Touch optimization
    touch_enabled = models.BooleanField(default=True)
    button_size = models.CharField(
        max_length=20,
        choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')],
        default='large'
    )
    swipe_gestures_enabled = models.BooleanField(default=True)
    
    # Camera integration
    camera_enabled = models.BooleanField(default=False, help_text="Enable camera for file uploads")
    qr_scanner_enabled = models.BooleanField(default=False)
    
    # Offline support
    offline_mode_enabled = models.BooleanField(default=True)
    cache_strategy = models.CharField(
        max_length=50,
        choices=[
            ('cache_first', 'Cache First'),
            ('network_first', 'Network First'),
            ('cache_only', 'Cache Only'),
        ],
        default='network_first'
    )
    max_cache_size_mb = models.IntegerField(default=50)
    
    # Push notifications
    push_notifications_enabled = models.BooleanField(default=False)
    notification_events = models.JSONField(
        default=list,
        help_text="Events that trigger notifications (e.g., ['form_updated', 'reminder'])"
    )
    
    # Geolocation
    geolocation_enabled = models.BooleanField(default=False)
    auto_detect_location = models.BooleanField(default=False)
    location_accuracy = models.CharField(
        max_length=20,
        choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')],
        default='medium'
    )
    
    # Mobile layout
    single_column_layout = models.BooleanField(default=True)
    fixed_header = models.BooleanField(default=True)
    progress_indicator_style = models.CharField(
        max_length=20,
        choices=[('bar', 'Progress Bar'), ('steps', 'Step Indicator'), ('percentage', 'Percentage')],
        default='bar'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mobile_optimizations'
    
    def __str__(self):
        return f"Mobile config for {self.form.title}"


class GeolocationField(models.Model):
    """Geolocation data for form fields"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey('forms.Submission', on_delete=models.CASCADE, related_name='geolocations')
    field_id = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    accuracy = models.FloatField(help_text="Accuracy in meters")
    altitude = models.FloatField(null=True, blank=True)
    address = models.JSONField(
        default=dict,
        blank=True,
        help_text="Reverse geocoded address"
    )
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'geolocation_fields'
    
    def __str__(self):
        return f"Location for submission {self.submission.id}"


class OfflineSubmission(models.Model):
    """Queue for submissions made offline"""
    STATUS_CHOICES = [
        ('pending', 'Pending Sync'),
        ('syncing', 'Syncing'),
        ('synced', 'Synced'),
        ('failed', 'Sync Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='offline_submissions')
    device_id = models.CharField(max_length=200, help_text="Unique device identifier")
    submission_data = models.JSONField(help_text="Complete submission data")
    files_metadata = models.JSONField(
        default=list,
        help_text="Metadata for attached files (uploaded separately)"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sync_attempts = models.IntegerField(default=0)
    last_sync_attempt = models.DateTimeField(null=True, blank=True)
    sync_error = models.TextField(blank=True)
    synced_submission_id = models.UUIDField(null=True, blank=True, help_text="ID of synced submission")
    created_at = models.DateTimeField(help_text="When offline submission was created")
    synced_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'offline_submissions'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['device_id', 'status']),
        ]
    
    def __str__(self):
        return f"Offline submission for {self.form.title} - {self.status}"


class PushNotificationSubscription(models.Model):
    """Push notification subscriptions for mobile users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='push_subscriptions'
    )
    device_id = models.CharField(max_length=200, unique=True)
    endpoint = models.URLField(help_text="Push service endpoint")
    auth_key = models.CharField(max_length=500)
    p256dh_key = models.CharField(max_length=500)
    device_type = models.CharField(
        max_length=20,
        choices=[('android', 'Android'), ('ios', 'iOS'), ('web', 'Web')],
        default='web'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'push_notification_subscriptions'
    
    def __str__(self):
        return f"{self.device_type} - {self.device_id}"


class FormNotification(models.Model):
    """Notifications sent to users about forms"""
    NOTIFICATION_TYPES = [
        ('form_reminder', 'Form Reminder'),
        ('form_updated', 'Form Updated'),
        ('submission_received', 'Submission Received'),
        ('deadline_approaching', 'Deadline Approaching'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='push_notifications')
    subscription = models.ForeignKey(
        PushNotificationSubscription,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    body = models.TextField()
    data = models.JSONField(default=dict, help_text="Additional notification data")
    icon_url = models.URLField(blank=True)
    action_url = models.URLField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'form_notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} for {self.form.title}"


class MobileAnalytics(models.Model):
    """Analytics specific to mobile form usage"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='mobile_analytics')
    device_type = models.CharField(max_length=50)
    os = models.CharField(max_length=50)
    os_version = models.CharField(max_length=50)
    browser = models.CharField(max_length=50)
    screen_resolution = models.CharField(max_length=50)
    
    # Interaction metrics
    touch_interactions = models.IntegerField(default=0)
    swipe_actions = models.IntegerField(default=0)
    camera_uses = models.IntegerField(default=0)
    geolocation_uses = models.IntegerField(default=0)
    
    # Performance metrics
    load_time_ms = models.IntegerField(help_text="Form load time in milliseconds")
    completion_time_s = models.IntegerField(help_text="Time to complete in seconds")
    offline_duration_s = models.IntegerField(default=0, help_text="Time spent in offline mode")
    
    # Session info
    session_id = models.CharField(max_length=100)
    submitted = models.BooleanField(default=False)
    abandoned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'mobile_analytics'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['form', 'device_type']),
        ]
    
    def __str__(self):
        return f"{self.form.title} - {self.device_type}"


class QRCodeScan(models.Model):
    """Track QR code scans for forms"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='qr_scans')
    submission = models.ForeignKey(
        'forms.Submission',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='qr_scans'
    )
    scanned_data = models.TextField(help_text="Data from QR code")
    field_id = models.CharField(max_length=100, help_text="Field where QR data was used")
    device_type = models.CharField(max_length=50)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'qr_code_scans'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"QR scan for {self.form.title}"
