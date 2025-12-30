"""
Enhanced Security & Compliance Models

Features:
- Zero-Knowledge Encryption
- Blockchain Audit Trails
- AI-Powered Threat Detection
- Auto-Compliance Scanning (GDPR, CCPA, HIPAA)
- Data Residency Controls
- Advanced Audit Trail Automation
"""
from django.db import models
import uuid


# ============================================================================
# ZERO-KNOWLEDGE ENCRYPTION
# ============================================================================

class ZeroKnowledgeEncryption(models.Model):
    """Zero-knowledge encryption configuration for sensitive form data"""
    ENCRYPTION_SCHEMES = [
        ('aes256_gcm', 'AES-256-GCM'),
        ('chacha20_poly1305', 'ChaCha20-Poly1305'),
        ('xchacha20_poly1305', 'XChaCha20-Poly1305'),
    ]
    
    KEY_DERIVATION_FUNCTIONS = [
        ('pbkdf2', 'PBKDF2'),
        ('argon2id', 'Argon2id'),
        ('scrypt', 'Scrypt'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='zk_encryption_config')
    
    is_enabled = models.BooleanField(default=False)
    encryption_scheme = models.CharField(max_length=30, choices=ENCRYPTION_SCHEMES, default='aes256_gcm')
    key_derivation = models.CharField(max_length=30, choices=KEY_DERIVATION_FUNCTIONS, default='argon2id')
    
    # Client-side encryption settings
    client_side_encryption = models.BooleanField(default=True)
    key_stored_locally = models.BooleanField(default=True, help_text="Key stored only on client")
    
    # Fields to encrypt
    encrypted_fields = models.JSONField(
        default=list,
        help_text="List of field IDs requiring encryption"
    )
    
    # Key management
    key_rotation_days = models.IntegerField(default=90)
    last_key_rotation = models.DateTimeField(null=True, blank=True)
    
    # Recovery settings
    recovery_enabled = models.BooleanField(default=False)
    recovery_shares = models.IntegerField(default=3, help_text="Shamir secret sharing shares")
    recovery_threshold = models.IntegerField(default=2, help_text="Shares needed for recovery")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'zk_encryption_configs'
    
    def __str__(self):
        return f"ZK Encryption for {self.form.title}"


class EncryptionKey(models.Model):
    """Key metadata for encrypted submissions (key material never stored)"""
    KEY_TYPES = [
        ('form_key', 'Form Encryption Key'),
        ('field_key', 'Field-Specific Key'),
        ('recovery_share', 'Recovery Share'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    zk_config = models.ForeignKey(ZeroKnowledgeEncryption, on_delete=models.CASCADE, related_name='key_metadata')
    
    key_type = models.CharField(max_length=20, choices=KEY_TYPES)
    key_id = models.CharField(max_length=100, unique=True, help_text="Public key identifier")
    
    # Key derivation parameters (for reconstruction)
    salt = models.BinaryField(help_text="Salt used in key derivation")
    iterations = models.IntegerField(default=100000)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'encryption_keys'
    
    def __str__(self):
        return f"Key {self.key_id[:16]}..."


# ============================================================================
# BLOCKCHAIN AUDIT TRAILS
# ============================================================================

class BlockchainConfig(models.Model):
    """Blockchain integration for immutable audit trails"""
    BLOCKCHAIN_NETWORKS = [
        ('ethereum', 'Ethereum'),
        ('polygon', 'Polygon'),
        ('arbitrum', 'Arbitrum'),
        ('optimism', 'Optimism'),
        ('private', 'Private Network'),
        ('hyperledger', 'Hyperledger Fabric'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'users.Team',
        on_delete=models.CASCADE,
        related_name='blockchain_configs',
        null=True,
        blank=True
    )
    
    name = models.CharField(max_length=200)
    is_enabled = models.BooleanField(default=False)
    network = models.CharField(max_length=30, choices=BLOCKCHAIN_NETWORKS, default='polygon')
    
    # Network configuration
    rpc_url = models.URLField(blank=True)
    contract_address = models.CharField(max_length=100, blank=True)
    
    # API credentials
    api_key_encrypted = models.TextField(blank=True)
    wallet_address = models.CharField(max_length=100, blank=True)
    
    # What to record
    record_submissions = models.BooleanField(default=True)
    record_updates = models.BooleanField(default=True)
    record_deletions = models.BooleanField(default=True)
    record_access = models.BooleanField(default=False)
    
    # Privacy settings
    store_hashes_only = models.BooleanField(default=True, help_text="Store hashes, not data")
    hash_algorithm = models.CharField(max_length=20, default='sha256')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'blockchain_configs'
    
    def __str__(self):
        return f"Blockchain: {self.name} ({self.network})"


class BlockchainAuditEntry(models.Model):
    """Individual blockchain audit entries"""
    ENTRY_TYPES = [
        ('submission_created', 'Submission Created'),
        ('submission_updated', 'Submission Updated'),
        ('submission_deleted', 'Submission Deleted'),
        ('data_accessed', 'Data Accessed'),
        ('form_published', 'Form Published'),
        ('consent_granted', 'Consent Granted'),
        ('consent_revoked', 'Consent Revoked'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    config = models.ForeignKey(BlockchainConfig, on_delete=models.CASCADE, related_name='entries')
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, null=True, blank=True)
    submission = models.ForeignKey('forms.Submission', on_delete=models.SET_NULL, null=True, blank=True)
    
    entry_type = models.CharField(max_length=30, choices=ENTRY_TYPES)
    
    # Data to record
    data_hash = models.CharField(max_length=100, help_text="SHA-256 hash of data")
    metadata = models.JSONField(default=dict, help_text="Non-sensitive metadata")
    
    # Blockchain transaction
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_hash = models.CharField(max_length=100, blank=True)
    block_number = models.BigIntegerField(null=True, blank=True)
    gas_used = models.BigIntegerField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'blockchain_audit_entries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['data_hash']),
            models.Index(fields=['transaction_hash']),
        ]
    
    def __str__(self):
        return f"{self.entry_type} - {self.data_hash[:16]}..."


# ============================================================================
# AI-POWERED THREAT DETECTION
# ============================================================================

class ThreatDetectionConfig(models.Model):
    """AI-powered threat detection configuration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='threat_detection_config')
    
    is_enabled = models.BooleanField(default=True)
    
    # Detection features
    detect_sql_injection = models.BooleanField(default=True)
    detect_xss = models.BooleanField(default=True)
    detect_bot_submissions = models.BooleanField(default=True)
    detect_velocity_abuse = models.BooleanField(default=True)
    detect_data_exfiltration = models.BooleanField(default=True)
    detect_anomalous_patterns = models.BooleanField(default=True)
    
    # ML-based detection
    ml_anomaly_detection = models.BooleanField(default=True)
    ml_model_version = models.CharField(max_length=50, default='v1.0')
    anomaly_threshold = models.FloatField(default=0.85, help_text="Anomaly score threshold")
    
    # Response actions
    auto_block_threats = models.BooleanField(default=True)
    block_duration_hours = models.IntegerField(default=24)
    notify_on_threat = models.BooleanField(default=True)
    notification_emails = models.JSONField(default=list)
    
    # Rate limiting
    rate_limit_enabled = models.BooleanField(default=True)
    max_submissions_per_ip_hour = models.IntegerField(default=10)
    max_submissions_per_ip_day = models.IntegerField(default=50)
    
    # Fingerprinting
    device_fingerprinting = models.BooleanField(default=True)
    behavioral_fingerprinting = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'threat_detection_configs'
    
    def __str__(self):
        return f"Threat Detection for {self.form.title}"


class ThreatEvent(models.Model):
    """Detected threat events"""
    THREAT_TYPES = [
        ('sql_injection', 'SQL Injection Attempt'),
        ('xss', 'XSS Attempt'),
        ('bot', 'Bot Submission'),
        ('velocity_abuse', 'Velocity Abuse'),
        ('data_exfiltration', 'Data Exfiltration'),
        ('anomalous_pattern', 'Anomalous Pattern'),
        ('brute_force', 'Brute Force'),
        ('credential_stuffing', 'Credential Stuffing'),
        ('form_spam', 'Form Spam'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('detected', 'Detected'),
        ('blocked', 'Blocked'),
        ('allowed', 'Allowed'),
        ('investigating', 'Investigating'),
        ('false_positive', 'False Positive'),
        ('confirmed', 'Confirmed Threat'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='threat_events')
    
    threat_type = models.CharField(max_length=30, choices=THREAT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='detected')
    
    # Source information
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    device_fingerprint = models.CharField(max_length=100, blank=True)
    
    # Threat details
    description = models.TextField()
    detection_reason = models.TextField()
    ml_score = models.FloatField(default=0, help_text="ML confidence score")
    
    # Affected data
    submission_attempt_data = models.JSONField(default=dict)
    payload_analysis = models.JSONField(default=dict)
    
    # Rule that triggered
    triggered_rules = models.JSONField(default=list)
    
    # Response taken
    action_taken = models.CharField(max_length=50, blank=True)
    blocked_until = models.DateTimeField(null=True, blank=True)
    
    # Review
    reviewed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'threat_events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['form', 'threat_type']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['severity', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.severity.upper()}: {self.threat_type} - {self.ip_address}"


class IPBlocklist(models.Model):
    """IP addresses blocked for security reasons"""
    BLOCK_REASONS = [
        ('manual', 'Manual Block'),
        ('threat_detected', 'Threat Detected'),
        ('velocity_abuse', 'Velocity Abuse'),
        ('bot_activity', 'Bot Activity'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(
        'forms.Form',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ip_blocklist',
        help_text="Null for global block"
    )
    
    ip_address = models.GenericIPAddressField()
    ip_range = models.CharField(max_length=50, blank=True, help_text="CIDR notation")
    
    reason = models.CharField(max_length=30, choices=BLOCK_REASONS)
    description = models.TextField(blank=True)
    
    is_permanent = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    threat_event = models.ForeignKey(ThreatEvent, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ip_blocklist'
        indexes = [
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"Blocked: {self.ip_address}"


# ============================================================================
# COMPLIANCE AUTOMATION
# ============================================================================

class ComplianceFramework(models.Model):
    """Compliance frameworks and their requirements"""
    FRAMEWORKS = [
        ('gdpr', 'GDPR'),
        ('ccpa', 'CCPA'),
        ('hipaa', 'HIPAA'),
        ('pci_dss', 'PCI-DSS'),
        ('sox', 'SOX'),
        ('ferpa', 'FERPA'),
        ('coppa', 'COPPA'),
        ('lgpd', 'LGPD'),
        ('pipeda', 'PIPEDA'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, choices=FRAMEWORKS, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Requirements
    requirements = models.JSONField(
        default=list,
        help_text="List of compliance requirements with IDs and descriptions"
    )
    
    # Automated checks
    automated_checks = models.JSONField(
        default=list,
        help_text="List of automated compliance checks"
    )
    
    # Documentation requirements
    documentation_requirements = models.JSONField(default=list)
    
    # Regional applicability
    applicable_regions = models.JSONField(default=list, help_text="ISO country codes")
    
    version = models.CharField(max_length=20)
    last_updated = models.DateField()
    
    class Meta:
        db_table = 'compliance_frameworks'
    
    def __str__(self):
        return f"{self.code.upper()} - {self.name}"


class FormComplianceConfig(models.Model):
    """Form-specific compliance configuration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='compliance_config')
    
    # Required frameworks
    required_frameworks = models.ManyToManyField(ComplianceFramework, related_name='forms')
    
    # Auto-scanning
    auto_scan_enabled = models.BooleanField(default=True)
    scan_frequency_hours = models.IntegerField(default=24)
    last_scan_at = models.DateTimeField(null=True, blank=True)
    
    # Data classification
    data_classification = models.CharField(
        max_length=30,
        choices=[
            ('public', 'Public'),
            ('internal', 'Internal'),
            ('confidential', 'Confidential'),
            ('restricted', 'Restricted'),
            ('pii', 'PII'),
            ('phi', 'PHI'),
            ('pci', 'PCI'),
        ],
        default='internal'
    )
    
    # PII detection
    pii_fields = models.JSONField(default=list, help_text="Fields containing PII")
    sensitive_fields = models.JSONField(default=list, help_text="Other sensitive fields")
    
    # Retention
    data_retention_days = models.IntegerField(default=365)
    auto_delete_enabled = models.BooleanField(default=False)
    
    # Consent requirements
    consent_required = models.BooleanField(default=True)
    consent_version = models.CharField(max_length=20, default='1.0')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'form_compliance_configs'
    
    def __str__(self):
        return f"Compliance config for {self.form.title}"


class AdvancedComplianceScan(models.Model):
    """Automated compliance scan results - Enhanced version with more detailed tracking"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    RESULT_CHOICES = [
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('partial', 'Partial Compliance'),
        ('needs_review', 'Needs Review'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='advanced_compliance_scans')
    framework = models.ForeignKey(ComplianceFramework, on_delete=models.CASCADE)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, null=True, blank=True)
    
    # Scores
    overall_score = models.FloatField(default=0, help_text="0-100 compliance score")
    
    # Check results
    checks_passed = models.IntegerField(default=0)
    checks_failed = models.IntegerField(default=0)
    checks_warning = models.IntegerField(default=0)
    checks_skipped = models.IntegerField(default=0)
    
    # Detailed results
    check_results = models.JSONField(
        default=list,
        help_text="Individual check results"
    )
    
    # Issues found
    issues = models.JSONField(default=list)
    critical_issues = models.IntegerField(default=0)
    
    # Recommendations
    recommendations = models.JSONField(default=list)
    auto_fixable_issues = models.JSONField(default=list)
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'advanced_compliance_scans'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Scan: {self.form.title} - {self.framework.code}"


# ============================================================================
# DATA RESIDENCY CONTROLS
# ============================================================================

class DataResidencyConfig(models.Model):
    """Data residency and geographic storage controls"""
    REGIONS = [
        ('us-east', 'US East'),
        ('us-west', 'US West'),
        ('eu-west', 'EU West'),
        ('eu-central', 'EU Central'),
        ('apac', 'Asia Pacific'),
        ('australia', 'Australia'),
        ('canada', 'Canada'),
        ('brazil', 'Brazil'),
        ('india', 'India'),
        ('uk', 'United Kingdom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='data_residency_config')
    
    is_enabled = models.BooleanField(default=False)
    
    # Primary storage region
    primary_region = models.CharField(max_length=30, choices=REGIONS, default='us-east')
    
    # Allowed regions
    allowed_regions = models.JSONField(default=list, help_text="Regions where data can be stored")
    forbidden_regions = models.JSONField(default=list, help_text="Regions where data cannot be stored")
    
    # User-based routing
    auto_route_by_user_location = models.BooleanField(default=False)
    user_location_field = models.CharField(max_length=100, blank=True, help_text="Field containing user location")
    
    # Replication settings
    replication_enabled = models.BooleanField(default=False)
    replication_regions = models.JSONField(default=list)
    
    # Transfer restrictions
    cross_border_transfer_allowed = models.BooleanField(default=True)
    transfer_requires_consent = models.BooleanField(default=False)
    
    # Compliance mapping
    region_compliance_mapping = models.JSONField(
        default=dict,
        help_text="Map regions to required compliance frameworks"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'data_residency_configs'
    
    def __str__(self):
        return f"Data Residency for {self.form.title}"


class SubmissionDataLocation(models.Model):
    """Track where each submission's data is stored"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.OneToOneField('forms.Submission', on_delete=models.CASCADE, related_name='data_location')
    
    # Storage location
    storage_region = models.CharField(max_length=30)
    storage_provider = models.CharField(max_length=50, default='primary')
    storage_path = models.TextField(blank=True)
    
    # Encryption
    encrypted_at_rest = models.BooleanField(default=True)
    encryption_key_region = models.CharField(max_length=30, blank=True)
    
    # Replication
    replicated_to = models.JSONField(default=list, help_text="Regions replicated to")
    last_replication_at = models.DateTimeField(null=True, blank=True)
    
    # Transfer history
    transfer_history = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'submission_data_locations'
    
    def __str__(self):
        return f"Location: {self.storage_region}"


# ============================================================================
# ADVANCED AUDIT TRAIL AUTOMATION
# ============================================================================

class AuditTrailConfig(models.Model):
    """Automated audit trail configuration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='audit_trail_config')
    
    is_enabled = models.BooleanField(default=True)
    
    # What to log
    log_views = models.BooleanField(default=False)
    log_submissions = models.BooleanField(default=True)
    log_updates = models.BooleanField(default=True)
    log_deletions = models.BooleanField(default=True)
    log_exports = models.BooleanField(default=True)
    log_access = models.BooleanField(default=True)
    log_field_changes = models.BooleanField(default=True)
    
    # Detail level
    capture_before_after = models.BooleanField(default=True)
    capture_user_context = models.BooleanField(default=True)
    capture_device_info = models.BooleanField(default=True)
    capture_geolocation = models.BooleanField(default=False)
    
    # Retention
    retention_days = models.IntegerField(default=2555, help_text="7 years default")
    
    # Exports
    auto_export_enabled = models.BooleanField(default=False)
    export_format = models.CharField(
        max_length=20,
        choices=[('json', 'JSON'), ('csv', 'CSV'), ('pdf', 'PDF')],
        default='json'
    )
    export_frequency = models.CharField(
        max_length=20,
        choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
        default='monthly'
    )
    export_destination = models.URLField(blank=True)
    
    # Tampering protection
    tamper_evident = models.BooleanField(default=True)
    hash_chain_enabled = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'audit_trail_configs'
    
    def __str__(self):
        return f"Audit Trail for {self.form.title}"


class AuditLogEntry(models.Model):
    """Individual audit log entries with hash chain"""
    ACTIONS = [
        ('create', 'Create'),
        ('read', 'Read'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('export', 'Export'),
        ('access', 'Access'),
        ('share', 'Share'),
        ('consent', 'Consent Change'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='audit_log_entries')
    
    # Action details
    action = models.CharField(max_length=20, choices=ACTIONS)
    resource_type = models.CharField(max_length=50, help_text="submission, form, field, etc.")
    resource_id = models.CharField(max_length=100)
    
    # Actor
    actor_user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    actor_email = models.EmailField(blank=True)
    actor_ip = models.GenericIPAddressField(null=True, blank=True)
    actor_user_agent = models.TextField(blank=True)
    
    # Change details
    previous_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    changes = models.JSONField(default=dict, help_text="Diff of changes")
    
    # Context
    reason = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    
    # Hash chain for tamper evidence
    entry_hash = models.CharField(max_length=64, unique=True)
    previous_entry_hash = models.CharField(max_length=64, blank=True)
    
    # Verification
    is_verified = models.BooleanField(default=True)
    verification_failed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_log_entries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['form', '-created_at']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['actor_user']),
            models.Index(fields=['entry_hash']),
        ]
    
    def __str__(self):
        return f"{self.action} {self.resource_type} by {self.actor_email or 'System'}"


class AdvancedComplianceReport(models.Model):
    """Advanced generated compliance reports with extended features"""
    REPORT_TYPES = [
        ('audit_trail', 'Audit Trail Export'),
        ('compliance_summary', 'Compliance Summary'),
        ('data_inventory', 'Data Inventory'),
        ('access_report', 'Access Report'),
        ('consent_report', 'Consent Report'),
        ('breach_assessment', 'Breach Assessment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='advanced_compliance_reports')
    
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    title = models.CharField(max_length=255)
    
    # Date range
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Report content
    summary = models.JSONField(default=dict)
    detailed_data = models.JSONField(default=dict)
    
    # Generated files
    pdf_url = models.URLField(blank=True)
    csv_url = models.URLField(blank=True)
    json_url = models.URLField(blank=True)
    
    # Metadata
    generated_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'advanced_compliance_reports'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.report_type}: {self.title}"
