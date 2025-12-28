"""
Data quality, duplicate detection, and validation models
"""
from django.db import models
import uuid


class DataQualityScore(models.Model):
    """Data quality scoring for submissions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.OneToOneField(
        'forms.Submission',
        on_delete=models.CASCADE,
        related_name='quality_score'
    )
    
    # Overall score
    overall_score = models.FloatField(default=0, help_text="0-100 quality score")
    
    # Component scores
    completeness_score = models.FloatField(default=0, help_text="Required fields filled")
    accuracy_score = models.FloatField(default=0, help_text="Data validation passed")
    consistency_score = models.FloatField(default=0, help_text="Data consistency checks")
    validity_score = models.FloatField(default=0, help_text="External validation (email, phone)")
    
    # Issue counts
    total_issues = models.IntegerField(default=0)
    critical_issues = models.IntegerField(default=0)
    warnings = models.IntegerField(default=0)
    
    # Details
    issues = models.JSONField(default=list, help_text="List of quality issues")
    field_scores = models.JSONField(default=dict, help_text="Per-field quality scores")
    
    calculated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'data_quality_scores'
    
    def __str__(self):
        return f"Quality score {self.overall_score} for submission {self.submission.id}"


class DuplicateDetection(models.Model):
    """Duplicate submission detection results"""
    DUPLICATE_STATUS = [
        ('potential', 'Potential Duplicate'),
        ('confirmed', 'Confirmed Duplicate'),
        ('not_duplicate', 'Not a Duplicate'),
        ('merged', 'Merged'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='duplicate_detections')
    
    # The submissions being compared
    submission_a = models.ForeignKey(
        'forms.Submission',
        on_delete=models.CASCADE,
        related_name='duplicate_checks_a'
    )
    submission_b = models.ForeignKey(
        'forms.Submission',
        on_delete=models.CASCADE,
        related_name='duplicate_checks_b'
    )
    
    # Similarity analysis
    similarity_score = models.FloatField(help_text="0-100 similarity percentage")
    matching_fields = models.JSONField(default=list, help_text="Fields that match")
    differing_fields = models.JSONField(default=list, help_text="Fields that differ")
    
    # Status
    status = models.CharField(max_length=20, choices=DUPLICATE_STATUS, default='potential')
    
    # Resolution
    resolved_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_duplicates'
    )
    resolution_notes = models.TextField(blank=True)
    merged_into = models.ForeignKey(
        'forms.Submission',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='merged_submissions'
    )
    
    detected_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'duplicate_detections'
        unique_together = [['submission_a', 'submission_b']]
        ordering = ['-similarity_score']
    
    def __str__(self):
        return f"Duplicate check: {self.similarity_score}% match"


class ExternalValidation(models.Model):
    """External API validation results (email, phone, address)"""
    VALIDATION_TYPES = [
        ('email', 'Email Verification'),
        ('phone', 'Phone Verification'),
        ('address', 'Address Validation'),
        ('company', 'Company Verification'),
        ('domain', 'Domain Verification'),
        ('custom', 'Custom API Validation'),
    ]
    
    VALIDATION_STATUS = [
        ('pending', 'Pending'),
        ('valid', 'Valid'),
        ('invalid', 'Invalid'),
        ('risky', 'Risky'),
        ('unknown', 'Unknown'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(
        'forms.Submission',
        on_delete=models.CASCADE,
        related_name='external_validations'
    )
    field_id = models.CharField(max_length=100)
    field_value = models.TextField()
    
    validation_type = models.CharField(max_length=50, choices=VALIDATION_TYPES)
    status = models.CharField(max_length=20, choices=VALIDATION_STATUS, default='pending')
    
    # Validation results
    is_valid = models.BooleanField(null=True)
    confidence_score = models.FloatField(null=True, help_text="0-100 confidence")
    
    # Detailed results
    validation_result = models.JSONField(default=dict)
    corrected_value = models.TextField(blank=True, help_text="Suggested correction")
    
    # Provider info
    provider = models.CharField(max_length=50, blank=True)
    api_response = models.JSONField(default=dict)
    
    validated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'external_validations'
        indexes = [
            models.Index(fields=['submission', 'field_id']),
        ]
    
    def __str__(self):
        return f"{self.validation_type} validation for {self.field_value[:20]}..."


class DataCleansingRule(models.Model):
    """Rules for data standardization and cleansing"""
    RULE_TYPES = [
        ('trim', 'Trim Whitespace'),
        ('lowercase', 'Lowercase'),
        ('uppercase', 'Uppercase'),
        ('titlecase', 'Title Case'),
        ('phone_format', 'Phone Format'),
        ('date_format', 'Date Format'),
        ('address_standardize', 'Address Standardization'),
        ('remove_special', 'Remove Special Characters'),
        ('regex_replace', 'Regex Replace'),
        ('custom', 'Custom Transform'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='cleansing_rules')
    
    name = models.CharField(max_length=255)
    rule_type = models.CharField(max_length=50, choices=RULE_TYPES)
    
    # Target fields
    target_field_ids = models.JSONField(default=list, help_text="Field IDs to apply rule to")
    apply_to_all = models.BooleanField(default=False, help_text="Apply to all text fields")
    
    # Rule configuration
    config = models.JSONField(
        default=dict,
        help_text="Rule-specific configuration (regex pattern, date format, etc.)"
    )
    
    # Execution settings
    apply_on_submit = models.BooleanField(default=True)
    apply_on_export = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    order = models.IntegerField(default=0, help_text="Order of rule execution")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'data_cleansing_rules'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.name} - {self.rule_type}"


class DataCleansingLog(models.Model):
    """Log of data cleansing operations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(
        'forms.Submission',
        on_delete=models.CASCADE,
        related_name='cleansing_logs'
    )
    rule = models.ForeignKey(DataCleansingRule, on_delete=models.SET_NULL, null=True)
    
    field_id = models.CharField(max_length=100)
    original_value = models.TextField()
    cleansed_value = models.TextField()
    
    applied_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'data_cleansing_logs'
        ordering = ['-applied_at']


