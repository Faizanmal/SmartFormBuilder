"""
URL configuration for Advanced Features:
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
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views_features import (
    # Performance
    PerformanceMetricViewSet, PerformanceDashboardView,
    FieldCompletionMetricViewSet, FormCacheConfigViewSet,
    PerformanceAlertViewSet, AssetOptimizationViewSet,
    LazyLoadingConfigView,
    
    # Analytics
    HeatmapViewSet, SessionRecordingViewSet, DropOffAnalysisViewSet,
    ABTestResultViewSet, BehaviorInsightViewSet, FormFunnelViewSet,
    
    # Accessibility
    AccessibilityConfigViewSet, AccessibilityAuditViewSet,
    AccessibilityIssueViewSet, UserAccessibilityPreferenceViewSet,
    ComplianceReportViewSet,
    
    # Mobile
    VoiceInputView, GeolocationCaptureView, CameraUploadView,
    SwipeGestureConfigView,
    
    # Collaboration
    LiveEditingView, FormVersionHistoryViewSet, FormCommentEnhancedViewSet,
    
    # AI Optimization
    AIOptimizationViewSet, SmartDefaultViewSet,
    CompletionPredictionViewSet, ProgressiveDisclosureViewSet,
    
    # Data Quality
    DataQualityRuleViewSet, SubmissionQualityScoreViewSet,
    DuplicateSubmissionViewSet, ExternalValidationViewSet,
    DataCleansingRuleViewSet, ExportWithQualityView,
    
    # Offline & Sync
    OfflineSyncView, ConflictResolutionView, OfflineAnalyticsView,
    
    # Auto-Save & Recovery
    AutoSaveViewSet, CrashRecoveryViewSet, DraftScheduleViewSet,
    SubmissionAutoSaveViewSet,
    
    # Integration Marketplace
    UserIntegrationTemplateViewSet, APIConnectorBuilderView,
    IntegrationExecutionViewSet,
)

router = DefaultRouter()

# Performance routes
router.register(r'performance/metrics', PerformanceMetricViewSet, basename='performance-metric')
router.register(r'performance/field-metrics', FieldCompletionMetricViewSet, basename='field-metric')
router.register(r'performance/cache-config', FormCacheConfigViewSet, basename='cache-config')
router.register(r'performance/alerts', PerformanceAlertViewSet, basename='performance-alert')
router.register(r'performance/assets', AssetOptimizationViewSet, basename='asset-optimization')

# Analytics routes
router.register(r'analytics/heatmaps', HeatmapViewSet, basename='heatmap')
router.register(r'analytics/recordings', SessionRecordingViewSet, basename='session-recording')
router.register(r'analytics/drop-off', DropOffAnalysisViewSet, basename='drop-off')
router.register(r'analytics/ab-results', ABTestResultViewSet, basename='ab-result')
router.register(r'analytics/insights', BehaviorInsightViewSet, basename='behavior-insight')
router.register(r'analytics/funnels', FormFunnelViewSet, basename='form-funnel')

# Accessibility routes
router.register(r'accessibility/config', AccessibilityConfigViewSet, basename='accessibility-config')
router.register(r'accessibility/audits', AccessibilityAuditViewSet, basename='accessibility-audit')
router.register(r'accessibility/issues', AccessibilityIssueViewSet, basename='accessibility-issue')
router.register(r'accessibility/preferences', UserAccessibilityPreferenceViewSet, basename='accessibility-preference')
router.register(r'accessibility/compliance', ComplianceReportViewSet, basename='compliance-report')

# Collaboration routes
router.register(r'collaboration/comments', FormCommentEnhancedViewSet, basename='form-comment')

# AI Optimization routes
router.register(r'ai/optimization', AIOptimizationViewSet, basename='ai-optimization')
router.register(r'ai/smart-defaults', SmartDefaultViewSet, basename='smart-default')
router.register(r'ai/predictions', CompletionPredictionViewSet, basename='completion-prediction')
router.register(r'ai/progressive-disclosure', ProgressiveDisclosureViewSet, basename='progressive-disclosure')

# Data Quality routes
router.register(r'quality/rules', DataQualityRuleViewSet, basename='quality-rule')
router.register(r'quality/scores', SubmissionQualityScoreViewSet, basename='quality-score')
router.register(r'quality/duplicates', DuplicateSubmissionViewSet, basename='duplicate-submission')
router.register(r'quality/validations', ExternalValidationViewSet, basename='external-validation')
router.register(r'quality/cleansing', DataCleansingRuleViewSet, basename='cleansing-rule')

# Auto-Save & Recovery routes
router.register(r'autosave/builder', AutoSaveViewSet, basename='builder-autosave')
router.register(r'autosave/recovery', CrashRecoveryViewSet, basename='crash-recovery')
router.register(r'autosave/schedules', DraftScheduleViewSet, basename='draft-schedule')
router.register(r'autosave/submissions', SubmissionAutoSaveViewSet, basename='submission-autosave')

# Integration Marketplace routes
router.register(r'marketplace/user-templates', UserIntegrationTemplateViewSet, basename='user-template')
router.register(r'marketplace/executions', IntegrationExecutionViewSet, basename='integration-execution')

urlpatterns = [
    path('', include(router.urls)),
    
    # Performance endpoints
    path('performance/dashboard/<uuid:form_id>/', PerformanceDashboardView.as_view(), name='performance-dashboard'),
    path('performance/lazy-loading/<uuid:form_id>/', LazyLoadingConfigView.as_view(), name='lazy-loading-config'),
    
    # Mobile endpoints
    path('mobile/voice-input/', VoiceInputView.as_view(), name='voice-input'),
    path('mobile/geolocation/', GeolocationCaptureView.as_view(), name='geolocation-capture'),
    path('mobile/camera-upload/', CameraUploadView.as_view(), name='camera-upload'),
    path('mobile/swipe-config/<uuid:form_id>/', SwipeGestureConfigView.as_view(), name='swipe-config'),
    
    # Collaboration endpoints
    path('collaboration/live/<uuid:form_id>/', LiveEditingView.as_view(), name='live-editing'),
    path('collaboration/history/<uuid:form_id>/', FormVersionHistoryViewSet.as_view({
        'get': 'list'
    }), name='version-history'),
    path('collaboration/history/<uuid:form_id>/diff/', FormVersionHistoryViewSet.as_view({
        'get': 'diff'
    }), name='version-diff'),
    
    # Data Quality endpoints
    path('quality/export/', ExportWithQualityView.as_view(), name='export-with-quality'),
    
    # Offline & Sync endpoints
    path('offline/sync/', OfflineSyncView.as_view(), name='offline-sync'),
    path('offline/conflicts/', ConflictResolutionView.as_view(), name='conflict-resolution'),
    path('offline/analytics/', OfflineAnalyticsView.as_view(), name='offline-analytics'),
    
    # Integration Marketplace endpoints
    path('marketplace/connector-builder/', APIConnectorBuilderView.as_view(), name='connector-builder'),
]
