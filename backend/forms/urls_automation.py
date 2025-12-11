"""
URL configuration for automation features
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views_automation import (
    FormOptimizationViewSet,
    WorkflowViewSet,
    PersonalizationViewSet,
    ComplianceViewSet,
    VoiceDesignViewSet,
    PredictiveAnalyticsViewSet,
    AlertViewSet,
    IntegrationMarketplaceViewSet,
    AIContentViewSet,
)

router = DefaultRouter()
router.register(r'workflows', WorkflowViewSet, basename='workflow')
router.register(r'personalization', PersonalizationViewSet, basename='personalization')
router.register(r'alerts', AlertViewSet, basename='alert')
router.register(r'integrations', IntegrationMarketplaceViewSet, basename='integration')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Form Optimization
    path(
        'forms/<uuid:pk>/optimization/analyze/',
        FormOptimizationViewSet.as_view({'get': 'analyze'}),
        name='form-optimization-analyze'
    ),
    path(
        'forms/<uuid:pk>/optimization/suggestions/',
        FormOptimizationViewSet.as_view({'get': 'suggestions'}),
        name='form-optimization-suggestions'
    ),
    path(
        'forms/<uuid:pk>/optimization/generate-suggestions/',
        FormOptimizationViewSet.as_view({'post': 'generate_suggestions'}),
        name='form-optimization-generate'
    ),
    path(
        'forms/<uuid:pk>/optimization/apply/<uuid:suggestion_id>/',
        FormOptimizationViewSet.as_view({'post': 'apply_suggestion'}),
        name='form-optimization-apply'
    ),
    path(
        'forms/<uuid:pk>/optimization/auto-optimize/',
        FormOptimizationViewSet.as_view({'post': 'auto_optimize'}),
        name='form-optimization-auto'
    ),
    path(
        'forms/<uuid:pk>/optimization/dismiss/<uuid:suggestion_id>/',
        FormOptimizationViewSet.as_view({'post': 'dismiss_suggestion'}),
        name='form-optimization-dismiss'
    ),
    
    # Compliance
    path(
        'forms/<uuid:pk>/compliance/scan/',
        ComplianceViewSet.as_view({'post': 'scan'}),
        name='compliance-scan'
    ),
    path(
        'forms/<uuid:pk>/compliance/auto-fix/',
        ComplianceViewSet.as_view({'post': 'auto_fix'}),
        name='compliance-auto-fix'
    ),
    path(
        'forms/<uuid:pk>/compliance/history/',
        ComplianceViewSet.as_view({'get': 'history'}),
        name='compliance-history'
    ),
    path(
        'forms/<uuid:pk>/compliance/privacy-policy/',
        ComplianceViewSet.as_view({'post': 'generate_privacy_policy'}),
        name='compliance-privacy-policy'
    ),
    
    # Voice Design
    path(
        'voice/start-session/',
        VoiceDesignViewSet.as_view({'post': 'start_session'}),
        name='voice-start-session'
    ),
    path(
        'voice/process-audio/',
        VoiceDesignViewSet.as_view({'post': 'process_audio'}),
        name='voice-process-audio'
    ),
    path(
        'voice/process-text/',
        VoiceDesignViewSet.as_view({'post': 'process_text'}),
        name='voice-process-text'
    ),
    path(
        'voice/end-session/',
        VoiceDesignViewSet.as_view({'post': 'end_session'}),
        name='voice-end-session'
    ),
    path(
        'voice/session-history/',
        VoiceDesignViewSet.as_view({'get': 'session_history'}),
        name='voice-session-history'
    ),
    
    # Predictive Analytics
    path(
        'forms/<uuid:pk>/analytics/forecast/',
        PredictiveAnalyticsViewSet.as_view({'get': 'forecast'}),
        name='analytics-forecast'
    ),
    path(
        'forms/<uuid:pk>/analytics/anomalies/',
        PredictiveAnalyticsViewSet.as_view({'get': 'anomalies'}),
        name='analytics-anomalies'
    ),
    path(
        'forms/<uuid:pk>/analytics/insights/',
        PredictiveAnalyticsViewSet.as_view({'get': 'insights'}),
        name='analytics-insights'
    ),
    path(
        'forms/<uuid:pk>/analytics/trends/',
        PredictiveAnalyticsViewSet.as_view({'get': 'trends'}),
        name='analytics-trends'
    ),
    
    # Integration Marketplace
    path(
        'integrations/catalog/',
        IntegrationMarketplaceViewSet.as_view({'get': 'catalog'}),
        name='integration-catalog'
    ),
    path(
        'integrations/categories/',
        IntegrationMarketplaceViewSet.as_view({'get': 'categories'}),
        name='integration-categories'
    ),
    path(
        'integrations/<uuid:pk>/connect/',
        IntegrationMarketplaceViewSet.as_view({'post': 'connect'}),
        name='integration-connect'
    ),
    path(
        'integrations/<uuid:pk>/sync/',
        IntegrationMarketplaceViewSet.as_view({'post': 'sync'}),
        name='integration-sync'
    ),
    path(
        'integrations/<uuid:pk>/suggest-mapping/',
        IntegrationMarketplaceViewSet.as_view({'get': 'suggest_mapping'}),
        name='integration-suggest-mapping'
    ),
    path(
        'integrations/<uuid:pk>/oauth-callback/',
        IntegrationMarketplaceViewSet.as_view({'post': 'oauth_callback'}),
        name='integration-oauth-callback'
    ),
    
    # AI Content Generation
    path(
        'forms/<uuid:pk>/content/description/',
        AIContentViewSet.as_view({'post': 'generate_description'}),
        name='content-description'
    ),
    path(
        'forms/<uuid:pk>/content/thank-you/',
        AIContentViewSet.as_view({'post': 'generate_thank_you'}),
        name='content-thank-you'
    ),
    path(
        'forms/<uuid:pk>/content/email/',
        AIContentViewSet.as_view({'post': 'generate_email'}),
        name='content-email'
    ),
    path(
        'forms/<uuid:pk>/content/placeholders/',
        AIContentViewSet.as_view({'post': 'generate_placeholders'}),
        name='content-placeholders'
    ),
    path(
        'forms/<uuid:pk>/content/help-text/',
        AIContentViewSet.as_view({'post': 'generate_help_text'}),
        name='content-help-text'
    ),
    path(
        'forms/<uuid:pk>/content/questions/',
        AIContentViewSet.as_view({'post': 'generate_questions'}),
        name='content-questions'
    ),
    path(
        'forms/<uuid:pk>/content/improve/',
        AIContentViewSet.as_view({'post': 'improve_copy'}),
        name='content-improve'
    ),
    path(
        'forms/<uuid:pk>/content/translate/',
        AIContentViewSet.as_view({'post': 'translate'}),
        name='content-translate'
    ),
    path(
        'forms/<uuid:pk>/content/consent/',
        AIContentViewSet.as_view({'post': 'generate_consent'}),
        name='content-consent'
    ),
    path(
        'forms/<uuid:pk>/content/suggestions/',
        AIContentViewSet.as_view({'post': 'suggest_improvements'}),
        name='content-suggestions'
    ),
    path(
        'forms/<uuid:pk>/content/generated/',
        AIContentViewSet.as_view({'get': 'generated_content'}),
        name='content-generated'
    ),
]
