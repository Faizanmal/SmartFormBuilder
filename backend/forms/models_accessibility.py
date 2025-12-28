"""
Accessibility and compliance models
"""
from django.db import models
import uuid


class AccessibilityConfig(models.Model):
    """Accessibility configuration for forms"""
    WCAG_LEVELS = [
        ('A', 'WCAG 2.1 Level A'),
        ('AA', 'WCAG 2.1 Level AA'),
        ('AAA', 'WCAG 2.1 Level AAA'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField('forms.Form', on_delete=models.CASCADE, related_name='accessibility_config')
    
    # WCAG Compliance
    target_wcag_level = models.CharField(max_length=10, choices=WCAG_LEVELS, default='AA')
    is_compliant = models.BooleanField(default=False)
    last_audit_at = models.DateTimeField(null=True, blank=True)
    
    # Screen reader optimizations
    screen_reader_optimized = models.BooleanField(default=True)
    aria_labels_enabled = models.BooleanField(default=True)
    aria_live_regions = models.BooleanField(default=True)
    skip_links_enabled = models.BooleanField(default=True)
    
    # Keyboard navigation
    keyboard_nav_enabled = models.BooleanField(default=True)
    focus_visible_enabled = models.BooleanField(default=True)
    tab_order_custom = models.JSONField(default=list, blank=True)
    
    # Visual options
    high_contrast_available = models.BooleanField(default=True)
    font_scaling_enabled = models.BooleanField(default=True)
    min_font_size = models.IntegerField(default=16)
    max_font_size = models.IntegerField(default=32)
    
    # Motion preferences
    reduced_motion_support = models.BooleanField(default=True)
    auto_play_disabled = models.BooleanField(default=True)
    
    # Color settings
    color_blind_friendly = models.BooleanField(default=True)
    minimum_contrast_ratio = models.FloatField(default=4.5)
    
    # Error handling
    error_suggestions_enabled = models.BooleanField(default=True)
    inline_error_messages = models.BooleanField(default=True)
    error_summary_enabled = models.BooleanField(default=True)
    
    # Time limits
    session_timeout_warning = models.BooleanField(default=True)
    timeout_extension_enabled = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accessibility_configs'
    
    def __str__(self):
        return f"Accessibility config for {self.form.title}"


class AccessibilityAudit(models.Model):
    """Automated accessibility audit results"""
    AUDIT_STATUS = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='accessibility_audits')
    
    status = models.CharField(max_length=20, choices=AUDIT_STATUS, default='pending')
    wcag_level_tested = models.CharField(max_length=10, default='AA')
    
    # Audit scores
    overall_score = models.FloatField(default=0, help_text="0-100 score")
    perceivable_score = models.FloatField(default=0)
    operable_score = models.FloatField(default=0)
    understandable_score = models.FloatField(default=0)
    robust_score = models.FloatField(default=0)
    
    # Issue counts
    total_issues = models.IntegerField(default=0)
    critical_issues = models.IntegerField(default=0)
    serious_issues = models.IntegerField(default=0)
    moderate_issues = models.IntegerField(default=0)
    minor_issues = models.IntegerField(default=0)
    
    # Detailed results
    issues = models.JSONField(default=list, help_text="List of accessibility issues")
    passed_checks = models.JSONField(default=list)
    warnings = models.JSONField(default=list)
    
    # Manual review items
    manual_review_needed = models.JSONField(
        default=list,
        help_text="Items requiring manual accessibility review"
    )
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'accessibility_audits'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Audit for {self.form.title} - Score: {self.overall_score}"


class AccessibilityIssue(models.Model):
    """Individual accessibility issues found during audit"""
    IMPACT_LEVELS = [
        ('critical', 'Critical'),
        ('serious', 'Serious'),
        ('moderate', 'Moderate'),
        ('minor', 'Minor'),
    ]
    
    WCAG_PRINCIPLES = [
        ('perceivable', 'Perceivable'),
        ('operable', 'Operable'),
        ('understandable', 'Understandable'),
        ('robust', 'Robust'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    audit = models.ForeignKey(AccessibilityAudit, on_delete=models.CASCADE, related_name='audit_issues')
    
    rule_id = models.CharField(max_length=100)
    wcag_criteria = models.CharField(max_length=50, help_text="e.g., 1.1.1, 2.4.7")
    wcag_principle = models.CharField(max_length=20, choices=WCAG_PRINCIPLES)
    impact = models.CharField(max_length=20, choices=IMPACT_LEVELS)
    
    description = models.TextField()
    help_text = models.TextField(blank=True)
    help_url = models.URLField(blank=True)
    
    # Element details
    affected_element = models.CharField(max_length=500, blank=True)
    field_id = models.CharField(max_length=100, blank=True)
    html_snippet = models.TextField(blank=True)
    
    # Fix information
    fix_suggestion = models.TextField(blank=True)
    auto_fixable = models.BooleanField(default=False)
    
    is_fixed = models.BooleanField(default=False)
    fixed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'accessibility_issues'
        ordering = ['impact', '-created_at']
    
    def __str__(self):
        return f"{self.impact}: {self.rule_id} - {self.wcag_criteria}"


class UserAccessibilityPreference(models.Model):
    """User's accessibility preferences"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='accessibility_preferences',
        null=True,
        blank=True
    )
    # For anonymous users
    session_id = models.CharField(max_length=100, blank=True, db_index=True)
    
    # Visual preferences
    high_contrast_mode = models.BooleanField(default=False)
    dark_mode = models.BooleanField(default=False)
    font_size_scale = models.FloatField(default=1.0, help_text="1.0 = 100%, 1.5 = 150%")
    font_family = models.CharField(max_length=50, default='system', blank=True)
    line_height_scale = models.FloatField(default=1.5)
    letter_spacing = models.FloatField(default=0)
    
    # Motion preferences
    reduced_motion = models.BooleanField(default=False)
    no_animations = models.BooleanField(default=False)
    
    # Audio preferences
    screen_reader_hints = models.BooleanField(default=True)
    audio_descriptions = models.BooleanField(default=False)
    
    # Interaction preferences
    keyboard_only = models.BooleanField(default=False)
    extended_time = models.BooleanField(default=False)
    
    # Color preferences
    color_blind_mode = models.CharField(
        max_length=20,
        choices=[
            ('none', 'None'),
            ('protanopia', 'Protanopia'),
            ('deuteranopia', 'Deuteranopia'),
            ('tritanopia', 'Tritanopia'),
        ],
        default='none'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_accessibility_preferences'
    
    def __str__(self):
        if self.user:
            return f"Preferences for {self.user.email}"
        return f"Preferences for session {self.session_id[:8]}..."


class ComplianceReport(models.Model):
    """Compliance reports for forms (GDPR, ADA, HIPAA, etc.)"""
    COMPLIANCE_TYPES = [
        ('wcag', 'WCAG 2.1'),
        ('ada', 'ADA'),
        ('section508', 'Section 508'),
        ('en301549', 'EN 301 549'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey('forms.Form', on_delete=models.CASCADE, related_name='compliance_reports')
    compliance_type = models.CharField(max_length=50, choices=COMPLIANCE_TYPES)
    
    # Report details
    is_compliant = models.BooleanField(default=False)
    compliance_score = models.FloatField(default=0)
    
    # Requirements checklist
    requirements_checked = models.JSONField(default=list)
    requirements_met = models.JSONField(default=list)
    requirements_failed = models.JSONField(default=list)
    requirements_na = models.JSONField(default=list, help_text="Not applicable")
    
    # Documentation
    report_pdf_url = models.URLField(blank=True)
    certification_number = models.CharField(max_length=100, blank=True)
    
    valid_until = models.DateField(null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'compliance_reports'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.compliance_type} report for {self.form.title}"
