"""
URL configuration for 8 new advanced features
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views_advanced_new import (
    # Internationalization
    LanguageViewSet, FormTranslationViewSet, SubmissionTranslationViewSet,
    
    # Integration Marketplace
    IntegrationProviderViewSet, IntegrationConnectionViewSet,
    IntegrationWorkflowViewSet, WebhookEndpointViewSet,
    WebhookLogViewSet, IntegrationTemplateViewSet,
    
    # Scheduling
    FormScheduleViewSet, RecurringFormViewSet, FormLifecycleEventViewSet,
    
    # Themes
    ThemeViewSet, FormThemeViewSet, ThemeRatingViewSet, BrandGuidelineViewSet,
    
    # Security
    TwoFactorAuthViewSet, SSOProviderViewSet, DataPrivacyRequestViewSet,
    ConsentTrackingViewSet, SecurityAuditLogViewSet, IPAccessControlViewSet,
    
    # Collaboration
    FormCollaboratorViewSet, FormEditSessionViewSet, FormChangeViewSet,
    FormCommentViewSet, FormReviewWorkflowViewSet, FormReviewViewSet,
    
    # Predictive
    FieldPredictionViewSet, SmartDefaultViewSet, CompletionPredictionViewSet,
    ProgressiveDisclosureViewSet,
    
    # Mobile
    MobileOptimizationViewSet, GeolocationFieldViewSet, OfflineSubmissionViewSet,
    PushNotificationSubscriptionViewSet, FormNotificationViewSet,
)

router = DefaultRouter()

# Internationalization routes
router.register(r'languages', LanguageViewSet, basename='language')
router.register(r'form-translations', FormTranslationViewSet, basename='form-translation')
router.register(r'submission-translations', SubmissionTranslationViewSet, basename='submission-translation')

# Integration Marketplace routes
router.register(r'integration-providers', IntegrationProviderViewSet, basename='integration-provider')
router.register(r'integration-connections', IntegrationConnectionViewSet, basename='integration-connection')
router.register(r'integration-workflows', IntegrationWorkflowViewSet, basename='integration-workflow')
router.register(r'webhook-endpoints', WebhookEndpointViewSet, basename='webhook-endpoint')
router.register(r'webhook-logs', WebhookLogViewSet, basename='webhook-log')
router.register(r'integration-templates', IntegrationTemplateViewSet, basename='integration-template')

# Scheduling routes
router.register(r'form-schedules', FormScheduleViewSet, basename='form-schedule')
router.register(r'recurring-forms', RecurringFormViewSet, basename='recurring-form')
router.register(r'lifecycle-events', FormLifecycleEventViewSet, basename='lifecycle-event')

# Theme routes
router.register(r'themes', ThemeViewSet, basename='theme')
router.register(r'form-themes', FormThemeViewSet, basename='form-theme')
router.register(r'theme-ratings', ThemeRatingViewSet, basename='theme-rating')
router.register(r'brand-guidelines', BrandGuidelineViewSet, basename='brand-guideline')

# Security routes
router.register(r'two-factor-auth', TwoFactorAuthViewSet, basename='two-factor-auth')
router.register(r'sso-providers', SSOProviderViewSet, basename='sso-provider')
router.register(r'privacy-requests', DataPrivacyRequestViewSet, basename='privacy-request')
router.register(r'consent-tracking', ConsentTrackingViewSet, basename='consent-tracking')
router.register(r'security-audit-logs', SecurityAuditLogViewSet, basename='security-audit-log')
router.register(r'ip-access-controls', IPAccessControlViewSet, basename='ip-access-control')

# Collaboration routes
router.register(r'form-collaborators', FormCollaboratorViewSet, basename='form-collaborator')
router.register(r'form-edit-sessions', FormEditSessionViewSet, basename='form-edit-session')
router.register(r'form-changes', FormChangeViewSet, basename='form-change')
router.register(r'form-comments', FormCommentViewSet, basename='form-comment')
router.register(r'form-review-workflows', FormReviewWorkflowViewSet, basename='form-review-workflow')
router.register(r'form-reviews', FormReviewViewSet, basename='form-review')

# Predictive routes
router.register(r'field-predictions', FieldPredictionViewSet, basename='field-prediction')
router.register(r'smart-defaults', SmartDefaultViewSet, basename='smart-default')
router.register(r'completion-predictions', CompletionPredictionViewSet, basename='completion-prediction')
router.register(r'progressive-disclosure', ProgressiveDisclosureViewSet, basename='progressive-disclosure')

# Mobile routes
router.register(r'mobile-optimizations', MobileOptimizationViewSet, basename='mobile-optimization')
router.register(r'geolocation-fields', GeolocationFieldViewSet, basename='geolocation-field')
router.register(r'offline-submissions', OfflineSubmissionViewSet, basename='offline-submission')
router.register(r'push-subscriptions', PushNotificationSubscriptionViewSet, basename='push-subscription')
router.register(r'form-notifications', FormNotificationViewSet, basename='form-notification')

urlpatterns = [
    path('', include(router.urls)),
]
