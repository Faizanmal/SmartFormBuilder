"""
Serializers for Advanced Features:
- Performance Optimization Dashboard
- Advanced Analytics & User Behavior
- Enhanced Accessibility & Compliance
- Mobile-First Improvements
- Real-Time Collaboration
- AI-Powered Optimization
- Advanced Data Quality
- Offline Form Building & Sync
- Smart Form Recovery & Auto-Save
- Integration Marketplace
"""
from rest_framework import serializers
from django.utils import timezone


# ============================================================
# 1. PERFORMANCE OPTIMIZATION DASHBOARD
# ============================================================

class PerformanceMetricSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id')
    metric_type = serializers.CharField()
    value = serializers.FloatField()
    device_type = serializers.CharField()
    connection_type = serializers.CharField()
    browser = serializers.CharField()
    os = serializers.CharField()
    country = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        fields = '__all__'


class FieldCompletionMetricSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id')
    field_id = serializers.CharField()
    field_label = serializers.CharField()
    field_type = serializers.CharField()
    avg_completion_time = serializers.FloatField()
    min_completion_time = serializers.FloatField()
    max_completion_time = serializers.FloatField()
    p50_completion_time = serializers.FloatField()
    p95_completion_time = serializers.FloatField()
    total_interactions = serializers.IntegerField()
    total_completions = serializers.IntegerField()
    drop_off_count = serializers.IntegerField()
    error_count = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    date = serializers.DateField()


class FormCacheConfigSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id')
    cache_strategy = serializers.CharField()
    cache_ttl = serializers.IntegerField()
    auto_invalidation = serializers.BooleanField()
    invalidation_events = serializers.ListField()
    lazy_loading_enabled = serializers.BooleanField()
    lazy_loading_threshold = serializers.IntegerField()
    preload_enabled = serializers.BooleanField()
    cache_hit_count = serializers.IntegerField(read_only=True)
    cache_miss_count = serializers.IntegerField(read_only=True)
    last_invalidated_at = serializers.DateTimeField(read_only=True)


class PerformanceAlertSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id')
    alert_type = serializers.CharField()
    severity = serializers.CharField()
    message = serializers.CharField()
    metric_value = serializers.FloatField()
    threshold_value = serializers.FloatField()
    acknowledged = serializers.BooleanField()
    acknowledged_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField(read_only=True)


class AssetOptimizationSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id')
    asset_type = serializers.CharField()
    original_size = serializers.IntegerField()
    optimized_size = serializers.IntegerField()
    compression_ratio = serializers.FloatField()
    optimization_method = serializers.CharField()
    original_url = serializers.URLField()
    optimized_url = serializers.URLField()
    created_at = serializers.DateTimeField(read_only=True)


# ============================================================
# 2. ADVANCED ANALYTICS & USER BEHAVIOR
# ============================================================

class SessionRecordingSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id')
    session_id = serializers.CharField()
    device_type = serializers.CharField()
    browser = serializers.CharField()
    os = serializers.CharField()
    screen_width = serializers.IntegerField()
    screen_height = serializers.IntegerField()
    country = serializers.CharField()
    status = serializers.CharField()
    events_count = serializers.IntegerField()
    duration_seconds = serializers.IntegerField()
    completed_form = serializers.BooleanField()
    drop_off_field = serializers.CharField()
    rage_clicks_count = serializers.IntegerField()
    u_turns_count = serializers.IntegerField()
    started_at = serializers.DateTimeField()
    ended_at = serializers.DateTimeField()


class DropOffAnalysisSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id')
    field_id = serializers.CharField()
    field_label = serializers.CharField()
    drop_off_count = serializers.IntegerField()
    drop_off_rate = serializers.FloatField()
    avg_time_before_drop = serializers.FloatField()
    common_reasons = serializers.ListField()
    date = serializers.DateField()


class ABTestResultSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    test = serializers.UUIDField(source='test_id')
    form = serializers.UUIDField(source='form_id')
    variant_name = serializers.CharField()
    visitors = serializers.IntegerField()
    conversions = serializers.IntegerField()
    conversion_rate = serializers.FloatField()
    improvement = serializers.FloatField()
    confidence_level = serializers.FloatField()
    is_winner = serializers.BooleanField()
    p_value = serializers.FloatField()
    calculated_at = serializers.DateTimeField()


class BehaviorInsightSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id')
    insight_type = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    severity = serializers.CharField()
    affected_fields = serializers.ListField()
    recommendation = serializers.CharField()
    potential_impact = serializers.CharField()
    is_resolved = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class FormFunnelSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id')
    name = serializers.CharField()
    steps = serializers.ListField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()


# ============================================================
# 3. ENHANCED ACCESSIBILITY & COMPLIANCE
# ============================================================

class AccessibilityConfigSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id')
    target_wcag_level = serializers.CharField()
    screen_reader_optimized = serializers.BooleanField()
    keyboard_nav_enabled = serializers.BooleanField()
    high_contrast_mode = serializers.BooleanField()
    font_scaling_enabled = serializers.BooleanField()
    min_font_size = serializers.IntegerField()
    focus_indicators = serializers.BooleanField()
    skip_links_enabled = serializers.BooleanField()
    aria_live_regions = serializers.BooleanField()
    error_announcements = serializers.BooleanField()


class AccessibilityAuditSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id')
    status = serializers.CharField()
    wcag_level_tested = serializers.CharField()
    issues_count = serializers.IntegerField()
    warnings_count = serializers.IntegerField()
    passed_count = serializers.IntegerField()
    score = serializers.FloatField()
    started_at = serializers.DateTimeField()
    completed_at = serializers.DateTimeField()


class AccessibilityIssueSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    audit = serializers.UUIDField(source='audit_id')
    issue_type = serializers.CharField()
    severity = serializers.CharField()
    wcag_criterion = serializers.CharField()
    field_id = serializers.CharField()
    element_selector = serializers.CharField()
    description = serializers.CharField()
    recommendation = serializers.CharField()
    auto_fix_available = serializers.BooleanField()
    status = serializers.CharField()
    fixed_at = serializers.DateTimeField()


class UserAccessibilityPreferenceSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    user = serializers.UUIDField(source='user_id')
    high_contrast = serializers.BooleanField()
    large_text = serializers.BooleanField()
    reduced_motion = serializers.BooleanField()
    screen_reader_mode = serializers.BooleanField()
    font_size_multiplier = serializers.FloatField()
    color_blind_mode = serializers.CharField()
    keyboard_only = serializers.BooleanField()


class ComplianceReportSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id')
    standards_tested = serializers.ListField()
    overall_compliance = serializers.FloatField()
    detailed_results = serializers.DictField()
    recommendations = serializers.ListField()
    generated_at = serializers.DateTimeField()
    valid_until = serializers.DateTimeField()
    report_url = serializers.URLField()


# ============================================================
# 4-5. MOBILE & COLLABORATION
# ============================================================

class FormChangeSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id')
    user = serializers.UUIDField(source='user_id')
    change_type = serializers.CharField()
    field_id = serializers.CharField()
    previous_value = serializers.JSONField()
    new_value = serializers.JSONField()
    change_path = serializers.CharField()
    created_at = serializers.DateTimeField()


class FormCommentSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id')
    user = serializers.UUIDField(source='user_id')
    user_email = serializers.CharField(source='user.email', read_only=True)
    parent = serializers.UUIDField(source='parent_id', allow_null=True)
    comment_type = serializers.CharField()
    field_id = serializers.CharField()
    content = serializers.CharField()
    position_x = serializers.FloatField()
    position_y = serializers.FloatField()
    is_resolved = serializers.BooleanField()
    resolved_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()


# ============================================================
# 6. AI-POWERED OPTIMIZATION
# ============================================================

class SmartDefaultSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id')
    field_id = serializers.CharField()
    default_type = serializers.CharField()
    default_value = serializers.JSONField()
    source = serializers.CharField()
    confidence = serializers.FloatField()
    usage_count = serializers.IntegerField()
    is_active = serializers.BooleanField()


class CompletionPredictionSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id')
    session_id = serializers.CharField()
    predicted_completion_probability = serializers.FloatField()
    predicted_drop_off_field = serializers.CharField()
    risk_factors = serializers.ListField()
    recommended_interventions = serializers.ListField()
    actual_outcome = serializers.CharField()
    created_at = serializers.DateTimeField()


class ProgressiveDisclosureSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id')
    disclosure_rules = serializers.ListField()
    field_visibility_order = serializers.ListField()
    adaptive_enabled = serializers.BooleanField()
    min_visible_fields = serializers.IntegerField()
    max_visible_fields = serializers.IntegerField()


# ============================================================
# 7. ADVANCED DATA QUALITY
# ============================================================

class DataQualityRuleSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id')
    field_id = serializers.CharField()
    rule_type = serializers.CharField()
    rule_config = serializers.DictField()
    severity = serializers.CharField()
    error_message = serializers.CharField()
    is_active = serializers.BooleanField()


class SubmissionQualityScoreSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    submission = serializers.UUIDField(source='submission_id')
    overall_score = serializers.FloatField()
    completeness_score = serializers.FloatField()
    accuracy_score = serializers.FloatField()
    consistency_score = serializers.FloatField()
    field_scores = serializers.DictField()
    issues_found = serializers.ListField()
    calculated_at = serializers.DateTimeField()


class DuplicateSubmissionSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    original = serializers.UUIDField(source='original_id')
    duplicate = serializers.UUIDField(source='duplicate_id')
    similarity_score = serializers.FloatField()
    matching_fields = serializers.ListField()
    status = serializers.CharField()
    resolution = serializers.CharField()
    detected_at = serializers.DateTimeField()


class ExternalValidationSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    submission = serializers.UUIDField(source='submission_id')
    field_id = serializers.CharField()
    validation_type = serializers.CharField()
    original_value = serializers.CharField()
    is_valid = serializers.BooleanField()
    validation_result = serializers.DictField()
    provider = serializers.CharField()
    validated_at = serializers.DateTimeField()


class DataCleansingRuleSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id')
    field_id = serializers.CharField()
    cleansing_type = serializers.CharField()
    cleansing_config = serializers.DictField()
    is_active = serializers.BooleanField()
    applied_count = serializers.IntegerField()


# ============================================================
# 8-9. OFFLINE & AUTO-SAVE
# ============================================================

class FormBuilderAutoSaveSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id', allow_null=True)
    temp_id = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    schema_json = serializers.DictField()
    settings_json = serializers.DictField()
    editor_state = serializers.DictField()
    is_recovered = serializers.BooleanField()
    last_saved_at = serializers.DateTimeField()


class FormBuilderCrashRecoverySerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id', allow_null=True)
    autosave = serializers.UUIDField(source='autosave_id')
    status = serializers.CharField()
    crash_reason = serializers.CharField()
    created_at = serializers.DateTimeField()
    recovered_at = serializers.DateTimeField()


class FormDraftScheduleSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id')
    draft_schema = serializers.DictField()
    draft_settings = serializers.DictField()
    scheduled_at = serializers.DateTimeField()
    status = serializers.CharField()
    created_by = serializers.UUIDField(source='created_by_id')
    created_at = serializers.DateTimeField()


class SubmissionAutoSaveSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    form = serializers.UUIDField(source='form_id')
    session_id = serializers.CharField()
    resume_token = serializers.CharField(read_only=True)
    data_json = serializers.DictField()
    current_step = serializers.IntegerField()
    completed_fields = serializers.ListField()
    expires_at = serializers.DateTimeField()
    last_saved_at = serializers.DateTimeField()


# ============================================================
# 10. INTEGRATION MARKETPLACE
# ============================================================

class UserIntegrationTemplateSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    creator = serializers.UUIDField(source='creator_id', read_only=True)
    name = serializers.CharField()
    description = serializers.CharField()
    template_type = serializers.CharField()
    api_config = serializers.DictField()
    request_template = serializers.DictField()
    response_mapping = serializers.DictField()
    is_public = serializers.BooleanField()
    install_count = serializers.IntegerField(read_only=True)
    rating = serializers.FloatField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class IntegrationExecutionSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    workflow = serializers.UUIDField(source='workflow_id')
    trigger_event = serializers.CharField()
    trigger_data = serializers.DictField()
    status = serializers.CharField()
    actions_completed = serializers.IntegerField()
    actions_total = serializers.IntegerField()
    error_message = serializers.CharField()
    execution_log = serializers.ListField()
    started_at = serializers.DateTimeField()
    completed_at = serializers.DateTimeField()
    duration_ms = serializers.IntegerField()
