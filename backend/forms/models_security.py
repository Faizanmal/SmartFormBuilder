"""
Advanced security and compliance models
"""
from django.db import models
import uuid


class TwoFactorAuth(models.Model):
    """Two-factor authentication settings for users"""
    METHOD_CHOICES = [
        ('totp', 'Authenticator App (TOTP)'),
        ('sms', 'SMS'),
        ('email', 'Email'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='two_factor')
    is_enabled = models.BooleanField(default=False)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='totp')
    secret_key = models.CharField(max_length=100, blank=True, help_text="Encrypted TOTP secret")
    backup_codes = models.JSONField(default=list, help_text="Encrypted backup codes")
    phone_number = models.CharField(max_length=20, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'two_factor_auth'
    
    def __str__(self):
        return f"{self.user.email} - 2FA {self.method}"


class SSOProvider(models.Model):
    """Single Sign-On provider configurations"""
    PROVIDER_CHOICES = [
        ('google', 'Google'),
        ('microsoft', 'Microsoft'),
        ('saml', 'SAML'),
        ('okta', 'Okta'),
        ('auth0', 'Auth0'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'users.Team',
        on_delete=models.CASCADE,
        related_name='sso_providers',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100)
    provider_type = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    client_id = models.CharField(max_length=200)
    client_secret = models.CharField(max_length=500, help_text="Encrypted")
    
    # SAML specific
    entity_id = models.CharField(max_length=500, blank=True)
    sso_url = models.URLField(blank=True)
    x509_cert = models.TextField(blank=True)
    
    # Configuration
    domain_restriction = models.JSONField(
        default=list,
        help_text="Allowed email domains (e.g., ['company.com'])"
    )
    auto_provision = models.BooleanField(default=True, help_text="Auto-create users on first login")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sso_providers'
    
    def __str__(self):
        return f"{self.name} - {self.provider_type}"


class EncryptedSubmission(models.Model):
    """End-to-end encrypted submissions for sensitive data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.OneToOneField('forms.Submission', on_delete=models.CASCADE, related_name='encryption')
    encrypted_data = models.BinaryField(help_text="AES-256 encrypted submission data")
    encryption_key_id = models.CharField(max_length=100, help_text="Key ID for key rotation")
    encryption_algorithm = models.CharField(max_length=50, default='AES-256-GCM')
    iv = models.BinaryField(help_text="Initialization vector")
    auth_tag = models.BinaryField(null=True, blank=True, help_text="Authentication tag for GCM")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'encrypted_submissions'
    
    def __str__(self):
        return f"Encrypted Submission {self.submission.id}"


class DataPrivacyRequest(models.Model):
    """GDPR/CCPA data privacy requests"""
    REQUEST_TYPES = [
        ('export', 'Data Export'),
        ('deletion', 'Data Deletion'),
        ('rectification', 'Data Rectification'),
        ('portability', 'Data Portability'),
        ('restriction', 'Processing Restriction'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requester_email = models.EmailField()
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verification_token = models.CharField(max_length=100, unique=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Request details
    reason = models.TextField(blank=True)
    data_scope = models.JSONField(
        default=dict,
        help_text="Specific data requested (forms, submissions, etc.)"
    )
    
    # Processing
    processed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_privacy_requests'
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    # Export data
    export_file_url = models.URLField(blank=True)
    export_expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'data_privacy_requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.request_type} - {self.requester_email}"


class ConsentTracking(models.Model):
    """Track user consent for data processing"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey('forms.Submission', on_delete=models.CASCADE, related_name='consents')
    consent_type = models.CharField(
        max_length=50,
        choices=[
            ('data_processing', 'Data Processing'),
            ('marketing', 'Marketing Communications'),
            ('third_party_sharing', 'Third-party Sharing'),
            ('analytics', 'Analytics'),
        ]
    )
    granted = models.BooleanField()
    consent_text = models.TextField(help_text="Exact consent text shown to user")
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'consent_tracking'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.consent_type} - {'Granted' if self.granted else 'Denied'}"


class SecurityAuditLog(models.Model):
    """Comprehensive audit trail for security events"""
    EVENT_TYPES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('login_failed', 'Failed Login'),
        ('2fa_enabled', '2FA Enabled'),
        ('2fa_disabled', '2FA Disabled'),
        ('password_changed', 'Password Changed'),
        ('data_accessed', 'Data Accessed'),
        ('data_exported', 'Data Exported'),
        ('data_deleted', 'Data Deleted'),
        ('permission_changed', 'Permission Changed'),
        ('suspicious_activity', 'Suspicious Activity'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    location = models.JSONField(default=dict, blank=True, help_text="Geolocation data")
    metadata = models.JSONField(default=dict, help_text="Additional event context")
    risk_level = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='low'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'security_audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['event_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.user.email if self.user else 'Anonymous'}"


class IPAccessControl(models.Model):
    """IP-based access controls per form"""
    ACCESS_TYPES = [
        ('whitelist', 'Whitelist'),
        ('blacklist', 'Blacklist'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='ip_controls')
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPES)
    ip_ranges = models.JSONField(
        default=list,
        help_text="List of IP addresses or CIDR ranges"
    )
    countries = models.JSONField(
        default=list,
        blank=True,
        help_text="Country codes (ISO 3166-1 alpha-2)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ip_access_controls'
    
    def __str__(self):
        return f"{self.form.title} - {self.access_type}"


class SecurityScan(models.Model):
    """Security scanning results for submissions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.OneToOneField('forms.Submission', on_delete=models.CASCADE, related_name='security_scan')
    scan_completed = models.BooleanField(default=False)
    is_malicious = models.BooleanField(default=False)
    threats_detected = models.JSONField(
        default=list,
        help_text="List of detected threats (SQL injection, XSS, etc.)"
    )
    risk_score = models.IntegerField(default=0, help_text="0-100 risk score")
    blocked = models.BooleanField(default=False)
    scan_details = models.JSONField(default=dict)
    scanned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'security_scans'
    
    def __str__(self):
        return f"Scan {self.submission.id} - {'Malicious' if self.is_malicious else 'Clean'}"