class ValidationRule(models.Model):
    """Custom validation rules for forms"""
    RULE_TYPES = [
        ('required', 'Required'),
        ('email', 'Email Format'),
        ('phone', 'Phone Format'),
        ('url', 'URL Format'),
        ('regex', 'Regular Expression'),
        ('min_length', 'Minimum Length'),
        ('max_length', 'Maximum Length'),
        ('min_value', 'Minimum Value'),
        ('max_value', 'Maximum Value'),
        ('date_range', 'Date Range'),
        ('file_type', 'File Type'),
        ('file_size', 'File Size'),
        ('unique', 'Unique Value'),
        ('custom_api', 'Custom API Validation'),
        ('dependent', 'Dependent Field'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='validation_rules')
    
    name = models.CharField(max_length=255)
    rule_type = models.CharField(max_length=50, choices=RULE_TYPES)
    field_id = models.CharField(max_length=100)
    
    # Rule configuration
    config = models.JSONField(default=dict)
    error_message = models.CharField(max_length=500)
    
    # Validation timing
    validate_on_blur = models.BooleanField(default=True)
    validate_on_submit = models.BooleanField(default=True)
    validate_realtime = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'validation_rules'
        ordering = ['field_id', 'rule_type']
    
    def __str__(self):
        return f"{self.name} - {self.rule_type}"


class ExportWithQuality(models.Model):
    """Export jobs with data quality scores"""
    EXPORT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    EXPORT_FORMATS = [
        ('csv', 'CSV'),
        ('xlsx', 'Excel'),
        ('json', 'JSON'),
        ('pdf', 'PDF'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='quality_exports')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    
    # Export configuration
    format = models.CharField(max_length=10, choices=EXPORT_FORMATS, default='csv')
    include_quality_scores = models.BooleanField(default=True)
    include_validation_results = models.BooleanField(default=True)
    
    # Filters
    min_quality_score = models.FloatField(default=0)
    date_from = models.DateTimeField(null=True, blank=True)
    date_to = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=EXPORT_STATUS, default='pending')
    
    # Results
    total_records = models.IntegerField(default=0)
    exported_records = models.IntegerField(default=0)
    excluded_records = models.IntegerField(default=0, help_text="Failed quality threshold")
    
    file_url = models.URLField(blank=True)
    file_size = models.IntegerField(default=0, help_text="Size in bytes")
    
    # Quality summary
    avg_quality_score = models.FloatField(default=0)
    quality_distribution = models.JSONField(default=dict)
    
    error_message = models.TextField(blank=True)
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'export_with_quality'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Export {self.id} for {self.form.title}"
